# v2 execution and record contract

## Final live task board and candidate readiness (0.2.9)

The versioned checkpoint is the source of truth, not a stale project report.
After all delivery/documentation tasks reach COMPLETED, regenerate the live
workspace TASKS.md from the last checkpoint with the bundled
`team.py report <checkpoint> --markdown --output <workspace>/TASKS.md --expected-digest <current-sha256>`.
Read the generated file and verify its revision and per-task statuses match
the checkpoint. This helper locks and compares the checkpoint, writes via a
temporary proposal and atomic replace, and checks readback. Staged proposals
are retained if atomic replacement fails; investigate the actual file owner
without force-closing shared processes.

Live TASKS.md is a state projection, not a frozen source artifact; keep it
out of source manifests and input hashes. A missing board (when the flow has
DELIVERY or HANDOVER) or a stale existing board must cause `ready` to fail,
even if the candidate code and all evidence otherwise pass. Validate and run
ready again only after an independently observed report regeneration; never
backfill the missed report into a historical clean-host acceptance result.

This is a sequential host-tool workflow, not a runtime or security sandbox. Existing valid user authorization persists. Do not install, publish, deploy, migrate production data or expand scope because a role suggests it. For read-only requests inspect existing records; do not initialize or generate files.

## Before implementation

First-source-edit barrier: an initialized empty checkpoint is insufficient. Save the plan and role-use records. Finish design inspection/handoff, then advance the corresponding backend/frontend task to EXECUTING before its source files are written. Use `preflight <checkpoint> --task-id <developer-task> --purpose implementation --write-path <file>` with each planned file and require source_task_ready=true. DESIGN executing or a generic stage PASS is insufficient. Documentation can use --purpose stage for its own artifacts. The helper checks declared records/paths, not OS permissions, and does not intercept raw file tools.

New source outputs need not exist before starting a development task: its initial input hashes can reference the existing approved design/contract. Declare exact relative source files in optional task.write_paths (fallback: literal deliverables). After writing source under that task, update its verification inputs to include actual deliverable hashes before running QA. Each accepted evidence timestamp must be within the task's actual execution epoch, after its first EXECUTING event and before completion. Unchanged checks within the same repair epoch can be reused when inputs still match; checks from before a reopened task cannot prove a new execution. Never backdate events to make old tests fit.

For an authorized new directory, a structured PATH_NOT_FOUND result is expected. Discover/inspect the real directory-create capability and create that target, then read it back. Shell fallback must start from an existing cwd and use literal paths. A malformed command is not evidence of missing directory permissions; diagnose the contract instead of repeating variants blindly. Permission denial, device mismatch or unreachable tools are genuine blockers and must not be bypassed.

1. Verify actual device/workspace, tools, authorized paths, existing modifications and unknown prior operations. Save a baseline through authorized tools. Missing capability blocks dependent work.
2. Read only the operation's workflow and necessary catalog roles. Record role_id, catalog path/hash, evidence_ref and observation in state.role_reads. HOST_RETURN means an observed host read; UNVERIFIED means source use could not be observed. Do not invent read records or independent agents.
3. Version requirements with named acceptance IDs and observed confirmation/source. Resolve required business questions before executing dependent tasks. Define design, backend, frontend, integration and handover tasks for a cross-stack project, with actual dependencies and owner roles. Task count is based on independently verifiable outcomes, not a fixed quota for every request.

## Work and QA loop

For executable local QA use [one-shot captured checks](local-checks.md) before the first test or retest. It saves the process return and failure state before returning, including expected stage-assertion failures. Read that adapter contract first; ordinary file/command tools outside it are not intercepted. An actual omitted failure remains a workflow failure even if the later task gate passes.

