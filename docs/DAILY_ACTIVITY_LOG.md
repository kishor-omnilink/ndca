# Daily Activity Log

## Project

**Project:** `OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD`  
**Workstream:** `Branch · Branch · Network Requirement Analysis`  
**Repository:** `/opt/ndca/repo`  
**Remote:** `https://github.com/kishor-omnilink/ndca.git`

> This log records factual project activity from the Git repository. The workstream label above is a project/workstream identifier; the actual Git branch is recorded in each daily entry.

---

## 2026-08-18

### Repository State

- Repository verified at `/opt/ndca/repo`.
- Remote `origin` verified as `https://github.com/kishor-omnilink/ndca.git`.
- Actual current Git branch: `feature/sync-012-b-performance-collector`.
- The requested workstream label `Branch · Branch · Network Requirement Analysis` is not a literal Git branch name in the verified branch list.

### Activity Observed

Recent repository activity is centered on SYNC-012 performance-collector work:

- `726c8a9` — `feat(sync): add BGP performance evidence capture utility`
- `dc15f68` — `docs(sync): update SYNC-012-B.3 BGP evidence blocker`
- `7d5aa65` — `docs(sync): record SYNC-012-B.3 BGP evidence blocker`
- `6249b8a` — `feat(sync): implement SYNC-012-B.2 interface current data`
- `da9adfe` — `fix(sync): harden SYNC-012-B collector contract`
- `5b7cd66` — `feat(sync): add offline NFM-P performance collector foundation`
- `aaf4dfe` — `docs(sync): add SYNC-012-B performance collector design`
- `c0b6909` — `docs(sync): preserve SYNC-012-A discovery artifacts`

### Existing Documentation

The repository currently contains:

- `docs/Project State Document.md`
- `docs/sync/SYNC-012-A_NFMP_Performance_API_Discovery.md`
- `docs/sync/SYNC-012-A_Performance_Counter_Register.csv`
- `docs/sync/SYNC-012-B.2_NFMP_Interface_Current_Data.md`
- `docs/sync/SYNC-012-B.3_BGP_Current_Data_Blocker.md`
- `docs/sync/SYNC-012-B.3_Kafka_Implementation_Spec.md`
- `docs/sync/SYNC-012-B_NFMP_Performance_Collector_Design.md`

### Current Project State

**Active — SYNC-012-B performance collector work is in progress.**

The recent Git history shows implementation and documentation activity around NFM-P performance collection, interface current data, BGP evidence capture, and related blockers.

### Blockers / Open Items

- A BGP current-data blocker is explicitly documented in `docs/sync/SYNC-012-B.3_BGP_Current_Data_Blocker.md`.
- Further project progress should continue from the actual Git state and existing SYNC-012 documentation rather than assuming the workstream label is a literal branch.

### Next Actions

1. Continue the active SYNC-012-B work from `feature/sync-012-b-performance-collector`.
2. Resolve or progress the documented BGP evidence blocker.
3. Continue validation of the performance collector against the established design and API-discovery evidence.
4. Keep the daily activity log factual and synchronized with actual Git activity.

---

## 2026-08-18 — SYNC-012-B.3 BGP Evidence Update

### Activity Completed Today

