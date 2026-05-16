from datetime import datetime

from pydantic import BaseModel, Field
from app.models import OrderSide, OrderType, OrderStatus


class OrderCreateRequest(BaseModel):
    symbol: str = Field(..., examples=["BTC/USD"])
    side: OrderSide = Field(..., examples=["BUY"])
    type: OrderType = Field(..., examples=["LIMIT"])
    price: float = Field(..., examples=["45000.50"])
    quantity: float = Field(..., examples=["0.5"])


class OrderResponse(BaseModel):
    id: int
    symbol: str
    side: OrderSide
    type: OrderType
    price: float
    quantity: float
    filled_quantity: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
