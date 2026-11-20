from pathlib import Path
import pandas as pd

def read_source(path: str | Path) -> pd.DataFrame:
    """Read raw catalogue records without coercing source values."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)
