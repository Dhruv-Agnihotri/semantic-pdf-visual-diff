import argparse
from pathlib import Path
from src.report_generator import write_html_report
from src.semantic_diff import compare_pdfs


def main() -> None:
    parser = argparse.ArgumentParser(description="Hybrid Semantic & Visual PDF Comparator")
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline PDF path")
    parser.add_argument("--candidate", type=Path, required=True, help="Candidate PDF path")
    parser.add_argument("--out", type=Path, default=Path("reports/diff_report.html"), help="HTML report path")
    args = parser.parse_args()

    report = compare_pdfs(args.baseline, args.candidate, args.out.parent / "artifacts")
    write_html_report(report, args.out)
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
