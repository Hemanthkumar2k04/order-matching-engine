from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import OrderCreateRequest, OrderResponse
from app.services import OrderService, MatchingEngine

from app.api.market import global_book_order

global_matching_engine = MatchingEngine(global_book_order)

router = APIRouter()


def get_order_service(db: AsyncSession = Depends(get_db)):
    return OrderService(db, global_book_order, global_matching_engine)


@router.post("/", response_model=OrderResponse)
async def place_order(
    order_data: OrderCreateRequest,
    order_service: OrderService = Depends(get_order_service),
):
    try:
        order = await order_service.create_order(order_data)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_status(
    order_id: int, order_service: OrderService = Depends(get_order_service)
):
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order Not Found")
    return order


@router.delete("/{order_id}", response_model=OrderResponse)
async def cancel_order(
    order_id: int, order_service: OrderService = Depends(get_order_service)
):
    try:
        order = await order_service.cancel_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
