"""
Repository exceptions.

All persistence layer exceptions should derive from RepositoryError.
"""

from __future__ import annotations


class RepositoryError(Exception):
    """
    Base class for all repository exceptions.
    """


class RepositoryNotFoundError(RepositoryError):
    """
    Requested entity was not found.
    """


class RepositoryIntegrityError(RepositoryError):
    """
    Database integrity constraint violation.
    """


class RepositoryConnectionError(RepositoryError):
    """
    Database connectivity problem.
    """


class RepositoryQueryError(RepositoryError):
    """
    Query execution failed.
    """