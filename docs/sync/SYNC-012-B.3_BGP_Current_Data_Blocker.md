# SYNC-012-B.3 BGP Current Data Blocker

## Status

BLOCKED

This document records that SYNC-012-B.3 remains blocked even though the generic NFM-P 24.4 performance-collection evidence has been verified. The verified evidence confirms the generic collection mechanism and the documented BGP class names, but it does not confirm the exact BGP XML payload or the exact BGP field names required for a safe implementation. No BGP field names, XML payload structure, or normalized mapping are inferred or invented here.

## 1. Candidate capability

Candidate capability under review: `bgp.PeerStats` current performance data.

This capability is documented as a verified XML API class in the NFM-P 24.4 XML API Developer Guide and in the SYNC-012-A register, but the exact BGP XML response structure and field names remain unknown.

## 2. Verified evidence from the NFM-P 24.4 guides

The following items are verified from the uploaded NFM-P 24.4 XML API Developer Guide Issue 1 and Statistics Management Guide Issue 1:

- `bgp.PeerStats` — VERIFIED — XML API Developer Guide §14.4.1, p.175; §14.6, p.180; §7.1.1 / information-model reference, p.85
- `bgp.PeerStatsLogRecord` — VERIFIED — XML API Developer Guide §14.4.1, p.175; §14.8.2, pp.185-187; §14.8.3, p.188
- `generic.GenericObject.triggerCollect` — VERIFIED — XML API Developer Guide §14.5.5, p.179
- `instanceNames` — VERIFIED — XML API Developer Guide §14.5.5, p.179; §14.6, p.180
- `currentDataClasses` — VERIFIED — XML API Developer Guide §14.5.5, p.179; §14.6, p.180
- scheduled BGP PeerStats collection example — VERIFIED — XML API Developer Guide §14.7, p.182; §14.8.2, pp.185-187
- 5-minute scheduled polling example — VERIFIED — XML API Developer Guide §14.8.3, p.188
- `registerLogToFile` retrieval mechanism — VERIFIED — XML API Developer Guide §14.6, p.180; §14.8.2, pp.185-187; §14.8.3, p.188
- `registerLogToFile` generic input structure — VERIFIED — XML API Developer Guide §14.8.2, pp.185-187; §14.8.3, p.188
- generic XML statistics output structure — VERIFIED — XML API Developer Guide §14.4.1, p.175; §14.6, p.180; §14.8.2, pp.185-187

The following repository artifacts record the same verified status:

- [docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md](docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md)
- [docs/sync/SYNC-012-A_Performance_Counter_Register.csv](docs/sync/SYNC-012-A_Performance_Counter_Register.csv)

## 3. Verified classes from SYNC-012-A

The following classes are verified by the SYNC-012-A discovery and register artifacts:

- `bgp.PeerStats`
- `bgp.PeerStatsLogRecord`

These are recorded in the repository discovery and register artifacts above and are consistent with the uploaded NFM-P 24.4 documentation.

## 4. What is already verified

The following items are already verified:

- `generic.GenericObject.triggerCollect`
- `instanceNames`
- `currentDataClasses`
- VERIFIED status of `bgp.PeerStats` in the SYNC-012-A register
- scheduled BGP PeerStats collection example
- 5-minute scheduled polling example
- `registerLogToFile` retrieval mechanism
- `registerLogToFile` generic input structure
- generic XML statistics output structure

This confirms the generic operation path and the documented presence of the BGP class names in the NFM-P design and discovery artifacts. It does not confirm the exact BGP XML payload contract or the specific BGP counter names.

## 5. Missing evidence that remains blocked

The following evidence is still missing and remains a blocker before implementation may proceed safely:

- exact `bgp.PeerStats` attribute/counter names
- exact `bgp.PeerStats` XML response payload
- exact `bgp.PeerStatsLogRecord` attributes
- BGP-specific response-to-NDCA normalized-field mapping
- exact source page/section evidence for any additional BGP-specific response detail not yet cited

This document does not infer or invent any BGP field names. The exact payload, field names, and normalized mapping remain UNKNOWN.

## 6. Why implementation cannot safely proceed without this evidence

SYNC-012-B.3 cannot be implemented safely even with the verified generic operation path because:

- the XML response contract for BGP current data is not yet proven;
- the exact BGP counter names and attribute names are not documented in the supplied evidence;
- the response-to-normalized-field translation cannot be validated without a verified BGP payload contract;
- `bgp.PeerStatsLogRecord` attributes are not yet verified at the field level;
- any implementation based on inferred XML names or guessed field semantics would create unsupported production behavior and would violate the evidence-first rule used throughout the SYNC-012-A and SYNC-012-B design artifacts.

The design documents require verified request structure and verified response mapping before production logic is introduced. The BGP-specific details remain outside that threshold.

## 7. Required implementation gates before B.3

The following gates are required before any implementation of SYNC-012-B.3 is allowed:

- Gate 1: API/request structure verified.
  - Verify the exact NFM-P request structure used to invoke BGP current data collection.
  - Confirm the exact API contract for `triggerCollect`, `instanceNames`, and `currentDataClasses` when targeting `bgp.PeerStats`.
  - Confirm the exact `registerLogToFile` request details, including the generic input structure already verified.

- Gate 2: response structure and field mapping verified.
  - Verify the exact BGP XML response payload.
  - Confirm every counter/field name, type, and meaning.
  - Document the exact response-to-normalized-field mapping before any parser or collector logic is implemented.

No implementation is permitted to proceed until both gates are satisfied and the exact BGP payload semantics are documented.

## 8. Explicit non-implementation status

This document records the following restrictions:

- no production code changes
- no BGP XML parser
- no BGP collector
- no persistence
- no historical LogRecord implementation
- no invented XML fields/classes

No implementation artifacts are introduced here. This remains a blocker record only.

## 9. Repository evidence references

Relevant repository paths:

- [docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md](docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md)
- [docs/sync/SYNC-012-A_Performance_Counter_Register.csv](docs/sync/SYNC-012-A_Performance_Counter_Register.csv)
- [docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md](docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md)

The discovery and register artifacts establish the evidence baseline. The B.3 gate remains in place until the exact BGP response payload and field mapping are documented and verified.

## 10. Resolution statement

SYNC-012-B.3 remains BLOCKED. The generic collection path is verified, but the exact BGP payload and field-level mapping remain UNKNOWN. The milestone must not proceed until the remaining BGP evidence is supplied and both implementation gates are satisfied.
