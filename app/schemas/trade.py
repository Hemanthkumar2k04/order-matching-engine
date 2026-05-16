from datetime import datetime
from pydantic import BaseModel


class TradeResponse(BaseModel):
    id: int
    symbol: str
    buy_order_id: int
    sell_order_id: int
    price: float
    quantity: float
    timestamp: datetime

    class Config:
        from_attributes = True
