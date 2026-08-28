"""DNS tunneling detection module."""
import time
from typing import Optional
import redis.asyncio as aioredis
from app.core.logging import logger
from app.core.constants import REDIS_TUNNEL_WINDOW_PREFIX
from app.ml.features import shannon_entropy
from app.db.session import async_session_factory
from app.db.crud import TunnelIncidentCRUD

class TunnelingDetector:
    """Detects DNS tunneling using heuristics and time-window aggregation."""

    ENTROPY_THRESHOLD = 3.85
    LENGTH_THRESHOLD = 40
    UNIQUE_SUBDOMAIN_THRESHOLD = 25
    WINDOW_SECONDS = 60
    TUNNEL_QTYPES = {"TXT", "NULL", "CNAME", "MX", "A"}

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def check(self, domain: str, qtype: str, client_ip: str) -> bool:
        """
        Check a DNS query for tunneling.
        Returns True if tunneling is detected, False otherwise.
        """
        try:
            parts = domain.split('.')
            if len(parts) < 3:
                return False
            
            # Extract base domain and subdomain
            base_domain = f"{parts[-2]}.{parts[-1]}"
            subdomain = ".".join(parts[:-2])

            if not self._heuristic_check(subdomain, qtype):
                return False

            count = await self._window_check(base_domain, subdomain)

            if count > self.UNIQUE_SUBDOMAIN_THRESHOLD:
                logger.warning(f"DNS Tunneling detected for {base_domain} from {client_ip} ({count} unique subdomains)")
                entropy = shannon_entropy(subdomain)
                
                async with async_session_factory() as db:
                    await TunnelIncidentCRUD.create(
                        db,
                        base_domain=base_domain,
                        client_ip=client_ip,
                        unique_subdomains=count,
                        avg_entropy=entropy,
                        avg_subdomain_length=float(len(subdomain)),
                        severity="high"
                    )
                    await db.commit()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error in TunnelingDetector: {e}")
            return False

    def _heuristic_check(self, subdomain: str, qtype: str) -> bool:
        """
        Check if the subdomain characteristics match tunneling patterns.
        """
        if qtype.upper() not in self.TUNNEL_QTYPES:
            return False
            
        if len(subdomain) > self.LENGTH_THRESHOLD:
            return True
            
        entropy = shannon_entropy(subdomain)
        if entropy > self.ENTROPY_THRESHOLD:
            return True
            
        return False

    async def _window_check(self, base_domain: str, subdomain: str) -> int:
        """
        Update the sliding window for the base domain and return the number of unique subdomains.
        """
        key = f"{REDIS_TUNNEL_WINDOW_PREFIX}:{base_domain}"
        now = time.time()
        
        # Add new subdomain with current timestamp as score
        await self.redis.zadd(key, {subdomain: now})
        
        # Remove elements older than WINDOW_SECONDS
        cutoff = now - self.WINDOW_SECONDS
        await self.redis.zremrangebyscore(key, "-inf", cutoff)
        
        # Set expiry on the key to clean up if no activity
        await self.redis.expire(key, self.WINDOW_SECONDS + 10)
        
        # Count remaining unique subdomains
        count = await self.redis.zcard(key)
        return count
