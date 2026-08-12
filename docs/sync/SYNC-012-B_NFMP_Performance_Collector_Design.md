# SYNC-012-B NFM-P Performance Collector Design

## 1. Objective and Scope

Objective: Define the design for a discovery-driven, testable NFM-P performance collector that ingests verified NFM-P performance statistics (current and historical where available) and persists normalized records into NDCA.

Scope:
- Design only (no production code changes)
- Use SYNC-012-A artifacts as authoritative inputs
- Support current-data retrieval and historical LogRecord retrieval only where verified
- Define lifecycle, contract, error handling, observability, security, and test strategy

Non-goal: Implementing production collection or interacting with a live NFM-P system.

## 2. NFM-P Performance Collection Architecture

High-level components (logical):
- NFM-P XML API Client (encapsulates XML transport/auth and exposes typed operations)
- Performance Collector (collector class with `collect()`/`close()` lifecycle)
- Normalization / Mapping layer (converts XML/current-data/LogRecord payloads to NDCA normalized records)
- Persistence layer (repositories and ORM models to persist normalized records)
- Scheduler / Orchestration (external component that triggers scheduled polls or on-demand runs)

The design intentionally separates these concerns so each can be implemented and tested in isolation.

## 3. Separation of Concerns

- NFM-P XML API client
  - Responsibilities: authentication, XML request/response transport, basic XML validation
  - Must not embed normalization or persistence logic
  - Exposes methods corresponding to verified XML API operations (e.g., `triggerCollect`, `registerLogToFile`, `findToFile`) only when verified by SYNC-012-A

- Performance Collector
  - Responsibilities: invoke API client, perform pre/post validation, produce raw current-data or LogRecord payloads
  - Implements `collect()` and `close()` like other collectors

- Normalization / Mapping
  - Responsibilities: validate required fields, map NDMP-specific terminology to NDCA normalized field names
  - Must operate without assuming any unverified XML structure

- Persistence
  - Responsibilities: transactional persistence via repositories, maintain idempotency and deduplication rules

- Scheduling / Orchestration
  - Responsibilities: decide scheduled vs on-demand runs, provide snapshot completeness context, and call collectors according to policy

## 4. Collection Lifecycle

1. Request
   - Collector prepares request parameters (instanceNames, currentDataClasses) using only VERIFIED/PARTIAL classes from SYNC-012-A register.
2. Response
   - API client returns parsed XML (or structured dict). Unexpected formats are treated as errors.
3. Validation
   - Ensure required monitored-object identifiers and timestamps are present; otherwise mark record invalid.
4. Normalization
   - Map fields to the NDCA normalized record contract (see section 8) without assuming unverified XML structures.
5. Persistence
   - Use repository objects within a transaction; persist normalized records and record metadata (sync id, collection time).
6. Error handling
   - Classify and surface errors (timeouts, auth failures, malformed XML, partial responses, duplicate records) and return structured failure results for orchestration.

## 5. Supported Data Types

- Current performance data: SUPPORTED when the XML API class for the statistic is VERIFIED or PARTIAL (for PARTIAL use conservative mapping). `VERIFIED` and `PARTIAL` distinctions are driven by SYNC-012-A.

- Historical performance data: SUPPORTED only where a LogRecord class is `VERIFIED` in SYNC-012-A (e.g., `bgp.PeerStatsLogRecord`). On-demand current data is not to be treated as historical. `VERIFIED`.

- Interface statistics: supported via `equipment.InterfaceStats` and `equipment.InterfaceAdditionalStats` (VERIFIED).

- BGP peer statistics: supported via `bgp.PeerStats` and `bgp.PeerStatsLogRecord` (VERIFIED).

- Other IP/MPLS statistics: included only where SYNC-012-A marks them VERIFIED or PARTIAL. If the register marks them UNKNOWN, they are explicitly out of scope.

## 6. Counter / API Classification (per SYNC-012-A)

