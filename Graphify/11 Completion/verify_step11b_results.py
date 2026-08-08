"""Independent Step 11b verifier; never repairs or rewrites authority data.

All expected check IDs, challenge IDs, and counts are derived dynamically from the
production validator and challenge runner. No hard-coded historical counts remain.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
VALIDATOR = ROOT / "11 Completion" / "validate_final_graphify_freeze.py"
CHALLENGE_RUNNER = ROOT / "11 Completion" / "run_final_freeze_challenges.py"
CHALLENGES = ROOT / "11 Completion" / "FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json"
VALIDATION_RESULT = ROOT / "00 Execution Control" / "FINAL_FREEZE_VALIDATION_RESULT.json"
STATUS = ROOT / "00 Execution Control" / "STATUS.json"
BACKUP_RECEIPT = ROOT / "00 Execution Control" / "FINAL_AUTHORITATIVE_FREEZE_BACKUP_VERIFICATION.json"
CANDIDATE_MANIFEST = ROOT / "11 Completion" / "FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"
FROZEN_MANIFEST = ROOT / "00 Execution Control" / "FROZEN_ARTIFACT_MANIFEST.jsonl"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_hash(records):
    text = "\n".join(f"{row.get('path')}:{row.get('sha256')}" for row in sorted(records, key=lambda row: row.get("path")))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main():
    verify_only = "--verify-only" in sys.argv[1:]
    status = json.loads(STATUS.read_text(encoding="utf-8-sig"))
    certification_mode = "FINAL_FREEZE_CERTIFICATION" if status.get("planningFreezeStatus") == "FROZEN" else "FULL_TECHNICAL_CERTIFICATION"
    if not verify_only:
        process = subprocess.run(
            [sys.executable, str(VALIDATOR), "--mode", certification_mode, "--verify-only"],
            capture_output=True,
            text=True,
        )
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr, file=sys.stderr)
        if process.returncode:
            fail(f"Production {certification_mode} validation failed.")

    validator = load_module("mindroom_strict_validator", VALIDATOR)
    runner = load_module("mindroom_graphify_challenge_runner", CHALLENGE_RUNNER)
    required_checks = validator.get_check_definitions(certification_mode)
    required_challenges = [row["challengeId"] for row in runner.get_challenge_definitions()]
    manifest_path = FROZEN_MANIFEST if status.get("planningFreezeStatus") == "FROZEN" else CANDIDATE_MANIFEST
    manifest_relative = "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl" if manifest_path == FROZEN_MANIFEST else "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"

    for path in (CHALLENGES, VALIDATION_RESULT, STATUS, BACKUP_RECEIPT, manifest_path):
        if not path.exists():
            fail(f"Required result is missing: {path}")

    challenge_report = json.loads(CHALLENGES.read_text(encoding="utf-8-sig"))
    validation_report = json.loads(VALIDATION_RESULT.read_text(encoding="utf-8-sig"))
    receipt = json.loads(BACKUP_RECEIPT.read_text(encoding="utf-8-sig"))

    result = validation_report.get("validationResult") or {}
    present_checks = [check.get("checkId") for check in result.get("checks", [])]
    if present_checks != required_checks:
        missing = sorted(set(required_checks) - set(present_checks))
        unexpected = sorted(set(present_checks) - set(required_checks))
        fail(f"Validator report check IDs do not equal production check IDs. Missing: {missing}; Unexpected: {unexpected}")
    duplicates = [check_id for check_id, count in Counter(present_checks).items() if count > 1]
    if duplicates:
        fail(f"Duplicate validator check IDs in the live report: {duplicates}")
    if result.get("status") != "PASS" or result.get("failedChecksCount") != 0:
        fail(f"Persisted final validation result is not a zero-failure PASS: {result.get('status')} / {result.get('failedChecksCount')}")

    executed = [row.get("challengeId") for row in challenge_report.get("challenges", [])]
    if executed != required_challenges:
        missing = sorted(set(required_challenges) - set(executed))
        unexpected = sorted(set(executed) - set(required_challenges))
        fail(f"Challenge report IDs do not equal production challenge IDs. Missing: {missing}; Unexpected: {unexpected}")
    challenge_duplicates = [challenge_id for challenge_id, count in Counter(executed).items() if count > 1]
    if challenge_duplicates:
        fail(f"Duplicate challenge IDs in the challenge report: {challenge_duplicates}")
    if challenge_report.get("verdict") != "PASS":
        fail("Challenge report verdict is not PASS.")
    if challenge_report.get("fullCertificationStatus") != "PASS" or (challenge_report.get("fullCertificationFailedCheckIds") or []):
        fail("Challenge report full-certification status is not a zero-failure PASS.")
    if status.get("planningFreezeStatus") == "FROZEN" and (challenge_report.get("finalFreezeCertificationStatus") != "PASS" or (challenge_report.get("finalFreezeCertificationFailedCheckIds") or [])):
        fail("Challenge report final-freeze certification status is not a zero-failure PASS.")
    for row in challenge_report.get("challenges", []):
        if not row.get("passed"):
            fail(f"Challenge {row.get('challengeId')} did not pass.")
        if row.get("baselineStatus") != "PASS" or (row.get("baselineFailedCheckIds") or []) or (row.get("documentedEnvironmentFailures") or []) or (row.get("environmentExemptions") or []):
            fail(f"Challenge {row.get('challengeId')} contains a failed baseline or an exemption.")
        if row.get("productionValidatorInvoked") is not True:
            fail(f"Challenge {row.get('challengeId')} did not invoke the production validator.")
        if row.get("validationTarget") != "TEMPORARY_CHALLENGE_CANDIDATE" or row.get("overridesUsed") is not True or not row.get("temporaryChallengeId"):
            fail(f"Challenge {row.get('challengeId')} is not a properly identified temporary candidate.")
    if challenge_report.get("baselineFailuresSubtracted") is not False or challenge_report.get("challengesUsingBaselineFailureSubtraction") != 0:
        fail("Baseline-failure subtraction was used in the challenge suite.")
    if challenge_report.get("documentedEnvironmentFailures") or challenge_report.get("environmentExemptions"):
        fail("Environment exemptions remain recorded in the challenge report.")
    if challenge_report.get("backupUnchangedThroughoutChallenges") is not True or challenge_report.get("backupAggregateBeforeChallenges") != challenge_report.get("backupAggregateAfterChallenges"):
        fail("Challenge execution did not independently prove that the active backup remained unchanged.")

    if validation_report.get("validationTarget") != "LIVE_REPOSITORY":
        fail("Persisted live validation target is not LIVE_REPOSITORY.")
    if validation_report.get("candidateRootKind") != "REPOSITORY_RELATIVE" or validation_report.get("repositoryRelativeGraphifyRoot") != "Graphify":
        fail("Persisted live validation candidate-root metadata is not repository-relative.")
    if validation_report.get("overridesUsed") is not False or validation_report.get("temporaryChallengeId") is not None:
        fail("Persisted live validation used overrides or a temporary challenge ID.")
    if (result.get("derived") or {}).get("validationMode") != certification_mode or validation_report.get("validationMode") != certification_mode:
        fail(f"Persisted live validation mode is not {certification_mode}.")

    validator_hash = sha256_file(VALIDATOR)
    challenge_hash = sha256_file(CHALLENGE_RUNNER)
    verifier_hash = sha256_file(HERE)
    if validation_report.get("validatorSourceHash") != validator_hash or challenge_report.get("validatorSourceHash") != validator_hash:
        fail("Validator source hash does not match every regenerated result.")
    if validation_report.get("challengeSourceHash") != challenge_hash or challenge_report.get("challengeSourceHash") != challenge_hash:
        fail("Challenge source hash does not match every regenerated result.")
    if validation_report.get("verifierSourceHash") and validation_report.get("verifierSourceHash") != verifier_hash:
        fail("Verifier source hash does not match the recorded live-report value.")
    if challenge_report.get("verifierSourceHash") and challenge_report.get("verifierSourceHash") != verifier_hash:
        fail("Verifier source hash does not match the recorded challenge-report value.")
    if validation_report.get("validatorCheckCount") != len(required_checks) or challenge_report.get("validatorCheckCount") != len(required_checks):
        fail("Recorded validator check count does not equal the current production check count.")
    if validation_report.get("challengeTestCount") != len(required_challenges) or challenge_report.get("challengeTestCount") != len(required_challenges):
        fail("Recorded challenge count does not equal the current production challenge count.")

    failed_backup = [check.get("checkId") for check in result.get("checks", []) if check.get("status") == "FAIL" and str(check.get("checkId") or "").startswith("BAK-")]
    if failed_backup:
        fail(f"Backup checks failed in the live validation report: {failed_backup}")
    history = receipt.get("backupHistory") or {}
    original = history.get("historicalOriginalBackup", {})
    replacement = history.get("replacementPreReviewBackup", {})
    mutable_mirror = history.get("mutableWorkingMirror", {})
    invalidated = history.get("invalidatedCandidateBackup", {})
    active = history.get("activePreReviewBackup", {})
    common_history_is_canonical = (
        original.get("present") is False
        and original.get("active") is False
        and original.get("role") == "HISTORICAL_MISSING_NONACTIVE"
        and replacement.get("present") is False
        and replacement.get("verified") is False
        and replacement.get("active") is False
        and replacement.get("role") == "HISTORICAL_REPLACEMENT_PRE_REVIEW_BACKUP_MISSING_NONACTIVE"
        and mutable_mirror.get("active") is False
        and mutable_mirror.get("immutable") is False
        and mutable_mirror.get("role") == "MUTABLE_WORKING_MIRROR_NOT_VALID_AS_IMMUTABLE_ROLLBACK_POINT"
        and invalidated.get("present") is True
        and invalidated.get("verified") is True
        and invalidated.get("active") is False
        and invalidated.get("immutable") is True
        and invalidated.get("role") == "INVALIDATED_CANDIDATE_BACKUP"
    )
    if not common_history_is_canonical:
        fail("Backup receipt does not distinguish the canonical historical, missing, mutable, and invalidated backup roles.")
    if receipt.get("backupEvidence") is not None:
        fail("Backup receipt contains a duplicate sibling backup authority summary.")

    pending_state = receipt.get("backupState") == receipt.get("receiptState") == "PENDING_FINAL_CONVERGED_PRE_REVIEW_BACKUP"
    active_state = receipt.get("backupState") == receipt.get("receiptState") == "VERIFIED_ACTIVE_PRE_REVIEW_BACKUP"
    if pending_state:
        if not (
            set(history) == {"historicalOriginalBackup", "replacementPreReviewBackup", "mutableWorkingMirror", "invalidatedCandidateBackup"}
            and receipt.get("verified") is False
            and receipt.get("immutable") is False
            and receipt.get("activeBackupRole") == "PENDING_FINAL_CONVERGED_PRE_REVIEW_BACKUP"
            and receipt.get("backupRoot") is None
            and receipt.get("backupPath") is None
            and receipt.get("preFinalizationBackupPath") is None
            and receipt.get("copyEvidencePath") is None
            and receipt.get("backupManifestPath") is None
        ):
            fail("Pending backup receipt is not the exact fail-closed pre-Phase-9 state.")
    elif active_state:
        backup_root = Path(str(receipt.get("backupRoot") or ""))
        if not (
            set(history) == {"historicalOriginalBackup", "replacementPreReviewBackup", "mutableWorkingMirror", "invalidatedCandidateBackup", "activePreReviewBackup"}
            and receipt.get("verified") is True
            and receipt.get("immutable") is True
            and receipt.get("activeBackupRole") == "IMMUTABLE_BOUND_PRE_REVIEW_BACKUP"
            and backup_root.exists()
            and active.get("path") == receipt.get("backupRoot")
            and active.get("present") is True
            and active.get("verified") is True
            and active.get("active") is True
            and active.get("immutable") is True
            and active.get("role") == "IMMUTABLE_BOUND_PRE_REVIEW_BACKUP"
        ):
            fail("Verified active backup receipt is not the exact canonical post-Phase-9 state.")
    else:
        fail("Backup receipt is neither the canonical pending state nor the canonical verified active state.")
    for field in ("missingPaths", "extraPaths", "hashMismatches", "sizeMismatches", "directoryDifferences", "longPathOmissions", "unreadablePaths"):
        if receipt.get(field):
            fail(f"Backup receipt contains nonempty {field}.")

    failed_manifest = [check.get("checkId") for check in result.get("checks", []) if check.get("status") == "FAIL" and str(check.get("checkId") or "").startswith("MAN-")]
    if failed_manifest:
        fail(f"Candidate-manifest checks failed in the live validation report: {failed_manifest}")
    manifest_rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    manifest_self = [row.get("path") for row in manifest_rows if row.get("path") == manifest_relative]
    if manifest_self:
        fail("Active manifest contains itself.")
    manifest_mismatches = []
    for row in manifest_rows:
        path = ROOT / str(row.get("path"))
        if not path.exists() or sha256_file(path) != row.get("sha256"):
            manifest_mismatches.append(row.get("path"))
    if manifest_mismatches:
        fail(f"Candidate manifest hashes do not match live files: {manifest_mismatches}")
    calculated_manifest_hash = aggregate_hash(manifest_rows)
    if (result.get("derived") or {}).get("manifestAggregateHash") != calculated_manifest_hash:
        fail("Live-report candidate manifest aggregate hash does not match an independent recalculation.")

    if status.get("wave0Readiness") in {"WAVE_0_STARTED", "WAVE_0_COMPLETED"}:
        fail("Wave 0 has started; implementation must not proceed.")
    if status.get("codebaseExecutionStatus") not in {None, "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION"}:
        fail("Codebase execution is not blocked.")
    if status.get("finalReleaseReceiptStatus") == "VERIFIED":
        fail("Application release is falsely verified.")

    summary = {
        "status": "PASS",
        "expectedValidatorCheckIds": len(required_checks),
        "presentValidatorCheckIds": len(present_checks),
        "expectedChallengeIds": len(required_challenges),
        "presentChallengeIds": len(executed),
        "liveReportValidationPassed": True,
        "backupValidationPassed": True,
        "candidateManifestValidationPassed": True,
        "technicalGovernanceStateValidationPassed": True,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
