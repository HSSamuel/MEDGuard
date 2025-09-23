import sqlite3

DB_PATH = "medguard.db"

def add_analysis_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Check if the 'image_analysis_result' column exists
        c.execute("PRAGMA table_info(reports)")
        columns = [row[1] for row in c.fetchall()]
        if 'image_analysis_result' not in columns:
            print("Adding 'image_analysis_result' column to 'reports' table...")
            c.execute("ALTER TABLE reports ADD COLUMN image_analysis_result TEXT")
            print("'image_analysis_result' column added successfully.")
        else:
            print("'image_analysis_result' column already exists.")

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_analysis_column()