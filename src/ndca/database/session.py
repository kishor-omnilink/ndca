"""
Database session management.
"""

from sqlalchemy.orm import Session, sessionmaker

from ndca.database.engine import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_session() -> Session:
    """
    Return a new SQLAlchemy session.

    Caller is responsible for closing it.
    """
    return SessionLocal()