- Record a task PLANNED -> PREFLIGHT -> EXECUTING -> VERIFYING -> COMPLETED. Persist each transition as it occurs, including state revision, time and evidence references. Do not retrospectively mark a whole pipeline complete.
- DEVELOPMENT requires test + review; INTEGRATION requires integration + review; DOCUMENTATION and RESEARCH require inspection. Declare extra browser/security checks when applicable before starting. Documentation does not require code tests. Same-session review uses review_kind=ROLE_PHASE.
- Evidence must be a complete v2 Evidence record: actual tool, time, scope, operation, result, command exit code (null for noncommands), output path/hash, task/acceptance IDs, requirement_versions, input_hashes, check, provenance and review_kind. Do not label a model-written summary as raw tool output. MODEL_JUDGMENT cannot satisfy completion gates.
- Store raw host output separately from independent readback/retest and model assessment. HOST_RETURN is an observation category, not authenticated tool attestation; state the absence of independent connector audit. Never present a call ID, file existence or self-written JSON as sole proof.
- Copy actual returns/command stdout and stderr as observed, with sensitive fields redacted and the redaction noted. Do not synthesize a transcript or label a narrative file HOST_RETURN because a file tool wrote it. Record actual command exit codes as command evidence; do not turn a command into an observation with a null exit code. A multi-tool summary is MODEL_JUDGMENT with references to the separate actual checks, not an invented composite tool. Same-session review notes are model judgments; retain the real inspection/test outputs supporting the review and its limitations.
- Before completing, verify input files still match and passed evidence covers every acceptance ID and required check. Current FAIL/BLOCKED/UNKNOWN blocks until a later matching PASS explicitly supersedes it for the same check and scope. Preserve all original evidence. At most three controlled repair attempts after the initial attempt; investigate before any retry and stop on unknown effects.
- Handoffs name producer/consumer tasks and roles, requirement versions, actual artifacts/evidence, risks, questions and next preconditions. A dependent task cannot execute without a resolved, current handoff for each dependency. Resolve preconditions by observation, not by assuming resolved=true.

## State and files

The public workflow-v2.schema.json has all complete record definitions in $defs, including state and checkpoint. All saved v2 records require project_id, revision and updated_at. Use the existing task status enum; readiness, deployment and evidence certainty are separate results. v1 records must be explicitly migrated with observed missing fields; never guess dates, authorization or evidence to make migration pass.

Checkpoint.state is the sole status authority. Generate TASKS.md / handover summary from it, label revision, and read back before reporting. Keep caller-produced reports outside the registered hash baseline unless deliberately versioned, avoiding an endless report/hash/checkpoint update cycle. Exclude the checkpoint itself from its hash map.

The live generated board/summary must also be outside task input_hashes and immutable artifacts. After final completion, regenerate it from that final revision. Versioned historical reports may be retained under different names, but must not be presented as the current board. Do not register the evolving TASKS.md as a handover input and then overwrite it after completing that handover task.

Artifacts have category SOURCE, CONFIG, BUILD, DOCUMENT, EVIDENCE or RUNTIME. Version changes with new artifact IDs and supersedes; never rewrite old artifact hashes. Current SOURCE/CONFIG/BUILD form the release candidate manifest. RUNTIME files such as a live SQLite database are not frozen source inputs; verify persistence by restarting with the same data file, or by a consistent backup. A page refresh is not a process-restart test.

Each task's evidence binds its declared input_hashes and requirement_versions. Candidate labels alone do not determine reusability. Unchanged task evidence can be reused when those inputs/versions still match. The final integration result must bind the exact candidate ID and entire manifest; it must rerun for a new candidate. Requirement changes invalidate affected tasks and dependents and clear final integration references; retain old evidence and handoffs for audit.

## Optional local helper

Use only when the repository's development helpers and Python dependencies are actually accessible through an authorized tool. These commands are not plugin RPC tools and scripts are not a required component of ChatGPT Web. Without them use exposed file tools, the packaged schema and the same gates, recording deterministic checks as NOT_RUN if unavailable.

