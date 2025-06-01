# Corrected imports
from pathlib import Path
from typing import Any, Dict

import yaml


# YAML I/O utilities with error handling
def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents. Raises FileNotFoundError if file does not exist."""
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    with file_path.open("r") as file:
        return yaml.safe_load(file)


def save_yaml(data: Dict[Any, Any], file_path: Path) -> None:
    """Save a dictionary to a YAML file. Raises FileNotFoundError if parent directory does not exist."""
    parent_dir = file_path.parent
    if not parent_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {parent_dir}")
    with file_path.open("w") as file:
        yaml.safe_dump(data, file)
