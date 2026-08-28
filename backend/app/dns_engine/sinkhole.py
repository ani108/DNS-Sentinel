"""Sinkhole response builder for blocked DNS queries."""
import dnslib
from dnslib import DNSRecord, RR, QTYPE, A, AAAA
from app.core.constants import SINKHOLE_IPV4, SINKHOLE_IPV6, DEFAULT_TTL


def build_sinkhole_response(request: DNSRecord) -> DNSRecord:
    """Build a sinkhole response for a blocked DNS query.
    
    Returns 0.0.0.0 for A records, :: for AAAA records,
    and NXDOMAIN for all other record types.
    """
    qname = request.q.qname
    qtype = request.q.qtype
    
    reply = request.reply()
    
    if qtype == QTYPE.A:
        reply.add_answer(RR(
            rname=qname,
            rtype=QTYPE.A,
            rclass=1,
            ttl=DEFAULT_TTL,
            rdata=A(SINKHOLE_IPV4),
        ))
    elif qtype == QTYPE.AAAA:
        reply.add_answer(RR(
            rname=qname,
            rtype=QTYPE.AAAA,
            rclass=1,
            ttl=DEFAULT_TTL,
            rdata=AAAA(SINKHOLE_IPV6),
        ))
    else:
        # Return NXDOMAIN for non-A/AAAA queries
        reply.header.rcode = dnslib.RCODE.NXDOMAIN
    
    return reply
