"""
NDCA Configuration Management

Application configuration using Pydantic Settings.
"""

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

    # ==========================================================================
    # Application
    # ==========================================================================

    app_name: str = "NDCA"
    app_version: str = "0.1.0-dev"
    app_env: str = "development"

    # ==========================================================================
    # Logging
    # ==========================================================================

    log_level: str = "INFO"
    log_format: str = "json"

    # ==========================================================================
    # Database
    # ==========================================================================

    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = "ndca"
    db_user: str = "ndca"
    db_password: str = "change_me"

    # ==========================================================================
    # Nokia NSP Configuration
    # ==========================================================================

    nsp_base_url: str = Field(
        default="https://127.0.0.1",
        description="Nokia NSP Base URL",
    )

    nsp_username: str = Field(
        default="",
        description="Nokia NSP Username",
    )

    nsp_password: str = Field(
        default="",
        description="Nokia NSP Password",
    )

    nsp_verify_ssl: bool = Field(
        default=False,
        description="Verify Nokia NSP SSL Certificate",
    )

    nsp_token_endpoint: str = Field(
        default="/rest-gateway/rest/api/v1/auth/token",
        description="OAuth2 Token Endpoint",
    )

    api_base_path: str = Field(
        default="/restconf/data",
        description="NSP RESTCONF API Base Path",
    )

    # -------------------------------------------------------------------------
    # Nokia NSP RESTCONF Endpoints
    # -------------------------------------------------------------------------

    nsp_network_element_endpoint: str = (
        "/restconf/data/nsp-equipment:network/network-element"
    )
    
    # ==========================================================================
    # Legacy NFM-P (Reserved)
    # ==========================================================================

    nfmp_url: str = ""
    nfmp_username: str = ""
    nfmp_password: str = ""
    nfmp_verify_ssl: bool = False

    # ==========================================================================
    # NFM-T (Reserved)
    # ==========================================================================

    nfmt_url: str = ""
    nfmt_username: str = ""
    nfmt_password: str = ""
    nfmt_verify_ssl: bool = False

    # ==========================================================================
    # Collection
    # ==========================================================================

    collection_interval: int = 900
    http_timeout: int = 60
    max_retries: int = 3

    # ==========================================================================
    # TimescaleDB
    # ==========================================================================

    enable_timescale: bool = True

    # ==========================================================================
    # Reports
    # ==========================================================================

    report_timezone: str = "Asia/Kolkata"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()