# SYNC-012-B.3 — BGP Evidence Handoff

**Date:** 2026-08-18
**Status:** Evidence acquisition required; implementation remains blocked.

## 1. Objective

Unblock SYNC-012-B.3 by obtaining and verifying the exact NFM-P `bgp.PeerStats` current-data response and, separately where required, the exact `bgp.PeerStatsLogRecord` field structure.

## 2. What is already verified

- `bgp.PeerStats` is a verified NFM-P XML API class.
- `bgp.PeerStatsLogRecord` is a verified LogRecord class.
- `generic.GenericObject.triggerCollect` is verified.
- `instanceNames` and `currentDataClasses` are verified request fields.
- Scheduled BGP PeerStats collection and 5-minute polling examples are documented.
- `registerLogToFile` and its generic input structure are verified.
- The repository contains a read-only evidence-capture utility at `src/ndca/api/nfmp_evidence_capture.py`.

## 3. Gate status

### Gate 1 — Request structure

Status: **SUBSTANTIALLY VERIFIED** from vendor documentation and the existing client/evidence utility.

The repository request builder generates:

- `generic.GenericObject.triggerCollect`
- `instanceNames`
- `currentDataClasses`
- `bgp.PeerStats`

Do not treat the local request builder alone as vendor proof; vendor-document evidence remains authoritative.

### Gate 2 — Response structure and mapping

Status: **BLOCKED**.

Required evidence:

1. One real NFM-P `bgp.PeerStats` XML response captured from a representative network element.
2. Exact XML element/attribute names for every BGP field intended for the dashboard.
3. Data type and unit for every selected field.
4. Meaning/semantics of every selected field.
5. Exact source timestamp semantics, if present.
6. Object identity fields used to identify the BGP peer.
7. Evidence for `bgp.PeerStatsLogRecord` fields if historical BGP data will be implemented.

## 4. Evidence acquisition method

Use the existing read-only utility:

`src/ndca/api/nfmp_evidence_capture.py`

The utility is intentionally limited to `bgp.PeerStats`, sends the verified `generic.GenericObject.triggerCollect` request, and stores the raw XML plus metadata without parsing or persisting BGP fields.

Use an already-approved NFM-P endpoint and representative `instanceName` values from the existing project configuration. Do not commit credentials or secrets.

Example shape only:

```text
python -m ndca.api.nfmp_evidence_capture \
  --endpoint <existing-approved-nfmp-endpoint> \
  --instance-name <representative-instance-name> \
  --output-dir docs/sync/evidence
```

The actual endpoint, credentials, and instance names must come from the existing environment/configuration; they are not part of this document.

## 5. Evidence review checklist

For each captured XML response:

- [ ] Request succeeded against NFM-P.
- [ ] Response is the BGP current-data response.
- [ ] XML class is explicitly identifiable as `bgp.PeerStats`.
- [ ] Peer/object identity is identifiable.
- [ ] Every proposed BGP metric has an exact XML name.
- [ ] Every proposed metric has a verified type.
- [ ] Every proposed metric has a verified unit/meaning.
- [ ] Timestamp behavior is understood.
- [ ] No field name is inferred from naming conventions alone.
- [ ] Mapping to the NDCA normalized performance contract is documented.

## 6. Implementation prohibition

Until Gate 2 passes:

- do not implement BGP parsing;
- do not implement BGP production collection;
- do not add BGP ORM fields based on guesses;
- do not create dashboard metrics based on assumed BGP names;
- do not treat generic XML parsing as BGP schema validation.

## 7. Next chat handoff

Use ChatGPT chat:

`21-NFMP API & EVIDENCE`

Prompt:

> Continue SYNC-012-B.3 from the existing repository evidence. Review this handoff and the captured `bgp.PeerStats` evidence. Determine whether Gate 2 can be passed. If evidence is sufficient, produce the exact verified BGP field-to-NDCA mapping and implementation contract. If evidence is insufficient, identify only the remaining missing evidence. Do not implement production code.
