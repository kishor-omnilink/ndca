# Project State Document

## OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD

**Branch / Workstream:** `feature/sync-012-b-performance-collector`
**Document Type:** Project State / Baseline Reference
**State Date:** 21 August 2026
**Status:** **Active — SYNC-012-D.1 Historical Evidence Reconciliation / D.8 Foundation Validation**
**Primary Technology Domain:** Nokia NSP / NFM-P / NFM-T, IP/MPLS, Grafana, PostgreSQL, TimescaleDB

---

## 1. Executive Project State

The **OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD** project is intended to provide a custom operational, historical, performance and management dashboard for the Nokia IP/MPLS environment.

The project originated from the **Network Requirement Analysis** workstream, where the primary objective was to determine:

- What information is available from Nokia NSP/NFM-P/NFM-T.
- Which APIs should be used to collect the required data.
- Which data should be synchronized into a local database.
- How historical and performance information should be retained.
- How the synchronized information should be presented through Grafana.
- How the solution should support NOC, operations and management users.
- How the solution can scale beyond the initial monitored environment.

The current design direction is a **local data synchronization architecture** rather than making Grafana directly dependent on live NSP APIs for every dashboard query.

The target architecture is therefore:

**Nokia NSP / NFM-P / NFM-T → Data Collector / Adapter → PostgreSQL + TimescaleDB → Grafana → Custom Dashboards / Reports**

The project has progressed from requirements/architecture planning into implementation and evidence-validation work. SYNC-012-A performance API discovery, SYNC-012-B.2 interface current-data collection, SYNC-012-B.3 Kafka BGP performance collection, and SYNC-012-C final evidence reconciliation have been completed. The current active workstream is SYNC-012-D.1, focused on closing the remaining historical evidence gap for `equipment.InterfaceAdditionalStats`. The project is not yet production-ready.

---

# 2. Project Objectives

The project objectives are:

1. Build a custom dashboard specifically for the OCAC IP/MPLS environment.
2. Collect required network inventory and operational information from Nokia NSP.
3. Collect performance and historical information where supported.
4. Synchronize collected information into a local PostgreSQL/TimescaleDB database.
5. Decouple dashboard queries from direct NSP API dependency.
6. Provide historical trend analysis.
7. Provide operational dashboards for NOC and operations teams.
8. Provide management-oriented KPI views.
9. Support periodic synchronization.
10. Provide a scalable architecture that can accommodate additional network elements and data types.
11. Establish a reusable data model for future reports and analytics.

---

# 3. Confirmed Functional Direction

The following requirements have been established during the Network Requirement Analysis.

| Area | Current Decision / Requirement |
|---|---|
| Source platform | Nokia NSP |
| Primary network domain | IP/MPLS |
| NFM-P | Required source for applicable network/service data |
| NFM-T | To be considered/validated for applicable telemetry/performance data |
| Local database | PostgreSQL |
| Time-series storage | TimescaleDB |
| Visualization | Grafana |
| Synchronization model | Periodic synchronization into local DB |
| Initial refresh target | 15 minutes |
| Historical data | Required |
| Performance data | Required where available through supported APIs |
| Users | NOC Engineers, Operations, Management |
| RBAC | Required |
| Dashboard type | Custom dashboard |
| Reporting | PDF / Excel / CSV |
| Scheduled email reports | Optional future capability |
| Scalability | Initial scope designed to scale |
| Architecture principle | Local data layer between NSP and Grafana |

---

# 4. High-Level Architecture

The target logical architecture is:

