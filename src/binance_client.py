from __future__ import annotations

from typing import Any, Dict, List, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


class BinanceClient:
    """
    Простая обёртка над python-binance для работы с USDT-M Futures.

    ВАЖНО:
    - Для первых тестов используй testnet=True в конфиге.
    - Перед запуском на реальных деньгах всё перепроверь на демо.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        # В последних версиях python-binance есть поддержка testnet-параметра.
        # Если что-то не заработает, можно будет отдельно прописать URL.
        self.client = Client(api_key, api_secret, testnet=testnet)

    # ---------- Маркет / данные ----------

    def fetch_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
    ) -> List[List[Any]]:
        """
        Загружает свечи фьючерсов.
        Возвращает "сырые" данные так, как их отдаёт Binance.
        """
        try:
            return self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
            )
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in fetch_klines: {e}")
            return []

    # ---------- Леверидж ----------

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Устанавливает плечо для конкретного символа.
        """
        try:
            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            return True
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in set_leverage: {e}")
            return False

    # ---------- Баланс / позиции ----------

    def get_futures_balance(self, asset: str = "USDT") -> Optional[float]:
        """
        Возвращает баланс фьючерсного аккаунта по указанному asset.
        """
        try:
            balances = self.client.futures_account_balance()
            for b in balances:
                if b.get("asset") == asset:
                    return float(b.get("balance", 0.0))
            return None
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in get_futures_balance: {e}")
            return None

    def get_position_info(self, symbol: str) -> Dict[str, Any]:
        """
        Возвращает информацию о позиции по символу.
        Если позиции нет или ошибка — возвращает пустой словарь.
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            return positions[0] if positions else {}
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in get_position_info: {e}")
            return {}

    # ---------- Ордера ----------

    def open_long(
        self,
        symbol: str,
        quantity: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Открывает лонг по рынку.
        Пока без стопов и тейков — просто рыночный ордер.
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side="BUY",
                type="MARKET",
                quantity=quantity,
            )
            return order
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in open_long: {e}")
            return None

    def open_short(
        self,
        symbol: str,
        quantity: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Открывает шорт по рынку.
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side="SELL",
                type="MARKET",
                quantity=quantity,
            )
            return order
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in open_short: {e}")
            return None

    def close_position_market(self, symbol: str) -> bool:
        """
        Закрывает текущую позицию по рынку:
        - если лонг — продаём,
        - если шорт — покупаем.
        Если позиции нет — считаем, что всё ок.
        """
        try:
            pos = self.get_position_info(symbol)
            qty = float(pos.get("positionAmt", 0.0))

            if qty == 0:
                return True  # позиции нет

            side = "SELL" if qty > 0 else "BUY"

            self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=abs(qty),
            )
            return True
        except (BinanceAPIException, BinanceRequestException) as e:
            print(f"[BinanceClient] Error in close_position_market: {e}")
            return False