- `python -B scripts/team.py init <checkpoint> --workspace <project> --project-id <id> --authorization-ref <observed-reference>` creates an empty v2 checkpoint in an already authorized directory. Use --schema-version 1 only for explicit legacy work.
- `update <checkpoint> --proposal <complete-v2-document> --expected-digest <old-file-sha256>` validates and saves new records; it cannot alter task status, existing requirements or evidence history. New tasks start PLANNED. Update input/artifact hashes only after authorized changes and investigation, not to bypass external edits.
- `transition <checkpoint> --task-id <id> --status <status> --expected-digest <old-sha>` appends an actual transition and preserves checkpoint metadata. Complete required records before transition to COMPLETED.
- `change <checkpoint> --requirement-id <id> --description <new-content> --expected-digest <old-sha>` versions the requirement and invalidates affected acceptance, with explicit history.
- `invalidate <checkpoint> --task-id <id> --description <observed-change-reason> --expected-digest <old-sha>` reopens a task and its dependents after an input/code change without inventing a requirement version change. Investigate external edits first. Then explicitly version changed artifacts and update affected task input hashes through an authorized proposal.
- `validate <checkpoint>` checks records; `report <checkpoint> --markdown` prints a state projection; save its output only within authorized scope. `ready <checkpoint> --candidate <id>` checks the fixed manifest and final integration. Readiness is not deployment.
- `preflight <checkpoint> --task-id <active-task> --purpose stage` checks the saved task/role/dependencies and hashes. Before source writes use --purpose implementation and one or more --write-path values; this requires an active development/integration task and exact paths declared by it. An empty checkpoint cannot pass. Recheck actual authorization separately; these checks do not grant tool permissions.
- `resume <checkpoint> --workspace <project>` checks the entire saved baseline, including non-artifact files, and unknown operations. Then recheck real authorization/device before action; a checkpoint does not grant permission.
- `migrate <v1-file> --proposal <observed-complete-v2-document> --output <new-file>` keeps the original, stores its full legacy_snapshot and rejects missing fields or dropped/changed historical records. Never overwrite source to migrate. Legacy metadata cannot prove historical execution order.

For every update compare actual revision/file digest; preserve existing work on conflict. Write records through the existing cooperative lock/atomic save if helper is available. The mechanism does not provide OS isolation or authenticate execution.

An atomic replace or sharing/access error is not permission to overwrite by copy. Preserve the proposal and original, inspect file permissions, sharing and possible writers; close only an identified preview/handle you own if needed and authorized. Retry only after the cause is understood, otherwise BLOCKED. With helper access, prefer textual checkpoint reads or helper command output instead of opening an unnecessary file preview during mutation. A fallback without script capability must still compare the actual baseline and provide equivalent safe conflict handling; otherwise do not claim a successful save.

### Windows read-tool file-handle regression

Trial-16 found a live checkpoint held by the Desktop Commander MCP Node process, causing two team.py update attempts to fail at atomic replace with WinError 5. On a disposable file, one mcp__desktop_commander_mcp__read_file call was followed by a persistent sharing lock; another similar file did not reproduce. Sampled mcp__OmniTool_MCP__file_read and finite PowerShell Get-Content reads did not lock their own disposable files. This is host-specific evidence, not a universal guarantee about any tool.

For a live mutable checkpoint.json, avoid Desktop Commander read_file and file-preview paths if a verified nonlocking text reader is available. Probe a disposable authorized file and close probe handles. Before saving, compare the actual checkpoint digest and check for unknown operations/writers. If os.replace reports sharing/access denied, preserve both failure and proposed state, identify the owner with read-only diagnostics, and retry only after a tool-owned handle has demonstrably been released. Do not force-terminate the shared MCP server or replace checkpoint.json directly.

An incident document may be saved while a DEVELOPMENT stage is EXECUTING, but it is historical evidence, not final delivery. If DOCUMENTATION/HANDOVER remains PLANNED, do not create final README.md/REVIEW.md or a completion-claiming current task board. Never backfill a stage handoff from later files.

## Service and writer recovery

Before a launch or restart, inspect the project's existing launch records/logs, recorded PID and process start time, listener ownership, and read-only HTTP/data state. A workspace substring missing from a command line is insufficient: relative `server.py`/database arguments are common. Never conclude no service exists from that filter alone. Reuse a verified service; investigate multiple or uncertain instances before starting or stopping any. Check current process identity as PIDs may be reused. New launches should use absolute script/database paths and unique log files; save the actual PID/start time/URL/database path/candidate reference as RUNTIME metadata plus an observed last_confirmed_action. Do not freeze live runtime metadata/data into the release manifest.

Record an action's intent before a non-idempotent call and reconcile the actual return/state afterward. Interrupted calls remain unresolved until inspected. A client stop button, lost stream or missing spinner is not proof that remote work was cancelled. If revisions, files or services advance unexpectedly, block dependent writes/starts, identify the writer and reconcile authorization/history. Merely reading the new digest does not resolve the conflict. Run any exposed coding tools sequentially; do not start a second writer during an unknown prior operation. No permanent lease or background runtime is implied by these observations.

## Host verification and reporting

