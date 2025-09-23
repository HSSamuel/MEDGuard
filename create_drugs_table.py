import sqlite3

DB_PATH = "backend/database.db"  # adjust if needed


def create_drugs_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch_number TEXT UNIQUE NOT NULL,
            mfg_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            manufacturer TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ 'drugs' table created or already exists.")


if __name__ == "__main__":
    create_drugs_table()
