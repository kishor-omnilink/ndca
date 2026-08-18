# OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD — Small-Chat Working Structure

## Purpose

This document defines the ChatGPT working structure for the project. It is intentionally designed to keep each conversation bounded so that project work can continue without repeatedly loading the entire historical project context.

## Source-of-truth rules

1. Git repository is authoritative for source code and committed implementation state.
2. Project control documents are authoritative for verified project state, milestones, decisions, and handoffs.
3. A work chat must remain limited to one workstream.
4. Completed work must not be re-investigated unless a regression or contradictory evidence is found.
5. UNKNOWN vendor/API behavior must not be guessed or implemented.
6. Each completed workstream ends with a compact handoff/checkpoint.

## Chat structure

### Control

- `00-MASTER CONTROL` — overall project status, milestones, blockers, next approved action. No coding.
- `01-PROJECT STATE` — repository state, current branch, verified implementation, tests, recent commits.

### Architecture

- `10-REQUIREMENTS` — business and functional requirements.
- `11-ARCHITECTURE` — HLD/LLD and component/data-flow decisions.
- `12-DATA ARCHITECTURE` — source-to-storage-to-dashboard data model.
- `13-DECISION REGISTER` — architectural and implementation decisions.

### NDCA / NSP

- `21-NFMP API & EVIDENCE` — NFM-P XML API evidence and vendor-contract verification only.
- `22-PERFORMANCE COLLECTOR` — implementation of verified performance collection.
- `23-NORMALIZATION & MAPPING` — source payload to normalized NDCA records.
- `24-DATABASE & PERSISTENCE` — ORM, repositories, migrations, TimescaleDB.
- `25-SCHEDULER & ORCHESTRATION` — collection scheduling and run lifecycle.
- `26-KAFKA INTEGRATION` — existing Kafka path and only required future changes.

### Dashboard

Create only when the data pipeline is ready:

- `31-DASHBOARD BACKEND`
- `32-DASHBOARD UI`
- `33-KPIs & ANALYTICS`
- `34-HISTORICAL PERFORMANCE`
- `35-REPORTING`

### Validation / Operations

Create only when required:

- `41-UNIT TESTING`
- `42-INTEGRATION TESTING`
- `43-LIVE NFM-P VALIDATION`
- `44-END-TO-END VALIDATION`
- `51-DEPLOYMENT`
- `52-OPERATIONS & RUNBOOK`

## Current active chats

Only create/use these initially:

1. `00-MASTER CONTROL`
2. `01-PROJECT STATE`
3. `21-NFMP API & EVIDENCE`
4. `22-PERFORMANCE COLLECTOR`
5. `24-DATABASE & PERSISTENCE`

Additional chats are created only when that workstream begins.

## Standard opening block for every work chat

```text
PROJECT: OCAC_IPMPLS_NOKIA_CUSTOM_DASHBOARD
REPOSITORY: kishor-omnilink/ndca
WORKSTREAM: <one workstream only>
SOURCE OF TRUTH: Git repository + project control documents

RULES:
- Inspect current repository state before proposing changes.
- Do not repeat completed work.
- Do not invent vendor/API fields or behavior.
- Do not modify unrelated modules.
- Implement only verified requirements.
- Run relevant offline tests before declaring completion.
- End with a compact handoff for the next chat.
```

## Handoff rule

At the end of a workstream, produce a short handoff containing:

- Objective
- Verified facts
- Files/modules involved
- Changes made
- Tests performed/results
- Decisions
- Open issues/blockers
- Exact next action

The next chat receives the handoff, not the entire previous conversation.

## Current continuation point

The project must continue from `SYNC-012-B.3` evidence. Do not restart SYNC-012-A, generic API discovery, Kafka validation, or already completed interface-current-data work.
