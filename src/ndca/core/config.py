from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """NDCA application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NDCA"
    app_version: str = "0.1.0-dev"
    app_env: str = "development"

    log_level: str = "INFO"
    log_format: str = "json"

    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = "ndca"
    db_user: str = "ndca"
    db_password: str = "change_me"

    nfmp_url: str = ""
    nfmp_username: str = ""
    nfmp_password: str = ""
    nfmp_verify_ssl: bool = False

    nfmt_url: str = ""
    nfmt_username: str = ""
    nfmt_password: str = ""
    nfmt_verify_ssl: bool = False

    collection_interval: int = 900
    http_timeout: int = 60
    max_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
