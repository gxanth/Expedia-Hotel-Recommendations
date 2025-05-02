from pathlib import Path


class PathConfig:
    def __init__(self, feature_version: str = "v1"):
        # Project root (3 levels up from this file)
        self.PROJECT_DIR = Path(__file__).resolve().parents[2]

        # Data directories
        self.DATA_DIR = self.PROJECT_DIR / "data"
        self.EXTERNAL_DATA_DIR = self.DATA_DIR / "external"
        self.INTERIM_DATA_DIR = self.DATA_DIR / "interim"
        self.PROCESSED_DATA_DIR = self.DATA_DIR / "processed"
        self.VIZ_DATA_DIR = self.DATA_DIR / "viz"

        # Features
        self.FEATURE_VERSION = feature_version
        self.FEATURE_DIR = self.PROCESSED_DATA_DIR / self.FEATURE_VERSION / "features"

        # Models
        self.MODEL_DIR = self.PROJECT_DIR / "models"

        # Config
        self.CONFIG_DIR = self.PROJECT_DIR / "src" / "config"

    def __repr__(self):
        return f"PathConfig(feature_version='{self.FEATURE_VERSION}')"
