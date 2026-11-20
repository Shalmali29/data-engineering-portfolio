"""Run catalogue quality checks and write operational outputs."""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .quality import process_batch


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "accepted_records.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(result["accepted"][0].keys()) if result["accepted"] else [
            "product_id", "title", "category", "price", "availability"
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["accepted"])

    with (output_dir / "quarantined_records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "product_id", "title", "category", "price", "availability", "validation_errors"
        ])
        writer.writeheader()
        for item in result["quarantined"]:
            row = dict(item["record"])
            row["validation_errors"] = "|".join(item["errors"])
            writer.writerow({key: row.get(key, "") for key in writer.fieldnames})

    report = {key: value for key, value in result.items() if key not in {"accepted", "quarantined"}}
    report["run_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    (output_dir / "quality_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


def main():
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Monitor catalogue data quality.")
    parser.add_argument("--input", type=Path, default=project / "data/raw/products.csv")
    parser.add_argument("--output", type=Path, default=project / "data/processed")
    parser.add_argument("--warning-threshold", type=float, default=95.0)
    parser.add_argument("--failure-threshold", type=float, default=80.0)
    args = parser.parse_args()

    rows = read_rows(args.input)
    result = process_batch(rows, args.warning_threshold, args.failure_threshold)
    write_outputs(result, args.output)
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {"accepted", "quarantined"}}, indent=2))
    if result["status"] == "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
