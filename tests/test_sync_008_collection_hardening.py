"""SYNC-008 tests for NSP collection hardening."""

from datetime import UTC, datetime, timedelta
from unittest import TestCase
from unittest.mock import MagicMock, patch

import httpx

from ndca.api.auth import AuthenticationManager
from ndca.api.base_client import BaseApiClient
from ndca.api.session import APISession
from ndca.collectors.inventory.network_element_collector import NetworkElementCollector
from ndca.core.exceptions import APIError, AuthenticationError, CollectorError


class TestAuthenticationHardening(TestCase):
    def test_login_rejects_missing_token_fields(self) -> None:
        manager = AuthenticationManager.__new__(AuthenticationManager)
        manager.logger = MagicMock()
        manager._session = None
        manager._client = MagicMock()

        response = MagicMock()
        response.json.return_value = {"token_type": "Bearer", "expires_in": 60}
        response.raise_for_status.return_value = None
        manager._client.post.return_value = response

        with self.assertRaises(AuthenticationError):
            with patch("ndca.api.auth.settings") as settings_mock:
                settings_mock.nsp_username = "user"
                settings_mock.nsp_password = "password"
                settings_mock.nsp_base_url = "https://nsp"
                settings_mock.nsp_token_endpoint = "/token"
                manager.login()

    def test_login_rejects_invalid_expiry(self) -> None:
        manager = AuthenticationManager.__new__(AuthenticationManager)
        manager.logger = MagicMock()
        manager._session = None
        manager._client = MagicMock()

        response = MagicMock()
        response.json.return_value = {
            "access_token": "token",
            "token_type": "Bearer",
            "expires_in": "invalid",
        }
        response.raise_for_status.return_value = None
        manager._client.post.return_value = response

        with self.assertRaises(AuthenticationError):
            with patch("ndca.api.auth.settings") as settings_mock:
                settings_mock.nsp_username = "user"
                settings_mock.nsp_password = "password"
                settings_mock.nsp_base_url = "https://nsp"
                settings_mock.nsp_token_endpoint = "/token"
                manager.login()


class TestBaseApiClientHardening(TestCase):
    def make_client(self) -> BaseApiClient:
        client = BaseApiClient.__new__(BaseApiClient)
        client.logger = MagicMock()
        client._auth = MagicMock()
        client._client = MagicMock()
        client._auth.get_session.return_value = APISession(
            access_token="token",
            token_type="Bearer",
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
        )
        return client

    @staticmethod
    def response(status: int, payload: object = None) -> MagicMock:
        response = MagicMock()
        response.status_code = status
        response.json.return_value = payload
        if status >= 400:
            request = httpx.Request("GET", "https://nsp/test")
            response.request = request
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                f"HTTP {status}", request=request, response=response
            )
        else:
            response.raise_for_status.return_value = None
        return response

    def test_get_retries_transient_server_error(self) -> None:
        client = self.make_client()
        client._client.request.side_effect = [
            self.response(503, {"error": "temporary"}),
            self.response(200, {"items": []}),
        ]

        with patch("ndca.api.base_client.settings") as settings_mock:
            settings_mock.nsp_base_url = "https://nsp"
            settings_mock.max_retries = 1
            result = client.get("/inventory")

        self.assertEqual(result, {"items": []})
        self.assertEqual(client._client.request.call_count, 2)

    def test_get_reauthenticates_once_after_401(self) -> None:
        client = self.make_client()
        first = client._auth.get_session.return_value
        second = APISession(
            access_token="new-token",
            token_type="Bearer",
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
        )
        client._auth.get_session.side_effect = [first, second]
        client._client.request.side_effect = [
            self.response(401, {"error": "unauthorized"}),
            self.response(200, {"items": []}),
        ]

        with patch("ndca.api.base_client.settings") as settings_mock:
            settings_mock.nsp_base_url = "https://nsp"
            settings_mock.max_retries = 0
            result = client.get("/inventory")

        self.assertEqual(result, {"items": []})
        client._auth.invalidate.assert_called_once_with()
        self.assertEqual(client._client.request.call_count, 2)

    def test_get_raises_api_error_after_retry_exhaustion(self) -> None:
        client = self.make_client()
        client._client.request.side_effect = [
            self.response(500, {"error": "down"}),
            self.response(500, {"error": "still down"}),
        ]

        with self.assertRaises(APIError):
            with patch("ndca.api.base_client.settings") as settings_mock:
                settings_mock.nsp_base_url = "https://nsp"
                settings_mock.max_retries = 1
                client.get("/inventory")

        self.assertEqual(client._client.request.call_count, 2)

    def test_get_retries_transport_error(self) -> None:
        client = self.make_client()
        client._client.request.side_effect = [
            httpx.ConnectError("connection reset"),
            self.response(200, {"items": []}),
        ]

        with patch("ndca.api.base_client.settings") as settings_mock:
            settings_mock.nsp_base_url = "https://nsp"
            settings_mock.max_retries = 1
            result = client.get("/inventory")

        self.assertEqual(result, {"items": []})
        self.assertEqual(client._client.request.call_count, 2)

    def test_get_rejects_non_object_json(self) -> None:
        client = self.make_client()
        client._client.request.return_value = self.response(200, [])

        with self.assertRaises(APIError):
            with patch("ndca.api.base_client.settings") as settings_mock:
                settings_mock.nsp_base_url = "https://nsp"
                settings_mock.max_retries = 0
                client.get("/inventory")


class TestNetworkElementCollectorHardening(TestCase):
    def test_empty_object_is_valid_inventory(self) -> None:
        collector = NetworkElementCollector.__new__(NetworkElementCollector)
        collector.logger = MagicMock()
        collector.client = MagicMock()
        collector.client.get.return_value = {}

        with patch("ndca.collectors.inventory.network_element_collector.settings") as settings_mock:
            settings_mock.nsp_network_element_endpoint = "/inventory"
            self.assertEqual(collector.collect(), {})

    def test_non_object_response_is_rejected(self) -> None:
        collector = NetworkElementCollector.__new__(NetworkElementCollector)
        collector.logger = MagicMock()
        collector.client = MagicMock()
        collector.client.get.return_value = []

        with patch("ndca.collectors.inventory.network_element_collector.settings") as settings_mock:
            settings_mock.nsp_network_element_endpoint = "/inventory"
            with self.assertRaises(CollectorError):
                collector.collect()

    def test_api_failure_is_wrapped_as_collector_error(self) -> None:
        collector = NetworkElementCollector.__new__(NetworkElementCollector)
        collector.logger = MagicMock()
        collector.client = MagicMock()
        collector.client.get.side_effect = APIError("HTTP 503")

        with patch("ndca.collectors.inventory.network_element_collector.settings") as settings_mock:
            settings_mock.nsp_network_element_endpoint = "/inventory"
            with self.assertRaises(CollectorError):
                collector.collect()


if __name__ == "__main__":
    import unittest

    unittest.main()
