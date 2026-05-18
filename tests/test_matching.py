import pytest
from app.models.order import Order, OrderSide, OrderType
from app.services.orderbook_service import OrderBookService
from app.services.matching_engine import MatchingEngine

@pytest.fixture
def orderbook():
    return OrderBookService()

@pytest.fixture
def matching_engine(orderbook):
    return MatchingEngine(orderbook)

@pytest.mark.asyncio
async def test_match_exact_price(orderbook, matching_engine):
    # Setup resting SELL order
    sell_order = Order(
        id=1,
        symbol="BTC/USD",
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=2.0,
        filled_quantity=0.0
    )
    orderbook.add_order("BTC/USD", "SELL", 50000.0, sell_order)
    
    # Incoming BUY order
    buy_order = Order(
        id=2,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=50000.0,
        quantity=1.0,
        filled_quantity=0.0
    )
    
    trades = await matching_engine.match_order(buy_order)
    
    assert len(trades) == 1
    assert trades[0].quantity == 1.0
    assert trades[0].price == 50000.0
    assert trades[0].buy_order_id == 2
    assert trades[0].sell_order_id == 1
    assert sell_order.filled_quantity == 1.0

@pytest.mark.asyncio
async def test_market_order_sweep(orderbook, matching_engine):
    # Setup resting SELL orders
    sell_order1 = Order(id=1, symbol="BTC/USD", side=OrderSide.SELL, type=OrderType.LIMIT, price=50000.0, quantity=1.0, filled_quantity=0.0)
    sell_order2 = Order(id=2, symbol="BTC/USD", side=OrderSide.SELL, type=OrderType.LIMIT, price=50100.0, quantity=1.0, filled_quantity=0.0)
    orderbook.add_order("BTC/USD", "SELL", 50000.0, sell_order1)
    orderbook.add_order("BTC/USD", "SELL", 50100.0, sell_order2)
    
    # Incoming MARKET BUY order for 1.5
    buy_order = Order(
        id=3,
        symbol="BTC/USD",
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        price=0.0,
        quantity=1.5,
        filled_quantity=0.0
    )
    
    trades = await matching_engine.match_order(buy_order)
    
    assert len(trades) == 2
    assert trades[0].quantity == 1.0
    assert trades[0].price == 50000.0
    assert trades[1].quantity == 0.5
    assert trades[1].price == 50100.0
    assert sell_order1.filled_quantity == 1.0
    assert sell_order2.filled_quantity == 0.5
