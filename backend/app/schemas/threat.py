from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ThreatEntryResponse(BaseModel):
    id: int
    domain: str
    source: str
    category: str
    status: str
    first_seen: datetime
    last_seen: datetime

    model_config = {"from_attributes": True}


class FeedStatusResponse(BaseModel):
    feed_name: str
    last_sync: Optional[datetime] = None
    status: str
    domains_count: int
    is_enabled: bool


class FeedSyncLogResponse(BaseModel):
    id: int
    feed_name: str
    status: str
    domains_added: int
    domains_removed: int
    total_domains: int
    duration_seconds: float
    error_message: Optional[str] = None
    synced_at: datetime

    model_config = {"from_attributes": True}
