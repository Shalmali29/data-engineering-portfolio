from pathlib import Path
from src.extract import read_source
from src.transform import transform_records
from src.validate import validate_canonical
from src.load import write_csv, write_platform_outputs

BASE_DIR = Path(__file__).resolve().parents[1]

def run_pipeline() -> None:
    raw_path = BASE_DIR / "data" / "raw" / "products.csv"
    processed_dir = BASE_DIR / "data" / "processed"
    mapping_path = BASE_DIR / "config" / "schema_mappings.json"

    raw = read_source(raw_path)
    canonical, rejected = transform_records(raw)
    validate_canonical(canonical)

    write_csv(canonical, processed_dir / "canonical_products.csv")
    write_csv(rejected, processed_dir / "rejected_records.csv")
    platform_files = write_platform_outputs(canonical, mapping_path, processed_dir)

    print(f"Source rows: {len(raw)}")
    print(f"Accepted rows: {len(canonical)}")
    print(f"Rejected rows: {len(rejected)}")
    print("Created:")
    print(f" - {processed_dir / 'canonical_products.csv'}")
    print(f" - {processed_dir / 'rejected_records.csv'}")
    for path in platform_files:
        print(f" - {path}")

if __name__ == "__main__":
    run_pipeline()
