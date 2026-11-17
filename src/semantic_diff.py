import difflib
from pathlib import Path
import cv2
import fitz  # PyMuPDF
import numpy as np
from src.models import DiscrepancySeverity, DocumentDiffReport, PageDiffResult
from src.visual_diff import compare_page_images


def _pixmap_to_bgr(pix: fitz.Pixmap) -> np.ndarray:
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def classify_discrepancy(ssim_score: float, added: list[str], removed: list[str]) -> tuple[DiscrepancySeverity, str]:
    """
    Deterministic severity classifier (can be paired with an LLM prompt returning
    the same DiscrepancySeverity Pydantic schema when API credentials are configured).
    """
    if ssim_score >= 0.999 and not added and not removed:
        return DiscrepancySeverity.NONE, "Page matches baseline identically."
    if added or removed:
        return (
            DiscrepancySeverity.CRITICAL,
            f"Text content changed (+{len(added)} / -{len(removed)} lines) with SSIM={ssim_score}.",
        )
    if ssim_score < 0.98:
        return (
            DiscrepancySeverity.MINOR,
            f"Visual/layout shift detected without text delta (SSIM={ssim_score}).",
        )
    return DiscrepancySeverity.COSMETIC, f"Minor sub-pixel rendering variance (SSIM={ssim_score})."


def compare_pdfs(baseline_pdf: Path, candidate_pdf: Path, artifacts_dir: Path) -> DocumentDiffReport:
    doc_a = fitz.open(baseline_pdf)
    doc_b = fitz.open(candidate_pdf)
    page_count = min(len(doc_a), len(doc_b))
    results: list[PageDiffResult] = []

    for idx in range(page_count):
        page_a = doc_a[idx]
        page_b = doc_b[idx]

        img_a = _pixmap_to_bgr(page_a.get_pixmap(dpi=120))
        img_b = _pixmap_to_bgr(page_b.get_pixmap(dpi=120))
        diff_img_path = artifacts_dir / f"page_{idx + 1}_diff.png"
        ssim_score, box_count = compare_page_images(img_a, img_b, diff_img_path)

        lines_a = [ln.strip() for ln in page_a.get_text("text").splitlines() if ln.strip()]
        lines_b = [ln.strip() for ln in page_b.get_text("text").splitlines() if ln.strip()]

        added = [d[2:] for d in difflib.ndiff(lines_a, lines_b) if d.startswith("+ ")]
        removed = [d[2:] for d in difflib.ndiff(lines_a, lines_b) if d.startswith("- ")]

        severity, summary = classify_discrepancy(ssim_score, added, removed)
        results.append(
            PageDiffResult(
                page_number=idx + 1,
                ssim_score=ssim_score,
                changed_regions_count=box_count,
                severity=severity,
                summary=summary,
                added_lines=added,
                removed_lines=removed,
                diff_image_path=str(diff_img_path),
            )
        )

    passed = all(r.severity in (DiscrepancySeverity.NONE, DiscrepancySeverity.COSMETIC) for r in results)
    return DocumentDiffReport(
        baseline_file=baseline_pdf.name,
        candidate_file=candidate_pdf.name,
        total_pages_compared=page_count,
        overall_passed=passed,
        pages=results,
    )
