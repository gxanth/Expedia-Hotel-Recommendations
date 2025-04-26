import yaml
from pathlib import Path
from typing import Any, List, Dict
from functools import lru_cache


class ConfigLoader:
    """
    A simple configuration loader for YAML files inside the config directory.
    """

    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir

    @lru_cache(maxsize=10)
    def _load_yaml(self, file_name: str) -> Any:
        """Internal helper to load a YAML file with caching."""
        path = self.config_dir / file_name
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def load_app_config(self) -> dict:
        """Load general app configuration."""
        return self._load_yaml("app_config.yaml")

    def load_table_styles(self) -> List[Dict]:
        """Load Dash DataTable style rules."""
        style_config = self._load_yaml("table_styles.yaml")
        return [
            {
                "if": {
                    "filter_query": rule["filter_query"],
                    "column_id": rule["column"],
                },
                "backgroundColor": rule.get("backgroundColor", "white"),
                "color": rule.get("color", "black"),
            }
            for rule in style_config.get("style_rules", {}).values()
        ]

    def load_styles(self) -> dict:
        """Load UI style settings."""
        return self._load_yaml("style_config.yaml")
