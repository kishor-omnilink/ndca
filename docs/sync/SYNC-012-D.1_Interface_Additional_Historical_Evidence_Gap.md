# SYNC-012-D.1 — Interface Additional Historical Evidence Gap

## 1. Purpose

This document records the evidence reconciliation and implementation status for the NFM-P historical performance path associated with:

* `equipment.InterfaceAdditionalStats`
* `equipment.InterfaceAdditionalStatsLogRecord`
* the NFM-P `findToFile` historical response
* the raw historical record representation used by NDCA
* the future mapping required to normalize historical Interface Additional statistics into NDCA `PerformanceRecord` records.

This document is evidence-first.

The historical parser preserves Nokia source field names exactly at the raw parsing layer. No metric normalization or `PerformanceRecord` conversion is performed by the D.1.2 parser.

---

## 2. D.1 Status

**D.1 STATUS: EVIDENCE RECONCILED — HISTORICAL PARSER CONTRACT IMPLEMENTED AND VERIFIED**

D.8 established the reusable `findToFile` request-construction foundation.

D.1.2 subsequently established and regression-tested the historical Interface Additional LogRecord parsing contract using the captured NFM-P XML response fixture maintained in the NDCA test suite.

The D.1.2 implementation does not perform historical metric normalization or persistence.

Therefore, the current state is:

| Area                                                    | Status                            |
| ------------------------------------------------------- | --------------------------------- |
| `equipment.InterfaceAdditionalStats` current-data class | VERIFIED                          |
| Generic `findToFile` operation                          | VERIFIED                          |
| `findToFile` request-construction implementation        | VERIFIED                          |
| Historical Interface Additional LogRecord class         | VERIFIED BY CAPTURED XML EVIDENCE |
| Historical LogRecord XML structure                      | VERIFIED BY CAPTURED XML EVIDENCE |
| Historical LogRecord identity fields                    | VERIFIED                          |
| Historical `timeCaptured` field                         | VERIFIED                          |
| Historical metadata fields                              | VERIFIED                          |
| Historical Interface Additional metric field names      | VERIFIED                          |
| Raw historical XML parser                               | IMPLEMENTED                       |
| Multiple historical records                             | VERIFIED                          |
| Required historical record validation                   | VERIFIED                          |
| Historical response-to-`PerformanceRecord` mapping      | OPEN — D.1.3                      |
| Historical metric normalization                         | OPEN — D.1.3                      |
| Historical persistence                                  | OPEN — subsequent implementation  |
| Live NFM-P historical collection validation             | PENDING                           |
| Production historical collector integration             | NOT YET IMPLEMENTED               |

---

## 3. Evidence Boundary

The available NFM-P evidence establishes support for:

* current statistics
* scheduled statistics
* on-demand statistics
* LogRecord-based historical statistics
* `generic.GenericObject.triggerCollect`
* `registerLogToFile`
* `findToFile`

The current-data performance classes include:

* `equipment.InterfaceStats`
* `equipment.InterfaceAdditionalStats`

D.1.2 additionally establishes the historical response representation observed in the captured XML fixture:

```text
findToFileResponse
└── equipment.InterfaceAdditionalStatsLogRecord
    ├── monitoredObjectClass
    ├── monitoredObjectPointer
    ├── displayedName
    ├── monitoredObjectSiteId
    ├── monitoredObjectSiteName
    ├── timeCaptured
    ├── periodicTime
    ├── suspect
    ├── objectFullName
    ├── name
    ├── createdOnPollType
    ├── updatedOnPollType
    ├── recordId
    ├── bucketId
    ├── deploymentState
    ├── historical metric fields
    └── children-Set
```

The captured fixture therefore provides direct repository evidence for:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

The repository must continue to distinguish this captured XML evidence from a separately preserved OEM-document citation. The D.1.2 implementation does not claim more provenance than is actually preserved in the repository.

---

## 4. Historical XML Class

The verified historical class represented by the captured XML fixture is:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

The parser matches the complete Nokia dotted class name.

XML namespace qualification is ignored for class matching.

For example:

```text
{xmlapi_1.0}equipment.InterfaceAdditionalStatsLogRecord
```

is interpreted as:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

The full dotted Nokia class name is preserved in the parsed record as:

```text
xml_class
```

with the value:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

No shortened class name is substituted.

---

## 5. Historical Record Identity and Validation

Each historical record must contain the minimum identity/time fields required by the NDCA raw historical parsing contract:

