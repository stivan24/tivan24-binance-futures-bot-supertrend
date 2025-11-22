from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskManager:
    """
    Простой риск-менеджер.

    risk_per_trade_percent:
        Процент от депозита, которым готов рискнуть в одной сделке (например, 1.0 = 1%).
    """
    risk_per_trade_percent: float = 1.0

    def calculate_position_size(
        self,
        balance_usdt: float,
        entry_price: float,
        stop_loss_price: float,
        leverage: int,
    ) -> float:
        """
        Расчёт размера позиции (в монетах) по простому правилу:

        1. Считаем, сколько USDT готовы потерять в сделке:
           risk_amount = balance * (risk_percent / 100)
        2. Считаем риск на одну монету:
           price_risk = |entry_price - stop_loss_price|
        3. Без плеча количество монет:
           base_qty = risk_amount / price_risk
        4. С учётом плеча:
           qty = base_qty * leverage
        """
        if balance_usdt <= 0:
            return 0.0

        price_risk = abs(entry_price - stop_loss_price)
        if price_risk <= 0:
            return 0.0

        risk_amount = balance_usdt * (self.risk_per_trade_percent / 100.0)
        base_qty = risk_amount / price_risk
        qty = base_qty * leverage

        return max(qty, 0.0)
