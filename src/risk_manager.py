"""Risk management utilities for calculating position sizing."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskManager:
    """Simple risk manager based on fixed percentage per trade."""

    risk_per_trade_percent: float = 1.0

    def calculate_position_size(
        self, balance_usdt: float, entry_price: float, stop_loss_price: float, leverage: int
    ) -> float:
        """Calculate position size (quantity) based on risk parameters."""
        risk_usdt = balance_usdt * (self.risk_per_trade_percent / 100)
        price_risk = abs(entry_price - stop_loss_price)
        if price_risk == 0:
            return 0.0
        base_qty = risk_usdt / price_risk
        position_size = base_qty * leverage
        return max(position_size, 0.0)
