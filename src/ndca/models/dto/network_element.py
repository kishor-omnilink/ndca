"""
Network Element DTO.

Represents the Network Element fields collected from Nokia NSP
before conversion into the SQLAlchemy NetworkElement model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class NetworkElementDTO:
    """
    Data transfer object for a Nokia NSP Network Element.

    The DTO represents data received from NSP and does not contain
    SQLAlchemy-specific state.
    """

    ne_id: str
    ne_name: str

    component_id: str

    ip_address: str | None = None
    system_type: str | None = None
    software_version: str | None = None
    vendor: str | None = None

    admin_state: str | None = None
    oper_state: str | None = None
    availability_state: list[Any] | None = None
    description: str | None = None
    source_type: str | None = None