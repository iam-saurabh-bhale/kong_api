
import sqlite3
import os
from auth import hash_password

DB_PATH = os.getenv("DB_PATH", "/data/sqlite.db")
DEFAULT_ADMIN_USER = os.getenv("DEFAULT_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASS = os.getenv("DEFAULT_ADMIN_PASS", "admin123")

def init_db():
    os.makedirs("/data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("SELECT * FROM users WHERE username=?", (DEFAULT_ADMIN_USER,))
    user = cursor.fetchone()

    if not user:
        hashed = hash_password(DEFAULT_ADMIN_PASS)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (DEFAULT_ADMIN_USER, hashed)
        )

    conn.commit()
    conn.close()
