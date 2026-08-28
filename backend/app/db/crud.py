from datetime import datetime, timezone
from typing import Optional, Sequence
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    DNSQuery, ThreatEntry, Whitelist, CustomBlocklist,
    FeedSyncLog, MLPrediction, TunnelIncident,
)


class DNSQueryCRUD:
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> DNSQuery:
        query = DNSQuery(**kwargs)
        db.add(query)
        await db.flush()
        return query

    @staticmethod
    async def get_recent(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        verdict: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Sequence[DNSQuery]:
        stmt = select(DNSQuery).order_by(desc(DNSQuery.queried_at))
        if verdict:
            stmt = stmt.where(DNSQuery.verdict == verdict)
        if search:
            stmt = stmt.where(DNSQuery.domain.ilike(f"%{search}%"))
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        base = select(func.count()).select_from(DNSQuery).where(DNSQuery.queried_at >= today_start)
        
        total = (await db.execute(base)).scalar() or 0
        blocked = (await db.execute(base.where(DNSQuery.verdict != "ALLOWED"))).scalar() or 0
        tunneling = (await db.execute(base.where(DNSQuery.is_tunneling == True))).scalar() or 0
        
        return {
            "total_queries": total,
            "blocked_queries": blocked,
            "allowed_queries": total - blocked,
            "tunneling_detected": tunneling,
        }

    @staticmethod
    async def get_top_blocked(
        db: AsyncSession, limit: int = 20
    ) -> Sequence[tuple]:
        stmt = (
            select(DNSQuery.domain, func.count().label("count"))
            .where(DNSQuery.verdict != "ALLOWED")
            .group_by(DNSQuery.domain)
            .order_by(desc("count"))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.all()


class ThreatEntryCRUD:
    @staticmethod
    async def upsert(db: AsyncSession, domain: str, source: str, category: str, **kwargs) -> ThreatEntry:
        stmt = select(ThreatEntry).where(ThreatEntry.domain == domain)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry:
            entry.last_seen = datetime.now(timezone.utc)
            entry.status = "active"
            for k, v in kwargs.items():
                setattr(entry, k, v)
        else:
            entry = ThreatEntry(domain=domain, source=source, category=category, **kwargs)
            db.add(entry)
        await db.flush()
        return entry


class BlocklistCRUD:
    @staticmethod
    async def list_entries(
        db: AsyncSession, limit: int = 50, offset: int = 0
    ) -> Sequence[CustomBlocklist]:
        stmt = (
            select(CustomBlocklist)
            .order_by(desc(CustomBlocklist.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def add(db: AsyncSession, domain: str, added_by: str = "admin", reason: str = "") -> CustomBlocklist:
        entry = CustomBlocklist(domain=domain.lower().strip(), added_by=added_by, reason=reason)
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def delete(db: AsyncSession, entry_id: int) -> bool:
        stmt = select(CustomBlocklist).where(CustomBlocklist.id == entry_id)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry:
            await db.delete(entry)
            return True
        return False


class WhitelistCRUD:
    @staticmethod
    async def list_entries(
        db: AsyncSession, limit: int = 50, offset: int = 0
    ) -> Sequence[Whitelist]:
        stmt = (
            select(Whitelist)
            .order_by(desc(Whitelist.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def add(db: AsyncSession, domain: str, added_by: str = "admin", reason: str = "") -> Whitelist:
        entry = Whitelist(domain=domain.lower().strip(), added_by=added_by, reason=reason)
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def delete(db: AsyncSession, entry_id: int) -> bool:
        stmt = select(Whitelist).where(Whitelist.id == entry_id)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry:
            await db.delete(entry)
            return True
        return False


class FeedSyncLogCRUD:
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> FeedSyncLog:
        log = FeedSyncLog(**kwargs)
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_latest(db: AsyncSession, limit: int = 10) -> Sequence[FeedSyncLog]:
        stmt = select(FeedSyncLog).order_by(desc(FeedSyncLog.synced_at)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


class TunnelIncidentCRUD:
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> TunnelIncident:
        incident = TunnelIncident(**kwargs)
        db.add(incident)
        await db.flush()
        return incident

    @staticmethod
    async def list_incidents(
        db: AsyncSession, limit: int = 50, offset: int = 0, status: Optional[str] = None
    ) -> Sequence[TunnelIncident]:
        stmt = select(TunnelIncident).order_by(desc(TunnelIncident.detected_at))
        if status:
            stmt = stmt.where(TunnelIncident.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_status(db: AsyncSession, incident_id: int, status: str) -> Optional[TunnelIncident]:
        stmt = select(TunnelIncident).where(TunnelIncident.id == incident_id)
        result = await db.execute(stmt)
        incident = result.scalar_one_or_none()
        if incident:
            incident.status = status
            if status == "resolved":
                incident.resolved_at = datetime.now(timezone.utc)
            await db.flush()
        return incident
