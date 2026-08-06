"""
NDCA Nokia NSP Base REST Client
"""

from __future__ import annotations

from typing import Any

import httpx

from ndca.api.auth import AuthenticationManager
from ndca.core.config import settings
from ndca.core.exceptions import APIError
from ndca.core.logging import get_logger


class BaseApiClient:
    """
    Base client for all Nokia NSP REST API calls.
    """

    def __init__(self) -> None:

        self.logger = get_logger(__name__)

        self._auth = AuthenticationManager()

        self._client = httpx.Client(
            verify=settings.nsp_verify_ssl,
            timeout=settings.http_timeout,
        )

    def close(self) -> None:
        """
        Close HTTP session.
        """

        self._client.close()

        self._auth.close()

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute authenticated HTTP GET.
        """

        session = self._auth.get_session()

        headers = {
            "Authorization": session.authorization_header,
            "Accept": "application/json",
        }

        url = f"{settings.nsp_base_url}{path}"

        self.logger.info(
            "HTTP GET",
            url=url,
        )

        try:

            response = self._client.get(
                url,
                headers=headers,
                params=params,
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:

            self.logger.error(
                "HTTP Status Error",
                status=exc.response.status_code,
                url=url,
            )

            raise APIError(
                f"HTTP {exc.response.status_code}: {url}"
            ) from exc

        except httpx.HTTPError as exc:

            self.logger.error(
                "HTTP Error",
                error=str(exc),
            )

            raise APIError(
                str(exc)
            ) from exc

    def post(
        self,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute authenticated HTTP POST.
        """

        session = self._auth.get_session()

        headers = {
            "Authorization": session.authorization_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        url = f"{settings.nsp_base_url}{path}"

        self.logger.info(
            "HTTP POST",
            url=url,
        )

        try:

            response = self._client.post(
                url,
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:

            self.logger.error(
                "HTTP Status Error",
                status=exc.response.status_code,
                url=url,
            )

            raise APIError(
                f"HTTP {exc.response.status_code}: {url}"
            ) from exc

        except httpx.HTTPError as exc:

            self.logger.error(
                "HTTP Error",
                error=str(exc),
            )

            raise APIError(
                str(exc)
            ) from exc