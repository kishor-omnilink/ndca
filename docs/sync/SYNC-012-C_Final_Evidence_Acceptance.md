# SYNC-012-C — Final Evidence Reconciliation & Acceptance

## 1. Purpose

SYNC-012-C consolidates the remaining NFM-P performance API and evidence
coverage after completion of SYNC-012-B.3 Kafka BGP Performance Collector.

The purpose of this milestone is evidence reconciliation and acceptance
classification. It does not authorize speculative implementation for
domains where the NFM-P XML/API contract remains incomplete or unknown.

---

## 2. Scope

SYNC-012-C covers the remaining performance domains identified during
SYNC-012 performance API discovery and evidence review.

The following principles apply:

- Exact NFM-P API/class evidence is required before implementation.
- Telemetry discovery alone does not establish an NFM-P XML API contract.
- CurrentData evidence does not automatically establish LogRecord evidence.
- Accounting statistics must not be treated as CurrentData.
- Unknown mappings remain UNKNOWN.
- Partial mappings remain PARTIAL.
- Missing evidence is not permission to infer.
- OSPF is explicitly excluded from this project scope.

---

## 3. Frozen Acceptance Matrix

| Domain | Evidence Status | Acceptance | Implementation Decision | Remaining Gap |
|---|---|---|---|---|
| Interface | VERIFIED | ACCEPTED | READY | None for current scope |
| BGP | CLOSED | ACCEPTED / CLOSED | READY / CLOSED | None |
| MPLS Interface | VERIFIED | ACCEPTED | READY | None for current scope |
| MPLS LSP Egress | PARTIAL | CONDITIONAL | DEFERRED | Historical/LogRecord contract |
| MPLS LSP Ingress Accounting | PARTIAL | CONDITIONAL | DEFERRED | Exact accounting XML/retrieval contract |
| MPLS LSP Egress Accounting | PARTIAL | CONDITIONAL | DEFERRED | Exact accounting XML/retrieval contract |
| MPLS/IP Interface | UNKNOWN | NOT ACCEPTED | DEFERRED | Exact NFM-P XML class |
| MPLS DM | PARTIAL | CONDITIONAL | DEFERRED | Complete accounting/historical contract |
| IS-IS Service | UNKNOWN | NOT ACCEPTED | DEFERRED | Exact XML performance class |
| IS-IS Interface | UNKNOWN | NOT ACCEPTED | DEFERRED | Exact XML performance class |
| IS-IS LFA | UNKNOWN | NOT ACCEPTED | DEFERRED | Exact XML performance class |
| CFM DMM | UNVERIFIED | NOT ACCEPTED | DEFERRED | No authoritative saspm accounting evidence |
| CFM LMM | UNVERIFIED | NOT ACCEPTED | DEFERRED | No authoritative saspm accounting evidence |
| CFM SLM | UNVERIFIED | NOT ACCEPTED | DEFERRED | No authoritative saspm accounting evidence |
| IP Interface | VERIFIED | ACCEPTED | READY | None for current scope |
| IP Additional | VERIFIED CurrentData / PARTIAL historical | CONDITIONAL | CurrentData READY; historical DEFERRED | Exact historical/LogRecord class |
| SAR IP | PARTIAL | CONDITIONAL | DEFERRED | Historical/API contract |
| TWL | UNVERIFIED | NOT ACCEPTED | DEFERRED | No authoritative saspm accounting evidence |
| OSPF | EXCLUDED | EXCLUDED | N/A | Explicitly out of scope |

---

## 4. Accepted / Implementation-Ready Domains

The following domains have sufficient evidence for the current scope:

1. Interface
2. BGP
3. MPLS Interface
4. IP Interface

BGP is already closed under SYNC-012-B.3 and must not be reopened as
part of SYNC-012-C.

---

## 5. Interface Additional

The authoritative CurrentData class is:

    equipment.InterfaceAdditionalStats

This class is established by the existing discovery, implementation and
test evidence.

The remaining gap is the historical/LogRecord representation.

Therefore:

- CurrentData: VERIFIED / READY
- Historical LogRecord: PARTIAL / DEFERRED

No additional CurrentData discovery is required for this domain.

---

## 6. PARTIAL / DEFERRED Domains

### 6.1 MPLS LSP Egress

The performance/statistics class has been identified, but the complete
historical/LogRecord relationship is not sufficiently established.

Required before implementation:

- exact historical/log class
- request structure
- response structure
- required fields
- monitored LSP/object identity

Status: PARTIAL / DEFERRED.

### 6.2 MPLS LSP Ingress Accounting

The accounting/statistics identity has been identified, but the complete
NFM-P XML accounting retrieval contract remains incomplete.

Required:

- exact accounting XML class
- retrieval operation
- request
- response
- fields
- object identity

Status: PARTIAL / DEFERRED.

### 6.3 MPLS LSP Egress Accounting

The accounting/statistics identity has been identified, but the complete
NFM-P XML accounting retrieval contract remains incomplete.

Status: PARTIAL / DEFERRED.

### 6.4 MPLS DM

MPLS DM evidence is incomplete at the accounting/historical contract level.

Required before implementation:

- exact accounting contract
- fields
- session identity
- bin identity where applicable
- historical representation

Status: PARTIAL / DEFERRED.

### 6.5 SAR IP

The SAR IP performance/statistics area remains incomplete at the
historical/API contract level.

Status: PARTIAL / DEFERRED.

---

## 7. UNKNOWN / NOT ACCEPTED Domains

### 7.1 MPLS/IP Interface

No exact NFM-P XML performance class has been established.

Status: UNKNOWN / DEFERRED.

### 7.2 IS-IS Service

No exact NFM-P XML performance class has been established.

Status: UNKNOWN / DEFERRED.

