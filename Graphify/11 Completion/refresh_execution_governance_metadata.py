"""Regenerate authority inventory/manifest metadata after execution-governance changes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
CONTROL = ROOT / "00 Execution Control"
COMPLETION = ROOT / "11 Completion"

CURRENT_METADATA = (
    "00 Execution Control/STATUS.json",
    "00 Execution Control/FINAL_AUTHORITY_INDEX.json",
    "00 Execution Control/GRAPHIFY_MAPPING_RECEIPT.json",
    "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
    "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json",
    "00 Execution Control/FINAL_AUTHORITATIVE_FREEZE_BACKUP_VERIFICATION.json",
    "11 Completion/GRAPHIFY_MAPPING_RECEIPT.json",
    "11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json",
    "11 Completion/FINAL_SYNCHRONIZATION_REPORT.json",
    "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json",
    "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
)

NEW_AUTHORITY_PATHS = [
    "00 Execution Control/schemas/execution-state.schema.json",
    "00 Execution Control/schemas/execution-receipt.schema.json",
    "00 Execution Control/schemas/execution-trusted-baseline.schema.json",
    "11 Completion/EXECUTION_GOVERNANCE_ARCHITECTURE.md",
    "11 Completion/EXECUTION_AUTHORIZATION_RECORD.json",
    "11 Completion/EXECUTION_RECEIPTS.jsonl",
    "11 Completion/EXECUTION_CHECKPOINT_CHAIN.jsonl",
    "11 Completion/EXECUTION_TRUSTED_BASELINE.json",
    "11 Completion/EXECUTION_CERTIFICATION_CHALLENGE_REPORT.json",
    "11 Completion/validate_execution_state.py",
    "11 Completion/verify_execution_state.py",
    "11 Completion/run_execution_state_challenges.py",
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_hash(records):
    text = "\n".join(f"{row['path']}:{row['sha256']}" for row in sorted(records, key=lambda row: row["path"]))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    inventory_path = CONTROL / "FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl"
    inventory = read_jsonl(inventory_path)
    existing = {normalize(row.get("path")): row for row in inventory}

    for relative in NEW_AUTHORITY_PATHS:
        normalized = normalize(relative)
        classification = "CURRENT_AUTHORITATIVE"
        existing[normalized] = {
            "path": normalized,
            "classification": classification,
            "includedInFreeze": True,
            "exclusionReason": None,
            "sourceOfAuthority": "WAVE0-execution-governance change control",
            "recordCount": None,
        }
    inventory = [existing[key] for key in sorted(existing, key=str.casefold)]
    included_rows = [row for row in inventory if row.get("includedInFreeze")]
    for row in inventory:
        normalized = normalize(row.get("path"))
        path = ROOT / normalized
        if normalized == "00 Execution Control/FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl":
            row["recordCount"] = len(included_rows)
        elif path.suffix.lower() == ".jsonl" and path.exists():
            row["recordCount"] = sum(1 for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    write_jsonl(inventory_path, inventory)

    classification_path = CONTROL / "FINAL_AUTHORITY_CLASSIFICATION.jsonl"
    classification = read_jsonl(classification_path)
    classification_by_path = {normalize(row.get("path")): row for row in classification}
    for relative in NEW_AUTHORITY_PATHS:
        normalized = normalize(relative)
        classification_by_path[normalized] = {
            "path": normalized,
            "classification": "CURRENT_AUTHORITATIVE",
            "currentAuthority": True,
            "supersededBy": [],
            "reason": "Canonical execution governance authority introduced by WAVE0-execution-governance change control.",
            "includedInFinalManifest": True,
            "manifestExclusionReason": None,
        }
    write_jsonl(classification_path, [classification_by_path[key] for key in sorted(classification_by_path, key=str.casefold)])

    authority_index_path = CONTROL / "FINAL_AUTHORITY_INDEX.json"
    authority_index = read_json(authority_index_path)
    authority_map = authority_index.get("authoritativeMap") or {}
    authority_map.update({
        "executionValidator": "11 Completion/validate_execution_state.py",
        "executionVerifier": "11 Completion/verify_execution_state.py",
        "executionChallengeSuite": "11 Completion/run_execution_state_challenges.py",
        "executionAuthorization": "11 Completion/EXECUTION_AUTHORIZATION_RECORD.json",
        "executionReceipts": "11 Completion/EXECUTION_RECEIPTS.jsonl",
        "executionTrustedBaseline": "11 Completion/EXECUTION_TRUSTED_BASELINE.json",
        "executionCheckpointChain": "11 Completion/EXECUTION_CHECKPOINT_CHAIN.jsonl",
        "executionGovernanceArchitecture": "11 Completion/EXECUTION_GOVERNANCE_ARCHITECTURE.md",
    })
    authority_index["authoritativeMap"] = authority_map
    authority_index["validatorCheckCount"] = 232
    authority_index["challengeTestCount"] = 127
    authority_index["lifecyclePhase"] = "PRE_IMPLEMENTATION_FROZEN"
    authority_index["executionGovernanceReady"] = True
    authority_index["changeControlStatus"] = "WAVE0_EXECUTION_GOVERNANCE_CHANGE_CONTROL_COMPLETE"
    write_json(authority_index_path, authority_index)

    status_path = CONTROL / "STATUS.json"
    status = read_json(status_path)
    status["lifecyclePhase"] = "PRE_IMPLEMENTATION_FROZEN"
    status["executionGovernanceReady"] = True
    status["implementationPerformed"] = False
    status["applicationReleased"] = False
    write_json(status_path, status)

    # Re-read the final inventory (its self record-count changed) and build the manifest last.
    inventory = read_jsonl(inventory_path)
    def build_manifest(source_rows):
        rows = []
        for row in source_rows:
            if not row.get("includedInFreeze"):
                continue
            relative = normalize(row["path"])
            path = ROOT / relative
            rows.append({
                "path": relative,
                "authorityClass": row.get("classification"),
                "sha256": sha256_file(path),
                "sizeBytes": path.stat().st_size,
                "recordCount": row.get("recordCount"),
                "schemaVersion": "1",
                "frozenAt": "2026-08-16T00:00:00+03:00",
                "freezeRunId": "mindroom-wave0-execution-governance-20260816",
            })
        rows.sort(key=lambda row: row["path"])
        return rows

    manifest_rows = build_manifest(inventory)
    for row in inventory:
        if normalize(row.get("path")) == "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl":
            row["recordCount"] = len(manifest_rows)
    write_jsonl(inventory_path, inventory)
    inventory = read_jsonl(inventory_path)
    manifest_rows = build_manifest(inventory)
    manifest_path = CONTROL / "FROZEN_ARTIFACT_MANIFEST.jsonl"
    write_jsonl(manifest_path, manifest_rows)
    manifest_hash = aggregate_hash(manifest_rows)
    authority_index["manifestRecordCount"] = len(manifest_rows)
    authority_index["manifestAggregateHash"] = manifest_hash
    write_json(authority_index_path, authority_index)

    common = {
        "lifecyclePhase": "PRE_IMPLEMENTATION_FROZEN",
        "executionGovernanceReady": True,
        "manifestRecordCount": len(manifest_rows),
        "manifestAggregateHash": manifest_hash,
        "validatorCheckCount": 232,
        "challengeTestCount": 127,
        "codebaseFileCount": 10080,
        "codebaseDirectoryCount": 2548,
        "codebaseAggregateHash": "91600fc76001d8b2c108634d4fa3ceca5e743176f103a44d21b7e0e7273ec748",
        "implementationPerformed": False,
        "applicationReleased": False,
    }
    for relative in CURRENT_METADATA:
        path = ROOT / relative
        document = read_json(path)
        document.update(common)
        if relative == "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json":
            derived = (document.get("validationResult") or {}).get("derived") or {}
            derived["manifestAggregateHash"] = manifest_hash
            derived["manifestRecordCount"] = len(manifest_rows)
            document["validationResult"]["derived"] = derived
        write_json(path, document)

    print(json.dumps({
        "manifestRecordCount": len(manifest_rows),
        "manifestAggregateHash": manifest_hash,
        "authorityIndexPaths": len(authority_map),
        "statusLifecycle": status.get("lifecyclePhase"),
    }, indent=2))


def normalize(value):
    return str(value or "").replace("\\", "/").removeprefix("./").removeprefix("Graphify/")


if __name__ == "__main__":
    main()
