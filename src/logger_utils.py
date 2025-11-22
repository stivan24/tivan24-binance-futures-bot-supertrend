import logging
from pathlib import Path


def setup_logger(name: str = "bot") -> logging.Logger:
    """
    Настраивает логгер:
    - вывод в консоль
    - запись в файл logs/bot.log

    Если логгер уже настроен, повторно хендлеры не добавляются.
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Если уже есть хендлеры (например, при повторном вызове) — просто вернуть логгер
    if logger.handlers:
        return logger

    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Консоль
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    # Файл
    fh = logging.FileHandler(logs_dir / "bot.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
