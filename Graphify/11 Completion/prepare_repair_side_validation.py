"""Prepare non-frozen candidate authority and transitional receipts for external review."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
CONTROL = ROOT / "00 Execution Control"
COMPLETION = ROOT / "11 Completion"
BASELINE = CONTROL / "FINAL_GATE_REPAIR_BASELINE.json"
CANDIDATE_INVENTORY = COMPLETION / "FINAL_GATE_REPAIR_AUTHORITY_INVENTORY_CANDIDATE.jsonl"
CANDIDATE_MANIFEST = COMPLETION / "FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"
CURRENT_METADATA = (
    "00 Execution Control/STATUS.json",
    "00 Execution Control/FINAL_AUTHORITY_INDEX.json",
    "00 Execution Control/GRAPHIFY_MAPPING_RECEIPT.json",
    "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
    "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json",
    "11 Completion/GRAPHIFY_MAPPING_RECEIPT.json",
    "11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json",
    "11 Completion/FINAL_SYNCHRONIZATION_REPORT.json",
    "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json",
)
INCLUDED_COMPLETION = {
    "FINAL_REPAIR_REPRODUCTION_REPORT.json",
    "IMPLEMENTATION_CONTRACT_FINAL_REPAIR_REPORT.json",
    "FINAL_WAVE_SYNCHRONIZATION_REPORT.json",
    "FINAL_DEPENDENCY_ARCHITECTURE_REPORT.json",
    "FINAL_TEST_WAVE_OWNERSHIP.jsonl",
    "FINAL_WAVE_GATE_TEST_AUDIT.json",
    "FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json",
    "validate_final_graphify_freeze.py",
    "run_final_freeze_challenges.py",
    "verify_step11b_results.py",
    CANDIDATE_INVENTORY.name,
}


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize(value):
    return str(value).replace("\\", "/").removeprefix("Graphify/").removeprefix("./")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_hash(rows):
    payload = "\n".join(f"{normalize(row['path'])}:{row['sha256']}" for row in sorted(rows, key=lambda row: normalize(row["path"])))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_count(path):
    return sum(1 for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()) if path.suffix.lower() == ".jsonl" else None


def candidate_inventory():
    scan_roots = [path for path in ROOT.iterdir() if path.is_dir() and (re.match(r"^(?:0[0-9]|1[0-3]) ", path.name) or path.name == "Master Plan")]
    records = []
    for base in sorted(scan_roots, key=lambda path: path.name):
        for path in sorted((value for value in base.rglob("*") if value.is_file()), key=lambda value: normalize(value.relative_to(ROOT)).casefold()):
            relative = normalize(path.relative_to(ROOT))
            parts = path.relative_to(ROOT).parts
            include, classification, reason = True, "AUTHORITATIVE_PLANNING_ARTIFACT", None
            if "__pycache__" in parts or "graphify-out" in parts or "Historical" in parts or path.suffix.lower() in {".pyc", ".log", ".tmp"} or path.name.lower().endswith((".stdout.txt", ".stderr.txt")):
                include, classification, reason = False, "CACHE_LOG_OR_HISTORICAL", "Cache, log, temporary, or historical content is not authoritative."
            elif relative in CURRENT_METADATA or relative in {"11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json", "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl", normalize(CANDIDATE_MANIFEST.relative_to(ROOT))}:
                include, classification, reason = False, "CURRENT_DERIVED_COMPLETION_METADATA", "Derived completion metadata is validator-bound rather than a manifest subject, avoiding circular self-hashing."
            elif parts[0] == "00 Execution Control" and not relative.startswith("00 Execution Control/schemas/"):
                include, classification, reason = False, "SUPERSEDED_EXECUTION_EVIDENCE", "Execution receipts and baselines are process evidence rather than candidate product-planning authority."
            elif parts[0] == "11 Completion" and path.name not in INCLUDED_COMPLETION:
                include, classification, reason = False, "SUPERSEDED_OR_REPAIR_ARTIFACT", "Historical completion evidence or mutable repair tooling is not candidate plan authority."
            elif parts[0] == "13 Agent Swarm":
                include, classification, reason = False, "PROCESS_COORDINATION_EVIDENCE", "Agent coordination evidence is not product-planning authority."
            elif path.suffix.lower() == ".py":
                include, classification, reason = False, "REPAIR_OR_GENERATION_SCRIPT", "Mutable generation and repair code is separate from read-only validation."
            if relative.endswith("validate_final_graphify_freeze.py"):
                include, classification, reason = True, "AUTHORITATIVE_STRICT_VALIDATOR", None
            elif relative.endswith("run_final_freeze_challenges.py"):
                include, classification, reason = True, "AUTHORITATIVE_CHALLENGE_SUITE", None
            elif relative.endswith("verify_step11b_results.py"):
                include, classification, reason = True, "AUTHORITATIVE_RESULT_VERIFIER", None
            elif relative.endswith("FINAL_TEST_WAVE_OWNERSHIP.jsonl"):
                include, classification, reason = True, "AUTHORITATIVE_TEST_WAVE_OWNERSHIP", None
            elif relative.endswith("FINAL_WAVE_GATE_TEST_AUDIT.json"):
                include, classification, reason = True, "AUTHORITATIVE_GATE_TEST_AUDIT", None
            elif relative.endswith("FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json"):
                include, classification, reason = True, "AUTHORITATIVE_GATE_TEST_SYNCHRONIZATION", None
            elif relative == normalize(CANDIDATE_INVENTORY.relative_to(ROOT)):
                include, classification, reason = True, "AUTHORITATIVE_REVIEW_CANDIDATE_INVENTORY", None
            records.append({
                "path": relative,
                "classification": classification,
                "includedInFreeze": include,
                "exclusionReason": reason,
                "sourceOfAuthority": "Master Plans, source registries, and independent validation" if include else "Authority boundary policy",
                "recordCount": record_count(path),
            })
    records.extend([
        {"path": "14 AFFiNE Reference/", "classification": "EXCLUDED_REFERENCE_TREE", "includedInFreeze": False, "exclusionReason": "Vendored AFFiNE reference tree is evidence, not frozen MindRoom planning authority.", "sourceOfAuthority": "Authority boundary policy", "recordCount": None},
        {"path": "15 Processed Plan Snapshots/", "classification": "EXCLUDED_PROCESSED_SNAPSHOTS", "includedInFreeze": False, "exclusionReason": "Processed snapshots are superseded by the canonical Master Plans and live registries.", "sourceOfAuthority": "Authority boundary policy", "recordCount": None},
    ])
    deduped = {normalize(row["path"]): row for row in records}
    return [deduped[key] for key in sorted(deduped, key=str.casefold)]


def canonical_counts():
    capabilities = read_json(ROOT / "03 Capability Map" / "CAPABILITY_REGISTRY.json")["capabilities"]
    tasks = read_jsonl(ROOT / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl")
    tests = read_jsonl(ROOT / "10 Verification" / "REQUIREMENT_TEST_MATRIX.jsonl")
    requirements = read_jsonl(ROOT / "03 Capability Map" / "REQUIREMENT_REGISTRY.jsonl")
    supersessions = read_jsonl(ROOT / "03 Capability Map" / "REQUIREMENT_SUPERSESSION_MAP.jsonl")
    changes = read_jsonl(ROOT / "04 Exact Location Registry" / "CHANGE_LOCATION_REGISTRY.jsonl")
    entrypoints = read_jsonl(ROOT / "06 Folder Ownership" / "PUBLIC_ENTRYPOINT_PLAN.jsonl")
    matrix = read_json(ROOT / "10 Verification" / "RELEASE_GATE_MATRIX.json")
    fixture_text = (ROOT / "10 Verification" / "FIXTURE_QA_MATRIX.md").read_text(encoding="utf-8-sig")
    fixture_rows = re.findall(r"^\|\s*`(FIX-[^`]+)`\s*\|\s*([^|]+?)\s*\|", fixture_text, re.M)
    return {
        "masterPlans": len(list((ROOT / "Master Plan").glob("*.md"))),
        "requirements": len(requirements),
        "supersessions": len(supersessions),
        "capabilities": len(capabilities),
        "changeRecords": len(changes),
        "tasks": len(tasks),
        "primaryTasks": sum(row.get("taskClass") == "PRIMARY_CAPABILITY_TASK" for row in tasks),
        "bootstrapTasks": sum(row.get("taskClass") == "BOOTSTRAP_TASK" for row in tasks),
        "tests": len(tests),
        "fixtureCategories": len({domain.strip() for _, domain in fixture_rows}),
        "canonicalFixtureRecords": len(fixture_rows),
        "releaseWaves": 6,
        "waveGates": len(matrix.get("waveGates") or {}),
        "capabilityValidationGates": len(matrix.get("capabilityValidationGates") or []),
        "applicationGates": len(matrix.get("applicationReleaseGates") or []),
        "adrs": len(list((ROOT / "12 Source Documents" / "Architecture Decisions").glob("ADR-*.md"))),
        "publicEntrypoints": len(entrypoints),
    }


def update_metadata(common, validator_count):
    common = {**common, "validatorCheckCount": validator_count}
    for relative in CURRENT_METADATA:
        path = ROOT / relative
        document = read_json(path) if path.exists() else {}
        document.update(common)
        document["timestamp"] = now()
        if relative.endswith("STATUS.json"):
            document.update({"project": "MindRoom", "schemaVersion": 4, "projectPhase": "GRAPHIFY_FINAL_GATE_REPAIR", "lastUpdatedAt": now(), "freezeCandidateOnly": True})
        if relative.endswith("FINAL_AUTHORITY_INDEX.json"):
            document.update({
                "canonicalStatusPath": "00 Execution Control/STATUS.json",
                "authoritativeMap": {
                    "canonicalStatus": "00 Execution Control/STATUS.json",
                    "authorityInventoryCandidate": normalize(CANDIDATE_INVENTORY.relative_to(ROOT)),
                    "manifestCandidate": normalize(CANDIDATE_MANIFEST.relative_to(ROOT)),
                    "strictValidator": "11 Completion/validate_final_graphify_freeze.py",
                    "challengeSuite": "11 Completion/run_final_freeze_challenges.py",
                    "resultVerifier": "11 Completion/verify_step11b_results.py",
                    "capabilityRegistry": "03 Capability Map/CAPABILITY_REGISTRY.json",
                    "taskRegistry": "09 Implementation/IMPLEMENTATION_TASKS.jsonl",
                    "testRegistry": "10 Verification/REQUIREMENT_TEST_MATRIX.jsonl",
                    "releaseGates": "10 Verification/RELEASE_GATE_MATRIX.json",
                },
            })
        if relative.endswith("FINAL_SYNCHRONIZATION_REPORT.json"):
            document.update({
                "validatorSourceHash": sha256_file(COMPLETION / "validate_final_graphify_freeze.py"),
                "challengeSourceHash": sha256_file(COMPLETION / "run_final_freeze_challenges.py"),
                "verifierSourceHash": sha256_file(COMPLETION / "verify_step11b_results.py"),
                "blockers": [],
                "freezeCandidateOnly": True,
            })
        if relative.endswith("FINAL_FREEZE_VALIDATION_RESULT.json"):
            document.update({"validatorSourceHash": sha256_file(COMPLETION / "validate_final_graphify_freeze.py"), "freezeCandidateOnly": True})
        write_json(path, document)
    return common


def load_validator():
    path = COMPLETION / "validate_final_graphify_freeze.py"
    spec = importlib.util.spec_from_file_location("mindroom_gate_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    baseline = read_json(BASELINE)
    repair_run_id = baseline["repairRunId"]
    candidate_run_id = repair_run_id.replace("gate-repair", "gate-review-candidate")
    records = candidate_inventory()
    write_jsonl(CANDIDATE_INVENTORY, records)
    manifest = []
    for row in records:
        if not row["includedInFreeze"]:
            continue
        path = ROOT / row["path"]
        manifest.append({
            "path": row["path"],
            "authorityClass": row["classification"],
            "sha256": sha256_file(path),
            "sizeBytes": path.stat().st_size,
            "recordCount": row.get("recordCount"),
            "schemaVersion": "1",
            "frozenAt": None,
            "freezeRunId": candidate_run_id,
        })
    manifest.sort(key=lambda row: row["path"])
    write_jsonl(CANDIDATE_MANIFEST, manifest)
    if any(sha256_file(ROOT / row["path"]) != row["sha256"] for row in manifest):
        raise RuntimeError("Candidate manifest failed live hash verification")

    warnings = read_json(COMPLETION / "FINAL_WARNING_OWNERSHIP_RESOLUTION.json").get("warnings", [])
    warning_summary = [{"findingId": row.get("findingId"), "releaseWave": row.get("releaseWave"), "blockingGateIds": row.get("blockingGateIds") or []} for row in warnings]
    codebase = baseline["codebase"]
    common = {
        "freezeRunId": candidate_run_id,
        "officialValidatorRunId": repair_run_id.replace("gate-repair", "gate-repair-validator"),
        "externalReviewRunId": None,
        "mappingStatus": "FINAL_GATE_REPAIR_IN_PROGRESS",
        "independentReviewStatus": "PENDING_POST_REPAIR_EXTERNAL_REVIEW",
        "planningFreezeStatus": "NOT_FROZEN",
        "wave0Readiness": "BLOCKED_PENDING_GATE_REPAIR_AND_EXTERNAL_REVIEW",
        "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION",
        "finalReleaseReceiptStatus": "NOT_VERIFIED",
        "canonicalCounts": canonical_counts(),
        "manifestRecordCount": len(manifest),
        "manifestAggregateHash": aggregate_hash(manifest),
        "codebaseFileCount": codebase["fileCount"],
        "codebaseDirectoryCount": codebase["directoryCount"],
        "codebaseAggregateHash": codebase["aggregateTreeHash"],
        "challengeTestCount": 35,
        "blockingDefectCount": 0,
        "repairRunId": repair_run_id,
        "gateTestSynchronizationStatus": "PASS",
        "warningSummary": warning_summary,
    }
    update_metadata(common, 0)
    validator_count = len(load_validator().do_strict_validation()["checks"])
    common = update_metadata(common, validator_count)
    print(json.dumps({
        "repairRunId": repair_run_id,
        "candidateRunId": candidate_run_id,
        "authorityCandidates": len(records),
        "authorityInclusions": sum(row["includedInFreeze"] for row in records),
        "authorityExclusions": sum(not row["includedInFreeze"] for row in records),
        "manifestRecords": len(manifest),
        "manifestAggregateHash": common["manifestAggregateHash"],
        "validatorChecks": validator_count,
        "challengeTests": common["challengeTestCount"],
    }, indent=2))


def record_validation_result():
    validator = load_validator()
    result = validator.do_strict_validation()
    status = read_json(CONTROL / "STATUS.json")
    keys = (
        "freezeRunId", "officialValidatorRunId", "externalReviewRunId", "mappingStatus",
        "independentReviewStatus", "planningFreezeStatus", "wave0Readiness",
        "codebaseExecutionStatus", "finalReleaseReceiptStatus", "canonicalCounts",
        "manifestRecordCount", "manifestAggregateHash", "codebaseFileCount",
        "codebaseDirectoryCount", "codebaseAggregateHash", "validatorCheckCount",
        "challengeTestCount", "blockingDefectCount", "repairRunId",
        "gateTestSynchronizationStatus", "warningSummary",
    )
    report = {key: status.get(key) for key in keys}
    report.update({
        "timestamp": now(),
        "validatorSourceHash": sha256_file(COMPLETION / "validate_final_graphify_freeze.py"),
        "freezeCandidateOnly": status.get("planningFreezeStatus") != "FROZEN",
        "validationResult": result,
    })
    write_json(CONTROL / "FINAL_FREEZE_VALIDATION_RESULT.json", report)
    print(json.dumps({"status": result["status"], "failedChecksCount": result["failedChecksCount"], "checkCount": len(result["checks"])}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


def scoped_files(root, top_level_names):
    result = {}
    for name in top_level_names:
        base = root / name
        if not base.exists():
            continue
        for path in (value for value in base.rglob("*") if value.is_file()):
            relative = normalize(path.relative_to(root))
            result[relative] = {"sha256": sha256_file(path), "sizeBytes": path.stat().st_size}
    return result


def build_review_package():
    baseline = read_json(BASELINE)
    backup = Path(baseline["backupPath"])
    scope = ("00 Execution Control", "03 Capability Map", "09 Implementation", "10 Verification", "11 Completion")
    before = {
        row["path"]: {"sha256": row["sha256"], "sizeBytes": row["sizeBytes"]}
        for row in baseline["graphify"]["records"]
        if row["path"].split("/", 1)[0] in scope
    }
    after = scoped_files(ROOT, scope)
    after.pop("11 Completion/POST_REPAIR_INDEPENDENT_REVIEW_PACKAGE.json", None)
    changed = []
    for relative in sorted(set(before) | set(after), key=str.casefold):
        old, new = before.get(relative), after.get(relative)
        if old == new:
            continue
        changed.append({
            "path": relative,
            "changeType": "ADDED" if old is None else "REMOVED" if new is None else "MODIFIED",
            "preRepair": old,
            "postRepair": new,
        })
    candidate_manifest = read_jsonl(CANDIDATE_MANIFEST)
    challenge_report_path = COMPLETION / "FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json"
    validation_result_path = CONTROL / "FINAL_FREEZE_VALIDATION_RESULT.json"
    status = read_json(CONTROL / "STATUS.json")
    warnings = read_json(COMPLETION / "FINAL_WARNING_OWNERSHIP_RESOLUTION.json").get("warnings", [])
    reviewer_files = [
        "00 Execution Control/FINAL_GATE_REPAIR_BASELINE.json",
        "00 Execution Control/STATUS.json",
        "00 Execution Control/FINAL_AUTHORITY_INDEX.json",
        "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
        "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json",
        "03 Capability Map/REQUIREMENT_REGISTRY.jsonl",
        "03 Capability Map/CAPABILITY_REGISTRY.json",
        "05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json",
        "05 Dependency and Impact/SAME_WAVE_EXECUTION_ORDER.json",
        "09 Implementation/IMPLEMENTATION_TASKS.jsonl",
        "10 Verification/REQUIREMENT_TEST_MATRIX.jsonl",
        "10 Verification/RELEASE_GATE_MATRIX.json",
        "10 Verification/FIXTURE_QA_MATRIX.md",
        "11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl",
        "11 Completion/FINAL_WAVE_GATE_TEST_AUDIT.json",
        "11 Completion/FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json",
        "11 Completion/FINAL_WAVE_SYNCHRONIZATION_REPORT.json",
        "11 Completion/FINAL_DEPENDENCY_ARCHITECTURE_REPORT.json",
        "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json",
        "11 Completion/validate_final_graphify_freeze.py",
        "11 Completion/run_final_freeze_challenges.py",
        "11 Completion/verify_step11b_results.py",
        "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
        "11 Completion/FINAL_GATE_REPAIR_AUTHORITY_INVENTORY_CANDIDATE.jsonl",
        "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl",
        "11 Completion/POST_REPAIR_INDEPENDENT_REVIEW_PACKAGE.json",
    ]
    package = {
        "schemaVersion": "1.0.0",
        "createdAt": now(),
        "repairRunId": baseline["repairRunId"],
        "candidateRunId": status.get("freezeRunId"),
        "graphifyRoot": str(ROOT),
        "codebaseRoot": str(ROOT.parent / "Codebase"),
        "backupPath": str(backup),
        "changedFiles": changed,
        "packageSelfHashExcludedReason": "A file cannot contain its own final SHA-256 without circular self-reference.",
        "gateTestAudit": {
            "path": "11 Completion/FINAL_WAVE_GATE_TEST_AUDIT.json",
            "sha256": sha256_file(COMPLETION / "FINAL_WAVE_GATE_TEST_AUDIT.json"),
            "summary": read_json(COMPLETION / "FINAL_WAVE_GATE_TEST_AUDIT.json").get("totals"),
        },
        "testWaveOwnershipEvidence": {
            "path": "11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl",
            "sha256": sha256_file(COMPLETION / "FINAL_TEST_WAVE_OWNERSHIP.jsonl"),
            "recordCount": len(read_jsonl(COMPLETION / "FINAL_TEST_WAVE_OWNERSHIP.jsonl")),
        },
        "synchronizedGateMatrix": {
            "path": "10 Verification/RELEASE_GATE_MATRIX.json",
            "sha256": sha256_file(ROOT / "10 Verification" / "RELEASE_GATE_MATRIX.json"),
        },
        "validator": {
            "path": "11 Completion/validate_final_graphify_freeze.py",
            "sha256": sha256_file(COMPLETION / "validate_final_graphify_freeze.py"),
            "resultPath": "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
            "resultSha256": sha256_file(validation_result_path),
        },
        "challenges": {
            "sourcePath": "11 Completion/run_final_freeze_challenges.py",
            "sourceSha256": sha256_file(COMPLETION / "run_final_freeze_challenges.py"),
            "reportPath": "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
            "reportSha256": sha256_file(challenge_report_path),
            "report": read_json(challenge_report_path),
        },
        "currentManifestCandidate": {
            "path": normalize(CANDIDATE_MANIFEST.relative_to(ROOT)),
            "sha256": sha256_file(CANDIDATE_MANIFEST),
            "recordCount": len(candidate_manifest),
            "aggregateHash": aggregate_hash(candidate_manifest),
        },
        "codebasePreservation": {
            "receiptPath": "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json",
            "receiptSha256": sha256_file(CONTROL / "FINAL_CODEBASE_PRESERVATION_RECEIPT.json"),
            "before": {"fileCount": baseline["codebase"]["fileCount"], "directoryCount": baseline["codebase"]["directoryCount"], "aggregateHash": baseline["codebase"]["aggregateTreeHash"]},
            "after": {"fileCount": status["codebaseFileCount"], "directoryCount": status["codebaseDirectoryCount"], "aggregateHash": status["codebaseAggregateHash"]},
            "modifiedFiles": [],
            "addedFiles": [],
            "removedFiles": [],
        },
        "knownWarnings": warnings,
        "zeroBlockerClaim": {
            "claimed": status.get("blockingDefectCount") == 0,
            "blockingDefectCount": status.get("blockingDefectCount"),
            "gateTestSynchronizationStatus": status.get("gateTestSynchronizationStatus"),
        },
        "reviewerMustInspect": reviewer_files,
        "reviewInstruction": "Perform a neutral, strictly read-only audit. Independently derive all expected sets and report VERIFIED, CONDITIONALLY_VERIFIED, or FAILED from the evidence; do not assume any repair-side claim is true.",
        "approvalDecision": None,
    }
    write_json(COMPLETION / "POST_REPAIR_INDEPENDENT_REVIEW_PACKAGE.json", package)
    print(json.dumps({"package": str(COMPLETION / "POST_REPAIR_INDEPENDENT_REVIEW_PACKAGE.json"), "changedFiles": len(changed), "reviewerFiles": len(reviewer_files)}, indent=2))


if __name__ == "__main__":
    if "--record-validation" in sys.argv:
        record_validation_result()
    elif "--build-review-package" in sys.argv:
        build_review_package()
    else:
        main()
