import csv
from pathlib import Path

import pytest

from src.pipeline import process_catalogue, safe_asset_path, sha256_file
from src.storage import LocalAssetStorage


def test_safe_asset_path_rejects_traversal(tmp_path):
    root = tmp_path / "assets"
    root.mkdir()
    with pytest.raises(ValueError):
        safe_asset_path(root, "../outside.png")


def test_pipeline_uploads_valid_asset_and_reports_missing(tmp_path):
    raw = tmp_path / "raw"
    assets = raw / "assets"
    assets.mkdir(parents=True)
    image = assets / "valid.png"
    image.write_bytes(b"synthetic image bytes")
    source = raw / "catalogue.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["product_id", "image_path"])
        writer.writeheader()
        writer.writerows([
            {"product_id": "P-1", "image_path": "valid.png"},
            {"product_id": "P-2", "image_path": "missing.png"},
        ])

    storage_root = tmp_path / "stored"
    result = process_catalogue(
        source, assets, tmp_path / "output",
        LocalAssetStorage(storage_root, "https://cdn.example.test/assets"),
    )

    assert result == {"records_processed": 2, "assets_uploaded": 1, "rejected_assets": 1}
    with (tmp_path / "output/catalogue_with_asset_urls.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["image_url"].startswith("https://cdn.example.test/assets/")
    assert rows[0]["asset_sha256"] == sha256_file(image)
    assert rows[0]["asset_status"] == "uploaded"
    assert rows[1]["asset_status"] == "rejected"


def test_identical_assets_get_deterministic_object_keys(tmp_path):
    raw = tmp_path / "raw"
    assets = raw / "assets"
    assets.mkdir(parents=True)
    (assets / "one.png").write_bytes(b"same content")
    (assets / "two.png").write_bytes(b"same content")
    source = raw / "catalogue.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["product_id", "image_path"])
        writer.writeheader()
        writer.writerows([
            {"product_id": "P-1", "image_path": "one.png"},
            {"product_id": "P-2", "image_path": "two.png"},
        ])

    result = process_catalogue(source, assets, tmp_path / "out", LocalAssetStorage(tmp_path / "stored"))
    assert result["assets_uploaded"] == 2
    assert len(list((tmp_path / "stored").rglob("*.png"))) == 1
