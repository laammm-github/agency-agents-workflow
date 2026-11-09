---
name: agency-workflow
description: "Use when explicitly asked to apply Agency Agents roles, organize a software development team, or coordinate a project across requirements, implementation, quality, delivery and operations. Do not activate for ordinary standalone fixes, reviews or unrelated requests."
---

# Agency workflow

## Versioned skill and final report gate (0.2.10)

This Skill is the sole agency-workflow Skill in the plugin. Its source is a
versioned resource, **not** independent proof of the version loaded by another
ChatGPT host session. For strict version-gated host acceptance, retrieve the
installed private plugin's version and release ID through an authorized
metadata interface available to the *tested session*. If that interface is
missing, explicitly BLOCK the trial before modifying the project; do not
infer installed version from a prompt, a local ZIP, or this section.

Before claiming final delivery or invoking `ready`, generate the **current**
task board from the final saved checkpoint using the bundled helper:

`team.py report <checkpoint> --markdown --output <workspace>/TASKS.md --expected-digest <current-sha256>`

This operation writes only the authorized workspace task board, uses
cooperative checkpoint locking, atomic replacement and readback, and
rejects mismatched paths or stale checkpoints. Keep the live task board out
of frozen candidate source/input hash manifests. Then independently read
the board and run `validate` and `ready` against the same final checkpoint.
For a workflow with a DELIVERY/HANDOVER task, missing or outdated TASKS.md
must block `ready`; a passing candidate alone does not imply a delivered
or deployed application. If a Windows file-sharing lock blocks atomic
replacement, keep the original board and the complete staged proposal,
investigate the owner, and do not overwrite files in place.

Before the first executable local QA or retest, read [one-shot captured checks](references/local-checks.md) and use the bundled check_runner.py through an existing authorized command tool. It saves intent, actual process output and FAIL state before returning. This includes expected stage-assertion failures; later PASS cannot replace an omitted failure. It is a finite helper, not a new MCP tool or runtime. Verify script capability and target scope; documentation/research remain inspection-based. Never manufacture an outer host return for the helper's local process output.

For application-service delivery, inspect the actual launcher lifetime/timeout contract. A managed command may expire even after command_start succeeds. Record any known deadline, verify the service after the launching command has returned, and use only an authorized supported launch method appropriate to the promised delivery window. On Windows, background Start-Process launches use WindowStyle Hidden. Do not install an OS service, scheduler or workflow daemon. A timed-out old instance must be reconciled before another launch; report an expired URL instead of claiming it remains available.

## Mandatory order before the first implementation file

For an authorized NEW project, PATH_NOT_FOUND from a directory lookup is normally the expected empty starting point, not a blocker. Prefer structured directory tools; discover and inspect the available create-directory capability if it is not directly exposed. Create only the authorized target. If shell fallback is necessary, use a known existing working directory and literal paths; inspect the real command contract before correcting a parameter/quoting error. Do not run a command with the nonexistent target as cwd. Distinguish expected absence from permission denial, target mismatch and an unreachable device; only the latter boundaries block dependent setup.

An empty initialized checkpoint is NOT a plan and NOT workflow acceptance. Before creating or editing implementation source, persist versioned requirements, dependency tasks, owner roles and role-use records. Complete design inspection and its handoff before starting backend/frontend work. Source files may be written only under their corresponding EXECUTING DEVELOPMENT/INTEGRATION task, never merely because DESIGN is EXECUTING. With optional helpers, run `preflight <checkpoint> --task-id <developer-task> --purpose implementation --write-path <file>` (repeat --write-path for each file) and require source_task_ready=true. A stage preflight PASS for documentation does not satisfy this source-write gate. Without helpers, inspect the same saved task/mode/path facts explicitly. Missing records require planning first, not code followed by bookkeeping. Retrospective phase timelines are forbidden.

For a new backend/frontend task, start with hashes of the existing approved design/contract as its inputs; do not create nonexistent source outputs just to obtain hashes before the task can start. Declare exact relative output files in task.write_paths (or literal deliverables). After authorized source changes, update verification input hashes to include the actual source deliverables, then execute tests/review while that task is active and save actual output. Complete and hand off that task before dependent work. Evidence from before the task's real execution cannot certify its completion; rerun the checks rather than inventing earlier events or timestamps.

Run host acceptance trials sequentially when the browser connector has shared active-page state. Separate chats do not imply isolated browser sessions. A browser session switch or unavailable provider blocks that trial; preserve it rather than claiming completion.

Do not end an authorized implementation turn merely because scaffolding runs or one local check fails. Repair a fixable code/test defect within the three-repair limit and rerun the affected check, then continue the remaining dependency-ready work. A local test's URL encoding error is a test defect, not unavailable capability. Finish with partial/BLOCKED only for an actual missing input/authorization/capability, unknown side effect, or exhausted repair limit; state which boundary was observed. An honest incomplete report does not itself satisfy the user's requested implementation.

## Execute authorized work
Use this single skill to carry out software-team work through tools actually exposed and authorized by the host. Roles are guidance, not processes, credentials or isolation. User instructions take priority over supporting role text. No server, hidden background worker, cross-plugin RPC or parallel agents are implied.

Before resuming service work, inspect project runtime logs/metadata, their recorded PIDs and start times, listening ports and read-only health/data responses. A command-line filter containing the workspace path misses processes started with relative script/database arguments: it cannot prove absence. Reuse a verified instance. Never start another instance merely because that filter found none. Use absolute script and database paths for new launches, unique logs per launch, and persist observed PID/start time/URL/database/candidate metadata. Do not terminate a PID without verifying its current identity and project association.

