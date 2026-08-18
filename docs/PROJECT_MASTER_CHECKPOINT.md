# OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD — Compact Master Checkpoint

**Checkpoint date:** 2026-08-18
**Repository:** `kishor-omnilink/ndca`
**Working checkout:** `/opt/ndca/repo`
**Current branch:** `feature/sync-012-b-performance-collector`

## 1. Project objective

Build the OCAC IP/MPLS Nokia custom dashboard solution using the existing NDCA data-collection architecture, Nokia NSP/NFM-P integration, Kafka where already established, PostgreSQL + TimescaleDB, and a dashboard/analytics layer.

## 2. Verified completed foundation

- NDCA Python project foundation exists.
- Configuration, logging and database foundation exist.
- Network-element/inventory ORM foundation exists.
- NFM-P API discovery artifacts exist under `docs/sync/`.
- SYNC-012-A performance API/counter discovery is complete and is the authoritative evidence baseline.
- Generic NFM-P `generic.GenericObject.triggerCollect` path, `instanceNames`, and `currentDataClasses` are verified.
- Kafka/data-path work and previously completed API/configuration checks are treated as completed and must not be repeated unless regression evidence appears.
- SYNC-012-B performance collector design exists and defines evidence-first implementation gates.
- SYNC-012-B.2 interface current-data work exists for verified interface statistics classes.
- BGP evidence-capture utility exists and is deliberately read-only.

## 3. Current milestone

**SYNC-012-B.3 — BGP Current Data**

Status: **BLOCKED ON FIELD-LEVEL EVIDENCE**

Verified:

- `bgp.PeerStats`
- `bgp.PeerStatsLogRecord`
- `generic.GenericObject.triggerCollect`
- `instanceNames`
- `currentDataClasses`
- scheduled BGP PeerStats collection example
- 5-minute scheduled polling example
- `registerLogToFile` mechanism and generic input structure
- generic XML statistics output structure

Still missing:

- exact `bgp.PeerStats` XML response payload
- exact BGP attribute/counter names
- exact `bgp.PeerStatsLogRecord` attributes
- verified BGP response-to-NDCA normalized-field mapping

## 4. Explicit implementation gate

Do **not** implement a BGP parser, collector, normalization mapping, persistence, or historical LogRecord ingestion until the exact BGP payload and field semantics are verified.

No guessing of XML element names, counter names, types, or meanings.

## 5. Current repository evidence

Relevant files:

- `docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md`
- `docs/sync/SYNC-012-A_Performance_Counter_Register.csv`
- `docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md`
- `docs/sync/SYNC-012-B.2_NFMP_Interface_Current_Data.md`
- `docs/sync/SYNC-012-B.3_BGP_Current_Data_Blocker.md`
- `src/ndca/api/nfmp_evidence_capture.py`

The BGP evidence utility is read-only, allow-listed to `bgp.PeerStats`, and captures raw XML plus metadata without parsing or persisting BGP fields.

## 6. Next action

Open ChatGPT chat:

`21-NFMP API & EVIDENCE`

Task:

> Inspect the current SYNC-012-A/B evidence and repository evidence-capture implementation. Determine exactly what BGP XML payload/field evidence is still missing to pass SYNC-012-B.3 Gate 1 and Gate 2. Do not implement a BGP parser or collector. Do not repeat completed API discovery or Kafka validation. Produce the minimum evidence acquisition procedure and a precise evidence checklist.

## 7. After B.3 is unblocked

Proceed in this order:

1. `22-PERFORMANCE COLLECTOR` — BGP current-data collector implementation.
2. `23-NORMALIZATION & MAPPING` — verified BGP field mapping.
3. `24-DATABASE & PERSISTENCE` — normalized performance persistence and deduplication.
4. `25-SCHEDULER & ORCHESTRATION` — scheduled collection lifecycle.
5. Performance validation.
6. Dashboard backend/API.
7. Dashboard UI, analytics and reporting.
8. End-to-end validation.
9. Production deployment and operations documentation.

## 8. Working rules

- Git is authoritative for code.
- Project master/checkpoint documents are authoritative for verified project state.
- One ChatGPT chat = one workstream.
- Use compact handoffs between chats.
- Inspect before implementing.
- Preserve existing functionality.
- Keep changes scoped.
- Test before closing a workstream.
- Document only verified facts.

## 9. Do not go backward

The following are frozen as completed unless new contradictory evidence appears:

- project foundation
- initial NDCA architecture
- NFM-P performance discovery / SYNC-012-A
- generic collection mechanism verification
- previously completed Kafka/data-path checks
- interface current-data work already completed under SYNC-012-B.2

**Current project focus: resolve SYNC-012-B.3 evidence blocker.**