- Continued directly from the existing `SYNC-012-B.3` evidence state; `SYNC-012-A`, generic NFM-P API discovery, Kafka validation already completed earlier, and `SYNC-012-B.2` interface work were not repeated.
- Reviewed the existing BGP evidence under `docs/sync/evidence` and identified the previously captured `bgp.PeerStats` XML responses as unusable for field evidence because the captured XML was only a synthetic `<root><peer>sample</peer></root>` response.
- Investigated the NFM-P HTTPS path on `10.110.11.60:443` and confirmed TCP/HTTPS reachability. TLS verification was shown to be the issue for the initial request; an explicit HTTPX test with `verify=False` reached the NFM-P front end and returned HTTP `401 Authorization Required` from nginx.
- Confirmed the configured NDCA setting `NFMP_VERIFY_SSL=false`; therefore the remaining XML-path failure is authentication/access, not network reachability.
- Reoriented BGP evidence collection to the existing NSP Kafka telemetry path instead of continuing the blocked XML route.
- Verified Kafka TCP connectivity to `10.110.11.60:9192`.
- Verified the existing Kafka CLI at `/opt/kafka-cli/bin/kafka-console-consumer.sh` and the existing `/opt/kafka-cli/client.properties` configuration using `security.protocol=SSL`, the Nokia PKCS#12 truststore, and disabled endpoint identification.
- Confirmed the BGP telemetry topic: `ns-eg-1716a23b-7c94-4393-831d-cd97c20c1e70`.
- Performed a live Kafka read-only capture and observed `4` messages, of which `3` were identified as BGP messages.
- Live BGP evidence included real neighbor/session and performance fields such as `system-id`, `session-state`, `remote-family_family`, `sent_messages`, `sent_octets`, `sent_queues`, `sent_route-refresh`, `sent_updates`, `update-errors`, `time-captured`, and corresponding periodic fields.
- Confirmed the live BGP payload is substantially stronger evidence than the earlier synthetic XML response and is the appropriate current-data source for the BGP workstream.
- Identified that exact live Kafka field names must be preserved as observed; for example, the live payload uses `sent_route-refresh` rather than silently renaming it to `sent-route-refresh`.
- No production code was intentionally modified during today's evidence investigation.

### Evidence / Gate Position

- **NFM-P XML `bgp.PeerStats`: NOT VERIFIED / BLOCKED.** No genuine BGP XML field evidence was obtained; HTTP access reaches nginx but returns `401 Authorization Required`.
- **Kafka BGP current data: LIVE EVIDENCE VERIFIED.** A live BGP telemetry message was successfully observed from the configured Kafka topic over SSL.
- Kafka BGP fixture/mapper/test artifacts were found in the local working tree, but the Kafka implementation/evidence artifacts were also observed as untracked local work and therefore should not yet be treated as committed Git source-of-truth without an intentional commit.
- **SYNC-012-B.3 Gate 2: NEAR PASS / PENDING FINAL EVIDENCE RECONCILIATION.** The major live-data evidence gap is closed; the remaining task is to document the exact live field inventory and reconcile it with the existing NDCA normalized performance contract without inventing or silently renaming fields.

### Verified Live BGP Facts

- Kafka broker: `10.110.11.60:9192`
- Kafka security protocol: `SSL`
- BGP topic: `ns-eg-1716a23b-7c94-4393-831d-cd97c20c1e70`
- Live messages read: `4`
- Live BGP messages observed: `3`
- Example live system identity: `172.26.0.21`
- Example live session state: `Established`
- Example live remote family: `IPv4`
- Live counters observed include sent messages, sent octets, sent queues, sent route-refresh, sent updates, update errors, and their periodic variants.
- Live timestamp field observed: `time-captured` with corresponding `time-captured-periodic`.

### Remaining TODO

1. Produce the final SYNC-012-B.3 BGP evidence reconciliation from the already captured live Kafka message.
2. Record exact live JSON field names, JSON types, units/semantics, timestamps, NE identity, and peer/object identity.
3. Record the exact mapping from the live Kafka BGP fields to the NDCA normalized performance contract.
4. Preserve the live Kafka capture and metadata under `docs/sync/evidence/` as the Gate 2 evidence artifact, if not already preserved in the local working tree.
5. Update `docs/sync/SYNC-012-B.3_EVIDENCE_HANDOFF.md` / related checkpoint documentation with the final Gate 2 decision once the reconciliation is complete.
6. Do not modify production collector code until the evidence gate is explicitly closed and the implementation scope is agreed.

---

## Log Maintenance Rules

- Append a new dated section; do not overwrite previous entries.
- Record the actual Git branch used for the work.
- Record only activity supported by Git history, repository files, commits, tests, or project evidence.
- Record blockers explicitly.
- Record validation/testing when actually performed.
- Do not invent work, decisions, tests, or outcomes.
- Preserve the project/workstream label `Branch · Branch · Network Requirement Analysis`.
