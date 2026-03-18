import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


async def get_redis():
    """Provide a Redis client instance for caching and blacklisting refresh tokens."""
    return redis_client
