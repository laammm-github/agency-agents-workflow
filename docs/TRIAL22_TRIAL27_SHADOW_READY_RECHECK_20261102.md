# Trial-22 / Trial-27: isolated 0.2.9 readiness recheck

Trusted Plugin Creator metadata confirms the original USER/PRIVATE plugin is 0.2.9, release pluginrel_6ae53a8cc71881919a8e7c98c19f7536. The shadow 0.2.9 team.py CLI was run on byte-identical checkpoint snapshots, never the originals.

- trial-22: validate EXIT 0; ready EXIT 1 (Unfinished work). Raw backend QA FAIL then PASS; three browser negative captures PASS; same SQLite restart capture PASS; frozen manifest 7/7 hashes match. HANDOVER remains EXECUTING; project TASKS.md is absent. Historical failure retained.
- trial-27: validate EXIT 0; ready EXIT 1 (Unfinished work). Backend QA EXIT 1 with PATCH HTTP 501; FRONTEND, INTEGRATION, HANDOVER incomplete. Project TASKS.md absent.
- Original host end remains unproven. Its Edge tab is discarded; runs.json still SUBMITTED_RUNNING. No host correction, original trial mutation, concurrent host trial, or success reclassification.
- Two initial independent audit wrapper failures were preserved as failures in the machine audit; the corrected capture used separate stdout/stderr and exit codes.
- Strict 0/3 clean streak and TEAM-01..14, ROLE-01..18, E2E-TEAM-A/B/C/D host acceptance gaps remain.

Raw captures, snapshots, and READINESS_RECHECK_AUDIT.json: build/host-workflow-v2/acceptance-gap-matrix-20261102/snapshot-20261101T223831Z/. Shared STATUS.md and TASKS.md remain unchanged due potential lock/concurrent writer.