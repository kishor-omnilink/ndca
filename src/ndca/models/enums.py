"""
Common enumerations used by NDCA ORM models.
"""

from enum import Enum


class SourceSystem(str, Enum):
    """Supported inventory source systems."""

    NFM_P = "NFM-P"
    NFM_T = "NFM-T"


class SyncStatus(str, Enum):
    """Inventory synchronization status."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AdminState(str, Enum):
    """Administrative state."""

    UP = "UP"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


class OperState(str, Enum):
    """Operational state."""

    UP = "UP"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"
