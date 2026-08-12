# SYNC-012-B.2 NFM-P Interface Current Data

## Objective

Document the verified NFM-P XML API contract for a conservative, offline current-data collector focused on interface statistics. This task is intentionally limited to the set of XML API operations and classes explicitly supported by the supplied Nokia NFM-P Release 24.4 XML API Developer Guide evidence.

## Source evidence

The authoritative evidence for this task is the Nokia NFM-P Release 24.4 XML API Developer Guide:

- Section 14.5.5: "On-demand statistics collection"
- Section 14.4: scheduled statistics vs current-data / historical data distinction
- Section 14.6 / 14.8: `registerLogToFile` is the recommended mechanism for ongoing performance statistics retrieval

Verified operation and request fields:

- `generic.GenericObject.triggerCollect`
- request fields:
  - `<instanceNames>`
  - `<currentDataClasses>`

Verified current-data classes:

- `equipment.InterfaceStats`
- `equipment.InterfaceAdditionalStats`

The guide also states that `triggerCollect` creates or updates an on-demand current-data object and does not create a new historical log record.

## Current-data vs historical-data distinction

- On-demand statistics collection uses `generic.GenericObject.triggerCollect`.
- Triggered current-data objects are not historical log records.
- Scheduled performance statistics combine current data with LogRecord history.
- Historical LogRecord collection is explicitly not implemented in this task.

## Request flow

1. Collector validates the requested XML class names against the verified allow-list.
2. Collector invokes `generic.GenericObject.triggerCollect` with:
   - `instanceNames`
   - `currentDataClasses`
3. Collector inspects the returned current-data payload.
4. Collector normalizes only fields supported by supplier evidence or already-used project conventions.
5. The normalized record is stored as a `PerformanceRecord` with `is_historical = False`.

## Verified classes included in this task

- `equipment.InterfaceStats`
- `equipment.InterfaceAdditionalStats`

## Explicitly out of scope for this task

The following classes are not added in this task unless they are later confirmed in vendor evidence:

- IP
- Ethernet
- OSPF
- IS-IS
- MPLS

The collector must reject unverified interface or non-interface classes.

## Normalized output

The collector normalizes only the following supported fields for current-data interface statistics:

- `source`: "NFM-P"
- `xml_class`: source XML class when explicitly present and verified
- `category`: current-data statistic category when supplied by the response
- `object_id`: monitored-object identifier when present
- `object_name`: monitored-object name when present
- `metric`: normalized metric name when available
- `metric_source_name`: exact source terminology when available
- `value`: numeric or string value when present
- `collection_time`: UTC-aware timestamp captured by the collector
- `source_time`: UTC-aware timestamp when explicitly present in the payload
- `is_historical`: `False`
- `evidence_status`: `VERIFIED`

No other XML element names are inferred from guesswork.

## XML parsing policy

This task supports only explicit payload fields that are documented or already captured in existing project evidence. If a field is not sufficiently documented, it remains unmapped rather than guessed.

## Error handling

The collector and XML client must treat malformed XML and empty responses conservatively:

- malformed XML: reject and classify as malformed or invalid payload
- empty response: handle as `EmptyResponse` and do not interpret as an inventory/performance snapshot
- unverified response class: reject as invalid

## Non-goals

The following are intentionally excluded from this task:

- live NFM-P connectivity
- authentication implementation
- registerLogToFile production implementation
- historical LogRecord persistence
- TimescaleDB / ORM / repository changes
- production scheduling
- unsupported XML API classes

## Remaining evidence gaps

- exact XML element names beyond the verified operation contract and the explicitly documented current-data classes are not yet available in the supplied evidence for all performance payloads
- the current task intentionally leaves unsupported fields unmapped rather than guessing
- additional classes should be added only after direct vendor evidence confirms their exact operation name, request schema, and response structure
