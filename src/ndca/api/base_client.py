"""
NDCA Nokia NSP Base REST Client
"""

from __future__ import annotations

from typing import Any, Callable

import httpx

from ndca.api.auth import AuthenticationManager
from ndca.core.config import settings
from ndca.core.exceptions import APIError
from ndca.core.logging import get_logger


class BaseApiClient:
    """Base client for all Nokia NSP REST API calls."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self._auth = AuthenticationManager()
        self._client = httpx.Client(
            verify=settings.nsp_verify_ssl,
            timeout=settings.http_timeout,
        )

    def close(self) -> None:
        """Close HTTP session."""
        self._client.close()
        self._auth.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an authenticated request with transient-failure recovery."""
        url = f"{settings.nsp_base_url}{path}"
        max_retries = max(0, int(settings.max_retries))
        transient_attempt = 0
        auth_retry = False

        while True:
            session = self._auth.get_session()
            headers = {
                "Authorization": session.authorization_header,
                "Accept": "application/json",
            }
            if method == "POST":
                headers["Content-Type"] = "application/json"

            try:
                response = self._client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=payload,
                )

                if response.status_code == 401 and not auth_retry:
                    self.logger.warning(
                        "NSP authentication rejected; refreshing token",
                        url=url,
                    )
                    self._auth.invalidate()
                    auth_retry = True
                    continue

                if response.status_code == 401:
                    response.raise_for_status()

                if response.status_code == 429 or 500 <= response.status_code <= 599:
                    if transient_attempt < max_retries:
                        transient_attempt += 1
                        self.logger.warning(
                            "Transient NSP HTTP failure; retrying",
                            method=method,
                            status=response.status_code,
                            attempt=transient_attempt,
                            max_retries=max_retries,
                            url=url,
                        )
                        continue

                response.raise_for_status()

                try:
                    result = response.json()
                except ValueError as exc:
                    raise APIError(f"Invalid JSON response from NSP: {url}") from exc

                if not isinstance(result, dict):
                    raise APIError(f"NSP response must be a JSON object: {url}")

                return result

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
                if transient_attempt < max_retries:
                    transient_attempt += 1
                    self.logger.warning(
                        "Transient NSP HTTP error; retrying",
                        method=method,
                        attempt=transient_attempt,
                        max_retries=max_retries,
                        error=str(exc),
                        url=url,
                    )
                    continue

                self.logger.error("HTTP Error", error=str(exc), url=url)
                raise APIError(str(exc)) from exc

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute authenticated HTTP GET."""
        self.logger.info("HTTP GET", url=f"{settings.nsp_base_url}{path}")
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute authenticated HTTP POST."""
        self.logger.info("HTTP POST", url=f"{settings.nsp_base_url}{path}")
        return self._request("POST", path, payload=payload)
