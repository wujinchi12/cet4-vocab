"""Parse 四级词汇.docx, extract POS via heuristics, add missing words, update POS for existing words."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from docx import Document
from app.database import SessionLocal, engine, Base
from app.models.word import Word

DOCX_PATH = os.path.join(os.path.dirname(__file__), "..", "四级词汇.docx")


def extract_pos(english: str, chinese: str) -> str:
    """Heuristic POS extraction from English suffix and Chinese definition patterns."""
    eng = english.lower()
    pos_tags = []

    # Chinese definition heuristics (strong signals)
    parts = chinese.replace("，", ",").split(",")
    parts = [p.strip() for p in parts]

    has_adj = any(p.endswith("的") for p in parts)
    has_adv = any(p.endswith("地") for p in parts)

    # English suffix heuristics
    noun_suffixes = [
        "tion", "sion", "ment", "ness", "ity", "ty", "ance", "ence",
        "ure", "dom", "ship", "hood", "ology", "ism", "ist", "er", "or",
        "ee", "ian", "th", "tude", "sure", "cy", "ry", "phy", "gy", "my",
    ]
    verb_suffixes = ["ate", "ize", "ify", "ise"]
    adj_suffixes = [
        "ive", "ous", "ious", "ful", "less", "able", "ible",
        "al", "ial", "ic", "ish", "ary", "ory", "like", "some",
    ]

    is_noun = any(eng.endswith(s) and len(eng) > len(s) + 1 for s in noun_suffixes)
    is_verb = any(eng.endswith(s) and len(eng) > len(s) + 1 for s in verb_suffixes)
    is_adj = any(eng.endswith(s) and len(eng) > len(s) + 1 for s in adj_suffixes)
    is_adv = eng.endswith("ly") and len(eng) > 4

    # Combine signals
    if is_noun or (not is_verb and not is_adj and not is_adv):
        pos_tags.append("n.")
    if is_verb or (any(p.endswith("化") for p in parts)):
        pos_tags.append("v.")
    if is_adj or has_adj:
        pos_tags.append("adj.")
    if is_adv or has_adv:
        pos_tags.append("adv.")

    # Ensure at least one tag
    if not pos_tags:
        pos_tags.append("other")

    return " ".join(pos_tags)


def parse_docx(path: str) -> list[dict]:
    doc = Document(path)
    words = []
    seen = set()
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        parts = text.split(None, 1)
        if len(parts) != 2:
            continue
        english = parts[0].strip()
        chinese = parts[1].strip()
        key = (english.lower(), chinese)
        if key in seen:
            continue
        seen.add(key)
        words.append({"english": english, "chinese": chinese})
    return words


def enrich():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Quick check: only parse docx if DB needs enrichment
    total = db.query(Word).count()
    null_pos_count = db.query(Word).filter(Word.part_of_speech == None).count()

    if total >= 4410 and null_pos_count == 0:
        db.close()
        return

    # Parse docx for full enrichment
    docx_words = parse_docx(DOCX_PATH)
    print(f"Docx entries (deduplicated): {len(docx_words)}")

    # Build lookup of existing words
    existing = db.query(Word).all()
    existing_map = {}
    for w in existing:
        key = (w.english.lower(), w.chinese)
        existing_map[key] = w

    print(f"Existing words in DB: {len(existing)}")

    # Find missing (same english+chinese combo not in DB)
    missing = []
    for w in docx_words:
        key = (w["english"].lower(), w["chinese"])
        if key not in existing_map:
            missing.append(w)

    print(f"Missing words to add: {len(missing)}")

    if missing:
        for w in missing:
            pos = extract_pos(w["english"], w["chinese"])
            db.add(Word(english=w["english"], chinese=w["chinese"], part_of_speech=pos))
        db.commit()
        print(f"Added {len(missing)} missing words.")

    # Update POS for words that don't have it
    null_pos = db.query(Word).filter(Word.part_of_speech == None).all()
    print(f"Words without POS: {len(null_pos)}")

    if null_pos:
        for w in null_pos:
            w.part_of_speech = extract_pos(w.english, w.chinese)
        db.commit()
        print(f"Updated POS for {len(null_pos)} words.")

    # Summary
    total = db.query(Word).count()
    pos_counts = {}
    for w in db.query(Word).all():
        for tag in (w.part_of_speech or "other").split():
            pos_counts[tag] = pos_counts.get(tag, 0) + 1
    print(f"\nTotal words: {total}")
    print(f"POS distribution: {pos_counts}")

    db.close()


if __name__ == "__main__":
    enrich()
