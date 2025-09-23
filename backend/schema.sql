CREATE TABLE IF NOT EXISTS drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    batch_number TEXT UNIQUE NOT NULL,
    mfg_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_name TEXT,
    batch_number TEXT NOT NULL,
    location TEXT,
    note TEXT,
    reported_on TIMESTAMP DEFAULT (datetime('now')),
    status INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_verified INTEGER DEFAULT 0,
    role TEXT NOT NULL
);