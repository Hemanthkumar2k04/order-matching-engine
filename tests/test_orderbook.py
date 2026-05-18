import pytest
from app.services.order_service import OrderBookService
from app.models import Order, OrderSide, OrderType


@pytest.fixture
def orderbook():
    return OrderBookService()


def test_add_order(orderbook):
    order: Order = Order(
        id=1,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=1.0,
        filled_quantity=0.0,
    )

    orderbook.add_order("BTC/USD", "BUY", 50000.0, order=order)

    orders = orderbook.get_orders_at_price("BTC/USD", "BUY", 50000.0)
    assert len(orders) == 1
    assert orders[0].id == 1


def test_get_best_bid_ask(orderbook):
    order1 = Order(
        id=1,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=1.0,
        filled_quantity=0.0,
    )
    order2 = Order(
        id=2,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50100.0,
        quantity=1.0,
        filled_quantity=0.0,
    )
    order3 = Order(
        id=3,
        symbol="BTC/USD",
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        price=50200.0,
        quantity=1.0,
        filled_quantity=0.0,
    )
    order4 = Order(
        id=4,
        symbol="BTC/USD",
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        price=50300.0,
        quantity=1.0,
        filled_quantity=0.0,
    )
    orderbook.add_order("BTC/USD", "BUY", 50000.0, order1)
    orderbook.add_order("BTC/USD", "BUY", 50100.0, order2)
    orderbook.add_order("BTC/USD", "SELL", 50200.0, order3)
    orderbook.add_order("BTC/USD", "SELL", 50300.0, order4)
    assert orderbook.get_best_bid("BTC/USD") == 50100
    assert orderbook.get_best_ask("BTC/USD") == 50200


def test_remove_order(orderbook):
    order = Order(
        id=1,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=1.0,
        filled_quantity=0.0,
    )
    orderbook.add_order("BTC/USD", "BUY", 50000.0, order)
    assert len(orderbook.get_orders_at_price("BTC/USD", "BUY", 50000.0)) == 1
    orderbook.remove_order("BTC/USD", "BUY", 50000.0, 1)

    assert len(orderbook.get_orders_at_price("BTC/USD", "BUY", 50000.0)) == 0
    assert orderbook.get_best_bid("BTC/USD") is None


def test_get_snapshot(orderbook):
    order1 = Order(
        id=1,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=2.0,
        filled_quantity=0.5,
    )
    order2 = Order(
        id=2,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=1.0,
        filled_quantity=0.0,
    )

    orderbook.add_order("BTC/USD", "BUY", 50000.0, order1)
    orderbook.add_order("BTC/USD", "BUY", 50000.0, order2)

    snapshot = orderbook.get_snapshot("BTC/USD")

    assert len(snapshot["bids"]) == 1
    assert snapshot["bids"][0]["price"] == 50000.0

    assert snapshot["bids"][0]["quantity"] == 2.5
    assert len(snapshot["asks"]) == 0
