# database.py
import psycopg2
import bcrypt
import json

DB_CONFIG = {
    'host': 'localhost',
    'database': 'kniha_data',
    'user': 'kniha_user',
    'password': '4T7*hT4cB',
    'port': '5432'
}

def get_db_connection():
    """Získá a vrátí připojení k PostgreSQL databázi."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        print(f"Chyba připojení k databázi: {e}")
        return None

def initialize_db():
    """Inicializuje databázi PostgreSQL a vytváří tabulky, pokud neexistují."""
    conn = get_db_connection()
    if conn is None:
        print("Nelze inicializovat databázi: Připojení selhalo.")
        return

    cursor = conn.cursor()
    try:
        # Tabulka uživatelů
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)
        print("Tabulka 'users' již existuje nebo byla vytvořena.")

        # Tabulka tras
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                start_location VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                distance VARCHAR(255),
                travel_time INTEGER,
                fuel_consumption NUMERIC,
                gas_stations JSONB DEFAULT '[]',
                needs_fuel BOOLEAN DEFAULT FALSE,
                trip_purpose VARCHAR(255),
                waypoints JSONB DEFAULT '[]',
                route_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (user_id, name)
            );
        """)
        print("Tabulka 'routes' již existuje nebo byla vytvořena.")

        # Tabulka aut
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                car_type VARCHAR(50) NOT NULL, -- 'electric' nebo 'combustion'
                avg_consumption NUMERIC(5, 2) DEFAULT NULL, -- Průměrná spotřeba, např. 7.50 L/100km
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, name) -- Uživatel nemůže mít dvě auta se stejným názvem
            );
        """)
        print("Tabulka 'cars' již existuje nebo byla vytvořena.")

        conn.commit()
        print("Databáze úspěšně inicializována.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při inicializaci databáze: {e}")
    finally:
        cursor.close()
        conn.close()

def register_user(username, password, is_admin=False):
    """Zaregistruje nového uživatele."""
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s);",
            (username, hashed_password, is_admin)
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"Uživatel '{username}' již existuje.")
        return False
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při registraci uživatele: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def verify_user(username, password):
    """Ověří uživatelské jméno a heslo."""
    conn = get_db_connection()
    if conn is None:
        return None, False, None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash, is_admin FROM users WHERE username = %s;", (username,))
        result = cursor.fetchone()
        if result:
            user_id, hashed_password, is_admin = result
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return user_id, True, is_admin
        return None, False, None
    except psycopg2.Error as e:
        print(f"Chyba při ověřování uživatele: {e}")
        return None, False, None
    finally:
        cursor.close()
        conn.close()

def get_user_id(username):
    """Získá ID uživatele podle uživatelského jména."""
    conn = get_db_connection()
    if conn is None:
        return None
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

def get_all_users():
    """Získá všechny uživatele (pro admina)."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, is_admin FROM users ORDER BY username;")
        users = [{'id': row[0], 'username': row[1], 'is_admin': row[2]} for row in cursor.fetchall()]
        return users
    except psycopg2.Error as e:
        print(f"Chyba při získávání všech uživatelů: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_route(user_id, name, start_location, destination, distance, travel_time, fuel_consumption, gas_stations, needs_fuel, trip_purpose=None, route_date=None, waypoints=None):
    """Přidá novou trasu do databáze."""
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO routes (user_id, name, start_location, destination, distance, travel_time, 
                              fuel_consumption, gas_stations, needs_fuel, trip_purpose, route_date, waypoints)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (user_id, name, start_location, destination, distance, travel_time, 
             fuel_consumption, json.dumps(gas_stations), needs_fuel, trip_purpose, route_date, json.dumps(waypoints if waypoints else []))
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"Trasa s názvem '{name}' pro uživatele {user_id} již existuje.")
        return False
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při přidávání trasy: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_routes_by_user(user_id):
    """Získá všechny trasy pro konkrétního uživatele."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    routes = []
    try:
        cursor.execute(
            """
            SELECT id, name, start_location, destination, distance, travel_time, 
                   fuel_consumption, gas_stations, needs_fuel, trip_purpose, route_date, waypoints
            FROM routes
            WHERE user_id = %s
            ORDER BY route_date ASC NULLS LAST;
            """,
            (user_id,)
        )
        for row in cursor.fetchall():
            route = {
                'id': row[0],
                'name': row[1],
                'start_location': row[2],
                'destination': row[3],
                'distance': row[4],
                'travel_time': row[5],
                'fuel_consumption': row[6],
                'gas_stations': row[7] if row[7] is not None else [],
                'needs_fuel': row[8],
                'trip_purpose': row[9],
                'route_date': row[10],
                'waypoints': row[11] if row[11] is not None else []
            }
            routes.append(route)
        return routes
    except psycopg2.Error as e:
        print(f"Chyba při získávání tras uživatele: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_routes_by_date_range(user_id, start_date, end_date):
    """Získá trasy pro konkrétního uživatele v daném časovém rozmezí."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    routes = []
    try:
        cursor.execute(
            """
            SELECT id, name, start_location, destination, distance, travel_time, 
                   fuel_consumption, gas_stations, needs_fuel, trip_purpose, route_date
            FROM routes
            WHERE user_id = %s AND route_date BETWEEN %s AND %s
            ORDER BY route_date ASC;
            """,
            (user_id, start_date, end_date)
        )
        for row in cursor.fetchall():
            route = {
                'id': row[0],
                'name': row[1],
                'start_location': row[2],
                'destination': row[3],
                'distance': row[4],
                'travel_time': row[5],
                'fuel_consumption': row[6],
                'gas_stations': row[7] if row[7] is not None else [],
                'needs_fuel': row[8],
                'trip_purpose': row[9],
                'route_date': row[10]
            }
            routes.append(route)
        return routes
    except psycopg2.Error as e:
        print(f"Chyba při získávání tras uživatele: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def recreate_db():
    """Znovu vytvoří databázové tabulky."""
    conn = get_db_connection()
    if conn is None:
        print("Nelze inicializovat databázi: Připojení selhalo.")
        return

    cursor = conn.cursor()
    try:
        # Drop existing tables with CASCADE to handle dependencies
        cursor.execute("DROP TABLE IF EXISTS routes CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS cars CASCADE;")
        print("Existující tabulky byly odstraněny.")

        # Create tables with correct schema
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)
        print("Tabulka 'users' byla vytvořena.")

        cursor.execute("""
            CREATE TABLE routes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                start_location VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                distance VARCHAR(255),
                travel_time INTEGER,
                fuel_consumption NUMERIC,
                gas_stations JSONB DEFAULT '[]',
                needs_fuel BOOLEAN DEFAULT FALSE,
                trip_purpose VARCHAR(255),
                waypoints JSONB DEFAULT '[]',
                route_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (user_id, name)
            );
        """)
        print("Tabulka 'routes' byla vytvořena.")

        # Vytvoření tabulky cars
        cursor.execute("""
            CREATE TABLE cars (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                car_type VARCHAR(50) NOT NULL, -- 'electric' nebo 'combustion'
                avg_consumption NUMERIC(5, 2) DEFAULT NULL, -- Průměrná spotřeba, např. 7.50 L/100km
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, name)
            );
        """)
        print("Tabulka 'cars' byla vytvořena.")

        # Recreate the favorites table if it was used
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                route_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (route_id) REFERENCES routes(id),
                UNIQUE (user_id, route_id)
            );
        """)
        print("Tabulka 'favorites' byla vytvořena (pokud byla použita).")

        conn.commit()
        print("Databáze byla úspěšně znovu vytvořena.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při vytváření databáze: {e}")
    finally:
        cursor.close()
        conn.close()

def get_all_routes(user_id):
    """Get all routes for a specific user, including all details."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    routes = []
    try:
        cursor.execute(
            """
            SELECT id, name, start_location, destination, distance, travel_time, 
                   fuel_consumption, gas_stations, needs_fuel, trip_purpose, route_date, waypoints
            FROM routes
            WHERE user_id = %s
            ORDER BY route_date ASC NULLS LAST;
            """,
            (user_id,)
        )
        for row in cursor.fetchall():
            route = {
                'id': row[0],
                'name': row[1],
                'start_location': row[2],
                'destination': row[3],
                'distance': row[4],
                'travel_time': row[5],
                'fuel_consumption': row[6],
                'gas_stations': row[7] if row[7] is not None else [],
                'needs_fuel': row[8],
                'trip_purpose': row[9],
                'route_date': row[10],
                'waypoints': row[11] if row[11] is not None else []
            }
            routes.append(route)
        return routes
    except psycopg2.Error as e:
        print(f"Error getting all routes: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- Funkce pro správu aut ---

def add_car(user_id, name, car_type, avg_consumption=None):
    """Přidá nové auto do databáze pro daného uživatele."""
    conn = get_db_connection()
    if conn is None:
        return False, "Nepodařilo se připojit k databázi."
    cursor = conn.cursor()
    try:
        if car_type == 'combustion' and avg_consumption is None:
            return False, "Pro spalovací auto musí být zadána průměrná spotřeba."
        if car_type == 'electric':
            avg_consumption = None # U elektrických aut spotřebu v L/100km neukládáme

        cursor.execute(
            """
            INSERT INTO cars (user_id, name, car_type, avg_consumption)
            VALUES (%s, %s, %s, %s) RETURNING id;
            """,
            (user_id, name, car_type, avg_consumption)
        )
        car_id = cursor.fetchone()[0]
        conn.commit()
        return True, car_id
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, f"Auto s názvem '{name}' již existuje."
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při přidávání auta: {e}")
        return False, f"Chyba databáze: {e}"
    finally:
        cursor.close()
        conn.close()

def get_cars_by_user(user_id):
    """Získá všechna auta pro konkrétního uživatele."""
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cars = []
    try:
        cursor.execute(
            """
            SELECT id, name, car_type, avg_consumption
            FROM cars
            WHERE user_id = %s
            ORDER BY name ASC;
            """,
            (user_id,)
        )
        for row in cursor.fetchall():
            car = {
                'id': row[0],
                'name': row[1],
                'car_type': row[2],
                'avg_consumption': row[3],
            }
            cars.append(car)
        return cars
    except psycopg2.Error as e:
        print(f"Chyba při získávání aut uživatele: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_car_by_id(car_id, user_id):
    """Získá konkrétní auto podle jeho ID a ID uživatele (pro ověření vlastnictví)."""
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, name, car_type, avg_consumption
            FROM cars
            WHERE id = %s AND user_id = %s;
            """,
            (car_id, user_id)
        )
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'user_id': user_id,
                'name': row[1],
                'car_type': row[2],
                'avg_consumption': row[3],
            }
        return None
    except psycopg2.Error as e:
        print(f"Chyba při získávání auta podle ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_car(car_id, user_id, name, car_type, avg_consumption=None):
    """Aktualizuje údaje o autě."""
    conn = get_db_connection()
    if conn is None:
        return False, "Nepodařilo se připojit k databázi."
    cursor = conn.cursor()
    try:
        if car_type == 'combustion' and avg_consumption is None:
            return False, "Pro spalovací auto musí být zadána průměrná spotřeba."
        if car_type == 'electric':
            avg_consumption = None

        cursor.execute(
            """
            UPDATE cars
            SET name = %s, car_type = %s, avg_consumption = %s
            WHERE id = %s AND user_id = %s;
            """,
            (name, car_type, avg_consumption, car_id, user_id)
        )
        conn.commit()
        return True, "Auto úspěšně aktualizováno."
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, f"Auto s názvem '{name}' již existuje pro jiný záznam."
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při aktualizaci auta: {e}")
        return False, f"Chyba databáze: {e}"
    finally:
        cursor.close()
        conn.close()

def delete_car(car_id, user_id):
    """Smaže auto z databáze."""
    conn = get_db_connection()
    if conn is None:
        return False, "Nepodařilo se připojit k databázi."
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM cars WHERE id = %s AND user_id = %s;",
            (car_id, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Auto nebylo nalezeno nebo nemáte oprávnění jej smazat."
        return True, "Auto úspěšně smazáno."
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Chyba při mazání auta: {e}")
        return False, f"Chyba databáze: {e}"
    finally:
        cursor.close()
        conn.close()

def delete_user(user_id):
    pass

if __name__ == "__main__":
    recreate_db()
    print("PostgreSQL databáze připravena.")