### 7.3 IS-IS Interface

No exact NFM-P XML performance class has been established.

Status: UNKNOWN / DEFERRED.

### 7.4 IS-IS LFA

No exact NFM-P XML performance class has been established.

Status: UNKNOWN / DEFERRED.

No topology/inventory class is to be substituted for an IS-IS performance
class.

---

## 8. CFM Evidence Gaps

### CFM DMM

The repository contains session-level CFM references, but no authoritative
performance/accounting evidence sufficient to establish the proposed
saspm accounting contract.

Status: UNVERIFIED / DEFERRED.

### CFM LMM

No authoritative performance/accounting contract is currently evidenced.

Status: UNVERIFIED / DEFERRED.

### CFM SLM

No authoritative performance/accounting contract is currently evidenced.

Status: UNVERIFIED / DEFERRED.

No implementation is authorized for these domains under SYNC-012-C.

---

## 9. TWL Evidence Gap

TWL session-level evidence exists, but the proposed accounting/performance
contract is not sufficiently evidenced in the current repository.

Status: UNVERIFIED / DEFERRED.

No implementation is authorized under SYNC-012-C.

---

## 10. Evidence Gap Register

| ID | Domain | Status | Required Closure Evidence |
|---|---|---|---|
| EG-001 | MPLS LSP Egress | PARTIAL | Historical/LogRecord class and complete retrieval contract |
| EG-002 | MPLS LSP Ingress Accounting | PARTIAL | Exact XML accounting class, retrieval, request/response and fields |
| EG-003 | MPLS LSP Egress Accounting | PARTIAL | Exact XML accounting class, retrieval, request/response and fields |
| EG-004 | MPLS/IP Interface | UNKNOWN | Exact NFM-P XML performance class and retrieval evidence |
| EG-005 | MPLS DM | PARTIAL | Complete accounting/historical contract |
| EG-006 | IS-IS Service | UNKNOWN | Exact NFM-P XML performance class |
| EG-007 | IS-IS Interface | UNKNOWN | Exact NFM-P XML performance class |
| EG-008 | IS-IS LFA | UNKNOWN | Exact NFM-P XML performance class |
| EG-009 | CFM DMM | UNVERIFIED | Authoritative performance/accounting API evidence |
| EG-010 | CFM LMM | UNVERIFIED | Authoritative performance/accounting API evidence |
| EG-011 | CFM SLM | UNVERIFIED | Authoritative performance/accounting API evidence |
| EG-012 | IP Additional historical | PARTIAL | Exact historical/LogRecord class |
| EG-013 | SAR IP | PARTIAL | Complete historical/API contract |
| EG-014 | TWL | UNVERIFIED | Authoritative performance/accounting API evidence |

---

## 11. Documentation Drift Register

### DD-001 — CFM/TWL Evidence Drift

Historical activity documentation contains session-level references for
CFM and TWL, but the current SYNC-012 evidence set does not contain
corresponding authoritative performance/accounting evidence.

Disposition: DEFERRED.

### DD-002 — Interface Additional Historical Mapping

The CurrentData class `equipment.InterfaceAdditionalStats` is established,
but the exact historical/LogRecord class remains unspecified.

Disposition: DEFERRED.

Documentation Drift items are recorded for later cleanup and are not to
be corrected as part of the SYNC-012-C evidence-freeze activity.

---

## 12. Explicit Exclusion

### OSPF

OSPF is not used by the target environment and is explicitly excluded from
SYNC-012-C and subsequent performance collector implementation.

No OSPF discovery, mapping or implementation work is required.

---

## 13. Implementation Rules After Freeze

The following rules are frozen:

1. Do not infer an NFM-P XML class from a telemetry name.
2. Do not substitute topology/inventory classes for performance classes.
3. Do not treat CurrentData evidence as proof of historical LogRecord
   support.
4. Do not treat accounting statistics as CurrentData.
5. Do not implement UNKNOWN mappings.
6. Do not implement PARTIAL mappings until the missing contract evidence
   is obtained.
7. Do not reopen SYNC-012-B.3 BGP implementation.
8. Do not introduce code changes solely to close an evidence gap.
9. OSPF remains excluded.

---

## 14. SYNC-012-C Closure Statement

SYNC-012-C — Final Evidence Reconciliation is COMPLETE from the currently
available repository evidence.

The SYNC-012 performance-domain acceptance matrix has been frozen.

Interface, BGP, MPLS Interface and IP Interface have sufficient evidence
for acceptance/implementation readiness, with BGP already closed under
SYNC-012-B.3.

Remaining MPLS, CFM/TWL, IS-IS, SAR-IP and historical Interface Additional
gaps are explicitly classified as PARTIAL, UNKNOWN or UNVERIFIED and
remain DEFERRED.

No implementation shall be initiated for these domains until the required
NFM-P API/accounting evidence is obtained.

OSPF is explicitly excluded from scope.

Documentation Drift items identified during reconciliation are recorded
for later cleanup and are not to be modified as part of SYNC-012-C.

---

## 15. Recommended Follow-On Work

Future evidence work should be handled as a separate milestone or
explicit evidence task.

Recommended order:

1. Historical Interface Additional contract
2. MPLS LSP Egress historical contract
3. MPLS LSP accounting
4. MPLS DM
5. SAR IP
6. MPLS/IP Interface
7. IS-IS performance domains
8. CFM DMM/LMM/SLM
9. TWL

No speculative implementation should precede contract closure.

---

## 16. Final Status

**SYNC-012-C: EVIDENCE RECONCILIATION COMPLETE / ACCEPTANCE MATRIX FROZEN**

Implementation-ready domains:

- Interface
- BGP
- MPLS Interface
- IP Interface

All other unresolved domains remain explicitly deferred pending
authoritative evidence.
