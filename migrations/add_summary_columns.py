import sqlite3

DB_PATH = "medguard.db"

def upgrade():
    """Adds a summary column to the reports and adr_reports tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # --- Add summary to reports table ---
        c.execute("PRAGMA table_info(reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'summary' not in columns:
            print("Adding 'summary' column to 'reports' table...")
            c.execute("ALTER TABLE reports ADD COLUMN summary TEXT")
            print("'summary' column added successfully.")
        else:
            print("'summary' column in 'reports' already exists.")

        # --- Add summary to adr_reports table ---
        c.execute("PRAGMA table_info(adr_reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'summary' not in columns:
            print("Adding 'summary' column to 'adr_reports' table...")
            c.execute("ALTER TABLE adr_reports ADD COLUMN summary TEXT")
            print("'summary' column added successfully.")
        else:
            print("'summary' column in 'adr_reports' already exists.")
            
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()