"""Validate synthetic property records and prepare RAG-ready documents."""
import csv
import json
import math
from pathlib import Path

REQUIRED_TEXT = ("property_id", "title", "description", "city", "property_type")


def clean_record(row: dict) -> tuple[dict, list[str]]:
    cleaned = {key: (value or "").strip() for key, value in row.items()}
    errors = []
    for field in REQUIRED_TEXT:
        if not cleaned.get(field):
            errors.append(f"missing_{field}")
    try:
        price = float(cleaned.get("price", ""))
        if not math.isfinite(price) or price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        price = None
        errors.append("invalid_price")
    try:
        area = float(cleaned.get("area_sqft", ""))
        if not math.isfinite(area) or area <= 0:
            raise ValueError
    except (TypeError, ValueError):
        area = None
        errors.append("invalid_area_sqft")
    try:
        bedrooms = int(cleaned.get("bedrooms", ""))
        if bedrooms < 0:
            raise ValueError
    except (TypeError, ValueError):
        bedrooms = None
        errors.append("invalid_bedrooms")
    cleaned.update({"price": price, "area_sqft": area, "bedrooms": bedrooms})
    cleaned["city"] = cleaned.get("city", "").title()
    cleaned["property_type"] = cleaned.get("property_type", "").title()
    return cleaned, errors


def property_document(record: dict) -> dict:
    text = (
        f"{record['title']}. {record['property_type']} in {record['city']}. "
        f"{record['bedrooms']} bedrooms, {record['area_sqft']} square feet. "
        f"Price {record['price']}. {record['description']}"
    )
    return {
        "property_id": record["property_id"],
        "text": text,
        "metadata": {
            "city": record["city"],
            "property_type": record["property_type"],
            "bedrooms": record["bedrooms"],
            "price": record["price"],
            "area_sqft": record["area_sqft"],
        },
    }


def run_pipeline(input_csv: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    valid, rejected, seen_ids = [], [], set()
    with input_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            record, errors = clean_record(row)
            property_id = record.get("property_id", "")
            if property_id and property_id in seen_ids:
                errors.append("duplicate_property_id")
            if property_id:
                seen_ids.add(property_id)
            if errors:
                rejected.append({"property_id": property_id, "reasons": "|".join(errors)})
            else:
                valid.append(record)

    clean_fields = list(valid[0].keys()) if valid else [
        "property_id", "title", "description", "city", "property_type",
        "price", "area_sqft", "bedrooms",
    ]
    with (output_dir / "properties_clean.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=clean_fields)
        writer.writeheader()
        writer.writerows(valid)
    with (output_dir / "rejected_records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["property_id", "reasons"])
        writer.writeheader()
        writer.writerows(rejected)
    with (output_dir / "property_documents.jsonl").open("w", encoding="utf-8") as handle:
        for record in valid:
            handle.write(json.dumps(property_document(record), ensure_ascii=False) + "\n")
    return {"accepted": len(valid), "rejected": len(rejected)}


def main():
    project = Path(__file__).resolve().parents[1]
    result = run_pipeline(project / "data/raw/properties.csv", project / "data/processed")
    print(result)


if __name__ == "__main__":
    main()
