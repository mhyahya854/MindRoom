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
BACKUP_RECEIPT = ROOT / "00 Execution Control" / "FINAL_LONG_PATH_BACKUP_VERIFICATION.json"
MANIFEST = ROOT / "11 Completion" / "FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"


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
    if not verify_only:
        process = subprocess.run(
            [sys.executable, str(VALIDATOR), "--mode", "FULL_TECHNICAL_CERTIFICATION", "--verify-only"],
            capture_output=True,
            text=True,
        )
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr, file=sys.stderr)
        if process.returncode:
            fail("Production FULL_TECHNICAL_CERTIFICATION validation failed.")

    validator = load_module("mindroom_strict_validator", VALIDATOR)
    runner = load_module("mindroom_graphify_challenge_runner", CHALLENGE_RUNNER)
    required_checks = validator.get_check_definitions("FULL_TECHNICAL_CERTIFICATION")
    required_challenges = [row["challengeId"] for row in runner.get_challenge_definitions()]

    for path in (CHALLENGES, VALIDATION_RESULT, STATUS, BACKUP_RECEIPT, MANIFEST):
        if not path.exists():
            fail(f"Required result is missing: {path}")

    challenge_report = json.loads(CHALLENGES.read_text(encoding="utf-8-sig"))
    validation_report = json.loads(VALIDATION_RESULT.read_text(encoding="utf-8-sig"))
    status = json.loads(STATUS.read_text(encoding="utf-8-sig"))
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

    if validation_report.get("validationTarget") != "LIVE_REPOSITORY":
        fail("Persisted live validation target is not LIVE_REPOSITORY.")
    if Path(str(validation_report.get("candidateRoot") or "")).resolve() != ROOT.resolve():
        fail("Persisted live validation candidate root is not the Graphify root.")
    if validation_report.get("overridesUsed") is not False or validation_report.get("temporaryChallengeId") is not None:
        fail("Persisted live validation used overrides or a temporary challenge ID.")
    if (result.get("derived") or {}).get("validationMode") != "FULL_TECHNICAL_CERTIFICATION" or validation_report.get("validationMode") != "FULL_TECHNICAL_CERTIFICATION":
        fail("Persisted live validation mode is not FULL_TECHNICAL_CERTIFICATION.")

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
    if receipt.get("verified") is not True or not Path(str(receipt.get("backupRoot") or "")).exists():
        fail("Backup receipt is not verified or the backup root is missing.")
    for field in ("missingPaths", "extraPaths", "hashMismatches", "sizeMismatches", "directoryDifferences", "longPathOmissions", "unreadablePaths"):
        if receipt.get(field):
            fail(f"Backup receipt contains nonempty {field}.")

    failed_manifest = [check.get("checkId") for check in result.get("checks", []) if check.get("status") == "FAIL" and str(check.get("checkId") or "").startswith("MAN-")]
    if failed_manifest:
        fail(f"Candidate-manifest checks failed in the live validation report: {failed_manifest}")
    manifest_rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    manifest_self = [row.get("path") for row in manifest_rows if row.get("path") == "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"]
    if manifest_self:
        fail("Candidate manifest contains itself.")
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
    if status.get("codebaseExecutionStatus") not in {None, "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION", "BLOCKED_PENDING_INDEPENDENT_REVIEW_DEFECT_REPAIR", "BLOCKED_PENDING_INDEPENDENT_LINEAGE_REVIEW"}:
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
