from __future__ import annotations

from typing import List, Any
from logging import Logger

from .binance_client import BinanceClient
from .risk_manager import RiskManager


class TradeManager:
    """
    Управление сделками (пока в режиме "бумажной" торговли).

    Логика:
    - Держим в памяти текущее состояние позиции: flat / long / short.
    - По сигналам "long"/"short" считаем размер позиции и логируем,
      что бы мы открыли/закрыли, НО реальные ордера не отправляем.
    """

    def __init__(
        self,
        client: BinanceClient,
        risk_manager: RiskManager,
        logger: Logger,
        config: dict,
    ) -> None:
        self.client = client
        self.risk_manager = risk_manager
        self.logger = logger
        self.config = config

        self.symbol: str = config.get("symbol", "BTCUSDT")
        self.leverage: int = int(config.get("leverage", 10))
        self.position_side: str = "flat"  # flat | long | short
        self.entry_price: float | None = None
        self.position_qty: float = 0.0

    def _get_last_close(self, klines: List[List[Any]]) -> float:
        """
        Берём цену закрытия последней свечи.
        В данных Binance это 5-й элемент (индекс 4).
        """
        last_kline = klines[-1]
        return float(last_kline[4])

    def _get_stop_loss_price(self, signal: str, klines: List[List[Any]]) -> float:
        """
        Простейшее определение стоп-лосса:
        - для лонга: ниже минимума последних N свечей,
        - для шорта: выше максимума последних N свечей.
        """
        lookback = 5
        recent = klines[-lookback:]

        lows = [float(k[3]) for k in recent]   # low = индекс 3
        highs = [float(k[2]) for k in recent]  # high = индекс 2

        if signal == "long":
            sl = min(lows)
        else:
            sl = max(highs)

        return sl

    def process_signal(self, signal: str, klines: List[List[Any]]) -> None:
        """
        Обрабатывает торговый сигнал.

        Режим "бумажной" торговли:
        - Никаких реальных ордеров.
        - Только расчёты и логирование.
        """
        if signal == "none":
            self.logger.info("No trading signal. Doing nothing.")
            return

        last_close = self._get_last_close(klines)
        stop_loss_price = self._get_stop_loss_price(signal, klines)

        balance = self.client.get_futures_balance(asset="USDT")
        if balance is None:
            self.logger.warning("Could not fetch futures balance. Skipping trade simulation.")
            return

        qty = self.risk_manager.calculate_position_size(
            balance_usdt=balance,
            entry_price=last_close,
            stop_loss_price=stop_loss_price,
            leverage=self.leverage,
        )

        if qty <= 0:
            self.logger.warning("Calculated position size is zero. Skipping trade simulation.")
            return

        self.logger.info(
            f"[PAPER TRADE] Signal: {signal}, last_close={last_close:.2f}, "
            f"stop_loss={stop_loss_price:.2f}, balance={balance:.2f}, qty={qty:.4f}"
        )

        # Логика смены позиции (только в логах):
        if signal == "long":
            if self.position_side == "long":
                self.logger.info("[PAPER TRADE] Already in LONG. No action.")
                return

            if self.position_side == "short":
                self.logger.info("[PAPER TRADE] Would CLOSE SHORT position here.")
                # здесь могла бы быть реальная закрывашка шорта

            self.logger.info("[PAPER TRADE] Would OPEN LONG position here.")
            self.position_side = "long"
            self.entry_price = last_close
            self.position_qty = qty

        elif signal == "short":
            if self.position_side == "short":
                self.logger.info("[PAPER TRADE] Already in SHORT. No action.")
                return

            if self.position_side == "long":
                self.logger.info("[PAPER TRADE] Would CLOSE LONG position here.")
                # здесь могла бы быть реальная закрывашка лонга

            self.logger.info("[PAPER TRADE] Would OPEN SHORT position here.")
            self.position_side = "short"
            self.entry_price = last_close
            self.position_qty = qty

        self.logger.info(
            f"[PAPER TRADE] Position state: side={self.position_side}, "
            f"entry_price={self.entry_price}, qty={self.position_qty:.4f}"
        )
