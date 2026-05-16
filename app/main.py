import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select

from app.database import engine, Base, async_session_maker
from app.redis_client import init_redis, close_client
from app.models.order import Order, OrderStatus

from app.api import orders_router, market_router
from app.api.market import global_book_order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Connecting to Redis...")
    await init_redis()

    logger.info("Restoring active orders into the in-memory orderbook...")
    async with async_session_maker() as session:
        result = await session.execute(
            select(Order).where(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED])
            )
        )
        active_orders = result.scalars().all()

        restored_count = 0
        for order in active_orders:
            global_book_order.add_order(
                symbol=order.symbol, side=order.side, price=order.price, order=order
            )
            restored_count += 1

        logger.info(f"Successfully loaded {restored_count} active orders.")

    logger.info("Order Matching Engine Started Successfully!")

    yield

    logger.info("Closing Database connection....")
    await engine.dispose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Order Matching Engine",
    description="High-performance async order matching backend",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(market_router, tags=["Market Data"])


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "Order Matching Engine", "version": "1.0.0"}
