"""Aggregated API v1 router."""
from fastapi import APIRouter

# Import route modules
# These will be created in Phase 5. For now, use empty routers as placeholders.
from app.api.v1 import dashboard, blocklist, analyze, settings as settings_routes

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(blocklist.router, tags=["Blocklist & Whitelist"])
api_router.include_router(analyze.router, tags=["Domain Analysis"])
api_router.include_router(settings_routes.router, tags=["Settings"])
