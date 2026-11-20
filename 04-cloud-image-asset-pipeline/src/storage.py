"""Storage backends for catalogue image assets."""
from pathlib import Path
import shutil


class LocalAssetStorage:
    def __init__(self, root: Path, public_base_url: str = "http://localhost/assets"):
        self.root = root
        self.public_base_url = public_base_url.rstrip("/")

    def upload(self, source: Path, object_key: str, content_type: str) -> str:
        destination = self.root / object_key
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return f"{self.public_base_url}/{object_key}"


class GCSAssetStorage:
    def __init__(self, bucket_name: str, prefix: str = "", public_base_url: str = ""):
        try:
            from google.cloud import storage
        except ImportError as exc:
            raise RuntimeError(
                "GCS mode requires google-cloud-storage. Install it with "
                "pip install 'google-cloud-storage>=2.18,<4'."
            ) from exc
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.prefix = prefix.strip("/")
        self.public_base_url = public_base_url.rstrip("/")

    def upload(self, source: Path, object_key: str, content_type: str) -> str:
        key = f"{self.prefix}/{object_key}" if self.prefix else object_key
        blob = self.bucket.blob(key)
        blob.upload_from_filename(str(source), content_type=content_type)
        if self.public_base_url:
            return f"{self.public_base_url}/{key}"
        return f"gs://{self.bucket.name}/{key}"
