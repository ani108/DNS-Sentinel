"""DNS Proxy Server — listens on UDP port 53 and processes queries."""
import asyncio
import time
from typing import Optional, Tuple

from dnslib import DNSRecord, QTYPE

from app.config import settings
from app.core.logging import logger
from app.core.redis import RedisManager
from app.dns_engine.filter import DNSFilter
from app.dns_engine.resolver import UpstreamResolver
from app.dns_engine.sinkhole import build_sinkhole_response


class DNSProxyProtocol(asyncio.DatagramProtocol):
    """Async UDP protocol handler for DNS queries.
    
    For each incoming DNS query:
    1. Parse the raw UDP packet
    2. Check whitelist/blocklist/ML/tunneling via DNSFilter
    3. Either sinkhole or forward to upstream
    4. Send response back to client
    5. Log the event via Redis Pub/Sub
    """

    def __init__(self):
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.filter: Optional[DNSFilter] = None
        self.resolver: Optional[UpstreamResolver] = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport
        redis_client = RedisManager.get_client()
        self.filter = DNSFilter(redis_client)
        self.resolver = UpstreamResolver()
        logger.info(
            f"DNS Proxy listening on "
            f"{settings.dns_listen_host}:{settings.dns_port}/UDP"
        )

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Called when a DNS query packet is received."""
        asyncio.create_task(self._handle_query(data, addr))

    def error_received(self, exc: Exception) -> None:
        logger.error(f"DNS Protocol error: {exc}")

    async def _handle_query(
        self, data: bytes, addr: Tuple[str, int]
    ) -> None:
        """Process a single DNS query."""
        start_time = time.monotonic()
        client_ip = addr[0]

        try:
            # 1. Parse the DNS packet
            request = DNSRecord.parse(data)
            domain = str(request.q.qname).rstrip(".")
            qtype_str = QTYPE[request.q.qtype]

            logger.debug(
                f"Query: {domain} ({qtype_str}) from {client_ip}"
            )

            # 2. Check cache first
            cached = await self.filter.get_cached_response(domain, qtype_str)
            if cached:
                self.transport.sendto(cached, addr)
                elapsed_ms = int((time.monotonic() - start_time) * 1000)
                await self.filter.publish_event(
                    domain, qtype_str, client_ip,
                    "ALLOWED", None, None, elapsed_ms,
                )
                await self.filter.increment_stats("ALLOWED")
                return

            # 3. Run the filter pipeline
            verdict, reason, ml_score = await self.filter.check_domain(
                domain, qtype_str, client_ip
            )

            # 4. Build response based on verdict
            if verdict in ("BLOCKED", "SINKHOLED"):
                response = build_sinkhole_response(request)
                response_bytes = response.pack()
            else:
                # Forward to upstream
                response_bytes = await self.resolver.resolve_raw(data)
                if response_bytes is None:
                    # Upstream failed — send SERVFAIL
                    response = request.reply()
                    response.header.rcode = 2  # SERVFAIL
                    response_bytes = response.pack()
                else:
                    # Cache the clean response
                    await self.filter.cache_response(
                        domain, qtype_str, response_bytes
                    )

            # 5. Send response to client
            self.transport.sendto(response_bytes, addr)

            # 6. Log and publish event
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            await self.filter.publish_event(
                domain, qtype_str, client_ip,
                verdict, reason, ml_score, elapsed_ms,
            )
            await self.filter.increment_stats(verdict)

            logger.info(
                f"{verdict}: {domain} ({qtype_str}) "
                f"from {client_ip} [{elapsed_ms}ms]"
                f"{f' reason={reason}' if reason else ''}"
            )

        except Exception as e:
            logger.error(
                f"Error handling query from {client_ip}: {e}",
                exc_info=True,
            )
            # Try to send SERVFAIL
            try:
                request = DNSRecord.parse(data)
                reply = request.reply()
                reply.header.rcode = 2  # SERVFAIL
                self.transport.sendto(reply.pack(), addr)
            except Exception:
                pass


async def start_dns_server() -> asyncio.DatagramTransport:
    """Start the DNS proxy server.
    
    Returns the transport so it can be closed on shutdown.
    """
    loop = asyncio.get_running_loop()
    
    transport, protocol = await loop.create_datagram_endpoint(
        DNSProxyProtocol,
        local_addr=(settings.dns_listen_host, settings.dns_port),
    )
    
    logger.info(
        f"DNS Proxy server started on "
        f"{settings.dns_listen_host}:{settings.dns_port}"
    )
    
    return transport
