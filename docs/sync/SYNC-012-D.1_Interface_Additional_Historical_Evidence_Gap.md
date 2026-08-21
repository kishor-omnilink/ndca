# SYNC-012-D.1 — Interface Additional Historical Evidence Gap

## 1. Purpose

This document records the remaining NFM-P historical performance evidence gap for:

- `equipment.InterfaceAdditionalStats`
- its scheduled/historical `LogRecord` representation
- the exact historical response structure
- the mapping required to normalize historical Interface Additional statistics into NDCA `PerformanceRecord` records.

This document is evidence-first.

No XML API class, LogRecord class, attribute, counter, response structure, or NDCA mapping may be inferred from naming similarity.

---

## 2. Current Status

**D.1 STATUS: OPEN — HISTORICAL EVIDENCE GAP NOT CLOSED**

The D.8 implementation work has established a reusable `findToFile` request-construction foundation.

However, D.8 does **not** establish the exact Nokia historical Interface Additional `LogRecord` contract.

Therefore:

| Area | Status |
|---|---|
| `equipment.InterfaceAdditionalStats` current-data class | VERIFIED |
| Generic `findToFile` operation | VERIFIED |
| `findToFile` request-construction implementation | VERIFIED |
| Historical Interface Additional LogRecord class | UNKNOWN |
| Historical LogRecord attributes | UNKNOWN |
| Exact historical XML response payload | UNKNOWN |
| Historical response-to-`PerformanceRecord` mapping | OPEN |
| Historical collector implementation | NOT AUTHORIZED |
| Historical persistence implementation | NOT AUTHORIZED |

---

## 3. Evidence Boundary

The supplied NFM-P documentation establishes that performance statistics support:

- current statistics
- scheduled statistics
- on-demand statistics
- LogRecord-based historical statistics
- `generic.GenericObject.triggerCollect`
- `registerLogToFile`
- `findToFile`

The documentation also establishes:

- `equipment.InterfaceStats`
- `equipment.InterfaceAdditionalStats`

as NFM-P XML API performance classes.

However, the currently available evidence does **not** establish the exact historical LogRecord class corresponding to:

`equipment.InterfaceAdditionalStats`

The evidence therefore remains insufficient to claim:

`equipment.InterfaceAdditionalStatsLogRecord`

as a verified Nokia XML API class.

---

## 4. Verified Current Interface Additional Class

The following class is explicitly established by the available NFM-P evidence:

```text
equipment.InterfaceAdditionalStats