import pytest
from app.ml.features import extract_features_dict, shannon_entropy
from app.dns.server import build_sinkhole_response
from app.dns.upstream import UpstreamResolver
import dnslib

def test_shannon_entropy():
    # Test high entropy string
    high_ent = shannon_entropy("a8f93j2k1l0zxm")
    assert high_ent > 3.0

    # Test low entropy string
    low_ent = shannon_entropy("google")
    assert low_ent < 3.0

def test_extract_features_dict():
    domain = "test-domain123.com"
    features = extract_features_dict(domain)
    
    assert "length" in features
    assert features["length"] == len(domain)
    assert "entropy" in features
    assert features["num_digits"] == 3
    assert features["num_hyphens"] == 1
    assert features["num_dots"] == 1

def test_build_sinkhole_response():
    # Create a dummy request
    q = dnslib.DNSRecord.question("malicious.com")
    sinkhole_ip = "192.168.1.100"
    
    response = build_sinkhole_response(q, sinkhole_ip)
    
    assert response.header.qr == 1  # Response flag
    assert response.q.qname == "malicious.com"
    assert len(response.rr) == 1
    assert str(response.rr[0].rdata) == sinkhole_ip

@pytest.mark.asyncio
async def test_upstream_resolver():
    resolver = UpstreamResolver(servers=["8.8.8.8", "1.1.1.1"])
    assert resolver.servers == ["8.8.8.8", "1.1.1.1"]
    
    # We won't test actual network calls here to keep tests fast and reliable,
    # but we can test the instantiation and server selection logic if any.
