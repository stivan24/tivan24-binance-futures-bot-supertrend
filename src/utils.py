from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_config(
    path: str = "config.json",
    example_path: str = "config.example.json",
) -> Dict[str, Any]:
    """
    Загружает конфиг бота.

    1. Пытается прочитать config.json (рабочий конфиг с ключами).
    2. Если config.json не найден, использует config.example.json.
    3. Возвращает словарь с настройками.
    """
    config_path = Path(path)

    if not config_path.exists():
        print(f"[utils] {path} не найден, использую {example_path}")
        config_path = Path(example_path)

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)
