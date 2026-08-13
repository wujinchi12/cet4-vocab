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

    # Deduplicate: gunicorn runs multiple workers, each executing startup seeding,
    # so the idempotency check below can be passed by several workers concurrently
    # (english is not globally unique). Remove duplicate CET-6 rows (same english,
    # keep lowest id) to converge back to exactly one row per word.
    from sqlalchemy import func as sqlfunc
    dupes = (
        db.query(Word.english, sqlfunc.count(Word.id))
        .filter(Word.level == "cet6")
        .group_by(Word.english)
        .having(sqlfunc.count(Word.id) > 1)
        .all()
    )
    for english, _ in dupes:
        ids = [row[0] for row in db.query(Word.id).filter(Word.level == "cet6", Word.english == english).order_by(Word.id).all()]
        keep, remove = ids[0], ids[1:]
        for rid in remove:
            db.query(Word).filter(Word.id == rid).delete()
        print(f"Deduped cet6 '{english}': kept id={keep}, removed ids={remove}")
    if dupes:
        db.commit()

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
