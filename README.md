# Adobe India Hackathon 2025 — Challenge 1A

## 📄 Overview

This repository contains my solution for **Challenge 1A** of the Adobe India Hackathon 2025.

**Goal:**  
- Process PDF documents in a **resource-constrained**, **offline**, **CPU-only** container.  
- Extract a structured **outline**: 
  - **Title** of the document.
  - Hierarchical **headings** (H1, H2, H3) with page numbers.
- Output **valid JSON** conforming to the required schema.
- Must complete under **10 seconds** for a **50-page PDF**.

---

## ✅ Solution Highlights

- **Language:** Python 3.11
- **Core Library:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **Container:** Docker (`linux/amd64`)

**How it works:**
- For each PDF in `/app/input`:
  - If available, extract title from **PDF metadata**.
  - Fallback: pick the **largest font block** on the first page as title.
  - Parse **all pages**, extract all text spans with **font size** and **position**.
  - Cluster unique font sizes into heading levels (H1, H2, H3) using a ±0.5pt threshold.
  - Sort headings by **page number** and **vertical position** for natural order.
  - Deduplicate repeated headings (e.g., footers, headers).
  - Write `filename.json` into `/app/output`.

- The solution **automatically clears previous output files** each time it runs.

---

## 🚀 Folder Structure

```plaintext
.
├── Dockerfile
├── process_pdfs.py
├── requirements.txt
├── .gitignore
├── sample_dataset/
│   ├── pdfs/            # Input PDFs
│   ├── outputs/         # JSON output (auto-cleared)
│   └── schema/          # Provided output_schema.json
```
---
## 🐳 Docker Build & Run
```bash
docker build --platform linux/amd64 -t adobe-pdf-extractor .
```
```bash
docker run --rm \
  -v $(pwd)/sample_dataset/pdfs:/app/input:ro \
  -v $(pwd)/sample_dataset/outputs:/app/output \
  --network none adobe-pdf-extractor
```
Note:
- Input directory is read-only.
- Output JSONs appear in sample_dataset/outputs/.
- Runtime is offline and uses only CPU.
---
## ✅ Constraints Met
- ✔️ Offline, open-source libraries only.
- ✔️ No internet access at runtime.
- ✔️ Fully CPU-only (amd64).
- ✔️ Output JSON matches output_schema.json.
- ✔️ Execution time under 10 seconds for large PDFs.
- ✔️ Cross-platform: works on both simple & complex PDFs.
- ✔️ Automatic batch processing for all PDFs in /app/input.
---
## 📝 Notes
- Output folder is cleared each run to ensure fresh, accurate results.
- Logic is modular — can be reused for Round 1B with keyword-based enhancements.

The solution is designed for maintainability and easy review by judges.
---
## 👩‍💻 Author
Malavika Gupta

