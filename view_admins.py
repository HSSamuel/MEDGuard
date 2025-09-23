import sqlite3
from werkzeug.security import check_password_hash

DB_PATH = "medguard.db"  # adjust if your DB file is elsewhere


def list_admins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT id, company_name, email, password_hash, role, is_verified FROM admin_users"
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No admin users found.")
        return

    print("=== Admin Users ===")
    for row in rows:
        admin_id, company_name, email, password_hash, role, is_verified = row
        print(f"ID: {admin_id}")
        print(f"Company: {company_name}")
        print(f"Email: {email}")
        print(f"Password Hash: {password_hash}")
        print(f"Role: {role}")
        print(f"Verified: {'Yes' if is_verified else 'No'}")
        print("-" * 40)


def test_password(email, password):
    """Check if the given password matches the stored hash for this email."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT password_hash FROM admin_users WHERE email = ?", (email.lower(
        ),)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"❌ No admin found with email: {email}")
        return

    stored_hash = row[0]
    if check_password_hash(stored_hash, password):
        print("✅ Password is correct.")
    else:
        print("❌ Password is incorrect.")


if __name__ == "__main__":
    print("1. View all admins")
    print("2. Test a password for an admin")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "1":
        list_admins()
    elif choice == "2":
        email = input("Enter admin email: ").strip()
        password = input("Enter password to test: ").strip()
        test_password(email, password)
    else:
        print("❌ Invalid choice.")
