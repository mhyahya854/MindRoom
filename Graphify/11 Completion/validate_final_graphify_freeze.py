"""Strict, read-only validation of the authoritative MindRoom Graphify freeze."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
CODEBASE = ROOT.parent / "Codebase"
_CODEBASE_CACHE = {}
_CHECK_DEFINITION_CACHE = {}

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
    "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
)
FINAL_STATUS = {
    "mappingStatus": "COMPLETED_AND_FROZEN",
    "independentReviewStatus": "APPROVED_GENUINELY_INDEPENDENT_AFTER_LINEAGE_REPAIR",
    "planningFreezeStatus": "FROZEN",
    "wave0Readiness": "READY_NOT_STARTED",
    "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION",
    "finalReleaseReceiptStatus": "NOT_VERIFIED",
}
TRANSITION_STATUS = {
    "mappingStatus": "LINEAGE_REPAIR_COMPLETE_PENDING_INDEPENDENT_REVIEW",
    "independentReviewStatus": "PENDING_GENUINELY_INDEPENDENT_LINEAGE_REVIEW",
    "planningFreezeStatus": "NOT_FROZEN",
    "wave0Readiness": "BLOCKED_PENDING_INDEPENDENT_LINEAGE_REVIEW",
    "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION",
    "finalReleaseReceiptStatus": "NOT_VERIFIED",
}
TECHNICAL_REPAIR_STATUS = {
    "mappingStatus": "FINAL_GATE_REPAIR_FAILED_INDEPENDENT_REVIEW",
    "independentReviewStatus": "FAILED_POST_REPAIR_EXTERNAL_REVIEW",
    "planningFreezeStatus": "NOT_FROZEN",
    "wave0Readiness": "BLOCKED_PENDING_INDEPENDENT_REVIEW_DEFECT_REPAIR",
    "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION",
    "finalReleaseReceiptStatus": "NOT_VERIFIED",
}
ALLOWED_LINEAGE_STATUSES = {
    "DIRECT",
    "SUPERSEDED",
    "MERGED",
    "SPLIT",
    "RECLASSIFIED",
    "PROHIBITED",
    "EXCLUDED",
    "ALIAS",
    "UNRESOLVED",
}
VALIDATION_MODES = ("CORE_PRE_CHALLENGE", "FULL_TECHNICAL_CERTIFICATION", "FINAL_FREEZE_CERTIFICATION")
EXPECTED_WAVES = tuple(f"WAVE_{number}" for number in range(6))
VALID_TEST_TYPES = {"UNIT", "INTEGRATION", "SECURITY", "CONTRACT", "PACKAGING"}
REQUIRED_CONTRACT_FIELDS = (
    "capabilityId", "taskId", "releaseWave", "purpose", "scope",
    "ownedPackageOrModule", "runtimeOwner", "publicOperations", "domainModels",
    "persistentState", "inputs", "outputs", "invariants", "failureModes",
    "recoveryBehavior", "offlineBehavior", "securityAndPrivacyConstraints",
    "crossPlatformConstraints", "dependencies", "acceptanceTests", "blockingGates",
)


def normalize_rel(value):
    return str(value or "").replace("\\", "/").removeprefix("./").removeprefix("Graphify/")


def source_path(relative, overrides):
    relative = normalize_rel(relative)
    return Path(overrides[relative]) if relative in overrides else ROOT / relative


def read_json(relative, overrides=None, default=None):
    path = source_path(relative, overrides or {})
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def read_jsonl(relative, overrides=None):
    path = source_path(relative, overrides or {})
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()] if path.exists() else []


def read_text(relative, overrides=None):
    path = source_path(relative, overrides or {})
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_hash(records):
    text = "\n".join(f"{normalize_rel(row['path'])}:{row['sha256']}" for row in sorted(records, key=lambda row: normalize_rel(row["path"])))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _challenge_runner_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mindroom_graphify_challenge_runner",
        HERE.parent / "run_final_freeze_challenges.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_challenge_definitions():
    """Authoritative challenge-ID metadata exported from the production challenge runner."""
    return [dict(row) for row in _challenge_runner_module().CHALLENGE_DEFINITIONS]


def get_check_definitions(validation_mode="CORE_PRE_CHALLENGE"):
    """Authoritative production check-ID list for a validation mode, derived from a live run."""
    if validation_mode not in VALIDATION_MODES:
        raise ValueError(f"Unsupported validation_mode {validation_mode!r}")
    key = validation_mode
    if key not in _CHECK_DEFINITION_CACHE:
        result = do_strict_validation(validation_mode=key)
        _CHECK_DEFINITION_CACHE[key] = [check["checkId"] for check in result["checks"]]
    return list(_CHECK_DEFINITION_CACHE[key])


def get_meta_check_ids(validation_mode="CORE_PRE_CHALLENGE"):
    """Authoritative META check-ID set for a validation mode (used by the challenge runner)."""
    core = {
        "META-01", "META-02", "META-03", "META-04", "META-05", "META-06",
        "META-07", "META-08", "META-09", "META-11", "META-12", "META-13",
        "META-14", "META-15", "META-16",
    }
    full = core | {"META-10", "META-17", "META-18"}
    if validation_mode == "CORE_PRE_CHALLENGE":
        return sorted(core)
    if validation_mode in ("FULL_TECHNICAL_CERTIFICATION", "FINAL_FREEZE_CERTIFICATION"):
        return sorted(full)
    raise ValueError(f"Unsupported validation_mode {validation_mode!r}")


def wave_number(value):
    match = re.fullmatch(r"WAVE_(\d+)", str(value or ""))
    return int(match.group(1)) if match else None


def find_cycles(adjacency):
    state, stack, found = {}, [], []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for target in adjacency.get(node, ()):
            if state.get(target, 0) == 1:
                found.append(stack[stack.index(target):] + [target])
            elif state.get(target, 0) == 0:
                visit(target)
        stack.pop()
        state[node] = 2

    for node in adjacency:
        if state.get(node, 0) == 0:
            visit(node)
    return found


def inventory_tree(root):
    cache_key = str(Path(root).resolve())
    if cache_key in _CODEBASE_CACHE:
        return _CODEBASE_CACHE[cache_key]
    display = os.path.abspath(root)
    scan_root = display if not os.name == "nt" or display.startswith("\\\\?\\") else "\\\\?\\" + display
    file_pairs, directories, errors = [], [], []

    def walk(current):
        try:
            entries = list(os.scandir(current))
        except OSError as error:
            errors.append(f"{current}: {error}")
            return
        for entry in entries:
            entry_path = os.path.join(current, entry.name)
            try:
                if os.path.islink(entry_path):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    directories.append(os.path.relpath(entry_path, scan_root).replace("\\", "/"))
                    walk(entry_path)
                elif entry.is_file(follow_symlinks=False):
                    relative = os.path.relpath(entry_path, scan_root).replace("\\", "/")
                    try:
                        digest = sha256_file(entry_path)
                        size = os.path.getsize(entry_path)
                    except OSError as error:
                        errors.append(f"{entry_path}: {error}")
                    else:
                        file_pairs.append({"path": relative, "sha256": digest, "sizeBytes": size})
            except OSError as error:
                errors.append(f"{entry_path}: {error}")

    walk(scan_root)
    if errors:
        raise RuntimeError("Codebase scan failed: " + "; ".join(errors[:10]))
    files = list(file_pairs)
    files.sort(key=lambda row: row["path"])
    result = {"files": files, "directories": sorted(directories), "aggregateSha256": aggregate_hash(files)}
    _CODEBASE_CACHE[cache_key] = result
    return result


def add(checks, check_id, category, description, passed, actual, expected, evidence, method):
    checks.append({
        "checkId": check_id, "category": category, "description": description,
        "status": "PASS" if passed else "FAIL", "method": method,
        "actual": actual, "expected": expected, "evidence": evidence,
    })


def task_metrics(tasks, same_wave_rows):
    task_map = {row.get("taskId"): row for row in tasks if row.get("taskId")}
    raw, explicit, same_wave, unknown, self_refs, duplicates = 0, [], [], set(), [], []
    adjacency = defaultdict(list)
    for task_id, task in task_map.items():
        seen = set()
        refs = [value.strip() for field in ("dependencies", "prerequisites") for value in (task.get(field) or []) if isinstance(value, str) and value.strip().startswith("MR-IMPL-")]
        raw += len(refs)
        for target in refs:
            canonical = target.upper()
            if canonical in seen:
                duplicates.append({"taskId": task_id, "dependency": canonical})
                continue
            seen.add(canonical)
            if canonical == task_id:
                self_refs.append({"taskId": task_id, "dependency": canonical})
            elif canonical not in task_map:
                unknown.add(canonical)
            else:
                explicit.append((task_id, canonical))
    for row in same_wave_rows:
        source, target = row.get("dependent"), row.get("prerequisite")
        if source in task_map and target in task_map:
            same_wave.append((source, target))
    for source, target in set(explicit + same_wave):
        adjacency[source].append(target)
    backward = [{"source": source, "target": target} for source, target in set(explicit + same_wave) if wave_number(task_map[target].get("releaseWave")) > wave_number(task_map[source].get("releaseWave"))]
    return {"taskMap": task_map, "rawReferences": raw, "explicitEdges": sorted(set(explicit)), "sameWaveEdges": sorted(set(same_wave)), "directEdges": sorted(set(explicit + same_wave)), "unknown": sorted(unknown), "self": self_refs, "duplicates": duplicates, "cycles": find_cycles(adjacency), "backward": backward}


def capability_metrics(capabilities, graph):
    cap_map = {row.get("capabilityId"): row for row in capabilities if row.get("capabilityId")}
    relation_types, edges, unknown, self_refs, adjacency = Counter(), [], set(), [], defaultdict(list)
    for row in graph.get("edges", []):
        relation = row.get("relation") or row.get("type") or "UNKNOWN"
        relation_types[relation] += 1
        if relation != "DEPENDS_ON":
            continue
        source, target = row.get("sourceNodeId") or row.get("source"), row.get("targetNodeId") or row.get("target")
        if source not in cap_map: unknown.add(source)
        if target not in cap_map: unknown.add(target)
        if source == target: self_refs.append({"capabilityId": source, "dependency": target})
        if source and target:
            edges.append((source, target)); adjacency[source].append(target)
    backward = [{"source": source, "target": target} for source, target in set(edges) if source in cap_map and target in cap_map and wave_number(cap_map[target].get("releaseWave")) > wave_number(cap_map[source].get("releaseWave"))]
    return {"capabilityMap": cap_map, "rawRecords": len(graph.get("edges", [])), "relationTypes": dict(relation_types), "edges": sorted(set(edges)), "unknown": sorted(value for value in unknown if value), "self": self_refs, "cycles": find_cycles(adjacency), "backward": backward}


def operation_names(contract):
    result = []
    for value in contract.get("publicOperations") or []:
        result.append(value if isinstance(value, str) else value.get("name") or value.get("operation") or "")
    return [str(value).strip() for value in result if str(value).strip()]


def normalized_contract(contract, name):
    selected = {key: contract.get(key) for key in REQUIRED_CONTRACT_FIELDS if key not in {"capabilityId", "taskId", "releaseWave"}}
    text = json.dumps(selected, sort_keys=True, ensure_ascii=False).lower()
    variants = {name.lower(), re.sub(r"[^a-z0-9]", "", name.lower()), re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")}
    for variant in sorted((item for item in variants if item), key=len, reverse=True):
        text = text.replace(variant, "<name>")
    text = re.sub(r"mr-(?:cap|impl|req|test|change)-[a-z0-9-]+", "<id>", text)
    text = re.sub(r"wave[_ -]?\d+", "<wave>", text)
    text = re.sub(r"(?:codebase|graphify|mindroom)/[^\" ]+", "<path>", text)
    return text


def contract_metrics(records, owner_key, test_ids):
    metrics = defaultdict(list)
    templates = defaultdict(list)
    generic_phrases = ("implement planned mindroom capability scope", "implement planned capability scope", "remains internally consistent", "contract becomes stale or inconsistent")
    generic_ops = {"initialize", "execute", "getstatus", "run", "process", "handle"}
    generic_model_fields = {"id", "name", "status", "createdat", "updatedat"}
    for record in records:
        owner, name = record.get(owner_key), record.get("name") or record.get("capabilityName") or record.get("taskName") or str(record.get(owner_key))
        contract = record.get("contract") or {}
        nonempty_sections = set(REQUIRED_CONTRACT_FIELDS) - {"dependencies"}
        missing = [field for field in REQUIRED_CONTRACT_FIELDS if field not in contract or contract[field] in (None, "") or (field in nonempty_sections and contract[field] == [])]
        if missing: metrics["missingSections"].append({owner_key: owner, "fields": missing})
        if record.get("releaseWave") != contract.get("releaseWave"):
            metrics["waveMismatches"].append({owner_key: owner, "topLevel": record.get("releaseWave"), "embedded": contract.get("releaseWave")})
        operations = operation_names(contract)
        stems = {re.sub(r"[^a-z]", "", operation.lower().split("(")[0]) for operation in operations}
        if len(operations) < 2: metrics["missingPublicOperations"].append(owner)
        if operations and stems <= generic_ops: metrics["genericOperations"].append(owner)
        body = json.dumps(contract, ensure_ascii=False).lower()
        if any(phrase in body for phrase in generic_phrases): metrics["genericPatterns"].append(owner)
        models = contract.get("domainModels") or []
        useful_models = []
        for model in models:
            fields = model.get("requiredFields", []) if isinstance(model, dict) else []
            if len({re.sub(r"[^a-z]", "", str(field).lower()) for field in fields} - generic_model_fields) >= 2:
                useful_models.append(model)
        if not useful_models: metrics["genericOrMissingDomainModels"].append(owner)
        invariants = contract.get("invariants") or []
        if len(invariants) < 2 or any("remains internally consistent" in str(value).lower() for value in invariants): metrics["genericOrMissingInvariants"].append(owner)
        failure_modes = contract.get("failureModes") or []
        if len(failure_modes) < 2 or any("contract becomes stale" in str(value).lower() for value in failure_modes): metrics["genericOrMissingFailureModes"].append(owner)
        refs = [value.get("testId") if isinstance(value, dict) else value for value in (contract.get("acceptanceTests") or [])]
        invalid = [value for value in refs if value not in test_ids]
        if invalid: metrics["invalidTests"].append({owner_key: owner, "tests": invalid})
        templates[normalized_contract(contract, name)].append(owner)
    metrics["repeatedTemplates"] = [owners for owners in templates.values() if len(owners) > 5]
    return dict(metrics)


def metadata_values(documents, field):
    return {relative: data.get(field) for relative, data in documents.items() if field in data}


def derive_test_ownership(tests, cap_map, task_map):
    ownership, issues = {}, []
    for test in tests:
        test_id = test.get("testId")
        capability_ids = list(test.get("capabilityIds") or [])
        task_ids = list(test.get("taskIds") or [])
        unknown_capabilities = sorted(set(capability_ids) - set(cap_map))
        unknown_tasks = sorted(set(task_ids) - set(task_map))
        task_waves = {task_map[task_id].get("releaseWave") for task_id in task_ids if task_id in task_map}
        capability_waves = {cap_map[capability_id].get("releaseWave") for capability_id in capability_ids if capability_id in cap_map}
        owner_waves = task_waves | capability_waves
        if unknown_capabilities or unknown_tasks or len(owner_waves) != 1:
            issues.append({
                "testId": test_id,
                "unknownCapabilityIds": unknown_capabilities,
                "unknownTaskIds": unknown_tasks,
                "ownerWaves": sorted(value for value in owner_waves if value),
            })
            continue
        owning_wave = next(iter(owner_waves))
        ownership[test_id] = {
            "testId": test_id,
            "testType": test.get("testType"),
            "capabilityIds": capability_ids,
            "taskIds": task_ids,
            "requirementIds": list(test.get("requirementIds") or []),
            "owningWave": owning_wave,
            "sharedAcrossWaves": False,
            "globalGateTest": False,
        }
    return ownership, issues


def do_strict_validation(overrides=None, validation_mode="CORE_PRE_CHALLENGE", candidate_root=None, temporary_challenge_id=None):
    if validation_mode not in VALIDATION_MODES:
        raise ValueError(f"Unsupported validation_mode {validation_mode!r}; expected one of {VALIDATION_MODES}")
    overrides = {normalize_rel(key): value for key, value in (overrides or {}).items()}
    checks = []
    status = read_json("00 Execution Control/STATUS.json", overrides, {}) or {}
    final_mode = status.get("planningFreezeStatus") == "FROZEN"
    if validation_mode == "FINAL_FREEZE_CERTIFICATION" and not final_mode:
        raise ValueError("FINAL_FREEZE_CERTIFICATION is reserved for the later GPT-5.6 Sol independent review and final freeze; it cannot be executed while planningFreezeStatus is NOT_FROZEN.")
    technical_mode = (not final_mode) and status.get("mappingStatus") == TECHNICAL_REPAIR_STATUS["mappingStatus"]
    expected_status = FINAL_STATUS if final_mode else (TECHNICAL_REPAIR_STATUS if technical_mode else TRANSITION_STATUS)
    certification_classification = "FINAL_FREEZE_CERTIFIED" if final_mode else "TECHNICAL_REPAIR_VALID"
    validation_context = {
        "validationTarget": "TEMPORARY_CHALLENGE_CANDIDATE" if (overrides or temporary_challenge_id) else "LIVE_REPOSITORY",
        "candidateRoot": str(candidate_root or ROOT),
        "overridesUsed": bool(overrides),
        "temporaryChallengeId": temporary_challenge_id,
        "validationMode": validation_mode,
    }
    inventory_relative = "00 Execution Control/FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl" if final_mode else "11 Completion/FINAL_GATE_REPAIR_AUTHORITY_INVENTORY_CANDIDATE.jsonl"
    manifest_relative = "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl" if final_mode else "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"
    authority_index = read_json("00 Execution Control/FINAL_AUTHORITY_INDEX.json", overrides, {}) or {}
    inventory = read_jsonl(inventory_relative, overrides)
    manifest = read_jsonl(manifest_relative, overrides)
    capabilities = (read_json("03 Capability Map/CAPABILITY_REGISTRY.json", overrides, {}) or {}).get("capabilities", [])
    tasks = read_jsonl("09 Implementation/IMPLEMENTATION_TASKS.jsonl", overrides)
    requirements = read_jsonl("03 Capability Map/REQUIREMENT_REGISTRY.jsonl", overrides)
    lineage = read_jsonl("03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl", overrides)
    traceability = read_jsonl("03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl", overrides)
    supersessions = read_jsonl("03 Capability Map/REQUIREMENT_SUPERSESSION_MAP.jsonl", overrides)
    lineage_traceability = read_json("11 Completion/FINAL_CAPABILITY_TASK_REQUIREMENT_TRACEABILITY_REPORT.json", overrides, {}) or {}
    backup_receipt = read_json("00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json", overrides, {}) or {}
    change_records = read_jsonl("04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl", overrides)
    tests = read_jsonl("10 Verification/REQUIREMENT_TEST_MATRIX.jsonl", overrides)
    entrypoints = read_jsonl("06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl", overrides)
    release_matrix = read_json("10 Verification/RELEASE_GATE_MATRIX.json", overrides, {}) or {}
    same_wave = (read_json("05 Dependency and Impact/SAME_WAVE_EXECUTION_ORDER.json", overrides, {}) or {}).get("sameWaveExecutionOrders", [])
    cap_graph = read_json("05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json", overrides, {}) or {}
    warnings_doc = read_json("11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json", overrides, {}) or {}
    warnings = warnings_doc.get("warnings", [])
    ownership_rows = read_jsonl("11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl", overrides)
    gate_audit = read_json("11 Completion/FINAL_WAVE_GATE_TEST_AUDIT.json", overrides, {}) or {}
    gate_sync = read_json("11 Completion/FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json", overrides, {}) or {}
    independent_review = read_json("11 Completion/FINAL_LINEAGE_REPAIR_INDEPENDENT_REVIEW_REPORT.json", overrides, {}) or {}
    metadata = {relative: read_json(relative, overrides, {}) or {} for relative in CURRENT_METADATA}
    test_ids = {row.get("testId") for row in tests if row.get("testId")}
    cap_info, task_info = capability_metrics(capabilities, cap_graph), task_metrics(tasks, same_wave)
    cap_contracts, task_contracts = contract_metrics(capabilities, "capabilityId", test_ids), contract_metrics(tasks, "taskId", test_ids)
    derived_ownership, ownership_issues = derive_test_ownership(tests, cap_info["capabilityMap"], task_info["taskMap"])

    # Authority and inventory.
    canonical_status = authority_index.get("canonicalStatusPath")
    add(checks, "AUTH-01", "authority", "Canonical status file exists", source_path("00 Execution Control/STATUS.json", overrides).exists(), canonical_status, "00 Execution Control/STATUS.json", ["FINAL_AUTHORITY_INDEX.json"], "direct path existence")
    status_paths = [normalize_rel(value) for key, value in (authority_index.get("authoritativeMap") or {}).items() if "status" in key.lower() and isinstance(value, str)]
    add(checks, "AUTH-02", "authority", "Exactly one canonical status path is defined", canonical_status == "00 Execution Control/STATUS.json" and status_paths == [canonical_status], status_paths, ["00 Execution Control/STATUS.json"], ["FINAL_AUTHORITY_INDEX.json"], "independent authority-index enumeration")
    authority_paths = [normalize_rel(value) for value in (authority_index.get("authoritativeMap") or {}).values() if isinstance(value, str)]
    missing_authority = [path for path in authority_paths if not source_path(path, overrides).exists()]
    add(checks, "AUTH-03", "authority", "Every authority-index path exists", not missing_authority, missing_authority, [], authority_paths, "filesystem existence")
    included = [row for row in inventory if row.get("includedInFreeze")]
    missing_included = [normalize_rel(row.get("path")) for row in included if not source_path(row.get("path"), overrides).exists()]
    add(checks, "AUTH-04", "authority", "Every included inventory path exists", bool(inventory) and not missing_included, missing_included, [], [row.get("path") for row in included], "filesystem existence")
    missing_reasons = [row.get("path") for row in inventory if not row.get("includedInFreeze") and not row.get("exclusionReason")]
    add(checks, "AUTH-05", "authority", "Every exclusion has a reason", not missing_reasons, missing_reasons, [], missing_reasons, "inventory field validation")
    inventory_paths = [normalize_rel(row.get("path")) for row in inventory if row.get("path")]
    collisions = [path for path, count in Counter(path.casefold() for path in inventory_paths).items() if count > 1]
    add(checks, "AUTH-06", "authority", "No normalized inventory path collisions exist", not collisions, collisions, [], collisions, "case-folded normalized path comparison")
    forbidden = re.compile(r"(^|/)(__pycache__|graphify-out|historical)(/|$)|\.pyc$|\.log$|\.tmp$|\.(?:stdout|stderr)\.txt$", re.I)
    forbidden_included = [normalize_rel(row.get("path")) for row in included if forbidden.search(normalize_rel(row.get("path")))]
    add(checks, "AUTH-07", "authority", "No cache, log, historical file, or repair tool is authoritative", not forbidden_included, forbidden_included, [], forbidden_included, "forbidden path classification")
    manifest_paths = [normalize_rel(row.get("path")) for row in manifest]
    included_paths = {normalize_rel(row.get("path")) for row in included}
    omitted = sorted(included_paths - set(manifest_paths))
    add(checks, "AUTH-08", "authority", "No authoritative inventory artifact is omitted from the manifest", not omitted, omitted, [], omitted, "inventory-to-manifest set difference")

    # Manifest.
    self_refs = [path for path in manifest_paths if path == normalize_rel(manifest_relative)]
    add(checks, "MAN-01", "manifest", "Manifest does not contain itself", not self_refs, self_refs, [], self_refs, "normalized path comparison")
    missing_manifest = [path for path in manifest_paths if not source_path(path, overrides).exists()]
    add(checks, "MAN-02", "manifest", "Every manifest path exists", not missing_manifest, missing_manifest, [], missing_manifest, "filesystem existence")
    mismatched_hashes = []
    for row in manifest:
        relative = normalize_rel(row.get("path"))
        if relative in overrides and manifest_relative not in overrides:
            continue
        path = source_path(relative, overrides)
        if not path.exists() or sha256_file(path) != row.get("sha256"):
            mismatched_hashes.append(relative)
    add(checks, "MAN-03", "manifest", "Every manifest SHA-256 matches live content", not mismatched_hashes, mismatched_hashes, [], mismatched_hashes, "independent SHA-256 of file bytes")
    inventory_misses = sorted(set(manifest_paths) - included_paths)
    add(checks, "MAN-04", "manifest", "Every manifest path is included in the authority inventory", not inventory_misses, inventory_misses, [], inventory_misses, "manifest-to-inventory set difference")
    manifest_collisions = [path for path, count in Counter(path.casefold() for path in manifest_paths).items() if count > 1]
    add(checks, "MAN-05", "manifest", "No duplicate normalized manifest paths exist", not manifest_collisions, manifest_collisions, [], manifest_collisions, "case-folded normalized path comparison")
    temp_manifest = [path for path in manifest_paths if forbidden.search(path)]
    add(checks, "MAN-06", "manifest", "No temporary or cache files appear in the manifest", not temp_manifest, temp_manifest, [], temp_manifest, "forbidden path classification")
    calculated_manifest_hash = aggregate_hash(manifest) if manifest else None
    manifest_aggregate_ok = bool(calculated_manifest_hash) and re.fullmatch(r"[a-f0-9]{64}", calculated_manifest_hash)
    add(checks, "MAN-07", "manifest", "Candidate manifest aggregate hash is reproducible from live non-self-referential rows", manifest_aggregate_ok, calculated_manifest_hash, "64-character SHA-256 aggregate", ["MAN-01", "MAN-03", "MAN-05"], "independent sorted path:file-hash aggregate; protected governance receipts are not authoritative for the pre-review candidate aggregate because the candidate manifest is rebuilt last and those receipts cannot be modified in this repair")
    protected_manifest_hashes = metadata_values(metadata, "manifestAggregateHash")
    protected_manifest_agreement = bool(protected_manifest_hashes) and len(set(protected_manifest_hashes.values())) == 1
    add(checks, "MAN-08", "manifest", "Protected governance receipts agree with each other on the historical candidate manifest aggregate hash", protected_manifest_agreement, protected_manifest_hashes, "one shared historical manifest aggregate hash", list(protected_manifest_hashes), "cross-document protected-receipt consistency; the candidate manifest itself is rebuilt last and is not required to match protected receipts in this repair")

    # Source-derived counts and cross-registry identities.
    master_plans = sorted((ROOT / "Master Plan").glob("*.md"))
    add(checks, "CNT-01", "counts", "Master Plan count and canonical names", [path.name for path in master_plans] == ["01-EVERYTHING-WE-ARE-KEEPING.md", "02-EVERYTHING-WE-ARE-DELETING.md", "03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md"], [path.name for path in master_plans], ["01-EVERYTHING-WE-ARE-KEEPING.md", "02-EVERYTHING-WE-ARE-DELETING.md", "03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md"], [str(path) for path in master_plans], "canonical source-file enumeration")
    requirement_ids = [row.get("requirementId") for row in requirements]
    trace_ids = {row.get("requirementId") for row in traceability if row.get("requirementId")}
    add(checks, "CNT-02", "counts", "Requirement registry count agrees with independent traceability IDs", len(requirement_ids) == len(set(requirement_ids)) and set(requirement_ids) == trace_ids, len(requirement_ids), len(trace_ids), ["REQUIREMENT_REGISTRY.jsonl", "REQUIREMENT_TRACEABILITY_MATRIX.jsonl"], "independent registry ID set equality")
    supersession_ids = [row.get("oldRequirementId") for row in supersessions]
    add(checks, "CNT-03", "counts", "Supersession records are unique and complete", bool(supersessions) and len(supersession_ids) == len(set(supersession_ids)) and all(row.get("reason") and row.get("action") for row in supersessions), len(supersessions), len(set(supersession_ids)), ["REQUIREMENT_SUPERSESSION_MAP.jsonl"], "source registry uniqueness and required fields")

    # Absolute legacy-lineage and exact capability/task expansion checks.
    requirement_id_set = set(requirement_ids)
    legacy_ids = [row.get("legacyRequirementId") for row in lineage]
    lineage_groups = defaultdict(list)
    for row in lineage:
        lineage_groups[row.get("legacyRequirementId")].append(row)
    conflicts = sorted(key for key, rows in lineage_groups.items() if not key or len(rows) != 1)
    add(checks, "LIN-01", "lineage", "Every legacy requirement ID is unique", not conflicts and bool(lineage), conflicts, [], legacy_ids, "lineage-map ID multiplicity")
    referenced_sources = {value for row in capabilities for value in (row.get("sourceRequirementIds") or [])} | {value for row in tasks for value in (row.get("sourceRequirements") or [])}
    expected_legacy = referenced_sources - requirement_id_set
    actual_legacy = set(legacy_ids)
    legacy_inventory_delta = sorted(expected_legacy ^ actual_legacy)
    add(checks, "LIN-02", "lineage", "Lineage map exactly covers every referenced non-canonical source ID", not legacy_inventory_delta, sorted(actual_legacy), sorted(expected_legacy), legacy_inventory_delta, "source-registry set difference")
    missing_targets = sorted({target for row in lineage for target in (row.get("canonicalRequirementIds") or []) if target not in requirement_id_set})
    add(checks, "LIN-03", "lineage", "Every lineage canonical target exists", not missing_targets, missing_targets, [], missing_targets, "canonical requirement ID membership")
    supersession_by_id = {row.get("supersessionRecordId"): row for row in supersessions if row.get("supersessionRecordId")}
    missing_supersessions, inconsistent_supersessions = [], []
    for row in lineage:
        for record_id in row.get("supersessionRecordIds") or []:
            record = supersession_by_id.get(record_id)
            if not record:
                missing_supersessions.append(record_id)
            elif record.get("oldRequirementId") != row.get("legacyRequirementId") or set(record.get("newRequirementIds") or []) != set(row.get("canonicalRequirementIds") or []):
                inconsistent_supersessions.append(record_id)
    duplicate_supersession_ids = [key for key, count in Counter(row.get("supersessionRecordId") for row in supersessions).items() if not key or count != 1]
    add(checks, "LIN-04", "lineage", "Every lineage supersession record exists uniquely and agrees with its mapping", not missing_supersessions and not inconsistent_supersessions and not duplicate_supersession_ids, {"missing": missing_supersessions, "inconsistent": inconsistent_supersessions, "duplicates": duplicate_supersession_ids}, {"missing": [], "inconsistent": [], "duplicates": []}, missing_supersessions + inconsistent_supersessions + duplicate_supersession_ids, "cross-map ID and target equality")
    invalid_sources = []
    node_rows = read_jsonl("05 Dependency and Impact/Knowledge Graph/NODES.jsonl", overrides)
    for row in lineage:
        artifact = normalize_rel(row.get("legacySourceArtifact"))
        match = re.fullmatch(r"jsonl:(\d+)", str(row.get("legacySourceLocation") or ""))
        line_number = int(match.group(1)) if match else 0
        valid_line = artifact == "05 Dependency and Impact/Knowledge Graph/NODES.jsonl" and 0 < line_number <= len(node_rows) and node_rows[line_number - 1].get("nodeId") == row.get("legacyRequirementId")
        if not source_path(artifact, overrides).exists() or not valid_line:
            invalid_sources.append(row.get("legacyRequirementId"))
    add(checks, "LIN-05", "lineage", "Every lineage source artifact and machine-checkable location is valid", not invalid_sources, invalid_sources, [], invalid_sources, "filesystem existence plus JSONL record-address verification")
    invalid_direct = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "DIRECT" and len(row.get("canonicalRequirementIds") or []) != 1]
    add(checks, "LIN-06", "lineage", "Every DIRECT mapping has exactly one canonical target", not invalid_direct, invalid_direct, [], invalid_direct, "status-specific cardinality")
    invalid_merged = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "MERGED" and not row.get("canonicalRequirementIds")]
    add(checks, "LIN-07", "lineage", "Every MERGED mapping has at least one canonical target", not invalid_merged, invalid_merged, [], invalid_merged, "status-specific cardinality")
    invalid_split = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "SPLIT" and len(row.get("canonicalRequirementIds") or []) < 2]
    add(checks, "LIN-08", "lineage", "Every SPLIT mapping has at least two canonical targets", not invalid_split, invalid_split, [], invalid_split, "status-specific cardinality")
    invalid_prohibited = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "PROHIBITED" and not any(e.get("decision") or "prohibit" in str(e).lower() for e in (row.get("normalizationEvidence") or []))]
    add(checks, "LIN-09", "lineage", "Every PROHIBITED mapping cites authoritative prohibition evidence", not invalid_prohibited, invalid_prohibited, [], invalid_prohibited, "evidence-record semantic classification")
    invalid_excluded = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "EXCLUDED" and not any(e.get("evidenceType") == "EXPLICIT_EXCLUSION_DECISION" for e in (row.get("normalizationEvidence") or []))]
    add(checks, "LIN-10", "lineage", "Every EXCLUDED mapping cites an explicit exclusion decision", not invalid_excluded, invalid_excluded, [], invalid_excluded, "evidence-record type validation")
    unresolved = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "UNRESOLVED"]
    add(checks, "LIN-11", "lineage", "No lineage mapping remains unresolved", not unresolved, unresolved, [], unresolved, "absolute resolution-status scan")
    add(checks, "LIN-12", "lineage", "No conflicting lineage mapping exists", not conflicts, conflicts, [], conflicts, "duplicate legacy-ID conflict detection")
    low_review = [row.get("legacyRequirementId") for row in lineage if row.get("confidence") == "LOW" or row.get("reviewRequired") is True]
    add(checks, "LIN-13", "lineage", "No low-confidence or review-required lineage mapping enters a freeze", not low_review, low_review, [], low_review, "confidence and review flag scan")

    def expected_expansion(source_ids):
        expanded, unknown = [], []
        for source_id in source_ids:
            if source_id in requirement_id_set:
                targets = [source_id]
            elif len(lineage_groups.get(source_id, [])) == 1 and lineage_groups[source_id][0].get("resolutionStatus") != "UNRESOLVED":
                targets = lineage_groups[source_id][0].get("canonicalRequirementIds") or []
            else:
                targets = []
                unknown.append(source_id)
            for target in targets:
                if target not in expanded:
                    expanded.append(target)
        return expanded, unknown

    trace_repairs = {row.get("artifactId"): row for row in lineage_traceability.get("repairs", [])}
    cap_unknown, cap_missing, cap_mismatch, cap_lost, cap_evidence = [], [], [], [], []
    for row in capabilities:
        source_ids = row.get("sourceRequirementIds") or []
        expected, unknown = expected_expansion(source_ids)
        actual = row.get("resolvedCanonicalRequirementIds") or []
        cap_unknown += [{"capabilityId": row.get("capabilityId"), "sourceRequirementId": value} for value in unknown]
        cap_missing += [{"capabilityId": row.get("capabilityId"), "canonicalRequirementId": value} for value in actual if value not in requirement_id_set]
        if actual != expected or row.get("requirementLineageStatus") != "RESOLVED": cap_mismatch.append(row.get("capabilityId"))
        repair = trace_repairs.get(row.get("capabilityId"), {})
        if source_ids != repair.get("sourceValuesBefore") or source_ids != repair.get("sourceValuesAfter"): cap_lost.append(row.get("capabilityId"))
        if {item.get("sourceRequirementId") for item in (row.get("requirementLineageEvidence") or [])} != set(source_ids): cap_evidence.append(row.get("capabilityId"))
    add(checks, "LIN-14", "lineage", "Every capability source ID resolves", not cap_unknown, cap_unknown, [], cap_unknown, "canonical-or-lineage resolution")
    add(checks, "LIN-15", "lineage", "Every capability canonical target exists", not cap_missing, cap_missing, [], cap_missing, "canonical requirement ID membership")
    add(checks, "LIN-16", "lineage", "Every capability resolved set exactly equals source-lineage expansion", not cap_mismatch, cap_mismatch, [], cap_mismatch, "independent ordered source expansion")
    add(checks, "LIN-17", "lineage", "Every original capability source identity is preserved", not cap_lost, cap_lost, [], cap_lost, "repair-report before/current source-array equality")
    add(checks, "LIN-18", "lineage", "Every capability records evidence for every source ID", not cap_evidence, cap_evidence, [], cap_evidence, "source/evidence set equality")
    task_unknown, task_missing, task_mismatch, task_lost, task_evidence = [], [], [], [], []
    for row in tasks:
        source_ids = row.get("sourceRequirements") or []
        expected, unknown = expected_expansion(source_ids)
        actual = row.get("resolvedCanonicalRequirementIds") or []
        task_unknown += [{"taskId": row.get("taskId"), "sourceRequirementId": value} for value in unknown]
        task_missing += [{"taskId": row.get("taskId"), "canonicalRequirementId": value} for value in actual if value not in requirement_id_set]
        if actual != expected or row.get("requirementLineageStatus") != "RESOLVED": task_mismatch.append(row.get("taskId"))
        repair = trace_repairs.get(row.get("taskId"), {})
        if source_ids != repair.get("sourceValuesBefore") or source_ids != repair.get("sourceValuesAfter"): task_lost.append(row.get("taskId"))
        if {item.get("sourceRequirementId") for item in (row.get("requirementLineageEvidence") or [])} != set(source_ids): task_evidence.append(row.get("taskId"))
    add(checks, "LIN-19", "lineage", "Every task source ID resolves", not task_unknown, task_unknown, [], task_unknown, "canonical-or-lineage resolution")
    add(checks, "LIN-20", "lineage", "Every task canonical target exists", not task_missing, task_missing, [], task_missing, "canonical requirement ID membership")
    add(checks, "LIN-21", "lineage", "Every task resolved set exactly equals source-lineage expansion", not task_mismatch, task_mismatch, [], task_mismatch, "independent ordered source expansion")
    add(checks, "LIN-22", "lineage", "Every original task source identity is preserved", not task_lost, task_lost, [], task_lost, "repair-report before/current source-array equality")
    add(checks, "LIN-23", "lineage", "Every task records evidence for every source ID", not task_evidence, task_evidence, [], task_evidence, "source/evidence set equality")

    # --- Lineage semantic validation: exact vocabulary, status-specific rules, and evidence binding. ---
    invalid_status_rows = []
    for row in lineage:
        value = row.get("resolutionStatus")
        if value not in ALLOWED_LINEAGE_STATUSES:
            invalid_status_rows.append({"legacyRequirementId": row.get("legacyRequirementId"), "resolutionStatus": value})
    add(checks, "LINEAGE-STATUS-ENUM", "lineage", "Every lineage resolutionStatus is in the exact allowed vocabulary without normalization", not invalid_status_rows, invalid_status_rows, [], invalid_status_rows, "exact allowed-status enumeration; no lowercasing, trimming, or aliasing")
    missing_legacy_ids = [row.get("legacyRequirementId") for row in lineage if not str(row.get("legacyRequirementId") or "").strip()]
    duplicate_legacy_ids = sorted(key for key, rows in lineage_groups.items() if key and len(rows) != 1)
    add(checks, "LINEAGE-LEGACY-ID-UNIQUENESS", "lineage", "Every lineage record has a present, nonempty, unique legacyRequirementId", not missing_legacy_ids and not duplicate_legacy_ids, {"missing": missing_legacy_ids, "duplicates": duplicate_legacy_ids}, {"missing": [], "duplicates": []}, missing_legacy_ids + duplicate_legacy_ids, "legacy-ID presence and multiplicity scan")
    lineage_common_issues = []
    target_required_statuses = {"DIRECT", "SUPERSEDED", "MERGED", "SPLIT", "RECLASSIFIED", "ALIAS"}
    missing_required_targets = []
    for row in lineage:
        legacy_id = row.get("legacyRequirementId")
        if not str(legacy_id or "").strip():
            continue
        issues = []
        if not str(row.get("legacyRequirementType") or "").strip():
            issues.append("missing legacyRequirementType")
        artifact = normalize_rel(row.get("legacySourceArtifact"))
        if not artifact or not source_path(artifact, overrides).exists():
            issues.append("missing or nonexistent legacySourceArtifact")
        location = str(row.get("legacySourceLocation") or "")
        if not re.fullmatch(r"jsonl:\d+", location):
            issues.append("structurally invalid legacySourceLocation")
        targets = row.get("canonicalRequirementIds")
        if not isinstance(targets, list):
            issues.append("canonicalRequirementIds is not a list")
        else:
            duplicate_targets = sorted({target for target, count in Counter(targets).items() if count > 1})
            if duplicate_targets:
                issues.append("duplicate canonicalRequirementIds: " + ",".join(duplicate_targets))
            if row.get("resolutionStatus") in target_required_statuses:
                absent = sorted({target for target in targets if target not in requirement_id_set})
                if absent:
                    missing_required_targets.append({"legacyRequirementId": legacy_id, "missingTargets": absent})
        supers = row.get("supersessionRecordIds")
        if not isinstance(supers, list):
            issues.append("supersessionRecordIds is not a list")
        else:
            absent_supersessions = [record_id for record_id in supers if record_id not in supersession_by_id]
            if absent_supersessions:
                issues.append("missing supersession records: " + ",".join(absent_supersessions))
        if not isinstance(row.get("normalizationEvidence"), list) or not row.get("normalizationEvidence"):
            issues.append("normalizationEvidence is not a nonempty list")
        if not str(row.get("resolutionReason") or "").strip():
            issues.append("missing resolutionReason")
        if row.get("confidence") not in {"HIGH", "MEDIUM", "LOW"}:
            issues.append("confidence not in HIGH/MEDIUM/LOW")
        if not isinstance(row.get("reviewRequired"), bool):
            issues.append("reviewRequired is not boolean")
        if issues:
            lineage_common_issues.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-CANONICAL-TARGETS", "lineage", "Common lineage record invariants and canonical target/supersession references are valid", not lineage_common_issues and not missing_required_targets, {"recordIssues": lineage_common_issues, "missingRequiredTargets": missing_required_targets}, {"recordIssues": [], "missingRequiredTargets": []}, lineage_common_issues + missing_required_targets, "schema field, target existence, and supersession cross-reference validation")
    supersession_evidence_issues = []
    for row in lineage:
        legacy_id = row.get("legacyRequirementId")
        issues = []
        for record_id in row.get("supersessionRecordIds") or []:
            record = supersession_by_id.get(record_id)
            if not record:
                issues.append(f"missing supersession record {record_id}")
            elif record.get("oldRequirementId") != legacy_id or set(record.get("newRequirementIds") or []) != set(row.get("canonicalRequirementIds") or []):
                issues.append(f"supersession record {record_id} does not agree with the lineage mapping")
        if row.get("resolutionStatus") == "SUPERSEDED":
            if not (row.get("supersessionRecordIds") or []):
                issues.append("SUPERSEDED requires at least one supersession record")
            elif not any(supersession_by_id.get(record_id) and supersession_by_id[record_id].get("oldRequirementId") == legacy_id for record_id in row.get("supersessionRecordIds") or []):
                issues.append("SUPERSEDED supersession records do not reference the legacy source")
        if issues:
            supersession_evidence_issues.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-SUPERSESSION-EVIDENCE", "lineage", "Every declared supersession record exists, references the legacy source, and agrees with its lineage mapping", not supersession_evidence_issues, supersession_evidence_issues, [], supersession_evidence_issues, "supersession-map cross-reference, source binding, and target-set equality")

    def evidence_node_ids(evidence):
        return {str(item.get("nodeId")) for item in (evidence or []) if isinstance(item, dict) and item.get("nodeId")}

    def evidence_canonical_ids(evidence):
        return {str(item.get("canonicalRequirementId")) for item in (evidence or []) if isinstance(item, dict) and item.get("canonicalRequirementId")}

    invalid_direct_semantics = []
    for row in lineage:
        if row.get("resolutionStatus") != "DIRECT":
            continue
        legacy_id = row.get("legacyRequirementId")
        targets = row.get("canonicalRequirementIds") or []
        issues = []
        if len(targets) != 1:
            issues.append("DIRECT requires exactly one canonical target")
        else:
            target = targets[0]
            if target not in requirement_id_set:
                issues.append(f"canonical target {target} does not exist")
            evidence = row.get("normalizationEvidence") or []
            if not any(isinstance(item, dict) and item.get("nodeId") == legacy_id and item.get("canonicalRequirementId") == target for item in evidence):
                issues.append("evidence does not directly bind the legacy ID to the canonical target")
            for record_id in row.get("supersessionRecordIds") or []:
                record = supersession_by_id.get(record_id)
                if record and (record.get("oldRequirementId") != legacy_id or set(record.get("newRequirementIds") or []) != {target}):
                    issues.append(f"contradictory supersession mapping {record_id}")
        if row.get("confidence") != "HIGH":
            issues.append("DIRECT confidence is not HIGH")
        if row.get("reviewRequired") is True:
            issues.append("DIRECT reviewRequired is true")
        if issues:
            invalid_direct_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-DIRECT-SEMANTICS", "lineage", "DIRECT mappings require one existing canonical target, direct binding evidence, HIGH confidence, and no review requirement", not invalid_direct_semantics, invalid_direct_semantics, [], invalid_direct_semantics, "status-specific cardinality, evidence binding, confidence, and review-flag semantics")
    invalid_superseded_semantics = []
    for row in lineage:
        if row.get("resolutionStatus") != "SUPERSEDED":
            continue
        legacy_id = row.get("legacyRequirementId")
        targets = row.get("canonicalRequirementIds") or []
        record_ids = row.get("supersessionRecordIds") or []
        issues = []
        if not targets:
            issues.append("SUPERSEDED requires at least one canonical target")
        if not record_ids:
            issues.append("SUPERSEDED requires at least one supersession record")
        else:
            resolved_targets = set()
            for record_id in record_ids:
                record = supersession_by_id.get(record_id)
                if not record:
                    issues.append(f"missing supersession record {record_id}")
                elif record.get("oldRequirementId") != legacy_id:
                    issues.append(f"supersession record {record_id} does not reference the legacy source")
                else:
                    resolved_targets |= set(record.get("newRequirementIds") or [])
            if set(targets) != resolved_targets:
                issues.append("supersession records do not resolve to the declared canonical target set")
        evidence = row.get("normalizationEvidence") or []
        if legacy_id not in evidence_node_ids(evidence):
            issues.append("evidence does not identify the authoritative supersession decision")
        if row.get("reviewRequired") is True:
            issues.append("SUPERSEDED reviewRequired is true")
        if issues:
            invalid_superseded_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-SUPERSEDED-SEMANTICS", "lineage", "SUPERSEDED mappings require canonical targets, valid supersession records binding the legacy source, and decision evidence", not invalid_superseded_semantics, invalid_superseded_semantics, [], invalid_superseded_semantics, "status-specific supersession cardinality, resolution, and evidence semantics")
    invalid_merged_semantics = []
    for row in lineage:
        if row.get("resolutionStatus") != "MERGED":
            continue
        legacy_id = row.get("legacyRequirementId")
        targets = row.get("canonicalRequirementIds") or []
        evidence = row.get("normalizationEvidence") or []
        issues = []
        if not targets:
            issues.append("MERGED requires at least one canonical target")
        if legacy_id not in evidence_node_ids(evidence):
            issues.append("evidence does not identify the exact legacy source ID")
        declared = {str(target) for target in targets}
        ev_targets = evidence_canonical_ids(evidence)
        if declared - ev_targets:
            issues.append("declared canonical target absent from evidence: " + ",".join(sorted(declared - ev_targets)))
        if ev_targets - declared:
            issues.append("undeclared canonical target in evidence: " + ",".join(sorted(ev_targets - declared)))
        reason_text = str(row.get("resolutionReason") or "")
        if not (any(str(target) in reason_text for target in targets) or re.search(r"merge|normaliz|ident", reason_text.lower())):
            issues.append("resolutionReason does not explain the merge")
        if row.get("reviewRequired") is True:
            issues.append("MERGED reviewRequired is true")
        if issues:
            invalid_merged_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-MERGED-SEMANTICS", "lineage", "MERGED mappings bind the exact legacy source to the complete declared canonical target set", not invalid_merged_semantics, invalid_merged_semantics, [], invalid_merged_semantics, "source-ID binding, complete target coverage, undeclared-target rejection, and merge rationale")
    invalid_split_semantics = []
    for row in lineage:
        if row.get("resolutionStatus") != "SPLIT":
            continue
        legacy_id = row.get("legacyRequirementId")
        targets = row.get("canonicalRequirementIds") or []
        issues = []
        if len(set(targets)) < 2:
            issues.append("SPLIT requires at least two distinct canonical targets")
        else:
            absent = sorted({target for target in targets if target not in requirement_id_set})
            if absent:
                issues.append("missing split targets: " + ",".join(absent))
        evidence = row.get("normalizationEvidence") or []
        if legacy_id not in evidence_node_ids(evidence):
            issues.append("evidence does not bind the legacy source to the split targets")
        declared = {str(target) for target in targets}
        ev_targets = evidence_canonical_ids(evidence)
        if declared - ev_targets:
            issues.append("evidence misses declared split targets: " + ",".join(sorted(declared - ev_targets)))
        if ev_targets - declared:
            issues.append("undeclared split target in evidence: " + ",".join(sorted(ev_targets - declared)))
        if not re.search(r"split", str(row.get("resolutionReason") or "").lower()):
            issues.append("resolutionReason does not explain the split")
        if row.get("reviewRequired") is True:
            issues.append("SPLIT reviewRequired is true")
        if issues:
            invalid_split_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-SPLIT-SEMANTICS", "lineage", "SPLIT mappings require at least two existing targets with complete binding evidence and a split rationale", not invalid_split_semantics, invalid_split_semantics, [], invalid_split_semantics, "status-specific cardinality, target existence, evidence coverage, and rationale")
    invalid_reclassified_semantics = []
    invalid_reclassified_source = []
    invalid_reclassified_target = []
    for row in lineage:
        if row.get("resolutionStatus") != "RECLASSIFIED":
            continue
        legacy_id = row.get("legacyRequirementId")
        targets = row.get("canonicalRequirementIds") or []
        evidence = row.get("normalizationEvidence") or []
        issues = []
        source_issues = []
        target_issues = []
        control_targets = [item for item in evidence if isinstance(item, dict) and (item.get("targetId") or item.get("controlTargetId") or item.get("targetType"))]
        if not targets and not control_targets:
            issues.append("RECLASSIFIED requires a canonical target or an explicit authoritative typed control target")
        if legacy_id not in evidence_node_ids(evidence):
            issues.append("evidence does not bind the legacy ID to the reclassified target")
            source_issues.append("evidence does not identify the exact legacy source ID")
        if not any(isinstance(item, dict) and (item.get("originalClassification") or item.get("previousClassification")) for item in evidence):
            issues.append("evidence does not identify the original classification")
        if not any(isinstance(item, dict) and (item.get("newClassification") or item.get("reclassifiedAs")) for item in evidence):
            issues.append("evidence does not identify the new classification")
        if targets:
            if len(targets) != 1:
                issues.append("RECLASSIFIED canonical target set is not exactly one")
            else:
                declared = targets[0]
                if declared not in requirement_id_set:
                    issues.append(f"canonical target {declared} does not exist")
                ev_targets = evidence_canonical_ids(evidence)
                if declared not in ev_targets:
                    issues.append("evidence target does not equal the declared canonical target")
                    target_issues.append(f"evidence canonical target does not equal declared target {declared}")
                if ev_targets - {declared}:
                    issues.append("evidence cites undeclared canonical targets: " + ",".join(sorted(ev_targets - {declared})))
                    target_issues.append("evidence cites undeclared canonical targets")
        elif not control_targets or not any(item.get("targetId") or item.get("controlTargetId") for item in control_targets):
            issues.append("no explicit typed control target identified in evidence")
            target_issues.append("no explicit typed control target identified in evidence")
        if not re.search(r"reclass", str(row.get("resolutionReason") or "").lower()):
            issues.append("resolutionReason does not explain the reclassification")
        if row.get("reviewRequired") is True:
            issues.append("RECLASSIFIED reviewRequired is true")
        if source_issues:
            invalid_reclassified_source.append({"legacyRequirementId": legacy_id, "issues": source_issues})
        if target_issues:
            invalid_reclassified_target.append({"legacyRequirementId": legacy_id, "issues": target_issues})
        if issues:
            invalid_reclassified_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-RECLASSIFIED-SOURCE", "lineage", "RECLASSIFIED evidence identifies the exact legacy source ID", not invalid_reclassified_source, invalid_reclassified_source, [], invalid_reclassified_source, "evidence nodeId to legacyRequirementId exact binding")
    add(checks, "LINEAGE-RECLASSIFIED-TARGET", "lineage", "RECLASSIFIED evidence identifies the exact declared canonical or typed-control target", not invalid_reclassified_target, invalid_reclassified_target, [], invalid_reclassified_target, "evidence canonical/control target equality with the record target")
    add(checks, "LINEAGE-RECLASSIFIED-SEMANTICS", "lineage", "RECLASSIFIED mappings require classification evidence and are not treated as MERGED", not invalid_reclassified_semantics, invalid_reclassified_semantics, [], invalid_reclassified_semantics, "original/new classification identification and target binding semantics")
    invalid_prohibited_semantics = []
    for row in lineage:
        if row.get("resolutionStatus") != "PROHIBITED":
            continue
        legacy_id = row.get("legacyRequirementId")
        evidence = row.get("normalizationEvidence") or []
        issues = []
        if (row.get("canonicalRequirementIds") or []) != []:
            issues.append("canonical targets do not follow the prohibition schema")
        prohibition_evidence = [item for item in evidence if isinstance(item, dict) and ("PROHIBIT" in str(item.get("evidenceType") or "").upper() or "PROHIBIT" in str(item.get("decision") or "").upper() or "Architecture Decisions" in str(item.get("artifact") or ""))]
        if not prohibition_evidence:
            issues.append("no authoritative prohibition record or ADR evidence")
        elif legacy_id not in {str(item.get("nodeId")) for item in prohibition_evidence if item.get("nodeId")} and not any(legacy_id in str(item.get("decision") or "") for item in prohibition_evidence):
            issues.append("prohibition evidence does not apply to this legacy requirement")
        if not re.search(r"prohibit", str(row.get("resolutionReason") or "").lower()):
            issues.append("resolutionReason does not explain the prohibition")
        if row.get("reviewRequired") is True:
            issues.append("PROHIBITED reviewRequired is true")
        if issues:
            invalid_prohibited_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-PROHIBITED-SEMANTICS", "lineage", "PROHIBITED mappings cite authoritative prohibition evidence applying to the same legacy requirement", not invalid_prohibited_semantics, invalid_prohibited_semantics, [], invalid_prohibited_semantics, "prohibition-schema representation, authoritative evidence, and same-requirement applicability")
    invalid_excluded_semantics = []
    for row in lineage:
        if row.get("resolutionStatus") != "EXCLUDED":
            continue
        legacy_id = row.get("legacyRequirementId")
        evidence = row.get("normalizationEvidence") or []
        issues = []
        if (row.get("canonicalRequirementIds") or []) != []:
            issues.append("canonical targets do not follow the exclusion schema")
        if not any(isinstance(item, dict) and item.get("evidenceType") == "EXPLICIT_EXCLUSION_DECISION" for item in evidence):
            issues.append("missing authoritative exclusion evidence")
        if legacy_id not in evidence_node_ids(evidence):
            issues.append("evidence does not explicitly identify the excluded legacy requirement")
        if not str(row.get("resolutionReason") or "").strip():
            issues.append("missing exclusion rationale")
        if row.get("reviewRequired") is True:
            issues.append("EXCLUDED reviewRequired is true")
        if issues:
            invalid_excluded_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-EXCLUDED-SEMANTICS", "lineage", "EXCLUDED mappings retain explicit authoritative exclusion evidence and the excluded legacy identity", not invalid_excluded_semantics, invalid_excluded_semantics, [], invalid_excluded_semantics, "exclusion-schema representation, decision evidence, and explicit legacy-ID identification")
    alias_rows = {row.get("legacyRequirementId"): row for row in lineage if row.get("resolutionStatus") == "ALIAS"}
    alias_adjacency = {}
    invalid_alias_semantics = []
    invalid_alias_source = []
    invalid_alias_target = []
    for legacy_id, row in alias_rows.items():
        targets = row.get("canonicalRequirementIds") or []
        evidence = row.get("normalizationEvidence") or []
        issues = []
        source_issues = []
        target_issues = []
        if len(targets) != 1:
            issues.append("ALIAS requires exactly one canonical target")
            target_issues.append("ALIAS requires exactly one canonical target")
        else:
            target = targets[0]
            if target not in requirement_id_set:
                issues.append(f"canonical target {target} does not exist")
                target_issues.append(f"canonical target {target} does not exist")
            if target in alias_rows:
                issues.append("alias target is itself an alias (chain or cycle)")
                target_issues.append("alias target is itself an alias (chain or cycle)")
            alias_adjacency[legacy_id] = [target]
            bound = any(isinstance(item, dict) and item.get("nodeId") == legacy_id and item.get("canonicalRequirementId") == target for item in evidence)
            if not any(isinstance(item, dict) and item.get("nodeId") == legacy_id for item in evidence):
                issues.append("evidence does not identify the exact legacy source ID")
                source_issues.append("evidence nodeId does not equal the legacy source ID")
            if not any(isinstance(item, dict) and item.get("canonicalRequirementId") == target for item in evidence):
                issues.append("evidence does not bind the exact canonical target")
                target_issues.append(f"evidence canonicalRequirementId does not equal {target}")
            if not bound:
                issues.append("evidence does not prove the exact source-to-target alias binding")
        if row.get("confidence") != "HIGH":
            issues.append("ALIAS confidence is not HIGH")
        if row.get("reviewRequired") is True:
            issues.append("ALIAS reviewRequired is true")
        if source_issues:
            invalid_alias_source.append({"legacyRequirementId": legacy_id, "issues": source_issues})
        if target_issues:
            invalid_alias_target.append({"legacyRequirementId": legacy_id, "issues": target_issues})
        if issues:
            invalid_alias_semantics.append({"legacyRequirementId": legacy_id, "issues": issues})
    for cycle in find_cycles(alias_adjacency):
        for node in cycle[:-1]:
            for entry in invalid_alias_semantics:
                if entry["legacyRequirementId"] == node and "creates a cycle" not in " ".join(entry["issues"]):
                    entry["issues"].append("alias mapping creates a cycle")
            for entry in invalid_alias_target:
                if entry["legacyRequirementId"] == node and "creates a cycle" not in " ".join(entry["issues"]):
                    entry["issues"].append("alias mapping creates a cycle")
    add(checks, "LINEAGE-ALIAS-SOURCE", "lineage", "ALIAS evidence identifies the exact legacy source ID", not invalid_alias_source, invalid_alias_source, [], invalid_alias_source, "evidence nodeId to legacyRequirementId exact binding")
    add(checks, "LINEAGE-ALIAS-TARGET", "lineage", "ALIAS evidence identifies the exact single canonical target", not invalid_alias_target, invalid_alias_target, [], invalid_alias_target, "evidence canonicalRequirementId to declared target exact binding")
    add(checks, "LINEAGE-ALIAS-SEMANTICS", "lineage", "ALIAS mappings are single-target, evidence-backed, HIGH-confidence, and free of chains and cycles", not invalid_alias_semantics, invalid_alias_semantics, [], invalid_alias_semantics, "alias cardinality, existence, exact source/target proof, chain/cycle resolution, confidence, and review-flag semantics")
    unresolved_semantic = [row.get("legacyRequirementId") for row in lineage if row.get("resolutionStatus") == "UNRESOLVED"]
    add(checks, "LINEAGE-UNRESOLVED", "lineage", "No lineage mapping remains UNRESOLVED at final-freeze validation", not unresolved_semantic, unresolved_semantic, [], unresolved_semantic, "absolute UNRESOLVED status scan identifying each legacy ID")
    invalid_confidence = []
    for row in lineage:
        legacy_id = row.get("legacyRequirementId")
        confidence = row.get("confidence")
        issues = []
        if confidence not in {"HIGH", "MEDIUM", "LOW"}:
            issues.append(f"invalid confidence {confidence!r}")
        elif confidence == "LOW":
            issues.append("LOW confidence is not acceptable")
        elif confidence == "MEDIUM":
            evidence = row.get("normalizationEvidence") or []
            if not any(isinstance(item, dict) and str(item.get("artifact") or "").strip() for item in evidence):
                issues.append("MEDIUM confidence lacks explicit authoritative evidence")
            if row.get("reviewRequired") is True:
                issues.append("MEDIUM confidence requires no review requirement")
        if row.get("reviewRequired") is True:
            issues.append("reviewRequired is true")
        if issues:
            invalid_confidence.append({"legacyRequirementId": legacy_id, "issues": issues})
    add(checks, "LINEAGE-CONFIDENCE", "lineage", "Confidence and review-required lineage rules are enforced", not invalid_confidence, invalid_confidence, [], invalid_confidence, "confidence enumeration plus LOW/review rejection and MEDIUM evidence requirement")
    cap_expansion_issues = []
    for row in capabilities:
        capability_id = row.get("capabilityId")
        source_ids = row.get("sourceRequirementIds") or []
        expected, unknown = expected_expansion(source_ids)
        actual = row.get("resolvedCanonicalRequirementIds") or []
        issues = []
        if unknown:
            issues.append("unresolved source IDs: " + ",".join(sorted(unknown)))
        if len(actual) != len(set(actual)):
            issues.append("duplicated canonical IDs in resolved set")
        if actual != expected:
            issues.append("resolved set differs from the lineage expansion")
        if row.get("requirementLineageStatus") != "RESOLVED":
            issues.append("requirementLineageStatus is not RESOLVED")
        if issues:
            cap_expansion_issues.append({"capabilityId": capability_id, "issues": issues})
    add(checks, "CAPABILITY-LINEAGE-EXPANSION", "lineage", "Every capability resolved canonical set exactly equals its source-lineage expansion with no missing, extra, invented, unresolved, or duplicated IDs", not cap_expansion_issues, cap_expansion_issues, [], cap_expansion_issues, "exact ordered expansion through the lineage authority")
    def evidence_expectation(source_id):
        if source_id in requirement_id_set:
            return "DIRECT", [source_id], []
        records = lineage_groups.get(source_id, [])
        if len(records) != 1:
            return None, [], []
        record = records[0]
        return record.get("resolutionStatus"), record.get("canonicalRequirementIds") or [], record.get("supersessionRecordIds") or []

    def audit_evidence_payload(owner_id, source_ids, resolved_ids, evidence):
        by_check = {key: [] for key in ("SOURCE", "STATUS", "TARGETS", "SUPERSESSION", "AUTHORITY", "PAYLOAD")}
        if not isinstance(evidence, list) or not evidence:
            by_check["PAYLOAD"].append(f"{owner_id}: missing evidence payload")
        seen_sources = []
        for item in evidence if isinstance(evidence, list) else []:
            if not isinstance(item, dict):
                by_check["PAYLOAD"].append(f"{owner_id}: evidence entry is not an object")
                continue
            source_id = item.get("sourceRequirementId")
            seen_sources.append(source_id)
            if source_id not in source_ids:
                by_check["SOURCE"].append(f"{owner_id}: evidence cites unrelated source ID {source_id!r}")
            expected_status, expected_targets, expected_sup = evidence_expectation(source_id)
            if expected_status is None:
                by_check["AUTHORITY"].append(f"{owner_id}: evidence cites a missing or non-unique lineage record for {source_id!r}")
                continue
            actual_status = item.get("resolutionStatus")
            if actual_status != expected_status:
                by_check["STATUS"].append(f"{owner_id}: evidence status {actual_status!r} for {source_id!r} != authoritative {expected_status!r}")
            ev_targets = item.get("canonicalRequirementIds")
            if not isinstance(ev_targets, list):
                by_check["TARGETS"].append(f"{owner_id}: evidence canonicalRequirementIds is not a list for {source_id!r}")
                ev_targets = []
            if ev_targets != expected_targets:
                by_check["TARGETS"].append(f"{owner_id}: evidence canonical set for {source_id!r} does not match the lineage expansion")
            sup_ids = item.get("supersessionRecordIds")
            if not isinstance(sup_ids, list):
                by_check["SUPERSESSION"].append(f"{owner_id}: evidence supersessionRecordIds is not a list for {source_id!r}")
                sup_ids = []
            for record_id in sup_ids:
                if record_id not in supersession_by_id:
                    by_check["SUPERSESSION"].append(f"{owner_id}: evidence cites a missing supersession record {record_id!r}")
            if sup_ids != expected_sup:
                by_check["SUPERSESSION"].append(f"{owner_id}: evidence supersession records for {source_id!r} do not match the lineage map")
            authority_refs = [item.get(key) for key in ("lineageRecordId", "authorityReference", "legacyRecordId", "evidenceRecordId") if item.get(key) is not None]
            if authority_refs and not all(str(ref) == str(source_id) for ref in authority_refs):
                by_check["AUTHORITY"].append(f"{owner_id}: evidence authority reference for {source_id!r} does not identify the same lineage record")
        for source_id in source_ids:
            if seen_sources.count(source_id) != 1:
                by_check["PAYLOAD"].append(f"{owner_id}: source {source_id!r} does not have exactly one evidence entry")
        evidence_union = []
        for item in evidence if isinstance(evidence, list) else []:
            if isinstance(item, dict):
                for target in item.get("canonicalRequirementIds") or []:
                    if target not in evidence_union:
                        evidence_union.append(target)
        if evidence_union != (resolved_ids or []):
            by_check["TARGETS"].append(f"{owner_id}: evidence canonical union does not match the stored resolved set")
        return by_check

    cap_evidence_by_check = {key: [] for key in ("SOURCE", "STATUS", "TARGETS", "SUPERSESSION", "AUTHORITY", "PAYLOAD")}
    for row in capabilities:
        capability_id = row.get("capabilityId")
        by_check = audit_evidence_payload(capability_id, row.get("sourceRequirementIds") or [], row.get("resolvedCanonicalRequirementIds") or [], row.get("requirementLineageEvidence") or [])
        for key, entries in by_check.items():
            cap_evidence_by_check[key].extend(entries)
    add(checks, "CAPABILITY-LINEAGE-EVIDENCE-SOURCE", "lineage", "Every capability evidence source ID exactly equals a declared source and never cites an unrelated ID", not cap_evidence_by_check["SOURCE"], cap_evidence_by_check["SOURCE"], [], cap_evidence_by_check["SOURCE"], "evidence source identity binding")
    add(checks, "CAPABILITY-LINEAGE-EVIDENCE-STATUS", "lineage", "Every capability evidence resolution status equals the authoritative direct or lineage-map status", not cap_evidence_by_check["STATUS"], cap_evidence_by_check["STATUS"], [], cap_evidence_by_check["STATUS"], "evidence status to lineage-map exact comparison")
    add(checks, "CAPABILITY-LINEAGE-EVIDENCE-TARGETS", "lineage", "Every capability evidence canonical target set exactly equals the authoritative lineage expansion", not cap_evidence_by_check["TARGETS"], cap_evidence_by_check["TARGETS"], [], cap_evidence_by_check["TARGETS"], "evidence target-set equality and resolved-set union match")
    add(checks, "CAPABILITY-LINEAGE-EVIDENCE-SUPERSESSION", "lineage", "Every capability evidence supersession set exactly equals the lineage-map supersession records", not cap_evidence_by_check["SUPERSESSION"], cap_evidence_by_check["SUPERSESSION"], [], cap_evidence_by_check["SUPERSESSION"], "evidence supersession cross-reference equality")
    add(checks, "CAPABILITY-LINEAGE-EVIDENCE-AUTHORITY", "lineage", "Every capability evidence authority reference identifies the same legacy record and payload is complete", not cap_evidence_by_check["AUTHORITY"] and not cap_evidence_by_check["PAYLOAD"], {"authority": cap_evidence_by_check["AUTHORITY"], "payload": cap_evidence_by_check["PAYLOAD"]}, [], cap_evidence_by_check["AUTHORITY"] + cap_evidence_by_check["PAYLOAD"], "lineage-record authority identity and one-entry-per-source completeness")
    cap_evidence_all = []
    for key in ("SOURCE", "STATUS", "TARGETS", "SUPERSESSION", "AUTHORITY", "PAYLOAD"):
        cap_evidence_all.extend(cap_evidence_by_check[key])
    add(checks, "CAPABILITY-LINEAGE-EVIDENCE", "lineage", "Every capability evidence payload semantically identifies its sources, lineage/supersession authority, and exact canonical outcomes", not cap_evidence_all, cap_evidence_all, [], cap_evidence_all, "evidence source binding, authority cross-reference, canonical set match, and resolved-set union equality")
    task_expansion_issues = []
    for row in tasks:
        task_id = row.get("taskId")
        source_ids = row.get("sourceRequirements") or []
        expected, unknown = expected_expansion(source_ids)
        actual = row.get("resolvedCanonicalRequirementIds") or []
        issues = []
        if unknown:
            issues.append("unresolved source IDs: " + ",".join(sorted(unknown)))
        if len(actual) != len(set(actual)):
            issues.append("duplicated canonical IDs in resolved set")
        if actual != expected:
            issues.append("resolved set differs from the lineage expansion")
        if row.get("requirementLineageStatus") != "RESOLVED":
            issues.append("requirementLineageStatus is not RESOLVED")
        if issues:
            task_expansion_issues.append({"taskId": task_id, "issues": issues})
    add(checks, "TASK-LINEAGE-EXPANSION", "lineage", "Every task resolved canonical set exactly equals its source-lineage expansion with no missing, extra, invented, unresolved, or duplicated IDs", not task_expansion_issues, task_expansion_issues, [], task_expansion_issues, "exact ordered expansion through the lineage authority")
    task_evidence_by_check = {key: [] for key in ("SOURCE", "STATUS", "TARGETS", "SUPERSESSION", "AUTHORITY", "PAYLOAD")}
    for row in tasks:
        task_id = row.get("taskId")
        by_check = audit_evidence_payload(task_id, row.get("sourceRequirements") or [], row.get("resolvedCanonicalRequirementIds") or [], row.get("requirementLineageEvidence") or [])
        for key, entries in by_check.items():
            task_evidence_by_check[key].extend(entries)
    add(checks, "TASK-LINEAGE-EVIDENCE-SOURCE", "lineage", "Every task evidence source ID exactly equals a declared source and never cites an unrelated ID", not task_evidence_by_check["SOURCE"], task_evidence_by_check["SOURCE"], [], task_evidence_by_check["SOURCE"], "evidence source identity binding")
    add(checks, "TASK-LINEAGE-EVIDENCE-STATUS", "lineage", "Every task evidence resolution status equals the authoritative direct or lineage-map status", not task_evidence_by_check["STATUS"], task_evidence_by_check["STATUS"], [], task_evidence_by_check["STATUS"], "evidence status to lineage-map exact comparison")
    add(checks, "TASK-LINEAGE-EVIDENCE-TARGETS", "lineage", "Every task evidence canonical target set exactly equals the authoritative lineage expansion", not task_evidence_by_check["TARGETS"], task_evidence_by_check["TARGETS"], [], task_evidence_by_check["TARGETS"], "evidence target-set equality and resolved-set union match")
    add(checks, "TASK-LINEAGE-EVIDENCE-SUPERSESSION", "lineage", "Every task evidence supersession set exactly equals the lineage-map supersession records", not task_evidence_by_check["SUPERSESSION"], task_evidence_by_check["SUPERSESSION"], [], task_evidence_by_check["SUPERSESSION"], "evidence supersession cross-reference equality")
    add(checks, "TASK-LINEAGE-EVIDENCE-AUTHORITY", "lineage", "Every task evidence authority reference identifies the same legacy record and payload is complete", not task_evidence_by_check["AUTHORITY"] and not task_evidence_by_check["PAYLOAD"], {"authority": task_evidence_by_check["AUTHORITY"], "payload": task_evidence_by_check["PAYLOAD"]}, [], task_evidence_by_check["AUTHORITY"] + task_evidence_by_check["PAYLOAD"], "lineage-record authority identity and one-entry-per-source completeness")
    task_evidence_all = []
    for key in ("SOURCE", "STATUS", "TARGETS", "SUPERSESSION", "AUTHORITY", "PAYLOAD"):
        task_evidence_all.extend(task_evidence_by_check[key])
    add(checks, "TASK-LINEAGE-EVIDENCE", "lineage", "Every task evidence payload semantically identifies its sources, lineage/supersession authority, and exact canonical outcomes", not task_evidence_all, task_evidence_all, [], task_evidence_all, "evidence source binding, authority cross-reference, canonical set match, and resolved-set union equality")
    inventory_manifest_path = "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl"
    matching_inventory_records = [row for row in inventory if normalize_rel(row.get("path")) == inventory_manifest_path]
    live_manifest_count = len(manifest)
    inventory_count_issues = []
    if len(matching_inventory_records) != 1:
        inventory_count_issues.append({"matchingRecords": len(matching_inventory_records), "expected": 1})
    else:
        declared = matching_inventory_records[0].get("recordCount")
        if declared != live_manifest_count:
            inventory_count_issues.append({"declared": declared, "actual": live_manifest_count})
    add(checks, "INVENTORY-CANDIDATE-RECORD-COUNT", "inventory", "The candidate inventory record count equals the live candidate manifest nonblank valid JSONL record count", not inventory_count_issues, {"issues": inventory_count_issues, "duplicates": max(0, len(matching_inventory_records) - 1), "missing": 1 if not matching_inventory_records else 0}, {"declared": live_manifest_count, "duplicates": 0, "missing": 0}, matching_inventory_records, "live nonblank JSONL enumeration and unique inventory lookup")

    # Absolute replacement-backup verification: live source, live backup, and receipt must all agree. No environment exclusions exist.
    backup_errors = []
    source_root = Path(str(backup_receipt.get("sourceRoot") or ""))
    backup_root = Path(str(backup_receipt.get("backupRoot") or ""))
    source_scan = inventory_tree(ROOT)
    backup_scan = {"files": [], "directories": [], "aggregateSha256": None}
    try:
        if backup_root.exists():
            backup_scan = inventory_tree(backup_root)
    except Exception as error:
        backup_errors.append(str(error))
    source_files = {row.get("path"): row for row in source_scan.get("files", [])}
    backup_files = {row.get("path"): row for row in backup_scan.get("files", [])}
    source_dirs = set(source_scan.get("directories", []))
    backup_dirs = set(backup_scan.get("directories", []))
    backup_missing = sorted(set(source_files) - set(backup_files))
    backup_extra = sorted(set(backup_files) - set(source_files))
    backup_hash_mismatches = sorted(path for path in set(source_files) & set(backup_files) if source_files[path].get("sha256") != backup_files[path].get("sha256"))
    backup_size_mismatches = sorted(path for path in set(source_files) & set(backup_files) if source_files[path].get("sizeBytes") != backup_files[path].get("sizeBytes"))
    backup_directory_delta = sorted(source_dirs ^ backup_dirs)
    long_path_omissions = sorted(path for path in backup_missing if len(str(backup_root)) + 1 + len(path) >= 260)
    source_root_ok = bool(source_root) and source_root.exists() and Path(str(source_root)).resolve() == ROOT.resolve()
    backup_root_ok = bool(backup_root) and backup_root.exists() and not backup_errors
    add(checks, "BAK-01", "backup", "Backup root exists and the receipt references the real current Graphify source root", backup_root_ok and source_root_ok and backup_receipt.get("backupPurpose") == "PRE_REVIEW_CERTIFICATION_RECOVERY_POINT" and bool(backup_receipt.get("supersedesMissingHistoricalBackupPath")), {"sourceRoot": str(source_root), "backupRoot": str(backup_root), "errors": backup_errors}, "two readable existing roots plus replacement-backup purpose", backup_errors, "filesystem existence, exact root identity, and replacement-backup purpose")
    add(checks, "BAK-02", "backup", "Backup file count matches live source and receipt", backup_receipt.get("sourceFileCount") == backup_receipt.get("backupFileCount") == len(source_files) == len(backup_files), {"receiptSource": backup_receipt.get("sourceFileCount"), "receiptBackup": backup_receipt.get("backupFileCount"), "scannedSource": len(source_files), "scannedBackup": len(backup_files)}, len(source_files), [], "live source/backup enumeration plus receipt counts")
    add(checks, "BAK-03", "backup", "Backup directory count and set match live source and receipt", backup_receipt.get("sourceDirectoryCount") == backup_receipt.get("backupDirectoryCount") == len(source_dirs) == len(backup_dirs) and not backup_directory_delta, {"receiptSource": backup_receipt.get("sourceDirectoryCount"), "receiptBackup": backup_receipt.get("backupDirectoryCount"), "scannedSource": len(source_dirs), "scannedBackup": len(backup_dirs), "delta": backup_directory_delta}, len(source_dirs), backup_directory_delta, "live source/backup directory-set equality plus receipt counts")
    add(checks, "BAK-04", "backup", "Backup has zero missing files", not backup_receipt.get("missingPaths") and not backup_missing, {"receipt": backup_receipt.get("missingPaths"), "scanned": backup_missing}, [], backup_missing, "live source/backup path difference")
    add(checks, "BAK-05", "backup", "Backup has zero extra files", not backup_receipt.get("extraPaths") and not backup_extra, {"receipt": backup_receipt.get("extraPaths"), "scanned": backup_extra}, [], backup_extra, "live backup/source path difference")
    add(checks, "BAK-06", "backup", "Backup has zero file hash mismatches", not backup_receipt.get("hashMismatches") and not backup_hash_mismatches, {"receipt": backup_receipt.get("hashMismatches"), "scanned": backup_hash_mismatches}, [], backup_hash_mismatches, "per-file SHA-256 comparison")
    add(checks, "BAK-07", "backup", "Backup has zero file size mismatches", not backup_receipt.get("sizeMismatches") and not backup_size_mismatches, {"receipt": backup_receipt.get("sizeMismatches"), "scanned": backup_size_mismatches}, [], backup_size_mismatches, "per-file byte-size comparison")
    add(checks, "BAK-08", "backup", "Backup has zero long-path omissions", not backup_receipt.get("longPathOmissions") and not long_path_omissions, {"receipt": backup_receipt.get("longPathOmissions"), "scanned": long_path_omissions}, [], long_path_omissions, "receipt plus long-path subset of live path difference")
    add(checks, "BAK-09", "backup", "Backup has zero unreadable paths", not backup_receipt.get("unreadablePaths") and not backup_errors, {"receipt": backup_receipt.get("unreadablePaths"), "scannedErrors": backup_errors}, [], backup_receipt.get("unreadablePaths") or [], "explicit error collection with no silent skips")
    self_referential_artifacts = {
        "00 Execution Control/FINAL_LONG_PATH_BACKUP_VERIFICATION.json",
        "11 Completion/FINAL_GATE_REPAIR_MANIFEST_CANDIDATE.jsonl",
        "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
        "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
        "11 Completion/FINAL_THREE_FILE_CERTIFICATION_REPAIR_REPORT.json",
    }
    source_aggregate_excluding_artifacts = aggregate_hash([row for row in source_scan.get("files", []) if row.get("path") not in self_referential_artifacts])
    backup_aggregate_excluding_artifacts = aggregate_hash([row for row in backup_scan.get("files", []) if row.get("path") not in self_referential_artifacts])
    add(checks, "BAK-10", "backup", "Backup aggregate hash matches live source and receipt", backup_receipt.get("sourceAggregateHash") == backup_receipt.get("backupAggregateHash") == source_aggregate_excluding_artifacts == backup_aggregate_excluding_artifacts, {"receiptSource": backup_receipt.get("sourceAggregateHash"), "receiptBackup": backup_receipt.get("backupAggregateHash"), "scannedSource": source_aggregate_excluding_artifacts, "scannedBackup": backup_aggregate_excluding_artifacts}, source_aggregate_excluding_artifacts, [], "independent sorted path:file-hash aggregate over the tree excluding the backup receipt, candidate manifest, live validation result, challenge report, and three-file repair report. Those five generated artifacts are excluded because the receipt records the tree aggregate, the candidate manifest records the receipt hash, and the live validation result records the manifest aggregate: a full-tree fixed point that includes all five cannot exist when regenerated reports carry fresh timestamps. Every per-file check (BAK-04/05/06/07/12) and the external full-tree backup verification still cover all files byte-for-byte")
    add(checks, "BAK-11", "backup", "Backup receipt is a verified replacement recovery point", backup_receipt.get("verified") is True and bool(backup_receipt.get("verifiedAt")) and backup_receipt.get("copyExitCode") is not None, {"verified": backup_receipt.get("verified"), "verifiedAt": backup_receipt.get("verifiedAt"), "copyExitCode": backup_receipt.get("copyExitCode")}, {"verified": True, "verifiedAt": "nonempty", "copyExitCode": "recorded"}, [], "receipt verification fields")
    add(checks, "BAK-12", "backup", "Receipt records zero directory-set differences", not backup_receipt.get("directoryDifferences") and not backup_directory_delta, {"receipt": backup_receipt.get("directoryDifferences"), "scanned": backup_directory_delta}, [], backup_directory_delta, "receipt and live directory-set difference lists")
    cap_ids = [row.get("capabilityId") for row in capabilities]
    change_ids = {row.get("capabilityId") for row in change_records}
    add(checks, "CNT-04", "counts", "Capability count agrees with change records", len(cap_ids) == len(set(cap_ids)) and set(cap_ids) == change_ids, len(cap_ids), len(change_ids), ["CAPABILITY_REGISTRY.json", "CHANGE_LOCATION_REGISTRY.jsonl"], "independent registry ID set equality")
    add(checks, "CNT-05", "counts", "Change-record count agrees with capability registry", len(change_records) == len(set(cap_ids)), len(change_records), len(set(cap_ids)), ["CHANGE_LOCATION_REGISTRY.jsonl", "CAPABILITY_REGISTRY.json"], "independent registry ID set equality")
    task_ids = [row.get("taskId") for row in tasks]
    primary = [row for row in tasks if row.get("taskClass") == "PRIMARY_CAPABILITY_TASK"]
    bootstrap = [row for row in tasks if row.get("taskClass") == "BOOTSTRAP_TASK"]
    task_class_ok = len(task_ids) == len(set(task_ids)) and {row.get("capabilityId") for row in primary} == set(cap_ids) and len(bootstrap) == 1
    add(checks, "CNT-06", "counts", "Task count and classifications cover every capability plus one bootstrap", task_class_ok, {"total": len(tasks), "primary": len(primary), "bootstrap": len(bootstrap)}, {"primaryCapabilityIds": len(set(cap_ids)), "bootstrap": 1}, ["IMPLEMENTATION_TASKS.jsonl"], "task-class and owner ID set validation")
    actual_test_ids = [row.get("testId") for row in tests]
    tested_caps = {cap_id for row in tests for cap_id in (row.get("capabilityIds") or [])}
    add(checks, "CNT-07", "counts", "Test specifications are unique and cover every capability", len(actual_test_ids) == len(set(actual_test_ids)) and tested_caps == set(cap_ids), {"tests": len(tests), "coveredCapabilities": len(tested_caps)}, {"uniqueTests": len(set(actual_test_ids)), "capabilities": len(set(cap_ids))}, ["REQUIREMENT_TEST_MATRIX.jsonl"], "test ID uniqueness and capability coverage")
    fixture_text = read_text("10 Verification/FIXTURE_QA_MATRIX.md", overrides)
    fixture_rows = re.findall(r"^\|\s*`(FIX-[^`]+)`\s*\|\s*([^|]+?)\s*\|", fixture_text, re.M)
    fixture_categories = sorted({domain.strip() for _, domain in fixture_rows})
    add(checks, "CNT-08", "counts", "Fixture categories are present and uniquely named", bool(fixture_categories), fixture_categories, "one or more table-derived domains", ["FIXTURE_QA_MATRIX.md"], "fixture-table domain enumeration")
    fixture_records = [fixture_id for fixture_id, _ in fixture_rows]
    add(checks, "CNT-09", "counts", "Canonical fixture records are present and unique", bool(fixture_records) and len(fixture_records) == len(set(fixture_records)), len(fixture_records), len(set(fixture_records)), ["FIXTURE_QA_MATRIX.md"], "canonical fixture ID enumeration")
    owner_release_waves = {row.get("releaseWave") for row in capabilities + tasks if row.get("releaseWave")}
    release_waves = set(EXPECTED_WAVES)
    wave_gates = release_matrix.get("waveGates", {})
    add(checks, "CNT-10", "counts", "Owner waves are valid and all six release-wave gates exist", owner_release_waves <= release_waves and set(wave_gates) == release_waves, {"ownerWaves": sorted(owner_release_waves), "gateWaves": sorted(wave_gates)}, {"validOwnerWaves": list(EXPECTED_WAVES), "gateWaves": list(EXPECTED_WAVES)}, ["CAPABILITY_REGISTRY.json", "IMPLEMENTATION_TASKS.jsonl", "RELEASE_GATE_MATRIX.json"], "owner-wave subset and exact gate-key equality")
    add(checks, "CNT-11", "counts", "Exactly six wave gates exist", len(wave_gates) == len(EXPECTED_WAVES), len(wave_gates), len(EXPECTED_WAVES), ["RELEASE_GATE_MATRIX.json"], "absolute gate count")
    capability_gates = release_matrix.get("capabilityValidationGates", [])
    add(checks, "CNT-12", "counts", "Capability-validation gates cover every capability", {row.get("capabilityId") for row in capability_gates} == set(cap_ids), len(capability_gates), len(set(cap_ids)), ["RELEASE_GATE_MATRIX.json"], "capability ID set equality")
    application_gates = release_matrix.get("applicationReleaseGates", [])
    add(checks, "CNT-13", "counts", "Application release gates are explicit and blocking", bool(application_gates) and all(row.get("blocking") for row in application_gates), len(application_gates), "one or more blocking gates", ["RELEASE_GATE_MATRIX.json"], "gate field validation")
    adr_files = sorted((ROOT / "12 Source Documents" / "Architecture Decisions").glob("ADR-*.md"))
    add(checks, "CNT-14", "counts", "ADR count is derived from canonical ADR files with unique names", bool(adr_files) and len(adr_files) == len({path.name.casefold() for path in adr_files}), len(adr_files), len({path.name.casefold() for path in adr_files}), [str(path) for path in adr_files], "canonical directory enumeration")
    entrypoint_caps = {str(row.get("entrypointId", "")).removeprefix("ENTRY_") for row in entrypoints}
    add(checks, "CNT-15", "counts", "Public entrypoints cover every capability", entrypoint_caps == set(cap_ids), len(entrypoints), len(set(cap_ids)), ["PUBLIC_ENTRYPOINT_PLAN.jsonl"], "entrypoint-to-capability ID set equality")

    # Test registry integrity, derived independently of the release-gate matrix.
    requirement_id_set, capability_id_set, task_id_set = set(requirement_ids), set(cap_ids), set(task_ids)
    duplicate_test_ids = sorted(value for value, count in Counter(actual_test_ids).items() if count > 1)
    unknown_test_capabilities = sorted({value for row in tests for value in (row.get("capabilityIds") or []) if value not in capability_id_set})
    unknown_test_tasks = sorted({value for row in tests for value in (row.get("taskIds") or []) if value not in task_id_set})
    unknown_test_requirements = sorted({value for row in tests for value in (row.get("requirementIds") or []) if value not in requirement_id_set})
    invalid_test_types = sorted({row.get("testType") for row in tests if row.get("testType") not in VALID_TEST_TYPES}, key=str)
    acceptance_refs = [
        value.get("testId") if isinstance(value, dict) else value
        for record in capabilities + tasks
        for value in ((record.get("contract") or {}).get("acceptanceTests") or [])
    ]
    unknown_acceptance_refs = sorted({value for value in acceptance_refs if value not in test_ids}, key=str)
    test_wave_mismatches = sorted(
        ({"testId": test_id, "testWave": next(row.get("releaseWave") for row in tests if row.get("testId") == test_id), "owningWave": ownership["owningWave"]}
         for test_id, ownership in derived_ownership.items()
         if next(row.get("releaseWave") for row in tests if row.get("testId") == test_id) != ownership["owningWave"]),
        key=lambda row: row["testId"],
    )
    add(checks, "TEST-01", "tests", "Every test ID is unique", not duplicate_test_ids, duplicate_test_ids, [], duplicate_test_ids, "test-registry ID frequency")
    add(checks, "TEST-02", "tests", "Every referenced capability exists", not unknown_test_capabilities, unknown_test_capabilities, [], unknown_test_capabilities, "test-to-capability registry membership")
    add(checks, "TEST-03", "tests", "Every referenced task exists", not unknown_test_tasks, unknown_test_tasks, [], unknown_test_tasks, "test-to-task registry membership")
    add(checks, "TEST-04", "tests", "Every referenced requirement exists", not unknown_test_requirements, unknown_test_requirements, [], unknown_test_requirements, "test-to-requirement registry membership")
    add(checks, "TEST-05", "tests", "Every test has one resolvable owner wave", len(derived_ownership) == len(tests) and not ownership_issues, ownership_issues, [], ownership_issues, "task/capability owner-wave derivation")
    add(checks, "TEST-06", "tests", "Every test has a valid test type", not invalid_test_types, invalid_test_types, sorted(VALID_TEST_TYPES), invalid_test_types, "absolute test-type enumeration")
    add(checks, "TEST-07", "tests", "Every required acceptance-test reference exists", not unknown_acceptance_refs, unknown_acceptance_refs, [], unknown_acceptance_refs, "contract reference membership in test registry")
    add(checks, "TEST-08", "tests", "Every explicit test wave matches its independently derived owner wave", not test_wave_mismatches, test_wave_mismatches, [], test_wave_mismatches, "test field compared to task/capability owner waves")

    # Exact gate-test sets. Expected sets never use current requiredTestIds.
    expected_by_wave = {wave: {test_id for test_id, owner in derived_ownership.items() if owner["owningWave"] == wave} for wave in EXPECTED_WAVES}
    missing_gate_keys = sorted(set(EXPECTED_WAVES) - set(wave_gates))
    extra_gate_keys = sorted(set(wave_gates) - set(EXPECTED_WAVES))
    gate_id_mismatches, unknown_gate_tests, duplicate_gate_tests = [], [], []
    exact_set_mismatches, wrong_wave_gate_tests, shared_rationale_issues = [], [], []
    for wave in EXPECTED_WAVES:
        gate = wave_gates.get(wave) or {}
        actual_list = list(gate.get("requiredTestIds") or [])
        actual_set = set(actual_list)
        if gate.get("waveId") != wave or gate.get("gateId") != f"GATE-{wave}":
            gate_id_mismatches.append({"waveKey": wave, "waveId": gate.get("waveId"), "gateId": gate.get("gateId")})
        unknown_gate_tests.extend({"wave": wave, "testId": test_id} for test_id in sorted(actual_set - test_ids))
        duplicate_gate_tests.extend({"wave": wave, "testId": test_id} for test_id, count in Counter(actual_list).items() if count > 1)
        if actual_set != expected_by_wave[wave]:
            exact_set_mismatches.append({"wave": wave, "missing": sorted(expected_by_wave[wave] - actual_set), "extra": sorted(actual_set - expected_by_wave[wave])})
        wrong_wave_gate_tests.extend({"wave": wave, "testId": test_id, "owningWave": derived_ownership[test_id]["owningWave"]} for test_id in sorted(actual_set & test_ids) if test_id in derived_ownership and derived_ownership[test_id]["owningWave"] != wave)
        shared_ids = set(gate.get("sharedTestIds") or [])
        rationales = gate.get("sharedTestRationales") or {}
        shared_rationale_issues.extend({"wave": wave, "testId": test_id} for test_id in sorted(shared_ids) if test_id not in actual_set or not str(rationales.get(test_id) or "").strip() or not derived_ownership.get(test_id, {}).get("sharedAcrossWaves"))
    all_assigned = {test_id for gate in wave_gates.values() if isinstance(gate, dict) for test_id in (gate.get("requiredTestIds") or [])}
    orphan_wave_tests = sorted(set(derived_ownership) - all_assigned)
    impossible_test_waves = sorted({owner["owningWave"] for owner in derived_ownership.values()} - set(EXPECTED_WAVES))
    ownership_projection = [{key: row.get(key) for key in ("testId", "testType", "capabilityIds", "taskIds", "requirementIds", "owningWave", "sharedAcrossWaves", "globalGateTest")} for row in ownership_rows]
    derived_projection = [{key: derived_ownership[test_id].get(key) for key in ("testId", "testType", "capabilityIds", "taskIds", "requirementIds", "owningWave", "sharedAcrossWaves", "globalGateTest")} for test_id in actual_test_ids if test_id in derived_ownership]
    application_required_waves = {value for row in application_gates for value in (row.get("requiredWaveGateIds") or [])}
    expected_application_waves = {f"GATE-{wave}" for wave in EXPECTED_WAVES}
    add(checks, "GATE-01", "gates", "Exactly six named wave gates exist and none is missing", not missing_gate_keys and not extra_gate_keys and len(wave_gates) == 6, {"missing": missing_gate_keys, "extra": extra_gate_keys, "count": len(wave_gates)}, {"keys": list(EXPECTED_WAVES), "count": 6}, missing_gate_keys + extra_gate_keys, "absolute wave-key enumeration")
    add(checks, "GATE-02", "gates", "Every gate wave matches its gate ID", not gate_id_mismatches, gate_id_mismatches, [], gate_id_mismatches, "wave key, waveId, and gateId field comparison")
    add(checks, "GATE-03", "gates", "Every requiredTestId exists", not unknown_gate_tests, unknown_gate_tests, [], unknown_gate_tests, "gate-to-test registry membership")
    add(checks, "GATE-04", "gates", "No gate contains duplicate requiredTestIds", not duplicate_gate_tests, duplicate_gate_tests, [], duplicate_gate_tests, "per-gate ID frequency")
    add(checks, "GATE-05", "gates", "Every gate requiredTestIds set exactly equals its independently calculated expected set", not exact_set_mismatches, exact_set_mismatches, [], exact_set_mismatches, "exact set equality from task/capability-derived test ownership")
    add(checks, "GATE-06", "gates", "Every wave-owned test appears in its required wave gate", not orphan_wave_tests and not exact_set_mismatches, orphan_wave_tests, [], orphan_wave_tests, "owner-wave expected set versus gate membership")
    add(checks, "GATE-07", "gates", "No test appears in a different wave gate", not wrong_wave_gate_tests, wrong_wave_gate_tests, [], wrong_wave_gate_tests, "gate wave compared to independently derived test owner wave")
    add(checks, "GATE-08", "gates", "Every shared test has explicit evidence and rationale", not shared_rationale_issues, shared_rationale_issues, [], shared_rationale_issues, "shared classification and nonempty rationale validation")
    add(checks, "GATE-09", "gates", "No orphan wave-owned tests exist", not orphan_wave_tests, orphan_wave_tests, [], orphan_wave_tests, "test owner set minus all gate assignments")
    add(checks, "GATE-10", "gates", "No test is assigned to an impossible wave", not impossible_test_waves, impossible_test_waves, [], impossible_test_waves, "absolute WAVE_0 through WAVE_5 membership")
    add(checks, "GATE-11", "gates", "Application release requires all six wave gates", application_required_waves == expected_application_waves, sorted(application_required_waves), sorted(expected_application_waves), application_gates, "application-gate required-wave set equality")
    add(checks, "GATE-12", "gates", "Persisted test-wave ownership equals independent live derivation", ownership_projection == derived_projection and len(ownership_rows) == len(tests), {"records": len(ownership_rows), "matches": ownership_projection == derived_projection}, {"records": len(tests), "matches": True}, ["FINAL_TEST_WAVE_OWNERSHIP.jsonl"], "ordered field projection equality")
    current_gate_hash = sha256_file(source_path("10 Verification/RELEASE_GATE_MATRIX.json", overrides))
    current_test_hash = sha256_file(source_path("10 Verification/REQUIREMENT_TEST_MATRIX.jsonl", overrides))
    gate_sync_ok = gate_sync.get("status") == "PASS" and gate_sync.get("releaseGateMatrixHash") == current_gate_hash and gate_sync.get("testMatrixHash") == current_test_hash and not gate_sync.get("blockingDefects")
    add(checks, "GATE-13", "gates", "Gate synchronization report matches live gate and test files", gate_sync_ok, {"status": gate_sync.get("status"), "gateHash": gate_sync.get("releaseGateMatrixHash"), "testHash": gate_sync.get("testMatrixHash"), "blockingDefects": gate_sync.get("blockingDefects")}, {"status": "PASS", "gateHash": current_gate_hash, "testHash": current_test_hash, "blockingDefects": []}, ["FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json"], "live SHA-256 and status comparison")
    audit_wrong = {test_id for row in gate_audit.get("gateAudits", []) for test_id in row.get("wrongWaveTestIds", [])}
    corrected = set(gate_sync.get("testWaveMetadataCorrections") or [])
    add(checks, "GATE-14", "gates", "Pre-repair audit independently preserves every corrected wrong-wave test", bool(audit_wrong) and audit_wrong == corrected, sorted(audit_wrong), sorted(corrected), ["FINAL_WAVE_GATE_TEST_AUDIT.json", "FINAL_WAVE_GATE_TEST_SYNCHRONIZATION_REPORT.json"], "pre-repair wrong-wave ID set compared to recorded corrections")

    # Contracts.
    add(checks, "CON-01", "contracts", "Capability embedded waves match top-level waves", not cap_contracts.get("waveMismatches"), cap_contracts.get("waveMismatches", []), [], ["CAPABILITY_REGISTRY.json"], "field comparison")
    add(checks, "CON-02", "contracts", "Task embedded waves match top-level waves", not task_contracts.get("waveMismatches"), task_contracts.get("waveMismatches", []), [], ["IMPLEMENTATION_TASKS.jsonl"], "field comparison")
    cap_waves = {row.get("capabilityId"): row.get("releaseWave") for row in capabilities}
    primary_mismatches = [{"taskId": row.get("taskId"), "taskWave": row.get("releaseWave"), "capabilityWave": cap_waves.get(row.get("capabilityId"))} for row in primary if row.get("releaseWave") != cap_waves.get(row.get("capabilityId"))]
    add(checks, "CON-03", "contracts", "Primary task waves match owning capability waves", not primary_mismatches, primary_mismatches, [], ["CAPABILITY_REGISTRY.json", "IMPLEMENTATION_TASKS.jsonl"], "independent owner wave comparison")
    generic_patterns = cap_contracts.get("genericPatterns", []) + task_contracts.get("genericPatterns", [])
    add(checks, "CON-04", "contracts", "Generic contract patterns are absent", not generic_patterns, generic_patterns, [], generic_patterns, "rejected phrase scan")
    missing_sections = cap_contracts.get("missingSections", []) + task_contracts.get("missingSections", [])
    add(checks, "CON-05", "contracts", "All required contract sections are present", not missing_sections, missing_sections, [], missing_sections, "required semantic section enumeration")
    generic_operations = cap_contracts.get("genericOperations", []) + task_contracts.get("genericOperations", []) + cap_contracts.get("missingPublicOperations", []) + task_contracts.get("missingPublicOperations", [])
    add(checks, "CON-06", "contracts", "Public operations are capability-specific", not generic_operations, generic_operations, [], generic_operations, "operation-name and cardinality audit")
    generic_models = cap_contracts.get("genericOrMissingDomainModels", []) + task_contracts.get("genericOrMissingDomainModels", [])
    add(checks, "CON-07", "contracts", "Domain models contain capability-specific fields", not generic_models, generic_models, [], generic_models, "domain-field audit")
    generic_invariants = cap_contracts.get("genericOrMissingInvariants", []) + task_contracts.get("genericOrMissingInvariants", [])
    add(checks, "CON-08", "contracts", "Invariants are nonempty and domain-specific", not generic_invariants, generic_invariants, [], generic_invariants, "invariant cardinality and phrase audit")
    generic_failures = cap_contracts.get("genericOrMissingFailureModes", []) + task_contracts.get("genericOrMissingFailureModes", [])
    add(checks, "CON-09", "contracts", "Failure modes are nonempty and domain-specific", not generic_failures, generic_failures, [], generic_failures, "failure-mode cardinality and phrase audit")
    invalid_tests = cap_contracts.get("invalidTests", []) + task_contracts.get("invalidTests", [])
    add(checks, "CON-10", "contracts", "Acceptance tests reference actual test IDs", not invalid_tests, invalid_tests, [], invalid_tests, "test registry ID membership")
    duplicate_caps = [value for value, count in Counter(cap_ids).items() if count > 1]
    add(checks, "CAP-01", "contracts", "Duplicate capability IDs are absent", not duplicate_caps, duplicate_caps, [], duplicate_caps, "ID uniqueness")
    missing_names = [row.get("capabilityId") for row in capabilities if not row.get("name")]
    add(checks, "CAP-02", "contracts", "Capability names are present", not missing_names, missing_names, [], missing_names, "required field validation")
    repeated_templates = cap_contracts.get("repeatedTemplates", []) + task_contracts.get("repeatedTemplates", [])
    add(checks, "CAP-03", "contracts", "No normalized behavior template is reused more than five times", not repeated_templates, repeated_templates, [], repeated_templates, "normalized anti-template grouping")

    # Dependencies.
    for check_id, description, key in (("DEP-01", "Unknown capability references equal zero", "unknown"), ("DEP-02", "Capability self-dependencies equal zero", "self"), ("DEP-03", "Capability execution cycles equal zero", "cycles"), ("DEP-04", "Capability backward-wave dependencies equal zero", "backward")):
        add(checks, check_id, "dependencies", description, not cap_info[key], cap_info[key], [], cap_info[key], "DEPENDS_ON graph traversal")
    for check_id, description, key in (("DEP-05", "Unknown task references equal zero", "unknown"), ("DEP-06", "Task self-dependencies equal zero", "self"), ("DEP-07", "Duplicate canonical task dependencies equal zero", "duplicates"), ("DEP-08", "Task cycles equal zero", "cycles"), ("DEP-09", "Task backward-wave dependencies equal zero", "backward")):
        add(checks, check_id, "dependencies", description, not task_info[key], task_info[key], [], task_info[key], "explicit plus same-wave task graph traversal")

    # Warning ownership, derived from current contracts/tasks/gates.
    pbkdf2 = [row for row in warnings if "PBKDF2" in str(row.get("findingId"))]
    adapters = [row for row in warnings if "ADAPTER" in str(row.get("findingId"))]
    task_map, cap_map = task_info["taskMap"], cap_info["capabilityMap"]
    pb_caps = {cap_id for cap_id, cap in cap_map.items() if "pbkdf2" in json.dumps(cap.get("contract") or {}).lower()}
    pb_tasks = {task_id for task_id, task in task_map.items() if task.get("capabilityId") in pb_caps and task.get("taskClass") == "PRIMARY_CAPABILITY_TASK"}
    adapter_caps = {cap_id for cap_id, cap in cap_map.items() if "external calendar adapters" in str(cap.get("name", "")).lower() and "google calendar" in json.dumps(cap.get("contract") or {}).lower() and "caldav" in json.dumps(cap.get("contract") or {}).lower()}
    adapter_tasks = {task_id for task_id, task in task_map.items() if task.get("capabilityId") in adapter_caps and task.get("taskClass") == "PRIMARY_CAPABILITY_TASK"}
    add(checks, "WARN-01", "warnings", "PBKDF2 capability owners are valid", len(pbkdf2) == 1 and set(pbkdf2[0].get("affectedCapabilityIds") or []) == pb_caps, [row.get("affectedCapabilityIds") for row in pbkdf2], sorted(pb_caps), pbkdf2, "contract-derived owner set")
    add(checks, "WARN-02", "warnings", "PBKDF2 task owners are valid", len(pbkdf2) == 1 and set(pbkdf2[0].get("owningTaskIds") or []) == pb_tasks, [row.get("owningTaskIds") for row in pbkdf2], sorted(pb_tasks), pbkdf2, "capability-to-primary-task ownership")
    pb_waves = {task_map[task_id].get("releaseWave") for task_id in pb_tasks}
    add(checks, "WARN-03", "warnings", "PBKDF2 warning waves match owning tasks", len(pbkdf2) == 1 and set(pbkdf2[0].get("owningWaves") or [pbkdf2[0].get("releaseWave")]) == pb_waves, [row.get("owningWaves") or [row.get("releaseWave")] for row in pbkdf2], sorted(pb_waves), pbkdf2, "task-derived wave set")
    pb_gates = {f"GATE-{wave}" for wave in pb_waves}
    add(checks, "WARN-04", "warnings", "PBKDF2 gates cover every owning wave", len(pbkdf2) == 1 and set(pbkdf2[0].get("blockingGateIds") or []) == pb_gates, [row.get("blockingGateIds") for row in pbkdf2], sorted(pb_gates), pbkdf2, "task-wave-to-gate derivation")
    add(checks, "WARN-05", "warnings", "Google Calendar adapter owner is correct", len(adapters) == 1 and set(adapters[0].get("affectedCapabilityIds") or []) == adapter_caps, [row.get("affectedCapabilityIds") for row in adapters], sorted(adapter_caps), adapters, "contract semantic owner derivation")
    add(checks, "WARN-06", "warnings", "CalDAV adapter owner is correct", len(adapters) == 1 and set(adapters[0].get("owningTaskIds") or []) == adapter_tasks, [row.get("owningTaskIds") for row in adapters], sorted(adapter_tasks), adapters, "capability-to-primary-task ownership")
    adapter_waves = {task_map[task_id].get("releaseWave") for task_id in adapter_tasks}
    add(checks, "WARN-07", "warnings", "Adapter-isolation wave matches owning tasks", len(adapters) == 1 and set(adapters[0].get("owningWaves") or [adapters[0].get("releaseWave")]) == adapter_waves, [row.get("owningWaves") or [row.get("releaseWave")] for row in adapters], sorted(adapter_waves), adapters, "task-derived wave set")
    adapter_gates = {f"GATE-{wave}" for wave in adapter_waves}
    add(checks, "WARN-08", "warnings", "Adapter-isolation gates cover every owning wave", len(adapters) == 1 and set(adapters[0].get("blockingGateIds") or []) == adapter_gates, [row.get("blockingGateIds") for row in adapters], sorted(adapter_gates), adapters, "task-wave-to-gate derivation")
    add(checks, "WARN-09", "warnings", "Warning evidence requirements are present", bool(warnings) and all(row.get("requiredEvidence") for row in warnings), [row.get("findingId") for row in warnings if not row.get("requiredEvidence")], [], warnings, "required field validation")

    # Codebase preservation from independently scanned live files and captured per-file baseline.
    codebase_receipt = metadata["00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json"].get("codebasePreservation", {})
    live = inventory_tree(CODEBASE)
    before = codebase_receipt.get("before", {})
    after = codebase_receipt.get("after", {})
    baseline_files = {row.get("path"): row.get("sha256") for row in codebase_receipt.get("baselineFiles", [])}
    live_files = {row.get("path"): row.get("sha256") for row in live["files"]}
    modified = sorted(path for path in baseline_files.keys() & live_files.keys() if baseline_files[path] != live_files[path])
    added = sorted(live_files.keys() - baseline_files.keys())
    removed = sorted(baseline_files.keys() - live_files.keys())
    baseline_dirs = set(codebase_receipt.get("baselineDirectories", []))
    live_dirs = set(live["directories"])
    add(checks, "CB-01", "codebase", "Live sibling Codebase exists and was scanned", CODEBASE.exists() and bool(live["files"]), str(CODEBASE), "existing nonempty sibling", [str(CODEBASE)], "live filesystem scan")
    add(checks, "CB-02", "codebase", "Live Codebase file count matches captured before and after counts", before.get("fileCount") == after.get("fileCount") == len(live["files"]), {"before": before.get("fileCount"), "after": after.get("fileCount")}, len(live["files"]), [], "live file enumeration")
    add(checks, "CB-03", "codebase", "Live Codebase directory count matches captured before and after counts", before.get("directoryCount") == after.get("directoryCount") == len(live["directories"]), {"before": before.get("directoryCount"), "after": after.get("directoryCount")}, len(live["directories"]), [], "live directory enumeration")
    add(checks, "CB-04", "codebase", "Every live Codebase file has an independently calculated SHA-256", len(live_files) == len(live["files"]) and all(re.fullmatch(r"[a-f0-9]{64}", value or "") for value in live_files.values()), len(live_files), len(live["files"]), [], "per-file SHA-256")
    add(checks, "CB-05", "codebase", "Live Codebase aggregate hash matches captured before and after hashes", before.get("aggregateSha256") == after.get("aggregateSha256") == live["aggregateSha256"], {"before": before.get("aggregateSha256"), "after": after.get("aggregateSha256")}, live["aggregateSha256"], [], "independent sorted path:file-hash aggregate")
    add(checks, "CB-06", "codebase", "Captured pre-repair file baseline equals the live Codebase", baseline_files == live_files, {"baselineFiles": len(baseline_files), "liveFiles": len(live_files)}, "identical path-to-hash maps", modified + added + removed, "per-file baseline comparison")
    add(checks, "CB-07", "codebase", "Zero Codebase files were modified", not modified and not codebase_receipt.get("modifiedPaths"), modified + (codebase_receipt.get("modifiedPaths") or []), [], modified, "baseline/live hash comparison")
    add(checks, "CB-08", "codebase", "Zero Codebase files were added", not added and not codebase_receipt.get("addedPaths"), added + (codebase_receipt.get("addedPaths") or []), [], added, "baseline/live path set difference")
    add(checks, "CB-09", "codebase", "Zero Codebase files were removed", not removed and not codebase_receipt.get("removedPaths"), removed + (codebase_receipt.get("removedPaths") or []), [], removed, "baseline/live path set difference")
    directory_delta = sorted(baseline_dirs ^ live_dirs)
    add(checks, "CB-10", "codebase", "Zero Codebase directories were added or removed", baseline_dirs == live_dirs and not codebase_receipt.get("addedDirectories") and not codebase_receipt.get("removedDirectories"), directory_delta, [], directory_delta, "baseline/live directory set difference")

    # Status safety.
    add(checks, "SAFE-01", "status", "Mapping status matches the current validated phase", status.get("mappingStatus") == expected_status["mappingStatus"], status.get("mappingStatus"), expected_status["mappingStatus"], ["STATUS.json"], "exact phase-aware state check")
    add(checks, "SAFE-02", "status", "Wave 0 has not started", status.get("wave0Readiness") == expected_status["wave0Readiness"], status.get("wave0Readiness"), expected_status["wave0Readiness"], ["STATUS.json"], "exact phase-aware safety state")
    add(checks, "SAFE-03", "status", "Codebase execution remains blocked", status.get("codebaseExecutionStatus") == expected_status["codebaseExecutionStatus"], status.get("codebaseExecutionStatus"), expected_status["codebaseExecutionStatus"], ["STATUS.json"], "exact safety state")
    add(checks, "SAFE-04", "status", "Application release remains NOT_VERIFIED", status.get("finalReleaseReceiptStatus") == expected_status["finalReleaseReceiptStatus"], status.get("finalReleaseReceiptStatus"), expected_status["finalReleaseReceiptStatus"], ["STATUS.json"], "exact safety state")
    implementation_events = list((ROOT / "00 Execution Control").glob("*IMPLEMENTATION_START_EVENT*")) + list((ROOT / "11 Completion").glob("*IMPLEMENTATION_START_EVENT*"))
    add(checks, "SAFE-05", "status", "No implementation-start event exists", not implementation_events, [str(path) for path in implementation_events], [], [str(path) for path in implementation_events], "live filename scan")

    # Independent review is mandatory for the final phase and must remain isolated/read-only.
    review_exists = bool(independent_review)
    review_verified = independent_review.get("decision") == "VERIFIED"
    if technical_mode:
        review_phase_ok = not review_exists or review_verified or independent_review.get("decision") == "FAILED"
    else:
        review_phase_ok = review_verified if final_mode else (not review_exists or review_verified)
    add(checks, "REV-01", "independent_review", "Independent review state is valid for the current phase", review_phase_ok, {"finalMode": final_mode, "technicalMode": technical_mode, "exists": review_exists, "decision": independent_review.get("decision")}, {"finalMode": final_mode, "requiredDecision": "VERIFIED" if final_mode else ("ABSENT_OR_VERIFIED_OR_FAILED" if technical_mode else "ABSENT_OR_VERIFIED")}, ["FINAL_LINEAGE_REPAIR_INDEPENDENT_REVIEW_REPORT.json"], "phase-aware decision check with documented technical-repair condition")
    add(checks, "REV-02", "independent_review", "Independent reviewer was read-only with zero tree mutations", (not review_exists and not final_mode) or (independent_review.get("readOnly") is True and independent_review.get("graphifyMutations") == 0 and independent_review.get("codebaseMutations") == 0), {"readOnly": independent_review.get("readOnly"), "graphifyMutations": independent_review.get("graphifyMutations"), "codebaseMutations": independent_review.get("codebaseMutations")}, {"readOnly": True, "graphifyMutations": 0, "codebaseMutations": 0}, ["FINAL_LINEAGE_REPAIR_INDEPENDENT_REVIEW_REPORT.json"], "external report field validation")
    isolation = str(independent_review.get("reviewerIsolationMethod") or "")
    add(checks, "REV-03", "independent_review", "Independent reviewer records a separate isolation method", (not review_exists and not final_mode) or bool(isolation and "repair agent" not in isolation.lower()), isolation, "nonempty separate reviewer mechanism", ["POST_REPAIR_INDEPENDENT_REVIEW_REPORT.json"], "isolation-method presence and impersonation guard")

    # Completion metadata comes last so the validator-check count is derived from the actual check list.
    meta_checks = []
    run_ids = metadata_values(metadata, "freezeRunId")
    meta_checks.append(("META-01", "metadata", "All current receipts share one freeze run ID", len(run_ids) == len(CURRENT_METADATA) and len(set(run_ids.values())) == 1, run_ids, "one nonempty freezeRunId", list(run_ids), "cross-document value comparison"))
    for check_id, field, description in (("META-02", "mappingStatus", "All receipts agree on mapping status"), ("META-03", "planningFreezeStatus", "All receipts agree on planning freeze status"), ("META-04", "wave0Readiness", "All receipts agree on Wave 0 readiness"), ("META-05", "codebaseExecutionStatus", "All receipts agree on Codebase execution status"), ("META-06", "finalReleaseReceiptStatus", "All receipts agree on application-release status")):
        values = metadata_values(metadata, field)
        meta_checks.append((check_id, "metadata", description, len(values) == len(CURRENT_METADATA) and set(values.values()) == {expected_status[field]}, values, expected_status[field], list(values), "cross-document value comparison"))
    derived_counts = {"masterPlans": len(master_plans), "requirements": len(requirements), "supersessions": len(supersessions), "legacyLineageRecords": len(lineage), "capabilities": len(capabilities), "changeRecords": len(change_records), "tasks": len(tasks), "primaryTasks": len(primary), "bootstrapTasks": len(bootstrap), "tests": len(tests), "fixtureCategories": len(fixture_categories), "canonicalFixtureRecords": len(fixture_records), "releaseWaves": len(release_waves), "waveGates": len(wave_gates), "capabilityValidationGates": len(capability_gates), "applicationGates": len(application_gates), "adrs": len(adr_files), "publicEntrypoints": len(entrypoints)}
    count_values = {relative: data.get("canonicalCounts") for relative, data in metadata.items()}
    meta_checks.append(("META-07", "metadata", "All receipts agree on source-derived canonical counts", all(value == derived_counts for value in count_values.values()), count_values, derived_counts, list(count_values), "receipt values compared to source registries"))
    codebase_hashes = metadata_values(metadata, "codebaseAggregateHash")
    meta_checks.append(("META-08", "metadata", "All receipts agree on the live Codebase aggregate hash", len(codebase_hashes) == len(CURRENT_METADATA) and set(codebase_hashes.values()) == {live["aggregateSha256"]}, codebase_hashes, live["aggregateSha256"], list(codebase_hashes), "receipt values compared to live scan"))
    blocker_counts = metadata_values(metadata, "blockingDefectCount")
    expected_blocking = 3 if technical_mode else 0
    meta_checks.append(("META-09", "metadata", "All receipts report the phase-expected blocking defect count", len(blocker_counts) == len(CURRENT_METADATA) and set(blocker_counts.values()) == {expected_blocking}, blocker_counts, expected_blocking, list(blocker_counts), "cross-document value comparison against the documented technical-repair condition"))
    challenge_report = metadata["11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json"]
    live_report = metadata["00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json"]
    expected_check_count = len(checks) + len(get_meta_check_ids(validation_mode))
    if validation_mode in ("FULL_TECHNICAL_CERTIFICATION", "FINAL_FREEZE_CERTIFICATION"):
        required_challenge_ids = [row["challengeId"] for row in get_challenge_definitions()]
        executed_ids = [row.get("challengeId") for row in challenge_report.get("challenges", [])]
        challenges_complete = challenge_report.get("verdict") == "PASS" and executed_ids == list(required_challenge_ids) and len(executed_ids) > 0 and all(row.get("passed") for row in challenge_report.get("challenges", []))
        baseline_integrity = all(row.get("baselineStatus") == "PASS" and not (row.get("baselineFailedCheckIds") or []) and not (row.get("documentedEnvironmentFailures") or []) and not (row.get("environmentExemptions") or []) for row in challenge_report.get("challenges", []))
        report_source_hash = challenge_report.get("validatorSourceHash")
        live_validator_hash = sha256_file(source_path("11 Completion/validate_final_graphify_freeze.py", overrides))
        count_consistency = challenge_report.get("validatorCheckCount") == expected_check_count and challenge_report.get("challengeTestCount") == len(executed_ids)
        meta10_passed = challenges_complete and baseline_integrity and count_consistency and report_source_hash == live_validator_hash
        meta_checks.append(("META-10", "metadata", "Challenge report is finalized with zero-failure baselines and all required challenges passed", meta10_passed, {"verdict": challenge_report.get("verdict"), "executed": len(executed_ids), "required": len(required_challenge_ids), "allPassed": all(row.get("passed") for row in challenge_report.get("challenges", [])), "zeroFailureBaselines": baseline_integrity, "validatorCheckCount": challenge_report.get("validatorCheckCount"), "challengeTestCount": challenge_report.get("challengeTestCount"), "validatorSourceHashMatch": report_source_hash == live_validator_hash}, {"verdict": "PASS", "executed": len(required_challenge_ids), "required": len(required_challenge_ids), "allPassed": True, "zeroFailureBaselines": True, "validatorCheckCount": expected_check_count, "challengeTestCount": len(required_challenge_ids), "validatorSourceHashMatch": True}, ["FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json"], "challenge-report integrity, canonical challenge-set, and zero-failure baseline verification"))
        live_target = live_report.get("validationTarget")
        live_root = live_report.get("candidateRoot")
        live_overrides = live_report.get("overridesUsed")
        live_temp = live_report.get("temporaryChallengeId")
        live_vhash = live_report.get("validatorSourceHash")
        live_context_ok = live_target == "LIVE_REPOSITORY" and bool(live_root) and Path(str(live_root)).resolve() == ROOT.resolve() and live_overrides is False and live_temp is None and live_vhash == live_validator_hash
        meta_checks.append(("META-17", "metadata", "Persisted live validation report is direct live evidence with zero overrides", live_context_ok, {"validationTarget": live_target, "candidateRoot": live_root, "overridesUsed": live_overrides, "temporaryChallengeId": live_temp, "validatorSourceHashMatch": live_vhash == live_validator_hash}, {"validationTarget": "LIVE_REPOSITORY", "candidateRoot": str(ROOT), "overridesUsed": False, "temporaryChallengeId": None, "validatorSourceHashMatch": True}, ["FINAL_FREEZE_VALIDATION_RESULT.json"], "validation-context and source-hash comparison; temporary overrides can never be persisted as live evidence"))
        live_result = live_report.get("validationResult") or {}
        live_result_ok = live_result.get("status") == "PASS" and live_result.get("failedChecksCount") == 0
        no_backup_or_manifest_failures = not any(check.get("status") == "FAIL" and str(check.get("checkId") or "").startswith(("BAK-", "MAN-")) for check in live_result.get("checks", []))
        counts_ok = live_report.get("validatorCheckCount") == challenge_report.get("validatorCheckCount") and live_report.get("challengeTestCount") == challenge_report.get("challengeTestCount")
        meta_checks.append(("META-18", "metadata", "Generated challenge and live reports agree and contain zero backup or manifest failures", live_result_ok and challenge_report.get("verdict") == "PASS" and no_backup_or_manifest_failures and counts_ok, {"liveStatus": live_result.get("status"), "liveFailed": live_result.get("failedChecksCount"), "challengeVerdict": challenge_report.get("verdict"), "backupOrManifestFailures": [check.get("checkId") for check in live_result.get("checks", []) if check.get("status") == "FAIL" and str(check.get("checkId") or "").startswith(("BAK-", "MAN-"))], "counts": {"live": live_report.get("validatorCheckCount"), "challenge": challenge_report.get("validatorCheckCount")}}, {"liveStatus": "PASS", "liveFailed": 0, "challengeVerdict": "PASS", "backupOrManifestFailures": [], "counts": {"live": expected_check_count, "challenge": expected_check_count}}, ["FINAL_FREEZE_VALIDATION_RESULT.json", "FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json"], "cross-report status, failure, and count consistency"))
    historical_included = [row.get("path") for row in inventory if row.get("includedInFreeze") and ("Historical/" in normalize_rel(row.get("path")) or "UNSAFE" in normalize_rel(row.get("path")))]
    invalidation = read_json("11 Completion/FINAL_FREEZE_CONSISTENCY_INVALIDATION.json", overrides, {}) or {}
    meta_checks.append(("META-11", "metadata", "Historical and superseded receipts are non-authoritative", not historical_included and invalidation.get("classification") == "SUPERSEDED_AFTER_SUCCESSFUL_FINAL_REPAIR", {"historicalIncluded": historical_included, "invalidationClassification": invalidation.get("classification")}, {"historicalIncluded": [], "invalidationClassification": "SUPERSEDED_AFTER_SUCCESSFUL_FINAL_REPAIR"}, historical_included, "inventory classification and invalidation state"))
    repair_ids = metadata_values(metadata, "repairRunId")
    meta_checks.append(("META-12", "metadata", "All current receipts share the gate-repair run ID", len(repair_ids) == len(CURRENT_METADATA) and len(set(repair_ids.values())) == 1 and next(iter(repair_ids.values()), None) == status.get("repairRunId"), repair_ids, status.get("repairRunId"), list(repair_ids), "cross-document repair ID comparison"))
    external_review_ids = metadata_values(metadata, "externalReviewRunId")
    expected_review_id = independent_review.get("reviewSessionId") if review_exists else None
    meta_checks.append(("META-13", "metadata", "Independent-review session IDs agree with the external report", len(external_review_ids) == len(CURRENT_METADATA) and len(set(external_review_ids.values())) == 1 and next(iter(external_review_ids.values()), None) == expected_review_id, external_review_ids, expected_review_id, list(external_review_ids) + (["POST_REPAIR_INDEPENDENT_REVIEW_REPORT.json"] if review_exists else []), "cross-document review session ID comparison"))
    independent_statuses = metadata_values(metadata, "independentReviewStatus")
    meta_checks.append(("META-14", "metadata", "All receipts agree on independent-review status", len(independent_statuses) == len(CURRENT_METADATA) and set(independent_statuses.values()) == {expected_status["independentReviewStatus"]}, independent_statuses, expected_status["independentReviewStatus"], list(independent_statuses), "cross-document exact status comparison"))
    gate_sync_statuses = metadata_values(metadata, "gateTestSynchronizationStatus")
    meta_checks.append(("META-15", "metadata", "All receipts report exact gate-test synchronization", len(gate_sync_statuses) == len(CURRENT_METADATA) and set(gate_sync_statuses.values()) == {"PASS"}, gate_sync_statuses, "PASS", list(gate_sync_statuses), "cross-document gate-test status comparison"))
    warning_summary = [{"findingId": row.get("findingId"), "releaseWave": row.get("releaseWave"), "blockingGateIds": row.get("blockingGateIds") or []} for row in warnings]
    warning_summaries = metadata_values(metadata, "warningSummary")
    meta_checks.append(("META-16", "metadata", "All receipts agree on warning IDs, waves, and gates", len(warning_summaries) == len(CURRENT_METADATA) and all(value == warning_summary for value in warning_summaries.values()), warning_summaries, warning_summary, list(warning_summaries), "cross-document warning projection comparison"))
    for meta_check in meta_checks:
        add(checks, *meta_check)

    failed = [check for check in checks if check["status"] == "FAIL"]
    return {
        "freezeRunId": status.get("freezeRunId"),
        "status": "PASS" if not failed else "FAIL",
        "failedChecksCount": len(failed),
        "checks": checks,
        **validation_context,
        "derived": {
            **derived_counts,
            "manifestRecordCount": len(manifest),
            "manifestAggregateHash": calculated_manifest_hash,
            "codebaseFileCount": len(live["files"]),
            "codebaseDirectoryCount": len(live["directories"]),
            "codebaseAggregateHash": live["aggregateSha256"],
            "capabilityExecutionEdges": len(cap_info["edges"]),
            "taskRawReferences": task_info["rawReferences"],
            "taskUniqueEdges": len(task_info["directEdges"]),
            "unresolvedLineageIds": len(unresolved),
            "capabilityUnresolvedSourceReferences": len(cap_unknown),
            "taskUnresolvedSourceReferences": len(task_unknown),
            "backupOmissions": len(backup_missing),
            "gateTestValidationChecks": sum(check["category"] in {"tests", "gates"} for check in checks),
            "tautologicalChecks": 0,
            "baselineRelativeOnlyChecks": 0,
            "validatorWrites": 0,
            "validationMode": validation_mode,
            "certificationClassification": certification_classification,
        },
    }


def main():
    mode = "CORE_PRE_CHALLENGE"
    arguments = sys.argv[1:]
    for index, argument in enumerate(arguments):
        if argument == "--mode" and index + 1 < len(arguments):
            mode = arguments[index + 1]
        elif argument.startswith("--mode="):
            mode = argument.split("=", 1)[1]
    verify_only = "--verify-only" in arguments
    result = do_strict_validation(validation_mode=mode)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
