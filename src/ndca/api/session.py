"""
Authenticated Nokia NSP API session.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime


@dataclass(slots=True)
class APISession:
    """
    Represents an authenticated Nokia NSP API session.
    """

    access_token: str
    token_type: str
    expires_at: datetime

    @property
    def authorization_header(self) -> str:
        """
        Return the HTTP Authorization header.
        """

        return f"{self.token_type} {self.access_token}"

    @property
    def expired(self) -> bool:
        """
        True when the token has expired.
        """

        return datetime.now(UTC) >= self.expires_at