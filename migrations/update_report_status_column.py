import sqlite3

# Adjust the path to your database if necessary
DB_PATH = "medguard.db"

def upgrade():
    """Updates the status column in the reports table to TEXT."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        print("Upgrading 'reports' table...")
        # We create a new table with the correct schema
        c.execute("""
            CREATE TABLE reports_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                drug_name TEXT,
                batch_number TEXT NOT NULL,
                location TEXT,
                note TEXT,
                image_filename TEXT,
                latitude REAL,
                longitude REAL,
                reported_on TIMESTAMP DEFAULT (datetime('now')),
                status TEXT DEFAULT 'New', -- Changed to TEXT
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Copy the data from the old table to the new one, converting the status
        c.execute("""
            INSERT INTO reports_new (id, user_id, drug_name, batch_number, location, note, image_filename, latitude, longitude, reported_on, status)
            SELECT id, user_id, drug_name, batch_number, location, note, image_filename, latitude, longitude, reported_on,
                   CASE status WHEN 0 THEN 'New' WHEN 1 THEN 'Resolved' ELSE 'New' END
            FROM reports
        """)

        # Drop the old table and rename the new one
        c.execute("DROP TABLE reports")
        c.execute("ALTER TABLE reports_new RENAME TO reports")
        
        conn.commit()
        print("✅ 'reports' table upgraded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()