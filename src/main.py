from __future__ import annotations

import time

from .logger_utils import setup_logger
from .utils import load_config
from .binance_client import BinanceClient
from .risk_manager import RiskManager
from .strategy_supertrend import SuperTrendParams, SuperTrendStrategy
from .trade_manager import TradeManager
from .data_fetcher import fetch_latest_klines


def main() -> None:
    # Логгер и конфиг
    logger = setup_logger("bot")
    config = load_config()

    symbol = config.get("symbol", "BTCUSDT")
    leverage = int(config.get("leverage", 10))
    timeframe = config.get("timeframe", "5m")
    polling_interval = int(config.get("polling_interval_seconds", 30))

    # Клиент Binance
    client = BinanceClient(
        api_key=config["binance_api_key"],
        api_secret=config["binance_api_secret"],
        testnet=bool(config.get("testnet", True)),
    )

        # Плечо
    # На этом этапе можем не трогать плечо через API,
    # а выставить его вручную в интерфейсе Binance.
    success = client.set_leverage(symbol, leverage)
    if not success:
        logger.warning(
            "Could not set leverage via API. "
            "Set leverage manually in Binance interface. "
            "Bot will continue to work with existing leverage."
        )


    # Риск-менеджмент
    risk_manager = RiskManager(
        risk_per_trade_percent=float(config.get("risk_per_trade_percent", 1.0))
    )

    # Параметры стратегии SuperTrend
    st_params = SuperTrendParams(
        period=int(config["supertrend"]["period"]),
        multiplier=float(config["supertrend"]["multiplier"]),
    )
    strategy = SuperTrendStrategy(st_params)

    # Менеджер сделок (пока только логика без реальных ордеров)
    trade_manager = TradeManager(
        client=client,
        risk_manager=risk_manager,
        logger=logger,
        config=config,
    )

    logger.info("Bot started, entering main loop...")

    while True:
        try:
            klines = fetch_latest_klines(
                client=client,
                symbol=symbol,
                interval=timeframe,
                limit=200,
            )

            if not klines:
                logger.warning("No klines received from Binance. Retrying...")
                time.sleep(polling_interval)
                continue

            signal = strategy.generate_signal(klines)
            logger.info(f"Generated signal: {signal}")

            # Обработка сигнала (пока без реальных сделок)
            trade_manager.process_signal(signal, klines)

        except Exception as e:
            logger.exception(f"Unhandled exception in main loop: {e}")

        time.sleep(polling_interval)


if __name__ == "__main__":
    main()
