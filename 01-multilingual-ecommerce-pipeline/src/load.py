from pathlib import Path
import json
import pandas as pd

def write_csv(data: pd.DataFrame, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(destination, index=False)

def write_platform_outputs(data: pd.DataFrame, mapping_path: str | Path,
                           output_dir: str | Path) -> list[Path]:
    mappings = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    output_paths = []
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for platform, field_mapping in mappings.items():
        missing = set(field_mapping).difference(data.columns)
        if missing:
            raise ValueError(f"{platform} mapping references missing fields: {sorted(missing)}")
        output = data[list(field_mapping)].rename(columns=field_mapping)
        path = output_dir / f"{platform}_products.csv"
        output.to_csv(path, index=False)
        output_paths.append(path)
    return output_paths
