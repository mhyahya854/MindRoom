"""Create the neutral, self-contained lineage-repair review package."""

from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTPUT = HERE / "FINAL_LINEAGE_REPAIR_INDEPENDENT_REVIEW_PACKAGE.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(relative: str):
    path = ROOT / relative
    return {
        "path": relative,
        "sha256": sha256_file(path),
        "sizeBytes": path.stat().st_size,
        "recordCount": sum(bool(line.strip()) for line in path.read_text(encoding="utf-8-sig").splitlines()) if path.suffix == ".jsonl" else None,
    }


def current_files():
    display = os.path.abspath(ROOT)
    scan_root = "\\\\?\\" + display if os.name == "nt" and not display.startswith("\\\\?\\") else display
    pairs = []
    for current, dirnames, filenames in os.walk(scan_root, topdown=True, followlinks=False):
        dirnames[:] = [name for name in dirnames if not os.path.islink(os.path.join(current, name))]
        for name in filenames:
            path = os.path.join(current, name)
            if not os.path.islink(path):
                pairs.append((os.path.relpath(path, scan_root).replace("\\", "/"), path))

    def digest(item):
        relative, path = item
        value = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                value.update(chunk)
        return relative, value.hexdigest(), os.path.getsize(path)

    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as executor:
        return {relative: {"sha256": digest_value, "sizeBytes": size} for relative, digest_value, size in executor.map(digest, pairs)}


def main():
    status = read_json(ROOT / "00 Execution Control/STATUS.json")
    backup = read_json(ROOT / "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json")
    baseline_document = read_json(Path(backup["sourceBaselineManifestPath"]))
    baseline = {row["relativePath"]: row for row in baseline_document["graphify"]["files"]}
    current = current_files()
    changed = []
    for relative in sorted(set(baseline) | set(current)):
        if relative == "11 Completion/FINAL_LINEAGE_REPAIR_INDEPENDENT_REVIEW_PACKAGE.json":
            continue
        before, after = baseline.get(relative), current.get(relative)
        if (before or {}).get("sha256") != (after or {}).get("sha256"):
            changed.append({
                "path": relative,
                "changeType": "ADDED" if before is None else "REMOVED" if after is None else "MODIFIED",
                "beforeSha256": (before or {}).get("sha256"),
                "afterSha256": (after or {}).get("sha256"),
                "beforeSizeBytes": (before or {}).get("sizeBytes"),
                "afterSizeBytes": (after or {}).get("sizeBytes"),
            })

    paths = {
        "backupVerification": "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json",
        "lineageMap": "03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl",
        "supersessionMap": "03 Capability Map/REQUIREMENT_SUPERSESSION_MAP.jsonl",
        "lineageReconciliationReport": "11 Completion/FINAL_REQUIREMENT_LINEAGE_RECONCILIATION_REPORT.json",
        "traceabilityReport": "11 Completion/FINAL_CAPABILITY_TASK_REQUIREMENT_TRACEABILITY_REPORT.json",
        "validator": "11 Completion/validate_final_graphify_freeze.py",
        "challengeHarness": "11 Completion/run_final_freeze_challenges.py",
        "validatorResult": "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
        "challengeResult": "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
        "candidateAuthorityInventory": "11 Completion/FINAL_GATE_REPAIR_AUTHORITY_INVENTORY_CANDIDATE.jsonl",
        "candidateManifest": "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl",
        "codebasePreservationReceipt": "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json",
        "warningOwnership": "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json",
    }
    validator_result = read_json(ROOT / paths["validatorResult"])
    challenge_result = read_json(ROOT / paths["challengeResult"])
    reconciliation = read_json(ROOT / paths["lineageReconciliationReport"])
    traceability = read_json(ROOT / paths["traceabilityReport"])
    package = {
        "schemaVersion": 1,
        "reviewPackageId": "mindroom-lineage-independent-review-package-" + datetime.now().astimezone().strftime("%Y%m%d-%H%M%S"),
        "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "repairSessionId": status["repairRunId"],
        "candidateFreezeRunId": status["freezeRunId"],
        "reviewDecision": None,
        "neutralReviewInstruction": "Independently verify every claim from the cited live artifacts. Do not assume approval; report VERIFIED, CONDITIONALLY_VERIFIED, or FAILED from evidence only. Remain strictly read-only.",
        "changedFiles": changed,
        "packageSelfExclusion": "The package omits its own hash and change-ledger row to avoid recursive self-reference.",
        "artifacts": {name: artifact(relative) for name, relative in paths.items()},
        "backupVerification": read_json(ROOT / paths["backupVerification"]),
        "lineageMap": read_jsonl(ROOT / paths["lineageMap"]),
        "lineageReconciliationReport": reconciliation,
        "capabilityTaskTraceabilityReport": traceability,
        "strictValidatorSourceHash": sha256_file(ROOT / paths["validator"]),
        "challengeSourceHash": sha256_file(ROOT / paths["challengeHarness"]),
        "validatorResult": validator_result,
        "challengeResult": challenge_result,
        "candidateAuthorityInventory": read_jsonl(ROOT / paths["candidateAuthorityInventory"]),
        "candidateManifest": read_jsonl(ROOT / paths["candidateManifest"]),
        "codebasePreservationReceipt": read_json(ROOT / paths["codebasePreservationReceipt"]),
        "knownWarnings": read_json(ROOT / paths["warningOwnership"]).get("warnings", []),
        "candidateZeroBlockerClaim": {
            "claim": "ZERO_LINEAGE_BACKUP_VALIDATOR_CHALLENGE_MANIFEST_OR_CODEBASE_BLOCKERS_PENDING_REVIEWER_VERIFICATION",
            "unresolvedLineageIds": reconciliation["lineageCounts"]["unresolved"],
            "capabilityUnresolvedReferences": traceability["after"]["capabilityUnresolvedReferences"],
            "taskUnresolvedReferences": traceability["after"]["taskUnresolvedReferences"],
            "validatorFailures": validator_result["validationResult"]["failedChecksCount"],
            "challengeFailures": sum(not row["passed"] for row in challenge_result["challenges"]),
            "backupOmissions": len(backup["missingPaths"]),
            "codebaseMutations": len(read_json(ROOT / paths["codebasePreservationReceipt"])["codebasePreservation"].get("modifiedPaths", [])),
        },
    }
    assert package["reviewDecision"] is None
    assert package["candidateZeroBlockerClaim"] == {
        "claim": "ZERO_LINEAGE_BACKUP_VALIDATOR_CHALLENGE_MANIFEST_OR_CODEBASE_BLOCKERS_PENDING_REVIEWER_VERIFICATION",
        "unresolvedLineageIds": 0,
        "capabilityUnresolvedReferences": 0,
        "taskUnresolvedReferences": 0,
        "validatorFailures": 0,
        "challengeFailures": 0,
        "backupOmissions": 0,
        "codebaseMutations": 0,
    }
    OUTPUT.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), "reviewPackageId": package["reviewPackageId"], "changedFiles": len(changed), "sizeBytes": OUTPUT.stat().st_size, "reviewDecision": package["reviewDecision"]}, indent=2))


if __name__ == "__main__":
    main()