```text
                    Nokia NSP Environment
                           │
              ┌────────────┴────────────┐
              │                         │
           NFM-P                     NFM-T
              │                         │
              └────────────┬────────────┘
                           │
                     REST/API Layer
                           │
                           ▼
                ┌─────────────────────┐
                │  Data Collector /   │
                │  Synchronization    │
                │      Service        │
                └──────────┬──────────┘
                           │
                    Transform / Validate
                           │
                           ▼
                ┌─────────────────────┐
                │ PostgreSQL          │
                │ +                   │
                │ TimescaleDB         │
                └──────────┬──────────┘
                           │
                    SQL / Time-series
                           │
                           ▼
                ┌─────────────────────┐
                │      Grafana        │
                │                     │
                │ Operational         │
                │ Historical          │
                │ Performance         │
                │ KPI / Management    │
                └─────────────────────┘
```

This architecture provides separation between:

- Data acquisition
- Data normalization
- Data persistence
- Time-series retention
- Visualization
- Reporting

---

# 5. Data Synchronization Strategy

The preferred approach is to periodically pull information from NSP and store it locally.

The target synchronization interval identified during requirements analysis is:

**15 minutes**

The synchronization process should distinguish between different classes of data.

### 5.1 Inventory Data

Examples:

- Network elements
- Router identity
- Management address
- Device type
- Software version
- Administrative state
- Operational state
- Site/location
- Equipment hierarchy
- Cards/slots
- Ports/interfaces
- Logical interfaces
- Service-related inventory where required

Inventory data does not necessarily require the same polling frequency as performance data.

### 5.2 Operational State

Examples:

- Node availability
- Reachability
- Administrative state
- Operational state
- Interface state
- Alarm/state information
- Service state where exposed through the API

### 5.3 Performance Data

Potential categories include:

- Interface traffic
- Utilization
- Input/output rates
- Packet statistics
- Error/discard statistics
- MPLS-related performance
- Service performance
- Other KPIs exposed by NSP

The exact performance dataset must be finalized against the APIs available in the deployed NSP release.

### 5.4 Historical Data

Historical information should be retained in TimescaleDB so that Grafana can efficiently provide:

- Hourly trends
- Daily trends
- Weekly trends
- Monthly trends
- Capacity trends
- Utilization trends
- Historical comparison

---

# 6. Database Strategy

The database architecture is:

**PostgreSQL + TimescaleDB**

PostgreSQL is the primary relational database.

TimescaleDB is intended to provide optimized storage and querying for time-series/performance information.

The database should logically separate:

```text
Inventory
    │
    ├── Network Elements
    ├── Equipment
    ├── Interfaces
    ├── Services
    └── Locations

Operational State
    │
    ├── Node State
    ├── Interface State
    └── Service State

Performance
    │
    ├── Interface Metrics
    ├── Network Metrics
    ├── Service Metrics
    └── Other KPIs

Synchronization
    │
    ├── Collection Runs
    ├── API Status
    ├── Errors
    └── Data Quality

Reporting
    │
    └── Dashboard / KPI datasets
```

The database should become the stable data contract between the collector and Grafana.

---

# 7. Grafana Strategy

Grafana is intended to provide the visualization and analytics layer.

The dashboards should not be designed as a single large dashboard.

A dashboard hierarchy should be used.

### Level 1 — Management / Executive

Possible information:

- Total network elements
- Network availability
- Major alarms
- Overall utilization
- Top congested links
- Service health
- Availability trend
- Capacity trend

### Level 2 — NOC Operations

Possible information:

- Node status
- Interface status
- Active alarms
- Top utilization
- Failed/unstable nodes
- Failed interfaces
- Service status
- Recent events

### Level 3 — Network Element

Possible information:

- Individual router status
- Interface inventory
- Interface utilization
- Traffic trend
- Errors/discards
- Alarms
- Historical availability

### Level 4 — Performance / Analytics

Possible information:

- Interface utilization trends
- Traffic growth
- Capacity analysis
- Top N links
- Historical comparison
- Peak utilization
- SLA/KPI analysis

---

# 8. User / RBAC Model

RBAC is a confirmed requirement.

The expected user categories are:

### NOC Engineer

Access to:

- Operational dashboards
- Network health
- Alarms
- Node status
- Interface status
- Current performance

