"""Run canonical transformation and export three destination payloads."""
import json
from pathlib import Path
from .catalogue import (
    load_rows, to_canonical, map_schema_a, map_schema_b, map_schema_c,
)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def run(input_path: Path, output_dir: Path) -> dict:
    canonical_records = []
    report = []
    for row in load_rows(input_path):
        canonical, issues = to_canonical(row)
        canonical_records.append(canonical)
        if issues:
            report.append({"product_id": canonical["product_id"], "issues": issues})

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "schema_a.jsonl", [map_schema_a(p) for p in canonical_records])
    write_jsonl(output_dir / "schema_b.jsonl", [map_schema_b(p) for p in canonical_records])
    write_jsonl(output_dir / "schema_c.jsonl", [map_schema_c(p) for p in canonical_records])
    (output_dir / "validation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return {
        "records_processed": len(canonical_records),
        "records_with_issues": len(report),
        "outputs": ["schema_a.jsonl", "schema_b.jsonl", "schema_c.jsonl", "validation_report.json"],
    }


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    result = run(project / "data/raw/products.csv", project / "data/processed")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
