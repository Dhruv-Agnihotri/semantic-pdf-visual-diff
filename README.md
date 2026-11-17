# Hybrid Semantic & Visual Document Comparator

![CI Status](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-SSIM-5C3EE8?logo=opencv&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-Structured_AI-E92063?logo=pydantic&logoColor=white)

A dual-stage document QA pipeline that combines **deterministic computer vision (`OpenCV` + `SSIM`)** with **structured semantic diffing (`PyMuPDF` + `Pydantic` LLM schemas)** to catch both layout regressions and textual/meaning discrepancies across document revisions.

## Why Hybrid Diffing?
- **Pixel-only diffs** break on minor font rendering or pagination shifts.
- **Text-only diffs** miss missing figures, shifted tables, and visual overlap.
- **This pipeline** computes page-level Structural Similarity (SSIM) with bounding-box visual overlays *and* classifies text changes into structured severity levels (`CRITICAL`, `MINOR`, `COSMETIC`) via Pydantic-validated schemas.

## Project Structure

```text
semantic-pdf-visual-diff/
├── src/
│   ├── models.py            # Pydantic v2 schemas for deterministic diff reports
│   ├── visual_diff.py       # OpenCV + SSIM pixel-level diff & contour highlighter
│   ├── semantic_diff.py     # PyMuPDF text extraction + LLM/deterministic semantic analyzer
│   └── report_generator.py  # Self-contained HTML & JSON QA report builder
├── tests/
│   └── test_diff_pipeline.py
├── cli.py                   # Command-line interface
└── requirements.txt
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run automated tests
pytest -v

# Compare two PDF revisions via CLI
python cli.py --baseline v1.pdf --candidate v2.pdf --out reports/diff_report.html
```
