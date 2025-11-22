"""Trade manager stub that reacts to strategy signals."""
from __future__ import annotations

from logging import Logger
from typing import List

from .binance_client import BinanceClient
from .risk_manager import RiskManager


class TradeManager:
    """Handle trading actions based on generated signals."""

    def __init__(self, client: BinanceClient, risk_manager: RiskManager, logger: Logger, config: dict) -> None:
        self.client = client
        self.risk_manager = risk_manager
        self.logger = logger
        self.config = config

    def process_signal(self, signal: str, klines: List[List]) -> None:
        """Process the incoming trading signal without executing real orders."""
        if signal == "none":
            self.logger.info("No trading signal generated; skipping.")
            return

        self.logger.info("Received signal: %s", signal)

        # TODO: implement live trading steps when enabling live trading mode:
        # - Fetch futures balance using BinanceClient.get_futures_balance
        # - Determine stop-loss based on recent candle data
        # - Calculate position size via RiskManager.calculate_position_size
        # - Place long/short orders through BinanceClient open/close methods

        # Currently running in safe mode (no orders executed).
        self.logger.info("Safe mode active: trading actions are logged only.")
