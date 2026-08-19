# SPDX-License-Identifier: MIT
"""Kafka transport boundary for SYNC-012-B.3 BGP telemetry."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from ndca.mappers.bgp_kafka_mapper import BGPKafkaPayloadError


@dataclass(slots=True, frozen=True)
class KafkaRecord:
    """Normalized Kafka record supplied to the BGP parser."""

    value: bytes | str | dict[str, Any]
    topic: str
    partition: int
    offset: int
    key: bytes | str | None = None


class KafkaMessageSource(Protocol):
    """Protocol implemented by a concrete Kafka client adapter."""

    def poll(self, timeout: float) -> KafkaRecord | None:
        """Return one record or None when no record is available."""

    def close(self) -> None:
        """Release Kafka client resources."""


class KafkaBGPPerformanceConsumer:
    """Dependency-neutral consumer boundary with an injectable source."""

    def __init__(
        self,
        source: KafkaMessageSource,
        handler: Callable[[KafkaRecord], Any],
    ) -> None:
        self._source = source
        self._handler = handler

    def consume_once(self, timeout: float = 1.0) -> Any | None:
        """Poll one record and pass it to the handler."""
        record = self._source.poll(timeout)
        if record is None:
            return None

        return self._handler(record)

    def consume(
        self,
        *,
        timeout: float = 1.0,
        max_messages: int | None = None,
    ) -> int:
        """Consume records until the limit or source exhaustion.

        Malformed BGP payloads are isolated to the individual record.
        A BGPKafkaPayloadError does not terminate the consumer loop.
        Successfully handled records are counted as processed.
        """
        processed = 0

        while max_messages is None or processed < max_messages:
            record = self._source.poll(timeout)

            if record is None:
                break

            try:
                self._handler(record)
            except BGPKafkaPayloadError:
                continue

            processed += 1

        return processed

    def close(self) -> None:
        """Close the injected source."""
        self._source.close()