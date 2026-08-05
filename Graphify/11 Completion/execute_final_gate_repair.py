"""Synchronize MindRoom test ownership and release gates without touching Codebase."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
COMPLETION = ROOT / "11 Completion"
EXPECTED_WAVES = tuple(f"WAVE_{number}" for number in range(6))
VALID_TEST_TYPES = {"UNIT", "INTEGRATION", "SECURITY", "CONTRACT", "PACKAGING"}


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def read_jsonl(relative: str):
    return [
        json.loads(line)
        for line in (ROOT / relative).read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_ownership(test, capability_waves, task_waves):
    test_id = test.get("testId")
    capability_ids = list(test.get("capabilityIds") or [])
    task_ids = list(test.get("taskIds") or [])
    requirement_ids = list(test.get("requirementIds") or [])
    unknown_capabilities = sorted(set(capability_ids) - set(capability_waves))
    unknown_tasks = sorted(set(task_ids) - set(task_waves))
    if unknown_capabilities or unknown_tasks:
        raise ValueError(f"{test_id} has unknown owners: capabilities={unknown_capabilities}, tasks={unknown_tasks}")

    task_owner_waves = {task_waves[task_id] for task_id in task_ids}
    capability_owner_waves = {capability_waves[capability_id] for capability_id in capability_ids}
    owner_waves = task_owner_waves | capability_owner_waves
    explicit_wave = test.get("releaseWave")
    if len(owner_waves) != 1:
        raise ValueError(f"{test_id} has ambiguous cross-wave ownership: {sorted(owner_waves)}")
    owning_wave = next(iter(owner_waves))
    if owning_wave not in EXPECTED_WAVES:
        raise ValueError(f"{test_id} resolves to an impossible wave: {owning_wave}")

    if explicit_wave == owning_wave:
        method = "EXPLICIT_TEST_WAVE_CONFIRMED_BY_TASK_AND_CAPABILITY_OWNERS"
    elif len(task_owner_waves) == 1:
        method = "OWNING_TASK_RELEASE_WAVE_OVERRIDES_INVALID_EXPLICIT_TEST_WAVE"
    else:
        method = "OWNING_CAPABILITY_RELEASE_WAVE_OVERRIDES_INVALID_EXPLICIT_TEST_WAVE"

    return {
        "testId": test_id,
        "testType": test.get("testType"),
        "capabilityIds": capability_ids,
        "taskIds": task_ids,
        "requirementIds": requirement_ids,
        "owningWave": owning_wave,
        "ownershipMethod": method,
        "sharedAcrossWaves": False,
        "globalGateTest": False,
        "evidence": [
            {"source": "REQUIREMENT_TEST_MATRIX.jsonl", "explicitTestWave": explicit_wave},
            {"source": "IMPLEMENTATION_TASKS.jsonl", "ownerWaves": sorted(task_owner_waves)},
            {"source": "CAPABILITY_REGISTRY.json", "ownerWaves": sorted(capability_owner_waves)},
        ],
    }


def category_sets(wave, tests, ownership_by_id):
    owned = [test for test in tests if ownership_by_id[test["testId"]]["owningWave"] == wave]
    return {
        "expectedCapabilityOwnedTestIds": [test["testId"] for test in owned if test.get("capabilityIds")],
        "expectedTaskOwnedTestIds": [test["testId"] for test in owned if test.get("taskIds")],
        "expectedSharedTestIds": [test["testId"] for test in owned if ownership_by_id[test["testId"]]["sharedAcrossWaves"]],
        "expectedIntegrationTestIds": [test["testId"] for test in owned if test.get("testType") == "INTEGRATION"],
        "expectedFixtureTestIds": [test["testId"] for test in owned if test.get("fixtures")],
        "expectedGlobalTestIds": [test["testId"] for test in owned if ownership_by_id[test["testId"]]["globalGateTest"]],
    }


def gate_audit(wave, gate, tests, ownership_by_id):
    test_ids = set(ownership_by_id)
    expected = [test["testId"] for test in tests if ownership_by_id[test["testId"]]["owningWave"] == wave]
    current = list((gate or {}).get("requiredTestIds") or [])
    counts = Counter(current)
    missing = sorted(set(expected) - set(current))
    extra = sorted(set(current) - set(expected))
    duplicate = sorted(test_id for test_id, count in counts.items() if count > 1)
    unknown = sorted(set(current) - test_ids)
    wrong_wave = sorted(test_id for test_id in extra if test_id in test_ids)
    present = gate is not None
    result = {
        "gateId": (gate or {}).get("gateId", f"GATE-{wave}"),
        "wave": wave,
        "gatePresent": present,
        **category_sets(wave, tests, ownership_by_id),
        "expectedTestIds": expected,
        "currentTestIds": current,
        "missingTestIds": missing,
        "extraTestIds": extra,
        "duplicateTestIds": duplicate,
        "unknownTestIds": unknown,
        "wrongWaveTestIds": wrong_wave,
        "sharedTestIds": [test_id for test_id in expected if ownership_by_id[test_id]["sharedAcrossWaves"]],
    }
    result["status"] = "MATCH" if present and not any((missing, extra, duplicate, unknown, wrong_wave)) else "MISMATCH"
    return result


def main():
    baseline = read_json("00 Execution Control/FINAL_GATE_REPAIR_BASELINE.json")
    repair_run_id = baseline["repairRunId"]
    capabilities = read_json("03 Capability Map/CAPABILITY_REGISTRY.json")["capabilities"]
    tasks = read_jsonl("09 Implementation/IMPLEMENTATION_TASKS.jsonl")
    tests = read_jsonl("10 Verification/REQUIREMENT_TEST_MATRIX.jsonl")
    release_matrix = read_json("10 Verification/RELEASE_GATE_MATRIX.json")
    capability_waves = {row["capabilityId"]: row.get("releaseWave") for row in capabilities}
    task_waves = {row["taskId"]: row.get("releaseWave") for row in tasks}

    ownership = [resolve_ownership(test, capability_waves, task_waves) for test in tests]
    ownership_by_id = {row["testId"]: row for row in ownership}
    if len(ownership_by_id) != len(tests):
        raise ValueError("Test IDs must be unique before gate synchronization")
    invalid_types = sorted({test.get("testType") for test in tests} - VALID_TEST_TYPES)
    if invalid_types:
        raise ValueError(f"Invalid test types: {invalid_types}")

    ownership_path = COMPLETION / "FINAL_TEST_WAVE_OWNERSHIP.jsonl"
    write_jsonl(ownership_path, ownership)

    old_wave_gates = release_matrix.get("waveGates") or {}
    before_rows = [gate_audit(wave, old_wave_gates.get(wave), tests, ownership_by_id) for wave in EXPECTED_WAVES]
    before_audit = {
        "schemaVersion": "1.0.0",
        "repairRunId": repair_run_id,
        "createdAt": timestamp(),
        "ownershipSource": "11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl",
        "expectedSetMethod": "Test ownership independently derived from task and capability release waves; current gate assignments are never an ownership input.",
        "gateAudits": before_rows,
        "totals": {
            "waveGatesPresent": sum(row["gatePresent"] for row in before_rows),
            "missingTestAssignments": sum(len(row["missingTestIds"]) for row in before_rows),
            "extraTestAssignments": sum(len(row["extraTestIds"]) for row in before_rows),
            "duplicateTestAssignments": sum(len(row["duplicateTestIds"]) for row in before_rows),
            "unknownTestAssignments": sum(len(row["unknownTestIds"]) for row in before_rows),
            "wrongWaveTests": len({test_id for row in before_rows for test_id in row["wrongWaveTestIds"]}),
        },
    }
    audit_path = COMPLETION / "FINAL_WAVE_GATE_TEST_AUDIT.json"
    write_json(audit_path, before_audit)

    corrected_test_ids = []
    for test in tests:
        owning_wave = ownership_by_id[test["testId"]]["owningWave"]
        if test.get("releaseWave") != owning_wave:
            corrected_test_ids.append(test["testId"])
            test["releaseWave"] = owning_wave
    write_jsonl(ROOT / "10 Verification" / "REQUIREMENT_TEST_MATRIX.jsonl", tests)

    new_wave_gates = {}
    for wave in EXPECTED_WAVES:
        if wave in old_wave_gates:
            gate = dict(old_wave_gates[wave])
        else:
            gate = {
                "gateId": f"GATE-{wave}",
                "waveId": wave,
                "title": f"{wave} final evidence release gate",
                "requiredTaskIds": [],
                "requiredCapabilityIds": [],
                "requiredReceipts": [f"VERIFY_{wave}_RECEIPT"],
                "blocking": True,
                "passCriteria": [
                    "All earlier wave gates and required final evidence remain satisfied.",
                    "Application release remains separately NOT_VERIFIED until its release gate passes.",
                    "Codebase execution requires explicit user authorization.",
                ],
                "failureAction": f"BLOCK_{wave}_COMPLETION",
                "status": "PLANNED_NOT_EXECUTED",
            }
        gate["requiredTestIds"] = [test["testId"] for test in tests if ownership_by_id[test["testId"]]["owningWave"] == wave]
        gate["sharedTestIds"] = []
        gate["globalTestIds"] = []
        gate["sharedTestRationales"] = {}
        gate["globalTestRationales"] = {}
        new_wave_gates[wave] = gate
    release_matrix["schemaVersion"] = max(3, int(release_matrix.get("schemaVersion") or 0))
    release_matrix["timestamp"] = timestamp()
    release_matrix["waveGates"] = new_wave_gates
    release_matrix["testWaveOwnershipSource"] = "11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl"
    release_matrix["sharedTestAssignments"] = []
    release_matrix["globalTestAssignments"] = []
    for gate in release_matrix.get("applicationReleaseGates") or []:
        gate["requiredWaveGateIds"] = [f"GATE-{wave}" for wave in EXPECTED_WAVES]
    write_json(ROOT / "10 Verification" / "RELEASE_GATE_MATRIX.json", release_matrix)

    repaired_tests = read_jsonl("10 Verification/REQUIREMENT_TEST_MATRIX.jsonl")
    repaired_ownership = [resolve_ownership(test, capability_waves, task_waves) for test in repaired_tests]
    repaired_ownership_by_id = {row["testId"]: row for row in repaired_ownership}
    repaired_matrix = read_json("10 Verification/RELEASE_GATE_MATRIX.json")
    after_rows = [gate_audit(wave, repaired_matrix["waveGates"].get(wave), repaired_tests, repaired_ownership_by_id) for wave in EXPECTED_WAVES]
    after_totals = {
        "waveGates": len(repaired_matrix["waveGates"]),
        "unknownRequiredTestIds": sum(len(row["unknownTestIds"]) for row in after_rows),
        "duplicateRequiredTestIds": sum(len(row["duplicateTestIds"]) for row in after_rows),
        "missingWaveOwnedTests": sum(len(row["missingTestIds"]) for row in after_rows),
        "wrongWaveTests": len({test_id for row in after_rows for test_id in row["wrongWaveTestIds"]}),
        "ambiguousUnclassifiedSharedTests": sum(row["status"] != "MATCH" for row in after_rows if row["sharedTestIds"]),
        "testsAssignedToImpossibleWave": sum(row["owningWave"] not in EXPECTED_WAVES for row in repaired_ownership),
    }
    passed = after_totals == {
        "waveGates": 6,
        "unknownRequiredTestIds": 0,
        "duplicateRequiredTestIds": 0,
        "missingWaveOwnedTests": 0,
        "wrongWaveTests": 0,
        "ambiguousUnclassifiedSharedTests": 0,
        "testsAssignedToImpossibleWave": 0,
    }
    synchronization = {
        "schemaVersion": "1.0.0",
        "repairRunId": repair_run_id,
        "createdAt": timestamp(),
        "testCount": len(repaired_tests),
        "testWaveMetadataCorrections": corrected_test_ids,
        "before": before_audit["totals"],
        "after": after_totals,
        "gateAudits": after_rows,
        "releaseGateMatrixHash": sha256_file(ROOT / "10 Verification" / "RELEASE_GATE_MATRIX.json"),
        "testMatrixHash": sha256_file(ROOT / "10 Verification" / "REQUIREMENT_TEST_MATRIX.jsonl"),
        "blockingDefects": [] if passed else ["Gate-test synchronization did not reach exact-set equality."],
        "status": "PASS" if passed else "FAIL",
    }
    write_json(COMPLETION / "FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json", synchronization)

    wave_report = read_json("11 Completion/FINAL_WAVE_SYNCHRONIZATION_REPORT.json")
    wave_report.update({
        "repairRunId": repair_run_id,
        "timestamp": timestamp(),
        "authoritativeReleaseWaves": list(EXPECTED_WAVES),
        "releaseWaveCount": len(EXPECTED_WAVES),
        "waveGateCount": len(EXPECTED_WAVES),
        "gateTestSynchronizationStatus": synchronization["status"],
        "testWaveMetadataCorrections": corrected_test_ids,
        "staleWave5Disposition": "Restored as an explicit final-evidence wave gate with no current capability-, task-, or test-owned records; application release remains a separate NOT_VERIFIED gate.",
    })
    write_json(COMPLETION / "FINAL_WAVE_SYNCHRONIZATION_REPORT.json", wave_report)
    print(json.dumps({
        "repairRunId": repair_run_id,
        "tests": len(repaired_tests),
        "correctedTestWaveMetadata": len(corrected_test_ids),
        "wrongWaveTestsBefore": before_audit["totals"]["wrongWaveTests"],
        "wrongWaveTestsAfter": after_totals["wrongWaveTests"],
        "waveGates": after_totals["waveGates"],
        "status": synchronization["status"],
    }, indent=2))
    raise SystemExit(0 if passed else 1)


def repair_test_requirement_references():
    requirements = {row["requirementId"] for row in read_jsonl("03 Capability Map/REQUIREMENT_REGISTRY.jsonl")}
    tasks = {row["taskId"]: row for row in read_jsonl("09 Implementation/IMPLEMENTATION_TASKS.jsonl")}
    tests = read_jsonl("10 Verification/REQUIREMENT_TEST_MATRIX.jsonl")
    ownership = read_jsonl("11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl")
    ownership_by_id = {row["testId"]: row for row in ownership}
    corrections = []
    for test in tests:
        unknown = sorted(set(test.get("requirementIds") or []) - requirements)
        if not unknown:
            continue
        replacements = sorted({requirement_id for task_id in (test.get("taskIds") or []) for requirement_id in (tasks[task_id].get("requirementIds") or []) if requirement_id in requirements})
        if not replacements:
            raise ValueError(f"{test['testId']} has no authoritative replacement for unknown requirements {unknown}")
        corrections.append({"testId": test["testId"], "removedRequirementIds": unknown, "replacementRequirementIds": replacements})
        test["requirementIds"] = replacements
        ownership_by_id[test["testId"]]["requirementIds"] = replacements
    write_jsonl(ROOT / "10 Verification" / "REQUIREMENT_TEST_MATRIX.jsonl", tests)
    write_jsonl(COMPLETION / "FINAL_TEST_WAVE_OWNERSHIP.jsonl", [ownership_by_id[row["testId"]] for row in ownership])
    synchronization = read_json("11 Completion/FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json")
    synchronization["testRequirementMetadataCorrections"] = corrections
    synchronization["testMatrixHash"] = sha256_file(ROOT / "10 Verification" / "REQUIREMENT_TEST_MATRIX.jsonl")
    synchronization["createdAt"] = timestamp()
    write_json(COMPLETION / "FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json", synchronization)
    print(json.dumps({"testRequirementMetadataCorrections": corrections}, indent=2))


if __name__ == "__main__":
    repair_test_requirement_references() if "--repair-test-requirements" in sys.argv else main()
