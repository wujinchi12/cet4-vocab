"""Parse 四级词汇.docx and insert all words into the database. Idempotent — safe to run multiple times."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from docx import Document
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal, engine, Base
from app.models.word import Word

DOCX_PATH = os.path.join(os.path.dirname(__file__), "..", "四级词汇.docx")
EXPECTED_COUNT = 4417


def parse_docx(path: str) -> list[dict]:
    doc = Document(path)
    words = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        parts = text.split(None, 1)
        if len(parts) != 2:
            continue
        english = parts[0].strip()
        chinese = parts[1].strip()
        words.append({"english": english, "chinese": chinese})
    return words


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(Word).count()

    if existing == EXPECTED_COUNT:
        print(f"Database has {existing} words. Skipping seed.")
        db.close()
        return

    # Data is missing or duplicated — clean and reseed
    if existing > 0:
        print(f"Found {existing} word records (expected {EXPECTED_COUNT}), cleaning up...")
        db.query(Word).delete()
        db.commit()

    words = parse_docx(DOCX_PATH)
    print(f"Seeding {len(words)} words...")
    for w in words:
        db.add(Word(english=w["english"], chinese=w["chinese"]))

    try:
        db.commit()
        print(f"Seeded {len(words)} words successfully.")
    except IntegrityError:
        db.rollback()
        print("Seed already completed by another process.")

    db.close()


if __name__ == "__main__":
    seed()
