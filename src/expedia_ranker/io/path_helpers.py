# path_helpers.py
from pathlib import Path
from typing import List, Union

from .paths import (
    CONFIG_FEATURES_DIR,
    DATA_DASHBOARD_DIR,
    DATA_PROCESSED_DIR,
    MODELS_ROOT_DIR,
)

# === 📦 Model Output Paths ===


def get_models_root_dir() -> Path:
    """Return the root directory for all models."""
    return MODELS_ROOT_DIR


def get_model_output_dir(model_name: str) -> Path:
    """Return the output directory for a specific model."""
    return get_models_root_dir() / model_name


# === 📂 Feature Paths ===


def get_feature_file_path(feature_name: str, version: str) -> Path:
    """Return the path for a versioned feature Parquet file."""
    return DATA_PROCESSED_DIR / f"{feature_name}_v{version}.parquet"


def get_feature_schema_path() -> Path:
    """Return the path to the feature schema YAML file."""
    path = CONFIG_FEATURES_DIR / "schema.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_feature_rename_map_path() -> Path:
    """Return the path to the feature rename map YAML file."""
    path = CONFIG_FEATURES_DIR / "rename_map.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_feature_base_list_path() -> Path:
    """Return the path to the base features YAML file."""
    path = CONFIG_FEATURES_DIR / "base_features.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_feature_registry_path() -> Path:
    """Return the path to the feature registry YAML file."""
    path = CONFIG_FEATURES_DIR / "feature_registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# === 📊 Dashboard Paths ===


def get_dashboard_tab_dir(tab_name: str) -> Path:
    """Return the root directory for a specific dashboard tab."""
    return DATA_DASHBOARD_DIR / f"{tab_name}_tab"


def get_dashboard_figure_path(tab_name: str, filename: str) -> Path:
    """Return the path to a file inside a dashboard tab folder."""
    return get_dashboard_tab_dir(tab_name) / filename


def get_feature_distributions_dir() -> Path:
    """Return the root directory for all feature distributions."""
    return get_dashboard_tab_dir("univariate") / "feature_distributions"


def get_feature_distribution_dir(feature_name: str, create: bool = True) -> Path:
    """Return the directory for a specific feature's distribution plots."""
    path = get_feature_distributions_dir() / feature_name
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_feature_distribution_path(
    feature_name: str, file: str = "histogram.parquet"
) -> Path:
    """Return the full path to a feature distribution file."""
    return get_feature_distribution_dir(feature_name) / file


# === 📂 Utility Functions ===


def list_subdirectories(path: Path, names: bool = False) -> List[Union[str, Path]]:
    """Return all subdirectories of a given path."""
    return [p.name if names else p for p in path.iterdir() if p.is_dir()]


def list_continuous_features(path: Path, names: bool = False) -> List[Union[str, Path]]:
    """Return all subdirectories for continuous variables."""
    return [
        p.name if names else p
        for p in path.iterdir()
        if p.is_dir() and (p / "histogram.parquet").exists()
    ]


# === 💾 Processed Data Paths ===


def get_processed_dir() -> Path:
    """Return the processed data directory."""
    return DATA_PROCESSED_DIR
