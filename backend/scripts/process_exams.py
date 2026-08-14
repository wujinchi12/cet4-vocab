"""Process raw CET-4 past papers (PDF / DOC / DOCX) into a web-servable 真题库.

For each source file:
  * .doc / .docx are converted to PDF via Word COM (Windows only).
  * Large PDFs (>= 3 MB, i.e. scanned images) are rasterized to 150 DPI
    grayscale JPEG pages to shrink them drastically.
  * Small / text PDFs are re-saved with garbage collection + deflate.
Output goes to backend/static/exams/ together with an index.json manifest
that the frontend reads to render the 真题库.

Usage:
    python backend/scripts/process_exams.py [SOURCE_DIR]

SOURCE_DIR defaults to where the zip was extracted (F:/test2/.exam_tmp).
"""
import json
import os
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

import fitz  # PyMuPDF

SOURCE_DIR = "F:/test2/.exam_tmp"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "exams")
RASTERIZE_THRESHOLD = 3 * 1024 * 1024  # rasterize PDFs >= 3 MB
RASTER_DPI = 150
RASTER_JPEG_QUALITY = 80


# ---------------------------------------------------------------------------
# Metadata for the 30 papers.
#   src      : filename inside SOURCE_DIR
#   slug     : normalized output filename (no extension)
#   title    : clean display title
#   year     : exam year (0 = unknown / mixed)
#   month    : exam month (0 = unknown)
#   set      : 套数 (0 = N/A or 全3套/合集)
#   category : 试卷 | 听力原文 | 写作 | 答案 | 合集
#   note     : extra info (含答案 / 含答案解析 / ...)
# ---------------------------------------------------------------------------
PAPERS = [
    {"src": "2024年6月英语四级真题试卷第1套（含答案）.pdf", "slug": "2024-06-s1", "title": "2024年6月 第1套", "year": 2024, "month": 6, "set": 1, "category": "试卷", "note": "含答案"},
    {"src": "2024年6月英语四级真题试卷第2套（含答案）.pdf", "slug": "2024-06-s2", "title": "2024年6月 第2套", "year": 2024, "month": 6, "set": 2, "category": "试卷", "note": "含答案"},
    {"src": "2024年12月英语四级真题试卷第1套（含答案解析）.pdf", "slug": "2024-12-s1", "title": "2024年12月 第1套", "year": 2024, "month": 12, "set": 1, "category": "试卷", "note": "含答案解析"},
    {"src": "2024年12月英语四级真题试卷第2套（含答案解析）.pdf", "slug": "2024-12-s2", "title": "2024年12月 第2套", "year": 2024, "month": 12, "set": 2, "category": "试卷", "note": "含答案解析"},
    {"src": "2025年6月大学英语四级真题试卷第2套（含答案解析）.pdf", "slug": "2025-06-s2", "title": "2025年6月 第2套", "year": 2025, "month": 6, "set": 2, "category": "试卷", "note": "含答案解析"},
    {"src": "2025年6月大学英语四级真题试卷听力原文及解析(第1套).pdf", "slug": "2025-06-s1-listening", "title": "2025年6月 第1套 听力原文", "year": 2025, "month": 6, "set": 1, "category": "听力原文", "note": "含解析"},
    {"src": "2025年全国大学英语四级考试写作真题.docx", "slug": "2025-writing", "title": "2025年 写作真题", "year": 2025, "month": 0, "set": 0, "category": "写作", "note": ""},
    {"src": "2023年3月英语四级真题试卷全3套(含答案解析).pdf", "slug": "2023-03-all", "title": "2023年3月 全3套", "year": 2023, "month": 3, "set": 0, "category": "试卷", "note": "含答案解析"},
    {"src": "2023年6月英语四级真题试卷第1套（含答案解析）.pdf", "slug": "2023-06-s1", "title": "2023年6月 第1套", "year": 2023, "month": 6, "set": 1, "category": "试卷", "note": "含答案解析"},
    {"src": "2023年12月英语四级真题试卷第2套（含答案解析）.pdf", "slug": "2023-12-s2", "title": "2023年12月 第2套", "year": 2023, "month": 12, "set": 2, "category": "试卷", "note": "含答案解析"},
    {"src": "2023年12月英语四级真题试卷第3套（含答案解析）.pdf", "slug": "2023-12-s3", "title": "2023年12月 第3套", "year": 2023, "month": 12, "set": 3, "category": "试卷", "note": "含答案解析"},
    {"src": "2022年6月英语四级真题试卷（含答案解析）—听力原文.pdf", "slug": "2022-06-listening", "title": "2022年6月 听力原文", "year": 2022, "month": 6, "set": 0, "category": "听力原文", "note": "含答案解析"},
    {"src": "2022年12月英语四级真题试卷第2套（含答案解析）.pdf", "slug": "2022-12-s2", "title": "2022年12月 第2套", "year": 2022, "month": 12, "set": 2, "category": "试卷", "note": "含答案解析"},
    {"src": "2021年6月英语四级真题试卷第1套（含答案解析）.pdf", "slug": "2021-06-s1", "title": "2021年6月 第1套", "year": 2021, "month": 6, "set": 1, "category": "试卷", "note": "含答案解析"},
    {"src": "2021年6月英语四级真题试卷第2套.pdf", "slug": "2021-06-s2", "title": "2021年6月 第2套", "year": 2021, "month": 6, "set": 2, "category": "试卷", "note": ""},
    {"src": "2021年12月英语四级真题试卷第1套.pdf", "slug": "2021-12-s1", "title": "2021年12月 第1套", "year": 2021, "month": 12, "set": 1, "category": "试卷", "note": ""},
    {"src": "2021年12月CET4真题参考答案A卷(北京).pdf", "slug": "2021-12-answer-a", "title": "2021年12月 参考答案(A卷)", "year": 2021, "month": 12, "set": 0, "category": "答案", "note": "北京卷"},
    {"src": "2021年大学英语四级真题试卷听力原文及解析.pdf", "slug": "2021-listening", "title": "2021年 听力原文及解析", "year": 2021, "month": 0, "set": 0, "category": "听力原文", "note": ""},
    {"src": "历年大学英语四级cet-4作文真题试卷写作范文.doc", "slug": "writing-samples", "title": "历年四级作文真题范文", "year": 0, "month": 0, "set": 0, "category": "写作", "note": "历年合集"},
    {"src": "历年大学英语四级(CET-4)真题试卷及参考答案.doc", "slug": "collection-4", "title": "历年四级真题及参考答案", "year": 0, "month": 0, "set": 0, "category": "合集", "note": "历年合集"},
    {"src": "四级考试试卷真题及答案.docx", "slug": "collection-1", "title": "四级考试真题及答案", "year": 0, "month": 0, "set": 0, "category": "合集", "note": "历年合集"},
    {"src": "四级真题试卷历年真题及答案.docx", "slug": "collection-2", "title": "四级真题历年真题及答案", "year": 0, "month": 0, "set": 0, "category": "合集", "note": "历年合集"},
    {"src": "四级英语考试真题试卷及答案.docx", "slug": "collection-3", "title": "四级英语真题试卷及答案", "year": 0, "month": 0, "set": 0, "category": "合集", "note": "历年合集"},
    {"src": "四级考试近年试卷真题及答案.docx", "slug": "collection-5", "title": "四级近年试卷真题及答案", "year": 0, "month": 0, "set": 0, "category": "合集", "note": "近年合集"},
    {"src": "大学生英语CET四级真题试卷5篇.pdf", "slug": "collection-5papers", "title": "大学生英语CET四级真题5篇", "year": 0, "month": 0, "set": 0, "category": "合集", "note": "5篇"},
    {"src": "大学英语四级（CET-4）真题试卷.pdf", "slug": "cet4-paper-1", "title": "大学英语四级（CET-4）真题试卷", "year": 0, "month": 0, "set": 0, "category": "试卷", "note": ""},
    {"src": "大学英语四级考试试题真题.pdf", "slug": "cet4-paper-2", "title": "大学英语四级考试试题真题", "year": 0, "month": 0, "set": 0, "category": "试卷", "note": ""},
    {"src": "大学英语四级考试真题卷.pdf", "slug": "cet4-paper-3", "title": "大学英语四级考试真题卷", "year": 0, "month": 0, "set": 0, "category": "试卷", "note": ""},
    {"src": "大学英语四级考试真题.pdf", "slug": "cet4-paper-4", "title": "大学英语四级考试真题", "year": 0, "month": 0, "set": 0, "category": "试卷", "note": ""},
    {"src": "大学英语四级(CET-4)真题.pdf", "slug": "cet4-paper-5", "title": "大学英语四级(CET-4)真题", "year": 0, "month": 0, "set": 0, "category": "试卷", "note": ""},
]


