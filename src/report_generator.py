from pathlib import Path
from src.models import DocumentDiffReport


def write_html_report(report: DocumentDiffReport, output_html: Path) -> Path:
    output_html.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in report.pages:
        rows.append(
            f"<tr><td>{p.page_number}</td><td>{p.ssim_score}</td>"
            f"<td>{p.changed_regions_count}</td><td><b>{p.severity.value}</b></td>"
            f"<td>{p.summary}</td></tr>"
        )
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>PDF Visual & Semantic Diff Report</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 24px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
  th {{ background: #1e293b; color: #fff; }}
</style></head>
<body>
  <h2>Document Comparison Report: {report.baseline_file} vs {report.candidate_file}</h2>
  <p>Overall Status: <b>{"PASS" if report.overall_passed else "DISCREPANCIES FOUND"}</b></p>
  <table>
    <thead><tr><th>Page</th><th>SSIM</th><th>Visual Diff Boxes</th><th>Severity</th><th>Summary</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body></html>"""
    output_html.write_text(html, encoding="utf-8")
    return output_html
