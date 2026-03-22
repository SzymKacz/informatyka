
import sqlite3
import pandas as pd
from datetime import datetime
DB_PATH = "app/db/database2.db"

def get_connection():
    return sqlite3.connect(DB_PATH)
def get_user(username: str):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM users WHERE username = ?",
        conn,
        params=(username,)
    )
    conn.close()
    if df.empty:
        return None
    return df.iloc[0]

def create_user(username: str, password_hash: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.now())
    )
    conn.commit()
    conn.close()

def update_user_password(username: str, new_password_hash: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (new_password_hash, username)
    )
    conn.commit()
    conn.close()