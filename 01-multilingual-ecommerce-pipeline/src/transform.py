import re
from decimal import Decimal, InvalidOperation
import pandas as pd

AVAILABILITY_MAP = {
    "in stock": "in_stock",
    "auf lager": "in_stock",
    "en stock": "in_stock",
    "disponible": "in_stock",
    "out of stock": "out_of_stock",
    "unavailable": "out_of_stock",
}

CURRENCY_SYMBOLS = {"€": "EUR", "£": "GBP", "$": "USD"}

def parse_localized_price(raw_price: str, currency: str) -> Decimal:
    """Parse common European/English price formats into a Decimal amount."""
    value = str(raw_price).strip().replace("\u00a0", "").replace(" ", "")
    if not value or value.lower() in {"nan", "inf", "+inf", "-inf", "infinity"}:
        raise ValueError(f"Invalid price: {raw_price!r}")

    detected_currency = next((code for symbol, code in CURRENCY_SYMBOLS.items()
                              if symbol in value), None)
    if detected_currency and currency and detected_currency != currency.upper():
        raise ValueError(f"Currency symbol {detected_currency} conflicts with {currency}")

    value = re.sub(r"[€£$]", "", value)
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        tail = value.rsplit(",", 1)[-1]
        value = value.replace(",", ".") if len(tail) in (1, 2) else value.replace(",", "")

    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid price: {raw_price!r}") from exc

    if not amount.is_finite() or amount < 0:
        raise ValueError(f"Price must be finite and non-negative: {raw_price!r}")
    return amount.quantize(Decimal("0.01"))

def normalize_availability(raw_value: str) -> str:
    key = str(raw_value).strip().casefold()
    if key not in AVAILABILITY_MAP:
        raise ValueError(f"Unknown availability value: {raw_value!r}")
    return AVAILABILITY_MAP[key]

def transform_records(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (valid canonical rows, rejected rows with rejection_reason)."""
    accepted, rejected = [], []
    seen_ids = set()

    for row_number, row in raw.iterrows():
        record = row.to_dict()
        try:
            product_id = str(record.get("product_id", "")).strip()
            title = str(record.get("title", "")).strip()
            if not product_id or not title:
                raise ValueError("Missing required product_id or title")
            if product_id in seen_ids:
                raise ValueError(f"Duplicate product_id: {product_id}")

            currency = str(record.get("currency", "")).strip().upper()
            if not currency:
                raise ValueError("Missing currency")

            price = parse_localized_price(record.get("price", ""), currency)
            availability = normalize_availability(record.get("availability", ""))

            accepted.append({
                "product_id": product_id,
                "title": title,
                "locale": str(record.get("locale", "")).strip(),
                "price": format(price, ".2f"),
                "currency": currency,
                "availability": availability,
                "category": str(record.get("category", "")).strip(),
                "image_url": str(record.get("image_url", "")).strip(),
            })
            seen_ids.add(product_id)
        except (ValueError, TypeError) as exc:
            record["rejection_reason"] = str(exc)
            record["source_row"] = int(row_number) + 2
            rejected.append(record)

    columns = ["product_id", "title", "locale", "price", "currency",
               "availability", "category", "image_url"]
    return pd.DataFrame(accepted, columns=columns), pd.DataFrame(rejected)