def word_to_pdf(src, dst):
    """Convert a legacy .doc to PDF using Word COM automation (Windows)."""
    src_win = src.replace("/", "\\")
    dst_win = dst.replace("/", "\\")
    ps = (
        "$w = New-Object -ComObject Word.Application; "
        "$w.Visible = $false; "
        "$w.DisplayAlerts = 0; "
        f"$d = $w.Documents.Open('{src_win}'); "
        f"$d.SaveAs([ref]'{dst_win}', [ref]17); "
        "$d.Close(); "
        "$w.Quit()"
    )
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", ps],
        check=True, capture_output=True, timeout=120,
    )


_W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _wrap_text(text, max_width, fontsize):
    out = []
    cur = ""
    for ch in text:
        if fitz.get_text_length(cur + ch, fontname="china-s", fontsize=fontsize) <= max_width:
            cur += ch
        else:
            if cur:
                out.append(cur)
            cur = ch
    if cur:
        out.append(cur)
    return out


def docx_to_pdf(src, dst):
    """Convert a .docx to a text PDF by parsing word/document.xml directly.

    Robust against .docx files that Word reports as "corrupted" but whose ZIP
    structure is intact. Layout is plain text (questions/answers), which is all
    these collection files contain.
    """
    with zipfile.ZipFile(src) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs = []
    for p in root.iter(_W_NS + "p"):
        runs = [t.text or "" for t in p.iter(_W_NS + "t")]
        paragraphs.append("".join(runs).strip())

    A4 = (595.0, 842.0)
    margin = 50.0
    fontsize = 11
    lineheight = fontsize * 1.5
    max_width = A4[0] - 2 * margin

    lines = []
    for para in paragraphs:
        if not para:
            lines.append("")
            continue
        lines.extend(_wrap_text(para, max_width, fontsize))

    doc = fitz.open()
    y = margin
    page = doc.new_page(width=A4[0], height=A4[1])
    for line in lines:
        if y + lineheight > A4[1] - margin:
            page = doc.new_page(width=A4[0], height=A4[1])
            y = margin
        if line:
            page.insert_text((margin, y + fontsize), line, fontname="china-s", fontsize=fontsize)
        y += lineheight

    doc.save(dst, garbage=4, deflate=True)
    doc.close()


