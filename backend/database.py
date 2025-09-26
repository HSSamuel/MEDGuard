import sqlite3
from flask import g
from backend.config import get_config
from werkzeug.security import generate_password_hash

# Load configuration
cfg = get_config()


def get_db():
    """
    Get a database connection with timeout and WAL mode enabled.
    Uses Flask's `g` to reuse the same connection per request.
    """
    if "db" not in g:
        conn = sqlite3.connect(
            cfg.DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES,
            timeout=10
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        g.db = conn
    return g.db


def get_conn():
    """Alias for get_db() to maintain compatibility with existing code."""
    return get_db()


def close_db(e=None):
    """
    Close the database connection at the end of the request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Initialize the database tables if they don't exist.
    """
    conn = sqlite3.connect(cfg.DB_PATH)
    c = conn.cursor()

    # Create drugs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch_number TEXT UNIQUE NOT NULL,
            mfg_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Create users table for the public
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (datetime('now'))
        )
    """)

    # Create reports table with user_id foreign key
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        drug_name TEXT,
        batch_number TEXT NOT NULL,
        location TEXT,
        note TEXT,
        image_filename TEXT,
        latitude REAL,
        longitude REAL,
        image_analysis_result TEXT,
        reported_on TIMESTAMP DEFAULT (datetime('now')),
        status INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Create admin_users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            role TEXT NOT NULL
        )
    """)
    
    # NEW: Create the scan_logs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_number TEXT NOT NULL,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            latitude REAL,
            longitude REAL,
            ip_address TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Add default admin user if table is empty
    c.execute("SELECT COUNT(*) FROM admin_users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO admin_users (company_name, email, password_hash, is_verified, role) VALUES (?, ?, ?, ?, ?)",
            ("NAFDAC",
             "admin@nafdac.gov.ng",
             "scrypt:32768:8:1$DoYZQKT3lgjtjzud$fd4dd946a8eaa84c7ea9271df7a633d2d5dc296c06a29088713f0884e65ca1e43316df3bf71de1306feea0e1fd9757aff40e0eb1841f6014b1e5a64f9081e510",
             1, 
             "regulator")
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print(f"Initializing database at: {cfg.DB_PATH}")
    init_db()
    print("✅ Database initialized successfully with clean schema.")