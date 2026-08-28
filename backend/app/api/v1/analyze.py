"""Domain analysis endpoint — interactive test widget backend."""
from fastapi import APIRouter, Depends
import redis.asyncio as aioredis

from app.api.deps import get_redis
from app.schemas.dns import DomainAnalyzeRequest, DomainAnalyzeResponse, FeatureBreakdown
from app.core.constants import REDIS_BLOCKLIST_KEY, REDIS_WHITELIST_KEY

router = APIRouter()


@router.post("/analyze", response_model=DomainAnalyzeResponse)
async def analyze_domain(
    request: DomainAnalyzeRequest,
    redis: aioredis.Redis = Depends(get_redis),
):
    """Analyze a domain and return ML prediction, features, and threat intel match.
    
    This powers the "Domain Tester" widget on the dashboard.
    """
    domain = request.domain.lower().strip().rstrip(".")
    
    # Check threat intelligence
    threat_match = await redis.sismember(REDIS_BLOCKLIST_KEY, domain)
    is_whitelisted = await redis.sismember(REDIS_WHITELIST_KEY, domain)
    
    # Extract features
    # TODO: Replace with actual ML feature extraction in Phase 3
    from app.ml.features import extract_features_dict
    features_dict = extract_features_dict(domain)
    features = FeatureBreakdown(**features_dict)
    
    # ML prediction
    # TODO: Replace with actual model inference in Phase 3
    ml_score = 0.0  # Placeholder
    try:
        from app.ml.classifier import DomainClassifier
        classifier = DomainClassifier.get_instance()
        if classifier:
            ml_score = classifier.predict_score(domain)
    except Exception:
        pass  # ML model not yet trained
    
    # Determine verdict
    if is_whitelisted:
        verdict = "ALLOWED"
        explanation = "Domain is whitelisted and will always be allowed."
    elif threat_match:
        verdict = "BLOCKED"
        explanation = "Domain found in threat intelligence feeds."
    elif ml_score > 0.7:
        verdict = "BLOCKED"
        explanation = f"ML classifier detected as malicious (score: {ml_score:.3f})."
    elif ml_score > 0.4:
        verdict = "SUSPICIOUS"
        explanation = f"ML classifier flagged as suspicious (score: {ml_score:.3f}). Monitoring."
    else:
        verdict = "ALLOWED"
        explanation = f"Domain appears clean (ML score: {ml_score:.3f})."
    
    return DomainAnalyzeResponse(
        domain=domain,
        verdict=verdict,
        ml_score=ml_score,
        features=features,
        threat_intel_match=threat_match,
        threat_intel_source="threat_feeds" if threat_match else None,
        threat_category="malware" if threat_match else None,
        explanation=explanation,
    )
