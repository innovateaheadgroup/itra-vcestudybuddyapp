from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/vce_prep_buddy"

    jwt_secret_key: str = "change-me-in-production"
    jwt_refresh_secret_key: str = "change-me-refresh-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:5173"

    llm_provider: str = "mock"
    llm_model: str = "mock-v1"
    buddy_scoring_refusal_patterns: str = (
        "write my sac answer,write my sat answer,do my sac,do my sat,complete my sac"
    )

    code_run_rate_limit_per_minute: int = 20
    code_run_timeout_seconds: int = 3
    max_upload_size_mb: int = Field(default=10, ge=1, le=100)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def buddy_refusal_patterns(self) -> list[str]:
        return [pattern.strip().lower() for pattern in self.buddy_scoring_refusal_patterns.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