```text
monitoredObjectPointer
timeCaptured
```

If either required field is absent or empty, the parser raises `ValueError`.

The parser does not require every documented statistic counter to be present.

This is intentional because a Nokia `findToFile` request may use a `resultFilter` to restrict the attributes returned by NFM-P.

---

## 6. Verified Historical Metadata Fields

The captured historical Interface Additional record contains the following metadata fields:

```text
monitoredObjectClass
monitoredObjectPointer
displayedName
monitoredObjectSiteId
monitoredObjectSiteName
timeCaptured
periodicTime
suspect
objectFullName
name
createdOnPollType
updatedOnPollType
recordId
bucketId
deploymentState
```

The D.1.2 parser preserves these source names exactly.

No metadata normalization is performed at this layer.

---

## 7. Verified Historical Metric Fields

The captured Interface Additional historical record contains the following Nokia source metric names:

```text
receivedTotalOctets
receivedTotalOctetsPeriodic

receivedUnicastPackets
receivedUnicastPacketsPeriodic

receivedMulticastPackets
receivedMulticastPacketsPeriodic

receivedBroadcastPackets
receivedBroadcastPacketsPeriodic

transmittedTotalOctets
transmittedTotalOctetsPeriodic

transmittedUnicastPackets
transmittedUnicastPacketsPeriodic

transmittedMulticastPackets
transmittedMulticastPacketsPeriodic

transmittedBroadcastPackets
transmittedBroadcastPacketsPeriodic
```

These names are authoritative **as source field names for the captured evidence fixture**.

They must not be silently renamed during raw parsing.

For example:

```text
receivedBroadcastPackets
```

must remain:

```text
receivedBroadcastPackets
```

and must not be converted at this layer into:

```text
rx_broadcast_packets
```

or another normalized name.

Any normalized NDCA metric name belongs to the subsequent D.1.3 normalization layer.

---

## 8. Raw Parser Contract

The implemented parser is:

```text
NFMPXmlClient.parse_find_to_file_response()
```

with the Interface Additional convenience method:

```text
NFMPXmlClient.parse_interface_additional_historical_response()
```

The Interface Additional parser delegates to the generic `findToFile` response parser with:

```text
expected_class =
equipment.InterfaceAdditionalStatsLogRecord
```

The returned structure is a list of raw dictionaries.

A representative record has the logical form:

```text
{
    "xml_class": "equipment.InterfaceAdditionalStatsLogRecord",
    "monitoredObjectClass": "...",
    "monitoredObjectPointer": "...",
    "displayedName": "...",
    "monitoredObjectSiteId": "...",
    "monitoredObjectSiteName": "...",
    "timeCaptured": "...",
    "periodicTime": "...",
    "suspect": "...",
    "objectFullName": "...",
    "name": "...",
    "createdOnPollType": "...",
    "updatedOnPollType": "...",
    "recordId": "...",
    "bucketId": "...",
    "deploymentState": "...",
    "... Nokia metric fields ...": "..."
}
```

The parser intentionally returns source values without converting metric types or applying NDCA metric normalization.

---

## 9. XML Namespace Handling

NFM-P XML responses may use the:

```text
xmlapi_1.0
```

namespace.

The parser therefore strips namespace qualification when matching XML element names.

The original Nokia local field names are preserved.

This allows both:

```text
{xmlapi_1.0}equipment.InterfaceAdditionalStatsLogRecord
```

and:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

to resolve to the same Nokia class name for parser matching.

---

## 10. Multiple Record Handling

The parser supports multiple historical LogRecord elements within a single `findToFileResponse`.

For example:

```text
findToFileResponse
├── equipment.InterfaceAdditionalStatsLogRecord
│   ├── monitoredObjectPointer = port-1
│   └── timeCaptured = ...
└── equipment.InterfaceAdditionalStatsLogRecord
    ├── monitoredObjectPointer = port-2
    └── timeCaptured = ...
```

The parser returns one raw dictionary per matching historical record.

---

## 11. `findToFile` Request Contract

The D.8 `findToFile` request foundation is reused by D.1.2.

The required request fields are:

```text
full_class_name
monitored_object_pointer
time_captured.first
time_captured.second
file_name
```

The Interface Additional historical class is now supported as:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

The optional:

```text
result_filter
```

may be supplied to restrict returned attributes.

The generated request preserves the supplied Nokia attribute names.

---

## 12. Evidence Fixture

The D.1.2 parser is regression-tested against:

