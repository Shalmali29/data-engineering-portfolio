import pandas as pd

REQUIRED_COLUMNS = {
    "product_id", "title", "locale", "price", "currency",
    "availability", "category", "image_url"
}

def validate_canonical(data: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing canonical columns: {sorted(missing)}")
    if data["product_id"].duplicated().any():
        raise ValueError("Canonical product_id values must be unique")
    if data["product_id"].astype(str).str.strip().eq("").any():
        raise ValueError("product_id cannot be blank")
    if data["price"].astype(str).str.fullmatch(r"\d+\.\d{2}").eq(False).any():
        raise ValueError("Price must be normalized to 2 decimal places")
    allowed = {"in_stock", "out_of_stock"}
    invalid = set(data["availability"].dropna()) - allowed
    if invalid:
        raise ValueError(f"Invalid canonical availability values: {sorted(invalid)}")
