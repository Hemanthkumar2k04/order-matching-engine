import redis.asyncio as redis
from app.config import settings
import json

redis_client = None


async def init_redis():
    global redis_client
    redis_url = (
        f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        if settings.REDIS_PASSWORD
        else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    )
    redis_client = redis.from_url(redis_url)


async def close_client():
    if redis_client:
        await redis_client.aclose()


async def set_cache(key: str, value: dict | list | str, exp: int):
    if redis_client:
        await redis_client.set(key, json.dumps(value), ex=exp)


async def get_cache(key: str):
    if redis_client:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
    return None
