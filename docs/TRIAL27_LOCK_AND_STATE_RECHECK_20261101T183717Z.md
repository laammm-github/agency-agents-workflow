# Trial-27 independent read-only lock and state recheck

Observed UTC: 2026-11-01T18:37:17.402128+00:00

The original private plugin metadata was independently read as USER/PRIVATE, version 0.2.9 and the specified release. The run registry still says SUBMITTED_RUNNING; trial-27 checkpoint remains revision 14 with {'DESIGN': 'COMPLETED', 'BACKEND': 'FAILED', 'FRONTEND': 'PLANNED', 'INTEGRATION': 'PLANNED', 'HANDOVER': 'PLANNED'}. No host-completion proof was obtained: the original ChatGPT Edge tab is discarded, and file inactivity does not establish remote termination.

The shared Desktop Commander node process PID 20772 is alive and has currently open handles to: scripts/team.py, scripts/workflow_v2.py, scripts/check_runner.py, build/host-workflow-v2/runs.json, build/host-workflow-v2/trial-22/checkpoint.json, build/host-workflow-v2/trial-27/checkpoint.json, docs/STATUS.md, docs/TASKS.md. Handle share modes were not established; this is a material Windows atomic-replacement risk, not permission to force close handles.

Root helper hashes differ from the 0.2.9 shadow for team.py and workflow_v2.py; check_runner.py matches. No root helper synchronization was attempted.

Original trial-27 QA failure and all historical failures are preserved. The clean autonomous count remains 0/3; TEAM-01..14, ROLE-01..18, and E2E-TEAM-A/B/C/D are not certified complete.

Independent audit: build/host-workflow-v2/trial27-lock-and-state-recheck-20261101T183717Z.json
Shared docs/STATUS.md and docs/TASKS.md are left unchanged due observed open handles; this note is an append-only separate status document.
