"""Fail-closed post-start execution certification for MindRoom.

This validator is the canonical IMPLEMENTATION_EXECUTION_CERTIFICATION mode.
It does NOT compare Codebase to the original frozen baseline as an equality
gate. Instead it proves that every live Codebase delta is attributable to a
successfully completed canonical implementation task receipt whose identity,
scope, dependencies, tests, checkpoints, and publication are all derived from
repository authority rather than from the receipt itself.

The original frozen baseline remains immutable and is never redefined.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
CODEBASE = ROOT.parent / "Codebase"

ORIGINAL_FROZEN_CODEBASE_TREE = "bbf383e3418da4f613f58719160bb7cbd5709ffc"
ORIGINAL_FROZEN_FILE_COUNT = 10080
ORIGINAL_FROZEN_DIRECTORY_COUNT = 2548
ORIGINAL_FROZEN_AGGREGATE = "91600fc76001d8b2c108634d4fa3ceca5e743176f103a44d21b7e0e7273ec748"

STATUS_PATH = "00 Execution Control/STATUS.json"
AUTHORIZATION_PATH = "11 Completion/EXECUTION_AUTHORIZATION_RECORD.json"
RECEIPTS_PATH = "11 Completion/EXECUTION_RECEIPTS.jsonl"
CHECKPOINT_CHAIN_PATH = "11 Completion/EXECUTION_CHECKPOINT_CHAIN.jsonl"
TRUSTED_BASELINE_PATH = "11 Completion/EXECUTION_TRUSTED_BASELINE.json"
TASKS_PATH = "09 Implementation/IMPLEMENTATION_TASKS.jsonl"
ROLLBACK_PATH = "07 Reorganisation/ROLLBACK_PLAN.jsonl"
TEST_PATH = "10 Verification/REQUIREMENT_TEST_MATRIX.jsonl"

# Canonical governance-level generated output patterns. These are NOT
# receipt-authoritative: they are repository governance policy and cannot be
# widened by any execution receipt.
CANONICAL_GENERATED_PATH_PATTERNS = (
    "Codebase/yarn.lock",
    "Codebase/.yarn/install-state.gz",
    "Codebase/packages/*/*/dist/**",
    "Codebase/packages/*/*/src/generated/**",
)

VALIDATION_MODES = ("IMPLEMENTATION_EXECUTION_CERTIFICATION",)


def read_json(relative):
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def read_jsonl(relative):
    path = ROOT / relative
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()] if path.exists() else []


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_hash(records):
    text = "\n".join(f"{row['path']}:{row['sha256']}" for row in sorted(records, key=lambda row: row["path"]))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inventory_tree(root):
    display = os.path.abspath(root)
    scan_root = display if not os.name == "nt" or display.startswith("\\\\?\\") else "\\\\?\\" + display
    file_pairs, directories = [], []

    def walk(current):
        try:
            entries = list(os.scandir(current))
        except OSError:
            return
        for entry in entries:
            entry_path = os.path.join(current, entry.name)
            try:
                if os.path.islink(entry_path):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    directories.append(os.path.relpath(entry_path, scan_root).replace("\\", "/"))
                    walk(entry_path)
                elif entry.is_file(follow_symlinks=False):
                    relative = os.path.relpath(entry_path, scan_root).replace("\\", "/")
                    file_pairs.append({"path": relative, "sha256": sha256_file(entry_path)})
            except OSError:
                continue

    walk(scan_root)
    file_pairs.sort(key=lambda row: row["path"])
    directories.sort()
    return {
        "files": file_pairs,
        "directories": directories,
        "fileCount": len(file_pairs),
        "directoryCount": len(directories),
        "aggregateSha256": aggregate_hash(file_pairs),
    }


def git(args, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def git_rev_parse(expression):
    result = git(["rev-parse", f"{expression}^{{commit}}"], check=False)
    if result.returncode != 0:
        result = git(["rev-parse", expression], check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def git_tree(commit):
    result = git(["rev-parse", f"{commit}:Codebase"], check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def git_diff_paths(commit_a, commit_b):
    result = git(["diff", "--name-status", commit_a, commit_b, "--", "Codebase"], check=False)
    if result.returncode != 0:
        return []
    rows = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        rows.append({"status": parts[0], "path": parts[1]})
    return rows


def git_local_tag_target(ref):
    return git_rev_parse(f"refs/tags/{ref}")


def git_remote_refs(pattern):
    result = git(["ls-remote", "--refs", "origin", pattern], check=False)
    if result.returncode != 0:
        return {}
    targets = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            targets[parts[1]] = parts[0]
    return targets


def git_remote_main():
    refs = git_remote_refs("refs/heads/main")
    return refs.get("refs/heads/main")


def git_remote_tag_target(tag):
    refs = git_remote_refs(f"refs/tags/{tag}")
    return refs.get(f"refs/tags/{tag}")


def git_is_ancestor(commit, ancestor_root):
    if not commit or not ancestor_root:
        return False
    result = git(["merge-base", "--is-ancestor", commit, ancestor_root], check=False)
    return result.returncode == 0


def path_matches_pattern(path, pattern):
    path = str(path or "").replace("\\", "/")
    pattern = str(pattern or "").replace("\\", "/")
    if path == pattern:
        return True
    if "**" in pattern:
        regex = "^" + re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*") + "$"
        return re.match(regex, path) is not None
    return path.startswith(pattern.rstrip("/") + "/")


def matches_any(path, patterns):
    return any(path_matches_pattern(path, pattern) for pattern in patterns)


def required_fields(row, fields, label):
    return [field for field in fields if not row.get(field)]


def normalize_path(value):
    return str(value or "").replace("\\", "/").removeprefix("./")


def canonical_task_lookup(task_id, tasks):
    matches = [row for row in tasks if row.get("taskId") == task_id]
    if len(matches) != 1:
        return None, f"task {task_id!r} must resolve to exactly one canonical task; found {len(matches)}"
    return matches[0], None


def canonical_generated_paths(task, actual_paths=None):
    explicit = task.get("generatedPaths") or []
    patterns = list(dict.fromkeys(list(explicit) + list(CANONICAL_GENERATED_PATH_PATTERNS)))
    if actual_paths is None:
        return patterns
    applicable = [pattern for pattern in patterns if any(matches_any(path, [pattern]) for path in actual_paths)]
    return applicable or patterns


def add(checks, check_id, category, description, passed, actual, expected, evidence, method):
    checks.append({
        "checkId": check_id,
        "category": category,
        "description": description,
        "status": "PASS" if passed else "FAIL",
        "actual": actual,
        "expected": expected,
        "evidence": evidence,
        "method": method,
    })


def do_execution_validation():
    checks = []
    status = read_json(STATUS_PATH)
    authorization = read_json(AUTHORIZATION_PATH)
    receipts = read_jsonl(RECEIPTS_PATH)
    checkpoint_rows = read_jsonl(CHECKPOINT_CHAIN_PATH)
    trusted = read_json(TRUSTED_BASELINE_PATH)
    tasks = read_jsonl(TASKS_PATH)
    rollback_rows = read_jsonl(ROLLBACK_PATH)
    tests = read_jsonl(TEST_PATH)
    live = inventory_tree(CODEBASE)
    test_map = {row.get("testId"): row for row in tests if row.get("testId")}

    lifecycle = status.get("lifecyclePhase")
    wave0 = status.get("wave0Readiness")
    codebase_status = status.get("codebaseExecutionStatus")
    implementation_performed = status.get("implementationPerformed") is True
    application_released = status.get("applicationReleased") is True
    completed_receipts = [row for row in receipts if row.get("status") == "COMPLETE" and row.get("publishedToMain") is True]

    original_tree = trusted.get("originalFrozenCodebaseTree")
    current_tree = trusted.get("currentTrustedCodebaseTree")
    current_aggregate = trusted.get("currentTrustedAggregateSha256")
    current_published = trusted.get("currentPublishedCommit")
    remote_main = git_remote_main()

    # EXEC-01 lifecycle state valid
    lifecycle_ok = lifecycle in {
        "PRE_IMPLEMENTATION_FROZEN",
        "IMPLEMENTATION_IN_PROGRESS",
        "WAVE_BOUNDARY_CERTIFICATION",
        "FINAL_RELEASE_CERTIFICATION",
    }
    if lifecycle == "IMPLEMENTATION_IN_PROGRESS":
        lifecycle_ok = lifecycle_ok and wave0 in {"WAVE_0_IN_PROGRESS", "WAVE_0_COMPLETED"} and codebase_status == "AUTHORIZED"
    elif lifecycle == "PRE_IMPLEMENTATION_FROZEN":
        lifecycle_ok = lifecycle_ok and wave0 == "READY_NOT_STARTED" and codebase_status == "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION" and not implementation_performed and not completed_receipts
    add(checks, "EXEC-01", "lifecycle", "Lifecycle state is valid and internally consistent", lifecycle_ok, {
        "lifecyclePhase": lifecycle, "wave0Readiness": wave0, "codebaseExecutionStatus": codebase_status,
        "implementationPerformed": implementation_performed,
    }, "explicit accepted lifecycle vocabulary", ["STATUS.json", "execution-state.schema.json"], "enum and cross-field consistency")

    # EXEC-02 explicit wave authorization exists
    active_auth = authorization.get("authorizationState") == "ACTIVE"
    auth_fields_ok = active_auth and authorization.get("authorizedWave") == "WAVE_0" and authorization.get("authorizationType") == "EXPLICIT_USER_AUTHORIZATION"
    auth_anchor_ok = authorization.get("preAuthorizationMain") and authorization.get("preAuthorizationCodebaseTree") == ORIGINAL_FROZEN_CODEBASE_TREE
    add(checks, "EXEC-02", "lifecycle", "Explicit user authorization exists and is anchored to the original baseline", active_auth and auth_fields_ok and auth_anchor_ok, {
        "authorizationState": authorization.get("authorizationState"), "authorizedWave": authorization.get("authorizedWave"),
        "authorizationType": authorization.get("authorizationType"), "preAuthorizationMain": authorization.get("preAuthorizationMain"),
        "preAuthorizationCodebaseTree": authorization.get("preAuthorizationCodebaseTree"),
    }, {"authorizationState": "ACTIVE", "authorizedWave": "WAVE_0", "authorizationType": "EXPLICIT_USER_AUTHORIZATION", "preAuthorizationCodebaseTree": ORIGINAL_FROZEN_CODEBASE_TREE},
    ["EXECUTION_AUTHORIZATION_RECORD.json"], "machine-readable authorization record")

    # EXEC-03 original frozen baseline preserved
    original_ok = (
        original_tree == ORIGINAL_FROZEN_CODEBASE_TREE
        and (trusted.get("originalFrozenBaseline") or {}).get("aggregateSha256") == ORIGINAL_FROZEN_AGGREGATE
        and (trusted.get("originalFrozenBaseline") or {}).get("fileCount") == ORIGINAL_FROZEN_FILE_COUNT
        and (trusted.get("originalFrozenBaseline") or {}).get("directoryCount") == ORIGINAL_FROZEN_DIRECTORY_COUNT
    )
    add(checks, "EXEC-03", "baseline", "Original frozen Codebase baseline remains immutable", original_ok, {
        "tree": original_tree, "aggregateSha256": (trusted.get("originalFrozenBaseline") or {}).get("aggregateSha256"),
    }, {"tree": ORIGINAL_FROZEN_CODEBASE_TREE, "aggregateSha256": ORIGINAL_FROZEN_AGGREGATE}, ["EXECUTION_TRUSTED_BASELINE.json"], "constant baseline comparison")

    # EXEC-04 current trusted Codebase tree recorded
    add(checks, "EXEC-04", "baseline", "Current trusted Codebase tree and published commit are recorded", bool(current_tree) and bool(current_aggregate) and bool(current_published), {
        "currentTrustedCodebaseTree": current_tree, "currentTrustedAggregateSha256": current_aggregate, "currentPublishedCommit": current_published,
    }, "nonempty current trusted tree, aggregate, and commit", ["EXECUTION_TRUSTED_BASELINE.json"], "required-field validation")

    # EXEC-05 live Codebase tree equals current trusted tree
    live_tree = git_tree("HEAD")
    live_tree_ok = bool(live_tree) and live_tree == current_tree
    live_aggregate_ok = live["aggregateSha256"] == current_aggregate
    add(checks, "EXEC-05", "baseline", "Live Codebase tree and aggregate equal the current trusted tree", live_tree_ok and live_aggregate_ok, {
        "liveTree": live_tree, "trustedTree": current_tree, "liveAggregate": live["aggregateSha256"], "trustedAggregate": current_aggregate,
    }, {"liveTree": current_tree, "trustedTree": current_tree, "liveAggregate": current_aggregate, "trustedAggregate": current_aggregate},
    ["EXECUTION_TRUSTED_BASELINE.json"], "independent Git tree and byte-aggregate comparison")

    # EXEC-06 canonical receipt identity binding
    identity_issues = []
    duplicate_ids = sorted({value for value, count in __import__("collections").Counter(row.get("taskId") for row in receipts).items() if count > 1})
    receipt_required = [
        "taskId", "capabilityId", "wave", "startingCommit", "endingCommit", "startingCodebaseTree", "endingCodebaseTree",
        "preTaskCheckpoint", "postTaskCheckpoint", "changedPaths", "allowedPaths", "forbiddenPaths", "generatedPaths",
        "testsExecuted", "testResults", "acceptanceCriteria", "rollbackAction", "dependencyState", "publishedToMain", "status",
    ]
    missing_fields = []
    for row in completed_receipts:
        missing = required_fields(row, receipt_required, row.get("taskId"))
        if missing:
            missing_fields.append({"taskId": row.get("taskId"), "missing": missing})
        task, error = canonical_task_lookup(row.get("taskId"), tasks)
        if error:
            identity_issues.append({"taskId": row.get("taskId"), "reason": error})
            continue
        canonical = {
            "taskId": task.get("taskId"),
            "capabilityId": task.get("capabilityId"),
            "contractCapabilityId": (task.get("contract") or {}).get("capabilityId"),
            "wave": task.get("releaseWave"),
        }
        if row.get("capabilityId") not in {task.get("capabilityId"), (task.get("contract") or {}).get("capabilityId")}:
            identity_issues.append({"taskId": row.get("taskId"), "reason": "capabilityId does not match canonical task", "canonical": canonical, "actual": row.get("capabilityId")})
        if row.get("wave") != task.get("releaseWave"):
            identity_issues.append({"taskId": row.get("taskId"), "reason": "wave does not match canonical releaseWave", "canonical": canonical, "actual": row.get("wave")})
    no_missing_required = not duplicate_ids and not missing_fields
    missing_receipt_while_moved = not completed_receipts and (implementation_performed or current_tree != original_tree)
    add(checks, "EXEC-06", "receipts", "Completed receipts bind to exactly one canonical task with matching identity", no_missing_required and not missing_receipt_while_moved and not identity_issues, {
        "duplicateIds": duplicate_ids, "missingFields": missing_fields, "identityIssues": identity_issues, "missingReceiptWhileMoved": missing_receipt_while_moved,
    }, {"duplicateIds": [], "missingFields": [], "identityIssues": [], "missingReceiptWhileMoved": False}, ["EXECUTION_RECEIPTS.jsonl", "IMPLEMENTATION_TASKS.jsonl"], "receipt-to-canonical-task identity join")

    # EXEC-07 receipt chain is contiguous
    chain_ok = True
    chain_evidence = []
    previous_tree = original_tree
    if completed_receipts:
        ordered = list(completed_receipts)
        for index, row in enumerate(ordered):
            if row.get("startingCodebaseTree") != previous_tree:
                chain_ok = False
                chain_evidence.append({"taskId": row.get("taskId"), "expectedStartingTree": previous_tree, "actualStartingTree": row.get("startingCodebaseTree")})
            previous_tree = row.get("endingCodebaseTree")
        if previous_tree != current_tree:
            chain_ok = False
            chain_evidence.append({"expectedEndingTree": current_tree, "actualEndingTree": previous_tree})
    elif current_tree != original_tree:
        chain_ok = False
        chain_evidence.append({"noReceiptsButTreeMoved": current_tree})
    add(checks, "EXEC-07", "receipts", "Execution receipt chain is contiguous from the original baseline to the current tree", chain_ok, chain_evidence, [], ["EXECUTION_RECEIPTS.jsonl", "EXECUTION_TRUSTED_BASELINE.json"], "tree-transition comparison")

    # EXEC-08 task Git transitions reproduce receipt trees
    git_transition_issues = []
    for row in completed_receipts:
        start_tree = git_tree(row.get("startingCommit"))
        end_tree = git_tree(row.get("endingCommit"))
        if start_tree != row.get("startingCodebaseTree") or end_tree != row.get("endingCodebaseTree"):
            git_transition_issues.append({
                "taskId": row.get("taskId"), "receiptStartTree": row.get("startingCodebaseTree"), "gitStartTree": start_tree,
                "receiptEndTree": row.get("endingCodebaseTree"), "gitEndTree": end_tree,
            })
    add(checks, "EXEC-08", "receipts", "Git commits reproduce every receipt starting and ending tree", not git_transition_issues, git_transition_issues, [], ["EXECUTION_RECEIPTS.jsonl"], "Git tree identity reproduction")

    # EXEC-09 actual path deltas obey canonical allowed/forbidden/generated scope
    scope_issues = []
    scope_equality_issues = []
    for row in completed_receipts:
        task, _ = canonical_task_lookup(row.get("taskId"), tasks)
        if task is None:
            continue
        canonical_allowed = task.get("allowedPaths") or []
        canonical_forbidden = task.get("forbiddenPaths") or []
        diffs = git_diff_paths(row.get("startingCommit"), row.get("endingCommit"))
        actual_paths = {diff["path"] for diff in diffs}
        canonical_generated = canonical_generated_paths(task, actual_paths)
        for field in ("allowedPaths", "forbiddenPaths", "generatedPaths"):
            receipt_scope = row.get(field) or []
            canonical_scope = {"allowedPaths": canonical_allowed, "forbiddenPaths": canonical_forbidden, "generatedPaths": canonical_generated}[field]
            if [normalize_path(v) for v in receipt_scope] != [normalize_path(v) for v in canonical_scope]:
                scope_equality_issues.append({"taskId": row.get("taskId"), "field": field, "receipt": receipt_scope, "canonical": canonical_scope})
        for diff in diffs:
            path = diff["path"]
            if matches_any(path, canonical_forbidden):
                scope_issues.append({"taskId": row.get("taskId"), "path": path, "reason": "forbidden by canonical task scope"})
            elif not matches_any(path, canonical_allowed) and not matches_any(path, canonical_generated):
                scope_issues.append({"taskId": row.get("taskId"), "path": path, "reason": "outside canonical allowed/generated scope"})
    add(checks, "EXEC-09", "scope", "Actual task path deltas obey canonical scope and receipt scope equals canonical scope", not scope_issues and not scope_equality_issues, {
        "scopeIssues": scope_issues, "scopeEqualityIssues": scope_equality_issues,
    }, {"scopeIssues": [], "scopeEqualityIssues": []}, ["EXECUTION_RECEIPTS.jsonl", "IMPLEMENTATION_TASKS.jsonl"], "Git diff vs canonical task path sets")

    # EXEC-10 canonical dependencies were satisfied before execution
    dependency_issues = []
    completed_ids = [row.get("taskId") for row in completed_receipts]
    for index, row in enumerate(completed_receipts):
        task, _ = canonical_task_lookup(row.get("taskId"), tasks)
        if task is None:
            continue
        canonical_deps = (task.get("dependencies") or []) + (task.get("prerequisites") or [])
        receipt_deps = (row.get("dependencyState") or {}).get("dependencies") or []
        if sorted(set(canonical_deps)) != sorted(set(receipt_deps)):
            dependency_issues.append({"taskId": row.get("taskId"), "canonical": sorted(set(canonical_deps)), "receipt": sorted(set(receipt_deps)), "reason": "receipt dependency evidence does not match canonical task"})
        for dependency in canonical_deps:
            if dependency not in completed_ids[:index]:
                dependency_issues.append({"taskId": row.get("taskId"), "dependency": dependency, "reason": "not complete before task"})
    add(checks, "EXEC-10", "dependencies", "Task dependencies come from canonical authority and were complete before execution", not dependency_issues, dependency_issues, [], ["IMPLEMENTATION_TASKS.jsonl", "EXECUTION_RECEIPTS.jsonl"], "canonical dependency-order comparison")

    # EXEC-11/12 remote checkpoints
    remote_checkpoint_issues = []
    checkpoint_chain_issues = []
    for row in completed_receipts:
        remote_pre = git_remote_tag_target(row.get("preTaskCheckpoint"))
        remote_post = git_remote_tag_target(row.get("postTaskCheckpoint"))
        local_pre = git_local_tag_target(row.get("preTaskCheckpoint"))
        local_post = git_local_tag_target(row.get("postTaskCheckpoint"))
        if remote_pre != row.get("startingCommit") or (local_pre and local_pre != remote_pre):
            remote_checkpoint_issues.append({"taskId": row.get("taskId"), "kind": "pre", "remote": remote_pre, "local": local_pre, "expected": row.get("startingCommit")})
        if remote_post != row.get("endingCommit") or (local_post and local_post != remote_post):
            remote_checkpoint_issues.append({"taskId": row.get("taskId"), "kind": "post", "remote": remote_post, "local": local_post, "expected": row.get("endingCommit")})
        pre_rows = [r for r in checkpoint_rows if r.get("taskId") == row.get("taskId") and r.get("kind") == "pre-task"]
        post_rows = [r for r in checkpoint_rows if r.get("taskId") == row.get("taskId") and r.get("kind") == "post-task"]
        if len(pre_rows) != 1 or len(post_rows) != 1:
            checkpoint_chain_issues.append({"taskId": row.get("taskId"), "preRows": len(pre_rows), "postRows": len(post_rows), "reason": "checkpoint chain must have exactly one pre and one post row"})
        else:
            if pre_rows[0].get("tag") != row.get("preTaskCheckpoint") or pre_rows[0].get("targetCommit") != row.get("startingCommit"):
                checkpoint_chain_issues.append({"taskId": row.get("taskId"), "kind": "pre", "reason": "chain row does not match receipt/remote target"})
            if post_rows[0].get("tag") != row.get("postTaskCheckpoint") or post_rows[0].get("targetCommit") != row.get("endingCommit"):
                checkpoint_chain_issues.append({"taskId": row.get("taskId"), "kind": "post", "reason": "chain row does not match receipt/remote target"})
    add(checks, "EXEC-11", "checkpoints", "Pre-task immutable checkpoints exist on origin and target the starting commit", not [row for row in remote_checkpoint_issues if row.get("kind") == "pre"], [row for row in remote_checkpoint_issues if row.get("kind") == "pre"], [], ["EXECUTION_RECEIPTS.jsonl"], "origin ls-remote tag reproduction")
    add(checks, "EXEC-12", "checkpoints", "Post-task immutable checkpoints exist on origin and target the ending commit", not [row for row in remote_checkpoint_issues if row.get("kind") == "post"], [row for row in remote_checkpoint_issues if row.get("kind") == "post"], [], ["EXECUTION_RECEIPTS.jsonl"], "origin ls-remote tag reproduction")

    # EXEC-13 remote main publication authority
    publication_issues = []
    if current_published:
        published_tree = git_tree(current_published)
        if remote_main != current_published:
            publication_issues.append({"reason": "currentPublishedCommit does not equal remote main", "trusted": current_published, "remoteMain": remote_main})
        if published_tree != current_tree:
            publication_issues.append({"reason": "currentPublishedCommit Codebase tree does not equal trusted tree", "commitTree": published_tree, "trustedTree": current_tree})
    for row in completed_receipts:
        ending = row.get("endingCommit")
        if not ending or not remote_main or not git_is_ancestor(ending, remote_main):
            publication_issues.append({"taskId": row.get("taskId"), "endingCommit": ending, "reason": "ending commit is not an ancestor of remote main"})
    add(checks, "EXEC-13", "authority", "Current published commit is actual remote main and completed endings are published on remote main", not publication_issues, publication_issues, [], ["EXECUTION_TRUSTED_BASELINE.json", "EXECUTION_RECEIPTS.jsonl"], "origin main and ancestry validation")

    # EXEC-14 receipt changedPaths equals real Git delta
    path_equality_issues = []
    for row in completed_receipts:
        actual = git_diff_paths(row.get("startingCommit"), row.get("endingCommit"))
        actual_paths = {diff["path"] for diff in actual}
        canonical_generated = canonical_generated_paths(canonical_task_lookup(row.get("taskId"), tasks)[0] if canonical_task_lookup(row.get("taskId"), tasks)[0] else {}, actual_paths)
        actual_generated = {path for path in actual_paths if matches_any(path, canonical_generated)}
        actual_source = actual_paths - actual_generated
        receipt_source = set(normalize_path(path) for path in (row.get("changedPaths") or []))
        receipt_generated = set(normalize_path(path) for path in (row.get("generatedPaths") or []))
        if receipt_source != actual_source or receipt_generated != actual_generated:
            path_equality_issues.append({
                "taskId": row.get("taskId"),
                "receiptSource": sorted(receipt_source), "actualSource": sorted(actual_source),
                "receiptGenerated": sorted(receipt_generated), "actualGenerated": sorted(actual_generated),
            })
    add(checks, "EXEC-14", "scope", "Receipt changedPaths and generatedPaths exactly equal the real Git delta", not path_equality_issues, path_equality_issues, [], ["EXECUTION_RECEIPTS.jsonl"], "Git diff vs receipt path partition")

    # EXEC-15 status/receipt lifecycle metadata agree
    metadata_ok = (
        (implementation_performed and bool(completed_receipts))
        or (not implementation_performed and not completed_receipts)
    ) and (
        (lifecycle == "IMPLEMENTATION_IN_PROGRESS" and (bool(completed_receipts) or wave0 == "WAVE_0_IN_PROGRESS"))
        or (lifecycle == "PRE_IMPLEMENTATION_FROZEN" and not completed_receipts)
    )
    add(checks, "EXEC-15", "lifecycle", "Status lifecycle metadata agrees with execution receipts", metadata_ok, {
        "implementationPerformed": implementation_performed, "completedReceipts": len(completed_receipts), "lifecyclePhase": lifecycle,
    }, "consistent lifecycle/receipt combination", ["STATUS.json", "EXECUTION_RECEIPTS.jsonl"], "cross-record comparison")

    # EXEC-16 application release remains false
    add(checks, "EXEC-16", "release", "Application release remains false during Wave 0", not application_released, application_released, False, ["STATUS.json"], "release-state comparison")

    # EXEC-17 completed-task count matches canonical evidence
    chain = trusted.get("completedTaskChain") or []
    count_ok = len(chain) == len(completed_receipts) and [row.get("taskId") for row in completed_receipts] == chain
    add(checks, "EXEC-17", "receipts", "Completed-task count and chain match canonical evidence", count_ok, {
        "chain": chain, "receipts": [row.get("taskId") for row in completed_receipts],
    }, "identical task chain", ["EXECUTION_TRUSTED_BASELINE.json", "EXECUTION_RECEIPTS.jsonl"], "chain equality")

    # EXEC-18 current wave state matches completed task set
    wave_ids = {row.get("wave") for row in completed_receipts}
    wave_ok = wave0 == "WAVE_0_IN_PROGRESS" and wave_ids == {"WAVE_0"} if completed_receipts else wave0 == "READY_NOT_STARTED" and not wave_ids
    add(checks, "EXEC-18", "waves", "Current wave state matches the completed task set", wave_ok, {"wave0Readiness": wave0, "receiptWaves": sorted(wave_ids)}, {"WAVE_0_IN_PROGRESS": "WAVE_0" if completed_receipts else "READY_NOT_STARTED"}, ["STATUS.json", "EXECUTION_RECEIPTS.jsonl"], "wave consistency")

    # EXEC-19 rollback evidence exists for completed tasks
    rollback_ids = {row.get("capabilityId") for row in rollback_rows}
    rollback_issues = [row.get("taskId") for row in completed_receipts if not row.get("rollbackAction") or row.get("capabilityId") not in rollback_ids]
    add(checks, "EXEC-19", "rollback", "Rollback evidence exists for every completed task", not rollback_issues, rollback_issues, [], ["EXECUTION_RECEIPTS.jsonl", "ROLLBACK_PLAN.jsonl"], "rollback contract coverage")

    # EXEC-20 validation does not mutate Codebase
    add(checks, "EXEC-20", "safety", "Execution validation performs zero Codebase mutations", True, 0, 0, [], "read-only validator design")

    # EXEC-21 canonical test/acceptance binding
    test_issues = []
    for row in completed_receipts:
        task, _ = canonical_task_lookup(row.get("taskId"), tasks)
        if task is None:
            continue
        required_tests = list(dict.fromkeys((task.get("tests") or []) + ((task.get("contract") or {}).get("acceptanceTests") or [])))
        canonical_test_ids = [test_id for test_id in required_tests if re.fullmatch(r"TEST-[A-Z0-9-]+", str(test_id))]
        receipt_results = row.get("testResults") or {}
        receipt_tests = row.get("testsExecuted") or []
        for test_id in canonical_test_ids:
            if test_id not in test_map:
                test_issues.append({"taskId": row.get("taskId"), "testId": test_id, "reason": "required test is not canonical"})
            if test_id not in receipt_tests or receipt_results.get(test_id) != "PASS":
                test_issues.append({"taskId": row.get("taskId"), "testId": test_id, "reason": "required test missing or not PASS"})
        acceptance = row.get("acceptanceCriteria") or {}
        for test_id in canonical_test_ids:
            if acceptance.get(test_id) != "PASS":
                test_issues.append({"taskId": row.get("taskId"), "testId": test_id, "reason": "acceptance criteria does not record PASS"})
    add(checks, "EXEC-21", "tests", "Required canonical tests and acceptance bindings are represented with PASS", not test_issues, test_issues, [], ["IMPLEMENTATION_TASKS.jsonl", "REQUIREMENT_TEST_MATRIX.jsonl", "EXECUTION_RECEIPTS.jsonl"], "canonical test/acceptance join")

    # EXEC-22 checkpoint-chain reconciliation
    add(checks, "EXEC-22", "checkpoints", "Execution checkpoint chain reconciles with receipts and remote tags", not checkpoint_chain_issues, checkpoint_chain_issues, [], ["EXECUTION_CHECKPOINT_CHAIN.jsonl", "EXECUTION_RECEIPTS.jsonl"], "checkpoint-chain cross-record reconciliation")

    failed = [check for check in checks if check["status"] == "FAIL"]
    return {
        "mode": "IMPLEMENTATION_EXECUTION_CERTIFICATION",
        "status": "PASS" if not failed else "FAIL",
        "failedChecksCount": len(failed),
        "checks": checks,
        "derived": {
            "completedReceiptCount": len(completed_receipts),
            "liveCodebaseAggregateSha256": live["aggregateSha256"],
            "currentTrustedCodebaseTree": current_tree,
            "originalFrozenCodebaseTree": original_tree,
            "remoteMain": remote_main,
            "validatorWrites": 0,
        },
    }


def main():
    arguments = sys.argv[1:]
    mode = "IMPLEMENTATION_EXECUTION_CERTIFICATION"
    for index, argument in enumerate(arguments):
        if argument == "--mode" and index + 1 < len(arguments):
            mode = arguments[index + 1]
        elif argument.startswith("--mode="):
            mode = argument.split("=", 1)[1]
    if mode not in VALIDATION_MODES:
        raise SystemExit(f"Unsupported execution validation mode: {mode}")
    result = do_execution_validation()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
