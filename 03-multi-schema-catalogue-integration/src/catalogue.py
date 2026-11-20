"""Canonical catalogue model and destination schema transformations."""
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


def _json_list(value: str, field: str) -> tuple[list[dict[str, Any]], str | None]:
    try:
        parsed = json.loads(value or "[]")
        if not isinstance(parsed, list) or any(not isinstance(item, dict) for item in parsed):
            raise ValueError("expected a JSON array of objects")
        return parsed, None
    except (json.JSONDecodeError, ValueError) as exc:
        return [], f"{field}: {exc}"


def to_canonical(row: dict[str, str]) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    try:
        amount = Decimal(row.get("price", ""))
        if not amount.is_finite() or amount < 0:
            raise InvalidOperation
        price = str(amount)
    except (InvalidOperation, ValueError):
        price = None
        issues.append("price: missing or invalid non-negative decimal")

    variants, variant_error = _json_list(row.get("variants_json", ""), "variants")
    warehouses, warehouse_error = _json_list(row.get("warehouses_json", ""), "warehouses")
    if variant_error:
        issues.append(variant_error)
    if warehouse_error:
        issues.append(warehouse_error)

    stock_total = 0
    stock_known = True
    for warehouse in warehouses:
        try:
            quantity = int(warehouse["stock"])
            if quantity < 0:
                raise ValueError("negative stock")
            stock_total += quantity
        except (KeyError, TypeError, ValueError):
            stock_known = False
            issues.append(f"warehouse {warehouse.get('warehouse_id', 'unknown')}: invalid stock")

    images = [url for url in (row.get("image_urls") or "").split("|") if url]
    canonical = {
        "product_id": (row.get("product_id") or "").strip() or None,
        "title": (row.get("title") or "").strip() or None,
        "description": (row.get("description") or "").strip() or None,
        "category": (row.get("category") or "").strip() or None,
        "price": price,
        "currency": (row.get("currency") or "").strip() or None,
        "image_urls": images,
        "variants": variants,
        "warehouses": warehouses,
        "total_stock": stock_total if stock_known else None,
    }
    for required in ("product_id", "title", "category", "price", "currency"):
        if not canonical[required]:
            issues.append(f"{required}: required field is missing")
    if not canonical["description"]:
        issues.append("description: missing optional content")
    if not canonical["image_urls"]:
        issues.append("image_urls: no product images")
    return canonical, issues


def _set_path(target: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def map_schema_a(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": product["product_id"],
        "title": product["title"],
        "description": product["description"],
        "category": product["category"],
        "price": product["price"],
        "currency": product["currency"],
        "images": product["image_urls"],
        "variants": product["variants"],
        "stock": product["total_stock"],
    }


def map_schema_b(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "productId": product["product_id"],
        "name": product["title"],
        "longDescription": product["description"],
        "taxonomy": {"category": product["category"]},
        "pricing": {"amount": product["price"], "currency": product["currency"]},
        "variantOptions": product["variants"],
        "inventory": {
            "warehouses": product["warehouses"],
            "total": product["total_stock"],
        },
    }


def map_schema_c(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": product["product_id"],
        "display_name": product["title"],
        "content": product["description"],
        "attributes": {
            "category": product["category"],
            "price": product["price"],
            "currency": product["currency"],
            "variants": product["variants"],
            "available_units": product["total_stock"],
        },
        "media": {"image_urls": product["image_urls"]},
    }


def load_rows(path: Path) -> list[dict[str, str]]:
    import csv
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
