from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # PostgreSQL
    postgres_user: str = "dnsadmin"
    postgres_password: str = "changeme"
    postgres_db: str = "dns_security"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # DNS
    upstream_dns: str = "1.1.1.1"
    dns_port: int = 53
    dns_listen_host: str = "0.0.0.0"

    # ML
    ml_threshold: float = 0.7
    ml_model_path: str = "app/ml/models/domain_classifier.joblib"

    # Feeds
    feed_sync_interval_minutes: int = 60

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

settings = Settings()
