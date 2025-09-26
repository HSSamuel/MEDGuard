import sqlite3

# Adjust the path to your database if necessary
DB_PATH = "medguard.db"

def upgrade():
    """Adds the adr_reports table to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS adr_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_id INTEGER NOT NULL,
                patient_age_range TEXT,
                patient_gender TEXT,
                reaction_description TEXT NOT NULL,
                reaction_start_date TEXT,
                other_medications TEXT,
                report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (drug_id) REFERENCES drugs (id)
            )
        """)
        conn.commit()
        print("✅ 'adr_reports' table created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()