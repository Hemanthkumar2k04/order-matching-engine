from app.models import Order, Trade, OrderStatus, OrderSide, OrderType
from app.services.orderbook_service import OrderBookService
from app.models.memory_order import MemoryOrder
from datetime import datetime


class MatchingEngine:
    def __init__(self, order_book_service: OrderBookService) -> None:
        self.order_book = order_book_service

    async def match_order(self, order: Order) -> list[Trade]:
        trades = []
        remaining_quantity = order.quantity

        if order.side == OrderSide.BUY:
            trades = await self._match_against_asks(order, remaining_quantity)

        else:
            trades = await self._match_against_bids(order, remaining_quantity)

        return trades

    async def _match_against_asks(
        self, buy_order: Order, remaining_quantity: float
    ) -> list[Trade]:
        trades = []

        symbol_book = self.order_book.get_or_create_symbol(buy_order.symbol)

        ask_prices = list(symbol_book["SELL"].keys())

        for ask_price in ask_prices:
            if buy_order.type != OrderType.MARKET and buy_order.price < ask_price:
                break

            if remaining_quantity <= 0:
                break

            sell_orders = symbol_book["SELL"][ask_price]

            while sell_orders and remaining_quantity > 0:
                sell_order: MemoryOrder = sell_orders[0]

                trade_qty: float = min(
                    remaining_quantity, sell_order.quantity - sell_order.filled_quantity
                )

                trade: Trade = Trade(
                    symbol=buy_order.symbol,
                    buy_order_id=buy_order.id,
                    sell_order_id=sell_order.id,
                    price=ask_price,
                    quantity=trade_qty,
                    timestamp=datetime.now(),
                )
                trades.append(trade)

                remaining_quantity -= trade_qty
                sell_order.filled_quantity += trade_qty

                if sell_order.filled_quantity >= sell_order.quantity:
                    sell_orders.popleft()
        return trades

    async def _match_against_bids(
        self, sell_order: Order, remaining_quantity: float
    ) -> list[Trade]:
        trades = []

        symbol_book = self.order_book.get_or_create_symbol(sell_order.symbol)
        bid_prices = list(symbol_book["BUY"].keys())

        for bid_price in bid_prices:
            if sell_order.type != OrderType.MARKET and sell_order.price > bid_price:
                break
            if remaining_quantity <= 0:
                break

            buy_orders = symbol_book["BUY"][bid_price]

            while buy_orders and remaining_quantity > 0:
                buy_order: MemoryOrder = buy_orders[0]

                trade_qty: float = min(
                    remaining_quantity, buy_order.quantity - buy_order.filled_quantity
                )

                trade: Trade = Trade(
                    symbol=sell_order.symbol,
                    buy_order_id=buy_order.id,
                    sell_order_id=sell_order.id,
                    price=bid_price,
                    quantity=trade_qty,
                    timestamp=datetime.now(),
                )
                trades.append(trade)

                remaining_quantity -= trade_qty
                buy_order.filled_quantity += trade_qty

                if buy_order.filled_quantity >= buy_order.quantity:
                    buy_orders.popleft()

        return trades
