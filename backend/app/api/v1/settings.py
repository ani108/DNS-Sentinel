"""Settings API endpoints."""
from fastapi import APIRouter
from app.config import settings
from app.schemas.dashboard import SettingsResponse, SettingsUpdate

router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """Get current application settings."""
    return SettingsResponse(
        upstream_dns=settings.upstream_dns,
        ml_threshold=settings.ml_threshold,
        feed_sync_interval_minutes=settings.feed_sync_interval_minutes,
        dns_port=settings.dns_port,
    )


@router.patch("/settings", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate):
    """Update application settings.
    
    Note: In a production app, these would be persisted to a database.
    For the SIH demo, we update the in-memory settings object.
    Changes take effect immediately but don't survive restarts.
    """
    if update.upstream_dns is not None:
        settings.upstream_dns = update.upstream_dns
    if update.ml_threshold is not None:
        settings.ml_threshold = update.ml_threshold
    if update.feed_sync_interval_minutes is not None:
        settings.feed_sync_interval_minutes = update.feed_sync_interval_minutes
    
    return SettingsResponse(
        upstream_dns=settings.upstream_dns,
        ml_threshold=settings.ml_threshold,
        feed_sync_interval_minutes=settings.feed_sync_interval_minutes,
        dns_port=settings.dns_port,
    )