### Operations User

Access to:

- NOC dashboards
- Historical performance
- Capacity information
- Device-level analytics
- Service-level information

### Management

Access to:

- Executive dashboards
- High-level KPIs
- Availability
- Capacity
- Major incidents
- Historical trends
- Management reports

The final authorization model remains to be mapped against the organizational/user hierarchy.

---

# 9. Reporting Requirements

The project requirements identified the following report formats:

- PDF
- Excel
- CSV

Potential reporting areas include:

- Network availability
- Device inventory
- Interface inventory
- Utilization
- Capacity
- Top-N utilization
- Service health
- Historical performance
- SLA/KPI information

Scheduled email delivery has been identified as an **optional future capability**, rather than a mandatory initial dependency.

---

# 10. API Verification Requirement

One of the most important unresolved areas is API capability verification.

The implementation must verify the APIs exposed by the deployed Nokia NSP releases, particularly:

- NFM-P 24.4
- NFM-T 24.12

The verification needs to establish:

1. Which APIs are available.
2. Which APIs provide inventory.
3. Which APIs provide operational state.
4. Which APIs provide alarms/events.
5. Which APIs provide performance data.
6. Which APIs provide historical information.
7. Which APIs provide service information.
8. Pagination behaviour.
9. Filtering capabilities.
10. Maximum query size.
11. Authentication mechanism.
12. API rate/usage limitations.
13. Response structure.
14. Incremental synchronization capability.
15. Whether historical performance must be obtained from another source.

This API matrix is a critical input to the final collector implementation.

---

# 11. Major Design Decisions

The following design decisions have been established.

### Decision 1 — Local Database

A local PostgreSQL database will be used instead of making Grafana depend directly on NSP for every visualization query.

**Reason:** improved query performance, historical retention, analytics capability and reduced dashboard dependency on NSP API availability.

### Decision 2 — TimescaleDB

TimescaleDB will be used for time-series/performance data.

**Reason:** efficient storage and querying of high-volume timestamped network telemetry/performance information.

### Decision 3 — Grafana

Grafana will be used as the primary visualization platform.

### Decision 4 — Periodic Synchronization

Data will be synchronized periodically.

**Initial target:** 15 minutes.

### Decision 5 — Historical Data

Historical and performance data will be retained locally where the source API provides the required information.

### Decision 6 — Separate Collection and Visualization

The collector and Grafana should remain independent.

```text
NSP API
   ↓
Collector
   ↓
Database
   ↓
Grafana
```

Grafana should not contain the NSP integration logic.

---

# 12. Implementation Direction

The implementation is expected to follow these logical components:

```text
collector/
    ├── authentication
    ├── inventory
    ├── operational
    ├── performance
    ├── alarms
    └── services

database/
    ├── models
    ├── repositories
    ├── migrations
    └── time-series

scheduler/
    ├── inventory sync
    ├── state sync
    └── performance sync

grafana/
    ├── dashboards
    ├── variables
    ├── queries
    └── alert/KPI views
```

The collector should include proper handling for:

- API authentication
- Connection failures
- HTTP errors
- Invalid responses
- Timeouts
- Pagination
- Retry
- Logging
- Synchronization status
- Data validation
- Duplicate prevention
- Partial synchronization
- Auditability

---

### SYNC-012-D.1 Evidence Boundary

The current evidence establishes:

- `equipment.InterfaceAdditionalStats` as a verified current-data class.
- Generic `findToFile` as a documented historical retrieval operation.
- A reusable `findToFile` request-construction implementation with validation and XML escaping.
- Passing D.8/performance collector tests and SYNC-012-A API discovery tests.

The current evidence does **not** establish:

- The exact historical Interface Additional LogRecord class.
- The historical LogRecord attributes.
- The exact historical XML response structure.
- The historical response-to-`PerformanceRecord` mapping.

Therefore no historical Interface Additional collector or persistence implementation is authorized until authoritative evidence closes the gap.


