import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "Order Matching Engine",
            "version": "1.0.0",
        }


@pytest.mark.asyncio
async def test_create_limit_order():
    payload = {
        "symbol": "ETH/USD",
        "side": "BUY",
        "type": "LIMIT",
        "price": 3000.50,
        "quantity": 2.0,
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/orders/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "ETH/USD"
        assert data["status"] == "PENDING"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_orderbook():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/orderbook/ETH/USD")
        assert response.status_code == 200
        data = response.json()
        assert "bids" in data
        assert "asks" in data


@pytest.mark.asyncio
async def test_cancel_order():
    payload = {
        "symbol": "ETH/USD",
        "side": "SELL",
        "type": "LIMIT",
        "price": 3100.00,
        "quantity": 1.0,
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        create_response = await ac.post("/api/orders/", json=payload)
        if create_response.status_code != 200:
            print("ERROR DETAILS:", create_response.text)
        assert create_response.status_code == 200
        order_id = create_response.json()["id"]

        cancel_response = await ac.delete(f"/api/orders/{order_id}")
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "CANCELLED"
