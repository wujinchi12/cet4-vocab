import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cet4_vocab.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Neon PG requires SSL — add sslmode if not already in URL
    connect_args = {}
    if "sslmode" not in DATABASE_URL:
        connect_args["sslmode"] = "require"
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_schema():
    """Add missing columns to existing tables (safe to call on every startup)."""
    with engine.connect() as conn:
        if DATABASE_URL.startswith("sqlite"):
            # SQLite: check if column exists via PRAGMA
            cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(quiz_history)").fetchall()]
            if "source" not in cols:
                conn.exec_driver_sql('ALTER TABLE quiz_history ADD COLUMN source VARCHAR DEFAULT "all"')
                conn.commit()
        else:
            # PostgreSQL: add column if not exists
            try:
                conn.exec_driver_sql(
                    "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS source VARCHAR DEFAULT 'all'"
                )
                conn.commit()
            except Exception:
                pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
