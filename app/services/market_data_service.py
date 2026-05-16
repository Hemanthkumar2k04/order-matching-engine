from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Trade
from app.services import OrderBookService
from app.redis_client import get_cache, set_cache
import json


class MarketDataService:
    def __init__(self, db: AsyncSession, order_book: OrderBookService):
        self.db = db
        self.order_book = order_book

    async def get_orderbook_snapshot(self, symbol: str) -> dict:
        data = await get_cache(f"snapshot:{symbol}")
        if data:
            return data

        snapshot = self.order_book.get_snapshot(symbol=symbol)

        await set_cache(f"snapshot:{symbol}", snapshot, 5)

        return snapshot

    async def get_recent_trades(self, symbol: str, limit: int = 50) -> list[Trade]:
        data = await get_cache(f"recent_trades:{symbol}")

        if data:
            return data

        def trade_to_dict(t: Trade):
            t["timestamp"] = t.timestamp.isoformat()
            return t

        statement = (
            select(Trade)
            .where(Trade.symbol == symbol)
            .order_by(desc(Trade.timestamp))
            .limit(limit)
        )
        result = await self.db.execute(statement)
        rows = list(result.scalars().all())

        data = [trade_to_dict(t) for t in rows]

        return data