# 13. Current Project State

| Workstream | State | Assessment |
|---|---|---|
| Requirement analysis | **Substantially completed** | Core objectives and requirements established |
| Architecture | **Defined** | NSP → Collector → PostgreSQL/TimescaleDB → Grafana |
| Database direction | **Defined** | PostgreSQL + TimescaleDB |
| Visualization platform | **Defined** | Grafana |
| Refresh frequency | **Defined** | 15 minutes |
| User groups | **Defined** | NOC / Operations / Management |
| RBAC | **Required** | Detailed mapping pending |
| Inventory requirements | **Partially defined** | Broader API/data mapping remains |
| Performance requirements | **Partially validated** | SYNC-012 performance API discovery completed; remaining evidence gaps tracked |
| Historical storage | **Defined conceptually** | Exact historical contracts/retention remain domain-dependent |
| NFM-P performance API discovery | **Completed for SYNC-012-A** | Documented performance classes and evidence captured |
| NFM-T/Kafka data path | **Established** | Existing collection/data-flow baseline is available |
| Database schema | **Design stage** | Final schema required |
| Collector | **Implementation in progress** | SYNC-012-B current-data/BGP work completed; D.1 historical evidence remains open |
| D.8 generic `findToFile` foundation | **Implemented / Verified** | Generic historical retrieval request builder tested without inventing a LogRecord class |
| SYNC-012-D.1 | **OPEN** | Exact historical Interface Additional LogRecord contract remains unverified |
| Grafana dashboards | **Design stage** | Requires finalized data contract |
| Reporting | **Requirement identified** | Detailed report definitions pending |
| Security | **To be finalized** | Authentication/RBAC/API security |
| Production deployment | **Not yet finalized** | Dependent on implementation and validation completion |

## 13.1 SYNC-012 Milestone State

The current SYNC-012 milestone position is:

```text
SYNC-012-A  COMPLETE
     ↓
SYNC-012-B.2 COMPLETE
     ↓
SYNC-012-B.3 COMPLETE / CLOSED
     ↓
SYNC-012-C   COMPLETE / CLOSED
     ↓
SYNC-012-D.1 IN PROGRESS
     │
     ├── D.1.1 Evidence reconciliation: COMPLETE
     ├── D.1.2 Historical XML parser: COMPLETE
     ├── D.1.3 Historical normalization: NEXT
     ├── Historical persistence: PENDING
     └── Live historical collection: PENDING
```

### SYNC-012-D.1 Evidence Boundary

Current verified foundation:

* `equipment.InterfaceAdditionalStats`: VERIFIED for CurrentData
* Generic `findToFile`: VERIFIED
* `findToFile` request builder: IMPLEMENTED / TESTED
* `equipment.InterfaceAdditionalStatsLogRecord`: VERIFIED at the captured XML evidence boundary
* Historical metadata fields: VERIFIED at the captured XML evidence boundary
* Historical Interface Additional metric source names: VERIFIED at the captured XML evidence boundary
* Historical raw XML parser: IMPLEMENTED / TESTED
* Multiple historical LogRecords: VERIFIED
* Required historical record validation: VERIFIED

D.1.2 validation:

```text
tests/test_sync_012_b_performance_collector_impl.py
26 passed
```

Previously established regression validation:

```text
SYNC-012-B.2       10 passed
SYNC-012-B.3        7 passed
SYNC-012-B.3 evidence
                    7 passed
```

### Historical Parser Boundary

The historical parser establishes the raw representation:

```text
NFM-P findToFileResponse
        ↓
equipment.InterfaceAdditionalStatsLogRecord
        ↓
raw historical record
        ↓
exact Nokia source field names preserved
```

The parser does not perform:

* metric normalization
* `PerformanceRecord` construction
* database persistence
* live historical collection

### D.1.3 Next Boundary

The next implementation stage is:

