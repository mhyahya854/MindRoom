"""Read-only defect reproduction for the final MindRoom Graphify repair."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
REPORT = ROOT / "11 Completion" / "FINAL_REPAIR_REPRODUCTION_REPORT.json"


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def read_jsonl(relative: str):
    return [json.loads(line) for line in (ROOT / relative).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wave_number(value):
    match = re.search(r"\d+", str(value or ""))
    return int(match.group()) if match else None


def cycles(adjacency):
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


def flattened_operations(contract):
    operations = [value if isinstance(value, str) else value.get("name") or value.get("operation") or "" for value in contract.get("publicOperations", [])]
    for interface in contract.get("publicInterfaces", []):
        if isinstance(interface, dict):
            operations.extend(interface.get("methods", []))
    return [str(value).strip() for value in operations if str(value).strip()]


def normalized_contract(contract):
    selected = {key: contract.get(key) for key in (
        "purpose", "scope", "ownedPackageOrModule", "runtimeOwner", "publicOperations",
        "domainModels", "persistentState", "inputs", "outputs", "invariants", "failureModes",
        "recoveryBehavior", "offlineBehavior", "securityAndPrivacyConstraints",
        "crossPlatformConstraints", "dependencies", "acceptanceTests", "blockingGates",
        "behaviorToAdd", "publicInterfaces", "storageContract", "failureContract",
    )}
    text = json.dumps(selected, sort_keys=True, ensure_ascii=False).lower()
    text = re.sub(r"mr-(?:cap|impl|req|test|change)-[a-z0-9-]+", "<id>", text)
    text = re.sub(r"wave[_ -]?\d+", "<wave>", text)
    text = re.sub(r"[a-z]:[/\\][^\" ]+|(?:codebase|graphify)/[^\" ]+", "<path>", text)
    text = re.sub(r"\b\d+\b", "<n>", text)
    return text


def contract_metrics(records, owner_key):
    result = defaultdict(list)
    templates = defaultdict(list)
    generic_ops = {"initialize()", "execute()", "getstatus()"}
    for record in records:
        owner = record.get(owner_key)
        contract = record.get("contract") or record.get("implementationContract") or {}
        operations = [op.lower() for op in flattened_operations(contract)]
        if operations and set(operations) <= generic_ops:
            result["genericInitializeExecuteStatusOnly"].append(owner)
        if "implement planned mindroom capability scope" in json.dumps(contract, ensure_ascii=False).lower():
            result["genericPlannedCapabilityScope"].append(owner)
        if record.get("releaseWave") != contract.get("releaseWave"):
            result["waveMismatches"].append({owner_key: owner, "topLevel": record.get("releaseWave"), "embedded": contract.get("releaseWave")})
        required = {
            "publicOperations": operations,
            "domainModels": contract.get("domainModels"),
            "invariants": contract.get("invariants"),
            "failureModes": contract.get("failureModes") or contract.get("failureContract"),
            "persistentState": contract.get("persistentState") or contract.get("storageContract"),
            "platformRuntimeOwnership": contract.get("runtimeOwner") or contract.get("targetOwner"),
        }
        for field, value in required.items():
            if not value:
                result[f"missing{field[0].upper()}{field[1:]}"] .append(owner)
        templates[normalized_contract(contract)].append(owner)
    result["normalizedDuplicateGroups"] = [owners for owners in templates.values() if len(owners) > 1]
    result["highFrequencyNormalizedDuplicateGroups"] = [owners for owners in templates.values() if len(owners) > 5]
    return dict(result)


def task_dependency_metrics(tasks):
    task_map = {task["taskId"]: task for task in tasks}
    adjacency, edges, unknown, self_refs, duplicates = defaultdict(list), [], set(), [], []
    raw = 0
    for task in tasks:
        task_id, seen = task["taskId"], set()
        refs = [ref for field in ("dependencies", "prerequisites") for ref in (task.get(field) or []) if isinstance(ref, str)]
        raw += len(refs)
        for ref in refs:
            ref = ref.strip()
            if ref in seen:
                duplicates.append({"taskId": task_id, "dependency": ref})
                continue
            seen.add(ref)
            if ref == task_id:
                self_refs.append({"taskId": task_id, "dependency": ref})
            elif ref not in task_map:
                unknown.add(ref)
            else:
                edges.append((task_id, ref))
                adjacency[task_id].append(ref)
    backward = [{"taskId": source, "dependency": target} for source, target in edges if wave_number(task_map[target].get("releaseWave")) > wave_number(task_map[source].get("releaseWave"))]
    return {"rawReferences": raw, "uniqueEdges": len(set(edges)), "unknownReferences": sorted(unknown), "selfDependencies": self_refs, "duplicateCanonicalReferences": duplicates, "cycles": cycles(adjacency), "backwardWaveDependencies": backward}


def capability_dependency_metrics(capabilities, graph):
    cap_map = {cap["capabilityId"]: cap for cap in capabilities}
    execution_relations = {"DEPENDS_ON", "EXECUTION_DEPENDENCY", "EXECUTION"}
    adjacency, edges, unknown, self_refs = defaultdict(list), [], set(), []
    relation_types = Counter()
    for row in graph.get("edges", []):
        relation = row.get("relation") or row.get("type") or "UNKNOWN"
        relation_types[relation] += 1
        if relation not in execution_relations:
            continue
        source, target = row.get("sourceNodeId") or row.get("source"), row.get("targetNodeId") or row.get("target")
        if source not in cap_map: unknown.add(source)
        if target not in cap_map: unknown.add(target)
        if source == target: self_refs.append(source)
        if source and target:
            edges.append((source, target)); adjacency[source].append(target)
    backward = [{"capabilityId": source, "dependency": target} for source, target in edges if source in cap_map and target in cap_map and wave_number(cap_map[target].get("releaseWave")) > wave_number(cap_map[source].get("releaseWave"))]
    return {"rawRecords": len(graph.get("edges", [])), "relationTypes": dict(relation_types), "uniqueExecutionEdges": len(set(edges)), "unknownReferences": sorted(value for value in unknown if value), "selfDependencies": self_refs, "cycles": cycles(adjacency), "backwardWaveDependencies": backward}


def metadata_conflicts(paths):
    aliases = {
        "planningStatus": ("planningFreezeStatus", "planningStatus", "mappingStatus"),
        "applicationReleaseStatus": ("applicationReleaseStatus", "finalReleaseReceiptStatus"),
        "manifestAggregateHash": ("manifestAggregateHash", "frozenManifestAggregateSha256"),
        "codebaseAggregateHash": ("codebaseAggregateHash", "aggregateHash", "codebaseManifestHash"),
        "releaseWaveCount": ("releaseWaveCount",),
        "validatorCheckCount": ("validatorCheckCount", "validationCheckCount"),
        "challengeTestCount": ("challengeTestCount", "challengesExecuted"),
        "blockingDefectCount": ("blockingDefectCount", "blockerCount"),
    }
    keys = ("freezeRunId", "mappingStatus", "independentReviewStatus", "wave0Readiness", "codebaseExecutionStatus")
    values = defaultdict(dict)
    for relative in paths:
        data = read_json(relative)
        for field in keys:
            if field in data: values[field][relative] = data[field]
        for field, candidates in aliases.items():
            for candidate in candidates:
                if candidate in data:
                    values[field][relative] = data[candidate]; break
            if field == "releaseWaveCount" and isinstance(data.get("counts"), dict) and "releaseWaves" in data["counts"]:
                values[field][relative] = data["counts"]["releaseWaves"]
    return {field: mapping for field, mapping in values.items() if len({json.dumps(value, sort_keys=True) for value in mapping.values()}) > 1}


def main():
    capabilities = read_json("03 Capability Map/CAPABILITY_REGISTRY.json")["capabilities"]
    tasks = read_jsonl("09 Implementation/IMPLEMENTATION_TASKS.jsonl")
    cap_contracts = contract_metrics(capabilities, "capabilityId")
    task_contracts = contract_metrics(tasks, "taskId")
    cap_map = {cap["capabilityId"]: cap for cap in capabilities}
    primary_wave_mismatches = [{"taskId": task["taskId"], "capabilityId": task.get("capabilityId"), "taskWave": task.get("releaseWave"), "capabilityWave": cap_map.get(task.get("capabilityId"), {}).get("releaseWave")} for task in tasks if task.get("taskClass") == "PRIMARY_CAPABILITY_TASK" and task.get("releaseWave") != cap_map.get(task.get("capabilityId"), {}).get("releaseWave")]
    manifest = read_jsonl("00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl")
    manifest_paths = [str(row.get("path", "")).replace("\\", "/") for row in manifest]
    current_hashes = []
    missing, mismatched = [], []
    for row, relative in zip(manifest, manifest_paths):
        path = ROOT / relative
        if not path.exists(): missing.append(relative)
        elif sha256_file(path) != row.get("sha256"): mismatched.append(relative)
        current_hashes.append((relative, row.get("sha256", "")))
    aggregate = hashlib.sha256("\n".join(f"{path}:{digest}" for path, digest in sorted(current_hashes)).encode()).hexdigest()
    inventory = read_jsonl("00 Execution Control/FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl")
    inventory_included = {str(row.get("path", "")).replace("\\", "/") for row in inventory if row.get("includedInFreeze")}
    metadata_paths = [
        "00 Execution Control/STATUS.json", "00 Execution Control/FINAL_AUTHORITY_INDEX.json",
        "00 Execution Control/GRAPHIFY_MAPPING_RECEIPT.json", "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
        "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json", "11 Completion/GRAPHIFY_MAPPING_RECEIPT.json",
        "11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json", "11 Completion/FINAL_SYNCHRONIZATION_REPORT.json",
        "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
    ]
    stored_aggregates = {}
    for relative in metadata_paths:
        text = (ROOT / relative).read_text(encoding="utf-8-sig")
        stored_aggregates[relative] = sorted(set(re.findall(r"\b[a-f0-9]{64}\b", text.lower())))
    validator_source = (ROOT / "11 Completion" / "validate_final_graphify_freeze.py").read_text(encoding="utf-8")
    report = {
        "repairRunId": "mindroom-graphify-final-repair-20260801-081542",
        "phase": "PRE_REPAIR_REPRODUCTION",
        "sourcePolicy": "Calculated from live registries and files; no completion receipt is used as its own expected evidence.",
        "capabilityRegistry": {
            "capabilityCount": len(capabilities),
            "duplicateCapabilityIds": [item for item, count in Counter(cap["capabilityId"] for cap in capabilities).items() if count > 1],
            "missingCapabilityNames": [cap.get("capabilityId") for cap in capabilities if not cap.get("name")],
            "topLevelReleaseWaves": dict(Counter(cap.get("releaseWave") for cap in capabilities)),
            "embeddedContractReleaseWaves": dict(Counter((cap.get("contract") or {}).get("releaseWave") for cap in capabilities)),
            **cap_contracts,
        },
        "taskRegistry": {
            "totalTasks": len(tasks),
            "primaryTasks": sum(task.get("taskClass") == "PRIMARY_CAPABILITY_TASK" for task in tasks),
            "bootstrapTasks": sum(task.get("taskClass") == "BOOTSTRAP_TASK" for task in tasks),
            "otherSupportTasks": sum(task.get("taskClass") not in {"PRIMARY_CAPABILITY_TASK", "BOOTSTRAP_TASK"} for task in tasks),
            "duplicateTaskIds": [item for item, count in Counter(task["taskId"] for task in tasks).items() if count > 1],
            "unknownCapabilityOwners": sorted({task.get("capabilityId") for task in tasks if task.get("capabilityId") not in cap_map}),
            "topLevelReleaseWaves": dict(Counter(task.get("releaseWave") for task in tasks)),
            "embeddedContractReleaseWaves": dict(Counter((task.get("contract") or {}).get("releaseWave") for task in tasks)),
            "capabilityTaskWaveMismatches": primary_wave_mismatches,
            **task_contracts,
            "dependencies": task_dependency_metrics(tasks),
        },
        "capabilityDependencies": capability_dependency_metrics(capabilities, read_json("05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json")),
        "receiptConflicts": metadata_conflicts(metadata_paths),
        "manifest": {
            "recordCount": len(manifest), "missingFiles": missing, "mismatchedHashes": mismatched,
            "selfReference": [path for path in manifest_paths if path.endswith("FROZEN_ARTIFACT_MANIFEST.jsonl")],
            "duplicateNormalizedPaths": [item for item, count in Counter(path.lower() for path in manifest_paths).items() if count > 1],
            "inventoryMismatches": sorted(set(manifest_paths) - inventory_included),
            "currentAggregateManifestHash": aggregate, "storedHashesByReceipt": stored_aggregates,
        },
        "validatorAudit": {
            "writesDetected": bool(re.search(r"write_text|write_bytes|open\([^\n]+['\"]w|json\.dump", validator_source)),
            "tautologicalOrPrepopulatedChecksDetected": [line.strip() for line in validator_source.splitlines() if "True, True, True" in line or "actual, actual" in line or "baselineHash'), codebase_receipt.get('baselineHash')" in line],
            "hardCodedWarningEvidenceDetected": [line.strip() for line in validator_source.splitlines() if "WAVE_1" in line or "WAVE_4" in line or "WARN-05" in line],
        },
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "capabilityGeneric": len(cap_contracts.get("genericPlannedCapabilityScope", [])), "taskGeneric": len(task_contracts.get("genericPlannedCapabilityScope", [])), "receiptConflictFields": len(report["receiptConflicts"]), "manifestMismatches": len(mismatched)}, indent=2))


if __name__ == "__main__":
    main()
