from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class StatsSummary(BaseModel):
    total_queries: int
    blocked_queries: int
    allowed_queries: int
    tunneling_detected: int
    active_feeds: int = 0
    blocklist_size: int = 0


class HourlyStat(BaseModel):
    hour: str  # "2024-01-15-14"
    allowed: int
    blocked: int
    tunneling: int


class TopBlockedDomain(BaseModel):
    domain: str
    count: int


class TopClient(BaseModel):
    client_ip: str
    query_count: int


class ThreatCategoryBreakdown(BaseModel):
    category: str
    count: int


class BlocklistEntry(BaseModel):
    id: int
    domain: str
    added_by: str
    reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BlocklistAddRequest(BaseModel):
    domains: List[str]
    reason: str = ""


class WhitelistEntry(BaseModel):
    id: int
    domain: str
    added_by: str
    reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WhitelistAddRequest(BaseModel):
    domains: List[str]
    reason: str = ""


class TunnelIncidentResponse(BaseModel):
    id: int
    base_domain: str
    client_ip: Optional[str] = None
    unique_subdomains: int
    avg_entropy: float
    avg_subdomain_length: float
    severity: str
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TunnelIncidentUpdate(BaseModel):
    status: str  # resolved, false_positive


class SettingsResponse(BaseModel):
    upstream_dns: str
    ml_threshold: float
    feed_sync_interval_minutes: int
    dns_port: int


class SettingsUpdate(BaseModel):
    upstream_dns: Optional[str] = None
    ml_threshold: Optional[float] = None
    feed_sync_interval_minutes: Optional[int] = None
