"""Adversarial mutations against the exact production freeze validator."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
VALIDATOR_PATH = ROOT / "11 Completion" / "validate_final_graphify_freeze.py"
REPORT_PATH = ROOT / "11 Completion" / "FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json"
VALIDATION_RESULT_PATH = ROOT / "00 Execution Control" / "FINAL_FREEZE_VALIDATION_RESULT.json"

MANIFEST_RELATIVE = "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"
FROZEN_MANIFEST_RELATIVE = "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl"
CAPABILITY_PATH = "03 Capability Map/CAPABILITY_REGISTRY.json"
TASK_PATH = "09 Implementation/IMPLEMENTATION_TASKS.jsonl"
LINEAGE_PATH = "03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl"
GATE_PATH = "10 Verification/RELEASE_GATE_MATRIX.json"
TEST_PATH = "10 Verification/REQUIREMENT_TEST_MATRIX.jsonl"
EXACT_LOCATION_PATH = "04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json"
BACKUP_RECEIPT_PATH = "00 Execution Control/FINAL_AUTHORITATIVE_FREEZE_BACKUP_VERIFICATION.json"
LIVE_REPORT_PATH = "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("mindroom_strict_validator", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def mutate_json(path, mutator):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    mutator(value)
    write_json(path, value)


def mutate_jsonl(path, mutator):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    mutator(rows)
    write_jsonl(path, rows)


def copy_overrides(temp_root, relatives):
    overrides, temporary = {}, []
    for relative in relatives:
        destination = temp_root / relative.replace("/", "__")
        shutil.copy2(ROOT / relative, destination)
        overrides[relative] = str(destination)
        # Persist only the logical source path. The random external temporary
        # root is execution detail and must not make certification receipts
        # nondeterministic across otherwise identical runs.
        temporary.append(relative)
    return overrides, temporary


def failed_ids(result):
    return {check["checkId"] for check in result["checks"] if check["status"] == "FAIL"}


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def github_backup_snapshot(validator, receipt):
    actual = validator.inspect_github_backup(receipt, verify_lfs=False)
    if not actual.get("remoteRefTarget") or actual.get("errors"):
        raise RuntimeError(f"GitHub backup is not reproducible before challenge execution: {actual.get('errors')}")
    identity = {key: actual.get(key) for key in (
        "remoteRefTarget", "treeSha", "graphifyTreeSha", "codebaseTreeSha",
        "trackedPathCount", "trackedPathSetSha256", "lfsObjects",
    )}
    identity["aggregateSha256"] = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return identity


def common_metadata(status):
    return {key: status.get(key) for key in (
        "freezeRunId", "officialValidatorRunId", "externalReviewRunId", "mappingStatus",
        "independentReviewStatus", "planningFreezeStatus", "wave0Readiness",
        "codebaseExecutionStatus", "finalReleaseReceiptStatus", "canonicalCounts",
        "manifestRecordCount", "manifestAggregateHash", "codebaseFileCount",
        "codebaseDirectoryCount", "codebaseAggregateHash", "validatorCheckCount",
        "challengeTestCount", "blockingDefectCount", "repairRunId",
        "gateTestSynchronizationStatus", "warningSummary", "backupBackend",
        "currentBackupRef", "persistentLocalBackupRequired",
    )}


def certification_timestamp(status):
    """Return the phase timestamp fixed by governance finalization."""
    value = status.get("certificationTimestamp") or status.get("timestamp") or status.get("lastUpdatedAt")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("A stable certification timestamp is required in canonical status metadata.")
    return value


def alias_row(legacy_id, target, node_id, ev_target):
    return {
        "legacyRequirementId": legacy_id,
        "legacyRequirementType": "ADD",
        "legacySourceArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
        "legacySourceLocation": "jsonl:1",
        "resolutionStatus": "ALIAS",
        "canonicalRequirementIds": [target],
        "supersessionRecordIds": [],
        "normalizationEvidence": [
            {
                "evidenceType": "ALIAS_BINDING",
                "nodeId": node_id,
                "canonicalRequirementId": ev_target,
                "artifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
                "location": "jsonl:1",
            }
        ],
        "resolutionReason": "Alias binding test",
        "confidence": "HIGH",
        "reviewRequired": False,
    }


def reclassified_row(legacy_id, target, node_id, ev_target):
    return {
        "legacyRequirementId": legacy_id,
        "legacyRequirementType": "ADD",
        "legacySourceArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
        "legacySourceLocation": "jsonl:1",
        "resolutionStatus": "RECLASSIFIED",
        "canonicalRequirementIds": [target] if target else [],
        "supersessionRecordIds": [],
        "normalizationEvidence": [
            {
                "evidenceType": "RECLASSIFICATION_DECISION",
                "nodeId": node_id,
                "canonicalRequirementId": ev_target,
                "originalClassification": "ADD",
                "newClassification": "KEEP",
                "artifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
                "location": "jsonl:1",
            }
        ],
        "resolutionReason": "Reclassified after normalization review",
        "confidence": "HIGH",
        "reviewRequired": False,
    }


def change_evidence_status(data, rows, owner_key, evidence_key, source_key):
    statuses = ["DIRECT", "SUPERSEDED", "MERGED", "SPLIT", "RECLASSIFIED", "PROHIBITED", "EXCLUDED", "ALIAS"]
    items = []
    if rows is None:
        for record in data.get(owner_key, []):
            items.extend(record.get(evidence_key) or [])
            if items:
                break
    else:
        for record in rows:
            items.extend(record.get(evidence_key) or [])
            if items:
                break
    current = items[0].get("resolutionStatus")
    items[0]["resolutionStatus"] = next(value for value in statuses if value != current)


def change_evidence_source(data, rows, owner_key, evidence_key, wrong_source):
    items = []
    if rows is None:
        for record in data.get(owner_key, []):
            items.extend(record.get(evidence_key) or [])
            if items:
                break
    else:
        for record in rows:
            items.extend(record.get(evidence_key) or [])
            if items:
                break
    items[0]["sourceRequirementId"] = wrong_source


def mr_impl_001(rows):
    return next(row for row in rows if row.get("taskId") == "MR-IMPL-001")


def mutate_missing_current_anchor(data):
    row = data["locations"]["MR-CAP-001"]["sourceAnchors"][0]
    row.update({
        "semanticType": "TYPESCRIPT_EXPORTED_SYMBOL",
        "literal": "export interface MR_CAP_001_AdversarialMissingSymbol",
    })


def mutate_owner_not_allowed(rows):
    task = mr_impl_001(rows)
    owner = task["contract"]["ownedPackageOrModule"]
    task["allowedPaths"].remove(owner)


def mutate_owner_caught_by_catchall(rows):
    task = mr_impl_001(rows)
    owner = task["contract"]["ownedPackageOrModule"]
    task["allowedPaths"].remove(owner)
    task["forbiddenPaths"].append("All paths not listed in allowedPaths")


def mutate_required_build_entry_omitted(rows):
    task = mr_impl_001(rows)
    task["architecturePreservationContract"]["buildEntryPaths"].pop(0)


def mutate_generated_output_as_canonical(rows):
    task = mr_impl_001(rows)
    generated_file = task["architecturePreservationContract"]["generatedOutputRoots"][0] + "/dist/adversarial.js"
    task["allowedPaths"].append(generated_file)
    task["ownedPaths"].append(generated_file)


def mutate_acceptance_missing_anchor(rows):
    test = next(row for row in rows if row.get("testId") == "TEST-MR-CAP-001-UNIT-001")
    test["executableAssertions"][0] = {
        "assertion": "SOURCE_LITERAL_PRESENT",
        "path": "Codebase/packages/frontend/core/package.json",
        "literal": "MR_CAP_001_AdversarialAcceptanceAnchor",
    }


def definition(challenge_id, mutation, relatives, expected, mutator, validation_mode="CORE_PRE_CHALLENGE"):
    return {
        "challengeId": challenge_id,
        "mutation": mutation,
        "relatives": relatives,
        "expectedFailedCheckIds": expected,
        "mutator": mutator,
        "validationMode": validation_mode,
    }


CHALLENGE_DEFINITIONS = [
    definition("CHALLENGE-001", "Remove one requirement while independent traceability retains it", ["03 Capability Map/REQUIREMENT_REGISTRY.jsonl"], ["CNT-02"], lambda o: mutate_jsonl(Path(o["03 Capability Map/REQUIREMENT_REGISTRY.jsonl"]), lambda rows: rows.pop())),
    definition("CHALLENGE-002", "Duplicate a capability ID", [CAPABILITY_PATH], ["CAP-01"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"].append(copy.deepcopy(data["capabilities"][0])))),
    definition("CHALLENGE-003", "Add an unknown MR-IMPL task dependency", [TASK_PATH], ["DEP-05"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: rows[0].setdefault("dependencies", []).append("MR-IMPL-NOT-DEFINED"))),
    definition("CHALLENGE-004", "Add a task self-dependency", [TASK_PATH], ["DEP-06"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: rows[0].setdefault("dependencies", []).append(rows[0]["taskId"]))),
    definition("CHALLENGE-005", "Create a two-task dependency cycle", [TASK_PATH], ["DEP-08"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: (lambda first, second: (first.setdefault("dependencies", []).append(second["taskId"]), second.setdefault("dependencies", []).append(first["taskId"])))(rows[0], rows[1]))),
    definition("CHALLENGE-006", "Make a Wave 0 task depend on a Wave 1 task", [TASK_PATH], ["DEP-09"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: (lambda source, target: source.setdefault("dependencies", []).append(target["taskId"]))(next(row for row in rows if row.get("releaseWave") == "WAVE_0"), next(row for row in rows if row.get("releaseWave") == "WAVE_1")))),
    definition("CHALLENGE-007", "Create a two-capability execution cycle", ["05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json"], ["DEP-03"], lambda o: mutate_json(Path(o["05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json"]), lambda data: data.setdefault("edges", []).extend([
        {"sourceNodeId": "MR-CAP-001", "targetNodeId": "MR-CAP-002", "relation": "DEPENDS_ON"},
        {"sourceNodeId": "MR-CAP-002", "targetNodeId": "MR-CAP-001", "relation": "DEPENDS_ON"},
    ]))),
    definition("CHALLENGE-008", "Make a Wave 0 capability depend on a Wave 1 capability", ["05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json"], ["DEP-04"], lambda o: mutate_json(Path(o["05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json"]), lambda data: data.setdefault("edges", []).append({"sourceNodeId": "MR-CAP-001", "targetNodeId": "MR-CAP-007", "relation": "DEPENDS_ON"}))),
    definition("CHALLENGE-009", "Point the authority index at a missing file", ["00 Execution Control/FINAL_AUTHORITY_INDEX.json"], ["AUTH-03"], lambda o: mutate_json(Path(o["00 Execution Control/FINAL_AUTHORITY_INDEX.json"]), lambda data: data["authoritativeMap"].__setitem__("strictValidator", "11 Completion/NO_SUCH_VALIDATOR.py"))),
    definition("CHALLENGE-AUTHORITY-CLASSIFICATION-001", "Point the current authority map at an existing historical status artifact", ["00 Execution Control/FINAL_AUTHORITY_INDEX.json"], ["AUTH-09"], lambda o: mutate_json(Path(o["00 Execution Control/FINAL_AUTHORITY_INDEX.json"]), lambda data: data["authoritativeMap"].__setitem__("statusAuthority", "00 Execution Control/STATUS_AUTHORITY.json"))),
    definition("CHALLENGE-010", "Replace one frozen artifact SHA-256", [MANIFEST_RELATIVE], ["MAN-03"], lambda o: mutate_jsonl(Path(o[MANIFEST_RELATIVE]), lambda rows: rows[0].__setitem__("sha256", "0" * 64))),
    definition("CHALLENGE-011", "Insert the active manifest into itself", [MANIFEST_RELATIVE], ["MAN-01"], lambda o: mutate_jsonl(Path(o[MANIFEST_RELATIVE]), lambda rows: rows.append({"path": MANIFEST_RELATIVE, "sha256": "0" * 64}))),
    definition("CHALLENGE-012", "Break the protected-governance manifest hash agreement", ["00 Execution Control/STATUS.json"], ["MAN-08"], lambda o: mutate_json(Path(o["00 Execution Control/STATUS.json"]), lambda data: data.__setitem__("manifestAggregateHash", "0" * 64))),
    definition("CHALLENGE-013", "Restore the forbidden generic planned-capability phrase", [CAPABILITY_PATH], ["CON-04"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["contract"].__setitem__("purpose", "Implement planned MindRoom capability scope"))),
    definition("CHALLENGE-014", "Change an embedded capability wave", [CAPABILITY_PATH], ["CON-01"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["contract"].__setitem__("releaseWave", "WAVE_9"))),
    definition("CHALLENGE-015", "Change an embedded task wave", [TASK_PATH], ["CON-02"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: rows[0]["contract"].__setitem__("releaseWave", "WAVE_9"))),
    definition("CHALLENGE-016", "Assign PBKDF2 evidence to an unrelated task", ["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"], ["WARN-02"], lambda o: mutate_json(Path(o["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"]), lambda data: data["warnings"][0].__setitem__("owningTaskIds", ["MR-IMPL-001"]))),
    definition("CHALLENGE-017", "Remove one PBKDF2 owning-wave gate", ["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"], ["WARN-04"], lambda o: mutate_json(Path(o["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"]), lambda data: data["warnings"][0].__setitem__("blockingGateIds", []))),
    definition("CHALLENGE-018", "Assign adapter isolation to the wrong wave", ["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"], ["WARN-07"], lambda o: mutate_json(Path(o["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"]), lambda data: data["warnings"][1].update({"releaseWave": "WAVE_2", "owningWaves": ["WAVE_2"]}))),
    definition("CHALLENGE-019", "Replace CalDAV ownership with an unrelated finance capability", ["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"], ["WARN-05", "WARN-06"], lambda o: mutate_json(Path(o["11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json"]), lambda data: data["warnings"][1].update({"affectedCapabilityIds": ["MR-CAP-133"], "owningTaskIds": ["MR-IMPL-133"]}))),
    definition("CHALLENGE-020", "Report zero release waves in a completion receipt", ["11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json"], ["META-07"], lambda o: mutate_json(Path(o["11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json"]), lambda data: data["canonicalCounts"].__setitem__("releaseWaves", 0))),
    definition("CHALLENGE-021", "Use a conflicting freeze run ID", ["00 Execution Control/STATUS.json"], ["META-01"], lambda o: mutate_json(Path(o["00 Execution Control/STATUS.json"]), lambda data: data.__setitem__("freezeRunId", "conflicting-freeze-run"))),
    definition("CHALLENGE-022", "Falsely verify application release", ["00 Execution Control/STATUS.json"], ["META-06", "SAFE-04"], lambda o: mutate_json(Path(o["00 Execution Control/STATUS.json"]), lambda data: data.__setitem__("finalReleaseReceiptStatus", "VERIFIED"))),
    definition("CHALLENGE-023", "Prematurely start Wave 0", ["00 Execution Control/STATUS.json"], ["META-04", "SAFE-02"], lambda o: mutate_json(Path(o["00 Execution Control/STATUS.json"]), lambda data: data.__setitem__("wave0Readiness", "WAVE_0_STARTED"))),
    definition("CHALLENGE-024", "Replace the captured Codebase after hash", ["00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json"], ["CB-05"], lambda o: mutate_json(Path(o["00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json"]), lambda data: data["codebasePreservation"]["after"].__setitem__("aggregateSha256", "f" * 64))),
    definition("CHALLENGE-025", "Remove one Codebase file from the captured baseline manifest", ["00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json"], ["CB-06", "CB-08"], lambda o: mutate_json(Path(o["00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json"]), lambda data: data["codebasePreservation"]["baselineFiles"].pop())),

    definition("CHALLENGE-GATE-001", "Remove a required test from its correct wave gate", [GATE_PATH], ["GATE-05", "GATE-06"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: data["waveGates"]["WAVE_1"]["requiredTestIds"].pop())),
    definition("CHALLENGE-GATE-002", "Add a WAVE_2 test to WAVE_1", [GATE_PATH], ["GATE-05", "GATE-07"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: data["waveGates"]["WAVE_1"]["requiredTestIds"].append(data["waveGates"]["WAVE_2"]["requiredTestIds"][0]))),
    definition("CHALLENGE-GATE-003", "Duplicate one requiredTestId", [GATE_PATH], ["GATE-04"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: data["waveGates"]["WAVE_1"]["requiredTestIds"].append(data["waveGates"]["WAVE_1"]["requiredTestIds"][0]))),
    definition("CHALLENGE-GATE-004", "Add an unknown test ID", [GATE_PATH], ["GATE-03", "GATE-05"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: data["waveGates"]["WAVE_1"]["requiredTestIds"].append("TEST-NOT-DEFINED"))),
    definition("CHALLENGE-GATE-005", "Assign a test to the wrong explicit owning wave", [TEST_PATH], ["TEST-08"], lambda o: mutate_jsonl(Path(o[TEST_PATH]), lambda rows: next(value for value in rows if value.get("releaseWave") == "WAVE_1").__setitem__("releaseWave", "WAVE_2"))),
    definition("CHALLENGE-GATE-006", "Remove an entire wave gate", [GATE_PATH], ["GATE-01"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: data["waveGates"].pop("WAVE_5"))),
    definition("CHALLENGE-GATE-007", "Change gateId without changing gate wave", [GATE_PATH], ["GATE-02"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: data["waveGates"]["WAVE_1"].__setitem__("gateId", "GATE-WAVE_2"))),
    definition("CHALLENGE-GATE-008", "Mark a wrong-wave test as shared without evidence", [GATE_PATH], ["GATE-07", "GATE-08"], lambda o: mutate_json(Path(o[GATE_PATH]), lambda data: (lambda test_id: (data["waveGates"]["WAVE_1"]["requiredTestIds"].append(test_id), data["waveGates"]["WAVE_1"].setdefault("sharedTestIds", []).append(test_id)))(data["waveGates"]["WAVE_2"]["requiredTestIds"][0]))),
    definition("CHALLENGE-GATE-009", "Create conflicting task and capability ownership waves", [TASK_PATH], ["TEST-05", "CON-03"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: next(value for value in rows if value.get("taskClass") == "PRIMARY_CAPABILITY_TASK" and value.get("releaseWave") == "WAVE_1").__setitem__("releaseWave", "WAVE_2"))),
    definition("CHALLENGE-GATE-010", "Make a completion receipt claim zero synchronized gates", ["11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json"], ["META-07"], lambda o: mutate_json(Path(o["11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json"]), lambda data: data["canonicalCounts"].__setitem__("waveGates", 0))),

    definition("CHALLENGE-LINEAGE-001", "Add an unknown legacy sourceRequirementId to a capability", [CAPABILITY_PATH], ["LIN-14"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["sourceRequirementIds"].append("MR-LEGACY-NOT-DEFINED"))),
    definition("CHALLENGE-LINEAGE-002", "Add an unknown sourceRequirements ID to a task", [TASK_PATH], ["LIN-19"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: rows[0]["sourceRequirements"].append("MR-LEGACY-NOT-DEFINED"))),
    definition("CHALLENGE-LINEAGE-003", "Remove a referenced legacy ID from the lineage map", [LINEAGE_PATH], ["LIN-02"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.pop(0))),
    definition("CHALLENGE-LINEAGE-004", "Map a legacy ID to a non-existent canonical requirement", [LINEAGE_PATH], ["LIN-03"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].__setitem__("canonicalRequirementIds", ["MR-REQ-NOT-DEFINED"]))),
    definition("CHALLENGE-LINEAGE-005", "Create two conflicting mappings for one legacy ID", [LINEAGE_PATH], ["LIN-01", "LIN-12"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append({**copy.deepcopy(rows[0]), "canonicalRequirementIds": []}))),
    definition("CHALLENGE-LINEAGE-006", "Set resolutionStatus to DIRECT with zero canonical targets", [LINEAGE_PATH], ["LIN-06"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: next(value for value in rows if not value.get("canonicalRequirementIds")).__setitem__("resolutionStatus", "DIRECT"))),
    definition("CHALLENGE-LINEAGE-007", "Set resolutionStatus to SPLIT with one canonical target", [LINEAGE_PATH], ["LIN-08"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: next(value for value in rows if len(value.get("canonicalRequirementIds") or []) == 1).__setitem__("resolutionStatus", "SPLIT"))),
    definition("CHALLENGE-LINEAGE-008", "Mark a lineage mapping UNRESOLVED", [LINEAGE_PATH], ["LIN-11"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].__setitem__("resolutionStatus", "UNRESOLVED"))),
    definition("CHALLENGE-LINEAGE-009", "Change a capability resolved canonical set away from lineage expansion", [CAPABILITY_PATH], ["LIN-16"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["resolvedCanonicalRequirementIds"].append("MR-REQ-PROHIBITION-AI-REMOTE-001"))),
    definition("CHALLENGE-LINEAGE-010", "Change a task resolved canonical set away from lineage expansion", [TASK_PATH], ["LIN-21"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: rows[0]["resolvedCanonicalRequirementIds"].append("MR-REQ-CANVAS-FOUNDATIONS-001"))),
    definition("CHALLENGE-LINEAGE-011", "Silently remove one original capability source ID", [CAPABILITY_PATH], ["LIN-17"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["sourceRequirementIds"].pop())),
    definition("CHALLENGE-LINEAGE-012", "Silently remove one original task source ID", [TASK_PATH], ["LIN-22"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: rows[0]["sourceRequirements"].pop())),
    definition("CHALLENGE-LINEAGE-013", "Reference a missing supersession record", [LINEAGE_PATH], ["LIN-04"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].__setitem__("supersessionRecordIds", ["MR-SUP-NOT-DEFINED"]))),
    definition("CHALLENGE-LINEAGE-014", "Create a low-confidence review-required mapping", [LINEAGE_PATH], ["LIN-13"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].update({"confidence": "LOW", "reviewRequired": True}))),

    definition("CHALLENGE-LINEAGE-STATUS-001", "Set resolutionStatus to an unknown value", [LINEAGE_PATH], ["LINEAGE-STATUS-ENUM"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].__setitem__("resolutionStatus", "NOT_A_REAL_STATUS"))),
    definition("CHALLENGE-LINEAGE-RECLASSIFIED-001", "Create an invalid RECLASSIFIED record without prior/new classification evidence", [LINEAGE_PATH], ["LINEAGE-RECLASSIFIED-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append({"legacyRequirementId": "MR-RECLASS-TEST-001", "legacyRequirementType": "ADD", "legacySourceArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl", "legacySourceLocation": "jsonl:1", "resolutionStatus": "RECLASSIFIED", "canonicalRequirementIds": ["MR-KEEP-002"], "supersessionRecordIds": [], "normalizationEvidence": [{"evidenceType": "RECLASSIFICATION_DECISION", "nodeId": "MR-RECLASS-TEST-001", "canonicalRequirementId": "MR-KEEP-002"}], "resolutionReason": "Reclassified without prior or new classification evidence", "confidence": "HIGH", "reviewRequired": False}))),
    definition("CHALLENGE-LINEAGE-ALIAS-001", "Create an alias pointing to a missing canonical target", [LINEAGE_PATH], ["LINEAGE-ALIAS-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append(alias_row("MR-ALIAS-TEST-001", "MR-REQ-NOT-DEFINED", "MR-ALIAS-TEST-001", "MR-REQ-NOT-DEFINED")))),
    definition("CHALLENGE-LINEAGE-ALIAS-002", "Create an alias cycle", [LINEAGE_PATH], ["LINEAGE-ALIAS-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.extend([alias_row("MR-ALIAS-A", "MR-ALIAS-B", "MR-ALIAS-A", "MR-ALIAS-B"), alias_row("MR-ALIAS-B", "MR-ALIAS-A", "MR-ALIAS-B", "MR-ALIAS-A")]))),
    definition("CHALLENGE-LINEAGE-MERGED-001", "Corrupt MERGED evidence so it refers to another legacy source ID", [LINEAGE_PATH], ["LINEAGE-MERGED-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: (lambda row: next((item.__setitem__("nodeId", "MR-OTHER-LEGACY-999") for item in row.get("normalizationEvidence") or [] if item.get("nodeId")), None))(next(value for value in rows if value.get("resolutionStatus") == "MERGED")))),
    definition("CHALLENGE-LINEAGE-MERGED-002", "Remove one declared canonical target from MERGED evidence", [LINEAGE_PATH], ["LINEAGE-MERGED-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: (lambda row: row.__setitem__("normalizationEvidence", [item for item in (row.get("normalizationEvidence") or []) if not item.get("canonicalRequirementId")]))(next(value for value in rows if value.get("resolutionStatus") == "MERGED")))),
    definition("CHALLENGE-LINEAGE-PROHIBITED-001", "Create a PROHIBITED record with unrelated prohibition evidence", [LINEAGE_PATH], ["LINEAGE-PROHIBITED-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append({"legacyRequirementId": "MR-PROHIBIT-TEST-001", "legacyRequirementType": "ADD", "legacySourceArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl", "legacySourceLocation": "jsonl:1", "resolutionStatus": "PROHIBITED", "canonicalRequirementIds": [], "supersessionRecordIds": [], "normalizationEvidence": [{"evidenceType": "EXPLICIT_EXCLUSION_DECISION", "artifact": "11 Completion/REQUIREMENT_NORMALIZATION_REPORT.json", "location": "unrelated exclusion rule", "decision": "EXCLUDED_NON_NORMATIVE_SOURCE_FRAGMENT", "nodeId": "MR-PROHIBIT-TEST-001"}], "resolutionReason": "Prohibited using unrelated evidence", "confidence": "HIGH", "reviewRequired": False}))),
    definition("CHALLENGE-LINEAGE-EXCLUDED-001", "Create an EXCLUDED record without authoritative exclusion evidence", [LINEAGE_PATH], ["LINEAGE-EXCLUDED-SEMANTICS"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append({"legacyRequirementId": "MR-EXCL-TEST-001", "legacyRequirementType": "ADD", "legacySourceArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl", "legacySourceLocation": "jsonl:1", "resolutionStatus": "EXCLUDED", "canonicalRequirementIds": [], "supersessionRecordIds": [], "normalizationEvidence": [{"evidenceType": "ORIGINAL_SOURCE_REQUIREMENT_NODE", "nodeId": "MR-EXCL-TEST-001", "artifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl", "location": "jsonl:1"}], "resolutionReason": "Excluded without authoritative evidence", "confidence": "HIGH", "reviewRequired": False}))),
    definition("CHALLENGE-CAPABILITY-EVIDENCE-001", "Change capability lineage evidence to cite the wrong source ID", [CAPABILITY_PATH], ["CAPABILITY-LINEAGE-EVIDENCE"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["requirementLineageEvidence"][0].__setitem__("sourceRequirementId", "MR-KEEP-NOT-DEFINED"))),
    definition("CHALLENGE-CAPABILITY-EVIDENCE-002", "Change capability lineage evidence to cite an extra canonical target", [CAPABILITY_PATH], ["CAPABILITY-LINEAGE-EVIDENCE"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: data["capabilities"][0]["requirementLineageEvidence"][0].__setitem__("canonicalRequirementIds", ["MR-KEEP-001", "MR-REQ-PROHIBITION-AI-REMOTE-001"]))),
    definition("CHALLENGE-TASK-EVIDENCE-001", "Change task lineage evidence to cite the wrong lineage-map record", [TASK_PATH], ["TASK-LINEAGE-EVIDENCE"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: next(value for value in rows if value.get("requirementLineageEvidence"))["requirementLineageEvidence"][0].__setitem__("supersessionRecordIds", ["MR-SUP-NOT-DEFINED"]))),
    definition("CHALLENGE-TASK-EVIDENCE-002", "Remove one task canonical target from its evidence payload", [TASK_PATH], ["TASK-LINEAGE-EVIDENCE"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: (lambda row: next((item.__setitem__("canonicalRequirementIds", []) for item in row["requirementLineageEvidence"] if item.get("canonicalRequirementIds")), None))(next(value for value in rows if any(item.get("canonicalRequirementIds") for item in (value.get("requirementLineageEvidence") or [])))))),
    definition("CHALLENGE-LINEAGE-CONFIDENCE-001", "Set a lineage mapping confidence to LOW", [LINEAGE_PATH], ["LINEAGE-CONFIDENCE"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].__setitem__("confidence", "LOW"))),
    definition("CHALLENGE-LINEAGE-REVIEW-001", "Set a lineage mapping reviewRequired to true", [LINEAGE_PATH], ["LINEAGE-CONFIDENCE"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows[0].__setitem__("reviewRequired", True))),

    definition("CHALLENGE-CAP-EVIDENCE-STATUS-001", "Change capability evidence to another allowed but incorrect status", [CAPABILITY_PATH], ["CAPABILITY-LINEAGE-EVIDENCE-STATUS"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: change_evidence_status(data, None, "capabilities", "requirementLineageEvidence", "sourceRequirementId"))),
    definition("CHALLENGE-TASK-EVIDENCE-STATUS-001", "Change task evidence to another allowed but incorrect status", [TASK_PATH], ["TASK-LINEAGE-EVIDENCE-STATUS"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: change_evidence_status(None, rows, "taskId", "requirementLineageEvidence", "sourceRequirementId"))),
    definition("CHALLENGE-CAP-EVIDENCE-SOURCE-001", "Change capability evidence to another source ID", [CAPABILITY_PATH], ["CAPABILITY-LINEAGE-EVIDENCE-SOURCE"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: change_evidence_source(data, None, "capabilities", "requirementLineageEvidence", "MR-REQ-0001"))),
    definition("CHALLENGE-TASK-EVIDENCE-SOURCE-001", "Change task evidence to another source ID", [TASK_PATH], ["TASK-LINEAGE-EVIDENCE-SOURCE"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: change_evidence_source(None, rows, "taskId", "requirementLineageEvidence", "MR-REQ-0002"))),
    definition("CHALLENGE-CAP-EVIDENCE-TARGET-001", "Add an extra capability canonical target", [CAPABILITY_PATH], ["CAPABILITY-LINEAGE-EVIDENCE-TARGETS"], lambda o: mutate_json(Path(o[CAPABILITY_PATH]), lambda data: (lambda ev: ev[0].setdefault("canonicalRequirementIds", []).append("MR-REQ-PROHIBITION-AI-REMOTE-001"))(next((cap.get("requirementLineageEvidence") or []) for cap in data["capabilities"] if cap.get("requirementLineageEvidence"))))),
    definition("CHALLENGE-TASK-EVIDENCE-TARGET-001", "Remove a required task canonical target", [TASK_PATH], ["TASK-LINEAGE-EVIDENCE-TARGETS"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: (lambda row: next((item.__setitem__("canonicalRequirementIds", []) for item in row["requirementLineageEvidence"] if item.get("canonicalRequirementIds")), None))(next(value for value in rows if any(item.get("canonicalRequirementIds") for item in (value.get("requirementLineageEvidence") or [])))))),
    definition("CHALLENGE-ALIAS-SOURCE-001", "Use the wrong legacy source in alias evidence", [LINEAGE_PATH], ["LINEAGE-ALIAS-SOURCE"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append(alias_row("MR-ALIAS-TEST-002", "MR-KEEP-002", "MR-OTHER-LEGACY-999", "MR-KEEP-002")))),
    definition("CHALLENGE-ALIAS-TARGET-001", "Use the wrong canonical target in alias evidence", [LINEAGE_PATH], ["LINEAGE-ALIAS-TARGET"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append(alias_row("MR-ALIAS-TEST-003", "MR-KEEP-002", "MR-ALIAS-TEST-003", "MR-KEEP-003")))),
    definition("CHALLENGE-RECLASSIFIED-SOURCE-001", "Use the wrong source ID in reclassification evidence", [LINEAGE_PATH], ["LINEAGE-RECLASSIFIED-SOURCE"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append(reclassified_row("MR-RECLASS-TEST-002", "MR-KEEP-002", "MR-OTHER-LEGACY-998", "MR-KEEP-002")))),
    definition("CHALLENGE-RECLASSIFIED-TARGET-001", "Use the wrong canonical/control target", [LINEAGE_PATH], ["LINEAGE-RECLASSIFIED-TARGET"], lambda o: mutate_jsonl(Path(o[LINEAGE_PATH]), lambda rows: rows.append(reclassified_row("MR-RECLASS-TEST-003", "MR-KEEP-002", "MR-RECLASS-TEST-003", "MR-KEEP-003")))),
    definition("CHALLENGE-BACKUP-MISSING-REF-001", "Remove the required GitHub backup ref", [BACKUP_RECEIPT_PATH], ["BAK-01", "BAK-02", "META-19"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("ref", ""))),
    definition("CHALLENGE-BACKUP-UNREACHABLE-REF-001", "Point at a syntactically valid but unreachable GitHub backup tag", [BACKUP_RECEIPT_PATH], ["BAK-02", "META-19"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("ref", "refs/tags/mindroom-backup/change-control/NO-SUCH-TAG"))),
    definition("CHALLENGE-BACKUP-WRONG-COMMIT-001", "Record a commit that differs from the remote tag target", [BACKUP_RECEIPT_PATH], ["BAK-03"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("commitSha", "0" * 40))),
    definition("CHALLENGE-BACKUP-WRONG-TREE-001", "Corrupt the recorded complete Git tree", [BACKUP_RECEIPT_PATH], ["BAK-10"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("treeSha", "0" * 40))),
    definition("CHALLENGE-BACKUP-WRONG-GRAPHIFY-001", "Corrupt the recorded Graphify subtree", [BACKUP_RECEIPT_PATH], ["BAK-05"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("graphifyTreeSha", "0" * 40))),
    definition("CHALLENGE-BACKUP-WRONG-CODEBASE-001", "Corrupt the recorded Codebase subtree", [BACKUP_RECEIPT_PATH], ["BAK-06"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("codebaseTreeSha", "0" * 40))),
    definition("CHALLENGE-BACKUP-INCOMPLETE-PATH-SET-001", "Corrupt the recorded tracked repository path-set identity", [BACKUP_RECEIPT_PATH], ["BAK-07"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("trackedPathSetSha256", "0" * 64))),
    definition("CHALLENGE-BACKUP-MISSING-LFS-001", "Remove one required LFS object from the receipt", [BACKUP_RECEIPT_PATH], ["BAK-08"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data["lfsObjects"].pop())),
    definition("CHALLENGE-BACKUP-LOCAL-REQUIRED-001", "Regress the current policy to require a persistent laptop backup", [BACKUP_RECEIPT_PATH], ["BAK-01", "META-19"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("persistentLocalBackupRequired", True))),
    definition("CHALLENGE-BACKUP-LOCAL-MASQUERADE-001", "Add an active local backup path to the GitHub receipt", [BACKUP_RECEIPT_PATH], ["BAK-13"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("backupRoot", "C:\\MindRoom-Recovery\\masquerade"))),
    definition("CHALLENGE-BACKUP-VERIFICATION-001", "Regress the current backup receipt verification status", [BACKUP_RECEIPT_PATH], ["BAK-11"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("status", "PENDING"))),
    definition("CHALLENGE-BACKUP-AUTHORITY-DUPLICATE-001", "Add a sibling backupEvidence authority object that duplicates backupHistory", [BACKUP_RECEIPT_PATH], ["BAK-13"], lambda o: mutate_json(Path(o[BACKUP_RECEIPT_PATH]), lambda data: data.__setitem__("backupEvidence", copy.deepcopy(data["backupHistory"])))),
    definition("CHALLENGE-TASK-OWNERSHIP-CONFLICT-001", "Give the bootstrap task a root owner that conflicts with its contract, owner set, and test", [TASK_PATH], ["TASK-OWNERSHIP-01"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), lambda rows: next(row for row in rows if row.get("taskId") == "MR-IMPL-BOOTSTRAP-001").__setitem__("capabilityId", "MR-CAP-160"))),
    definition("CHALLENGE-LIVE-REPORT-OVERRIDE-001", "Set the live validation report's overridesUsed to true", [LIVE_REPORT_PATH], ["META-17"], lambda o: mutate_json(Path(o[LIVE_REPORT_PATH]), lambda data: data.__setitem__("overridesUsed", True)), validation_mode="FULL_TECHNICAL_CERTIFICATION"),
    definition("CHALLENGE-MANIFEST-VALIDATOR-HASH-001", "Set the candidate manifest's validator SHA-256 to a stale value", [MANIFEST_RELATIVE], ["MAN-03"], lambda o: mutate_jsonl(Path(o[MANIFEST_RELATIVE]), lambda rows: next(row for row in rows if row.get("path") == "11 Completion/validate_final_graphify_freeze.py").__setitem__("sha256", "0" * 64))),
    definition("CHALLENGE-FROZEN-CANDIDATE-FLAG-001", "Regress frozen status to candidate-only", ["00 Execution Control/STATUS.json"], ["SAFE-06"], lambda o: mutate_json(Path(o["00 Execution Control/STATUS.json"]), lambda data: data.__setitem__("freezeCandidateOnly", True))),
    definition("CHALLENGE-FROZEN-PENDING-REVIEW-001", "Regress final synchronization to pending independent review", ["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"], ["SYNC-02"], lambda o: mutate_json(Path(o["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"]), lambda data: data.__setitem__("pendingIndependentReview", True))),
    definition("CHALLENGE-FROZEN-WAVE0-BLOCKED-001", "Regress final synchronization to review-blocked Wave 0", ["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"], ["SYNC-03"], lambda o: mutate_json(Path(o["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"]), lambda data: data.__setitem__("wave0Blocked", True))),
    definition("CHALLENGE-FROZEN-SYNC-GENERATION-001", "Regress final synchronization generation to candidate", ["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"], ["SYNC-01"], lambda o: mutate_json(Path(o["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"]), lambda data: data.__setitem__("synchronizationGeneration", "FINAL_AUTHORITY_CANDIDATE"))),
    definition("CHALLENGE-FROZEN-SYNC-MANIFEST-001", "Regress final synchronization to the candidate manifest", ["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"], ["SYNC-04"], lambda o: mutate_json(Path(o["11 Completion/FINAL_SYNCHRONIZATION_REPORT.json"]), lambda data: data.__setitem__("manifestPath", "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"))),
    definition("CHALLENGE-FROZEN-VALIDATION-MODE-001", "Regress the persisted frozen validation result to full technical mode", [LIVE_REPORT_PATH], ["CERT-01"], lambda o: mutate_json(Path(o[LIVE_REPORT_PATH]), lambda data: (data.__setitem__("validationMode", "FULL_TECHNICAL_CERTIFICATION"), (data.get("validationResult") or {}).setdefault("derived", {}).__setitem__("validationMode", "FULL_TECHNICAL_CERTIFICATION")))),
    definition("CHALLENGE-ARCH-001", "Claim a nonexistent TypeScript literal symbol in a current-authoritative JSON exact-location record", [EXACT_LOCATION_PATH], ["ARCH-01"], lambda o: mutate_json(Path(o[EXACT_LOCATION_PATH]), mutate_missing_current_anchor)),
    definition("CHALLENGE-ARCH-002", "Exclude the architecture contract owner from allowedPaths", [TASK_PATH], ["ARCH-02"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), mutate_owner_not_allowed)),
    definition("CHALLENGE-ARCH-003", "Catch the architecture contract owner with the forbidden catch-all", [TASK_PATH], ["ARCH-02", "ARCH-03"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), mutate_owner_caught_by_catchall)),
    definition("CHALLENGE-ARCH-004", "Omit one source-required Rspack entry from the declared preservation boundary", [TASK_PATH], ["ARCH-04"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), mutate_required_build_entry_omitted)),
    definition("CHALLENGE-ARCH-005", "Treat a generated dist file as an allowed owned canonical source", [TASK_PATH], ["ARCH-05"], lambda o: mutate_jsonl(Path(o[TASK_PATH]), mutate_generated_output_as_canonical)),
    definition("CHALLENGE-ARCH-006", "Make an MR-CAP-001 acceptance test require a nonexistent literal source anchor", [TEST_PATH], ["ARCH-06"], lambda o: mutate_jsonl(Path(o[TEST_PATH]), mutate_acceptance_missing_anchor)),
]


def get_challenge_definitions():
    """Authoritative challenge metadata (no mutators) exported for the dynamic verifier."""
    return [
        {
            "challengeId": row["challengeId"],
            "mutation": row["mutation"],
            "relatives": list(row["relatives"]),
            "expectedFailedCheckIds": list(row["expectedFailedCheckIds"]),
        }
        for row in CHALLENGE_DEFINITIONS
    ]


def verify_existing_report():
    if not REPORT_PATH.exists():
        print("Challenge report missing.", file=sys.stderr)
        raise SystemExit(1)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
    required_ids = [row["challengeId"] for row in CHALLENGE_DEFINITIONS]
    executed = [row.get("challengeId") for row in report.get("challenges", [])]
    failures = []
    if report.get("verdict") != "PASS":
        failures.append("verdict != PASS")
    if executed != required_ids:
        failures.append("challenge IDs do not exactly equal production definitions")
    if any(not row.get("passed") for row in report.get("challenges", [])):
        failures.append("at least one challenge did not pass")
    if any(row.get("baselineStatus") != "PASS" or (row.get("baselineFailedCheckIds") or []) or (row.get("documentedEnvironmentFailures") or []) or (row.get("environmentExemptions") or []) for row in report.get("challenges", [])):
        failures.append("a challenge contains a failed baseline or an exemption")
    if any(row.get("productionValidatorInvoked") is not True for row in report.get("challenges", [])):
        failures.append("a challenge did not invoke the production validator")
    if any(row.get("validationTarget") != "TEMPORARY_CHALLENGE_CANDIDATE" or row.get("overridesUsed") is not True or not row.get("temporaryChallengeId") for row in report.get("challenges", [])):
        failures.append("a challenge is not a properly identified temporary candidate")
    if report.get("baselineFailuresSubtracted") is not False or report.get("challengesUsingBaselineFailureSubtraction") != 0:
        failures.append("baseline-failure subtraction was used")
    if report.get("documentedEnvironmentFailures") or report.get("environmentExemptions"):
        failures.append("environment exemptions remain recorded")
    if report.get("backupUnchangedThroughoutChallenges") is not True or report.get("backupAggregateBeforeChallenges") != report.get("backupAggregateAfterChallenges"):
        failures.append("active backup immutability was not reproduced across challenge execution")
    if report.get("validatorSourceHash") != sha256_file(VALIDATOR_PATH):
        failures.append("validator source hash does not match the live validator")
    if failures:
        print(json.dumps({"verdict": "FAIL", "failures": failures}, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps({"verdict": "PASS", "challengeCount": len(executed)}, indent=2, ensure_ascii=False))


def main():
    arguments = sys.argv[1:]
    if "--verify-existing-report" in arguments:
        verify_existing_report()
        return
    if "--write-live-result" in arguments:
        validator = load_validator()
        status = json.loads((ROOT / "00 Execution Control" / "STATUS.json").read_text(encoding="utf-8-sig"))
        core = validator.do_strict_validation(validation_mode="CORE_PRE_CHALLENGE")
        certification_mode = "FINAL_FREEZE_CERTIFICATION" if status.get("planningFreezeStatus") == "FROZEN" else "FULL_TECHNICAL_CERTIFICATION"
        certification = validator.do_strict_validation(validation_mode=certification_mode)
        validator_hash = sha256_file(VALIDATOR_PATH)
        challenge_hash = sha256_file(Path(__file__).resolve())
        verifier_hash = sha256_file(ROOT / "11 Completion" / "verify_step11b_results.py")
        full_only_meta = set(validator.get_meta_check_ids("FULL_TECHNICAL_CERTIFICATION")) - set(validator.get_meta_check_ids("CORE_PRE_CHALLENGE"))
        validator_check_count = len(core["checks"]) + len(full_only_meta)
        required_challenge_ids = [row["challengeId"] for row in CHALLENGE_DEFINITIONS]
        live = {
            **common_metadata(status),
            "validatorCheckCount": validator_check_count,
            "challengeTestCount": len(required_challenge_ids),
            "timestamp": certification_timestamp(status),
            "validatorSourceHash": validator_hash,
            "challengeSourceHash": challenge_hash,
            "verifierSourceHash": verifier_hash,
            "validationTarget": "LIVE_REPOSITORY",
            "repositoryRelativeGraphifyRoot": "Graphify",
            "candidateRootKind": "REPOSITORY_RELATIVE",
            "overridesUsed": False,
            "temporaryChallengeId": None,
            "validationMode": certification_mode,
            "validationResult": certification,
        }
        write_json(VALIDATION_RESULT_PATH, live)
        print(json.dumps(live, indent=2, ensure_ascii=False))
        raise SystemExit(0 if certification["status"] == "PASS" else 1)
    validator = load_validator()
    status = json.loads((ROOT / "00 Execution Control" / "STATUS.json").read_text(encoding="utf-8-sig"))
    backup_receipt = json.loads((ROOT / "00 Execution Control" / "FINAL_AUTHORITATIVE_FREEZE_BACKUP_VERIFICATION.json").read_text(encoding="utf-8-sig"))
    backup_before_challenges = github_backup_snapshot(validator, backup_receipt)
    global MANIFEST_RELATIVE
    if status.get("planningFreezeStatus") == "FROZEN":
        MANIFEST_RELATIVE = FROZEN_MANIFEST_RELATIVE
    for row in CHALLENGE_DEFINITIONS:
        row["relatives"] = [
            MANIFEST_RELATIVE if rel == "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl" else rel
            for rel in row["relatives"]
        ]
    required_challenge_ids = [row["challengeId"] for row in CHALLENGE_DEFINITIONS]
    core = validator.do_strict_validation(validation_mode="CORE_PRE_CHALLENGE")
    core_failures = sorted(failed_ids(core))
    validator_hash = sha256_file(VALIDATOR_PATH)
    challenge_hash = sha256_file(Path(__file__).resolve())
    verifier_hash = sha256_file(ROOT / "11 Completion" / "verify_step11b_results.py")
    if core_failures:
        report = {
            **common_metadata(status),
            "timestamp": certification_timestamp(status),
            "validatorSourceHash": validator_hash,
            "challengeSourceHash": challenge_hash,
            "verifierSourceHash": verifier_hash,
            "requiredChallenges": required_challenge_ids,
            "challenges": [],
            "verdict": "FAIL",
            "coreBaselineStatus": "FAIL",
            "coreBaselineFailedCheckIds": core_failures,
            "documentedEnvironmentFailures": [],
            "environmentExemptions": [],
            "baselineFailuresSubtracted": False,
        }
        write_json(REPORT_PATH, report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    temp_root = Path(tempfile.mkdtemp(prefix="mindroom-graphify-freeze-challenges-"))
    challenges = []
    try:
        for challenge_definition in CHALLENGE_DEFINITIONS:
            overrides, temporary = copy_overrides(temp_root, challenge_definition["relatives"])
            challenge_definition["mutator"](overrides)
            result = validator.do_strict_validation(
                overrides,
                validation_mode=challenge_definition["validationMode"],
                candidate_root=temp_root,
                temporary_challenge_id=challenge_definition["challengeId"],
            )
            actual = sorted(failed_ids(result))
            expected = sorted(challenge_definition["expectedFailedCheckIds"])
            passed = result["status"] == "FAIL" and set(expected).issubset(actual)
            challenges.append({
                "challengeId": challenge_definition["challengeId"],
                "mutation": challenge_definition["mutation"],
                "temporaryFiles": temporary,
                "productionValidatorFunction": "validate_final_graphify_freeze.do_strict_validation",
                "productionValidatorInvoked": True,
                "expectedFailedCheckIds": expected,
                "actualFailedCheckIds": actual,
                "baselineStatus": "PASS",
                "baselineFailedCheckIds": [],
                "documentedEnvironmentFailures": [],
                "environmentExemptions": [],
                "expectedStatus": "FAIL",
                "actualStatus": result["status"],
                "validationTarget": "TEMPORARY_CHALLENGE_CANDIDATE",
                "overridesUsed": True,
                "temporaryChallengeId": challenge_definition["challengeId"],
                "independentExpectedEvidence": {"source": "immutable challenge specification", "checkIds": expected},
                "passed": passed,
            })
        challenge_count = len(challenges)
        challenge_set_ok = [row["challengeId"] for row in challenges] == required_challenge_ids and all(row["passed"] for row in challenges)
        full_only_meta = set(validator.get_meta_check_ids("FULL_TECHNICAL_CERTIFICATION")) - set(validator.get_meta_check_ids("CORE_PRE_CHALLENGE"))
        validator_check_count = len(core["checks"]) + len(full_only_meta)
        challenge_report = {
            **common_metadata(status),
            "challengeReportState": "FRESH_CHALLENGE_EXECUTION_VERIFIED",
            "validatorCheckCount": validator_check_count,
            "challengeTestCount": challenge_count,
            "timestamp": certification_timestamp(status),
            "validatorSourceHash": validator_hash,
            "challengeSourceHash": challenge_hash,
            "verifierSourceHash": verifier_hash,
            "requiredChallenges": required_challenge_ids,
            "challenges": challenges,
            "gateSpecificChallenges": sum(row["challengeId"].startswith("CHALLENGE-GATE-") for row in challenges),
            "lineageChallengesExecuted": sum(row["challengeId"].startswith("CHALLENGE-LINEAGE-") for row in challenges),
            "lineageChallengesPassed": sum(row["challengeId"].startswith("CHALLENGE-LINEAGE-") and row["passed"] for row in challenges),
            "lineageChallengeFailures": sum(row["challengeId"].startswith("CHALLENGE-LINEAGE-") and not row["passed"] for row in challenges),
            "lineageSemanticChallengesExecuted": sum(row["challengeId"].startswith(("CHALLENGE-LINEAGE-STATUS-", "CHALLENGE-LINEAGE-RECLASSIFIED-", "CHALLENGE-LINEAGE-ALIAS-", "CHALLENGE-LINEAGE-MERGED-", "CHALLENGE-LINEAGE-PROHIBITED-", "CHALLENGE-LINEAGE-EXCLUDED-", "CHALLENGE-CAPABILITY-EVIDENCE-", "CHALLENGE-TASK-EVIDENCE-", "CHALLENGE-LINEAGE-CONFIDENCE-", "CHALLENGE-LINEAGE-REVIEW-", "CHALLENGE-CAP-EVIDENCE-", "CHALLENGE-TASK-EVIDENCE-", "CHALLENGE-ALIAS-", "CHALLENGE-RECLASSIFIED-")) for row in challenges),
            "challengesUsingProductionValidator": sum(row["productionValidatorInvoked"] is True for row in challenges),
            "challengesWithIndependentExpectedEvidence": len(challenges),
            "challengesWithZeroFailureBaseline": sum(row.get("baselineStatus") == "PASS" and not (row.get("baselineFailedCheckIds") or []) and not (row.get("documentedEnvironmentFailures") or []) and not (row.get("environmentExemptions") or []) for row in challenges),
            "challengesUsingBaselineFailureSubtraction": 0,
            "baselineFailuresSubtracted": False,
            "coreBaselineStatus": "PASS" if not core_failures else "FAIL",
            "coreBaselineFailedCheckIds": core_failures,
            "documentedEnvironmentFailures": [],
            "environmentExemptions": [],
            "verdict": "PASS" if challenge_set_ok else "FAIL",
        }
        if not challenge_set_ok:
            write_json(REPORT_PATH, challenge_report)
            print(json.dumps(challenge_report, indent=2, ensure_ascii=False))
            raise SystemExit(1)
        # Certify the coherent fail-closed pending report pair first. Publishing
        # only one side of the final pair would correctly fail META-18.
        full = validator.do_strict_validation(validation_mode="FULL_TECHNICAL_CERTIFICATION")
        full_failures = sorted(failed_ids(full))
        final_freeze = validator.do_strict_validation(validation_mode="FINAL_FREEZE_CERTIFICATION") if status.get("planningFreezeStatus") == "FROZEN" else full
        final_freeze_failures = sorted(failed_ids(final_freeze))
        validator._GITHUB_BACKUP_CACHE.clear()
        backup_after_challenges = github_backup_snapshot(validator, backup_receipt)
        backup_unchanged = backup_before_challenges == backup_after_challenges
        if not backup_unchanged:
            full_failures.append("BACKUP-MUTATION-DURING-CHALLENGES")
            final_freeze_failures.append("BACKUP-MUTATION-DURING-CHALLENGES")
        certification_failures = sorted(set(full_failures + final_freeze_failures))
        challenge_report.update({
            "fullCertificationStatus": "PASS" if not full_failures else "FAIL",
            "fullCertificationFailedCheckIds": full_failures,
            "fullCertificationEnvironmentFailures": [],
            "finalFreezeCertificationStatus": "PASS" if not final_freeze_failures else "FAIL",
            "finalFreezeCertificationFailedCheckIds": final_freeze_failures,
            "finalFreezeCertificationEnvironmentFailures": [],
            "backupUnchangedThroughoutChallenges": backup_unchanged,
            "backupAggregateBeforeChallenges": backup_before_challenges.get("aggregateSha256"),
            "backupAggregateAfterChallenges": backup_after_challenges.get("aggregateSha256"),
            "verdict": "PASS" if not certification_failures else "FAIL",
            "timestamp": certification_timestamp(status),
        })
        write_json(REPORT_PATH, challenge_report)
        final_live = {
            **common_metadata(status),
            "validatorCheckCount": validator_check_count,
            "challengeTestCount": challenge_count,
            "timestamp": certification_timestamp(status),
            "validatorSourceHash": validator_hash,
            "challengeSourceHash": challenge_hash,
            "verifierSourceHash": verifier_hash,
            "validationTarget": "LIVE_REPOSITORY",
            "repositoryRelativeGraphifyRoot": "Graphify",
            "candidateRootKind": "REPOSITORY_RELATIVE",
            "overridesUsed": False,
            "temporaryChallengeId": None,
            "validationMode": "FINAL_FREEZE_CERTIFICATION" if status.get("planningFreezeStatus") == "FROZEN" else "FULL_TECHNICAL_CERTIFICATION",
            "validationResult": final_freeze,
        }
        write_json(VALIDATION_RESULT_PATH, final_live)
        if not certification_failures:
            # Revalidate the exact coherent PASS pair that will remain on disk,
            # then persist that post-publication result as the live authority.
            full = validator.do_strict_validation(validation_mode="FULL_TECHNICAL_CERTIFICATION")
            final_freeze = validator.do_strict_validation(validation_mode="FINAL_FREEZE_CERTIFICATION") if status.get("planningFreezeStatus") == "FROZEN" else full
            full_failures = sorted(failed_ids(full))
            final_freeze_failures = sorted(failed_ids(final_freeze))
            certification_failures = sorted(set(full_failures + final_freeze_failures))
            challenge_report.update({
                "fullCertificationStatus": "PASS" if not full_failures else "FAIL",
                "fullCertificationFailedCheckIds": full_failures,
                "finalFreezeCertificationStatus": "PASS" if not final_freeze_failures else "FAIL",
                "finalFreezeCertificationFailedCheckIds": final_freeze_failures,
                "postPublicationCertificationRevalidated": not certification_failures,
                "verdict": "PASS" if not certification_failures else "FAIL",
            })
            write_json(REPORT_PATH, challenge_report)
            final_live["validationResult"] = final_freeze
            write_json(VALIDATION_RESULT_PATH, final_live)
        print(json.dumps(challenge_report, indent=2, ensure_ascii=False))
        raise SystemExit(0 if not certification_failures else 1)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
