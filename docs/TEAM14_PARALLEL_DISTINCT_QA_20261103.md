# TEAM-14: concurrent QA runners with distinct captures (2026-11-03)

This is a new, isolated, real Windows multi-process regression for the published 0.2.10 QA runner. It is **not** a complete multi-agent or independent ChatGPT-host acceptance.

## Evidence and results

- Scope: `build/host-workflow-v2/team14-parallel-distinct-qa-20261103T0535JST/`; the three test projects were generated from the official synthetic V2 fixture, not copied from a prior trial or Demo.
- QA source: locally preserved, previously release-verified `check_runner.py` SHA-256 `7ad73950c45a12bd21fc9e5f84d17259cf9c7b4e9628bef70e9e79a5400fda64`; helpers came read-only from 0.2.9 shadow, with online Plugin Creator metadata confirming USER/PRIVATE 0.2.10 and release `pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`.
- Each of three fresh cases launched two independent Python processes against the **same original expected digest**, using different evidence IDs, different capture paths, and different side-effect marker files. Launch separation was approximately 8-12 ms.
- Results: three rounds **3/3 PASS for single-writer outcome**; each round had exactly one exit 0 and one exit 1, one actual side-effect marker, one evidence capture, one evidence record, zero pending operations and final checkpoint revision 4.
- The losing process in every round returned `[Errno 13] Permission denied`, **not** a semantic `Stale checkpoint` message. Therefore this confirms no double execution in these observed races, but does not prove clean CAS diagnostics or full conflict mediation.
- Independent 0.2.9 shadow `validate`: 3/3 exit 0. `ready`: 3/3 exit 1, expected because the synthetic test task is still EXECUTING; these are not complete project candidates.
- Raw stdout/stderr, process PIDs, launch times, fixture checkpoints, capture files, effect markers and the one-shot harness are retained under the audit directory.
- Five protected source/state files (`runs.json`, trial-22/27 checkpoints, `docs/STATUS.md`, `docs/TASKS.md`) matched SHA-256 before and after. Historical failures and original host trials were not changed.

## Audit and limits

- `PARALLEL_QA_AUDIT.json` SHA-256: `624aa793cab672c30e103cf6f44034068ba19d51175177fd69876dd5e7d0badd`.
- trial-22 remains archived as handover-incomplete, revision 43; independent 0.2.9 `validate` PASS and `ready` FAIL (`Unfinished work`).
- trial-27 remains revision 14, BACKEND FAILED and `runs.json` status `SUBMITTED_RUNNING`. No matching active observer was found, but host completion is still unproven. No concurrent host trial was started.
- Overall strict 0.2.9 consecutive clean path: **0/3**. Full TEAM **0/14**, ROLE **0/18**, E2E **0/4**.
- Shared Desktop Commander process PID 20772 remains alive; shared STATUS/TASKS were left unchanged to respect single-writer and atomic-save restrictions. This document is an independent append-only audit note.

