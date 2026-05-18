from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from app.models import OrderSide, OrderType, OrderStatus


class OrderCreateRequest(BaseModel):
    symbol: str = Field(..., examples=["BTC/USD"])
    side: OrderSide = Field(..., examples=["BUY"])
    type: OrderType = Field(..., examples=["LIMIT"])
    price: Optional[float] = Field(0.0, examples=["45000.50"])
    quantity: float = Field(..., examples=["0.5"])

    @model_validator(mode="after")
    def check_price_for_limit_order(self):
        if self.type == OrderType.LIMIT and (self.price is None or self.price <= 0):
            raise ValueError("LIMIT orders require a price greater than 0")
        if self.type == OrderType.MARKET and self.price is None:
            self.price = 0.0
        return self


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
