# TEAM-14: concurrent update CAS isolated acceptance (2026-11-02)

Read-only preflight checked runs.json, trial-22 and trial-27 checkpoints, STATUS.md and TASKS.md. Plugin Creator independently returned USER/PRIVATE, version 0.2.9 and release pluginrel_6ae53a8cc71881919a8e7c98c19f7536.

Three fresh, synthetic, separate Windows workspaces were created under build/host-workflow-v2/team14-concurrent-update-20261102T0235Z. In each, the published 0.2.9 shadow team.py initialized a V2 checkpoint; two real Python processes launched concurrent update commands with the same expected SHA256 and the same atomic proposal.

Each race had exactly one exit 0 and one exit 1; final checkpoint revision was 1 and validate exited 0 in all three. Losing processes reported [Errno 13] Permission denied, **not** a stale-digest rejection. This verifies single-winner behavior in these three trials, but does not prove a deterministic CAS error class or full multi-agent conflict arbitration. ready exited 1 because each fixture is an intentionally unfinished project.

Audit: build/host-workflow-v2/team14-concurrent-update-20261102T0235Z/CONCURRENT_UPDATE_AUDIT.json, SHA256 b552bb97be45bc5b94e948c19cf98c7d3e850bbe72d0689f447452c163274933. Each race stores raw init, two worker, validate and ready command returns with exit codes; failed returns were not overwritten. Harness preparation failures are described separately as model summaries in HARNESS_PREPARATION_ERRORS.json (raw returns remain in the tool history).

Original runs.json, trial-22/trial-27 checkpoints, STATUS.md, TASKS.md and both shadow helpers had matching SHA256 before and after the isolated test. No historical project, plugin, root helper, Git or public deployment was modified. No shared process was killed or Windows handle forcibly released.

**Verdict: TEAM-14 isolated concurrent-update subscenario PARTIAL PASS.** TEAM-14 full host acceptance remains NOT PASSED. TEAM 0/14, ROLE 0/18, E2E 0/4 and strict 0.2.9 clean streak 0/3 remain unchanged. trial-27 remains SUBMITTED_RUNNING with revision 14 and BACKEND FAILED; original host completion is not proved, so no new autonomous host trial or final archive was started.