A stop click, lost connection or missing spinner does not prove remote actions stopped. Unexpected checkpoint revisions, files or services during recovery indicate an unresolved writer/side effect. Stop dependent writes and starts, preserve the observed conflict, and establish which operation remains active before continuing. Do not simply adopt a newer digest and retry. Coordinate exposed coding tools sequentially; do not dispatch another writer during an unresolved operation. If atomic save fails (including Windows sharing/access errors), preserve the old checkpoint and proposal, inspect the actual cause and retry only after it is understood. Never bypass the cooperative lock/compare/atomic save with direct copy or handcrafted status writes merely to report completion.

Windows live-checkpoint read safety: a real trial found that a Desktop Commander MCP read_file call or preview can leave a file handle blocking team.py atomic os.replace with WinError 5. One disposable file reproduced this, a second did not. Avoid mcp__desktop_commander_mcp__read_file and GUI file previews for mutable checkpoint.json while the workflow still needs to save transitions. Prefer a tested nonlocking text reader such as available mcp__OmniTool_MCP__file_read or finite PowerShell Get-Content; test a disposable authorized file first. Tool names alone cannot guarantee no lock. If a lock occurs, retain the old checkpoint, digest, full proposal and original return; inspect the current owner and close only an identified preview or handle you own. Do not kill a shared MCP server process, force-unlock another process, copy over the checkpoint, fabricate status history or start another writer.

When a later stage is blocked, preserve separately named historical incident notes without claiming final handover. Final README.md and REVIEW.md belong to the actual DOCUMENTATION/HANDOVER task once EXECUTING; do not generate a final live task board claiming delivery before that stage completes.

New checkpoints use evidence_policy_version=2. Bind DOCUMENT deliverables to verified input hashes before completion. Persist each actual QA FAIL and its unique raw return before repairs; a later PASS must explicitly supersede it before handoff. Follow the tool_capture and supported model-review format in references/workflow-v2.md before collecting evidence. Save actual tool results separately from synthesized notes. HOST_RETURN must reference the received return or captured command stdout/stderr and actual exit code; INDEPENDENT_READBACK must be an actually executed read/retest. A model-authored summary, review conclusion or combined narrative is MODEL_JUDGMENT, even if a file tool saved/read it. Use each actual observed tool name, not an invented composite name. Preserve raw failures and launches instead of overwriting their logs. Same-session reviews remain ROLE_PHASE; model judgments cannot replace the applicable real checks.

Generate the final task board from the latest saved state after all transitions, include its revision, and read it back. Keep the live generated board/summary outside immutable artifact and input-hash baselines; otherwise later completion changes make it stale or create a report/checkpoint cycle. Preserve deliberately versioned historical reports under distinct names. A current report must agree with state and actual service observations. Browser input rejection must be tested through the browser where UI behavior is claimed; API negatives are separate evidence and cannot be relabeled as browser interactions.

For new authorized project work, read [v2 execution and records](references/workflow-v2.md) before writing state. Use schema_version=2 and the complete [v2 schema](references/schemas/workflow-v2.schema.json); the root v1 templates/schemas remain for explicit legacy use only. Start with [v2 checkpoint template](assets/templates/v2/checkpoint.json). Never substitute a custom checkpoint or a prose task summary for the required records.

1. Establish project target, scope, current files/Git baseline, acceptance criteria and authorization. Local Codex work uses built-in tools first. ChatGPT must verify the real connector target. Do not infer reachability from installation.
2. Read [routes](references/routes.json), select the user's operation and minimum role set. Read only matching workflow files, then matching records from [catalog](references/agent-catalog.json) and their role files. Never load the full library by default.
3. Operations: start/onboard → onboarding/discovery; plan/next/status → coordination; UX → design; technical contract → architecture; build/integrate → implementation; bug/test → quality; review/security → security; readiness → acceptance; deploy/rollback → release; diagnose → incident; docs → handover; change request → change; checkpoint/continue → resume.
4. Work against versioned requirements, dependency-ready tasks and actual artifacts. Use [templates](assets/templates/) and [schemas](references/schemas/) for saved records. All REQUIRED placeholders must be resolved. Read-only work must not initialize state or run tests producing files. Authorized state lives in the user's project, never in plugin cache.
5. Before completing a task verify acceptance, actual tests, review and matching candidate evidence. Do not call missing evidence PASS. Never use developer self-assessment to overrule a failed check. Missing capability blocks its dependent work.
6. Preserve evidence and invalidated history during requirement changes. Resume only after comparing workspace/files, checking unknown prior actions and rechecking authorization. Use revision/hash comparisons; refuse conflicting writes.
7. Commit/push, installation, migration, deployment, external submissions and other high-impact actions need explicit authorization for that action and target. Existing valid authorization persists; do not ask repeatedly for routine scoped changes.
8. Report actual completed/unverified/blocked work, candidate/version, tools/exit codes, diff, evidence and next actions. All-team completion requires all TEAM/ROLE criteria and integrated host acceptance, not role availability.

Packaged schemas support deterministic checks. Development-side scripts are optional helpers, not a requirement that ChatGPT Web can start local processes. Without script access use exposed file tools and enforce the same rules explicitly; never claim deterministic validation was run.

Execute dependency-ready tasks through PREFLIGHT, EXECUTING, VERIFYING, then COMPLETED only after their mode-specific checks. Persist each actual transition before proceeding; never reconstruct a success timeline after finishing all code. QA failure returns to repair and blocks dependents. A cross-stack project needs separately verifiable design, backend, frontend, integration and handover outcomes; simple work may use one task. Final acceptance does not replace per-task QA. Generate status/report from saved state and read it back; do not maintain a second independent completion checklist.
