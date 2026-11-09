# One-shot local QA capture

Use the bundled [team helper](../scripts/team.py), [v2 gates](../scripts/workflow_v2.py) and [check runner](../scripts/check_runner.py) when Python and jsonschema are actually available. They are ordinary finite command-line programs invoked through existing authorized command tools. They grant no permission, sandbox, MCP tool, independent agent or background runtime. Do not install dependencies without authorization.

If helpers are not already reachable on the verified target, read these three plugin resources and materialize their exact contents under an authorized project tools directory. Preserve the sibling layout `scripts/`, `references/schemas/` and `references/agent-catalog.json`; copy the schemas/catalog from this plugin. Verify the transferred files against the resources before executing. Never assume a helper path on ChatGPT is a path on the user's device. Do not overwrite an existing tools installation or copy another trial's implementation. For scriptless hosts use the existing file workflow and disclose that deterministic checks were not run.

Before running executable QA, save task inputs/artifacts and enter EXECUTING through team.py. Verify actual authorization and cwd. Use check_runner.py for finite code tests, integration scripts and executable security checks so the process return and FAIL are saved before any repair. Do not first run an unrecorded test and import only the later success. Browser tools and non-command inspections retain their exact host-return capture path; record each actual failure before repair. Documentation/research still use inspection and do not require code execution.

Save a UTF-8 JSON argv array in the project, for example `["python", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]`. Use the actually verified Python executable. Pass separate arguments through the actual command tool:

```
python -B <helper-root>/scripts/check_runner.py <checkpoint>
  --expected-digest <actual-checkpoint-sha256> --task-id <active-task>
  --evidence-id <new-id> --output evidence/<new-capture>.json
  --check test --argv-file <project-argv-file> --timeout 60
```

This shows arguments, not a literal multiline shell command. Use a unique evidence ID/path for each execution. `--acceptance-id` can restrict coverage to actual tested acceptance IDs; omitted means the task's declared set, so choose it honestly. Do not use this runner to launch persistent services, migrations or deployment actions. Commands and their descendants retain the host's permissions: the caller must keep them within authorized scope.

Set the outer command's actual lifetime above the child timeout plus state-save time, using its verified contract. A client wait ending does not prove execution stopped. If the outer command interrupts the adapter, inspect the persisted intent and real process/effects before continuing; do not run it again merely because its acknowledgement was lost.

The runner saves an exact argv/cwd intent in pending_operations before executing once, records stdout/stderr with exact base64 bytes and actual exit code, then atomically appends evidence. Nonzero results set the task FAILED before returning. Repair requires the existing FAILED → PREFLIGHT → EXECUTING transitions; for the new run pass `--supersedes <failed-evidence-id>` for each covered failure. A successful matched rerun retires explicitly superseded FAIL IDs only from the task's current evidence_refs, while preserving every original FAIL record and raw output in global history. An omitted supersedes cannot clear unresolved failure. The runner does not mark tasks complete, hand off, retry or broaden permissions. It preserves old records and current required review/inspection checks still apply.

`tool: python.subprocess.run` identifies the actual local Python API called by this adapter. Its response is a local process return, not a fabricated outer MCP response. HOST_RETURN describes those captured process bytes; independent connector authentication remains UNKNOWN. Save the actual outer host call separately when available, and independently inspect/retest before certification. A script returning exit 0 cannot prove its assertions were sufficient.

Timeout, launch uncertainty, changed inputs, a conflict or failed result save leaves the persisted intent unresolved and preserves any captured return. Investigate real effects; never automatically replay, clear pending_operations or adopt a new digest merely to pass. The adapter compares snapshots and hashes but cannot intercept arbitrary file tools or detect every change between observations. A lost acknowledgement after a successful state save is reconciled by reading the existing evidence ID and unique output, not by running the command again.

In manually captured returns omit observed_paths for commands that did not return source content. If present it must be nonempty and list actually read source inputs. A hash read alone does not provide source content for a ROLE_PHASE model review.
