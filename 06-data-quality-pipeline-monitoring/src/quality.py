"""Reusable validation rules and batch quality metrics."""
import math
from collections import Counter


REQUIRED_FIELDS = ("product_id", "title", "category", "price", "availability")
VALID_AVAILABILITY = {"in_stock", "out_of_stock", "preorder"}


def validate_record(row: dict) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if not str(row.get(field, "")).strip():
            errors.append(f"missing_{field}")

    raw_price = str(row.get("price", "")).strip()
    try:
        price = float(raw_price)
        if not math.isfinite(price) or price < 0:
            errors.append("invalid_price_range")
    except (TypeError, ValueError):
        errors.append("invalid_price")

    availability = str(row.get("availability", "")).strip().lower()
    if availability and availability not in VALID_AVAILABILITY:
        errors.append("invalid_availability")
    return errors


def process_batch(rows: list[dict], warning_threshold: float = 95.0,
                  failure_threshold: float = 80.0) -> dict:
    if not 0 <= failure_threshold <= warning_threshold <= 100:
        raise ValueError("Thresholds must satisfy 0 <= failure <= warning <= 100")

    accepted, quarantined, seen = [], [], set()
    error_counts = Counter()
    for row in rows:
        errors = validate_record(row)
        product_id = str(row.get("product_id", "")).strip()
        if product_id and product_id in seen:
            errors.append("duplicate_product_id")
        if product_id:
            seen.add(product_id)
        if errors:
            for error in errors:
                error_counts[error] += 1
            quarantined.append({"record": row, "errors": errors})
        else:
            accepted.append(row)

    total = len(rows)
    score = round((len(accepted) / total) * 100, 2) if total else 0.0
    if total == 0 or score < failure_threshold:
        status = "FAILED"
    elif score < warning_threshold:
        status = "WARNING"
    else:
        status = "SUCCESS"

    return {
        "status": status,
        "total_records": total,
        "accepted_records": len(accepted),
        "quarantined_records": len(quarantined),
        "quality_score_percent": score,
        "warning_threshold_percent": warning_threshold,
        "failure_threshold_percent": failure_threshold,
        "error_counts": dict(sorted(error_counts.items())),
        "accepted": accepted,
        "quarantined": quarantined,
    }
