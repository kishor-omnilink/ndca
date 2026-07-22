"""
Custom exceptions used throughout NDCA.
"""


class NDCAError(Exception):
    """Base exception for all NDCA errors."""


class ConfigurationError(NDCAError):
    """Raised when configuration is invalid."""


class DatabaseError(NDCAError):
    """Raised for database-related errors."""


class CollectorError(NDCAError):
    """Raised for collector failures."""


class AuthenticationError(NDCAError):
    """Raised for authentication failures."""


class APIError(NDCAError):
    """Raised for REST API failures."""
