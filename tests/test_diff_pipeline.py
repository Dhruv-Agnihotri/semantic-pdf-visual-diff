from pathlib import Path
import fitz
from src.models import DiscrepancySeverity
from src.report_generator import write_html_report
from src.semantic_diff import compare_pdfs


def _make_sample_pdf(path: Path, body_text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Release Specification v1.0", fontsize=16)
    page.insert_text((72, 110), body_text, fontsize=12)
    doc.save(path)


def test_detects_semantic_and_visual_change(tmp_path: Path):
    pdf_a = tmp_path / "baseline.pdf"
    pdf_b = tmp_path / "candidate.pdf"
    _make_sample_pdf(pdf_a, "Max concurrency limit: 10 workers.")
    _make_sample_pdf(pdf_b, "Max concurrency limit: 25 workers.")

    report = compare_pdfs(pdf_a, pdf_b, tmp_path / "artifacts")
    html_file = write_html_report(report, tmp_path / "report.html")

    assert report.overall_passed is False
    assert report.pages[0].severity == DiscrepancySeverity.CRITICAL
    assert "Max concurrency limit: 25 workers." in report.pages[0].added_lines
    assert html_file.exists()
