# database.py
import sqlite3
import json 
import bcrypt 

DATABASE_NAME = "app_data.db"

def initialize_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL, 
            is_admin INTEGER NOT NULL DEFAULT 0 
        )
    """)

    # Create routes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            start_location TEXT,
            destination TEXT NOT NULL,
            distance TEXT,
            needs_fuel INTEGER NOT NULL DEFAULT 0, 
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, name) 
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password, is_admin=0):
    """Registers a new user in the database with a hashed password."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                       (username, hashed_password, is_admin)) 
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
        return False
    except Exception as e:
        print(f"Error registering user: {e}")
        return False
    finally:
        conn.close()

def get_user_id(username):
    """Returns the user_id for a given username, or None if not found."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def verify_login(username, password):
    """Verifies user credentials by comparing provided password with the stored hash."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hashed_password = result[0].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password)
    return False 

def is_admin(username):
    """Checks if a user is an administrator."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] == 1 if result else False

def get_all_users():
    """Retrieves all users from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT id, username, is_admin FROM users")
    users_data = cursor.fetchall()
    conn.close()
    
    users_list = []
    for row in users_data:
        users_list.append({
            "id": row[0],
            "username": row[1],
            "is_admin": bool(row[2])
        })
    return users_list

def update_user_admin_status(user_id, is_admin_status):
    """Updates the admin status of a user by their ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    try:
        cursor.execute("UPDATE users SET is_admin = ? WHERE id = ?", (1 if is_admin_status else 0, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user admin status: {e}")
        return False
    finally:
        conn.close()

def delete_user(user_id):
    """Deletes a user by their ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        conn.close()

def add_route(user_id, name, start_location, destination, distance, needs_fuel):
    """Adds a new route for a specific user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    try:
        cursor.execute("""
            INSERT INTO routes (user_id, name, start_location, destination, distance, needs_fuel)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, start_location, destination, distance, 1 if needs_fuel else 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Route with name '{name}' already exists for user_id {user_id}.")
        return False
    except Exception as e:
        print(f"Error adding route: {e}")
        return False
    finally:
        conn.close()

def get_routes_by_user(user_id):
    """Retrieves all routes for a given user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT id, name, start_location, destination, distance, needs_fuel FROM routes WHERE user_id = ?", (user_id,))
    routes_data = cursor.fetchall()
    conn.close()
    
    routes_list = []
    for row in routes_data:
        routes_list.append({
            "id": row[0],
            "name": row[1],
            "start_location": row[2] if row[2] else "N/A", 
            "destination": row[3],
            "distance": row[4],
            "needs_fuel": bool(row[5]) 
        })
    return routes_list

def get_route_by_id(route_id):
    """Retrieves a single route by its ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT id, name, start_location, destination, distance, needs_fuel FROM routes WHERE id = ?", (route_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "start_location": row[2] if row[2] else "N/A",
            "destination": row[3],
            "distance": row[4],
            "needs_fuel": bool(row[5])
        }
    return None

def update_route(route_id, name, start_location, destination, distance, needs_fuel):
    """Updates an existing route."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    try:
        cursor.execute("""
            UPDATE routes
            SET name = ?, start_location = ?, destination = ?, distance = ?, needs_fuel = ?
            WHERE id = ?
        """, (name, start_location, destination, distance, 1 if needs_fuel else 0, route_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Update failed: Route with name '{name}' already exists for this user.")
        return False
    except Exception as e:
        print(f"Error updating route: {e}")
        return False
    finally:
        conn.close()

def delete_route(route_id):
    """Deletes a route by its ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    try:
        cursor.execute("DELETE FROM routes WHERE id = ?", (route_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting route: {e}")
        return False
    finally:
        conn.close()

def hash_existing_passwords():
    """
    Hashes all existing plain-text passwords in the 'users' table.
    This function should be run ONCE after updating to hashed passwords logic.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA busy_timeout = 10000') # Changed to 10 seconds
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    
    updated_count = 0
    for user_id, username, current_password in users:
        # Check if password is NOT already a bcrypt hash (starts with $2a$, $2b$, or $2y$)
        if not current_password.startswith(("$2a$", "$2b$", "$2y$")): 
            try:
                hashed_password = bcrypt.hashpw(current_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
                updated_count += 1
                print(f"Hashed password for user: {username}")
            except Exception as e:
                print(f"Error hashing password for user {username}: {e}")
        else:
            print(f"Password for user {username} already appears to be hashed. Skipping.")
            
    conn.commit()
    conn.close()
    print(f"Finished hashing existing passwords. {updated_count} passwords updated.")

def migrate_json_to_sqlite(json_file="login.json"):
    """
    Migrates user and route data from a JSON file to the SQLite database.
    This function should only be run once after setting up the SQLite DB.
    It will hash passwords during migration.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Attempting to migrate data from {json_file}...")
        for user_data in data.get("users", []):
            username = user_data.get("username")
            password = user_data.get("password") 
            is_admin_flag = 1 if user_data.get("admin") == "1" else 0

            # Check if user already exists before attempting to register
            if not get_user_id(username):
                if register_user(username, password, is_admin_flag):
                    user_id = get_user_id(username)
                    if user_id and "trasy" in user_data:
                        for route in user_data["trasy"]:
                            start_location = route.get("start_location", "N/A")
                            needs_fuel = route.get("needs_fuel", False) # Default to False if not in JSON
                            # Check if route with same name already exists for this user
                            if not any(r['name'] == route['name'] for r in get_routes_by_user(user_id)):
                                add_route(user_id, 
                                          route["name"], 
                                          start_location, 
                                          route["destination"], 
                                          route["distance"], 
                                          needs_fuel)
                                print(f"Migrated route '{route['name']}' for user '{username}'.")
                            else:
                                print(f"Skipping existing route '{route['name']}' for user '{username}' during migration.")
                else:
                    print(f"Skipping routes for user: {username} (already exists or registration failed).")
            else:
                print(f"User '{username}' already exists in DB. Skipping user and their routes during migration.")
        print("Migration process complete!")
    except FileNotFoundError:
        print(f"JSON file '{json_file}' not found for migration. Skipping migration.")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in '{json_file}'. Skipping migration.")
    except Exception as e:
        print(f"An unexpected error occurred during JSON migration: {e}")

if __name__ == "__main__":
    # This block is for direct execution of database.py for setup/migration
    initialize_db()
    print("Database initialized (app_data.db).")
    
    # --- IMPORTANT STEPS ---
    # 1. If you have an existing login.json and want to import users from it:
    #    Uncomment the line below, run this file ONCE.
    #    After migration, COMMENT IT OUT AGAIN.
    migrate_json_to_sqlite("login.json")

    # 2. If you already have users in app_data.db with plain-text passwords:
    #    Uncomment the line below, run this file ONCE.
    #    This will hash existing plain-text passwords.
    #    After hashing, COMMENT IT OUT AGAIN.
    # hash_existing_passwords()
    
    print("Database ready.")