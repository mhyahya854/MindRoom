"""Independent verifier for IMPLEMENTATION_EXECUTION_CERTIFICATION results."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
VALIDATOR = ROOT / "11 Completion" / "validate_execution_state.py"

REQUIRED_CHECKS = [f"EXEC-{number:02d}" for number in range(1, 21)]


def load_validator():
    spec = importlib.util.spec_from_file_location("mindroom_execution_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main():
    validator = load_validator()
    result = validator.do_execution_validation()
    present = [check.get("checkId") for check in result.get("checks", [])]
    if set(present) != set(REQUIRED_CHECKS):
        missing = sorted(set(REQUIRED_CHECKS) - set(present))
        unexpected = sorted(set(present) - set(REQUIRED_CHECKS))
        fail(f"Execution check IDs do not equal production check IDs. Missing: {missing}; Unexpected: {unexpected}")
    duplicates = [check_id for check_id, count in Counter(present).items() if count > 1]
    if duplicates:
        fail(f"Duplicate execution check IDs: {duplicates}")
    if result.get("mode") != "IMPLEMENTATION_EXECUTION_CERTIFICATION":
        fail("Execution result mode is not IMPLEMENTATION_EXECUTION_CERTIFICATION.")
    if result.get("status") != "PASS" or result.get("failedChecksCount") != 0:
        failed = [check.get("checkId") for check in result.get("checks", []) if check.get("status") == "FAIL"]
        fail(f"Execution certification failed: {failed}")
    if (result.get("derived") or {}).get("validatorWrites") != 0:
        fail("Execution validator reported Codebase writes.")
    summary = {
        "status": "PASS",
        "expectedValidatorCheckIds": len(REQUIRED_CHECKS),
        "presentValidatorCheckIds": len(present),
        "completedReceiptCount": (result.get("derived") or {}).get("completedReceiptCount"),
        "liveCodebaseAggregateSha256": (result.get("derived") or {}).get("liveCodebaseAggregateSha256"),
        "currentTrustedCodebaseTree": (result.get("derived") or {}).get("currentTrustedCodebaseTree"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    raise SystemExit(0)


if __name__ == "__main__":
    main()
