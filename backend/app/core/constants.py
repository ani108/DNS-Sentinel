"""Application-wide constants."""

# Redis key patterns
REDIS_BLOCKLIST_KEY = "blocklist"
REDIS_WHITELIST_KEY = "whitelist"
REDIS_DNS_CACHE_PREFIX = "dns:cache"
REDIS_STATS_TOTAL = "stats:queries:total"
REDIS_STATS_BLOCKED = "stats:queries:blocked"
REDIS_STATS_HOURLY_PREFIX = "stats:hourly"
REDIS_TUNNEL_WINDOW_PREFIX = "tunnel:window"
REDIS_LIVE_TRAFFIC_CHANNEL = "channel:live_traffic"

# DNS
SINKHOLE_IPV4 = "0.0.0.0"
SINKHOLE_IPV6 = "::"
DEFAULT_TTL = 60  # seconds for sinkhole responses
MIN_CACHE_TTL = 60
MAX_CACHE_TTL = 3600

# Verdicts
VERDICT_ALLOWED = "ALLOWED"
VERDICT_BLOCKED = "BLOCKED"
VERDICT_SINKHOLED = "SINKHOLED"

# Block reasons
REASON_THREAT_INTEL = "threat_intel"
REASON_ML_DETECTED = "ml_detected"
REASON_TUNNELING = "tunneling"
REASON_MANUAL_BLOCK = "manual_block"

# ML
ML_SUSPICIOUS_LOW = 0.4
ML_SUSPICIOUS_HIGH = 0.7

# Threat categories
CATEGORY_PHISHING = "phishing"
CATEGORY_MALWARE = "malware"
CATEGORY_C2 = "c2"
CATEGORY_DGA = "dga"
CATEGORY_ADWARE = "adware"

# High-risk TLDs
HIGH_RISK_TLDS = {
    "tk", "ml", "ga", "cf", "gq",  # Freenom TLDs
    "top", "xyz", "buzz", "club", "work",
    "fit", "life", "loan", "racing", "win",
    "bid", "stream", "click", "download",
}
