"""Standalone migration: SQLite → PostgreSQL (no SQLAlchemy imports)."""
import sys
import os
import sqlite3
import psycopg2
import psycopg2.extras

TABLES = ["users", "words", "user_progress", "quiz_history", "feedback", "wrong_answer_book"]

PG_DDL = {
    "users": """CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR NOT NULL UNIQUE,
        email VARCHAR NOT NULL UNIQUE,
        password_hash VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )""",
    "words": """CREATE TABLE IF NOT EXISTS words (
        id SERIAL PRIMARY KEY,
        english VARCHAR NOT NULL,
        chinese VARCHAR NOT NULL,
        part_of_speech VARCHAR,
        difficulty_level INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT NOW()
    )""",
    "user_progress": """CREATE TABLE IF NOT EXISTS user_progress (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        word_id INTEGER NOT NULL REFERENCES words(id),
        status VARCHAR DEFAULT 'new',
        correct_count INTEGER DEFAULT 0,
        wrong_count INTEGER DEFAULT 0,
        last_reviewed_at TIMESTAMP,
        next_review_at TIMESTAMP,
        UNIQUE(user_id, word_id)
    )""",
    "quiz_history": """CREATE TABLE IF NOT EXISTS quiz_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        quiz_type VARCHAR NOT NULL,
        total_questions INTEGER NOT NULL,
        correct_count INTEGER NOT NULL,
        wrong_count INTEGER DEFAULT 0,
        score_percent FLOAT NOT NULL,
        completed_at TIMESTAMP DEFAULT NOW()
    )""",
    "wrong_answer_book": """CREATE TABLE IF NOT EXISTS wrong_answer_book (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        word_id INTEGER NOT NULL REFERENCES words(id),
        user_answer VARCHAR,
        correct_answer VARCHAR NOT NULL,
        quiz_type VARCHAR(20),
        reviewed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(user_id, word_id)
    )""",
    "feedback": """CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        type VARCHAR(20) NOT NULL,
        content TEXT NOT NULL,
        contact VARCHAR(200),
        created_at TIMESTAMP DEFAULT NOW()
    )""",
}

TYPE_MAP = {
    "INTEGER": "INTEGER",
    "REAL": "FLOAT",
    "TEXT": "TEXT",
    "BLOB": "BYTEA",
    "datetime": "TIMESTAMP",
    "VARCHAR": "VARCHAR",
    "FLOAT": "FLOAT",
}


def get_sqlite_columns(sql_cur, table):
    rows = sql_cur.execute(f"PRAGMA table_info({table})").fetchall()
    cols = []
    for r in rows:
        name = r[1]
        col_type = r[2].upper()
        pg_type = TYPE_MAP.get(col_type, "TEXT")
        cols.append({"name": name, "type": pg_type})
    return cols


def migrate(sqlite_path: str, pg_url: str):
    sql_conn = sqlite3.connect(sqlite_path)
    sql_conn.row_factory = sqlite3.Row
    sql_cur = sql_conn.cursor()

    pg_conn = psycopg2.connect(pg_url, connect_timeout=10)
    pg_cur = pg_conn.cursor()

    # Create tables
    print("Creating tables...")
    for table in TABLES:
        if table in PG_DDL:
            pg_cur.execute(PG_DDL[table])
    pg_conn.commit()
    print("  Done.")

    # Migrate data — use upsert to preserve existing PG data
    for table in TABLES:
        # Check if table exists in SQLite
        sql_cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        if not sql_cur.fetchone():
            print(f"  {table}: not in SQLite, skipping.")
            continue

        sql_cur.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = sql_cur.fetchone()[0]
        if row_count == 0:
            print(f"  {table}: 0 rows in SQLite, skipping.")
            continue

        # For words table, only insert missing words (by id)
        if table == "words":
            sql_cur.execute(f"SELECT * FROM {table}")
            rows = sql_cur.fetchall()
            keys = [d[0] for d in sql_cur.description]
            columns = ", ".join(keys)
            placeholders = ", ".join(["%s"] * len(keys))
            inserted = 0
            for r in rows:
                data = tuple(r[k] for k in keys)
                try:
                    pg_cur.execute(
                        f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING",
                        data,
                    )
                    if pg_cur.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    print(f"    Skip row id={r['id']}: {e}")
            pg_conn.commit()
            print(f"  {table}: {inserted} new rows inserted (skipped existing).")
        else:
            sql_cur.execute(f"SELECT * FROM {table}")
            rows = sql_cur.fetchall()
            keys = [d[0] for d in sql_cur.description]
            columns = ", ".join(keys)
            placeholders = ", ".join(["%s"] * len(keys))
            data = [tuple(r[k] for k in keys) for r in rows]
            psycopg2.extras.execute_values(
                pg_cur,
                f"INSERT INTO {table} ({columns}) VALUES %s ON CONFLICT DO NOTHING",
                data,
                template=f"({placeholders})",
            )
            pg_conn.commit()
            print(f"  {table}: {len(rows)} rows processed.")

    # Reset sequences
    for table in TABLES:
        pg_cur.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
        )
    pg_conn.commit()

    # Verify
    print("\nVerification:")
    for table in TABLES:
        pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = pg_cur.fetchone()[0]
        print(f"  PG {table}: {count} rows")

    pg_cur.close()
    pg_conn.close()
    sql_cur.close()
    sql_conn.close()

    print("\nMigration complete!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_pg.py <postgres_database_url>")
        sys.exit(1)

    pg_url = sys.argv[1]
    sqlite_path = os.path.join(os.path.dirname(__file__), "..", "cet4_vocab.db")

    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite not found: {sqlite_path}")
        sys.exit(1)

    masked = pg_url[: pg_url.index("@")] + "@***" if "@" in pg_url else pg_url
    print(f"SQLite: {sqlite_path}")
    print(f"PG: {masked}\n")
    migrate(sqlite_path, pg_url)
