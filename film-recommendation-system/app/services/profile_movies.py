from __future__ import annotations
import sqlite3

def get_user_watched_movie_ids(conn: sqlite3.Connection, user_id: int) -> list[int]:
    rows = conn.execute(
        "SELECT movie_id FROM watched WHERE user_id = ? ORDER BY watched_at DESC",
        (user_id,),
    ).fetchall()
    return [int(r[0]) for r in rows]

def get_user_rated_movie_ids(conn: sqlite3.Connection, user_id: int) -> list[int]:
    rows = conn.execute(
        "SELECT movie_id FROM ratings WHERE user_id = ? ORDER BY rated_at DESC",
        (user_id,),
    ).fetchall()
    return [int(r[0]) for r in rows]
    
def get_user_rated_movie_ids_with_ratings(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, rating FROM ratings WHERE user_id = ?", (user_id,))
    return cursor.fetchall()