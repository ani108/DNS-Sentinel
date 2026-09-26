"""DNS Security Service — Main Application Entry Point.

Starts the FastAPI server and the DNS proxy concurrently.
"""
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import logger
from app.core.redis import RedisManager
from app.db.session import init_db
from app.dns_engine.server import start_dns_server
from app.ws.traffic import router as ws_router, redis_subscriber
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──
    logger.info("Starting DNS Security Service...")
    
    # Connect to Redis
    await RedisManager.connect()
    logger.info("Redis connected")
    
    # Initialize database tables
    await init_db()
    logger.info("Database initialized")
    
    # Start DNS proxy server
    dns_transport = None
    try:
        dns_transport = await start_dns_server()
        logger.info("DNS Proxy server started")
    except PermissionError:
        logger.error(
            f"Cannot bind to port {settings.dns_port}. "
            "Try running with elevated privileges or use a port > 1024."
        )
    except OSError as e:
        logger.error(f"DNS server bind error: {e}")
    
    # Start WebSocket Redis subscriber
    subscriber_task = asyncio.create_task(redis_subscriber())
    logger.info("WebSocket Redis subscriber started")
    
    # Start threat feed scheduler
    scheduler_task = None
    try:
        from app.threat_intel.sync import start_feed_scheduler
        scheduler_task = await start_feed_scheduler()
        logger.info("Threat feed scheduler started")
    except ImportError:
        logger.warning("Threat intel module not yet available — skipping feed sync")
    except Exception as e:
        logger.warning(f"Feed scheduler start error: {e}")
    
    # Initialize ML model
    try:
        from app.ml.classifier import DomainClassifier
        DomainClassifier.get_instance()
    except Exception as e:
        logger.warning(f"ML model initialization: {e}")
    
    logger.info("DNS Security Service started successfully")
    logger.info(f"API docs available at http://{settings.api_host}:{settings.api_port}/docs")
    
    yield  # ── Application is running ──
    
    # ── Shutdown ──
    logger.info("Shutting down DNS Security Service...")
    
    subscriber_task.cancel()
    if dns_transport:
        dns_transport.close()
    
    await RedisManager.disconnect()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="DNS Security Service",
    description="DNS Filtering Service using Threat Intelligence and AI/ML",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dns-security"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info",
    )
