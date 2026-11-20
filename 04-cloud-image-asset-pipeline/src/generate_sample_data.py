"""Create small synthetic image fixtures and a matching catalogue CSV."""
import base64
import csv
from pathlib import Path

# A valid 1x1 PNG fixture; intentionally tiny so the repository stays lightweight.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/"
    "l9sAAAAASUVORK5CYII="
)


def generate(project_dir: Path) -> None:
    assets = project_dir / "data/raw/assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "sample-product.png").write_bytes(PNG_BYTES)
    with (project_dir / "data/raw/catalogue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["product_id", "title", "image_path"])
        writer.writeheader()
        writer.writerows([
            {"product_id": "SYN-001", "title": "Synthetic Sample Product", "image_path": "sample-product.png"},
            {"product_id": "SYN-002", "title": "Missing Image Example", "image_path": "missing-image.jpg"},
        ])


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1])
    print("Generated synthetic catalogue and image fixture.")
