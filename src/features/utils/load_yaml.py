import yaml
from pathlib import Path


def load_yaml(path: str) -> dict:
    """Load a YAML file as a dictionary."""
    with open(path, "r") as f:
        return yaml.safe_load(f)
