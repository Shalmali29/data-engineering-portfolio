"""Validate, store and relink catalogue image assets."""
import csv
import hashlib
import mimetypes
import os
from pathlib import Path
from .storage import GCSAssetStorage, LocalAssetStorage

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def safe_asset_path(asset_root: Path, relative_path: str) -> Path:
    root = asset_root.resolve()
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("asset path escapes the permitted asset directory")
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_storage(assets_dir: Path):
    backend = os.getenv("ASSET_STORAGE_BACKEND", "local").lower()
    if backend == "local":
        return LocalAssetStorage(
            assets_dir,
            os.getenv("ASSET_PUBLIC_BASE_URL", "http://localhost/assets"),
        )
    if backend == "gcs":
        bucket = os.getenv("GCS_BUCKET")
        if not bucket:
            raise ValueError("GCS_BUCKET must be set when ASSET_STORAGE_BACKEND=gcs")
        return GCSAssetStorage(
            bucket,
            os.getenv("GCS_PREFIX", "catalogue-assets"),
            os.getenv("ASSET_PUBLIC_BASE_URL", ""),
        )
    raise ValueError(f"Unsupported ASSET_STORAGE_BACKEND: {backend}")


def process_catalogue(input_csv: Path, asset_root: Path, output_dir: Path, storage) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    processed, errors = [], []
    with input_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        if not {"product_id", "image_path"}.issubset(fieldnames):
            raise ValueError("Input CSV must contain product_id and image_path columns")
        for row in reader:
            try:
                source = safe_asset_path(asset_root, row.get("image_path", ""))
                if not source.is_file():
                    raise FileNotFoundError("image file does not exist")
                if source.suffix.lower() not in ALLOWED_EXTENSIONS:
                    raise ValueError("unsupported image extension")
                content_type = mimetypes.guess_type(source.name)[0]
                if not content_type or not content_type.startswith("image/"):
                    raise ValueError("could not determine image content type")
                digest = sha256_file(source)
                object_key = f"{digest[:2]}/{digest}{source.suffix.lower()}"
                row["image_url"] = storage.upload(source, object_key, content_type)
                row["asset_sha256"] = digest
                row["asset_status"] = "uploaded"
                processed.append(row)
            except Exception as exc:
                row["image_url"] = ""
                row["asset_sha256"] = ""
                row["asset_status"] = "rejected"
                errors.append({
                    "product_id": row.get("product_id", ""),
                    "image_path": row.get("image_path", ""),
                    "reason": str(exc),
                })
                processed.append(row)

    output_fields = fieldnames + [name for name in ("image_url", "asset_sha256", "asset_status") if name not in fieldnames]
    with (output_dir / "catalogue_with_asset_urls.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(processed)
    with (output_dir / "asset_errors.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["product_id", "image_path", "reason"])
        writer.writeheader()
        writer.writerows(errors)
    return {"records_processed": len(processed), "assets_uploaded": len(processed) - len(errors), "rejected_assets": len(errors)}


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    storage = build_storage(project / "data/processed/assets")
    summary = process_catalogue(
        project / "data/raw/catalogue.csv",
        project / "data/raw/assets",
        project / "data/processed",
        storage,
    )
    print(summary)


if __name__ == "__main__":
    main()
