"""Utility helpers for configuration management."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_config(path: str = "config.json", example_path: str = "config.example.json") -> Dict[str, Any]:
    """Load configuration from file.

    The function prioritizes the primary config file and falls back to the example
    configuration when the main file is absent.

    Args:
        path: Path to the primary configuration file.
        example_path: Path to the fallback example configuration file.

    Returns:
        Parsed configuration as a dictionary.
    """

    primary_path = Path(path)
    fallback_path = Path(example_path)

    config_path = primary_path if primary_path.exists() else fallback_path
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)
