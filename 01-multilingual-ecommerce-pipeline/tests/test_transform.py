from decimal import Decimal
import pandas as pd
import pytest
from src.transform import parse_localized_price, normalize_availability, transform_records

@pytest.mark.parametrize(("raw", "currency", "expected"), [
    ("1.299,50", "EUR", Decimal("1299.50")),
    ("79,90", "EUR", Decimal("79.90")),
    ("1,299.50", "USD", Decimal("1299.50")),
    ("£149.00", "GBP", Decimal("149.00")),
    ("24.50", "EUR", Decimal("24.50")),
])
def test_parse_localized_price(raw, currency, expected):
    assert parse_localized_price(raw, currency) == expected

@pytest.mark.parametrize("raw", ["NaN", "Infinity", "-Infinity", "not-a-price", ""])
def test_reject_invalid_prices(raw):
    with pytest.raises(ValueError):
        parse_localized_price(raw, "EUR")

def test_normalize_availability():
    assert normalize_availability("Auf Lager") == "in_stock"
    assert normalize_availability("Out of Stock") == "out_of_stock"

def test_unknown_availability_is_rejected():
    with pytest.raises(ValueError):
        normalize_availability("maybe")

def test_duplicate_ids_are_rejected():
    raw = pd.DataFrame([
        {"product_id":"A1","title":"One","locale":"en_IE","price":"10.00",
         "currency":"EUR","availability":"In Stock","category":"Home","image_url":""},
        {"product_id":"A1","title":"Duplicate","locale":"en_IE","price":"11.00",
         "currency":"EUR","availability":"In Stock","category":"Home","image_url":""},
    ])
    valid, rejected = transform_records(raw)
    assert len(valid) == 1
    assert len(rejected) == 1
    assert "Duplicate" in rejected.iloc[0]["rejection_reason"]
