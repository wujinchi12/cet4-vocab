"""Seed CET-6 words from cet6_words.json (idempotent — safe to run multiple times)."""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models.word import Word

DATA_PATH = os.path.join(os.path.dirname(__file__), "cet6_words.json")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(Word).filter(Word.level == "cet6").count()
    if existing > 0:
        print(f"CET-6 words already seeded ({existing}), skipping.")
        db.close()
        return

    with open(DATA_PATH, encoding="utf-8") as fh:
        words = json.load(fh)

    for w in words:
        db.add(Word(
            english=w["english"],
            chinese=w["chinese"],
            part_of_speech=w.get("part_of_speech"),
            phonetic=w.get("phonetic"),
            level="cet6",
        ))
    db.commit()
    print(f"Seeded {len(words)} CET-6 words.")
    db.close()


if __name__ == "__main__":
    seed()
