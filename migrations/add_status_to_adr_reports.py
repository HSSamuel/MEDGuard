import sqlite3

DB_PATH = "medguard.db"

def upgrade():
    """Adds a status column to the adr_reports table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Check if the 'status' column exists
        c.execute("PRAGMA table_info(adr_reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'status' not in columns:
            print("Adding 'status' column to 'adr_reports' table...")
            # We'll use TEXT for status: "New", "Under Review", "Resolved"
            c.execute("ALTER TABLE adr_reports ADD COLUMN status TEXT DEFAULT 'New'")
            print("'status' column added successfully.")
        else:
            print("'status' column already exists.")
            
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()