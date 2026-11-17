from pathlib import Path
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def compare_page_images(
    img_a: np.ndarray,
    img_b: np.ndarray,
    highlight_out: Path | None = None,
) -> tuple[float, int]:
    """
    Computes Structural Similarity (SSIM) between two BGR page images and draws
    bounding boxes around changed regions. Returns (ssim_score, contour_count).
    """
    if img_a.shape != img_b.shape:
        img_b = cv2.resize(img_b, (img_a.shape[1], img_a.shape[0]))

    gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)

    score, diff = ssim(gray_a, gray_b, full=True)
    diff_uint8 = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff_uint8, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    significant_boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 40]

    if highlight_out is not None:
        highlight_out.parent.mkdir(parents=True, exist_ok=True)
        annotated = img_b.copy()
        for x, y, w, h in significant_boxes:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imwrite(str(highlight_out), annotated)

    return round(float(score), 4), len(significant_boxes)
