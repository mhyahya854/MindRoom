"""Adversarial and positive challenge suite for execution-aware certification.

All fixtures are created in one disposable temporary clone. The live
repository and main Codebase are never mutated by this script.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
REAL_REPO = ROOT.parent
WIP_CANDIDATE = "1d72af0369db92402301e16a4d5cbd1acb2bd3ff"
ORIGINAL_FROZEN_CODEBASE_TREE = "bbf383e3418da4f613f58719160bb7cbd5709ffc"
ORIGINAL_FROZEN_AGGREGATE = "91600fc76001d8b2c108634d4fa3ceca5e743176f103a44d21b7e0e7273ec748"

EXECUTION_FILES = [
    "00 Execution Control/schemas/execution-state.schema.json",
    "00 Execution Control/schemas/execution-receipt.schema.json",
    "00 Execution Control/schemas/execution-trusted-baseline.schema.json",
    "11 Completion/EXECUTION_GOVERNANCE_ARCHITECTURE.md",
    "11 Completion/EXECUTION_AUTHORIZATION_RECORD.json",
    "11 Completion/EXECUTION_RECEIPTS.jsonl",
    "11 Completion/EXECUTION_CHECKPOINT_CHAIN.jsonl",
    "11 Completion/EXECUTION_TRUSTED_BASELINE.json",
    "11 Completion/validate_execution_state.py",
    "11 Completion/verify_execution_state.py",
]

WIP_FILES = [
    "Codebase/packages/common/mindroom/package.json",
    "Codebase/packages/common/mindroom/src/index.ts",
    "Codebase/packages/common/mindroom/tsconfig.json",
    "Codebase/yarn.lock",
]


def run(args, cwd, check=True):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {result.stderr.strip()}")
    return result


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def aggregate_codebase(fixture):
    codebase = fixture / "Codebase"
    records = []
    display = os.path.abspath(codebase)
    scan_root = display if not os.name == "nt" or display.startswith("\\\\?\\") else "\\\\?\\" + display

    def walk(current):
        try:
            entries = list(os.scandir(current))
        except OSError:
            return
        for entry in entries:
            entry_path = os.path.join(current, entry.name)
            try:
                if entry.is_dir(follow_symlinks=False):
                    walk(entry_path)
                elif entry.is_file(follow_symlinks=False):
                    relative = os.path.relpath(entry_path, scan_root).replace("\\", "/")
                    records.append({"path": relative, "sha256": sha256_file(entry_path)})
            except OSError:
                continue

    walk(scan_root)
    records.sort(key=lambda row: row["path"])
    return sha256_text("\n".join(f"{row['path']}:{row['sha256']}" for row in records))


def fresh_fixture():
    temp_root = Path(tempfile.mkdtemp(prefix="mindroom-exec-governance-fixture-"))
    fixture = temp_root / "repo"
    run(["git", "clone", "--no-checkout", str(REAL_REPO), str(fixture)], REAL_REPO)
    run(["git", "-C", str(fixture), "config", "core.longpaths", "true"], REAL_REPO)
    run(["git", "-C", str(fixture), "checkout", "-f", "main"], REAL_REPO)
    for relative in EXECUTION_FILES:
        source = ROOT / relative
        if not source.exists():
            raise RuntimeError(f"missing execution governance file: {relative}")
        destination = fixture / "Graphify" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    run(["git", "-C", str(fixture), "add", "--", "Graphify/00 Execution Control/schemas/execution-state.schema.json", "Graphify/00 Execution Control/schemas/execution-receipt.schema.json", "Graphify/00 Execution Control/schemas/execution-trusted-baseline.schema.json", "Graphify/11 Completion/EXECUTION_GOVERNANCE_ARCHITECTURE.md", "Graphify/11 Completion/EXECUTION_AUTHORIZATION_RECORD.json", "Graphify/11 Completion/EXECUTION_RECEIPTS.jsonl", "Graphify/11 Completion/EXECUTION_CHECKPOINT_CHAIN.jsonl", "Graphify/11 Completion/EXECUTION_TRUSTED_BASELINE.json", "Graphify/11 Completion/validate_execution_state.py", "Graphify/11 Completion/verify_execution_state.py"], REAL_REPO)
    run(["git", "-C", str(fixture), "-c", "user.name=MindRoom Test", "-c", "user.email=test@mindroom.local", "commit", "-m", "Fixture execution governance base"], REAL_REPO)
    return fixture


def apply_wip_candidate(fixture):
    for relative in WIP_FILES:
        content = run(["git", "show", f"{WIP_CANDIDATE}:{relative}"], REAL_REPO).stdout
        destination = fixture / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def commit_task(fixture, original_commit):
    unique = os.urandom(4).hex()
    pre_tag = f"mindroom-backup/wave0/pre-task/MR-IMPL-BOOTSTRAP-001-fixture-{original_commit[:10]}-{unique}"
    run(["git", "-C", str(fixture), "tag", pre_tag, original_commit], REAL_REPO)
    run(["git", "-C", str(fixture), "add", "--", "Codebase"], REAL_REPO)
    run(["git", "-C", str(fixture), "-c", "user.name=MindRoom Test", "-c", "user.email=test@mindroom.local", "commit", "-m", "Modeled MR-IMPL-BOOTSTRAP-001 execution candidate"], REAL_REPO)
    ending = run(["git", "-C", str(fixture), "rev-parse", "HEAD"], REAL_REPO).stdout.strip()
    ending_tree = run(["git", "-C", str(fixture), "rev-parse", f"{ending}:Codebase"], REAL_REPO).stdout.strip()
    post_tag = f"mindroom-backup/wave0/task/MR-IMPL-BOOTSTRAP-001-complete-fixture-{ending[:10]}-{unique}"
    run(["git", "-C", str(fixture), "tag", post_tag, ending], REAL_REPO)
    return ending, ending_tree, pre_tag, post_tag


def configure_execution_state(fixture, original_commit, ending_commit, ending_tree, pre_tag=None, post_tag=None, mutate=None):
    aggregate = aggregate_codebase(fixture)
    status_path = fixture / "Graphify" / "00 Execution Control" / "STATUS.json"
    status = json.loads(status_path.read_text(encoding="utf-8-sig"))
    status.update({
        "lifecyclePhase": "IMPLEMENTATION_IN_PROGRESS",
        "wave0Readiness": "WAVE_0_IN_PROGRESS",
        "codebaseExecutionStatus": "AUTHORIZED",
        "implementationPerformed": True,
        "applicationReleased": False,
    })

    auth_path = fixture / "Graphify" / "11 Completion" / "EXECUTION_AUTHORIZATION_RECORD.json"
    authorization = {
        "schemaVersion": 1,
        "authorizationState": "ACTIVE",
        "authorizedWave": "WAVE_0",
        "authorizationType": "EXPLICIT_USER_AUTHORIZATION",
        "authorizedAt": "2026-08-16T00:00:00+03:00",
        "preAuthorizationMain": original_commit,
        "preAuthorizationCodebaseTree": ORIGINAL_FROZEN_CODEBASE_TREE,
        "authorizationHistory": [],
    }

    baseline_path = fixture / "Graphify" / "11 Completion" / "EXECUTION_TRUSTED_BASELINE.json"
    baseline = {
        "schemaVersion": 1,
        "originalFrozenCodebaseTree": ORIGINAL_FROZEN_CODEBASE_TREE,
        "currentTrustedCodebaseTree": ending_tree,
        "currentTrustedAggregateSha256": aggregate,
        "lastCompletedTask": "MR-IMPL-BOOTSTRAP-001",
        "currentPublishedCommit": ending_commit,
        "completedTaskChain": ["MR-IMPL-BOOTSTRAP-001"],
        "originalFrozenBaseline": {
            "fileCount": 10080,
            "directoryCount": 2548,
            "aggregateSha256": ORIGINAL_FROZEN_AGGREGATE,
        },
    }

    receipt_path = fixture / "Graphify" / "11 Completion" / "EXECUTION_RECEIPTS.jsonl"
    changed_paths = [
        "Codebase/packages/common/mindroom/package.json",
        "Codebase/packages/common/mindroom/src/index.ts",
        "Codebase/packages/common/mindroom/tsconfig.json",
        "Codebase/yarn.lock",
    ]
    receipt = {
        "taskId": "MR-IMPL-BOOTSTRAP-001",
        "capabilityId": "MR-CAP-001",
        "wave": "WAVE_0",
        "startingCommit": original_commit,
        "endingCommit": ending_commit,
        "startingCodebaseTree": ORIGINAL_FROZEN_CODEBASE_TREE,
        "endingCodebaseTree": ending_tree,
        "preTaskCheckpoint": pre_tag or f"mindroom-backup/wave0/pre-task/MR-IMPL-BOOTSTRAP-001-fixture-{original_commit[:10]}",
        "postTaskCheckpoint": post_tag or f"mindroom-backup/wave0/task/MR-IMPL-BOOTSTRAP-001-complete-fixture-{ending_commit[:10]}",
        "changedPaths": changed_paths,
        "allowedPaths": [
            "Codebase/packages/common/mindroom/package.json",
            "Codebase/packages/common/mindroom/tsconfig.json",
            "Codebase/packages/common/mindroom/src/index.ts",
            "Codebase/package.json",
            "Codebase/.yarnrc.yml",
        ],
        "forbiddenPaths": ["Codebase/packages/frontend/core/**"],
        "generatedPaths": ["Codebase/yarn.lock"],
        "testsExecuted": ["TEST-MR-BOOTSTRAP-001"],
        "testResults": {"TEST-MR-BOOTSTRAP-001": "PASS"},
        "acceptanceCriteria": {"TEST-MR-BOOTSTRAP-001": "PASS"},
        "rollbackAction": "REVERT_PACKAGE_BOOTSTRAP",
        "dependencyState": {"prerequisitesComplete": True, "dependencies": []},
        "publishedToMain": True,
        "status": "COMPLETE",
    }

    chain_path = fixture / "Graphify" / "11 Completion" / "EXECUTION_CHECKPOINT_CHAIN.jsonl"
    chain = [
        {"kind": "pre-task", "taskId": "MR-IMPL-BOOTSTRAP-001", "tag": receipt["preTaskCheckpoint"], "targetCommit": original_commit},
        {"kind": "post-task", "taskId": "MR-IMPL-BOOTSTRAP-001", "tag": receipt["postTaskCheckpoint"], "targetCommit": ending_commit},
    ]
    if mutate:
        mutate({"authorization": authorization, "baseline": baseline, "receipt": receipt, "status": status, "chain": chain})
    write_json(status_path, status)
    write_json(auth_path, authorization)
    write_json(baseline_path, baseline)
    write_jsonl(receipt_path, [receipt])
    write_jsonl(chain_path, chain)


def run_execution_validator(fixture):
    validator = fixture / "Graphify" / "11 Completion" / "validate_execution_state.py"
    result = run([sys.executable, str(validator), "--mode", "IMPLEMENTATION_EXECUTION_CERTIFICATION"], fixture, check=False)
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        parsed = {"status": "FAIL", "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    parsed["returncode"] = result.returncode
    return parsed


def run_final_freeze_validator(fixture):
    validator = fixture / "Graphify" / "11 Completion" / "validate_final_graphify_freeze.py"
    result = run([sys.executable, str(validator), "--mode", "FINAL_FREEZE_CERTIFICATION", "--verify-only"], fixture, check=False)
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        parsed = {"status": "FAIL", "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    parsed["returncode"] = result.returncode
    return parsed


def failed_ids(result):
    return {check["checkId"] for check in result.get("checks", []) if check.get("status") == "FAIL"}


def prepare_task_branch(fixture, branch):
    run(["git", "-C", str(fixture), "checkout", "-f", "main"], REAL_REPO)
    run(["git", "-C", str(fixture), "checkout", "-b", branch], REAL_REPO)
    original = run(["git", "-C", str(fixture), "rev-parse", "HEAD"], REAL_REPO).stdout.strip()
    apply_wip_candidate(fixture)
    ending, ending_tree, pre_tag, post_tag = commit_task(fixture, original)
    run(["git", "-C", str(fixture), "branch", "-f", "main", ending], REAL_REPO)
    run(["git", "-C", str(fixture), "checkout", "main"], REAL_REPO)
    return fixture, original, ending, ending_tree, pre_tag, post_tag


def cleanup_branch(fixture, branch, original):
    run(["git", "-C", str(fixture), "checkout", "-f", branch], REAL_REPO)
    run(["git", "-C", str(fixture), "branch", "-f", "main", original], REAL_REPO)
    run(["git", "-C", str(fixture), "checkout", "-f", "main"], REAL_REPO)
    run(["git", "-C", str(fixture), "branch", "-D", branch], REAL_REPO, check=False)


def positive_bootstrap():
    fixture = fresh_fixture()
    branch = "challenge-pos-bootstrap"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag)
    execution = run_execution_validator(fixture)
    freeze = run_final_freeze_validator(fixture)
    cleanup_branch(fixture, branch, original)
    return {
        "challengeId": "EXEC-CHALLENGE-POS-001",
        "mutation": "Modeled legitimate bootstrap task with complete receipt chain",
        "expectedStatus": "PASS",
        "actualStatus": execution.get("status"),
        "failedCheckIds": sorted(failed_ids(execution)),
        "finalFreezeStatus": freeze.get("status"),
        "finalFreezeFailedCheckIds": sorted(failed_ids(freeze)),
        "passed": execution.get("status") == "PASS" and freeze.get("status") == "FAIL",
    }


def untouched_main():
    execution = run_execution_validator(REAL_REPO)
    freeze = run_final_freeze_validator(REAL_REPO)
    return {
        "challengeId": "EXEC-CHALLENGE-POS-002",
        "mutation": "Current untouched main remains valid pre-start",
        "expectedStatus": "FAIL",
        "actualStatus": execution.get("status"),
        "finalFreezeStatus": freeze.get("status"),
        "passed": freeze.get("status") == "PASS",
    }


def negative_challenges():
    fixture = fresh_fixture()
    results = []

    def finish(branch, challenge_id, mutation, expected_failed, result):
        actual = sorted(failed_ids(result))
        results.append({
            "challengeId": challenge_id,
            "mutation": mutation,
            "expectedStatus": "FAIL",
            "actualStatus": result.get("status"),
            "failedCheckIds": actual,
            "expectedFailedCheckIds": sorted(expected_failed),
            "passed": result.get("status") == "FAIL" and set(expected_failed).issubset(set(actual)),
        })
        cleanup_branch(fixture, branch, original)

    branch = "challenge-001"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    (fixture / "Codebase" / "packages" / "common" / "mindroom" / "unexpected.txt").write_text("unauthorized", encoding="utf-8")
    ending, ending_tree, pre_tag, post_tag = commit_task(fixture, original)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag)
    finish(branch, "EXEC-CHALLENGE-001", "Unauthorized Codebase path mutation", ["EXEC-09", "EXEC-14"], run_execution_validator(fixture))

    branch = "challenge-002"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag)
    (fixture / "Graphify" / "11 Completion" / "EXECUTION_RECEIPTS.jsonl").write_text("", encoding="utf-8")
    finish(branch, "EXEC-CHALLENGE-002", "Missing execution receipt", ["EXEC-06", "EXEC-07", "EXEC-13", "EXEC-14", "EXEC-15"], run_execution_validator(fixture))

    branch = "challenge-003"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: (state["receipt"].__setitem__("endingCodebaseTree", "0" * 40), state["baseline"].__setitem__("currentTrustedCodebaseTree", "0" * 40)))
    finish(branch, "EXEC-CHALLENGE-003", "Fake receipt with wrong ending tree", ["EXEC-05", "EXEC-08"], run_execution_validator(fixture))

    branch = "challenge-004"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: state["receipt"].__setitem__("status", "BLOCKED"))
    finish(branch, "EXEC-CHALLENGE-004", "Non-complete receipt is not treated as completed", ["EXEC-06", "EXEC-13", "EXEC-15"], run_execution_validator(fixture))

    branch = "challenge-005"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: state["baseline"].__setitem__("currentTrustedCodebaseTree", "1" * 40))
    finish(branch, "EXEC-CHALLENGE-005", "Broken task chain ending tree", ["EXEC-05", "EXEC-07"], run_execution_validator(fixture))

    branch = "challenge-006"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: state["receipt"].__setitem__("dependencyState", {"prerequisitesComplete": True, "dependencies": ["MR-IMPL-001"]}))
    finish(branch, "EXEC-CHALLENGE-006", "Dependency violation for completed task", ["EXEC-10"], run_execution_validator(fixture))

    branch = "challenge-007"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: state["receipt"].__setitem__("preTaskCheckpoint", "mindroom-backup/wave0/pre-task/NO_SUCH_TAG"))
    finish(branch, "EXEC-CHALLENGE-007", "Missing pre-task checkpoint", ["EXEC-11"], run_execution_validator(fixture))

    branch = "challenge-008"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: state["receipt"].__setitem__("publishedToMain", False))
    finish(branch, "EXEC-CHALLENGE-008", "Failed WIP branch promoted implicitly", ["EXEC-06", "EXEC-13", "EXEC-15"], run_execution_validator(fixture))

    branch = "challenge-009"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    def stale_status(state):
        state["status"].update({"lifecyclePhase": "PRE_IMPLEMENTATION_FROZEN", "wave0Readiness": "READY_NOT_STARTED", "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION", "implementationPerformed": False})
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=stale_status)
    finish(branch, "EXEC-CHALLENGE-009", "Stale pre-start status after Codebase change", ["EXEC-01", "EXEC-15", "EXEC-18"], run_execution_validator(fixture))

    branch = "challenge-010"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=lambda state: state["status"].__setitem__("applicationReleased", True))
    finish(branch, "EXEC-CHALLENGE-010", "Premature application release during Wave 0", ["EXEC-16"], run_execution_validator(fixture))

    branch = "challenge-011"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    def baseline_overwrite(state):
        state["baseline"]["originalFrozenCodebaseTree"] = state["receipt"]["endingCodebaseTree"]
        state["baseline"]["originalFrozenBaseline"]["aggregateSha256"] = "0" * 64
    configure_execution_state(fixture, original, ending, ending_tree, pre_tag, post_tag, mutate=baseline_overwrite)
    finish(branch, "EXEC-CHALLENGE-011", "Baseline overwrite attack", ["EXEC-03"], run_execution_validator(fixture))

    branch = "challenge-012"
    fixture, original, ending, ending_tree, pre_tag, post_tag = prepare_task_branch(fixture, branch)
    freeze = run_final_freeze_validator(fixture)
    results.append({
        "challengeId": "EXEC-CHALLENGE-012",
        "mutation": "Freeze-mode weakening: mutated Codebase must fail FINAL_FREEZE_CERTIFICATION",
        "expectedStatus": "FAIL",
        "actualStatus": freeze.get("status"),
        "failedCheckIds": sorted(failed_ids(freeze)),
        "passed": freeze.get("status") == "FAIL",
    })
    cleanup_branch(fixture, branch, original)
    return results


def main():
    arguments = sys.argv[1:]
    positive = []
    if "--positive" in arguments or not arguments:
        positive.append(untouched_main())
        positive.append(positive_bootstrap())
    negative = negative_challenges() if "--negative" in arguments or not arguments else []
    report = {
        "reportId": "mindroom-execution-governance-challenges",
        "validatorSourceHash": sha256_file(ROOT / "11 Completion" / "validate_execution_state.py"),
        "challengeSourceHash": sha256_file(Path(__file__).resolve()),
        "verdict": "PASS" if all(row["passed"] for row in positive + negative) else "FAIL",
        "positiveChallenges": positive,
        "negativeChallenges": negative,
        "baselineFailuresSubtracted": False,
        "environmentExemptions": [],
        "documentedEnvironmentFailures": [],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
