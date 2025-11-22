"""Client wrapper around python-binance for USDT-M futures interactions."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)


class BinanceClient:
    """Wrapper for Binance USDT-M futures API using python-binance."""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True) -> None:
        self.client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            # Ensure futures endpoints use testnet base URL.
            self.client.FUTURES_URL = self.client.TESTNET_FUTURES_URL
        logger.info("Binance client initialized in %s mode", "testnet" if testnet else "live")

    def fetch_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List[Any]]:
        """Fetch recent futures klines for the given symbol and interval."""
        try:
            return self.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to fetch klines: %s", exc)
            return []

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for a futures symbol."""
        try:
            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            logger.info("Leverage set to %s for %s", leverage, symbol)
            return True
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to set leverage: %s", exc)
            return False

    def get_futures_balance(self, asset: str = "USDT") -> Optional[float]:
        """Return futures wallet balance for the specified asset."""
        try:
            balances = self.client.futures_account_balance()
            for balance in balances:
                if balance.get("asset") == asset:
                    return float(balance.get("balance", 0))
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to fetch futures balance: %s", exc)
        return None

    def get_position_info(self, symbol: str) -> Dict[str, Any]:
        """Retrieve position information for the given symbol."""
        try:
            info = self.client.futures_position_information(symbol=symbol)
            return info[0] if info else {}
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to fetch position info: %s", exc)
            return {}

    def open_long(self, symbol: str, quantity: float, reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """Open a long position at market price."""
        try:
            return self.client.futures_create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity,
                reduceOnly=reduce_only,
            )
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to open long position: %s", exc)
            return None

    def open_short(self, symbol: str, quantity: float, reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """Open a short position at market price."""
        try:
            return self.client.futures_create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity,
                reduceOnly=reduce_only,
            )
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to open short position: %s", exc)
            return None

    def close_position_market(self, symbol: str, position_side: str, quantity: float) -> bool:
        """Close an existing position using a market order.

        Args:
            symbol: Trading pair symbol.
            position_side: Either Client.SIDE_BUY or Client.SIDE_SELL opposite to current position.
            quantity: Quantity to close.

        Returns:
            True when the order is placed successfully, otherwise False.
        """

        try:
            self.client.futures_create_order(
                symbol=symbol,
                side=position_side,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity,
                reduceOnly=True,
            )
            return True
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to close position: %s", exc)
            return False
