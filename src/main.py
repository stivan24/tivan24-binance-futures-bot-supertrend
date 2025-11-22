"""Entry point for the Binance futures SuperTrend bot."""
from __future__ import annotations

import time

from .binance_client import BinanceClient
from .data_fetcher import fetch_latest_klines
from .logger_utils import setup_logger
from .risk_manager import RiskManager
from .strategy_supertrend import SuperTrendParams, SuperTrendStrategy
from .trade_manager import TradeManager
from .utils import load_config


def main() -> None:
    """Run the trading bot in safe mode (no real orders)."""
    config = load_config()
    logger = setup_logger()

    symbol = config.get("symbol", "BTCUSDT")
    leverage = int(config.get("leverage", 1))
    timeframe = config.get("timeframe", "5m")
    polling_interval = int(config.get("polling_interval_seconds", 30))

    client = BinanceClient(
        api_key=config.get("binance_api_key", ""),
        api_secret=config.get("binance_api_secret", ""),
        testnet=bool(config.get("testnet", True)),
    )

    if client.set_leverage(symbol, leverage):
        logger.info("Leverage configured successfully.")
    else:
        logger.warning("Failed to configure leverage; proceeding with default exchange settings.")

    risk_manager = RiskManager(risk_per_trade_percent=float(config.get("risk_per_trade_percent", 1.0)))
    st_params = config.get("supertrend", {})
    strategy = SuperTrendStrategy(
        SuperTrendParams(
            period=int(st_params.get("period", 10)),
            multiplier=float(st_params.get("multiplier", 3.0)),
        )
    )

    trade_manager = TradeManager(client, risk_manager, logger, config)

    logger.info("Starting SuperTrend bot loop for %s on timeframe %s", symbol, timeframe)
    while True:
        try:
            klines = fetch_latest_klines(client, symbol=symbol, interval=timeframe)
            signal = strategy.generate_signal(klines)
            logger.info("Generated signal: %s", signal)
            trade_manager.process_signal(signal, klines)
        except Exception:
            logger.exception("Error while running bot loop")

        time.sleep(polling_interval)


if __name__ == "__main__":
    main()
