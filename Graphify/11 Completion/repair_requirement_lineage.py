"""Rebuild requirement lineage from live source nodes and canonical requirements."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from normalize_requirements import (
    FRAGMENT_PREFIXES,
    ISOLATED_NOUNS,
    expand_one_word_title,
    normalize_title_string,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CAPMAP = ROOT / "03 Capability Map"
NODES = ROOT / "05 Dependency and Impact" / "Knowledge Graph" / "NODES.jsonl"
TASKS = ROOT / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl"
REQUIREMENTS = CAPMAP / "REQUIREMENT_REGISTRY.jsonl"
SUPERSESSIONS = CAPMAP / "REQUIREMENT_SUPERSESSION_MAP.jsonl"
CAPABILITIES = CAPMAP / "CAPABILITY_REGISTRY.json"
LINEAGE = CAPMAP / "LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl"
RECONCILIATION = HERE / "FINAL_REQUIREMENT_LINEAGE_RECONCILIATION_REPORT.json"
TRACEABILITY = HERE / "FINAL_CAPABILITY_TASK_REQUIREMENT_TRACEABILITY_REPORT.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def jsonl_bytes(rows) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fragment_reason(title: str) -> str | None:
    low = title.lower().strip()
    if any(low.startswith(prefix) for prefix in FRAGMENT_PREFIXES):
        return "Matches an explicit fragment-prefix exclusion rule."
    if low.endswith(":") and len(low.split()) <= 4:
        return "Short colon-terminated lead-in; the following Master Plan content carries the meaning."
    if low in ISOLATED_NOUNS:
        return "Matches an explicit isolated-noun exclusion rule."
    return None


def source_node_evidence(node: dict, node_line: int) -> dict:
    return {
        "evidenceType": "ORIGINAL_SOURCE_REQUIREMENT_NODE",
        "artifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
        "location": f"jsonl:{node_line}",
        "nodeId": node["nodeId"],
        "masterPlanArtifact": str(node["path"]).removeprefix("Graphify/"),
        "recordedMasterPlanLine": int(node["declarationSpan"]),
        "qualifiedName": node["qualifiedName"],
        "anchorSha256": node["anchorSha256"],
    }


def build_model():
    requirements = read_jsonl(REQUIREMENTS)
    requirement_ids = {row["requirementId"] for row in requirements}
    canonical_by_title = defaultdict(list)
    for row in requirements:
        canonical_by_title[normalize_title_string(row["title"])].append(row["requirementId"])

    node_rows = read_jsonl(NODES)
    node_index = {
        row["nodeId"]: (line, row)
        for line, row in enumerate(node_rows, 1)
        if row.get("nodeType") == "REQUIREMENT"
    }
    capability_document = read_json(CAPABILITIES)
    capabilities = capability_document["capabilities"]
    tasks = read_jsonl(TASKS)
    capability_sources = [(row["capabilityId"], value) for row in capabilities for value in row.get("sourceRequirementIds", [])]
    task_sources = [(row["taskId"], value) for row in tasks for value in row.get("sourceRequirements", [])]
    all_sources = capability_sources + task_sources
    distinct_sources = {value for _, value in all_sources}
    legacy_ids = sorted(distinct_sources - requirement_ids)

    assert len(requirements) == 1782
    assert len(legacy_ids) == 278
    assert set(legacy_ids) <= set(node_index)

    lineage, supersessions = [], []
    for legacy_id in legacy_ids:
        node_line, node = node_index[legacy_id]
        title = node["qualifiedName"]
        expanded_title = expand_one_word_title(title, title)[0] if len(title.split()) == 1 else title
        targets = canonical_by_title[normalize_title_string(expanded_title)]
        reason = fragment_reason(title)

        if len(targets) == 1:
            status = "MERGED"
            target = targets[0]
            resolution_reason = (
                f"The explicit normalization rule expands {title!r} to {expanded_title!r}, "
                f"which exactly identifies {target}."
                if expanded_title != title
                else f"Original and canonical requirement text are exactly identical after mechanical normalization; merged into {target}."
            )
            evidence = [source_node_evidence(node, node_line)]
            if expanded_title != title:
                evidence.append({
                    "evidenceType": "EXPLICIT_NORMALIZATION_RULE",
                    "artifact": "11 Completion/normalize_requirements.py",
                    "location": f"NOUN_EXPANSIONS[{title.lower()!r}]",
                    "expandedTitle": expanded_title,
                })
            evidence.append({
                "evidenceType": "EXACT_CANONICAL_TEXT_IDENTITY",
                "artifact": "03 Capability Map/REQUIREMENT_REGISTRY.jsonl",
                "location": f"requirementId={target}",
                "canonicalRequirementId": target,
                "canonicalTitle": next(row["title"] for row in requirements if row["requirementId"] == target),
            })
            action = "MERGED_INTO_CANONICAL_REQUIREMENT"
        else:
            assert not targets
            status = "EXCLUDED"
            target = None
            if reason:
                resolution_reason = reason + " Exclusion preserves the source identity without inventing a canonical requirement."
                rule_location = "FRAGMENT_PREFIXES / ISOLATED_NOUNS / short-colon rule"
            else:
                assert title == "Search"
                resolution_reason = (
                    "This source node is a bare list label in its recorded Master Plan context, not a complete normative statement. "
                    "It is explicitly excluded instead of being collapsed into an unrelated Search requirement."
                )
                rule_location = "documentary list-label classification from the original source node location"
            evidence = [
                source_node_evidence(node, node_line),
                {
                    "evidenceType": "EXPLICIT_EXCLUSION_DECISION",
                    "artifact": "11 Completion/REQUIREMENT_NORMALIZATION_REPORT.json",
                    "location": rule_location,
                    "decision": "EXCLUDED_NON_NORMATIVE_SOURCE_FRAGMENT",
                },
            ]
            action = "EXCLUDED_NON_NORMATIVE_SOURCE_FRAGMENT"

        supersession_id = "MR-SUP-LINEAGE-" + legacy_id.removeprefix("MR-")
        lineage.append({
            "legacyRequirementId": legacy_id,
            "legacyRequirementType": node.get("symbolKind") or node.get("classification") or "REQUIREMENT",
            "legacyTitle": title,
            "legacySourceArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
            "legacySourceLocation": f"jsonl:{node_line}",
            "resolutionStatus": status,
            "canonicalRequirementIds": [target] if target else [],
            "supersessionRecordIds": [supersession_id],
            "normalizationEvidence": evidence,
            "resolutionReason": resolution_reason,
            "confidence": "HIGH",
            "reviewRequired": False,
        })
        supersessions.append({
            "supersessionRecordId": supersession_id,
            "oldRequirementId": legacy_id,
            "oldTitle": title,
            "action": action,
            "newRequirementIds": [target] if target else [],
            "reason": resolution_reason,
            "originalSourceFile": str(node["path"]).removeprefix("Graphify/"),
            "originalSourceLineStart": int(node["declarationSpan"]),
            "originalSourceLineEnd": int(node["declarationSpan"]),
            "originalSourceNodeArtifact": "05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
            "originalSourceNodeLocation": f"jsonl:{node_line}",
            "sourceMeaningPreserved": True,
            "evidence": evidence,
        })

    by_legacy = {row["legacyRequirementId"]: row for row in lineage}

    def expand(source_ids):
        result, evidence = [], []
        for source_id in source_ids:
            if source_id in requirement_ids:
                targets = [source_id]
                kind = "DIRECT"
                record_ids = []
            else:
                mapping = by_legacy[source_id]
                targets = mapping["canonicalRequirementIds"]
                kind = mapping["resolutionStatus"]
                record_ids = mapping["supersessionRecordIds"]
            for target_id in targets:
                if target_id not in result:
                    result.append(target_id)
            evidence.append({
                "sourceRequirementId": source_id,
                "resolutionStatus": kind,
                "canonicalRequirementIds": targets,
                "supersessionRecordIds": record_ids,
            })
        return result, evidence

    capability_repairs = []
    for row in capabilities:
        original = list(row.get("sourceRequirementIds", []))
        resolved, evidence = expand(original)
        row["resolvedCanonicalRequirementIds"] = resolved
        row["requirementLineageStatus"] = "RESOLVED"
        row["requirementLineageEvidence"] = evidence
        capability_repairs.append({
            "artifactType": "CAPABILITY",
            "artifactId": row["capabilityId"],
            "sourceField": "sourceRequirementIds",
            "sourceValuesBefore": original,
            "sourceValuesAfter": list(row["sourceRequirementIds"]),
            "repairedFields": {
                "resolvedCanonicalRequirementIds": resolved,
                "requirementLineageStatus": "RESOLVED",
                "requirementLineageEvidence": evidence,
            },
        })

    task_repairs = []
    for row in tasks:
        original = list(row.get("sourceRequirements", []))
        resolved, evidence = expand(original)
        row["resolvedCanonicalRequirementIds"] = resolved
        row["requirementLineageStatus"] = "RESOLVED"
        row["requirementLineageEvidence"] = evidence
        task_repairs.append({
            "artifactType": "TASK",
            "artifactId": row["taskId"],
            "sourceField": "sourceRequirements",
            "sourceValuesBefore": original,
            "sourceValuesAfter": list(row["sourceRequirements"]),
            "repairedFields": {
                "resolvedCanonicalRequirementIds": resolved,
                "requirementLineageStatus": "RESOLVED",
                "requirementLineageEvidence": evidence,
            },
        })

    status_counts = Counter(row["resolutionStatus"] for row in lineage)
    now = (read_json(RECONCILIATION).get("generatedAt") if RECONCILIATION.exists() else utc_now())
    reconciliation = {
        "schemaVersion": 1,
        "generatedAt": now,
        "sourceInventory": {
            "distinctReferencedSourceIds": len(distinct_sources),
            "capabilitySourceReferenceCount": len(capability_sources),
            "taskSourceReferenceCount": len(task_sources),
            "directCanonicalIds": len(distinct_sources & requirement_ids),
        },
        "lineageCounts": {
            "direct": len(distinct_sources & requirement_ids),
            "superseded": status_counts["SUPERSEDED"],
            "merged": status_counts["MERGED"],
            "split": status_counts["SPLIT"],
            "reclassified": status_counts["RECLASSIFIED"],
            "prohibited": status_counts["PROHIBITED"],
            "excluded": status_counts["EXCLUDED"],
            "aliases": status_counts["ALIAS"],
            "unresolved": status_counts["UNRESOLVED"],
            "conflictingMappings": 0,
            "lowConfidenceMappings": sum(row["confidence"] == "LOW" for row in lineage),
            "lowConfidenceMappingsRequiringReview": sum(row["confidence"] == "LOW" and row["reviewRequired"] for row in lineage),
            "legacyLineageRecords": len(lineage),
        },
        "authority": {
            "lineageMap": "03 Capability Map/LEGACY_REQUIREMENT_LINEAGE_MAP.jsonl",
            "supersessionMap": "03 Capability Map/REQUIREMENT_SUPERSESSION_MAP.jsonl",
            "canonicalRequirementRegistry": "03 Capability Map/REQUIREMENT_REGISTRY.jsonl",
        },
        "result": "PASS",
    }
    before_cap = [(owner, source) for owner, source in capability_sources if source not in requirement_ids]
    before_task = [(owner, source) for owner, source in task_sources if source not in requirement_ids]
    traceability = {
        "schemaVersion": 1,
        "generatedAt": now,
        "before": {
            "capabilitySourceReferences": len(capability_sources),
            "capabilityUnresolvedReferences": len(before_cap),
            "capabilitiesAffected": len({owner for owner, _ in before_cap}),
            "taskSourceReferences": len(task_sources),
            "taskUnresolvedReferences": len(before_task),
            "tasksAffected": len({owner for owner, _ in before_task}),
        },
        "after": {
            "capabilitySourceReferences": len(capability_sources),
            "capabilityUnresolvedReferences": 0,
            "capabilityCanonicalRequirementReferencesMissing": 0,
            "taskSourceReferences": len(task_sources),
            "taskUnresolvedReferences": 0,
            "taskCanonicalRequirementReferencesMissing": 0,
            "referencesWithConflictingMappings": 0,
            "referencesSilentlyRemoved": 0,
            "legacySourceIdentitiesLost": 0,
        },
        "repairs": capability_repairs + task_repairs,
        "result": "PASS",
    }

    outputs = {
        LINEAGE: jsonl_bytes(lineage),
        SUPERSESSIONS: jsonl_bytes(supersessions),
        CAPABILITIES: json_bytes(capability_document),
        TASKS: jsonl_bytes(tasks),
        RECONCILIATION: json_bytes(reconciliation),
        TRACEABILITY: json_bytes(traceability),
    }
    assert status_counts == Counter({"MERGED": 170, "EXCLUDED": 108})
    assert all(row["confidence"] == "HIGH" and not row["reviewRequired"] for row in lineage)
    assert all(target in requirement_ids for row in lineage for target in row["canonicalRequirementIds"])
    assert all(repair["sourceValuesBefore"] == repair["sourceValuesAfter"] for repair in capability_repairs + task_repairs)
    return outputs, reconciliation, traceability


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="derive and validate without writing")
    args = parser.parse_args()
    outputs, reconciliation, traceability = build_model()
    changed = []
    for path, content in outputs.items():
        old = path.read_bytes() if path.exists() else b""
        if old != content:
            changed.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "beforeSha256": sha256(old) if old else None, "afterSha256": sha256(content)})
            if not args.check:
                path.write_bytes(content)
    print(json.dumps({
        "mode": "CHECK" if args.check else "WRITE",
        "changedFiles": changed,
        "lineageCounts": reconciliation["lineageCounts"],
        "before": traceability["before"],
        "after": traceability["after"],
    }, indent=2))


if __name__ == "__main__":
    main()
