# SYNC-012-A NFM-P Performance API Discovery

## 1. Purpose

This document records the discovery findings for Nokia NFM-P 24.4 performance statistics API access and collection architecture. It is based on evidence from:

- `Statistics_Management_Guide_Issue_1.pdf` (Release 24.4, April 2024, Issue 1)
- `XML_API_Developer_Guide_Issue_1.pdf` (Release 24.4, April 2024, Issue 1)

This milestone is intentionally discovery-only: no NFM-P production performance collector is implemented yet.

## 2. Scope

- NFM-P performance statistics architecture
- Current vs historical statistics
- Scheduled vs on-demand collection
- `registerLogToFile`
- `findToFile`
- `triggerCollect`
- Statistics Search Tool
- Current-data vs LogRecord retrieval models
- Candidate IP/MPLS/router-related performance statistics
- Verified API/class mapping and remaining gaps

## 3. Source documents

- `Statistics_Management_Guide_Issue_1.pdf` (NFM-P 24.4)
- `XML_API_Developer_Guide_Issue_1.pdf` (NFM-P 24.4)

Where exact page numbers are not available in the current evidence summary, source references are marked with the document name and an explicit note stating that exact page numbers should be confirmed from the PDFs.

## 4. Evidence rules

- Use only information explicitly documented in the supplied NFM-P 24.4 documentation.
- Do not invent XML API class names, methods, counter names, endpoints, or statistics fields.
- `VERIFIED` means the documentation explicitly establishes the required API/class/statistic information.
- `PARTIAL` means the documentation establishes the concept, but exact API/class/method detail is incomplete.
- `UNKNOWN` means the documentation does not establish the required information.

## 5. Verified NFM-P performance architecture

The supplied documentation establishes the following architecture:

- NFM-P performance statistics provide categorized information about network throughput. `VERIFIED`
- Performance statistics are SNMP-based and acquired by sending SNMP queries to managed network elements. `VERIFIED`
- Performance statistics are available through XML API classes. `VERIFIED`
- Performance statistics can be scheduled or collected on demand. `VERIFIED`
- The Performance Statistics Search Tool provides device-specific lists of supported MIB-based performance statistics. `VERIFIED`
- Performance statistics record properties include Monitored Object, Monitored Object Name, Periodic Time, Record Type, Site ID, Site Name, Suspect, Time Captured, and Time Logged. `VERIFIED`
- Record types include Scheduled Full and On-demand. `VERIFIED`

## 6. Current vs historical statistics

Verified from the supplied documentation:

- Current data records are used for both scheduled and on-demand statistics. `VERIFIED`
- Historical statistics are available through scheduled collections and can be viewed in tabular or graphical form. `VERIFIED`
- Historical plots use data from scheduled collections. `VERIFIED`
- The last scheduled poll is stored using a LogRecord. `VERIFIED`
- On-demand statistics are current data only and are not equivalent to scheduled historical statistics. `VERIFIED`

## 7. Scheduled vs on-demand collection

Verified distinctions:

- Scheduled collection provides current data and creates historical statistics via LogRecord classes. `VERIFIED`
- On-demand collection uses current statistics and does not create historical LogRecord entries. `VERIFIED`
- Scheduled historical statistics can be viewed in tables or graphs. `VERIFIED`
- Real-time plots collect statistics while the plotter is open. `VERIFIED`

## 8. XML API retrieval mechanisms

The XML API Developer Guide documents that performance statistics objects are organized by package and that current data statistics classes are used for on-demand and scheduled retrieval. `VERIFIED`

The guide also documents that:

- `generic.GenericObject.triggerCollect` is the documented method for on-demand statistics collection. `VERIFIED`
- `triggerCollect` accepts `instanceNames` and `currentDataClasses`. `VERIFIED`
- Example documented classes include `equipment.InterfaceStats` and `equipment.InterfaceAdditionalStats`. `VERIFIED`

## 9. registerLogToFile

Verified documentation from the XML API Developer Guide:

- `registerLogToFile` is documented for continual accounting/performance statistics collection. `VERIFIED`
- It can specify multiple accounting/performance statistics classes. `VERIFIED`
- It generates files and raises `LogFileAvailableEvent`. `VERIFIED`
- It is recommended to minimize collection latency and system load. `VERIFIED`

## 10. findToFile

Verified documentation from the XML API Developer Guide:

- `findToFile` is documented for occasional or infrequent statistics retrieval. `VERIFIED`
- It produces `FileAvailableEvent`. `VERIFIED`
- It is intended for lower-volume retrieval when higher latency is acceptable. `VERIFIED`
- It can be used for fewer than 400,000 statistics records in 15 minutes when greater latency is acceptable. `VERIFIED`

