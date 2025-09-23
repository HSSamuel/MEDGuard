import sqlite3

DB_PATH = "medguard.db"

def add_user_id_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Check if the 'user_id' column exists
        c.execute("PRAGMA table_info(reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'user_id' not in columns:
            print("Adding 'user_id' column to 'reports' table...")
            c.execute("ALTER TABLE reports ADD COLUMN user_id INTEGER REFERENCES users(id)")
            print("'user_id' column added successfully.")
        else:
            print("'user_id' column already exists.")

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_user_id_column()