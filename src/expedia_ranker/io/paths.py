# paths.py
from pathlib import Path

# Root
PROJECT_ROOT = Path(__file__).parents[3].resolve()

# Data directories
DATA_ROOT_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_ROOT_DIR / "raw"
DATA_INTERIM_DIR = DATA_ROOT_DIR / "interim"
DATA_PROCESSED_DIR = DATA_ROOT_DIR / "processed"
DATA_DASHBOARD_DIR = DATA_ROOT_DIR / "dashboard"
DATA_SUBMISSION_DIR = DATA_ROOT_DIR / "submissions"

# Model outputs
MODELS_ROOT_DIR = PROJECT_ROOT / "models"

# Config directories
CONFIG_ROOT_DIR = PROJECT_ROOT / "configs"
CONFIG_FEATURES_DIR = CONFIG_ROOT_DIR / "features"
CONFIG_MODELS_DIR = CONFIG_ROOT_DIR / "models"
CONFIG_PIPELINE_DIR = CONFIG_ROOT_DIR / "pipelines"

# Dashboard layout directory
DASHBOARD_ROOT_DIR = PROJECT_ROOT / "src" / "expedia_ranker" / "dashboard"
