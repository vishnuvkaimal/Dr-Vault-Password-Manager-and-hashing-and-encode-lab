import sqlite3

DB_NAME = "securehash.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash BLOB NOT NULL,
        salt BLOB NOT NULL
    )
    """)

    # Vault table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT NOT NULL,
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        password_encrypted BLOB NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()