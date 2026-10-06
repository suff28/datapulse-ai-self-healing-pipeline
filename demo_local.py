from pathlib import Path

import pandas as pd

from src.generator import generate_orders
from src.normalizer import coerce_types, normalize_columns
from src.quality import compute_quality_score, flatten_issues, quality_checks, validate_orders
from src.repair_engine import build_repair_suggestions, explain_run


def main():
    sample_dir = Path("sample_output")
    sample_dir.mkdir(exist_ok=True)
    input_path = sample_dir / "messy_orders.csv"
    generate_orders(input_path, rows=250, messy=True)

    raw = pd.read_csv(input_path)
    normalized, rename_map = normalize_columns(raw)
    typed = coerce_types(normalized)
    clean, quarantine, global_issues = validate_orders(typed)
    issues = flatten_issues(quarantine, global_issues)
    score = compute_quality_score(len(raw), len(quarantine), any(i["issue_type"] == "missing_column" for i in issues))
    checks = quality_checks(len(raw), len(clean), len(quarantine), issues)
    suggestions = build_repair_suggestions(issues)
    summary = explain_run(len(raw), len(clean), len(quarantine), issues)

    clean_path = sample_dir / "clean_orders.csv"
    quarantine_path = sample_dir / "quarantined_records.csv"
    report_path = sample_dir / "datapulse_report.html"

    clean.to_csv(clean_path, index=False)
    pd.DataFrame(quarantine).to_csv(quarantine_path, index=False)
    _write_report(report_path, summary, score, rename_map, checks, suggestions)

    print(summary)
    print(f"Quality score: {score}")
    print(f"Clean output: {clean_path}")
    print(f"Quarantine output: {quarantine_path}")
    print(f"Report: {report_path}")


def _write_report(path: Path, summary: str, score: float, rename_map: dict, checks: list[dict], suggestions: list[dict]):
    checks_html = pd.DataFrame(checks).to_html(index=False)
    suggestions_html = pd.DataFrame(suggestions).to_html(index=False)
    html = f"""
    <html>
    <head>
      <title>DataPulse Local Report</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #17202a; }}
        .score {{ font-size: 42px; font-weight: 700; color: #0f766e; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f4f6f8; }}
      </style>
    </head>
    <body>
      <h1>DataPulse: AI Self-Healing Data Pipeline</h1>
      <p>{summary}</p>
      <div class="score">{score}</div>
      <h2>Column Mapping</h2>
      <pre>{rename_map}</pre>
      <h2>Quality Checks</h2>
      {checks_html}
      <h2>Repair Suggestions</h2>
      {suggestions_html}
    </body>
    </html>
    """
    path.write_text(html)


if __name__ == "__main__":
    main()
