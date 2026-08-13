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
    migrations = {
        "quiz_history": [("source", "VARCHAR DEFAULT 'all'")],
        "words": [
            ("level", "VARCHAR DEFAULT 'cet4'"),
            ("phonetic", "VARCHAR"),
        ],
    }
    with engine.connect() as conn:
        if DATABASE_URL.startswith("sqlite"):
            for table, cols in migrations.items():
                existing = [row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()]
                for name, ddl in cols:
                    if name not in existing:
                        conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
            conn.commit()
        else:
            for table, cols in migrations.items():
                for name, ddl in cols:
                    try:
                        conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {name} {ddl}")
                    except Exception:
                        pass
            conn.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
