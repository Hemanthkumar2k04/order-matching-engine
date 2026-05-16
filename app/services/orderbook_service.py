from sortedcontainers import SortedDict
from threading import RLock
from collections import deque
from app.models import Order, OrderSide


class OrderBookService:
    def __init__(self) -> None:
        self.order_book = {}
        self.lock = RLock()

    def get_or_create_symbol(self, symbol: str):
        if symbol not in self.order_book:
            self.order_book[symbol] = {
                "BUY": SortedDict(lambda price: -price),
                "SELL": SortedDict(),
            }
        return self.order_book[symbol]

    def add_order(self, symbol: str, side: str, price: float, order: Order):
        with self.lock:
            symbol_book = self.get_or_create_symbol(symbol)
            side_book = symbol_book[side]

            if price not in side_book:
                side_book[price] = deque()

            side_book[price].append(order)

    def get_best_bid(self, symbol: str):
        with self.lock:
            if symbol not in self.order_book or not self.order_book[symbol]["BUY"]:
                return None
            return self.order_book[symbol]["BUY"].keys()[0]

    def get_best_ask(self, symbol: str):
        with self.lock:
            if symbol not in self.order_book or not self.order_book[symbol]["SELL"]:
                return None
            return self.order_book[symbol]["SELL"].keys()[0]

    def get_orders_at_price(self, symbol: str, side: str, price: float):
        with self.lock:
            if symbol not in self.order_book:
                return deque()
            return self.order_book[symbol][side].get(price, deque())

    def remove_order(self, symbol: str, side: str, price: float, order_id: int):
        with self.lock:
            orders = self.get_orders_at_price(symbol, side, price)
            for i, order in enumerate(orders):
                if order_id == order.id:
                    orders.remove(i)
                    break

            if not orders and symbol in self.order_book:
                del self.order_book[symbol][side][price]

    def get_snapshot(self, symbol: str):
        with self.lock:
            if symbol not in self.order_book:
                return {"bids": [], "asks": []}
            bids = []
            for price, orders in self.order_book[symbol]["BUY"].items():
                quantity = sum(
                    max(0.0, (o.quantity - getattr(o, "filled_quantity", 0)))
                    for o in orders
                )
                if quantity > 0:
                    bids.append({"price": price, "quantity": quantity})

            asks = []
            for price, orders in self.order_book[symbol]["SELL"].items():
                quantity = sum(
                    max(0.0, (o.quantity - getattr(o, "filled_quantity", 0)))
                    for o in orders
                )
                if quantity > 0:
                    asks.append({"price": price, "quantity": quantity})

            return {"bids": bids, "asks": asks}
