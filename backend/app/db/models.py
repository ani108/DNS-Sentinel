from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, JSON, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.session import Base


class DNSQuery(Base):
    __tablename__ = "dns_queries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    queried_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    query_type: Mapped[str] = mapped_column(String(10), nullable=False, default="A")
    client_ip: Mapped[Optional[str]] = mapped_column(String(45))
    verdict: Mapped[str] = mapped_column(String(20), nullable=False)  # ALLOWED, BLOCKED, SINKHOLED
    block_reason: Mapped[Optional[str]] = mapped_column(String(50))
    ml_score: Mapped[Optional[float]] = mapped_column(Float)
    is_tunneling: Mapped[bool] = mapped_column(Boolean, default=False)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (
        Index("idx_dns_queries_domain_queried", "domain", "queried_at"),
    )


class ThreatEntry(Base):
    __tablename__ = "threat_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # urlhaus, phishtank, manual, ml
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # phishing, malware, c2, dga, adware
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, expired, false_positive
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Whitelist(Base):
    __tablename__ = "whitelist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    added_by: Mapped[str] = mapped_column(String(255), default="admin")
    reason: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CustomBlocklist(Base):
    __tablename__ = "custom_blocklist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    added_by: Mapped[str] = mapped_column(String(255), default="admin")
    reason: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FeedSyncLog(Base):
    __tablename__ = "feed_sync_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    feed_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, failed, partial
    domains_added: Mapped[int] = mapped_column(Integer, default=0)
    domains_removed: Mapped[int] = mapped_column(Integer, default=0)
    total_domains: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    prediction: Mapped[str] = mapped_column(String(20), nullable=False)  # malicious, benign
    features: Mapped[Optional[dict]] = mapped_column(JSON)
    model_version: Mapped[Optional[str]] = mapped_column(String(30))
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TunnelIncident(Base):
    __tablename__ = "tunnel_incidents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    base_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    client_ip: Mapped[Optional[str]] = mapped_column(String(45))
    unique_subdomains: Mapped[int] = mapped_column(Integer, default=0)
    avg_entropy: Mapped[float] = mapped_column(Float, default=0.0)
    avg_subdomain_length: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, resolved, false_positive
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
