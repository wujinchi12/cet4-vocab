"""Correct malformed CET-4 words in-place (idempotent — safe to run multiple times)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models.word import Word

FIXES = [
    # (english_to_find, new_english, old_chinese, new_chinese)
    ("o'clock=of", "o'clock", "the clock …点钟", "…点钟"),
    ("reservior", "reservoir", None, None),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    changed = 0

    for find, new_english, old_chinese, new_chinese in FIXES:
        w = db.query(Word).filter(Word.english == find).first()
        if not w:
            continue
        w.english = new_english
        if old_chinese is not None and w.chinese == old_chinese:
            w.chinese = new_chinese
        changed += 1
        print(f"Fixed '{find}' -> '{new_english}'")

    if changed:
        db.commit()
    db.close()


if __name__ == "__main__":
    seed()
