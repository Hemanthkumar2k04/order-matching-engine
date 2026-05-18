from locust import HttpUser, task, between
import random

class OrderMatchingUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def place_limit_buy(self):
        self.client.post("/api/orders/", json={
            "symbol": "BTC/USD",
            "side": "BUY",
            "type": "LIMIT",
            "price": round(random.uniform(49000, 50000), 2),
            "quantity": round(random.uniform(0.1, 2.0), 2)
        })

    @task(3)
    def place_limit_sell(self):
        self.client.post("/api/orders/", json={
            "symbol": "BTC/USD",
            "side": "SELL",
            "type": "LIMIT",
            "price": round(random.uniform(50000, 51000), 2),
            "quantity": round(random.uniform(0.1, 2.0), 2)
        })

    @task(1)
    def place_market_order(self):
        side = random.choice(["BUY", "SELL"])
        self.client.post("/api/orders/", json={
            "symbol": "BTC/USD",
            "side": side,
            "type": "MARKET",
            "quantity": round(random.uniform(0.1, 1.0), 2)
        })

    @task(2)
    def get_orderbook(self):
        self.client.get("/orderbook/BTC/USD")
