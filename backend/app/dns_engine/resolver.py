"""Upstream DNS resolver using dnspython."""
import asyncio
import dns.asyncresolver
import dns.message
import dns.rdatatype
from typing import Optional
from app.config import settings
from app.core.logging import logger


class UpstreamResolver:
    """Forwards DNS queries to upstream resolvers (e.g., 1.1.1.1, 8.8.8.8)."""

    def __init__(self, upstream_dns: Optional[str] = None):
        self.upstream = upstream_dns or settings.upstream_dns
        self._resolver = dns.asyncresolver.Resolver()
        self._resolver.nameservers = [self.upstream]
        self._resolver.lifetime = 5.0  # 5 second timeout

    async def resolve_raw(self, raw_query: bytes) -> Optional[bytes]:
        """Forward a raw DNS query packet to upstream and return raw response.
        
        Uses UDP with fallback to TCP if response is truncated.
        """
        try:
            # Parse the incoming query using dnspython
            query_msg = dns.message.from_wire(raw_query)
            
            # Forward via UDP
            response = await asyncio.wait_for(
                self._udp_query(query_msg),
                timeout=5.0,
            )
            
            if response:
                return response.to_wire()
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"Upstream DNS timeout for query")
            return None
        except Exception as e:
            logger.error(f"Upstream resolution error: {e}")
            return None

    async def _udp_query(self, query: dns.message.Message) -> Optional[dns.message.Message]:
        """Send DNS query via UDP to upstream."""
        try:
            response = await dns.asyncquery.udp(
                query,
                self.upstream,
                timeout=5.0,
            )
            # If truncated, retry with TCP
            if response.flags & dns.flags.TC:
                logger.debug("Response truncated, retrying with TCP")
                response = await dns.asyncquery.tcp(
                    query,
                    self.upstream,
                    timeout=5.0,
                )
            return response
        except Exception as e:
            logger.error(f"UDP query failed: {e}")
            return None


# Import dns.asyncquery for the actual query functions
import dns.asyncquery
