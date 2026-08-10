"""
NDCA Nokia NSP Authentication Manager
"""

from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from ndca.api.session import APISession
from ndca.core.config import settings
from ndca.core.exceptions import AuthenticationError
from ndca.core.logging import get_logger


class AuthenticationManager