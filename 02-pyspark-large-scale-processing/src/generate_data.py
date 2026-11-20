"""Generate deterministic synthetic catalogue records for the Spark demo."""
import csv
import random
from pathlib import Path

SECTORS = ["Grocery", "Fashion", "Electronics", "Home"]
CATEGORIES = ["Essentials", "Apparel", "Accessories", "Appliances", "Decor"]


def generate(output_path: Path, rows: int = 10_000) -> None:
    random.seed(42)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["product_id", "sector", "category", "price", "stock", "rating"],
        )
        writer.writeheader()
        for index in range(rows):
            # Deterministic quality edge cases exercise the rejection path.
            price = "invalid" if index % 997 == 0 else round(random.uniform(2, 2500), 2)
            stock = -3 if index % 991 == 0 else random.randint(0, 500)
            writer.writerow({
                "product_id": f"SKU-{index + 1:06d}",
                "sector": random.choice(SECTORS),
                "category": random.choice(CATEGORIES),
                "price": price,
                "stock": stock,
                "rating": round(random.uniform(1, 5), 1),
            })


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "data/raw/products.csv")
    print("Generated 10,000 synthetic catalogue records.")
