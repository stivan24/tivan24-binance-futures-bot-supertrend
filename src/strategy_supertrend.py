from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, List, Any

import pandas as pd

Signal = Literal["long", "short", "none"]


@dataclass
class SuperTrendParams:
    period: int = 10
    multiplier: float = 3.0


class SuperTrendStrategy:
    """
    Реализация индикатора SuperTrend по фьючерсным свечам Binance.
    Вход: список klines так, как их отдаёт futures_klines.
    """

    def __init__(self, params: SuperTrendParams) -> None:
        self.params = params

    # ---------- Вспомогательные методы ----------

    def _klines_to_df(self, klines: List[List[Any]]) -> pd.DataFrame:
        """
        Конвертация списка свечей Binance в DataFrame.
        """
        cols = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "num_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ]
        df = pd.DataFrame(klines, columns=cols)

        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        return df

    def _calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Базовая реализация SuperTrend.

        1. Считаем ATR.
        2. Строим верхнюю и нижнюю линии.
        3. Определяем направление тренда (direction).
        4. Строим сам SuperTrend.
        """
        period = self.params.period
        multiplier = self.params.multiplier

        high = df["high"]
        low = df["low"]
        close = df["close"]

        # True Range
        hl = high - low
        hc = (high - close.shift()).abs()
        lc = (low - close.shift()).abs()

        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

        # ATR
        atr = tr.rolling(window=period, min_periods=period).mean()

        # Средняя цена
        hl2 = (high + low) / 2.0

        # Базовые линии
        upperband = hl2 + multiplier * atr
        lowerband = hl2 - multiplier * atr

        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)

        # Инициализация
        supertrend.iloc[0] = 0.0
        direction.iloc[0] = 1  # первый бар условно считаем бычьим

        for i in range(1, len(df)):
            curr_close = close.iloc[i]

            prev_supertrend = supertrend.iloc[i - 1]
            prev_direction = direction.iloc[i - 1]

            # Определяем направление
            if curr_close > upperband.iloc[i - 1]:
                direction.iloc[i] = 1
            elif curr_close < lowerband.iloc[i - 1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = prev_direction
                # Подтягиваем линии, чтобы не ломать тренд
                if prev_direction == 1 and lowerband.iloc[i] < prev_supertrend:
                    lowerband.iloc[i] = prev_supertrend
                if prev_direction == -1 and upperband.iloc[i] > prev_supertrend:
                    upperband.iloc[i] = prev_supertrend

            # Линия SuperTrend
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lowerband.iloc[i]
            else:
                supertrend.iloc[i] = upperband.iloc[i]

        df["supertrend"] = supertrend
        df["direction"] = direction

        return df

    # ---------- Публичный метод ----------

    def generate_signal(self, klines: List[List[Any]]) -> Signal:
        """
        Генерирует торговый сигнал на основе смены направления SuperTrend.

        Возвращает:
        - "long"  — если тренд сменился с медвежьего на бычий,
        - "short" — если с бычьего на медвежий,
        - "none"  — если сигнала нет.
        """
        min_len = self.params.period + 5
        if len(klines) < min_len:
            return "none"

        df = self._klines_to_df(klines)
        df = self._calculate_supertrend(df)

        last = df.iloc[-1]
        prev = df.iloc[-2]

        if prev["direction"] <= 0 and last["direction"] > 0:
            return "long"
        if prev["direction"] >= 0 and last["direction"] < 0:
            return "short"

        return "none"
