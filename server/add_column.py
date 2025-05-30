import sqlite3

def add_trip_purpose_column():
    try:
        conn = sqlite3.connect('routing_app.db')
        cursor = conn.cursor()
        
        # Add the trip_purpose column if it doesn't exist
        cursor.execute("ALTER TABLE routes ADD COLUMN trip_purpose TEXT")
        
        conn.commit()
        print("Column 'trip_purpose' added successfully!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'trip_purpose' already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_trip_purpose_column() 