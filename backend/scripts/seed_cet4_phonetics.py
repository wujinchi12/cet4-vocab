"""Backfill CET-4 phonetics from cet4_phonetics.json (idempotent — safe to run multiple times)."""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models.word import Word

DATA_PATH = os.path.join(os.path.dirname(__file__), "cet4_phonetics.json")
OVERRIDE_PATH = os.path.join(os.path.dirname(__file__), "cet4_phonetics_override.json")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    with open(DATA_PATH, encoding="utf-8") as fh:
        mapping = json.load(fh)

    override = {}
    if os.path.isfile(OVERRIDE_PATH):
        with open(OVERRIDE_PATH, encoding="utf-8") as fh:
            override = json.load(fh)

    updated = 0
    for w in db.query(Word).filter(Word.level == "cet4").all():
        if w.phonetic:
            continue
        key = w.english.lower()
        ph = mapping.get(key) or override.get(key)
        if ph:
            w.phonetic = ph
            updated += 1
    db.commit()
    print(f"Backfilled phonetics for {updated} CET-4 words.")
    db.close()


if __name__ == "__main__":
    seed()
