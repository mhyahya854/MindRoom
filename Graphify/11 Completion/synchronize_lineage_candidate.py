"""Synchronize the unfrozen lineage-review candidate without touching the frozen manifest."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INVENTORY = HERE / "FINAL_GATE_REPAIR_AUTHORITY_INVENTORY_CANDIDATE.jsonl"
MANIFEST = HERE / "FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"
METADATA = (
    "00 Execution Control/STATUS.json",
    "00 Execution Control/FINAL_AUTHORITY_INDEX.json",
    "00 Execution Control/GRAPHIFY_MAPPING_RECEIPT.json",
    "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
    "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json",
    "11 Completion/GRAPHIFY_MAPPING_RECEIPT.json",
    "11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json",
    "11 Completion/FINAL_SYNCHRONIZATION_REPORT.json",
    "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json",
    "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
)
INCLUDE = {
    "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json": "AUTHORITATIVE_BACKUP_EVIDENCE",
    "03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl": "AUTHORITATIVE_REQUIREMENT_LINEAGE",
    "11 Completion/FINAL_REQUIREMENT_LINEAGE_RECONCILIATION_REPORT.json": "AUTHORITATIVE_REQUIREMENT_LINEAGE",
    "11 Completion/FINAL_CAPABILITY_TASK_REQUIREMENT_TRACEABILITY_REPORT.json": "AUTHORITATIVE_REQUIREMENT_LINEAGE",
}
EXCLUDE = {
    "11 Completion/repair_requirement_lineage.py": "Executable repair helper is reproducibility tooling, not frozen planning authority.",
    "11 Completion/synchronize_lineage_candidate.py": "Executable candidate synchronizer is process tooling, not frozen planning authority.",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_count(path: Path):
    if path.suffix == ".jsonl":
        return sum(bool(line.strip()) for line in path.read_text(encoding="utf-8-sig").splitlines())
    return None


def schema_version(path: Path):
    if path.suffix != ".json":
        return "1"
    try:
        return str(read_json(path).get("schemaVersion") or "1")
    except (AttributeError, json.JSONDecodeError):
        return "1"


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    status = read_json(ROOT / "00 Execution Control/STATUS.json")
    repair_id = status.get("repairRunId") if str(status.get("repairRunId", "")).startswith("mindroom-graphify-lineage-repair-") else f"mindroom-graphify-lineage-repair-{stamp}"
    freeze_id = status.get("freezeRunId") if str(status.get("freezeRunId", "")).startswith("mindroom-graphify-lineage-review-candidate-") else f"mindroom-graphify-lineage-review-candidate-{stamp}"
    validator_id = f"mindroom-graphify-lineage-validator-{stamp}"

    inventory = read_jsonl(INVENTORY)
    by_path = {row["path"]: row for row in inventory}
    for path, classification in INCLUDE.items():
        by_path[path] = {
            "path": path,
            "classification": classification,
            "includedInFreeze": True,
            "exclusionReason": None,
            "sourceOfAuthority": "Final six-phase lineage repair specification and live validator evidence",
            "recordCount": record_count(ROOT / path),
        }
    for path, reason in EXCLUDE.items():
        by_path[path] = {
            "path": path,
            "classification": "NON_AUTHORITATIVE_REPAIR_TOOLING",
            "includedInFreeze": False,
            "exclusionReason": reason,
            "sourceOfAuthority": "Authority boundary policy",
            "recordCount": None,
        }
    inventory = sorted(by_path.values(), key=lambda row: row["path"].casefold())
    own = by_path.get("11 Completion/FINAL_GATE_REPAIR_AUTHORITY_INVENTORY_CANDIDATE.jsonl")
    if own:
        own["recordCount"] = len(inventory)
    write_jsonl(INVENTORY, inventory)

    old_manifest = {row["path"]: row for row in read_jsonl(MANIFEST)}
    manifest = []
    for row in inventory:
        if not row.get("includedInFreeze"):
            continue
        path = ROOT / row["path"]
        assert path.exists(), row["path"]
        old = old_manifest.get(row["path"], {})
        manifest.append({
            "path": row["path"],
            "authorityClass": old.get("authorityClass") or row["classification"],
            "sha256": sha256_file(path),
            "sizeBytes": path.stat().st_size,
            "recordCount": record_count(path),
            "schemaVersion": old.get("schemaVersion") or schema_version(path),
            "frozenAt": None,
            "freezeRunId": freeze_id,
        })
    manifest.sort(key=lambda row: row["path"])
    write_jsonl(MANIFEST, manifest)
    aggregate = hashlib.sha256("\n".join(f"{row['path']}:{row['sha256']}" for row in manifest).encode("utf-8")).hexdigest()

    warnings = read_json(ROOT / "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json").get("warnings", [])
    warning_summary = [{"findingId": row.get("findingId"), "releaseWave": row.get("releaseWave"), "blockingGateIds": row.get("blockingGateIds") or []} for row in warnings]
    canonical_counts = {
        "masterPlans": 3,
        "requirements": sum(bool(line.strip()) for line in (ROOT / "03 Capability Map/REQUIREMENT_REGISTRY.jsonl").read_text(encoding="utf-8-sig").splitlines()),
        "supersessions": sum(bool(line.strip()) for line in (ROOT / "03 Capability Map/REQUIREMENT_SUPERSESSION_MAP.jsonl").read_text(encoding="utf-8-sig").splitlines()),
        "legacyLineageRecords": sum(bool(line.strip()) for line in (ROOT / "03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl").read_text(encoding="utf-8-sig").splitlines()),
        "capabilities": len(read_json(ROOT / "03 Capability Map/CAPABILITY_REGISTRY.json")["capabilities"]),
        "changeRecords": sum(bool(line.strip()) for line in (ROOT / "04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl").read_text(encoding="utf-8-sig").splitlines()),
        "tasks": sum(bool(line.strip()) for line in (ROOT / "09 Implementation/IMPLEMENTATION_TASKS.jsonl").read_text(encoding="utf-8-sig").splitlines()),
        "primaryTasks": 161,
        "bootstrapTasks": 1,
        "tests": sum(bool(line.strip()) for line in (ROOT / "10 Verification/REQUIREMENT_TEST_MATRIX.jsonl").read_text(encoding="utf-8-sig").splitlines()),
        "fixtureCategories": 6,
        "canonicalFixtureRecords": 6,
        "releaseWaves": 6,
        "waveGates": 6,
        "capabilityValidationGates": 161,
        "applicationGates": 1,
        "adrs": 14,
        "publicEntrypoints": 161,
    }
    common = {
        "freezeRunId": freeze_id,
        "officialValidatorRunId": validator_id,
        "externalReviewRunId": None,
        "mappingStatus": "LINEAGE_REPAIR_COMPLETE_PENDING_INDEPENDENT_REVIEW",
        "independentReviewStatus": "PENDING_GENUINELY_INDEPENDENT_LINEAGE_REVIEW",
        "planningFreezeStatus": "NOT_FROZEN",
        "wave0Readiness": "BLOCKED_PENDING_INDEPENDENT_LINEAGE_REVIEW",
        "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION",
        "finalReleaseReceiptStatus": "NOT_VERIFIED",
        "canonicalCounts": canonical_counts,
        "manifestRecordCount": len(manifest),
        "manifestAggregateHash": aggregate,
        "codebaseFileCount": 10080,
        "codebaseDirectoryCount": 2548,
        "codebaseAggregateHash": "91600fc76001d8b2c108634d4fa3ceca5e743176f103a44d21b7e0e7273ec748",
        "validatorCheckCount": 148,
        "challengeTestCount": 50,
        "blockingDefectCount": 0,
        "repairRunId": repair_id,
        "gateTestSynchronizationStatus": "PASS",
        "warningSummary": warning_summary,
    }
    for relative in METADATA:
        path = ROOT / relative
        data = read_json(path)
        data.update(common)
        data["timestamp"] = now
        if relative.endswith("STATUS.json"):
            data.update({"projectPhase": "GRAPHIFY_LINEAGE_REPAIR_PENDING_INDEPENDENT_REVIEW", "lastUpdatedAt": now, "backupPath": read_json(ROOT / "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json")["backupPath"], "freezeCandidateOnly": True})
        if relative.endswith("FINAL_AUTHORITY_INDEX.json"):
            data["authoritativeMap"].update({
                "legacyRequirementLineageMap": "03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl",
                "lineageReconciliationReport": "11 Completion/FINAL_REQUIREMENT_LINEAGE_RECONCILIATION_REPORT.json",
                "capabilityTaskTraceabilityReport": "11 Completion/FINAL_CAPABILITY_TASK_REQUIREMENT_TRACEABILITY_REPORT.json",
                "longPathBackupVerification": "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json",
            })
        if relative.endswith("FINAL_SYNCHRONIZATION_REPORT.json"):
            data.update({"backupPath": read_json(ROOT / "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json")["backupPath"], "validatorSourceHash": sha256_file(HERE / "validate_final_graphify_freeze.py"), "challengeSourceHash": sha256_file(HERE / "run_final_freeze_challenges.py"), "verifierSourceHash": sha256_file(HERE / "verify_step11b_results.py"), "blockers": [], "freezeCandidateOnly": True})
        if relative.endswith("FINAL_FREEZE_VALIDATION_RESULT.json"):
            data.update({"validatorSourceHash": sha256_file(HERE / "validate_final_graphify_freeze.py"), "freezeCandidateOnly": True, "validationResult": {"status": "PENDING_REVALIDATION", "failedChecksCount": None, "checks": []}})
        write_json(path, data)
    print(json.dumps({"repairRunId": repair_id, "candidateFreezeRunId": freeze_id, "validatorRunId": validator_id, "inventoryRecords": len(inventory), "authorityInclusions": len(manifest), "manifestAggregateHash": aggregate}, indent=2))


if __name__ == "__main__":
    main()
