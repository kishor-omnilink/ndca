# SYNC-012-B.3 BGP Current Data Blocker

## Status

BLOCKED

This document formally records that SYNC-012-B.3 is blocked pending vendor evidence for BGP current-data collection. This blocker is based on the verified discovery artifacts in the repository and does not infer or invent any NFM-P XML request, response, field names, or API classes.

## 1. Candidate capability

Candidate capability under review: `bgp.PeerStats` current performance data.

This is a candidate NFM-P statistics class for current BGP peer statistics. The class name itself is documented as a candidate capability in the SYNC-012-A discovery artifacts, but the required request/response evidence for implementation is not yet available in the supplied repository evidence.

## 2. Verified classes from SYNC-012-A

The following classes are verified by the SYNC-012-A discovery and register artifacts:

- `bgp.PeerStats`
- `bgp.PeerStatsLogRecord`

These entries are recorded in:

- `docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md`
- `docs/sync/SYNC-012-A_Performance_Counter_Register.csv`

## 3. What is already verified

The following items are already verified in the SYNC-012-A evidence set:

- `generic.GenericObject.triggerCollect`
- `instanceNames`
- `currentDataClasses`
- VERIFIED status of `bgp.PeerStats` in the SYNC-012-A register

This means that the generic collection mechanism and the high-level class identification are accepted as evidence, but the BGP-specific XML payload and normalization details are not yet verified.

## 4. Missing evidence

The following evidence is still missing and is required before implementation may proceed safely:

- documented BGP response XML/schema
- exact BGP counter/field names
- response-to-normalized-field mapping
- exact registerLogToFile request schema
- bgp.PeerStatsLogRecord response structure
- exact source page/section evidence where unavailable

The current repository evidence does not contain the actual BGP XML payload schema, the exact counter names, or the mapping from the vendor response to NDCA normalized fields. The exact page/section citations for the vendor PDFs are also not available in the supplied evidence summary, and implementation must not proceed on undocumented assumptions.

## 5. Why implementation cannot safely proceed without this evidence

SYNC-012-B.3 cannot be implemented safely without the required evidence because:

- the XML response contract is not yet proven;
- the exact field names and data types are not yet documented;
- the response-to-normalized-field translation cannot be validated without a verified payload and mapping;
- the registerLogToFile request shape for BGP is not proven;
- bgp.PeerStatsLogRecord has not been shown to have a valid response structure in the supplied evidence; and
- any implementation based on inferred XML names or guessed field semantics would create unsupported production behavior and would violate the evidence-first rule in the SYNC-012-A and SYNC-012-B design artifacts.

The design document explicitly states that UNKNOWN or undocumented classes must not be implemented or hard-coded. A BGP current-data collector would require verified request and response structure before normalization or persistence can be considered safe.

## 6. Required implementation gates before B.3

The following gates are required before any implementation of SYNC-012-B.3 is allowed:

- Gate 1: API/request structure verified.
  - Verify the exact NFM-P request structure used to invoke BGP current data collection and any related request parameters.
  - Confirm the exact usage of `triggerCollect`, `instanceNames`, and `currentDataClasses` with `bgp.PeerStats`.

- Gate 2: response structure and field mapping verified.
  - Verify the exact BGP XML response structure.
  - Confirm every counter/field name, type, and meaning.
  - Document the exact response-to-normalized-field mapping before any collector or parser logic is implemented.

No implementation is permitted to proceed until both gates are satisfied with explicit evidence.

## 7. Explicit non-implementation status

This document records the following restrictions:

- no production code changes
- no BGP XML parser
- no BGP collector
- no persistence
- no historical LogRecord implementation
- no invented XML fields/classes

No implementation artifacts are introduced here. This is a blocker record only.

## 8. Repository evidence references

Relevant repository paths:

- `docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md`
- `docs/sync/SYNC-012-A_Performance_Counter_Register.csv`
- `docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md`

The SYNC-012-A discovery and register artifacts are the authoritative verification inputs. The SYNC-012-B design doc states that implementation must be gated on verified API structure and verified response mapping before production behavior is introduced.

## 9. Resolution statement

SYNC-012-B.3 is BLOCKED pending the missing BGP evidence described above. The milestone must not proceed until the required evidence is available and both implementation gates are satisfied.
