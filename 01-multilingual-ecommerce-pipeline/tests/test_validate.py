import pandas as pd
import pytest
from src.validate import validate_canonical

def valid_frame():
    return pd.DataFrame([{
        "product_id":"P1", "title":"Lamp", "locale":"en_IE", "price":"12.50",
        "currency":"EUR", "availability":"in_stock", "category":"Home", "image_url":""
    }])

def test_valid_canonical_data_passes():
    validate_canonical(valid_frame())

def test_duplicate_ids_fail():
    frame = pd.concat([valid_frame(), valid_frame()], ignore_index=True)
    with pytest.raises(ValueError, match="unique"):
        validate_canonical(frame)

def test_non_normalized_price_fails():
    frame = valid_frame()
    frame.loc[0, "price"] = "12,50"
    with pytest.raises(ValueError, match="2 decimal places"):
        validate_canonical(frame)
