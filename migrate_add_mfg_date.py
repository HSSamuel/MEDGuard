import sqlite3

DB_PATH = "backend/database.db"  # adjust if your DB file is elsewhere


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_mfg_date_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if column_exists(c, "drugs", "mfg_date"):
        print("✅ 'mfg_date' column already exists. No changes made.")
    else:
        print("🔄 Adding 'mfg_date' column to 'drugs' table...")
        c.execute("ALTER TABLE drugs ADD COLUMN mfg_date TEXT")
        conn.commit()
        print("✅ 'mfg_date' column added successfully.")

    conn.close()


if __name__ == "__main__":
    add_mfg_date_column()
