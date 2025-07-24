import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def extract_title_and_outline(pdf_path):
    """
    Extracts the title and the hierarchical outline (H1, H2, H3) from the PDF at pdf_path.
    """
    doc = fitz.open(pdf_path)

    def is_meaningful(text):
        text = text.strip()
        if len(text) <= 3:
            return False
        filtered = re.sub(r'[\s\-\–\—\_\*\~\`\'\"\′\“\”\‘\’\·\•\›\‹\>\<<>]+', '', text)
        return len(filtered) > 0

    # Title extraction
    title = None
    meta_title = doc.metadata.get("title", "")
    if meta_title and is_meaningful(meta_title):
        title = meta_title.strip()

    if not title:
        page1 = doc.load_page(0)
        blocks = page1.get_text("dict")["blocks"]
        spans = []
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    if is_meaningful(text):
                        spans.append({"text": text, "size": size, "origin_y": span["bbox"][1]})
        if spans:
            max_size = max(span["size"] for span in spans)
            largest_spans = [s for s in spans if abs(s["size"] - max_size) < 0.01]
            largest_spans.sort(key=lambda s: s["origin_y"])
            title = largest_spans[0]["text"]

    # Heading extraction
    all_spans = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    if not is_meaningful(text):
                        continue
                    all_spans.append({
                        "text": text,
                        "size": size,
                        "page": page_num + 1,
                        "bbox": span["bbox"]
                    })

    if not all_spans:
        return {"title": title or "", "outline": []}

    unique_sizes = sorted({s["size"] for s in all_spans}, reverse=True)

    clusters = []
    for size in unique_sizes:
        placed = False
        for cluster in clusters:
            if abs(cluster[0] - size) <= 0.5:
                cluster.append(size)
                placed = True
                break
        if not placed:
            clusters.append([size])
    cluster_sizes = [sum(c)/len(c) for c in clusters]

    def map_size_to_level(size):
        for i, csize in enumerate(cluster_sizes[:3]):
            if abs(size - csize) <= 0.5:
                return f"H{i+1}"
        return None

    headings_with_pos = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    if not is_meaningful(text):
                        continue
                    lvl = map_size_to_level(size)
                    if lvl is None:
                        continue
                    headings_with_pos.append({
                        "level": lvl,
                        "text": text,
                        "page": page_num + 1,
                        "y0": span["bbox"][1]
                    })

    seen = set()
    clean_headings = []
    for h in sorted(headings_with_pos, key=lambda x: (x["page"], x["y0"])):
        key = (h["level"], h["text"], h["page"])
        if key in seen:
            continue
        seen.add(key)
        clean_headings.append({"level": h["level"], "text": h["text"], "page": h["page"]})

    return {"title": title or "", "outline": clean_headings}

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    for old in output_dir.glob("*.json"):
        old.unlink()

    for pdf in input_dir.glob("*.pdf"):
        result = extract_title_and_outline(pdf)
        out_file = output_dir / f"{pdf.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"✅ {pdf.name} --> {out_file.name}")

if __name__ == "__main__":
    main()
