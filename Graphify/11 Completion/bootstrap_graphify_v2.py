#!/usr/bin/env python3
"""Establish the V2 repair baseline, demote V1 output, and classify the corpus."""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from repair_v2_common import (
    CODEBASE,
    COMPLETION,
    CONTROL,
    GRAPHIFY,
    LAYERS,
    TOOL_CACHE,
    atomic_write_text,
    classify_layer_details,
    codebase_rel,
    graphify_rel,
    iter_jsonl,
    load_json,
    now_utc,
    sha256_file,
    source_hash_manifest,
    tree_digest,
    write_json,
    write_jsonl,
)


BASELINE_PATH = CONTROL / "GRAPHIFY_REPAIR_BASELINE.json"
MANIFEST_PATH = CONTROL / "GRAPHIFY_REPAIR_MANIFEST.json"
EVENTS_PATH = CONTROL / "GRAPHIFY_REPAIR_EVENTS.jsonl"
INVENTORY_PATH = GRAPHIFY / "01 Corpus Inventory" / "REPOSITORY_INVENTORY.jsonl"
LAYER_REGISTRY = GRAPHIFY / "01 Corpus Inventory" / "GRAPH_LAYER_FILE_REGISTRY.jsonl"


def event(run_id: str, event_type: str, status: str, evidence: list[str], detail: str) -> None:
    rows = list(iter_jsonl(EVENTS_PATH)) if EVENTS_PATH.exists() else []
    rows.append(
        {
            "runId": run_id,
            "timestamp": now_utc(),
            "eventType": event_type,
            "status": status,
            "evidencePaths": evidence,
            "detail": detail,
            "codebaseMutation": False,
        }
    )
    write_jsonl(EVENTS_PATH, rows)