Every counter/API used in implementation must be explicitly classified as one of:
- VERIFIED: documented XML API class and/or LogRecord class present in SYNC-012-A.
- PARTIAL: concept or category documented but exact XML API class missing; partial implementation requires additional verification before production.
- UNKNOWN: insufficient evidence; implementation of UNKNOWN classes is prohibited.

_Implementation prohibition_: UNKNOWN API classes must not be implemented or hard-coded; they require vendor documentation before inclusion.

## 7. Internal Normalized Performance Record Contract

Each normalized performance record stored by NDCA must contain at least the following fields (no XML assumptions):

- `sync_id` (string): correlation id for the collector run
- `source` (string): e.g., "NFM-P"
- `xml_class` (string | NULL): source XML API class name when VERIFIED; otherwise NULL
- `category` (string): from SYNC-012-A register (e.g., "Interface / Network Port")
- `object_id` (string): monitored object identifier (NE IP, interface name, peer id)
- `object_name` (string | NULL): monitored object human name where available
- `metric` (string): NDCA metric name (normalized)
- `metric_source_name` (string): exact NFM-P terminology when available
- `value` (numeric | string): measurement value
- `collection_time` (datetime UTC): when NDCA initiated collection or received record
- `source_time` (datetime UTC | NULL): measurement timestamp reported by NFM-P when present
- `persistence_time` (datetime UTC): when NDCA persisted the record
- `is_historical` (bool): True when record came from LogRecord-based retrieval
- `raw_payload` (JSON/dict): raw parsed payload for auditing (optional/size-limited)
- `evidence_status` (VERIFIED|PARTIAL|UNKNOWN)
- `notes` (string | NULL)

The normalization layer must populate `xml_class` only when the class is VERIFIED in SYNC-012-A; do not invent class names.

## 8. Timestamps

- `collection_time`: time the collector requested or received the response (UTC) — always present.
- `source_time`: measurement time reported by the NE/NFM-P, when present in the payload — optional.
- `persistence_time`: the time NDCA writes the normalized record — always present.

All timestamps must be normalized to UTC and stored with timezone information.

## 9. Error Handling Categories

- `Timeout`: API client timed out waiting for a response.
- `AuthenticationFailure`: failure to authenticate to the XML API.
- `MalformedXML`: XML parsing or schema validation failure.
- `EmptyResponse`: API returned no data (valid but empty result).
- `PartialResponse`: some records are present while others failed or missing.
- `DuplicateRecord`: duplicate monitored-object + metric detected during processing.
- `UnavailableHistoricalData`: requested LogRecord not available.
- `ApiError`: NFM-P returned an explicit API error/status.

Behavior:
- Classify and log each error; return structured error codes to orchestration.
- For recoverable errors (timeouts, transient API errors), orchestration may retry per the retry policy (see section 11).
- For non-recoverable errors (malformed XML, auth failure), fail the collector run and surface the error for human attention.

## 10. Retry Behavior (Conceptual)

- Retries are orchestrator-configurable and should be guided by error class and idempotency requirements.
- Timeouts and transient HTTP/XML transport errors: consider exponential backoff and bounded retries.
- Do not retry on malformed XML or authentication failure without human action.

(No retry implementation in SYNC-012-B; this is conceptual.)

## 11. Idempotency

- Collector runs must be idempotent within the scope of a single `sync_id`.
- Persistence must deduplicate records based on (`xml_class` when VERIFIED, `object_id`, `metric`, `source_time` if present) and an internal fingerprint for current-data entries.
- LogRecord-based historical ingestion should avoid re-inserting the same historical sample using the LogRecord identifier where available.

## 12. Logging and Observability

- Emit structured logs with levels: DEBUG/INFO/WARNING/ERROR.
- Emit correlation fields: `sync_id`, `xml_class`, `object_id`, `metric`, `evidence_status`.
- Emit metrics: `collector.success`, `collector.failure`, `collector.duration_seconds`, `records.normalized`, `records.persisted`.
- Preserve raw response to audit logs only when privacy/compliance allows; otherwise store a hashed fingerprint and minimal metadata.

