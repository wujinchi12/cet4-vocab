"""Extract CET-6 words from blank.apkg (Anki package) into cet6_words.json.

One-off utility. The generated JSON is committed so seed_cet6.py can import
CET-6 words on both local and Railway (which has no access to the .apkg).
"""
import os
import sys
import json
import re
import sqlite3
import zipfile
import html
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

APKG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "blank.apkg")
OUT_PATH = os.path.join(os.path.dirname(__file__), "cet6_words.json")

POS_MAP = {
    "pos_n": "n.",
    "pos_v": "v.",
    "pos_a": "adj.",
    "pos_r": "adv.",
    "pos_prep": "prep.",
    "pos_conj": "conj.",
    "pos_num": "num.",
    "pos_pron": "pron.",
    "pos_int": "int.",
    "pos_art": "art.",
    "pos_aux": "aux.",
    "pos_abbr": "abbr.",
}


def parse_definition(raw: str) -> tuple[str, str | None]:
    pos_set = []

    def repl(m):
        cls = m.group(1)
        label = m.group(2).strip()
        norm = "v." if label in ("vt.", "vi.") else POS_MAP.get(cls, label)
        if norm and norm not in pos_set:
            pos_set.append(norm)
        return ""

    text = re.sub(r"<a class='pos_(\w+)'>([^<]*)</a>", repl, raw or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text, " ".join(pos_set) or None


def clean_phonetic(raw) -> str | None:
    if not raw:
        return None
    text = re.sub(r"<[^>]+>", "", raw)
    text = html.unescape(text).replace("\xa0", " ").strip()
    return text or None


def extract():
    with zipfile.ZipFile(APKG_PATH) as z:
        data = z.read("collection.anki2")

    with tempfile.NamedTemporaryFile(suffix=".anki2", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        db = sqlite3.connect(tmp_path)
        cur = db.cursor()
        cur.execute("SELECT flds FROM notes")
        words = []
        for (flds,) in cur.fetchall():
            f = flds.split("\x1f")
            english = (f[0] or "").strip()
            if not english:
                continue
            phonetic = clean_phonetic(f[1] if len(f) > 1 else None)
            chinese, pos = parse_definition(f[2] if len(f) > 2 else "")
            words.append({
                "english": english,
                "chinese": chinese,
                "part_of_speech": pos,
                "phonetic": phonetic,
            })
        db.close()
    finally:
        os.unlink(tmp_path)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(words, fh, ensure_ascii=False, indent=2)
    print(f"Extracted {len(words)} words -> {OUT_PATH}")


if __name__ == "__main__":
    extract()
