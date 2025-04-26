import pandas as pd
from pathlib import Path
from typing import List, Optional

VIZ_DATA_PATH = Path("data/viz")


def _load_parquet(path: Path) -> Optional[pd.DataFrame]:
    """Load a parquet file safely. Return None if missing."""
    if path.exists():
        return pd.read_parquet(path)
    else:
        print(f"Warning: File not found {path}")
        return None


def load_summary_df() -> Optional[pd.DataFrame]:
    """Load the precomputed feature summary."""
    return _load_parquet(VIZ_DATA_PATH / "feature_summary.parquet")


def list_available_features() -> List[str]:
    """List available features (directories)."""
    return [f.name for f in VIZ_DATA_PATH.iterdir() if f.is_dir()]


def load_feature_histogram(feature_name: str) -> Optional[pd.DataFrame]:
    """Load histogram data for a given feature."""
    return _load_parquet(VIZ_DATA_PATH / feature_name / "histogram.parquet")


def load_feature_boxplot(feature_name: str) -> Optional[pd.DataFrame]:
    """Load boxplot sample data for a given feature."""
    return _load_parquet(VIZ_DATA_PATH / feature_name / "boxplot_sample.parquet")
