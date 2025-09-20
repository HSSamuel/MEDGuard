import sqlite3
import time
from typing import Optional, Dict
from backend.database import get_db

# ---------------------------
# Retry Settings
# ---------------------------
MAX_RETRIES = 3
RETRY_DELAY = 0.3  # seconds


def _execute_with_retry(conn, query, params=()):
    """
    Execute a query with retry logic if the database is locked.
    """
    for attempt in range(MAX_RETRIES):
        try:
            c = conn.cursor()
            c.execute(query, params)
            return c
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise


# ---------------------------
# DRUG BATCH FUNCTIONS
# ---------------------------

def insert_drug(name: str, batch_number: str, mfg_date: str, expiry_date: str, manufacturer: str):
    """
    Insert a new drug batch into the database with retry logic.
    """
    conn = get_db()
    _execute_with_retry(conn,
                        """
        INSERT INTO drugs (name, batch_number, mfg_date, expiry_date, manufacturer)
        VALUES (?, ?, ?, ?, ?)
        """,
                        (name, batch_number, mfg_date, expiry_date, manufacturer)
                        )
    conn.commit()


def get_drug_by_batch(batch_number: str) -> Optional[Dict]:
    """
    Retrieve a drug batch by its batch number.
    Returns a dict with all fields if found, else None.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        SELECT name, batch_number, mfg_date, expiry_date, manufacturer
        FROM drugs
        WHERE batch_number = ?
        """,
        (batch_number,)
    )
    row = c.fetchone()
    return dict(row) if row else None


# ---------------------------
# REPORT FUNCTIONS
# ---------------------------

def insert_report(batch_number: str, location: str = "", note: str = ""):
    """
    Insert a new report for a given batch number with retry logic.
    """
    conn = get_db()
    _execute_with_retry(conn,
                        "INSERT INTO reports (batch_number, location, note) VALUES (?, ?, ?)",
                        (batch_number, location, note)
                        )
    conn.commit()


def count_reports_for_batch(batch_number: str) -> int:
    """
    Count how many reports exist for a given batch number.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) as cnt FROM reports WHERE batch_number = ?",
        (batch_number,)
    )
    cnt = c.fetchone()["cnt"]
    return cnt


# ---------------------------
# ADMIN FUNCTIONS
# ---------------------------

def get_admin_by_email(conn, email: str):
    """
    Retrieve an admin user by email.
    """
    cur = conn.execute(
        """
        SELECT id, company_name, email, password_hash, role, is_verified
        FROM admin_users
        WHERE email = ?
        """,
        (email.lower(),)
    )
    row = cur.fetchone()
    if not row:
        return None
    keys = ["id", "company_name", "email",
            "password_hash", "role", "is_verified"]
    return dict(zip(keys, row))
