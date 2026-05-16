from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas import TradeResponse
from app.services import MarketDataService, OrderBookService
from app.websocket.handlers import manager

router = APIRouter()

global_book_order = OrderBookService()


def get_market_data_service(db: AsyncSession = Depends(get_db)) -> MarketDataService:
    return MarketDataService(db, global_book_order)


@router.get("/orderbook/{symbol:path}")
async def get_orderbook(
    symbol: str, market_service: MarketDataService = Depends(get_market_data_service)
):
    return await market_service.get_orderbook_snapshot(symbol)


@router.get("/trades/{symbol:path}")
async def get_recent_trades(
    symbol: str,
    limit: int = 50,
    market_service: MarketDataService = Depends(get_market_data_service),
):
    return await market_service.get_recent_trades(symbol, limit)


@router.websocket("/ws/market/{symbol:path}")
async def market_websocket(websocket: WebSocket, symbol: str):
    await manager.connect(websocket, symbol)

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