## 11. triggerCollect

Verified documentation from the XML API Developer Guide:

- `generic.GenericObject.triggerCollect` is the documented on-demand collection API. `VERIFIED`
- It accepts `instanceNames` and `currentDataClasses`. `VERIFIED`
- The documented example uses `equipment.InterfaceStats` and `equipment.InterfaceAdditionalStats`. `VERIFIED`

## 12. Statistics Search Tool

Verified from the Statistics Management Guide:

- The Performance Statistics Search Tool provides device-specific lists of supported MIB-based performance statistics. `VERIFIED`
- The tool is used to discover supported monitored objects and performance categories per device. `VERIFIED`

## 13. Current-data vs LogRecord model

Verified model:

- Current data statistics classes deliver real-time or on-demand statistics. `VERIFIED`
- Scheduled collection results are also archived through corresponding `LogRecord` classes. `VERIFIED`
- Historical plots and tables are based on scheduled collection LogRecords. `VERIFIED`
- On-demand statistics are explicitly not equivalent to historical LogRecord data. `VERIFIED`

## 14. Candidate IP/MPLS/router performance statistics

The register contains candidate entries derived from explicit documentation and from categories supported by the supplied guides.

Verified candidate entries include:

- `equipment.InterfaceStats` for interface statistics such as `Received Octets`. `VERIFIED`
- `equipment.InterfaceAdditionalStats` for interface additional statistics such as `Received Broadcast Packets`. `VERIFIED`
- `bgp.PeerStats` for current BGP peer statistics. `VERIFIED`
- `bgp.PeerStatsLogRecord` for historical BGP peer statistics. `VERIFIED`

Partially documented candidate entries include:

- MPLS interface support in default plotter profiles. `PARTIAL` (profile support is documented, exact XML API class names are not documented in the supplied summary evidence)
- Physical equipment status as a performance statistic category. `PARTIAL`
- Routing throughput as a supported performance category. `PARTIAL`

Categories with no explicit XML API class evidence in the supplied summary evidence are currently candidate-only:

- IP
- Ethernet
- OSPF
- IS-IS

## 15. Verified API/class matrix

| API/class | Evidence status | Notes |
|---|---|---|
| `equipment.InterfaceStats` | VERIFIED | Documented current statistics class example in XML API Developer Guide. |
| `equipment.InterfaceAdditionalStats` | VERIFIED | Documented current statistics class example in XML API Developer Guide. |
| `bgp.PeerStats` | VERIFIED | Documented current statistics class in XML API Developer Guide. |
| `bgp.PeerStatsLogRecord` | VERIFIED | Documented LogRecord class for historical BGP statistics. |
| `generic.GenericObject.triggerCollect` | VERIFIED | Documented on-demand collection method. |
| `registerLogToFile` | VERIFIED | Documented for continual accounting/performance statistics. |
| `findToFile` | VERIFIED | Documented for occasional/infrequent retrieval. |
| Statistics Search Tool | VERIFIED | Documented in Statistics Management Guide. |
| MPLS interfaces in plotter profiles | PARTIAL | Profile support is documented, exact XML API class names are not. |
| OSPF / IS-IS performance statistics | UNKNOWN | No explicit XML API class information in the supplied summary evidence. |

## 16. Remaining API gaps

- Exact XML API class names for MPLS, IP, Ethernet, OSPF, and IS-IS performance counters are not documented in the supplied evidence summary. `UNKNOWN`
- Exact source page numbers are not available in the current evidence summary and should be confirmed from the PDFs. `UNKNOWN`
- The full set of supported performance counters and the XML API reference/SDK are not available in the supplied summary. `UNKNOWN`

## 17. SYNC-012-B prerequisites

Required follow-up for SYNC-012-B:

- Confirm exact page/section references from `Statistics_Management_Guide_Issue_1.pdf`
- Confirm exact page/section references from `XML_API_Developer_Guide_Issue_1.pdf`
- Validate the complete set of supported XML API performance classes and LogRecord classes
- Confirm exact object scope and collection interval semantics for each documented class
- Map verified NFM-P performance classes to NDCA target fields

## 18. Acceptance criteria

- The discovery document exists at `docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md`.
- The register exists at `docs/sync/SYNC-012-A_Performance_Counter_Register.csv`.
- The discovery artifacts are based on the supplied NFM-P 24.4 documentation and do not invent API names or statistics classes.
- An offline test validates the discovery register structure and evidence status usage.
- No live NFM-P system is required to validate the discovery artifacts.
- No production NFM-P performance collector implementation is included in this milestone.
