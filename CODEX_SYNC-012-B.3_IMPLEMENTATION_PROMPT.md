# Codex / Code Studio Prompt — SYNC-012-B.3

Repository:
`/opt/ndca/repo`

Branch:
`feature/sync-012-b-performance-collector`

Implement **SYNC-012-B.3 — Kafka BGP Performance Collector**.

## Do not repeat investigation

Do not repeat:
- global/NE-specific YANG library discovery;
- `openconfig-bgp:bgp` testing;
- `nokia-oper-perform:` root testing;
- `openconfig-network-instance` namespace testing;
- RESTCONF subscription experiments.

Those are already completed.

## Verified runtime source

Bootstrap:
`10.110.11.60:9192`

Topic:
`ns-eg-1716a23b-7c94-4393-831d-cd97c20c1e70`

Existing subscription:
`service_vprn_bgp_neighbor_statistics`

Telemetry type:
`telemetry:/base/sros-service-vprn/service_vprn_bgp_neighbor_statistics`

Kafka CLI:
`4.3.1`

The topic has been successfully described and consumed and contains actual BGP telemetry records.

## First inspect the existing repository

Inspect before modifying:

`src/ndca/collectors/performance/nfmp_performance_collector.py`

`src/ndca/models/dto/performance_record.py`

`tests/test_sync_012_b_performance_collector.py`

`tests/test_sync_012_b_performance_collector_b2.py`

`tests/test_sync_012_b_performance_collector_b3.py`

`tests/test_sync_012_b_performance_collector_b3_evidence.py`

`tests/test_sync_012_b_performance_collector_impl.py`

Also inspect `pyproject.toml`, requirements files, current configuration, logging, and repository/persistence abstractions.

## Supplied implementation package

Use these supplied files as the starting point:

`docs/sync/SYNC-012-B.3_Kafka_Implementation_Spec.md`

`src/ndca/collectors/performance/kafka_bgp_performance_consumer.py`

`src/ndca/mappers/bgp_kafka_mapper.py`

`tests/test_sync_012_b_kafka_bgp_performance.py`

`config/sync-012-b-kafka.env.example`

Do not blindly overwrite existing files. Integrate with the existing NDCA architecture.

## Real payload requirement

A real Kafka consumer run already produced five BGP telemetry messages.

The first real payload must be saved as:

`tests/fixtures/nsp_bgp_neighbor_statistics_20260815.json`

If the actual fixture is not available in the repository, do not invent a production schema. Keep the supplied unit tests separate and report the missing real-payload fixture as the only evidence gap.

## Verified fields

Only map these verified BGP fields:

`neId`, `system-id`, `objectId`, `kpiType`

`peer-as`, `peer-port`, `local-port`, `session-state`, `last-state`, `last-event`, `last-error`, `negotiated-family`, `operational-local-address`, `operational-remote-address`, `peer-identifier`, `established-transitions`, `last-established-time`, `number-of-update-flaps`, `hold-time-interval`, `keep-alive-interval`

`family-prefix_ipv4_received`, `family-prefix_ipv4_active`, `family-prefix_ipv4_sent`, `family-prefix_ipv4_backup`, `family-prefix_ipv4_rejected`, `family-prefix_ipv4_suppressed`

`family-prefix_ipv6_received`, `family-prefix_ipv6_active`, `family-prefix_ipv6_sent`, `family-prefix_ipv6_backup`, `family-prefix_ipv6_rejected`, `family-prefix_ipv6_suppressed`

`received_messages`, `received_updates`, `received_octets`, `received-route-refresh`

`sent_messages`, `sent_updates`, `sent_octets`, `sent-route-refresh`

`oper-tcp-mss`, `rcvd-tcp-mss`, `time-captured`, `time-captured-periodic`

Accept periodic variants where the real payload contains them.

## Implementation rules

1. Separate Kafka transport from Nokia payload mapping.
2. Kafka client must be injectable/mocked.
3. Unit tests must not require Kafka.
4. Use existing NDCA configuration and logging.
5. Never store secrets in source.
6. Do not make runtime depend on `/opt/kafka-cli/client.properties`.
7. Preserve raw payload.
8. Normalize source timestamps to UTC.
9. Reject/ignore non-BGP telemetry according to existing conventions.
10. Malformed records must not crash the consumer loop.
11. Unknown fields remain raw and are not silently mapped.
12. Do not modify inventory behavior.
13. Reuse existing performance DTO/repository abstractions where appropriate.
14. Do not introduce Docker.
15. Do not write changes back to NSP/NFM-P.

## Kafka dependency

Inspect the current dependency set first.

If a Kafka library already exists, use it.

If not, use a maintained Python 3.12-compatible Kafka client; prefer `confluent-kafka` unless the existing dependency strategy dictates otherwise, and document the dependency.

## Tests

Add/modify tests for:
- valid BGP envelope;
- invalid/missing envelope;
- wrong `kpiType`;
- real payload regression;
- peer/service identity;
- session-state;
- prefix counters;
- traffic counters;
- periodic counters;
- timestamp normalization;
- raw payload preservation;
- malformed Kafka record handling;
- injectable consumer;
- no live broker in unit tests.

Run:

```bash
cd /opt/ndca/repo
python -m compileall -q src/ndca tests

python -m unittest -v   tests.test_sync_012_b_performance_collector   tests.test_sync_012_b_performance_collector_b2   tests.test_sync_012_b_performance_collector_b3   tests.test_sync_012_b_performance_collector_b3_evidence   tests.test_sync_012_b_performance_collector_impl   tests.test_sync_012_b_kafka_bgp_performance

git diff --check
git status --short
```

Run the broader existing regression suite if the repository defines one.

## Live Kafka integration

Keep live Kafka integration separate and disabled by default.

Use:
- `10.110.11.60:9192`
- `ns-eg-1716a23b-7c94-4393-831d-cd97c20c1e70`
- application TLS configuration
- dedicated consumer group

Do not hard-code secrets.

## Final report

Return:
1. Full paths of created/modified files.
2. Dependency changes.
3. Test results.
4. Whether the real Kafka fixture was added.
5. Whether live Kafka integration was executed.
6. Remaining blockers.
7. `git diff --check`.
8. `git status --short`.

Do not commit or push unless explicitly requested.
