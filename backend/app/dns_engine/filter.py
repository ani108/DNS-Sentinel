"""DNS query filtering logic — the brain of the DNS proxy."""
import json
import time
from typing import Optional, Tuple

import redis.asyncio as aioredis
from dnslib import DNSRecord, QTYPE

from app.config import settings
from app.core.constants import (
    REDIS_BLOCKLIST_KEY,
    REDIS_WHITELIST_KEY,
    REDIS_DNS_CACHE_PREFIX,
    REDIS_STATS_TOTAL,
    REDIS_STATS_BLOCKED,
    REDIS_LIVE_TRAFFIC_CHANNEL,
    VERDICT_ALLOWED,
    VERDICT_BLOCKED,
    VERDICT_SINKHOLED,
    REASON_THREAT_INTEL,
    REASON_ML_DETECTED,
    REASON_TUNNELING,
    MIN_CACHE_TTL,
    MAX_CACHE_TTL,
)
from app.core.logging import logger


class DNSFilter:
    """Filters DNS queries against blocklists, ML models, and tunneling detectors."""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def check_domain(
        self, domain: str, qtype_str: str, client_ip: str
    ) -> Tuple[str, Optional[str], Optional[float]]:
        """Check if a domain should be allowed or blocked.
        
        Returns:
            Tuple of (verdict, block_reason, ml_score)
            - verdict: ALLOWED, BLOCKED, or SINKHOLED
            - block_reason: None if allowed, else the reason string
            - ml_score: ML prediction score if ML was invoked, else None
        """
        domain_lower = domain.lower().rstrip(".")
        start_time = time.monotonic()

        # 1. WHITELIST CHECK — always allow whitelisted domains
        if await self.redis.sismember(REDIS_WHITELIST_KEY, domain_lower):
            logger.debug(f"Whitelisted: {domain_lower}")
            return VERDICT_ALLOWED, None, None

        # 2. BLOCKLIST CHECK — threat intelligence + custom blocklist
        if await self.redis.sismember(REDIS_BLOCKLIST_KEY, domain_lower):
            logger.info(f"Blocked (threat intel): {domain_lower}")
            return VERDICT_SINKHOLED, REASON_THREAT_INTEL, None

        # 3. ML CLASSIFIER — predict on unknown domains
        ml_score = await self._ml_predict(domain_lower)
        if ml_score is not None and ml_score > settings.ml_threshold:
            logger.info(f"Blocked (ML score={ml_score:.3f}): {domain_lower}")
            # Auto-add to blocklist for future fast-path
            await self.redis.sadd(REDIS_BLOCKLIST_KEY, domain_lower)
            return VERDICT_SINKHOLED, REASON_ML_DETECTED, ml_score

        # 4. TUNNELING CHECK
        is_tunneling = await self._check_tunneling(domain_lower, qtype_str, client_ip)
        if is_tunneling:
            logger.warning(f"Tunneling detected: {domain_lower} from {client_ip}")
            return VERDICT_SINKHOLED, REASON_TUNNELING, ml_score

        # 5. CLEAN — allow the query
        elapsed = (time.monotonic() - start_time) * 1000
        logger.debug(f"Allowed: {domain_lower} (check took {elapsed:.1f}ms)")
        return VERDICT_ALLOWED, None, ml_score

    async def get_cached_response(self, domain: str, qtype_str: str) -> Optional[bytes]:
        """Check Redis for a cached DNS response."""
        cache_key = f"{REDIS_DNS_CACHE_PREFIX}:{domain}:{qtype_str}"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.debug(f"Cache hit: {domain}/{qtype_str}")
            return cached.encode("latin-1") if isinstance(cached, str) else cached
        return None

    async def cache_response(
        self, domain: str, qtype_str: str, response_bytes: bytes, ttl: int = 300
    ) -> None:
        """Cache a DNS response in Redis."""
        cache_key = f"{REDIS_DNS_CACHE_PREFIX}:{domain}:{qtype_str}"
        ttl = max(MIN_CACHE_TTL, min(ttl, MAX_CACHE_TTL))
        # Store as latin-1 string since Redis decode_responses=True
        await self.redis.setex(cache_key, ttl, response_bytes.decode("latin-1"))

    async def publish_event(
        self,
        domain: str,
        qtype_str: str,
        client_ip: str,
        verdict: str,
        block_reason: Optional[str],
        ml_score: Optional[float],
        response_time_ms: int,
    ) -> None:
        """Publish a query event to Redis Pub/Sub for live dashboard."""
        event = {
            "domain": domain,
            "query_type": qtype_str,
            "client_ip": client_ip,
            "verdict": verdict,
            "block_reason": block_reason,
            "ml_score": ml_score,
            "response_time_ms": response_time_ms,
            "timestamp": time.time(),
        }
        await self.redis.publish(REDIS_LIVE_TRAFFIC_CHANNEL, json.dumps(event))

    async def increment_stats(self, verdict: str) -> None:
        """Increment query counters in Redis."""
        await self.redis.incr(REDIS_STATS_TOTAL)
        if verdict != VERDICT_ALLOWED:
            await self.redis.incr(REDIS_STATS_BLOCKED)
        
        # Hourly bucket for timeline charts
        from datetime import datetime, timezone
        hour_key = f"stats:hourly:{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H')}"
        field = "allowed" if verdict == VERDICT_ALLOWED else "blocked"
        await self.redis.hincrby(hour_key, field, 1)
        await self.redis.expire(hour_key, 48 * 3600)  # Keep 48 hours

    async def _ml_predict(self, domain: str) -> Optional[float]:
        """Run the ML classifier on a domain."""
        try:
            from app.ml.classifier import DomainClassifier
            classifier = DomainClassifier.get_instance()
            return classifier.predict_score(domain)
        except Exception as e:
            logger.error(f"ML error: {e}")
            return None

    async def _check_tunneling(
        self, domain: str, qtype_str: str, client_ip: str
    ) -> bool:
        """Check for DNS tunneling indicators."""
        try:
            from app.ml.tunneling import TunnelingDetector
            detector = TunnelingDetector(self.redis)
            return await detector.check(domain, qtype_str, client_ip)
        except Exception as e:
            logger.error(f"Tunneling error: {e}")
            return False
