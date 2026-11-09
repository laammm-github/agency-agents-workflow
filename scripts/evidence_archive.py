#!/usr/bin/env python3
"""Read-only evidence catalog, integrity verification and no-delete cleanup planning.

This is a DEVELOPMENT-SIDE utility, not bundled plugin runtime code.
It never changes existing trials, checkpoints, runs.json, evidence or logs.
Outputs must be new paths (exclusive-create) under the authorized project.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "agency-evidence-catalog/v1"
TRIAL_RE = re.compile(r"^trial-(\d+)(?:-(observed|recovery-\d+))?$")
PROTECTED_NAMES = {"checkpoint.json", "runs.json", "TASKS.md"}
PROTECTED_PARTS = {"evidence", "runtime", "logs", "captures"}
WINDOWS_TMP_SUFFIXES = {".pending", ".tmp"}
MAX_NOTICES = 250


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ensure_inside(root: Path, path: Path):
    root = root.resolve()
    candidate = path.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Path is outside the authorized project: " + str(path))
    return candidate


def valid_relative(base: Path, rel: str) -> Path | None:
    if not isinstance(rel, str) or not rel or "\\" in rel:
        return None
    pieces = rel.split("/")
    if any(x in {"", ".", ".."} for x in pieces):
        return None
    dest = (base / Path(*pieces)).resolve()
    return dest if dest.is_relative_to(base.resolve()) else None


def read_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def file_stat(path: Path):
    try:
        stat = path.stat()
        return {"exists": True, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    except (OSError, ValueError) as err:
        return {"exists": False, "error": type(err).__name__}


def archive_tree_counts(folder: Path):
    counts = Counter()
    bytes_total = 0
    risks = []
    for base, dirs, files in os.walk(folder, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
        counts["directories"] += len(dirs)
        for name in files:
            f = Path(base) / name
            if f.is_symlink():
                counts["symlinks"] += 1
                continue
            try:
                size = f.stat().st_size
                counts["files"] += 1
                bytes_total += size
                if name.endswith(".pyc") or "__pycache__" in f.parts:
                    counts["cache_files"] += 1
            except OSError as exc:
                risks.append({"path": str(f), "issue": type(exc).__name__})
    return dict(counts), bytes_total, risks[:MAX_NOTICES]


def evidence_records(base: Path, state: dict, verify_hashes: bool):
    entries = []
    missing = []
    mismatches = []
    artifact_aliases = {
        a.get("artifact_id"): a.get("path")
        for a in state.get("artifacts", [])
        if isinstance(a, dict) and a.get("artifact_id") and a.get("path")
    }
    for ev in state.get("evidence", []) if isinstance(state.get("evidence"), list) else []:
        if not isinstance(ev, dict):
            continue
        rel = ev.get("artifact_ref")
        entry = {
            "id": ev.get("evidence_id"),
            "task_id": ev.get("task_id"),
            "check": ev.get("check"),
            "outcome": ev.get("outcome"),
            "provenance": ev.get("provenance", "UNSPECIFIED"),
            "artifact_ref": rel,
            "recorded_sha256": ev.get("output_sha256"),
        }
        path = valid_relative(base, rel)
        # Early checkpoints sometimes stored an artifact ID, not a path.
        # Resolve only through its recorded artifact; preserve original ref.
        if (path is None or not path.is_file()) and rel in artifact_aliases:
            alias = artifact_aliases[rel]
            alternative = valid_relative(base, alias)
            if alternative is not None and alternative.is_file():
                path = alternative
                entry["resolution"] = "ARTIFACT_ID_ALIAS"
                entry["resolved_path"] = alias
        entry["safe_path"] = path is not None
        entry["exists"] = path is not None and path.is_file()
        if not entry["exists"]:
            missing.append(str(rel))
        elif verify_hashes and ev.get("output_sha256"):
            try:
                entry["observed_sha256"] = file_sha(path)
                entry["sha256_matches"] = entry["observed_sha256"] == ev["output_sha256"]
                if not entry["sha256_matches"]:
                    mismatches.append(str(rel))
            except OSError as exc:
                entry["read_error"] = type(exc).__name__
                mismatches.append(str(rel))
        entries.append(entry)
    return entries, missing, mismatches


def candidate_files(base: Path, state: dict, verify_hashes: bool):
    cand = state.get("candidate") or {}
    manifest = cand.get("manifest") or {}
    entries = []
    if not isinstance(manifest, dict):
        return {"candidate_id": cand.get("candidate_id"), "files": [], "error": "Invalid manifest"}
    for rel, expected in sorted(manifest.items()):
        path = valid_relative(base, rel)
        entry = {"path": rel, "recorded_sha256": expected, "safe_path": path is not None,
                 "exists": path is not None and path.is_file()}
        if entry["exists"] and verify_hashes:
            try:
                entry["observed_sha256"] = file_sha(path)
                entry["sha256_matches"] = entry["observed_sha256"] == expected
            except OSError as exc:
                entry["read_error"] = type(exc).__name__
        entries.append(entry)
    return {"candidate_id": cand.get("candidate_id"), "files": entries}


def snapshot_trial(folder: Path, root: Path):
    item = {"path": folder.relative_to(root).as_posix(), "kind": "observed-sibling" if folder.name.endswith("-observed") else "trial",
            "protected": True, "preservation": "DO_NOT_MOVE_OR_DELETE"}
    stats, size, issues = archive_tree_counts(folder)
    item.update({"file_counts": stats, "bytes": size, "scan_warnings": issues})
    checkpoint = folder / "checkpoint.json"
    if not checkpoint.is_file() or checkpoint.is_symlink():
        item["checkpoint"] = {"exists": False}
        item["verification_level"] = "UNVERIFIED_NO_CHECKPOINT"
        return item
    try:
        before = checkpoint.read_bytes()
        doc = json.loads(before)
        state = doc.get("state", {})
        tasks = state.get("tasks", [])
        statuses = {x["task_id"]: x["status"] for x in tasks if isinstance(x, dict) and "task_id" in x}
        complete = bool(statuses) and all(x == "COMPLETED" for x in statuses.values())
        item["checkpoint"] = {"exists": True, "sha256": digest(before), "revision": doc.get("revision"),
                              "status_by_task": statuses, "pending_operations": len(doc.get("pending_operations", [])),
                              "updated_at": doc.get("updated_at")}
        item["verification_level"] = "COMPLETED_READ_ONLY" if complete else "INCOMPLETE_METADATA_ONLY"
        # Do not deeply hash a running trial; shared browser/host may still be writing.
        verify_hashes = complete
        item["candidate"] = candidate_files(folder, state, verify_hashes)
        entries, missing, mismatches = evidence_records(folder, state, verify_hashes)
        item["evidence"] = entries
        item["evidence_missing_paths"] = missing
        item["evidence_hash_mismatches"] = mismatches
        board = folder / "TASKS.md"
        item["task_board"] = {"exists": board.is_file()}
        if board.is_file() and complete:
            try:
                item["task_board"]["sha256"] = file_sha(board)
                item["task_board"]["contains_revision"] = ("Revision: " + str(doc.get("revision"))) in board.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                item["task_board"]["read_error"] = type(exc).__name__
        # Recheck after scan; never present changing checkpoint as a certified snapshot.
        if digest(checkpoint.read_bytes()) != digest(before):
            item["verification_level"] = "CHANGING_DURING_SCAN"
            item["checkpoint"]["stable_during_scan"] = False
        else:
            item["checkpoint"]["stable_during_scan"] = True
    except (OSError, ValueError, TypeError, UnicodeError, KeyError) as exc:
        item["checkpoint"] = {"exists": True, "read_error": str(exc)[:160]}
        item["verification_level"] = "UNVERIFIED_READ_ERROR"
    return item


def snapshot_project(project: Path):
    project = project.resolve(strict=True)
    trials_root = project / "build" / "host-workflow-v2"
    if not trials_root.is_dir():
        raise ValueError("Expected build/host-workflow-v2 is missing")
    top = list(trials_root.iterdir())
    folder_items = []
    for path in sorted(top, key=lambda p: p.name.casefold()):
        if path.is_dir() and TRIAL_RE.fullmatch(path.name) and not path.is_symlink():
            folder_items.append(snapshot_trial(path, project))
    top_ext = Counter()
    top_protected = 0
    file_count, total_bytes = 0, 0
    review = []
    for path in top:
        if path.is_file() and not path.is_symlink():
            file_count += 1
            st = path.stat()
            total_bytes += st.st_size
            top_ext[path.suffix.lower()] += 1
            if path.suffix.lower() in WINDOWS_TMP_SUFFIXES:
                review.append({"path": path.relative_to(project).as_posix(), "size": st.st_size,
                               "classification": "REVIEW_ONLY_PRESERVE", "reason": "May be a failed CAS proposal"})
            if path.name == "runs.json" or path.name.endswith((".jsonl", ".log", ".stop")):
                top_protected += 1
    anchors = []
    for rel in ["build/host-workflow-v2/runs.json", "docs/STATUS.md", "docs/TASKS.md",
                "docs/ACCEPTANCE_MATRIX.md", "plugin.json", "package-files.json"]:
        path = valid_relative(project, rel)
        anchors.append({"path": rel, **file_stat(path), "sha256": file_sha(path) if path and path.is_file() else None})
    runs_file = trials_root / "runs.json"
    runs = {}
    if runs_file.is_file():
        try:
            content = read_json(runs_file)
            for key, value in content.items():
                if key.startswith("trial-") and isinstance(value, dict):
                    runs[key] = {"status": value.get("status"), "checkpoint_revision": value.get("checkpoint_revision"),
                                 "recorded_checkpoint_sha256": value.get("checkpoint_sha256"),
                                 "normal_path_counted": value.get("normal_path_counted")}
        except (OSError, ValueError) as exc:
            runs = {"_error": str(exc)[:200]}
    result = {
        "schema": SCHEMA, "generated_at_utc": utc_now(), "project_root": str(project),
        "source": "read-only project scan; statuses are record claims, not authenticated tool executions",
        "policy": {"retention": "INDEFINITE_UNLESS_USER_EXPLICITLY_AUTHORIZES_DESTRUCTION",
                   "immutable": ["trial-*/**", "trial-*-observed/**", "runs.json", "*-watch.jsonl",
                                 "**/checkpoint.json", "**/evidence/**", "**/proposal-*.json",
                                 "failed/raw tool returns", "published plugin archives"],
                   "cleanup_default": "DRY_RUN_ONLY_NO_DELETE_NO_RENAME_NO_MOVE"},
        "counts": {"top_level_entries": len(top), "top_level_regular_files": file_count,
                   "top_level_file_bytes": total_bytes, "top_level_protected_files": top_protected,
                   "top_level_suffixes": dict(top_ext),
                   "trial_related_directories": len(folder_items),
                   "trial_files": sum(x["file_counts"].get("files", 0) for x in folder_items),
                   "trial_bytes": sum(x.get("bytes", 0) for x in folder_items)},
        "anchors": anchors,
        "runs_index": runs,
        "trials": folder_items,
        "cleanup_review_candidates": review,
    }
    return result


def write_new_json(path: Path, obj, project: Path):
    dest = ensure_inside(project, path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    serialized = (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with dest.open("xb") as f:
        f.write(serialized)
        f.flush()
        os.fsync(f.fileno())
    if digest(dest.read_bytes()) != digest(serialized):
        raise IOError("Written snapshot failed independent readback")
    return {"path": str(dest), "sha256": digest(serialized), "bytes": len(serialized)}


def markdown_report(index: dict) -> str:
    """Human-readable navigation index; recorded PASS is not independently authenticated."""
    if index.get("schema") != SCHEMA:
        raise ValueError("Unsupported snapshot schema")
    counts = index["counts"]
    lines = [
        "# Agency Agents Workflow — 证据归档索引",
        "",
        "索引生成时间（UTC）：" + index["generated_at_utc"],
        "",
        "> 这是只读快照，供检索和完整性核验使用；状态来自保存记录，",
        "> 不独立证明宿主工具来源或软件验收通过。原始试验目录保持原位不变。",
        "",
        "## 范围与索引统计",
        "",
        f"- 顶层条目：{counts['top_level_entries']}；试验相关目录：{counts['trial_related_directories']}",
        f"- 试验目录文件：{counts['trial_files']}；试验目录总字节：{counts['trial_bytes']}",
        "- 已完成任务的候选/证据哈希可以核验；未完成试验和缺检查点目录暂不深度认证。",
        "- 原始 FAIL、UNKNOWN、观察器日志、CAS 提案和备份一律保留；没有自动清理。",
        "",
        "## 各轮试验",
        "",
        "| 目录 | 检查点 | 任务完成 | 文件/证据 | 校验状态 | 官方归档状态 |",
        "|---|---:|---|---:|---|---|",
    ]
    runs = index.get("runs_index", {})
    for trial in index["trials"]:
        rel = trial["path"]
        name = Path(rel).name
        cp = trial.get("checkpoint", {})
        states = cp.get("status_by_task") or {}
        done = sum(x == "COMPLETED" for x in states.values())
        task_status = f"{done}/{len(states)}" if states else "—"
        rev = str(cp.get("revision", "—"))
        evidence_count = len(trial.get("evidence", []))
        size = str(trial.get("file_counts", {}).get("files", 0)) + "/" + str(evidence_count)
        level = trial["verification_level"].replace("_", " ")
        archived = runs.get(name, {})
        archived_text = str(archived.get("status") or "未见正式归档状态")
        archived_text = archived_text.replace("|", "&#124;").replace("\n", " ")
        check_path = rel + ("/checkpoint.json" if cp.get("exists") else "")
        link = f"[{name}](../{check_path.removeprefix('build/')})"
        lines.append(f"| {link} | {rev} | {task_status} | {size} | {level} | {archived_text} |")
    aliases = [(t["path"], e["id"], e["artifact_ref"], e["resolved_path"])
               for t in index["trials"] for e in t.get("evidence", [])
               if e.get("resolution") == "ARTIFACT_ID_ALIAS"]
    lines += ["", "## 旧格式引用映射（不修改原文件）", ""]
    if aliases:
        lines += ["| 试验目录 | 证据 ID | 原逻辑引用 | 实际文件 |", "|---|---|---|---|"]
        for trial, eid, src, actual in aliases:
            lines.append(f"| {trial} | {eid} | {src} | {actual} |")
    else:
        lines.append("没有发现已成功解析的逻辑产物 ID 引用。")
    lines += ["", "## 完整性与清理", "",
              "查看 verification/ 与 plans/ 中和本快照对应的结果文件。",
              "校验结果、当前工作状态及清理许可须分别判断。索引不是删除许可。",
              "",
              "相关源文件：../../scripts/evidence_archive.py",
              "规则文档：../../docs/EVIDENCE_ARCHIVE_POLICY.md", ""]
    return "\n".join(lines)


def write_new_text(path: Path, value: str, project: Path):
    dest = ensure_inside(project, path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = value.encode("utf-8")
    with dest.open("xb") as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    if digest(dest.read_bytes()) != digest(raw):
        raise IOError("Written report failed independent readback")
    return {"path": str(dest), "sha256": digest(raw), "bytes": len(raw)}


def create_plan(index: dict):
    if index.get("schema") != SCHEMA:
        raise ValueError("Unsupported snapshot schema")
    protected_directories = [t["path"] for t in index.get("trials", [])]
    candidates = list(index.get("cleanup_review_candidates", []))
    return {
        "schema": "agency-evidence-cleanup-plan/v1",
        "based_on_snapshot_utc": index["generated_at_utc"],
        "project_root": index["project_root"],
        "default_action": "NO_DELETE",
        "never_touch": ["runs.json", "historical *.jsonl, *.log, *.stop", "checkpoint.json",
                        "all evidence and raw returns", "all proposal/failed CAS files",
                        "original package ZIPs", "trial directories", "current active runs"],
        "protected_trial_directories": protected_directories,
        "review_only": candidates,
        "automatic_deletion_candidates": [],
        "reversible_actions_performed": 0,
        "destructive_actions_performed": 0,
        "next_step": "Review individual paths, verify references and active writer absence; request explicit approval before any destructive or relocating action",
    }


def verify(index: dict):
    if index.get("schema") != SCHEMA:
        raise ValueError("Unsupported snapshot schema")
    root = Path(index["project_root"])
    findings = []
    checked = 0
    deferred = 0
    for anchor in index.get("anchors", []):
        path = valid_relative(root, anchor["path"])
        if path is None or not path.is_file():
            findings.append({"path": anchor["path"], "issue": "MISSING_ANCHOR"})
            continue
        checked += 1
        if file_sha(path) != anchor["sha256"]:
            findings.append({"path": anchor["path"], "issue": "CHANGED_SINCE_SNAPSHOT"})
    for trial in index.get("trials", []):
        level = trial.get("verification_level")
        if level != "COMPLETED_READ_ONLY":
            deferred += 1
            continue
        base = valid_relative(root, trial["path"])
        if base is None:
            findings.append({"path": trial["path"], "issue": "UNSAFE_TRIAL_PATH"})
            continue
        cp = trial.get("checkpoint", {})
        cp_path = base / "checkpoint.json"
        if not cp_path.is_file() or file_sha(cp_path) != cp.get("sha256"):
            findings.append({"path": trial["path"], "issue": "CHECKPOINT_CHANGED_OR_MISSING"})
            continue
        checked += 1
        for item in trial.get("candidate", {}).get("files", []):
            path = valid_relative(base, item["path"])
            if path is None or not path.is_file():
                findings.append({"path": trial["path"]+"/"+str(item["path"]), "issue": "CANDIDATE_MISSING"})
            else:
                checked += 1
                if file_sha(path) != item["recorded_sha256"]:
                    findings.append({"path": trial["path"]+"/"+item["path"], "issue": "CANDIDATE_CHANGED"})
        for item in trial.get("evidence", []):
            if not item.get("recorded_sha256"):
                continue
            path = valid_relative(base, item.get("resolved_path") or item["artifact_ref"])
            if path is None or not path.is_file():
                findings.append({"path": trial["path"]+"/"+str(item["artifact_ref"]), "issue": "RAW_EVIDENCE_MISSING"})
            else:
                checked += 1
                if file_sha(path) != item["recorded_sha256"]:
                    findings.append({"path": trial["path"]+"/"+item["artifact_ref"], "issue": "RAW_EVIDENCE_CHANGED"})
    return {"schema": "agency-evidence-verify/v1", "snapshot_generated_at": index["generated_at_utc"],
            "verification_at": utc_now(), "checked_files": checked,
            "deferred_trial_directories": deferred, "finding_count": len(findings),
            "findings": findings[:500], "truncated": len(findings) > 500,
            "note": "Changed evidence/checkpoint is a preservation discrepancy, not license to rewrite historical files"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["snapshot", "verify", "cleanup-plan", "report"])
    ap.add_argument("--project-root", required=True, help="existing authorized project root")
    ap.add_argument("--index", type=Path, help="snapshot input for verify/cleanup-plan")
    ap.add_argument("--output", type=Path, help="new unique output file (never overwritten)")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve(strict=True)
    if args.action == "snapshot":
        if args.index or args.output is None:
            ap.error("snapshot requires --output, no --index")
        result = snapshot_project(root)
        saved = write_new_json(args.output, result, root)
        print(json.dumps({"action": args.action, **saved, "counts": result["counts"]}, ensure_ascii=False))
        return 0
    if args.index is None:
        ap.error("verify/cleanup-plan/report require --index")
    index_path = ensure_inside(root, args.index)
    index = read_json(index_path)
    if index.get("project_root") != str(root):
        raise ValueError("Index belongs to a different project")
    if args.action == "report":
        if args.output is None:
            ap.error("report requires --output")
        saved = write_new_text(args.output, markdown_report(index), root)
        print(json.dumps({"action": args.action, "output": saved,
                          "trial_related_directories": len(index["trials"])}, ensure_ascii=False))
        return 0
    result = verify(index) if args.action == "verify" else create_plan(index)
    if args.output is not None:
        saved = write_new_json(args.output, result, root)
    else:
        saved = None
    print(json.dumps({"action": args.action, "output": saved, "summary": {
        k: v for k, v in result.items() if k in {"checked_files", "deferred_trial_directories",
                                                    "finding_count", "automatic_deletion_candidates",
                                                    "destructive_actions_performed"}
    }, "findings_preview": result.get("findings", [])[:10]}, ensure_ascii=False))
    return 1 if args.action == "verify" and result["finding_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileExistsError, OSError) as error:
        print(json.dumps({"error": type(error).__name__, "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
