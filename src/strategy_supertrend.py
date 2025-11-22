"""SuperTrend trading strategy implementation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, List

import numpy as np
import pandas as pd

Signal = Literal["long", "short", "none"]


@dataclass
class SuperTrendParams:
    """Parameters for the SuperTrend indicator."""

    period: int = 10
    multiplier: float = 3.0


class SuperTrendStrategy:
    """Generate trading signals based on the SuperTrend indicator."""

    def __init__(self, params: SuperTrendParams) -> None:
        self.params = params

    def _klines_to_df(self, klines: List[List]) -> pd.DataFrame:
        """Convert Binance kline response to a pandas DataFrame."""
        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trade_count",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ]
        df = pd.DataFrame(klines, columns=columns)
        numeric_cols = ["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_base", "taker_buy_quote"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        return df

    def _calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SuperTrend values and direction."""
        period = self.params.period
        multiplier = self.params.multiplier

        df = df.copy()
        hl2 = (df["high"] + df["low"]) / 2
        tr1 = df["high"] - df["low"]
        tr2 = (df["high"] - df["close"].shift()).abs()
        tr3 = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        upperband = hl2 + multiplier * atr
        lowerband = hl2 - multiplier * atr

        direction = np.ones(len(df))
        supertrend = pd.Series(index=df.index, dtype=float)

        for i in range(1, len(df)):
            if df.loc[i, "close"] > upperband.iloc[i - 1]:
                direction[i] = 1
            elif df.loc[i, "close"] < lowerband.iloc[i - 1]:
                direction[i] = -1
            else:
                direction[i] = direction[i - 1]
                if direction[i] == 1 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                    lowerband.iloc[i] = lowerband.iloc[i - 1]
                if direction[i] == -1 and upperband.iloc[i] > upperband.iloc[i - 1]:
                    upperband.iloc[i] = upperband.iloc[i - 1]

            supertrend.iloc[i] = lowerband.iloc[i] if direction[i] == 1 else upperband.iloc[i]

        df["supertrend"] = supertrend
        df["direction"] = direction
        return df

    def generate_signal(self, klines: List[List]) -> Signal:
        """Generate trading signal based on the latest SuperTrend direction change."""
        if len(klines) < self.params.period + 3:
            return "none"

        df = self._klines_to_df(klines)
        df = self._calculate_supertrend(df)

        if len(df) < 2:
            return "none"

        prev_dir = df["direction"].iloc[-2]
        curr_dir = df["direction"].iloc[-1]

        if prev_dir == -1 and curr_dir == 1:
            return "long"
        if prev_dir == 1 and curr_dir == -1:
            return "short"
        return "none"
