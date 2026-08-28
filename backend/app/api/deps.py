"""Dependency injection for FastAPI endpoints."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from app.db.session import async_session_factory
from app.core.redis import RedisManager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis() -> aioredis.Redis:
    """Return the Redis client."""
    return RedisManager.get_client()
