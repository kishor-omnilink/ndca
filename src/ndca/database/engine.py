"""
Database engine configuration.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ndca.core.config import settings


def build_database_url() -> str:
    """Build SQLAlchemy database URL from application settings."""

    return (
        f"postgresql+psycopg://"
        f"{settings.db_user}:"
        f"{settings.db_password}@"
        f"{settings.db_host}:"
        f"{settings.db_port}/"
        f"{settings.db_name}"
    )


DATABASE_URL = build_database_url()

engine: Engine = create_engine(
    DATABASE_URL,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=settings.db_pool_pre_ping,
    pool_recycle=settings.db_pool_recycle,
    future=True,
)


def database_health_check() -> bool:
    """Return True if the database connection is healthy."""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
