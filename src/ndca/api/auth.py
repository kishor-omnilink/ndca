"""
NDCA Nokia NSP Authentication Manager
"""

from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta

import httpx

from ndca.api.session import APISession
from ndca.core.config import settings
from ndca.core.exceptions import AuthenticationError
from ndca.core.logging import get_logger


class AuthenticationManager:
    """
    Handles authentication to Nokia NSP.

    Authentication Flow

        Basic Authentication
                │
                ▼
        OAuth2 Token Endpoint
                │
                ▼
        Access Token
                │
                ▼
        Cached APISession
    """

    def __init__(self) -> None:

        self.logger = get_logger(__name__)

        self._session: APISession | None = None

        self._client = httpx.Client(
            verify=settings.nsp_verify_ssl,
            timeout=settings.http_timeout,
        )

    def close(self) -> None:
        """
        Close HTTP client.
        """

        self._client.close()

    def invalidate(self) -> None:
        """
        Discard cached token.
        """

        self._session = None

    @property
    def session(self) -> APISession | None:
        return self._session

    def login(self) -> APISession:
        """
        Authenticate against Nokia NSP.

        Returns
        -------
        APISession
        """

        self.logger.info("Authenticating with Nokia NSP")

        credentials = (
            f"{settings.nsp_username}:{settings.nsp_password}"
        )

        encoded = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        url = (
            f"{settings.nsp_base_url}"
            f"{settings.nsp_token_endpoint}"
        )

        try:

            response = self._client.post(
                url,
                headers=headers,
                json={
                    "grant_type": "client_credentials"
                },
            )

            response.raise_for_status()

        except httpx.HTTPError as exc:

            self.logger.error(
                "Authentication failed",
                error=str(exc),
            )

            raise AuthenticationError(
                f"Authentication failed: {exc}"
            ) from exc

        payload = response.json()

        self._session = APISession(
            access_token=payload["access_token"],
            token_type=payload["token_type"],
            expires_at=(
                datetime.now(UTC)
                + timedelta(
                    seconds=payload["expires_in"]
                )
            ),
        )

        self.logger.info(
            "Authentication successful",
            expires_at=self._session.expires_at.isoformat(),
        )

        return self._session

    def get_session(self) -> APISession:
        """
        Return a valid session.
        """

        if self._session is None:
            return self.login()

        if self._session.expired:

            self.logger.info(
                "Access token expired. Re-authenticating."
            )

            return self.login()

        return self._session