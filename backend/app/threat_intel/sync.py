"""Threat intelligence feed synchronization."""
import importlib
import traceback
from datetime import datetime
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.logging import logger
from app.db.session import async_session_factory
from app.db.crud import ThreatEntryCRUD, FeedSyncLogCRUD
from app.core.redis import redis_client
from app.threat_intel.feeds import ThreatFeed

FEEDS: list[ThreatFeed] = [
    ThreatFeed(
        name="StevenBlack",
        url="https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
        category="malware",
        parser_func="stevenblack.parse"
    ),
    ThreatFeed(
        name="URLhaus",
        url="https://urlhaus.abuse.ch/downloads/csv/",
        category="malware",
        parser_func="urlhaus.parse"
    ),
    ThreatFeed(
        name="OpenPhish",
        url="https://openphish.com/feed.txt",
        category="phishing",
        parser_func="openphish.parse"
    ),
    ThreatFeed(
        name="FeodoTracker",
        url="https://feodotracker.abuse.ch/downloads/domainblocklist.txt",
        category="botnet",
        parser_func="feodo.parse"
    ),
    ThreatFeed(
        name="PhishTank",
        url="https://data.phishtank.com/data/online-valid.json",
        category="phishing",
        parser_func="phishtank.parse"
    ),
]

REDIS_BLOCKLIST_KEY = "dns:blocklist"

async def _fetch_feed(client: httpx.AsyncClient, url: str) -> str:
    """Fetch feed content from URL."""
    # Using a common user agent to avoid being blocked by some feeds
    headers = {"User-Agent": "SIH-DNS-Security/1.0"}
    response = await client.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()
    return response.text

async def sync_feed(feed: ThreatFeed) -> None:
    """Synchronize a single threat intelligence feed."""
    if not feed.enabled:
        return

    logger.info(f"Starting sync for feed {feed.name} ({feed.category})")
    start_time = datetime.utcnow()
    success = False
    domains_added = 0
    error_message = None

    try:
        # Fetch content
        async with httpx.AsyncClient() as client:
            content = await _fetch_feed(client, feed.url)

        # Import parser dynamically
        module_name, func_name = feed.parser_func.split('.')
        parser_module = importlib.import_module(f"app.threat_intel.parsers.{module_name}")
        parser_func_callable = getattr(parser_module, func_name)

        # Parse content
        domains = await parser_func_callable(content)
        
        if not domains:
            logger.warning(f"No domains parsed from {feed.name}")
            success = True
        else:
            # Update database
            async with async_session_factory() as session:
                domains_added = await ThreatEntryCRUD.upsert_domains(
                    session=session,
                    domains=list(domains),
                    source=feed.name,
                    category=feed.category
                )
                
                # Update Redis cache
                if domains:
                    await redis_client.sadd(REDIS_BLOCKLIST_KEY, *domains)
                
                await session.commit()
            
            logger.info(f"Successfully synced {feed.name}. Added {domains_added} domains.")
            success = True

    except Exception as e:
        logger.error(f"Error syncing feed {feed.name}: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        # Log the sync result
        try:
            async with async_session_factory() as session:
                await FeedSyncLogCRUD.create(
                    session=session,
                    feed_name=feed.name,
                    status="SUCCESS" if success else "FAILED",
                    records_added=domains_added,
                    error_message=error_message,
                    start_time=start_time,
                    end_time=end_time
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save sync log for {feed.name}: {str(e)}")

async def sync_all_feeds() -> None:
    """Synchronize all enabled threat feeds."""
    logger.info("Starting synchronization of all threat feeds...")
    for feed in FEEDS:
        await sync_feed(feed)
    logger.info("Completed synchronization of all threat feeds.")

def start_feed_scheduler() -> AsyncIOScheduler:
    """Initialize and start the async scheduler for feed synchronization."""
    scheduler = AsyncIOScheduler()
    
    # Get interval from settings, default to 60 minutes
    interval_minutes = getattr(settings, 'feed_sync_interval_minutes', 60)
    
    scheduler.add_job(
        sync_all_feeds,
        'interval',
        minutes=interval_minutes,
        id='sync_threat_feeds',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Started feed sync scheduler with interval of {interval_minutes} minutes.")
    return scheduler
