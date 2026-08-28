import redis.asyncio as aioredis
from app.config import settings

class RedisManager:
    """Manages Redis connection pool."""
    _pool: aioredis.Redis | None = None

    @classmethod
    async def connect(cls) -> None:
        cls._pool = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=50,
        )

    @classmethod
    async def disconnect(cls) -> None:
        if cls._pool:
            await cls._pool.aclose()
            cls._pool = None

    @classmethod
    def get_client(cls) -> aioredis.Redis:
        if cls._pool is None:
            raise RuntimeError("Redis not connected. Call RedisManager.connect() first.")
        return cls._pool

redis_client = RedisManager  # Alias for convenience
