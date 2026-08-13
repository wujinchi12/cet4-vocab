"""Extract CET-4 English->phonetic map from a shared Anki deck zip.

One-off utility. The generated JSON is committed so seed_cet4_phonetics.py can
backfill phonetics on both local and Railway (which has no access to the zip).
"""
import os
import re
import html
import json
import sqlite3
import zipfile
import tempfile

ZIP_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "svc_shared_download-deck_518356188.zip")
OUT_PATH = os.path.join(os.path.dirname(__file__), "cet4_phonetics.json")


def clean_phonetic(raw):
    if not raw:
        return None
    text = re.sub(r"<[^>]+>", "", html.unescape(raw))
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def extract():
    with zipfile.ZipFile(ZIP_PATH) as z:
        data = z.read("collection.anki2")

    tmp = tempfile.NamedTemporaryFile(suffix=".anki2", delete=False)
    tmp.write(data)
    tmp.close()

    try:
        db = sqlite3.connect(tmp.name)
        cur = db.cursor()
        cur.execute("SELECT flds FROM notes")
        mapping = {}
        for (flds,) in cur.fetchall():
            f = flds.split("\x1f")
            english = (f[0] or "").strip()
            phonetic = clean_phonetic(f[1] if len(f) > 1 else None)
            if english and phonetic:
                mapping[english.lower()] = phonetic
        db.close()
    finally:
        os.unlink(tmp.name)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=2)
    print(f"Extracted {len(mapping)} phonetics -> {OUT_PATH}")


if __name__ == "__main__":
    extract()