```text
tests/fixtures/nfmp_interface_additional_stats_logrecord_24_4.xml
```

The verified SHA-256 observed during D.1.2 reconciliation is:

```text
28819f01d803dbdd3866fd8146b1c928dcafb1cf9ca2755edd057f40c0ac5613
```

The fixture contains a namespaced:

```text
equipment.InterfaceAdditionalStatsLogRecord
```

record and representative historical metadata and Interface Additional metric fields.

The fixture is test evidence and must not be represented as a live NFM-P production capture unless separately identified as such.

---

## 13. D.1.2 Validation Evidence

The complete implementation test file was executed successfully:

```text
pytest -q tests/test_sync_012_b_performance_collector_impl.py
```

Result:

```text
26 passed in 0.28s
```

The D.1.2 implementation test coverage includes:

* historical response parsing
* exact Nokia metric-name preservation
* metadata-field preservation
* multiple historical records
* missing `monitoredObjectPointer` validation
* missing `timeCaptured` validation
* malformed XML handling
* empty XML handling
* historical `findToFile` class support
* optional `resultFilter`
* existing triggerCollect behavior
* existing `findToFile` request behavior

The following previously established regression suites also passed during D.1.2 validation:

```text
B.2:
10 passed

B.3:
7 passed

B.3 evidence:
7 passed
```

The implementation also passed:

```text
git diff --check
```

---

## 14. Implementation Boundary

D.1.2 deliberately stops at the raw historical parsing boundary.

Implemented:

```text
NFM-P findToFile XML
        ↓
XML parsing
        ↓
historical class identification
        ↓
raw LogRecord dictionary
        ↓
exact Nokia source fields preserved
```

Not implemented by D.1.2:

```text
raw LogRecord
        ↓
metric normalization
        ↓
NDCA PerformanceRecord
        ↓
database persistence
```

No `PerformanceRecord` conversion is performed by the historical parser.

No database write is performed by the historical parser.

---

## 15. D.1.3 Next Boundary

The next implementation stage is:

**SYNC-012-D.1.3 — Historical Interface Additional Normalization**

D.1.3 should establish:

1. mapping from verified Nokia source fields to NDCA metric names
2. source timestamp conversion
3. collection timestamp handling
4. counter versus periodic-counter semantics
5. object identity mapping
6. `PerformanceRecord` construction
7. validation of normalized records
8. regression tests for the normalization contract

D.1.3 must preserve the raw evidence contract established by D.1.2.

No Nokia source field should be renamed or discarded before the normalization boundary is explicitly defined and tested.

---

## 16. Live Validation Boundary

The D.1.2 parser has been validated against the repository fixture.

This does **not** by itself establish successful live NFM-P historical retrieval.

Live validation remains a separate evidence item and must be performed against the actual NFM-P environment before claiming end-to-end historical collection.

Required live evidence should include, where available:

```text
NFM-P endpoint
request class
monitored object
time range
findToFile request
raw response
response record count
observed historical class
observed fields
capture timestamp
```

Live evidence must be preserved separately from unit-test fixtures.

---

## 17. Evidence and Provenance Rule

The NDCA project follows an evidence-first approach.

Accordingly:

* captured XML evidence is preserved as evidence
* test fixtures are explicitly identified as fixtures
* source field names are preserved exactly
* implementation claims are tied to passing tests
* live collection claims require live evidence
* OEM-document claims require preserved OEM-document evidence or an explicit source reference
* assumptions are not silently promoted to verified facts

The historical parser implementation is therefore considered **verified at the captured XML parsing boundary**, while live end-to-end NFM-P historical collection remains a separate validation activity.

---

## 18. D.1 Closure Position

D.1.2 closes the historical Interface Additional **raw parsing contract**.

D.1.3 closes the evidence-backed historical Interface Additional **normalization contract** for the currently verified metric mapping.

It does not close the complete historical performance pipeline.

Current milestone position:

```text
D.1.1 — Historical evidence investigation
    COMPLETE

D.1.2 — Historical XML parser contract
    COMPLETE

D.1.3 — Historical → PerformanceRecord normalization
    COMPLETE

Historical persistence
    PENDING

Live end-to-end historical collection
    PENDING
```

Therefore:

**D.1.2 = COMPLETE**

**D.1.3 = COMPLETE**

**D.1 overall = NOT YET COMPLETE**

Historical persistence and live end-to-end NFM-P historical collection remain pending.
