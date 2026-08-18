# SPDX-License-Identifier: MIT
"""Confluent Kafka client adapter for SYNC-012-B.3 BGP telemetry."""

from __future__ import annotations

from typing import Any

from confluent_kafka import Consumer, KafkaError, Message

from ndca.collectors.performance.kafka_bgp_performance_consumer import (
    KafkaMessageSource,
    KafkaRecord,
)
from ndca.core.config import settings
from ndca.core.logging import get_logger


class ConfluentKafkaSource(KafkaMessageSource):
    """Confluent Kafka client adapter implementing KafkaMessageSource protocol."""

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        topic: str | None = None,
        group_id: str | None = None,
        auto_offset_reset: str = "latest",
        poll_timeout: float = 1.0,
        security_protocol: str | None = None,
        ssl_ca_location: str | None = None,
        ssl_certificate_location: str | None = None,
        ssl_key_location: str | None = None,
        ssl_key_password: str | None = None,
    ) -> None:
        """Initialize Confluent Kafka consumer.

        Args:
            bootstrap_servers: Comma-separated Kafka bootstrap servers
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            auto_offset_reset: Offset reset policy ('latest', 'earliest', etc.)
            poll_timeout: Poll timeout in seconds
            security_protocol: Security protocol (SASL_SSL, SSL, etc.)
            ssl_ca_location: Path to SSL CA certificate
            ssl_certificate_location: Path to SSL client certificate
            ssl_key_location: Path to SSL client key
            ssl_key_password: Password for encrypted SSL key
        """
        self.logger = get_logger(__name__)
        self.topic = topic or settings.kafka_topic
        self.poll_timeout = poll_timeout

        if not self.topic:
            raise ValueError("Kafka topic must be provided")

        # Build consumer configuration
        config: dict[str, Any] = {
            "bootstrap.servers": bootstrap_servers or settings.kafka_bootstrap_servers,
            "group.id": group_id or settings.kafka_group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": True,
        }

        # Configure security if specified
        if security_protocol or settings.kafka_security_protocol:
            protocol = security_protocol or settings.kafka_security_protocol
            config["security.protocol"] = protocol

            if ssl_ca_location or settings.kafka_ssl_ca_location:
                config["ssl.ca.location"] = ssl_ca_location or settings.kafka_ssl_ca_location

            if ssl_certificate_location or settings.kafka_ssl_certificate_location:
                config["ssl.certificate.location"] = (
                    ssl_certificate_location or settings.kafka_ssl_certificate_location
                )

            if ssl_key_location or settings.kafka_ssl_key_location:
                config["ssl.key.location"] = ssl_key_location or settings.kafka_ssl_key_location

            if ssl_key_password or settings.kafka_ssl_key_password:
                config["ssl.key.password"] = ssl_key_password or settings.kafka_ssl_key_password

        self.logger.info(
            "Creating Confluent Kafka consumer",
            bootstrap_servers=config.get("bootstrap.servers"),
            topic=self.topic,
            group_id=config.get("group.id"),
        )

        self._consumer = Consumer(config)
        self._consumer.subscribe([self.topic])
        self._closed = False

    def poll(self, timeout: float) -> KafkaRecord | None:
        """Poll one message from Kafka."""
        if self._closed:
            return None

        try:
            msg: Message | None = self._consumer.poll(timeout=timeout)
            if msg is None:
                return None

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    return None
                self.logger.error("Kafka consumer error", error=msg.error())
                return None

            return KafkaRecord(
                value=msg.value() or b"",
                topic=msg.topic(),
                partition=msg.partition(),
                offset=msg.offset(),
                key=msg.key(),
            )
        except Exception as exc:
            self.logger.error("Error polling Kafka", error=str(exc))
            return None

    def close(self) -> None:
        """Close the Kafka consumer."""
        if not self._closed:
            self._closed = True
            try:
                self._consumer.close()
                self.logger.info("Confluent Kafka consumer closed")
            except Exception as exc:
                self.logger.error("Error closing Kafka consumer", error=str(exc))
