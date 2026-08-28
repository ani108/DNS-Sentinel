"""Blocklist and Whitelist management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.api.deps import get_db, get_redis
from app.db.crud import BlocklistCRUD, WhitelistCRUD
from app.schemas.dashboard import (
    BlocklistEntry,
    BlocklistAddRequest,
    WhitelistEntry,
    WhitelistAddRequest,
)
from app.core.constants import REDIS_BLOCKLIST_KEY, REDIS_WHITELIST_KEY

router = APIRouter()


# ── Blocklist ──────────────────────────────────────────────────────

@router.get("/blocklist", response_model=list[BlocklistEntry])
async def list_blocklist(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """List custom blocklist entries."""
    entries = await BlocklistCRUD.list_entries(db, limit=limit, offset=offset)
    return entries


@router.post("/blocklist", response_model=list[BlocklistEntry])
async def add_to_blocklist(
    request: BlocklistAddRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Add domain(s) to the custom blocklist."""
    entries = []
    for domain in request.domains:
        domain_clean = domain.lower().strip()
        if not domain_clean:
            continue
        try:
            entry = await BlocklistCRUD.add(db, domain_clean, reason=request.reason)
            entries.append(entry)
            # Also add to Redis blocklist for immediate effect
            await redis.sadd(REDIS_BLOCKLIST_KEY, domain_clean)
        except Exception:
            pass  # Skip duplicates
    return entries


@router.delete("/blocklist/{entry_id}")
async def remove_from_blocklist(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Remove an entry from the custom blocklist."""
    # Get the domain before deleting so we can remove from Redis
    from sqlalchemy import select
    from app.db.models import CustomBlocklist
    stmt = select(CustomBlocklist).where(CustomBlocklist.id == entry_id)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    domain = entry.domain
    deleted = await BlocklistCRUD.delete(db, entry_id)
    if deleted:
        await redis.srem(REDIS_BLOCKLIST_KEY, domain)
    
    return {"deleted": deleted, "domain": domain}


# ── Whitelist ──────────────────────────────────────────────────────

@router.get("/whitelist", response_model=list[WhitelistEntry])
async def list_whitelist(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """List whitelist entries."""
    entries = await WhitelistCRUD.list_entries(db, limit=limit, offset=offset)
    return entries


@router.post("/whitelist", response_model=list[WhitelistEntry])
async def add_to_whitelist(
    request: WhitelistAddRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Add domain(s) to the whitelist."""
    entries = []
    for domain in request.domains:
        domain_clean = domain.lower().strip()
        if not domain_clean:
            continue
        try:
            entry = await WhitelistCRUD.add(db, domain_clean, reason=request.reason)
            entries.append(entry)
            # Also add to Redis whitelist for immediate effect
            await redis.sadd(REDIS_WHITELIST_KEY, domain_clean)
            # Remove from blocklist if present
            await redis.srem(REDIS_BLOCKLIST_KEY, domain_clean)
        except Exception:
            pass  # Skip duplicates
    return entries


@router.delete("/whitelist/{entry_id}")
async def remove_from_whitelist(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Remove an entry from the whitelist."""
    from sqlalchemy import select
    from app.db.models import Whitelist as WhitelistModel
    stmt = select(WhitelistModel).where(WhitelistModel.id == entry_id)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    domain = entry.domain
    deleted = await WhitelistCRUD.delete(db, entry_id)
    if deleted:
        await redis.srem(REDIS_WHITELIST_KEY, domain)
    
    return {"deleted": deleted, "domain": domain}
