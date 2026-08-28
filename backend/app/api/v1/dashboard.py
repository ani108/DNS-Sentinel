"""Dashboard and analytics API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.api.deps import get_db, get_redis
from app.db.crud import DNSQueryCRUD, TunnelIncidentCRUD
from app.schemas.dashboard import (
    StatsSummary,
    HourlyStat,
    TopBlockedDomain,
    TunnelIncidentResponse,
    TunnelIncidentUpdate,
)
from app.schemas.dns import DNSQueryResponse
from app.core.constants import REDIS_BLOCKLIST_KEY, REDIS_STATS_TOTAL, REDIS_STATS_BLOCKED

router = APIRouter()


@router.get("/stats/summary", response_model=StatsSummary)
async def get_stats_summary(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get summary statistics for the dashboard."""
    db_stats = await DNSQueryCRUD.get_stats(db)
    blocklist_size = await redis.scard(REDIS_BLOCKLIST_KEY)
    
    return StatsSummary(
        total_queries=db_stats["total_queries"],
        blocked_queries=db_stats["blocked_queries"],
        allowed_queries=db_stats["allowed_queries"],
        tunneling_detected=db_stats["tunneling_detected"],
        active_feeds=5,  # TODO: dynamic count from feed status
        blocklist_size=blocklist_size,
    )


@router.get("/stats/hourly", response_model=list[HourlyStat])
async def get_hourly_stats(
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get hourly query statistics for timeline chart (last 48h)."""
    from datetime import datetime, timedelta, timezone
    
    stats = []
    now = datetime.now(timezone.utc)
    
    for i in range(48):
        hour = now - timedelta(hours=i)
        key = f"stats:hourly:{hour.strftime('%Y-%m-%d-%H')}"
        data = await redis.hgetall(key)
        stats.append(HourlyStat(
            hour=hour.strftime("%Y-%m-%d-%H"),
            allowed=int(data.get("allowed", 0)),
            blocked=int(data.get("blocked", 0)),
            tunneling=int(data.get("tunneling", 0)),
        ))
    
    return list(reversed(stats))


@router.get("/stats/top-blocked", response_model=list[TopBlockedDomain])
async def get_top_blocked(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """Get top blocked domains."""
    results = await DNSQueryCRUD.get_top_blocked(db, limit=limit)
    return [TopBlockedDomain(domain=r[0], count=r[1]) for r in results]


@router.get("/queries/recent", response_model=list[DNSQueryResponse])
async def get_recent_queries(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    verdict: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get recent DNS queries with optional filtering."""
    queries = await DNSQueryCRUD.get_recent(
        db, limit=limit, offset=offset, verdict=verdict, search=search
    )
    return queries


@router.get("/tunneling/incidents", response_model=list[TunnelIncidentResponse])
async def get_tunnel_incidents(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
):
    """List detected DNS tunneling incidents."""
    incidents = await TunnelIncidentCRUD.list_incidents(
        db, limit=limit, offset=offset, status=status
    )
    return incidents


@router.patch("/tunneling/incidents/{incident_id}", response_model=TunnelIncidentResponse)
async def update_tunnel_incident(
    incident_id: int,
    update: TunnelIncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a tunneling incident status (resolved/false_positive)."""
    incident = await TunnelIncidentCRUD.update_status(db, incident_id, update.status)
    if not incident:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