def graphify_v1_manifest() -> list[dict[str, object]]:
    excluded_names = {
        "repair_v2_common.py",
        "bootstrap_graphify_v2.py",
        "build_graphify_v2.py",
        "finalize_graphify_v2.py",
        "validate_graphify_v2.py",
    }
    rows = []
    for path in sorted(item for item in GRAPHIFY.rglob("*") if item.is_file()):
        if TOOL_CACHE.resolve() in path.resolve().parents:
            continue
        if path.name in excluded_names:
            continue
        if path in {BASELINE_PATH, MANIFEST_PATH, EVENTS_PATH, LAYER_REGISTRY}:
            continue
        rows.append(
            {
                "path": graphify_rel(path),
                "sizeBytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def build_or_load_baseline() -> dict[str, object]:
    if BASELINE_PATH.exists():
        baseline = load_json(BASELINE_PATH)
        enriched = {
            **baseline,
            "schemaVersion": 2,
            "projectRoot": str(GRAPHIFY.parent.resolve()),
            "writeScope": "Graphify/** only",
            "codebaseMutationAllowed": False,
        }
        if enriched != baseline:
            write_json(BASELINE_PATH, enriched)
        return enriched
    timestamp = now_utc()
    compact = timestamp.replace("-", "").replace(":", "").replace(".", "")
    run_id = "graphify-v2-repair-" + compact[:15]
    source_rows = source_hash_manifest()
    v1_rows = graphify_v1_manifest()
    plan_hashes = {
        path.name: sha256_file(path).upper()
        for path in sorted((GRAPHIFY / "Master Plan").glob("*.md"))
    }
    baseline = {
        "schemaVersion": 2,
        "project": "MindRoom",
        "phase": "GRAPHIFY_V2_REPAIR",
        "runId": run_id,
        "createdAt": timestamp,
        "codebaseRoot": str(CODEBASE.resolve()),
        "graphifyRoot": str(GRAPHIFY.resolve()),
        "projectRoot": str(GRAPHIFY.parent.resolve()),
        "codebaseFileCount": len(source_rows),
        "codebaseDirectoryCount": sum(1 for path in CODEBASE.rglob("*") if path.is_dir()),
        "codebaseTreeSha256": tree_digest(source_rows),
        "masterPlanHashes": plan_hashes,
        "v1GraphifyFileCount": len(v1_rows),
        "v1GraphifyManifestSha256": tree_digest(v1_rows),
        "v1EvidencePolicy": "PRESERVE_AND_DEMOTE_NON_AUTHORITATIVE",
        "codebaseWritePolicy": "READ_ONLY_BYTE_IDENTICAL_REQUIRED",
        "writeScope": "Graphify/** only",
        "codebaseMutationAllowed": False,
        "semanticAiUsed": False,
        "mediaTranscriptionUsed": False,
    }
    write_json(BASELINE_PATH, baseline)
    write_json(
        MANIFEST_PATH,
        {
            "project": "MindRoom",
            "phase": "GRAPHIFY_V2_REPAIR",
            "runId": run_id,
            "createdAt": timestamp,
            "baseline": graphify_rel(BASELINE_PATH),
            "codebaseFiles": source_rows,
            "v1GraphifyFiles": v1_rows,
            "policyVersion": "mindroom-graphify-v2-layered-directed-1",
        },
    )
    event(
        run_id,
        "REPAIR_BASELINE_CREATED",
        "PASS",
        [graphify_rel(BASELINE_PATH), graphify_rel(MANIFEST_PATH)],
        f"Captured {len(source_rows)} Codebase files and {len(v1_rows)} V1 Graphify files before repair mutations.",
    )
    return baseline


def demote_v1(run_id: str) -> None:
    source = COMPLETION / "graphify-out"
    legacy_root = TOOL_CACHE / "legacy-v1"
    destination = legacy_root / "graphify-out"
    legacy_root.mkdir(parents=True, exist_ok=True)
    unresolved_snapshot = legacy_root / "V1_UNRESOLVED_ENDPOINTS_SNAPSHOT.jsonl"
    active_unresolved = GRAPHIFY / "05 Dependency and Impact" / "UNRESOLVED_ENDPOINTS.jsonl"
    if active_unresolved.exists() and not unresolved_snapshot.exists():
        # Preserve the one-to-one V1 diagnostic reclassification evidence
        # before any subsequent builder run rewrites the active registry.
        shutil.copy2(active_unresolved, unresolved_snapshot)
        write_json(
            legacy_root / "V1_UNRESOLVED_ENDPOINTS_SNAPSHOT_MANIFEST.json",
            {
                "runId": run_id,
                "sourcePath": graphify_rel(active_unresolved),
                "snapshotPath": graphify_rel(unresolved_snapshot),
                "sha256": sha256_file(unresolved_snapshot),
                "recordCount": sum(1 for _ in iter_jsonl(unresolved_snapshot)),
                "status": "PRESERVED_READ_ONLY_HISTORICAL_DIAGNOSTIC_INPUT",
                "preservedAt": now_utc(),
            },
        )
    if source.exists() and not destination.exists():
        if GRAPHIFY.resolve() not in source.resolve().parents or GRAPHIFY.resolve() not in destination.resolve().parents:
            raise RuntimeError("V1 demotion path escaped Graphify root")
        shutil.move(str(source), str(destination))
    source.mkdir(parents=True, exist_ok=True)
    legacy_files = sorted(item for item in destination.rglob("*") if item.is_file()) if destination.exists() else []
    write_json(
        legacy_root / "LEGACY_V1_MANIFEST.json",
        {
            "runId": run_id,
            "status": "PRESERVED_NON_AUTHORITATIVE",
            "originalPath": "Graphify/11 Completion/graphify-out",
            "preservedPath": "Graphify/00 Execution Control/Generated Tool Cache/legacy-v1/graphify-out",
            "fileCount": len(legacy_files),
            "byteCount": sum(path.stat().st_size for path in legacy_files),
            "knownDefects": [
                "existence-only AST batch cache",
                "undirected authoritative graph construction",
                "vendor/minified Yarn symbol pollution",
                "31809 dangling endpoint edges",
                "false SliderProps TypeScript self-loop",
            ],
            "authoritative": False,
            "preservedAt": now_utc(),
        },
    )
    event(
        run_id,
        "LEGACY_V1_DEMOTED",
        "PASS",
        ["Graphify/00 Execution Control/Generated Tool Cache/legacy-v1/LEGACY_V1_MANIFEST.json"],
        f"Preserved {len(legacy_files)} legacy files outside the final Completion graph directory.",
    )


def classify_inventory(run_id: str) -> dict[str, int]:
    existing = {row["path"]: row for row in iter_jsonl(INVENTORY_PATH)}
    file_rows: list[dict[str, object]] = []
    layer_counts: Counter[str] = Counter()
    directory_layers: dict[Path, Counter[str]] = defaultdict(Counter)

    for path in sorted(item for item in CODEBASE.rglob("*") if item.is_file()):
        relative = codebase_rel(path)
        layer, layer_rule_id, layer_evidence, layer_confidence = classify_layer_details(path)
        layer_counts[layer] += 1
        current = path.parent
        while current != CODEBASE.parent and (current == CODEBASE or CODEBASE in current.parents):
            directory_layers[current][layer] += 1
            if current == CODEBASE:
                break
            current = current.parent
        source = dict(existing.get(relative, {}))
        source.update(
            {
                "path": relative,
                "entityType": "FILE",
                "primaryLayer": layer,
                "layerRuleId": layer_rule_id,
                "layerEvidence": layer_evidence,
                "layerConfidence": layer_confidence,
                "layerPolicyVersion": "mindroom-graphify-v2-layered-directed-2",
                "layerClassifiedAt": now_utc(),
                "layerClassificationRunId": run_id,
            }
        )
        file_rows.append(source)

    directory_rows: list[dict[str, object]] = []
    for path in sorted(item for item in CODEBASE.rglob("*") if item.is_dir()):
        relative = codebase_rel(path)
        counts = directory_layers.get(path, Counter())
        dominant = counts.most_common(1)[0][0] if counts else "BUILD_AND_CONFIG"
        source = dict(existing.get(relative, {}))
        source.update(
            {
                "path": relative,
                "entityType": "DIRECTORY",
                "primaryLayer": dominant,
                "containedLayerCounts": {layer: counts.get(layer, 0) for layer in LAYERS if counts.get(layer)},
                "layerRuleId": "LAYER-V2-DIRECTORY-DOMINANT",
                "layerEvidence": [f"dominant contained file layer: {dominant}"],
                "layerConfidence": "DERIVED",
                "layerPolicyVersion": "mindroom-graphify-v2-layered-directed-2",
                "layerClassifiedAt": now_utc(),
                "layerClassificationRunId": run_id,
            }
        )
        directory_rows.append(source)

    violations: list[str] = []
    for row in file_rows:
        relative = str(row["path"])
        lower = "/" + relative.lower()
        name = Path(relative).name.lower()
        layer = str(row["primaryLayer"])
        if ("/src/androidtest/" in lower or "/apptests/" in lower or re.search(r"(?:tests?|uitests?)\.(?:swift|kt|kts|java)$", name)) and layer != "TEST_AND_FIXTURE":
            violations.append(f"test:{relative}:{layer}")
        if name == "build.rs" and layer != "BUILD_AND_CONFIG":
            violations.append(f"rust-build:{relative}:{layer}")
        if name.startswith(("tailwind.config", "postcss.config")) and layer != "BUILD_AND_CONFIG":
            violations.append(f"build-config:{relative}:{layer}")
        if name.startswith(("forge.config.", "capacitor.config.")) and layer != "PACKAGING_AND_DEPLOYMENT":
            violations.append(f"packaging-config:{relative}:{layer}")
    if violations:
        raise RuntimeError("Layer-classification invariant failure: " + ", ".join(violations[:20]))

    all_rows = sorted(directory_rows + file_rows, key=lambda row: str(row["path"]))
    write_jsonl(INVENTORY_PATH, all_rows)
    write_jsonl(
        LAYER_REGISTRY,
        [
            {
                "path": row["path"],
                "sha256": row.get("sha256", ""),
                "sizeBytes": row.get("sizeBytes", 0),
                "primaryLayer": row["primaryLayer"],
                "layerRuleId": row["layerRuleId"],
                "layerEvidence": row["layerEvidence"],
                "layerConfidence": row["layerConfidence"],
                "language": row.get("language", ""),
                "generated": row.get("generated", False) or row["primaryLayer"] == "GENERATED_BINDING",
                "vendor": row.get("vendor", False) or row["primaryLayer"] == "VENDOR_AND_TOOLCHAIN",
                "classificationRunId": run_id,
                "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
            }
            for row in file_rows
        ],
    )
    event(
        run_id,
        "REPOSITORY_LAYERS_CLASSIFIED",
        "PASS",
        [graphify_rel(INVENTORY_PATH), graphify_rel(LAYER_REGISTRY)],
        f"Classified {len(file_rows)} files and {len(directory_rows)} directories into mandatory primary layers.",
    )
    return dict(layer_counts)


def update_status(baseline: dict[str, object], layer_counts: dict[str, int]) -> None:
    status = load_json(CONTROL / "status.json", {})
    status["mappingStatus"] = "V2_REPAIR_IN_PROGRESS"
    status["phase"] = "GRAPHIFY_V2_REPAIR"
    status["v2Repair"] = {
        "runId": baseline["runId"],
        "policyVersion": "mindroom-graphify-v2-layered-directed-2",
        "lastCompletedStep": "REPOSITORY_LAYER_CLASSIFICATION",
        "codebaseTreeSha256": baseline["codebaseTreeSha256"],
        "repositoryFilesClassified": sum(layer_counts.values()),
        "layerCounts": layer_counts,
        "legacyV1Status": "PRESERVED_NON_AUTHORITATIVE",
        "affineArchiveStatus": "SEARCH_PENDING",
        "independentReviewStatus": "RESERVED",
        "implementationPerformed": False,
    }
    status["updatedAt"] = now_utc()
    write_json(CONTROL / "status.json", status)


def main() -> None:
    baseline = build_or_load_baseline()
    run_id = str(baseline["runId"])
    demote_v1(run_id)
    counts = classify_inventory(run_id)
    update_status(baseline, counts)
    print(json.dumps({"runId": run_id, "codebaseTreeSha256": baseline["codebaseTreeSha256"], "layerCounts": counts}, separators=(",", ":")))


if __name__ == "__main__":
    main()
