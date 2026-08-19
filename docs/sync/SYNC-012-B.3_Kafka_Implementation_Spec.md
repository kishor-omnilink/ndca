# SYNC-012-B.3 — Kafka BGP Performance Collector

## Status

IMPLEMENTATION READY

This implementation uses the already-enabled NSP telemetry subscription and its verified Kafka notification topic. Do not return to the completed RESTCONF/OpenConfig investigation.

## Verified runtime source

- Kafka bootstrap: `10.110.11.60:9192`
- Kafka topic: `ns-eg-1716a23b-7c94-4393-831d-cd97c20c1e70`
- Kafka CLI: `4.3.1`
- Topic is readable from the NDCA host.
- Existing NSP subscription: `service_vprn_bgp_neighbor_statistics`
- Telemetry type: `telemetry:/base/sros-service-vprn/service_vprn_bgp_neighbor_statistics`
- Subscription: enabled
- DB collection: enabled
- Notification: enabled
- Existing subscription period: 600 seconds

## Verified field allowlist

Identity:
- `neId`
- `system-id`
- `objectId`
- `kpiType`

Session/peer:
- `peer-as`
- `peer-port`
- `local-port`
- `session-state`
- `last-state`
- `last-event`
- `last-error`
- `negotiated-family`
- `operational-local-address`
- `operational-remote-address`
- `peer-identifier`
- `established-transitions`
- `last-established-time`
- `number-of-update-flaps`
- `hold-time-interval`
- `keep-alive-interval`

Prefixes:
- `family-prefix_ipv4_received`
- `family-prefix_ipv4_active`
- `family-prefix_ipv4_sent`
- `family-prefix_ipv4_backup`
- `family-prefix_ipv4_rejected`
- `family-prefix_ipv4_suppressed`
- `family-prefix_ipv6_received`
- `family-prefix_ipv6_active`
- `family-prefix_ipv6_sent`
- `family-prefix_ipv6_backup`
- `family-prefix_ipv6_rejected`
- `family-prefix_ipv6_suppressed`

Traffic:
- `received_messages`
- `received_updates`
- `received_octets`
- `received_route-refresh`
- `sent_messages`
- `sent_updates`
- `sent_octets`
- `sent_route-refresh`

Additional verified fields:
- `oper-tcp-mss`
- `rcvd-tcp-mss`
- `time-captured`
- `time-captured-periodic`

Periodic variants are accepted where present, but only for verified base fields.

## Payload rule

Preserve the actual Kafka payload as `raw_payload`.

The parser may remove JSON/SSE transport framing and extract the verified:
`ietf-restconf:notification` → `nsp-kpi:real_time_kpi-event` envelope.

Do not invent a Nokia payload schema.

Supported transport forms:
1. JSON Kafka value.
2. SSE-framed value containing `data:<JSON>`.
3. One SSE record per Kafka value.

Unknown fields remain in `raw_payload` and are not silently converted into metrics.

## Object identity

For the observed object ID form:

`/state/service/vprn[service-name='<SERVICE>']/bgp/neighbor[ip-address='<PEER-IP>']`

extract service name and peer IP, while always preserving the original object ID.

## Architecture

```text
NSP telemetry subscription
        |
        v
Kafka topic
        |
        v
Kafka transport adapter
        |
        v
BGP telemetry parser
        |
        v
NDCA PerformanceRecord / existing performance pipeline
        |
        v
PostgreSQL/TimescaleDB persistence layer
```

## Implementation boundaries

- Kafka transport must be separate from Nokia payload mapping.
- Kafka client must be injectable/mocked.
- Unit tests must not require a live broker.
- Use existing NDCA configuration and logging.
- Do not make NDCA depend on `/opt/kafka-cli/client.properties`.
- Do not modify inventory collectors.
- Do not create a second generic persistence architecture if an existing one is reusable.
- Do not write configuration or operational changes back to NSP/NFM-P.

## Acceptance criteria

1. Transport is unit-testable without Kafka.
2. Real captured payload fixture parses successfully.
3. `kpiType` is validated.
4. Non-BGP telemetry is rejected/ignored according to existing conventions.
5. NE ID and object ID are preserved.
6. Only verified fields are mapped.
7. Periodic counters are preserved.
8. Source timestamps are normalized to UTC.
9. Raw payload is retained.
10. Malformed records do not crash the consumer loop.
11. Existing SYNC-012-B.2 and regression tests remain passing.
12. `python -m compileall -q src/ndca tests` passes.
13. `git diff --check` passes.
