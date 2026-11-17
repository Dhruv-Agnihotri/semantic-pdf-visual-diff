from enum import Enum
from pydantic import BaseModel, Field


class DiscrepancySeverity(str, Enum):
    NONE = "NONE"
    COSMETIC = "COSMETIC"
    MINOR = "MINOR"
    CRITICAL = "CRITICAL"


class PageDiffResult(BaseModel):
    page_number: int
    ssim_score: float = Field(..., ge=0.0, le=1.0)
    changed_regions_count: int
    severity: DiscrepancySeverity
    summary: str
    added_lines: list[str] = Field(default_factory=list)
    removed_lines: list[str] = Field(default_factory=list)
    diff_image_path: str | None = None


class DocumentDiffReport(BaseModel):
    baseline_file: str
    candidate_file: str
    total_pages_compared: int
    overall_passed: bool
    pages: list[PageDiffResult]
