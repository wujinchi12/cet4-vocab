"""Parse 四级词汇.docx and insert all words into the SQLite database."""
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
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(Word).count()
    if existing > 0:
        print(f"Database already has {existing} words. Skipping seed.")
        db.close()
        return

    words = parse_docx(DOCX_PATH)
    for w in words:
        db.add(Word(english=w["english"], chinese=w["chinese"]))

    db.commit()
    print(f"Seeded {len(words)} words.")
    db.close()


if __name__ == "__main__":
    seed()
