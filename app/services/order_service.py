from app.models.order import OrderType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Order, OrderStatus, OrderSide, Trade
from app.schemas import OrderCreateRequest
from app.services import MatchingEngine, OrderBookService
from app.websocket.handlers import manager


class OrderService:
    def __init__(
        self,
        db: AsyncSession,
        order_book: OrderBookService,
        matching_engine: MatchingEngine,
    ):
        self.db = db
        self.order_book = order_book
        self.matching_engine = matching_engine

    async def create_order(self, order_data: OrderCreateRequest) -> Order:
        order = Order(
            symbol=order_data.symbol,
            side=order_data.side,
            type=order_data.type,
            price=order_data.price,
            quantity=order_data.quantity,
            filled_quantity=0.0,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)

        trades = await self.matching_engine.match_order(order)

        if trades:
            total_traded = sum(t.quantity for t in trades)
            order.filled_quantity += total_traded
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIALLY_FILLED

            for trade in trades:
                self.db.add(trade)

                resting_order_id = (
                    trade.sell_order_id
                    if order.side == OrderSide.BUY
                    else trade.buy_order_id
                )
                result = await self.db.execute(
                    select(Order).where(Order.id == resting_order_id)
                )
                resting_order = result.scalar_one()
                resting_order.filled_quantity += trade.quantity
                if resting_order.filled_quantity >= resting_order.quantity:
                    resting_order.status = OrderStatus.FILLED
                else:
                    resting_order.status = OrderStatus.PARTIALLY_FILLED

                await manager.broadcast(
                    order.symbol,
                    {
                        "event": "Trade",
                        "data": {
                            "price": float(trade.price),
                            "quantity": float(trade.quantity),
                            "maker_order_id": resting_order_id,
                            "taker_order_id": order.id,
                            "timestamp": (
                                trade.timestamp.isoformat() if trade.timestamp else None
                            ),
                        },
                    },
                )

        if order.filled_quantity < order.quantity:
            if order.type == OrderType.LIMIT:
                self.order_book.add_order(
                    order.symbol, order.side, float(order.price), order
                )
            else:
                order.status = OrderStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel_order(self, order_id: int) -> Order | None:
        order = await self.get_order(order_id)
        if not order:
            return None

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel order in status {order.status.value}")

        # Remove from the in-memory order book
        self.order_book.remove_order(
            order.symbol, order.side.value, float(order.price), order.id
        )

        # Update in database
        order.status = OrderStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_order(self, order_id: int) -> Order | None:
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()
