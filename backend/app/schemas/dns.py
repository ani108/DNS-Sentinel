from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DNSQueryResponse(BaseModel):
    id: int
    queried_at: datetime
    domain: str
    query_type: str
    client_ip: Optional[str] = None
    verdict: str
    block_reason: Optional[str] = None
    ml_score: Optional[float] = None
    is_tunneling: bool = False
    response_time_ms: Optional[int] = None

    model_config = {"from_attributes": True}


class DomainAnalyzeRequest(BaseModel):
    domain: str


class FeatureBreakdown(BaseModel):
    domain_length: int
    sld_length: int
    subdomain_length: int
    num_labels: int
    shannon_entropy: float
    sld_entropy: float
    digit_ratio: float
    vowel_ratio: float
    consonant_max_run: int
    digit_max_run: int
    has_hyphen: bool
    special_char_count: int
    bigram_avg_freq: float
    trigram_avg_freq: float
    tld_risk_score: float
    is_punycode: bool


class DomainAnalyzeResponse(BaseModel):
    domain: str
    verdict: str
    ml_score: float
    features: FeatureBreakdown
    threat_intel_match: bool
    threat_intel_source: Optional[str] = None
    threat_category: Optional[str] = None
    explanation: str
