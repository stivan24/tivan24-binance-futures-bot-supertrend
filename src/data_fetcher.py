from __future__ import annotations

from typing import List, Any

from .binance_client import BinanceClient


def fetch_latest_klines(
    client: BinanceClient,
    symbol: str,
    interval: str,
    limit: int = 200,
) -> List[List[Any]]:
    """
    Обёртка над BinanceClient.fetch_klines.

    На случай, если захочется добавить:
    - кэширование,
    - предобработку данных,
    - дополнительные проверки.
    """
    return client.fetch_klines(symbol=symbol, interval=interval, limit=limit)
