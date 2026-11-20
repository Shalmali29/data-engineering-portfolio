"""Generate a synthetic catalogue batch with valid and invalid records."""
import csv
from pathlib import Path

ROWS = [
    ["SKU-001", "Cotton T-shirt", "Fashion", "19.99", "in_stock"],
    ["SKU-002", "Ceramic mug", "Home", "8.50", "in_stock"],
    ["SKU-003", "Running shoes", "Sports", "64.00", "out_of_stock"],
    ["SKU-004", "Desk lamp", "Home", "25.00", "preorder"],
    ["SKU-005", "Wireless mouse", "Electronics", "15.75", "in_stock"],
    ["SKU-006", "Damaged record", "Home", "-5.00", "in_stock"],
    ["SKU-007", "Unknown stock", "Electronics", "12.00", "available"],
    ["SKU-008", "", "Fashion", "21.00", "in_stock"],
    ["SKU-002", "Duplicate mug", "Home", "9.00", "in_stock"],
    ["SKU-010", "Water bottle", "Sports", "11.50", "out_of_stock"],
]


def generate(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["product_id", "title", "category", "price", "availability"])
        writer.writerows(ROWS)


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    generate(project / "data/raw/products.csv")
    print("Generated synthetic product batch.")
