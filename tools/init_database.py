"""
Initialize the NDCA PostgreSQL schema.

This script creates tables defined by the SQLAlchemy ORM models.
"""

from ndca.database.base import Base
from ndca.database.engine import engine

# Import models so SQLAlchemy registers their tables.
from ndca.models import NetworkElement, Shelf  # noqa: F401


def main() -> None:
    """Create all registered NDCA database tables."""

    print("Initializing NDCA database schema...")

    Base.metadata.create_all(bind=engine)

    print("Database schema initialization completed.")

    print("\nRegistered tables:")
    for table_name in Base.metadata.tables:
        print(f" - {table_name}")


if __name__ == "__main__":
    main()