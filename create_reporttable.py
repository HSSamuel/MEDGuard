import sqlite3

DB_PATH = "backend/database.db"  # same DB as your drugs table


def create_reports_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT,
            batch_number TEXT NOT NULL,
            location TEXT,
            note TEXT,
            reported_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ 'reports' table created or already exists.")


if __name__ == "__main__":
    create_reports_table()
