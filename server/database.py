# database.py (NOVÁ VERZE PRO POSTGRESQL)
import psycopg2
import bcrypt
import json # Pro migraci z JSON, pokud ji budete chtít použít

# --- Konfigurace PostgreSQL připojení ---
# TYTO HODNOTY MUSÍTE UPRAVIT PODLE VAŠEHO NASTAVENÍ POSTGRESQL!
DB_CONFIG = {
    'host': 'localhost',
    'database': 'kniha_data',
    'user': 'kniha_user', 
    'password': '4T7*hT4cB',
    'port': '5432' 
}

def get_db_connection():
    """Získá a vrátí připojení k PostgreSQL databázi."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False # Nastavte na False pro explicitní transakce (commit/rollback)
        return conn
    except psycopg2.Error as e:
        print(f"Chyba připojení k databázi: {e}")
        # V produkci byste zde mohli chtít vyvolat výjimku nebo logovat chybu
        return None

def initialize_db():
    """Inicializuje databázi PostgreSQL a vytváří tabulky, pokud neexistují."""
    conn = get_db_connection()
    if conn is None:
        print("Nelze inicializovat databázi: Připojení selhalo.")
        return

    cursor = conn.cursor()
    try:
        # Vytvořit tabulku users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE
            );
        """)

        # Vytvořit tabulku routes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                start_location TEXT,
                destination TEXT NOT NULL,
                distance TEXT,
                needs_fuel BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, name) -- Ensure unique route names per user
            );
        """)
        conn.commit()
        print("PostgreSQL databáze inicializována a tabulky vytvořeny/ověřeny.")
    except psycopg2.Error as e:
        print(f"Chyba při inicializaci databáze PostgreSQL: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def register_user(username, password, is_admin=0):
    """Registruje nového uživatele do databáze s hašovaným heslem."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s);",
            (username, hashed_password, bool(is_admin))
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        print(f"Uživatel '{username}' již existuje.")
        conn.rollback()
        return False
    except psycopg2.Error as e:
        print(f"Chyba při registraci uživatele: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def verify_login(username, password):
    """
    Ověří přihlašovací údaje uživatele.
    Pokud je přihlášení úspěšné, vrátí slovník s 'id', 'username' a 'is_admin'.
    Jinak vrátí None.
    """
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username = %s;", (username,))
        result = cursor.fetchone()
        if result:
            user_id, db_username, stored_hashed_password, is_admin_status = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return {
                    'id': user_id,
                    'username': db_username,
                    'is_admin': bool(is_admin_status)
                }
        return None
    except psycopg2.Error as e:
        print(f"Chyba při ověřování přihlášení: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_id(username):
    """Získá ID uživatele podle uživatelského jména."""
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Chyba při získávání ID uživatele: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def is_admin(username): # Tato funkce už by neměla být přímo volána z login_screen.py, verify_login je lepší
    """Zkontroluje, zda je uživatel administrátor."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT is_admin FROM users WHERE username = %s;", (username,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    except psycopg2.Error as e:
        print(f"Chyba při kontrole administrátorských práv: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_route(user_id, name, start_location, destination, distance, needs_fuel):
    """Přidá novou trasu do databáze."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO routes (user_id, name, start_location, destination, distance, needs_fuel) VALUES (%s, %s, %s, %s, %s, %s);",
            (user_id, name, start_location, destination, distance, bool(needs_fuel))
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        print(f"Trasa s názvem '{name}' pro uživatele {user_id} již existuje.")
        conn.rollback()
        return False
    except psycopg2.Error as e:
        print(f"Chyba při přidávání trasy: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_routes_by_user(user_id):
    """Získá všechny trasy pro daného uživatele."""
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, start_location, destination, distance, needs_fuel FROM routes WHERE user_id = %s;", (user_id,))
        rows = cursor.fetchall()
        # Převod na slovníky pro snadnější manipulaci
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except psycopg2.Error as e:
        print(f"Chyba při získávání tras pro uživatele: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_route(route_id, name, start_location, destination, distance, needs_fuel):
    """Aktualizuje existující trasu."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE routes SET name = %s, start_location = %s, destination = %s, distance = %s, needs_fuel = %s WHERE id = %s;",
            (name, start_location, destination, distance, bool(needs_fuel), route_id)
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        print(f"Trasa s názvem '{name}' již existuje pro jiného uživatele nebo aktualizace vytvořila duplikát.")
        conn.rollback()
        return False
    except psycopg2.Error as e:
        print(f"Chyba při aktualizaci trasy: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def delete_route(route_id):
    """Smaže trasu z databáze."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM routes WHERE id = %s;", (route_id,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Chyba při mazání trasy: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    """Získá všechny uživatele (pro admina)."""
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, is_admin FROM users;")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except psycopg2.Error as e:
        print(f"Chyba při získávání všech uživatelů: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_user(user_id, new_username=None, new_password=None, new_is_admin=None):
    """Aktualizuje uživatelská data."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if new_username is not None:
            updates.append("username = %s")
            params.append(new_username)
        if new_password is not None:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            updates.append("password = %s")
            params.append(hashed_password)
        if new_is_admin is not None:
            updates.append("is_admin = %s")
            params.append(bool(new_is_admin))

        if not updates:
            return True

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s;"
        cursor.execute(query, tuple(params))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        print(f"Uživatelské jméno '{new_username}' již existuje.")
        conn.rollback()
        return False
    except psycopg2.Error as e:
        print(f"Chyba při aktualizaci uživatele: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def delete_user(user_id):
    """Smaže uživatele a jeho trasy."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Chyba při mazání uživatele: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def count_admins():
    """Spočítá počet administrátorů v databázi."""
    conn = get_db_connection()
    if conn is None: return 0
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE;")
        result = cursor.fetchone()
        return result[0] if result else 0
    except psycopg2.Error as e:
        print(f"Chyba při počítání administrátorů: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_route_by_name(user_id, route_name):
    """Pomocná funkce pro migraci: Získá trasu podle uživatele a názvu."""
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM routes WHERE user_id = %s AND name = %s;", (user_id, route_name))
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Chyba při kontrole existence trasy: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def migrate_json_to_postgresql(json_file):
    """
    Migruje uživatele a jejich trasy z JSON souboru do PostgreSQL databáze.
    Tato funkce by měla být spuštěna POUZE JEDNOU!
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        users_to_migrate = data.get("users", [])

        for user_data in users_to_migrate:
            username = user_data.get("username")
            password = user_data.get("password")
            is_admin = int(user_data.get("admin", "0"))

            if username and password:
                # Zkontrolovat, zda uživatel již existuje
                existing_user_id = get_user_id(username)
                if not existing_user_id:
                    # register_user vrací True/False, ne ID
                    if register_user(username, password, is_admin):
                        user_id = get_user_id(username) # Získat ID nově vytvořeného uživatele

                        # Migrace tras pro tohoto uživatele
                        user_routes = user_data.get("trasy", [])
                        for route in user_routes:
                            route_name = route.get("name")
                            start_location = route.get("start_location", "")
                            destination = route.get("destination")
                            distance = route.get("distance")
                            needs_fuel = route.get("needs_fuel", 0)

                            if route_name and destination and distance:
                                # Zkontrolovat duplicitní trasy pro tohoto uživatele
                                if not get_route_by_name(user_id, route_name):
                                    add_route(user_id, route_name, start_location, destination, distance, needs_fuel)
                                else:
                                    print(f"Skipping existing route '{route_name}' for user '{username}' during migration.")
                            else:
                                print(f"Skipping incomplete route for user '{username}': {route}")
                    else:
                        print(f"Skipping routes for user: {username} (already exists or registration failed).")
                else:
                    print(f"User '{username}' already exists in DB. Skipping user and their routes during migration.")
            else:
                print(f"Skipping user with incomplete data: {user_data}")
        print("Migrace JSON do PostgreSQL dokončena!")
    except FileNotFoundError:
        print(f"JSON soubor '{json_file}' nenalezen pro migraci. Migrace přeskočena.")
    except json.JSONDecodeError as e:
        print(f"Neplatný formát JSON v '{json_file}'. Migrace přeskočena. Chyba: {e}")
    except Exception as e:
        print(f"Při migraci JSON nastala neočekávaná chyba: {e}")

if __name__ == "__main__":
    # Tento blok je pro přímé spuštění database.py pro nastavení/migraci
    initialize_db()
    print("PostgreSQL databáze připravena.")
    
    # --- DŮLEŽITÉ KROKY ---
    # 1. Pokud máte existující login.json a chcete z něj importovat uživatele:
    #    Odkomentujte řádek níže, spusťte tento soubor JEDNOU pomocí `python database.py`.
    #    Po úspěšné migraci, ZAKOMENTUJTE HO ZNOVU, aby se nespouštěl pokaždé.
    # migrate_json_to_postgresql("login.json")

    pass