**SYNC-012-D.1.3 — Historical Interface Additional Normalization**

D.1.3 must establish an explicit, tested mapping from the verified Nokia historical source fields to the NDCA `PerformanceRecord` contract.

The mapping must explicitly define:

* metric names
* metric semantics
* timestamp handling
* object identity
* counter versus periodic-counter handling
* validation rules

No source field should be silently renamed or discarded at the raw parsing boundary.

### Current SYNC-012-D.1 Status

**D.1.1 — COMPLETE**

**D.1.2 — COMPLETE**

**D.1.3 — NEXT**

**D.1 overall — IN PROGRESS**

Historical persistence and live end-to-end NFM-P historical retrieval remain pending.

# 14. Outstanding Work

The following work should be treated as the next major project activities.

## A. SYNC-012-D.1 — Interface Additional Historical Performance

### Current Status

**IN PROGRESS — D.1.2 COMPLETE; D.1.3 NEXT**

### Completed

* Historical Interface Additional evidence boundary reconciled.
* `equipment.InterfaceAdditionalStatsLogRecord` verified at the captured XML evidence boundary.
* Historical XML structure established.
* Historical metadata fields established.
* Historical Interface Additional metric source names established.
* Namespace-safe historical parser implemented.
* Multiple historical records supported.
* Required historical identity/time validation implemented.
* D.8 `findToFile` foundation reused.
* D.1.2 implementation tests completed successfully.

### Validation

```text
D.1.2 implementation:
26 passed

B.2 regression:
10 passed

B.3 regression:
7 passed

B.3 evidence regression:
7 passed

git diff --check:
PASS
```

### Remaining

1. D.1.3 historical source-to-`PerformanceRecord` normalization.
2. Explicit timestamp semantics.
3. Explicit counter/periodic-counter semantics.
4. Historical object identity mapping.
5. Normalized-record regression tests.
6. Live NFM-P historical collection validation.
7. Historical persistence validation.
8. End-to-end historical performance pipeline validation.

### Evidence Rule

The D.1.2 parser contract is verified against captured repository XML evidence.

This does not constitute live NFM-P end-to-end validation.

OEM-document provenance must not be claimed beyond the evidence actually preserved in the repository.

### Next Deliverable

**SYNC-012-D.1.3 — Historical Interface Additional normalization into the NDCA `PerformanceRecord` contract.**

## B. API Capability Matrix

Create a definitive matrix for the remaining broader API/data coverage:

| Data Type | Required | NFM-P API | NFM-T API | Method | Frequency | DB Target |
|---|---|---|---|---|---|---|
| Network Element Inventory | Yes | TBD | TBD | TBD | 15 min / periodic | Inventory |
| Equipment Inventory | Yes | TBD | TBD | TBD | Periodic | Inventory |
| Interface Inventory | Yes | TBD | TBD | TBD | Periodic | Inventory |
| Node State | Yes | TBD | TBD | TBD | 15 min | State |
| Interface State | Yes | TBD | TBD | TBD | 15 min | State |
| Alarms | Yes | TBD | TBD | TBD | TBD | Events |
| Interface Performance | Yes | TBD | TBD | TBD | TBD | TimescaleDB |
| Service Performance | TBD | TBD | TBD | TBD | TBD | TimescaleDB |
| Historical Performance | Yes | TBD | TBD | TBD | TBD | TimescaleDB |

This matrix should be completed before finalizing the collector.

---

# 15. Data Model Finalization

The next design stage should define the canonical database model.

At minimum:

```text
network_element
interface
equipment
service
alarm/event
inventory_snapshot
operational_state
performance_metric
synchronization_run
synchronization_error
```

The model should distinguish:

- Current-state tables
- Historical tables
- Time-series tables
- Reference/master tables
- Synchronization/audit tables

---

# 16. Synchronization Model

The collector should maintain synchronization state.

A recommended logical flow is:

