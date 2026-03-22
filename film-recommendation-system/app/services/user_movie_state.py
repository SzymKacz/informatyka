# app/services/user_movie_state.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class UserMovieState:
    watched: bool
    rating: int | None  # 1..5 albo None


def get_user_movie_state(conn: sqlite3.Connection, user_id: int, movie_id: int) -> UserMovieState:
    conn.row_factory = sqlite3.Row

    r = conn.execute(
        "SELECT rating FROM ratings WHERE user_id = ? AND movie_id = ?",
        (user_id, movie_id),
    ).fetchone()
    rating = int(r["rating"]) if r else None

    w = conn.execute(
        "SELECT 1 FROM watched WHERE user_id = ? AND movie_id = ?",
        (user_id, movie_id),
    ).fetchone()
    watched = bool(w)

    return UserMovieState(watched=watched, rating=rating)


def upsert_rating(conn: sqlite3.Connection, user_id: int, movie_id: int, rating: int | None) -> None:
    if rating is None:
        conn.execute(
            "DELETE FROM ratings WHERE user_id = ? AND movie_id = ?",
            (user_id, movie_id),
        )
        return

    conn.execute(
        """
        INSERT INTO ratings (user_id, movie_id, rating, rated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, movie_id)
        DO UPDATE SET rating=excluded.rating, rated_at=excluded.rated_at
        """,
        (user_id, movie_id, int(rating), now_iso_utc()),
    )


def set_watched(conn: sqlite3.Connection, user_id: int, movie_id: int, watched: bool) -> None:
    if not watched:
        conn.execute(
            "DELETE FROM watched WHERE user_id = ? AND movie_id = ?",
            (user_id, movie_id),
        )
        return

    conn.execute(
        """
        INSERT INTO watched (user_id, movie_id, watched_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, movie_id)
        DO UPDATE SET watched_at=excluded.watched_at
        """,
        (user_id, movie_id, now_iso_utc()),
    )