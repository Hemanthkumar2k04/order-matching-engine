# Order Matching Engine - Tech Stack & Architecture

## Tech Stack

- **Framework:** FastAPI (async, built-in WebSocket)
- **Database:** PostgreSQL (orders, trades, audit logs)
- **Cache:** Redis (recent trades, market snapshots, session management)
- **Order Book:** `sortedcontainers.SortedDict` (for price levels)
- **Concurrency:** asyncio + ThreadPoolExecutor (matching is CPU-bound)
- **Testing:** pytest + locust (load testing)
- **Deployment:** Docker + docker-compose

## Core Architecture

### 4 Main Layers:

#### 1. API Layer (FastAPI)

- `POST /api/orders` - Place order
- `GET /api/orders/{id}` - Order status
- `GET /api/orderbook/{symbol}` - Order book snapshot
- `GET /api/trades/{symbol}` - Recent trades
- `WebSocket /ws/market/{symbol}` - Real-time updates

#### 2. Service Layer (Business Logic)

- **OrderBookService** - Manages order book state
- **MatchingEngine** - Core matching algorithm
- **OrderService** - Order CRUD + status tracking
- **MarketDataService** - Aggregates market data

#### 3. Data Layer (Database + Cache)

- **PostgreSQL:** orders, trades, price history
- **Redis:** order book snapshots, recent trades cache

#### 4. Event System (WebSocket Broadcasting)

- Publish trades immediately to connected clients
- Broadcast order book updates

---

## Data Models

### Order

- `id`, `symbol`, `side` (BUY/SELL), `type` (LIMIT/MARKET), `price`, `quantity`
- `status` (PENDING/PARTIALLY_FILLED/FILLED/CANCELLED)
- `created_at`, `updated_at`

### Trade

- `id`, `symbol`, `buy_order_id`, `sell_order_id`
- `price`, `quantity`, `timestamp`

### OrderBook (In-Memory)

- `symbol` → `{bids: SortedDict, asks: SortedDict}`
- Each level → queue of orders

---

## Project Structure

```text
order-matching-engine/
├── app/
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── order.py
│   │   ├── trade.py
│   │   └── __init__.py
│   ├── schemas/          # Pydantic request/response schemas
│   │   ├── order.py
│   │   ├── trade.py
│   │   └── __init__.py
│   ├── services/         # Business logic
│   │   ├── orderbook_service.py
│   │   ├── matching_engine.py
│   │   ├── order_service.py
│   │   ├── market_data_service.py
│   │   └── __init__.py
│   ├── api/              # FastAPI routes
│   │   ├── orders.py     # Order endpoints
│   │   ├── market.py     # Market data endpoints
│   │   └── __init__.py
│   ├── websocket/        # WebSocket handlers
│   │   ├── handlers.py
│   │   └── __init__.py
│   ├── database.py       # SQLAlchemy setup
│   ├── redis_client.py   # Redis connection
│   ├── config.py         # Settings (DB URL, Redis, etc)
│   └── main.py           # FastAPI app initialization
├── tests/
│   ├── test_orderbook.py
│   ├── test_matching.py
│   └── test_api.py
├── docker-compose.yml    # PostgreSQL + Redis
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Key Design Decisions

### Order Book (In-Memory)

- NOT in database - refreshed on app start
- Built from DB orders with status = `PENDING`/`PARTIALLY_FILLED`
- Gives you fast price level lookups (O(log n))

### Matching Strategy

- Price-time priority (highest/lowest price, then FIFO)
- Limit orders only for MVP
- Market orders in Week 2

### Concurrency Model

- FastAPI async for I/O (API calls, WebSocket)
- ThreadPoolExecutor for matching engine (CPU-bound)
- ReentrantLock on OrderBook for thread safety

### Persistence

- Orders/trades → PostgreSQL (audit trail)
- Recent market data → Redis cache (fast retrieval)

### Scalability Metrics

- Target: 1000 orders/sec (Week 3 goal: 5000/sec with optimization)
- Measure with locust load testing