def rasterize(src, dst):
    """Rebuild a scanned PDF from downsampled grayscale JPEG pages."""
    src_doc = fitz.open(src)
    out_doc = fitz.open()
    for page in src_doc:
        rect = page.rect
        pix = page.get_pixmap(dpi=RASTER_DPI, colorspace=fitz.csGRAY)
        jpg = pix.tobytes(output="jpeg", jpg_quality=RASTER_JPEG_QUALITY)
        new_page = out_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(new_page.rect, stream=jpg)
    out_doc.save(dst, garbage=4, deflate=True)
    out_doc.close()
    src_doc.close()


def resave(src, dst):
    """Re-save a text/small PDF with garbage collection + deflate."""
    doc = fitz.open(src)
    doc.save(dst, garbage=4, deflate=True)
    doc.close()


def process():
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = SOURCE_DIR

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    manifest = []
    failures = []

    for i, paper in enumerate(PAPERS, 1):
        src_path = os.path.join(source_dir, paper["src"])
        slug = paper["slug"]
        out_pdf = os.path.join(OUTPUT_DIR, slug + ".pdf")

        if not os.path.isfile(src_path):
            failures.append(f"{paper['src']}: source not found")
            print(f"[{i}/{len(PAPERS)}] MISSING {paper['src']}")
            continue

        try:
            ext = os.path.splitext(paper["src"])[1].lower()
            working_pdf = src_path

            if ext == ".docx":
                tmp_pdf = os.path.join(OUTPUT_DIR, f"_{slug}.tmp.pdf")
                docx_to_pdf(src_path, tmp_pdf)
                working_pdf = tmp_pdf
            elif ext == ".doc":
                tmp_pdf = os.path.join(OUTPUT_DIR, f"_{slug}.tmp.pdf")
                word_to_pdf(src_path, tmp_pdf)
                working_pdf = tmp_pdf

            size = os.path.getsize(working_pdf)
            if size >= RASTERIZE_THRESHOLD:
                rasterize(working_pdf, out_pdf)
            else:
                resave(working_pdf, out_pdf)

            if working_pdf.endswith(".tmp.pdf") and os.path.isfile(working_pdf):
                os.remove(working_pdf)

            final_size = os.path.getsize(out_pdf)
            with fitz.open(out_pdf) as d:
                pages = d.page_count

            entry = {
                "slug": slug,
                "title": paper["title"],
                "year": paper["year"],
                "month": paper["month"],
                "set": paper["set"],
                "category": paper["category"],
                "note": paper["note"],
                "filename": slug + ".pdf",
                "size": final_size,
                "pages": pages,
            }
            manifest.append(entry)
            print(f"[{i}/{len(PAPERS)}] OK {paper['title']}: "
                  f"{size/1e6:.1f}MB -> {final_size/1e6:.1f}MB, {pages}p")
        except Exception as e:
            failures.append(f"{paper['src']}: {e}")
            print(f"[{i}/{len(PAPERS)}] FAIL {paper['src']}: {e}")

    manifest.sort(key=lambda e: (e["year"], e["month"], e["set"]), reverse=True)
    index_path = os.path.join(OUTPUT_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"version": "2.4", "generated_at": time.strftime("%Y-%m-%d"),
                   "count": len(manifest), "papers": manifest},
                  f, ensure_ascii=False, indent=2)

    print(f"\nDone: {len(manifest)} papers -> {OUTPUT_DIR}")
    if failures:
        print("Failures:")
        for f in failures:
            print("  -", f)


if __name__ == "__main__":
    process()
