import sqlite3

DB_PATH = "medguard.db"

def add_location_columns():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Check if the 'latitude' column exists
        c.execute("PRAGMA table_info(reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'latitude' not in columns:
            print("Adding 'latitude' column to 'reports' table...")
            c.execute("ALTER TABLE reports ADD COLUMN latitude REAL")
            print("'latitude' column added successfully.")
        else:
            print("'latitude' column already exists.")

        # Check if the 'longitude' column exists
        c.execute("PRAGMA table_info(reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'longitude' not in columns:
            print("Adding 'longitude' column to 'reports' table...")
            c.execute("ALTER TABLE reports ADD COLUMN longitude REAL")
            print("'longitude' column added successfully.")
        else:
            print("'longitude' column already exists.")

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_location_columns()