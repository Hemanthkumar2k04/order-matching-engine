# Order Matching Engine

A high-performance, asynchronous order matching engine built with **FastAPI**, **PostgreSQL**, and **Redis**. Designed for low-latency trading systems with real-time order book updates via WebSocket.

## Features

- **Fast Order Matching**: Price-time priority matching with 1000+ orders/sec throughput
- **Real-Time Updates**: WebSocket-based order book and trade streaming
- **In-Memory Order Book**: Efficient price-level lookups using `SortedDict`
- **Persistent Storage**: All orders and trades logged to PostgreSQL
- **Caching Layer**: Redis for market snapshots and recent trades
- **Async I/O**: FastAPI async throughout for non-blocking operations
- **Thread-Safe**: ReentrantLock protection for concurrent order matching
- **Load Testing**: Included Locust configuration for performance testing

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### Setup with Docker (Recommended)

1. **Clone and configure**:
   ```bash
   git clone <repository>
   cd order-matching-engine
   cp .env.example .env
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Verify services are healthy**:
   ```bash
   docker-compose ps
   ```

   All services should show "healthy" status.

4. **Access the API**:
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

### Local Development Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL and Redis**:
   ```bash
   # Start only the database and cache
   docker-compose up -d db cache
   ```

4. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Update .env with your local settings
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Docker Configuration

### Images Used

- **PostgreSQL 15-Alpine**: 31MB - lightweight database with AOF persistence
- **Redis 7-Alpine**: 13MB - high-performance in-memory cache
- **Python 3.11-Slim**: Multi-stage build for minimal production image

### Services

```yaml
db (PostgreSQL)
  - Port: 5432 (configurable via .env)
  - Credentials: POSTGRES_USER, POSTGRES_PASSWORD
  - Database: POSTGRES_DB
  - Health Check: Every 10s

cache (Redis)
  - Port: 6379 (configurable via .env)
  - Persistence: AOF enabled
  - Max Memory: 256MB (LRU eviction)
  - Health Check: Every 10s

app (FastAPI)
  - Port: 8000 (configurable via .env)
  - Depends on: db, cache (waits for health checks)
  - Auto-reload: Dev mode volume mount
```

### Environment Variables

See `.env.example` for all available options:

```bash
# App Settings
PROJECT_NAME="Order Matching Engine"
VERSION="0.1.0"
DEBUG=True
ENV="development"

# Database
DATABASE_URL="postgresql+asyncpg://user:password@db:5432/orders"

# Redis
REDIS_HOST="cache"
REDIS_PORT=6379
REDIS_DB=0

# Matching Engine
DEFAULT_SYMBOL="BTC/USD"
PRICE_PRECISION=2
QUANTITY_PRECISION=8

# Security
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Endpoints

### Orders

```http
POST   /api/orders                    # Place new order
GET    /api/orders/{id}               # Get order status
GET    /api/orders?symbol=BTC/USD    # Get orders by symbol
```

### Market Data

```http
GET    /api/orderbook/{symbol}        # Get order book snapshot
GET    /api/trades/{symbol}           # Get recent trades
GET    /api/market/summary/{symbol}   # Get market summary
```

### WebSocket

```http
WebSocket /ws/market/{symbol}         # Real-time order book & trade updates
```

## Architecture

### 4-Layer Design

1. **API Layer** (FastAPI Routes)
   - Endpoint validation via Pydantic schemas
   - Request/response serialization

2. **Service Layer** (Business Logic)
   - `OrderService`: Order CRUD operations
   - `OrderBookService`: In-memory order book state
   - `MatchingEngine`: Core matching algorithm
   - `MarketDataService`: Aggregated market data

3. **Data Layer** (Persistence)
   - **PostgreSQL**: Orders, trades, audit logs
   - **Redis**: Order book snapshots, recent trades cache

4. **Event System** (WebSocket Broadcasting)
   - Trade notifications
   - Order book updates

### Order Book Design

- **In-Memory**: `SortedDict` for O(log n) price-level lookups
- **Refreshed on Startup**: Built from all `PENDING` and `PARTIALLY_FILLED` orders
- **Not in Database**: Provides deterministic rebuilding from order history

### Concurrency Model

- **FastAPI Async**: Handles I/O operations (DB, WebSocket, Redis)
- **ThreadPoolExecutor**: CPU-bound matching algorithm runs in threads
- **ReentrantLock**: Thread-safe order book access

## Testing

### Unit Tests

```bash
pytest tests/
```

### With Coverage

```bash
pytest --cov=app tests/
```

### Load Testing

```bash
# Start the app first
docker-compose up

# In another terminal
locust -f locustfile.py --host=http://localhost:8000
```

Visit http://localhost:8089 to control the load test.

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f cache
```

### Reset Database

```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Restart fresh
```

### Connect to PostgreSQL

```bash
docker-compose exec db psql -U cypher -d orders
```

### Connect to Redis

```bash
docker-compose exec cache redis-cli
```

### Stop Services

```bash
docker-compose down      # Stop and remove containers
docker-compose stop      # Stop without removing
```

## Performance Targets

- **MVP Goal**: 1,000 orders/sec
- **Week 3 Goal**: 5,000 orders/sec (optimized)

Monitor with:
```bash
locust -f locustfile.py --headless -u 1000 -r 50 -t 5m
```

## Project Structure

```
order-matching-engine/
├── app/
│   ├── api/                    # FastAPI routes
│   │   ├── orders.py          # Order endpoints
│   │   └── market.py          # Market data endpoints
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── order.py
│   │   └── trade.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── order.py
│   │   └── trade.py
│   ├── services/               # Business logic
│   │   ├── orderbook_service.py
│   │   ├── matching_engine.py
│   │   ├── order_service.py
│   │   └── market_data_service.py
│   ├── websocket/              # WebSocket handlers
│   │   └── handlers.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings management
│   ├── database.py             # SQLAlchemy setup
│   └── redis_client.py         # Redis connection
├── tests/
│   ├── test_orderbook.py
│   ├── test_matching.py
│   └── test_api.py
├── Dockerfile                  # Multi-stage production image
├── docker-compose.yml          # Full stack orchestration
├── .dockerignore                # Docker build ignore rules
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── architecture.md             # Technical architecture docs
└── README.md                   # This file
```

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | Latest |
| Web Server | Uvicorn | Latest |
| Database | PostgreSQL | 15 |
| Cache | Redis | 7 |
| ORM | SQLAlchemy | Latest |
| Async Driver | asyncpg | Latest |
| Validation | Pydantic | v2 |
| Monitoring | health checks | Built-in |
| Testing | pytest | Latest |
| Load Testing | Locust | Latest |
| Containers | Docker | Latest |
| Orchestration | Docker Compose | 3.8 |

## Troubleshooting

### Port Already in Use

```bash
# Change ports in .env or docker-compose.yml
POSTGRES_PORT=5433
REDIS_PORT=6380
APP_PORT=8001
```

### Database Connection Failed

```bash
# Check db service logs
docker-compose logs db

# Verify network connectivity
docker-compose exec app ping db
```

### Redis Connection Issues

```bash
# Check redis service
docker-compose logs cache

# Verify redis-cli
docker-compose exec cache redis-cli ping
```

### App Won't Start

```bash
# Check app logs
docker-compose logs app

# Rebuild image (clears cache)
docker-compose build --no-cache app
docker-compose up app
```

## Contributing

1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass: `pytest`
4. Follow code style guidelines
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check `architecture.md` for design details
- Review tests for usage examples
- Open an issue on GitHub
