import sqlite3
from werkzeug.security import generate_password_hash

# Path to your SQLite database
DB_PATH = "medguard.db"

# Approved regulator email domains
ALLOWED_DOMAINS = {
    "nafdac.gov.ng",
    "regulator.example.org"
    # Add more official domains here
}


def email_allowed(email: str) -> bool:
    """Check if the email's domain is in the allowed list."""
    try:
        domain = email.split("@", 1)[1].lower()
        return domain in ALLOWED_DOMAINS
    except Exception:
        return False


def create_admin_user():
    print("=== Create Regulator Admin Account ===")
    company_name = input("Company name: ").strip()
    email = input("Official email: ").strip().lower()
    password = input("Password: ").strip()

    if not company_name or not email or not password:
        print("❌ All fields are required.")
        return

    if not email_allowed(email):
        print(
            f"❌ Email domain not allowed. Must be one of: {', '.join(ALLOWED_DOMAINS)}")
        return

    # Hash the password
    password_hash = generate_password_hash(password)

    # Connect to DB and ensure table exists
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'regulator',
        is_verified INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)

    try:
        conn.execute(
            "INSERT INTO admin_users (company_name, email, password_hash, role, is_verified) VALUES (?, ?, ?, ?, ?)",
            (company_name, email, password_hash, "regulator", 1)
        )
        conn.commit()
        print(f"✅ Admin user for {company_name} created successfully.")
    except sqlite3.IntegrityError:
        print("❌ An account with that email already exists.")
    finally:
        conn.close()


if __name__ == "__main__":
    create_admin_user()