```text
START
  │
  ▼
Authenticate to NSP
  │
  ▼
Start synchronization run
  │
  ▼
Collect data
  │
  ├── Success ───────┐
  │                  │
  └── Error          │
       │             │
       ▼             │
    Log error        │
       │             │
       └─────────────┤
                     ▼
             Validate data
                     │
                     ▼
              Transform data
                     │
                     ▼
               Store in DB
                     │
                     ▼
             Record sync status
                     │
                     ▼
                    END
```

A failed or incomplete API response must not automatically be interpreted as the absence of network elements.

This is particularly important for inventory synchronization and prevents accidental mass deletion/deactivation caused by incomplete snapshots.

---

# 17. Performance Data Considerations

Performance data should be designed separately from inventory data.

For example:

```text
metric_timestamp
network_element_id
interface_id
metric_name
metric_value
unit
source
collection_time
```

TimescaleDB can then be used for efficient time-range queries.

Grafana can use these datasets for:

- Last 1 hour
- Last 6 hours
- Last 24 hours
- Last 7 days
- Last 30 days
- Custom historical period

---

# 18. Risks / Dependencies

### API Dependency

The most significant dependency is confirmation of the APIs available in the actual deployed NSP releases.

### Data Semantics

An API returning data does not automatically mean the data is suitable for historical analytics. Metric semantics, units, timestamps and aggregation behaviour must be validated.

### Data Volume

Performance polling at 15-minute intervals can generate significant data volume as the number of interfaces and metrics increases.

### Historical Retention

Retention policies must be established before production deployment.

### API Load

The collector must avoid unnecessarily expensive queries against NSP.

### Partial Responses

Incomplete API responses must be handled safely.

### Dashboard Dependency

Grafana dashboards should depend on the stable local data model rather than raw NSP API response structures.

---

# 19. Recommended Milestone Structure

The project should be controlled through explicit milestones.

### M0 — Project Baseline

- Scope
- Objectives
- Stakeholders
- Architecture principles
- Technology selection

**State:** Completed / established.

### M1 — Network Requirement Analysis

- Functional requirements
- Data requirements
- User requirements
- Reporting requirements
- Performance requirements

**State:** Substantially completed.

### M2 — NSP API Capability Validation

- NFM-P API inventory
- NFM-P operational APIs
- NFM-P performance APIs
- NFM-T API validation
- Authentication
- Pagination
- API limits

**State:** **In progress — performance API discovery completed for SYNC-012-A; broader capability/data mapping remains.**

### M3 — Data Model & Database Design

- PostgreSQL schema
- TimescaleDB hypertables
- Retention
- Indexes
- Aggregation strategy

**State:** Design stage.

### M4 — Collector Implementation

- Authentication
- Inventory collector
- State collector
- Alarm collector
- Performance collector
- Scheduler
- Error handling
- Synchronization audit

**State:** **In progress — SYNC-012-B implementation foundation established; remaining historical evidence gaps are tracked under SYNC-012-D.1.**

### M5 — Grafana Dashboard Implementation

- Executive dashboard
- NOC dashboard
- Network-element dashboard
- Performance dashboard
- Historical dashboards
- RBAC

**State:** Pending finalized data contract.

### M6 — Reporting

- PDF
- Excel
- CSV
- Scheduled reports

**State:** Future implementation stage.

### M7 — Integration / FAT

- End-to-end collection
- Database validation
- Dashboard validation
- Performance validation
- Failure/recovery testing

**State:** Pending.

### M8 — UAT / Production

- UAT
- Security validation
- Performance validation
- Documentation
- Production handover

**State:** Pending.

---

# 20. Project Baseline

The project should currently be treated as:

> **Architecture direction established, core requirements substantially identified, SYNC-012 performance API/collector work materially advanced, and the current active implementation/evidence task is SYNC-012-D.1. The solution is not production-ready until remaining API/data contracts, canonical data model, validation and deployment work are finalized.**