Browser evidence may come from any actually available, authorized browser tool, not only OmniTool. A received MCP content list can be preserved as the exact `response.content` list in tool_capture with the actual observed tool name and arguments. Do not invent success flags, exit codes or an OmniTool wrapper around another provider's return. Browser observations do not require a command exit code. Preserve each real action/result and the tested behavior separately from model assessment. If the tool exposes only rendered text, preserve that exact complete returned text and disclose which wrapper metadata could not be observed.

Reuse a verified owned browser session for the current project. A session-pool limit is not permission to close unknown sessions or bypass tool boundaries. If an exposed authorized browser already works, preserve that provider's real returns rather than repeatedly trying to create another session merely for an evidence format. Session cleanup requires actual ownership verification and an exposed supported close operation. Record unavoidable capability limits as BLOCKED, without inventing a capture.

Report exactly the actual actions, raw results and remaining uncertainty. A working demo, local unit tests, successful plugin save and full team host acceptance are different milestones. For fresh host trials do not copy old demo code or old execution timelines. Preserve failed trials; a user/evaluator correction is a failed autonomous-flow trial even if the repair later succeeds. Record elapsed time, observed tool count (UNKNOWN if not observable), autonomous repair count and evaluator corrections.

Final all-team delivery still requires TEAM-01–14, ROLE-01–18 and E2E-TEAM-A/B/C/D with real host evidence. Missing authorization/environment is BLOCKED, not a silent waiver. Test deployment, rollback and fault injection are restricted to the specifically authorized isolated target.


## Evidence policy 2 (new checkpoints)

New state uses `evidence_policy_version=2`. An absent flag or value 1 retains the legacy read/validation path; ordinary update cannot upgrade or downgrade it. This is separate from schema_version=2.

For every successful non-model check save a JSON `$defs/tool_capture` envelope: `capture_version:1`, the exact observed `tool`, actual `arguments` object, full received `response` object, actual `observed_at`, and the task's verified `input_hashes`. Hash this file in its evidence record. Preserve stdout/stderr and actual terminal status, not a rewritten success narrative. A running command needs its completion return; wrapper success alone does not prove test completion. Never invent absent exit codes. Text-only output without terminal status cannot certify code tests: retain it and use an available actual exit-code verifier, or report BLOCKED. Disclose any necessary redaction without inventing replacements.

Same-session review is `check:review`, `review_kind:ROLE_PHASE`, `provenance:MODEL_JUDGMENT`, `exit_code:null`. Save its conclusion separately and set `supporting_evidence_refs` to current passed same-task inspection records. Source-reading captures use `observed_paths` listing the actual source inputs read, with matching hashes. Reading a model summary is not source inspection. Model reviews cannot replace tests, security execution or final integration.

Completion, dependent-task execution and implementation preflight verify current evidence files. Never overwrite historical evidence files: preserve each original return at a unique path. Hashes and file presence do not authenticate execution. The gate reports `execution_authentication:UNKNOWN`; compare actual host calls/results independently when available and disclose missing audit coverage.

`migrate <legacy-v2-file> --proposal <complete-policy2-checkpoint> --output <new-file>` explicitly upgrades evidence policy while preserving the source and its full legacy_snapshot. Keep records, events, role observations, authorization and unknown operations. Reopen tasks and remove obsolete references from current evidence_refs; retain original evidence records and files. Do not relabel old summaries as raw returns. Completed tasks need actual valid current captures. Missing fields or changed baseline inputs block migration. Existing v1 migration remains supported.

Evidence policy 2 also binds DOCUMENT deliverables to task.input_hashes before completion, for both DOCUMENTATION and RESEARCH. Hash the actual inspected document versions and copy those hashes into their actual tool capture. This does not require code tests for document/research tasks. Generated live task boards remain outside immutable artifacts and verification inputs to avoid self-reference.

After an actual failed QA return, before modifying code or rerunning: save the entire failure at a unique capture path, append its FAIL record with original input hashes/time/actual exit, and persist a legal failure transition (EXECUTING or VERIFYING to FAILED; VERIFYING to BLOCKED when investigation requires a blocking precondition). Never store only the later PASS. Use the controlled repair transition, then save a new return and PASS record explicitly superseding the matching failure. Verify the checkpoint contains both original FAIL and rerun PASS before handing off or starting a dependent task. If the original return is unavailable, report missing evidence; do not reconstruct it from memory.
