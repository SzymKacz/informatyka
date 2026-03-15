import time
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

from app.db.db_connection import get_connection
from app.services.imdb_client import get_title

WORKERS = 16
BATCH_COMMIT = 10
LOG_EVERY = 10

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "movielens_raw"

MOVIES_CSV = DATA_DIR / "movies.csv"
LINKS_CSV = DATA_DIR / "links.csv"


def normalize_imdb_id(x) -> str:
    return f"tt{int(x):07d}"


def extract_year(title: str):
    if title and "(" in title:
        try:
            return int(title[-5:-1])
        except ValueError:
            pass
    return None


def fetch_movie(row):
    """WĄTEK HTTP"""
    imdb_id = row.imdb_id_norm
    data = get_title(imdb_id)
    return row, data


def main():
    start_time = time.time()

    print("📥 Wczytywanie MovieLens CSV...")
    movies_ml = pd.read_csv(MOVIES_CSV)
    links_ml = pd.read_csv(LINKS_CSV)

    ml = movies_ml.merge(links_ml, on="movieId")
    ml = ml.dropna(subset=["imdbId"])
    ml["imdb_id_norm"] = ml["imdbId"].apply(normalize_imdb_id)

    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 START OD OSTATNIEGO ID W BAZIE
    cursor.execute("SELECT COALESCE(MAX(id), 0) FROM movies")
    last_id = cursor.fetchone()[0]

    ml = ml[ml["movieId"] > last_id]

    print(f"🎬 Filmów do importu: {len(ml)}")
    print(f"⏩ Start od movieId > {last_id}")

    inserted = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(fetch_movie, row) for row in ml.itertuples()]

        for future in as_completed(futures):
            row, data = future.result()

            title = row.title
            year = extract_year(title)

            overview = data.get("plot", {}).get("plotText", {}).get("plainText") if data else None
            popularity = data.get("ratingsSummary", {}).get("aggregateRating") if data else None
            poster = data.get("primaryImage", {}).get("url") if data else None

            cursor.execute("""
                INSERT OR IGNORE INTO movies (
                    id, title, year, genres, imdb_id,
                    overview, poster_path, popularity, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                int(row.movieId),
                title,
                year,
                row.genres.replace("|", ", "),
                row.imdb_id_norm,
                overview,
                poster,
                popularity
            ))

            if cursor.rowcount == 1:
                inserted += 1

            if inserted % BATCH_COMMIT == 0:
                conn.commit()

            if inserted % LOG_EVERY == 0 and inserted > 0:
                elapsed = time.time() - start_time
                rate = inserted / elapsed
                print(f"✔ {inserted} zapisanych | ⏱ {elapsed:.1f}s | ⚡ {rate:.2f}/s")

    conn.commit()
    conn.close()

    total_time = time.time() - start_time
    print("✅ IMPORT ZAKOŃCZONY")
    print(f"📊 Filmy: {inserted}")
    print(f"⏱ Czas: {total_time:.1f}s")
    print(f"⚡ Średnio: {inserted / total_time:.2f} filmów/s")



if __name__ == "__main__":
    main()