The most important immediate activity is therefore **not dashboard development**. The immediate focus is closing evidence-backed data contracts and then progressing the remaining implementation stages.

The current dependency chain is:

```text
Requirements / Architecture
          ↓
API Capability & Evidence Validation
          ↓
Canonical Data Model
          ↓
Collector / Synchronization
          ↓
Database Validation
          ↓
Grafana Data Contract
          ↓
Dashboard Development
          ↓
Reporting
          ↓
FAT
          ↓
UAT
          ↓
Production
```

Current SYNC-012 position:

```text
SYNC-012-A  COMPLETE
     ↓
SYNC-012-B.2 COMPLETE
     ↓
SYNC-012-B.3 COMPLETE / CLOSED
     ↓
SYNC-012-C   COMPLETE / CLOSED
     ↓
SYNC-012-D.1 OPEN
     │
     ├── CurrentData class: VERIFIED
     ├── Generic findToFile: VERIFIED
     ├── Historical LogRecord class: UNKNOWN
     ├── Historical attributes: UNKNOWN
     └── Historical mapping/implementation: BLOCKED BY EVIDENCE
```

# 21. Current State Summary

**Project:** `OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD`

**Branch:** `feature/sync-012-b-performance-collector`

**State date:** **21 August 2026**

**Current phase:** **SYNC-012-D.1 — Interface Additional Historical Evidence Reconciliation**

**Architecture:**
**Nokia NSP → Collector/Adapter → PostgreSQL + TimescaleDB → Grafana**

**Completed SYNC-012 baseline:**
- SYNC-012-A — NFM-P Performance API Discovery: **COMPLETE**
- SYNC-012-B.2 — Interface Current Data: **COMPLETE**
- SYNC-012-B.3 — Kafka BGP Performance Collector: **COMPLETE / CLOSED**
- SYNC-012-C — Final Evidence Reconciliation / Acceptance: **COMPLETE / CLOSED**

**Current active milestone:**
**SYNC-012-D.1 — Interface Additional Historical Evidence Gap: OPEN**

**Current verified foundation:**
- `equipment.InterfaceAdditionalStats`: **VERIFIED** for CurrentData
- Generic `findToFile`: **VERIFIED**
- Generic `findToFile` request builder: **IMPLEMENTED / TESTED**
- D.8/performance collector tests: **33 passed**
- SYNC-012-A API discovery tests: **12 passed**
- Python compile check: **PASS**

**Primary unresolved dependency:**
**Authoritative historical/LogRecord contract for `equipment.InterfaceAdditionalStats`, including class name, attributes, response structure and NDCA field mapping.**

**Implementation restriction:**
No historical Interface Additional LogRecord collector or persistence implementation may be added until the missing historical contract is established from authoritative evidence.

**Primary next deliverable:**
**Authoritative evidence closure for SYNC-012-D.1, followed by evidence-backed historical mapping/implementation only if the contract is verified.**

**Secondary project deliverables:**
**Canonical PostgreSQL/TimescaleDB Data Model, broader API/data mapping, dashboard/reporting implementation, FAT, UAT and production readiness.**

**Implementation principle:**
Build the collector and dashboard against a controlled local data model rather than coupling Grafana directly to NSP APIs, and never infer unsupported historical API contracts.

**Overall state:**
**ACTIVE — SYNC-012-D.1 EVIDENCE RECONCILIATION / D.8 FOUNDATION VERIFIED / HISTORICAL INTERFACE ADDITIONAL CONTRACT OPEN**

# 22. Change Control

This document is the current project-state baseline for the `OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD` workstream as of 21 August 2026.

Future project discussions should update this baseline when any of the following changes:

- NSP release/API capability
- Data source
- Database architecture
- Dashboard platform
- Synchronization frequency
- User/RBAC model
- Historical retention
- Performance data strategy
- Project milestone status
- Production architecture

**End of Project State Document**
