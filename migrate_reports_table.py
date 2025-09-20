import sqlite3

DB_PATH = "backend/database.db"  # adjust if needed

# Define the expected schema for the reports table
EXPECTED_COLUMNS = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "drug_name": "TEXT",
    "batch_number": "TEXT NOT NULL",
    "location": "TEXT",
    "note": "TEXT",
    "reported_on": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
}


def migrate_reports_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ensure the table exists with at least the base structure
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS reports (
            {', '.join([f"{col} {definition}" for col, definition in EXPECTED_COLUMNS.items()])}
        )
    """)

    # Get current columns
    c.execute("PRAGMA table_info(reports)")
    existing_cols = [col[1] for col in c.fetchall()]

    # Add any missing columns
    for col, definition in EXPECTED_COLUMNS.items():
        if col not in existing_cols:
            print(f"⚠️ Column '{col}' missing. Adding it now...")
            c.execute(f"ALTER TABLE reports ADD COLUMN {col} {definition}")
            conn.commit()
            print(f"✅ Column '{col}' added.")

    print("✅ Reports table is up to date.")
    conn.close()


if __name__ == "__main__":
    migrate_reports_table()