## 13. Security Requirements

- Credentials must never be logged.
- XML payloads must not contain credentials; the client must sanitize any sensitive subelements before logging.
- Secrets (credentials, tokens) must come from configuration/environment and never be embedded in code or committed.
- TLS verification must be enabled by default and configurable via `ndca.core.config` settings. Default: verify TLS.

## 14. Test Strategy

- Unit tests: `unittest` + mocks for the API client. Validate normalization, error classification, and persistence calls.
- Integration tests (non-live): use recorded sample XML converted into fixtures under `tests/fixtures` and validate normalization.
- Live integration tests: separate gate and must be executed only when a lab NFM-P instance is available (Gate 5).
- All tests must run offline by default and not require a live NFM-P connection.

## 15. Non-goals for SYNC-012-B

- No production implementation of the collector or persistence models.
- No live NFM-P connectivity or credentials are included.
- No performance or scalability tuning beyond design-level notes.

## 16. Implementation Gates

Gate 1: API class verified
- The XML API class and its fields are present and documented in vendor PDFs.

Gate 2: response structure verified
- Example responses or schema validate the mapping to the normalized contract.

Gate 3: normalization verified
- Unit tests confirm mapping from raw payload to NDCA normalized record contract.

Gate 4: persistence verified
- Repositories persist normalized records without duplicates; transactional semantics validated.

Gate 5: live NFM-P integration test
- Run live tests against a lab NFM-P instance with recorded credentials and test data.

Each gate must be passed before moving to the next; UNKNOWN items block progression to Gate 4/5.

## 17. Mapping Table (SYNC-012-A → SYNC-012-B status)

| Category | Statistic / API | XML API class (SYNC-012-A) | LogRecord class | SYNC-012-B status | Notes |
|---|---|---|---|---|---|
| Interface / Network Port | Received Octets | equipment.InterfaceStats | UNKNOWN | VERIFIED | Documented in XML API guide; LogRecord for interface stats not present in summary evidence.
| Interface / Network Port | Received Broadcast Packets | equipment.InterfaceAdditionalStats | UNKNOWN | VERIFIED | Documented example in XML API guide for additional stats.
| BGP | Peer statistics | bgp.PeerStats | bgp.PeerStatsLogRecord | VERIFIED | Both current and LogRecord classes documented.
| Other / MPLS | MPLS interface plot support | UNKNOWN (profile support) | UNKNOWN | PARTIAL | Plotter profiles document MPLS support; XML class not in summary evidence.
| System / Equipment | Physical equipment status | UNKNOWN | UNKNOWN | PARTIAL | Category documented; exact XML class not provided in summary evidence.
| IP / Ethernet / OSPF / IS-IS | Various categories | UNKNOWN | UNKNOWN | UNKNOWN | No explicit XML API class evidence in supplied SYNC-012-A summary.

## 18. Implementation Notes

- The XML API client should be added under `src/ndca/api/` as a new module (e.g., `ndca.api.nfmp_xml`) and exported from `ndca.api.__init__` when the implementation is production-ready.
- The collector should be placed under `src/ndca/collectors/performance/` following existing collector patterns.
- New ORM objects (if required) should be added under `src/ndca/models/orm` and include `BaseMixin` fields.
- Tests should be added under `tests/` using `unittest` and the existing fixtures pattern.

## 19. Acceptance Criteria for SYNC-012-B Design

- Design document present at `docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md`.
- Design explicitly references SYNC-012-A artifacts and does not invent API class names for UNKNOWN items.
- Test strategy described and offline tests available to validate contract.
- Implementation gates defined and block implementation on UNKNOWN evidence.

---

Please approve this design and I will scaffold the collector and API client skeletons and the initial unit tests (mocked, offline) in a follow-up change.