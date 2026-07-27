"""Parse 四级词汇.docx and insert all words into the database. Idempotent — safe to run multiple times."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from docx import Document
from app.database import SessionLocal, engine, Base
from app.models.word import Word

DOCX_PATH = os.path.join(os.path.dirname(__file__), "..", "四级词汇.docx")


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
    from scripts.enrich_words import extract_pos

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    words = parse_docx(DOCX_PATH)
    existing = db.query(Word).count()

    if existing > 0:
        print(f"Database already has {existing} words, skipping seed.")
        db.close()
        return

    print(f"Seeding {len(words)} words...")
    for w in words:
        pos = extract_pos(w["english"], w["chinese"])
        db.add(Word(english=w["english"], chinese=w["chinese"], part_of_speech=pos))

    db.commit()
    print(f"Seeded {len(words)} words successfully.")
    db.close()


if __name__ == "__main__":
    seed()
