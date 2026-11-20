"""Generate a small synthetic real-estate catalogue."""
import csv
from pathlib import Path

ROWS = [
    ["PROP-001", "Bright family apartment", "Near schools, a park and public transport.", "Kolkata", "Apartment", "8500000", "1250", "3"],
    ["PROP-002", "Compact city studio", "A low-maintenance studio close to offices and metro.", "Kolkata", "Studio", "3200000", "520", "1"],
    ["PROP-003", "Garden-facing family home", "Quiet residential home with balcony and garden access.", "Pune", "House", "11200000", "1800", "3"],
    ["PROP-004", "Modern two-bedroom flat", "Recently renovated flat near shopping and transit.", "Bengaluru", "Apartment", "7400000", "980", "2"],
    ["PROP-005", "Invalid sample row", "This record intentionally has an invalid price.", "Kolkata", "Apartment", "unknown", "900", "2"],
    ["PROP-006", "Sunny starter apartment", "Affordable first home with a bright living room.", "Hyderabad", "Apartment", "4500000", "760", "2"],
]


def generate(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["property_id", "title", "description", "city", "property_type", "price", "area_sqft", "bedrooms"])
        writer.writerows(ROWS)


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    generate(project / "data/raw/properties.csv")
    print("Generated synthetic property catalogue.")
