"""Helpers for retrieving market data."""
from __future__ import annotations

import logging
from typing import List

from .binance_client import BinanceClient

logger = logging.getLogger(__name__)


def fetch_latest_klines(client: BinanceClient, symbol: str, interval: str, limit: int = 200) -> List[List]:
    """Fetch latest klines using the provided Binance client."""
    try:
        return client.fetch_klines(symbol=symbol, interval=interval, limit=limit)
    except Exception as exc:  # pragma: no cover - protective logging
        logger.error("Unexpected error while fetching klines: %s", exc)
        return []
