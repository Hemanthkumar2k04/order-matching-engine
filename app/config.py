from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field


class Settings(BaseSettings):

    PROJECT_NAME: str = "Order Matching Engine"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENV: str = "development"

    DB_URL: str = "postgresql+asyncpg://cypher:pass@localhost:5432/orders"
    DB_POOL_SIZE: int = Field(default=20, validation_alias="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, validation_alias="DB_MAX_OVERFLOW")

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    DEFAULT_SYMBOL: str = "BTC/USD"
    PRICE_PRECISION: int = 2
    QUANTITY_PRECISION: int = 8

    SECRET_KEY: str = "ordermatchingsystem"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:

    return Settings()


settings = get_settings()
