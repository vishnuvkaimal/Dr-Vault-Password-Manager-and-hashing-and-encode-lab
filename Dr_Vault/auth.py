import bcrypt
from database import get_connection
import os

def signup(username, password):
    conn = get_connection()
    cur = conn.cursor()

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, hashed, salt)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return False, None

    hashed, salt = row
    return bcrypt.checkpw(password.encode(), hashed), salt