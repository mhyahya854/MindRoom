#!/usr/bin/env python3
"""Comprehensive self-validation for the authoritative MindRoom Graphify V2 map.

This is integration validation, not the independent reviewer decision.  The
reviewer is represented only by an actual record in AGENT_REVIEWS.jsonl.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import posixpath
import re
import tomllib
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from repair_v2_common import (
    CODEBASE,
    COMPLETION,
    CONTROL,
    GRAPHIFY,
    KG,
    iter_jsonl,
    load_json,
    now_utc,
    sha256_file,
    source_hash_manifest,
    tree_digest,
    write_json,
)


if (CONTROL / "FORENSIC_FINALIZATION_BASELINE.json").exists():
    BASELINE = load_json(CONTROL / "FORENSIC_FINALIZATION_BASELINE.json")
elif (CONTROL / "GRAPHIFY_REPAIR_BASELINE.json").exists():
    BASELINE = load_json(CONTROL / "GRAPHIFY_REPAIR_BASELINE.json")
else:
    BASELINE = load_json(CONTROL / "FINALIZATION_BASELINE.json")
RUN_ID = BASELINE["runId"]
RESULT_PATH = COMPLETION / "GLOBAL_VALIDATION_RESULT.json"
RECEIPT_PATH = COMPLETION / "GRAPHIFY_MAPPING_RECEIPT.json"
ALLOWED_OUT = {"graph.json", "graph.html", "GRAPH_HEALTH.json", "GRAPH_REPORT.md", "GRAPH_LAYER_MANIFEST.json", "manifest.json"}
RESOLUTION_STATES = {
    "RESOLVED_INTERNAL_SYMBOL", "RESOLVED_INTERNAL_FILE", "RESOLVED_WORKSPACE_PACKAGE",
    "RESOLVED_EXTERNAL_PACKAGE", "RESOLVED_NODE_BUILTIN", "RESOLVED_GENERATED_ARTIFACT",
    "RESOLVED_RUNTIME_REGISTRATION", "RESOLVED_CONFIGURATION", "DYNAMIC_RUNTIME_REFERENCE",
    "PLANNED_REFERENCE", "UNRESOLVED_INTERNAL", "INVALID_REFERENCE",
}
AST_SCHEMA_VERSION = "mindroom.graphify.ast-batch-manifest.v2"
AST_EXTRACTION_SCHEMA_VERSION = "mindroom.graphify.extraction-manifest.v2"
AST_POLICY_VERSION = "mindroom-graphify-v2-layered-directed-2"
AST_EXTRACTOR_NAME = "graphify.extract.extract"
AST_SUPPORTED = {
    ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".rs", ".go", ".java", ".c", ".h", ".cc", ".cpp", ".hpp",
    ".cs", ".rb", ".php", ".swift", ".kt", ".kts", ".sql", ".graphql",
    ".gql",
}
AST_EXTRACT_LAYERS = {
    "AUTHORED_RUNTIME", "TEST_AND_FIXTURE", "BUILD_AND_CONFIG",
    "PACKAGING_AND_DEPLOYMENT", "MIGRATION_AND_SCHEMA", "GENERATED_BINDING",
}
AST_BATCH_FIELDS = {
    "schemaVersion", "runId", "batchId", "extractorName", "extractorVersion",
    "extractionPolicyVersion", "codebaseBaseline", "masterPlanHashes", "rootPath",
    "orderedInputFiles", "inputFileHashes", "configurationHashes", "layer",
    "batchIndex", "batchSizePolicy", "inputFingerprint", "batchOutputPath",
    "batchOutputSha256", "nodeCount", "edgeCount", "startedAt", "completedAt",
    "status",
}
RUNTIME_DISCOVERY_STATES = {
    "EVIDENCE_BACKED", "NO_REPOSITORY_MATCH_FOUND", "UNRESOLVED", "SUPPRESSED",
}
INTERNAL_RESOLUTION_STATES = {
    "RESOLVED_INTERNAL_SYMBOL", "RESOLVED_INTERNAL_FILE", "RESOLVED_WORKSPACE_PACKAGE",
    "RESOLVED_GENERATED_ARTIFACT",
}
STRICT_AST_LANGUAGE_FAMILIES = {
    ".ts": "JAVASCRIPT_TYPESCRIPT", ".tsx": "JAVASCRIPT_TYPESCRIPT",
    ".js": "JAVASCRIPT_TYPESCRIPT", ".jsx": "JAVASCRIPT_TYPESCRIPT",
    ".mjs": "JAVASCRIPT_TYPESCRIPT", ".cjs": "JAVASCRIPT_TYPESCRIPT",
    ".mts": "JAVASCRIPT_TYPESCRIPT", ".cts": "JAVASCRIPT_TYPESCRIPT",
    ".rs": "RUST", ".swift": "SWIFT", ".kt": "KOTLIN", ".kts": "KOTLIN",
    ".py": "PYTHON", ".c": "C_CPP", ".h": "C_CPP", ".cc": "C_CPP",
    ".cpp": "C_CPP", ".hpp": "C_CPP",
}
GENERATED_PROVENANCE_FIELDS = {
    "runId", "generatedArtifactNodeId", "generatedPath", "generatedFileSha256",
    "language", "producerNodeIds", "producerPaths", "generatorCommand",
    "commandEvidence", "inputPaths", "inputSchemaPaths", "consumerNodeIds",
    "consumerPaths", "regenerationRequirements", "provenanceStatus", "reviewStatus",
}
SCHEMA_INSTANCE_BINDINGS = {
    "capability-registry.schema.json": GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json",
    "deletion-candidate.schema.json": GRAPHIFY / "08 Cleanup" / "DELETION_CANDIDATES.jsonl",
    "deletion-receipt.schema.json": GRAPHIFY / "08 Cleanup" / "DELETION_RECEIPTS.jsonl",
    "dependency-edge.schema.json": GRAPHIFY / "05 Dependency and Impact" / "DEPENDENCY_EDGES.jsonl",
    "exact-location-registry.schema.json": GRAPHIFY / "04 Exact Location Registry" / "EXACT_LOCATION_REGISTRY.json",
    "final-release-receipt.schema.json": COMPLETION / "FINAL_RELEASE_RECEIPT.json",
    "graphify-mapping-receipt.schema.json": COMPLETION / "GRAPHIFY_MAPPING_RECEIPT.json",
    "hash-manifest-checkpoint.schema.json": CONTROL / "HASH_MANIFEST_CHECKPOINTS.jsonl",
    "implementation-task.schema.json": GRAPHIFY / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl",
    "repository-baseline.schema.json": CONTROL / "GRAPHIFY_REPAIR_BASELINE.json",
    "requirement-registry.schema.json": GRAPHIFY / "03 Capability Map" / "REQUIREMENT_REGISTRY.jsonl",
    "runtime-registration.schema.json": GRAPHIFY / "02 Architecture Map" / "RUNTIME_REGISTRATION_REGISTRY.jsonl",
    "status.schema.json": CONTROL / "STATUS.json",
    "symbol-registry.schema.json": GRAPHIFY / "04 Exact Location Registry" / "SYMBOL_REGISTRY.jsonl",
    "task-record.schema.json": GRAPHIFY / "13 Agent Swarm" / "AGENT_TASKS.jsonl",
    "test-receipt.schema.json": GRAPHIFY / "10 Verification" / "TEST_RECEIPTS.jsonl",
    "transplant-receipt.schema.json": GRAPHIFY / "09 Implementation" / "TRANSPLANT_RECEIPTS.jsonl",
}
KNOWN_SQL_RECURSION = {
    (
        "Codebase/packages/backend/server/migrations/20260711080000_auth_sessions/migration.sql",
        "auth_refresh_tokens",
    ),
}


def assert_fields(row: dict[str, Any], fields: Iterable[str], context: str) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise AssertionError(f"{context}: missing {missing}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def filesystem_path(path: Path) -> Path:
    resolved = path.resolve()
    if os.name == "nt":
        return Path("\\\\?\\" + str(resolved))
    return resolved


def is_preserved_affine_source(path: Path) -> bool:
    relative = path.resolve().relative_to(GRAPHIFY.resolve()).as_posix()
    return (
        relative == "14 AFFiNE Reference/Reference Tree"
        or relative.startswith("14 AFFiNE Reference/Reference Tree/")
        or relative == "14 AFFiNE Reference/Incoming"
        or relative.startswith("14 AFFiNE Reference/Incoming/")
    )


def strict_ast_language_family(path: str) -> str:
    return STRICT_AST_LANGUAGE_FAMILIES.get(Path(path).suffix.lower(), "")


def stable_id(prefix: str, *parts: str, length: int = 24) -> str:
    canonical = "\x1f".join(str(part).replace("\\", "/") for part in parts)
    return f"{prefix}-{sha256_bytes(canonical.encode('utf-8'))[:length]}"


def graphify_path(relative: str, context: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise AssertionError(f"{context}: empty Graphify-relative path")
    candidate = (GRAPHIFY / relative).resolve()
    if candidate != GRAPHIFY.resolve() and GRAPHIFY.resolve() not in candidate.parents:
        raise AssertionError(f"{context}: path escapes Graphify: {relative}")
    return candidate


def codebase_path(relative: str, context: str) -> Path:
    if not isinstance(relative, str) or not relative.startswith("Codebase/"):
        raise AssertionError(f"{context}: not a Codebase-relative path: {relative!r}")
    candidate = (GRAPHIFY.parent / relative).resolve()
    if CODEBASE.resolve() not in candidate.parents:
        raise AssertionError(f"{context}: path escapes Codebase: {relative}")
    return candidate


def ast_configuration_hashes() -> dict[str, str]:
    candidates = [
        COMPLETION / "run_ast_batched.py",
        COMPLETION / "repair_v2_common.py",
        GRAPHIFY / "01 Corpus Inventory" / "GRAPH_LAYER_FILE_REGISTRY.jsonl",
        CODEBASE / "package.json",
        CODEBASE / "yarn.lock",
        CODEBASE / ".yarnrc.yml",
        CODEBASE / "tsconfig.json",
    ]
    return {
        path.resolve().relative_to(GRAPHIFY.parent.resolve()).as_posix(): sha256_file(path)
        for path in candidates
        if path.is_file()
    }


def current_graphify_extractor_version() -> str:
    distributions = importlib.metadata.packages_distributions().get("graphify", [])
    for distribution in [*distributions, "graphifyy", "graphify"]:
        try:
            return f"{distribution}=={importlib.metadata.version(distribution)}"
        except importlib.metadata.PackageNotFoundError:
            continue
    raise AssertionError("installed Graphify extractor distribution version cannot be independently verified")


def expected_ast_inputs() -> tuple[dict[str, dict[str, Any]], list[str]]:
    registry_path = GRAPHIFY / "01 Corpus Inventory" / "GRAPH_LAYER_FILE_REGISTRY.jsonl"
    expected: dict[str, dict[str, Any]] = {}
    for number, row in enumerate(iter_jsonl(registry_path), 1):
        relative = row.get("path", "")
        layer = row.get("primaryLayer", "")
        if layer not in AST_EXTRACT_LAYERS:
            continue
        path = codebase_path(relative, f"AST registry:{number}")
        if path.suffix.lower() not in AST_SUPPORTED:
            continue
        if not path.is_file():
            raise AssertionError(f"AST registry:{number}: source is missing: {relative}")
        current_hash = sha256_file(path)
        if current_hash != row.get("sha256") or path.stat().st_size != row.get("sizeBytes"):
            raise AssertionError(f"AST registry:{number}: source hash/size is stale: {relative}")
        if relative in expected:
            raise AssertionError(f"AST registry duplicates extractable source: {relative}")
        expected[relative] = {"layer": layer, "sha256": current_hash}
    ordered = [
        relative
        for layer in sorted(AST_EXTRACT_LAYERS)
        for relative in sorted(path for path, row in expected.items() if row["layer"] == layer)
    ]
    return expected, ordered


def validate_ast_cache() -> dict[str, Any]:
    ast_root = CONTROL / "Generated Tool Cache" / "v2" / RUN_ID / "ast"
    extraction_path = ast_root / "EXTRACTION_MANIFEST.json"
    manifest = load_json(extraction_path)
    assert_fields(
        manifest,
        [
            "schemaVersion", "project", "runId", "extractionPolicyVersion",
            "extractorName", "extractorVersion", "codebaseBaseline", "masterPlanHashes",
            "rootPath", "authoritative", "status", "batchSizePolicy", "batchCount",
            "reusedBatchCount", "reextractedBatchCount", "fileCount", "layers",
            "partitionValidation", "batches", "startedAt", "completedAt",
        ],
        "AST extraction manifest",
    )
    exact_manifest_values = {
        "schemaVersion": AST_EXTRACTION_SCHEMA_VERSION,
        "project": "MindRoom",
        "runId": RUN_ID,
        "extractionPolicyVersion": AST_POLICY_VERSION,
        "extractorName": AST_EXTRACTOR_NAME,
        "codebaseBaseline": BASELINE["codebaseTreeSha256"],
        "masterPlanHashes": BASELINE["masterPlanHashes"],
        "rootPath": str(CODEBASE.resolve()),
        "authoritative": False,
        "status": "COMPLETE",
    }
    for field, expected_value in exact_manifest_values.items():
        if manifest.get(field) != expected_value:
            raise AssertionError(f"AST extraction manifest: {field} is not current/exact")
    if manifest.get("extractorVersion") != current_graphify_extractor_version():
        raise AssertionError("AST extraction manifest: extractorVersion differs from the installed distribution")
    batch_size = manifest.get("batchSizePolicy")
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise AssertionError("AST extraction manifest: batchSizePolicy must be positive")

    expected, expected_order = expected_ast_inputs()
    config_hashes = ast_configuration_hashes()
    memberships: list[str] = []
    actual_descriptors: list[tuple[str, int, list[str]]] = []
    seen_batch_ids: set[str] = set()
    batch_outputs = 0
    layer_counts = Counter(row["layer"] for row in expected.values())
    batches = manifest.get("batches")
    if not isinstance(batches, list) or not batches:
        raise AssertionError("AST extraction manifest: no batches")
    for summary_number, summary in enumerate(batches, 1):
        assert_fields(
            summary,
            [
                "batchId", "layer", "batchIndex", "inputFingerprint", "manifestPath",
                "batchOutputPath", "batchOutputSha256", "nodeCount", "edgeCount", "status",
            ],
            f"AST batch summary:{summary_number}",
        )
        manifest_path = graphify_path(summary["manifestPath"], f"AST batch summary:{summary_number}")
        batch = load_json(manifest_path)
        missing_fields = sorted(AST_BATCH_FIELDS - set(batch))
        if missing_fields:
            raise AssertionError(f"AST batch manifest:{summary_number}: missing {missing_fields}")
        if batch["batchId"] in seen_batch_ids:
            raise AssertionError(f"AST batch manifest:{summary_number}: duplicate batchId {batch['batchId']}")
        seen_batch_ids.add(batch["batchId"])
        if batch["status"] != "COMPLETE" or summary["status"] != "COMPLETE":
            raise AssertionError(f"AST batch manifest:{summary_number}: batch is not COMPLETE")
        ordered_inputs = batch["orderedInputFiles"]
        if not isinstance(ordered_inputs, list) or not ordered_inputs or ordered_inputs != sorted(ordered_inputs):
            raise AssertionError(f"AST batch manifest:{summary_number}: inputs are empty or not ordered")
        if len(ordered_inputs) != len(set(ordered_inputs)):
            raise AssertionError(f"AST batch manifest:{summary_number}: duplicate input within batch")
        if batch["layer"] not in AST_EXTRACT_LAYERS:
            raise AssertionError(f"AST batch manifest:{summary_number}: invalid extraction layer")
        if any(path not in expected or expected[path]["layer"] != batch["layer"] for path in ordered_inputs):
            raise AssertionError(f"AST batch manifest:{summary_number}: unexpected or cross-layer input")
        current_hashes = {path: expected[path]["sha256"] for path in ordered_inputs}
        canonical = {
            "schemaVersion": AST_SCHEMA_VERSION,
            "runId": RUN_ID,
            "extractorName": AST_EXTRACTOR_NAME,
            "extractorVersion": manifest["extractorVersion"],
            "extractionPolicyVersion": AST_POLICY_VERSION,
            "codebaseBaseline": BASELINE["codebaseTreeSha256"],
            "masterPlanHashes": BASELINE["masterPlanHashes"],
            "rootPath": str(CODEBASE.resolve()),
            "orderedInputFiles": ordered_inputs,
            "inputFileHashes": current_hashes,
            "configurationHashes": config_hashes,
            "layer": batch["layer"],
            "batchIndex": batch["batchIndex"],
            "batchSizePolicy": batch_size,
        }
        fingerprint = sha256_bytes(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        expected_batch_id = stable_id("MR-AST-BATCH-V2", batch["layer"], str(batch["batchIndex"]), fingerprint)
        exact_batch_values = {
            **canonical,
            "batchId": expected_batch_id,
            "inputFingerprint": fingerprint,
        }
        for field, expected_value in exact_batch_values.items():
            if batch.get(field) != expected_value:
                raise AssertionError(f"AST batch manifest:{summary_number}: stale/mismatched {field}")
        output = graphify_path(batch["batchOutputPath"], f"AST batch manifest:{summary_number}")
        slug = batch["layer"].lower().replace("_", "-")
        expected_output = ast_root / "batches" / slug / f"batch-{batch['batchIndex']:04d}.json"
        expected_batch_manifest = ast_root / "batches" / slug / f"batch-{batch['batchIndex']:04d}.manifest.json"
        if output != expected_output.resolve() or manifest_path != expected_batch_manifest.resolve():
            raise AssertionError(f"AST batch manifest:{summary_number}: cache output/manifest path is not canonical")
        if not output.is_file() or batch["batchOutputSha256"] != sha256_file(output):
            raise AssertionError(f"AST batch manifest:{summary_number}: output missing or hash mismatch")
        payload = load_json(output)
        if not isinstance(payload.get("nodes"), list) or not isinstance(payload.get("edges"), list):
            raise AssertionError(f"AST batch manifest:{summary_number}: output schema invalid")
        if batch["nodeCount"] != len(payload["nodes"]) or batch["edgeCount"] != len(payload["edges"]):
            raise AssertionError(f"AST batch manifest:{summary_number}: output count mismatch")
        summary_values = {
            "batchId": batch["batchId"], "layer": batch["layer"],
            "batchIndex": batch["batchIndex"], "inputFingerprint": fingerprint,
            "manifestPath": manifest_path.relative_to(GRAPHIFY).as_posix(),
            "batchOutputPath": batch["batchOutputPath"],
            "batchOutputSha256": batch["batchOutputSha256"],
            "nodeCount": batch["nodeCount"], "edgeCount": batch["edgeCount"],
            "status": "COMPLETE",
        }
        if any(summary.get(field) != value for field, value in summary_values.items()):
            raise AssertionError(f"AST batch summary:{summary_number}: summary differs from batch manifest")
        if batch.get("cacheDecision") != "REUSED_AFTER_FULL_VALIDATION" or int(batch.get("reuseValidationCount", 0)) < 1:
            raise AssertionError(f"AST batch manifest:{summary_number}: second-run cache reuse was not verified")
        memberships.extend(ordered_inputs)
        actual_descriptors.append((batch["layer"], batch["batchIndex"], ordered_inputs))
        batch_outputs += 1

    expected_descriptors: list[tuple[str, int, list[str]]] = []
    for layer in sorted(AST_EXTRACT_LAYERS):
        layer_inputs = sorted(path for path, row in expected.items() if row["layer"] == layer)
        for index in range(0, len(layer_inputs), batch_size):
            expected_descriptors.append((layer, index // batch_size, layer_inputs[index : index + batch_size]))
    if actual_descriptors != expected_descriptors:
        raise AssertionError("AST extraction manifest: batches are not the exact ordered batch-size partition")
    membership_counts = Counter(memberships)
    duplicates = sorted(path for path, count in membership_counts.items() if count != 1)
    omissions = sorted(set(expected) - set(memberships))
    unexpected = sorted(set(memberships) - set(expected))
    if duplicates or omissions or unexpected or memberships != expected_order:
        raise AssertionError({
            "ASTPartitionDuplicates": duplicates[:10], "ASTPartitionOmissions": omissions[:10],
            "ASTPartitionUnexpected": unexpected[:10], "orderedFullPartition": memberships == expected_order,
        })
    expected_partition = {
        "status": "PASS", "expectedFileCount": len(expected),
        "partitionedFileCount": len(memberships), "uniquePartitionedFileCount": len(set(memberships)),
        "duplicateFiles": [], "omittedFiles": [], "unexpectedFiles": [], "duplicateBatchIds": [],
        "orderedSourceSetSha256": sha256_bytes("\n".join(expected_order).encode("utf-8")),
    }
    if manifest["partitionValidation"] != expected_partition:
        raise AssertionError("AST extraction manifest: partitionValidation is not an exact current full partition")
    if manifest["batchCount"] != len(batches) or manifest["fileCount"] != len(expected):
        raise AssertionError("AST extraction manifest: batch/file counts differ from current partition")
    if manifest["layers"] != dict(sorted(layer_counts.items())):
        raise AssertionError("AST extraction manifest: layer counts differ from current partition")
    if manifest["reusedBatchCount"] != len(batches) or manifest["reextractedBatchCount"] != 0:
        raise AssertionError("AST extraction manifest: latest invocation is not a full verified reuse")

    run_receipts_path = ast_root / "EXTRACTION_RUNS.jsonl"
    runs = [row for row in iter_jsonl(run_receipts_path) if row.get("runId") == RUN_ID and row.get("status") == "COMPLETE"]
    fresh_indices = [
        index for index, row in enumerate(runs)
        if row.get("batchCount") == len(batches) and row.get("reusedBatchCount") == 0
        and row.get("reextractedBatchCount") == len(batches) and row.get("partitionStatus") == "PASS"
    ]
    reuse_indices = [
        index for index, row in enumerate(runs)
        if row.get("batchCount") == len(batches) and row.get("reusedBatchCount") == len(batches)
        and row.get("reextractedBatchCount") == 0 and row.get("partitionStatus") == "PASS"
    ]
    if not fresh_indices or not any(reuse > fresh_indices[0] for reuse in reuse_indices):
        raise AssertionError("AST extraction receipts lack a fresh COMPLETE run followed by a fully validated reuse run")
    return {
        "status": "PASS", "batchCount": len(batches), "fileCount": len(expected),
        "batchOutputsParsed": batch_outputs, "freshRunReceipt": True,
        "verifiedReuseRunReceipt": True, "partitionStatus": "PASS",
    }


def validate_json_files() -> dict[str, Any]:
    json_files = []
    jsonl_files = []
    for root, directories, files in os.walk(GRAPHIFY):
        root_path = Path(root)
        directories[:] = [
            name
            for name in directories
            if name != "Generated Tool Cache"
            and not is_preserved_affine_source(root_path / name)
        ]
        for name in files:
            path = root_path / name
            if name.endswith(".json"):
                json_files.append(path)
            elif name.endswith(".jsonl"):
                jsonl_files.append(path)
    parsed_json = 0
    parsed_jsonl_records = 0
    for path in sorted(json_files):
        load_json(path)
        parsed_json += 1
    for path in sorted(jsonl_files):
        parsed_jsonl_records += sum(1 for _ in iter_jsonl(path))
    cache = validate_ast_cache()
    return {
        "status": "PASS", "jsonFilesParsed": parsed_json, "jsonlFilesParsed": len(jsonl_files),
        "jsonlRecordsParsed": parsed_jsonl_records, "generatedCacheScope": "V2_HASH_MANIFEST_VALIDATED",
        "cacheBatchOutputsParsed": cache["batchOutputsParsed"], "astValidation": cache,
        "legacyV1CacheScope": "PRESERVED_NON_AUTHORITATIVE_EXCLUDED",
    }


def validate_schemas_and_contracts() -> dict[str, Any]:
    schema_files = sorted((CONTROL / "schemas").glob("*.schema.json"))
    if {path.name for path in schema_files} != set(SCHEMA_INSTANCE_BINDINGS):
        raise AssertionError({
            "unboundSchemas": sorted({path.name for path in schema_files} - set(SCHEMA_INSTANCE_BINDINGS)),
            "bindingsWithoutSchemas": sorted(set(SCHEMA_INSTANCE_BINDINGS) - {path.name for path in schema_files}),
        })
    schema_instance_results: dict[str, dict[str, Any]] = {}
    schema_errors: list[str] = []
    total_schema_instances = 0
    for schema_path in schema_files:
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        instance_path = SCHEMA_INSTANCE_BINDINGS[schema_path.name]
        if not instance_path.is_file():
            schema_errors.append(f"{schema_path.name}: instance artifact missing: {instance_path.relative_to(GRAPHIFY)}")
            schema_instance_results[schema_path.name] = {
                "instancePath": instance_path.relative_to(GRAPHIFY).as_posix(),
                "instanceCount": 0, "errorCount": 1,
            }
            continue
        instances = list(iter_jsonl(instance_path)) if instance_path.suffix == ".jsonl" else [load_json(instance_path)]
        if not instances:
            schema_errors.append(f"{schema_path.name}: instance artifact is empty")
        validator = Draft202012Validator(schema)
        error_count = 0
        for instance_number, instance in enumerate(instances, 1):
            for error in validator.iter_errors(instance):
                location = "/".join(str(part) for part in error.absolute_path) or "$"
                schema_errors.append(
                    f"{schema_path.name}:{instance_path.relative_to(GRAPHIFY)}:{instance_number}:{location}: {error.message}"
                )
                error_count += 1
        total_schema_instances += len(instances)
        schema_instance_results[schema_path.name] = {
            "instancePath": instance_path.relative_to(GRAPHIFY).as_posix(),
            "instanceCount": len(instances), "errorCount": error_count,
        }
    if schema_errors:
        raise AssertionError({"schemaInstanceErrorCount": len(schema_errors), "errors": schema_errors[:50]})
    node_count = 0
    for number, row in enumerate(iter_jsonl(KG / "NODES.jsonl"), 1):
        assert_fields(row, ["nodeId", "nodeType", "layer", "language", "package", "path", "qualifiedName", "symbolKind", "declarationSpan", "uniqueAnchor", "anchorSha256", "fileSha256", "generated", "vendor", "runtimeReachability", "capabilityIds", "requirementIds", "evidence", "runId"], f"NODES:{number}")
        node_count += 1
    edge_count = 0
    for number, row in enumerate(iter_jsonl(KG / "EDGES.jsonl"), 1):
        assert_fields(row, ["edgeId", "sourceNodeId", "targetNodeId", "relation", "declaringPath", "sourceSpan", "context", "evidenceOrigin", "sourceResolutionStatus", "targetResolutionStatus", "layer", "evidence", "runtimeRelationship", "reviewStatus", "recursiveStatus"], f"EDGES:{number}")
        edge_count += 1
    runtime_count = 0
    for number, row in enumerate(iter_jsonl(GRAPHIFY / "02 Architecture Map" / "RUNTIME_REGISTRATION_REGISTRY.jsonl"), 1):
        assert_fields(row, [
            "registrationId", "registrationType", "declaringPath", "declaringSymbol", "lineRange",
            "registeredIdentifier", "implementationPaths", "consumerPaths", "runtimeEntrypoints",
            "capabilityIds", "classification", "removalRisk", "evidence", "reviewStatus",
            "consumerDiscoveryStatus", "consumerSearchEvidence", "capabilityDiscoveryStatus",
            "capabilitySearchEvidence", "entrypointDiscoveryStatus", "entrypointSearchEvidence",
        ], f"RUNTIME:{number}")
        runtime_count += 1
    change_count = 0
    change_fields = ["changeId", "requirementIds", "capabilityId", "changeType", "currentLocationStatus", "currentPaths", "currentSymbols", "currentAnchors", "targetPaths", "targetOwner", "exactRequiredChange", "preserve", "removeLater", "addLater", "forbiddenChanges", "affineReferencePaths", "dependencies", "dependants", "runtimeRegistrations", "configurationReferences", "testsRequired", "fixturesRequired", "verificationReceiptsRequired", "rollbackRequirements", "riskLevel", "blockers", "status", "reviewStatus"]
    for number, row in enumerate(iter_jsonl(GRAPHIFY / "04 Exact Location Registry" / "CHANGE_LOCATION_REGISTRY.jsonl"), 1):
        assert_fields(row, change_fields, f"CHANGES:{number}")
        change_count += 1
    ponytail_count = 0
    ponytail_fields = ["findingId", "candidateType", "paths", "symbols", "capabilityIds", "currentHashes", "exactDuplicateEvidence", "incomingCallers", "outgoingDependencies", "exports", "runtimeRegistrations", "platformVariants", "generatedStatus", "testCoverage", "buildReferences", "packagingReferences", "licenceImplications", "estimatedReduction", "futureBatchId", "requiredProofs", "decision", "status", "independentReview"]
    for number, row in enumerate(iter_jsonl(GRAPHIFY / "08 Cleanup" / "PONYTAIL_AUDIT.jsonl"), 1):
        assert_fields(row, ponytail_fields, f"PONYTAIL:{number}")
        ponytail_count += 1
    return {
        "status": "PASS", "schemaDocumentsValidated": len(schema_files),
        "schemaInstancesValidated": total_schema_instances, "schemaInstanceErrors": 0,
        "schemaInstanceResults": schema_instance_results,
        "v2ContractInstancesValidated": node_count + edge_count + runtime_count + change_count + ponytail_count,
        "nodes": node_count, "edges": edge_count, "runtimeRegistrations": runtime_count,
        "requiredChanges": change_count, "ponytailFindings": ponytail_count,
    }


def validate_baseline() -> dict[str, Any]:
    current = source_hash_manifest()
    manifest = load_json(CONTROL / "GRAPHIFY_REPAIR_MANIFEST.json")
    expected = {row["path"]: (row["sizeBytes"], row["sha256"]) for row in manifest["codebaseFiles"]}
    actual = {row["path"]: (row["sizeBytes"], row["sha256"]) for row in current}
    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])
    directories = sum(1 for path in CODEBASE.rglob("*") if path.is_dir())
    if missing or added or changed or directories != BASELINE["codebaseDirectoryCount"]:
        raise AssertionError({"missing": missing[:10], "added": added[:10], "changed": changed[:10], "directories": directories})
    digest = tree_digest(current)
    if digest != BASELINE["codebaseTreeSha256"]:
        raise AssertionError("Codebase tree digest changed")
    status_mp_hashes = load_json(CONTROL / "status.json").get("masterPlanHashes", BASELINE["masterPlanHashes"])
    for name, expected_hash in status_mp_hashes.items():
        if sha256_file(GRAPHIFY / "Master Plan" / name).upper() != expected_hash.upper():
            raise AssertionError(f"Master Plan hash changed: {name}")
    return {
        "status": "PASS", "beforeTreeSha256": BASELINE["codebaseTreeSha256"], "afterTreeSha256": digest,
        "fileCount": len(current), "directoryCount": directories, "changedFiles": 0, "addedFiles": 0,
        "missingFiles": 0, "codebaseFilesModified": 0, "masterPlanHashesVerified": BASELINE["masterPlanHashes"],
    }


def is_known_non_runtime_path(relative: str) -> bool:
    path = relative.replace("\\", "/").lower()
    name = path.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    parts = path.split("/")
    return (
        "androidtest" in parts
        or "apptests" in parts
        or name == "build.rs"
        or (name.endswith((".swift", ".kt", ".kts", ".java")) and stem.endswith(("test", "tests")))
        or name.startswith("tailwind.config.")
        or name.startswith("forge.config.")
        or name.startswith("capacitor.config.")
    )


def validate_layer_exclusions(file_nodes: list[dict[str, Any]]) -> dict[str, Any]:
    known = [node for node in file_nodes if is_known_non_runtime_path(node.get("path", ""))]
    polluted = [node["path"] for node in known if node.get("layer") == "AUTHORED_RUNTIME"]
    if polluted:
        raise AssertionError({"knownNonRuntimeFilesInAuthoredRuntime": polluted[:50]})
    return {"status": "PASS", "knownNonRuntimeExamplesChecked": len(known), "authoredRuntimePollution": 0}


def case_sensitive_relative_candidates(source: str, specifier: str) -> list[str]:
    clean = specifier.split("?", 1)[0].split("#", 1)[0]
    base = posixpath.normpath(posixpath.join(posixpath.dirname(source), clean))
    candidates: list[str] = []
    suffix = Path(base).suffix.lower()
    if suffix in {".js", ".jsx", ".mjs", ".cjs"}:
        stem = base[: -len(suffix)]
        candidates.extend(stem + extension for extension in (".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs"))
    for extension in (
        "", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".json",
        ".css", ".scss", ".sass", ".less", ".graphql", ".gql", ".rs", ".swift", ".kt", ".py", ".sql",
        ".svg", ".png", ".jpg", ".webp", ".wasm", ".node",
    ):
        candidates.append(base + extension)
    candidates.extend(
        posixpath.join(base, index_name)
        for index_name in (
            "index.ts", "index.tsx", "index.mts", "index.js", "index.jsx", "index.mjs",
            "index.json", "index.css", "mod.rs", "__init__.py",
        )
    )
    return list(dict.fromkeys(candidates))


def validate_case_sensitive_internal_resolutions(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]], file_nodes: list[dict[str, Any]]
) -> dict[str, Any]:
    actual_paths = {node["path"] for node in file_nodes}
    casefold_index: dict[str, list[str]] = {}
    for path in actual_paths:
        casefold_index.setdefault(path.casefold(), []).append(path)
    nodes_by_id = {node["nodeId"]: node for node in nodes}
    checked = 0
    wrong_case: list[dict[str, str]] = []
    wrong_target: list[dict[str, str]] = []
    for edge in edges:
        context = str(edge.get("context", ""))
        if not context.startswith("language-aware-") or ":" not in context:
            continue
        specifier = context.split(":", 1)[1].strip()
        if not specifier.startswith(("./", "../")):
            continue
        declaring = edge.get("declaringPath", "")
        if declaring not in actual_paths:
            continue
        candidates = case_sensitive_relative_candidates(declaring, specifier)
        exact = next((candidate for candidate in candidates if candidate in actual_paths), None)
        if exact is None:
            folded = next(
                (
                    actual
                    for candidate in candidates
                    for actual in casefold_index.get(candidate.casefold(), [])
                ),
                None,
            )
            if folded:
                wrong_case.append({"edgeId": edge["edgeId"], "specifier": specifier, "actualPath": folded})
            continue
        checked += 1
        target = nodes_by_id.get(edge["targetNodeId"], {})
        if (
            edge.get("targetResolutionStatus") in {"RESOLVED_INTERNAL_FILE", "RESOLVED_GENERATED_ARTIFACT"}
            and target.get("path") != exact
        ):
            wrong_target.append({
                "edgeId": edge["edgeId"], "specifier": specifier,
                "expectedExactPath": exact, "targetPath": target.get("path", ""),
            })
    if wrong_case or wrong_target:
        raise AssertionError({
            "wrongCaseInternalResolutions": wrong_case[:50],
            "incorrectExactInternalTargets": wrong_target[:50],
        })
    return {"status": "PASS", "caseSensitiveRelativeResolutionsChecked": checked, "wrongCaseResolutions": 0}


def mask_comments(text: str, block_pattern: str, line_pattern: str) -> str:
    def preserve_lines(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = re.sub(block_pattern, preserve_lines, text, flags=re.DOTALL)
    return re.sub(line_pattern, "", text, flags=re.MULTILINE)


SQL_IDENTIFIER = r'(?:"[^"]+"|`[^`]+`|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]+"|`[^`]+`|[A-Za-z_][\w$]*))*'


def normalize_sql_identifier(identifier: str) -> str:
    value = re.split(r"\s*\.\s*", identifier.strip())[-1]
    return value.strip('"`').lower()


def matching_sql_paren(text: str, start: int) -> int:
    depth = 0
    quote = ""
    index = start
    while index < len(text):
        char = text[index]
        if quote:
            if char == quote:
                if index + 1 < len(text) and text[index + 1] == quote:
                    index += 2
                    continue
                quote = ""
        elif char in {'"', "'", "`"}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise AssertionError("SQL CREATE TABLE has an unbalanced body")


def discover_sql_self_references() -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    create_pattern = re.compile(
        rf"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<table>{SQL_IDENTIFIER})\s*\(",
        re.IGNORECASE,
    )
    reference_pattern = re.compile(rf"\bREFERENCES\s+(?P<table>{SQL_IDENTIFIER})\s*\(", re.IGNORECASE)
    alter_pattern = re.compile(
        rf"\bALTER\s+TABLE\s+(?:ONLY\s+)?(?P<table>{SQL_IDENTIFIER})(?P<body>.*?);",
        re.IGNORECASE | re.DOTALL,
    )
    for path in sorted(CODEBASE.rglob("*.sql")):
        relative = "Codebase/" + path.relative_to(CODEBASE).as_posix()
        text = path.read_text(encoding="utf-8")
        scan = mask_comments(text, r"/\*.*?\*/", r"--[^\n]*$")
        for create in create_pattern.finditer(scan):
            source = normalize_sql_identifier(create.group("table"))
            body_start = create.end() - 1
            body = scan[body_start + 1 : matching_sql_paren(scan, body_start)]
            for reference in reference_pattern.finditer(body):
                target = normalize_sql_identifier(reference.group("table"))
                if source == target:
                    found.add((relative, source))
        for alter in alter_pattern.finditer(scan):
            source = normalize_sql_identifier(alter.group("table"))
            for reference in reference_pattern.finditer(alter.group("body")):
                target = normalize_sql_identifier(reference.group("table"))
                if source == target:
                    found.add((relative, source))
    return found


def validate_self_loops(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    independently_proven = discover_sql_self_references()
    if independently_proven != KNOWN_SQL_RECURSION:
        raise AssertionError({
            "expectedKnownSqlRecursion": sorted(KNOWN_SQL_RECURSION),
            "independentlyParsedSqlRecursion": sorted(independently_proven),
        })
    nodes_by_id = {node["nodeId"]: node for node in nodes}
    loops = [edge for edge in edges if edge["sourceNodeId"] == edge["targetNodeId"]]
    invalid_loops: list[str] = []
    for edge in loops:
        node = nodes_by_id[edge["sourceNodeId"]]
        identity = (edge.get("declaringPath", ""), node.get("qualifiedName", "").split("::")[-1].lower())
        if (
            edge.get("relation") != "MIGRATION_DEPENDENCY"
            or edge.get("recursiveStatus") != "VALID_SCHEMA_SELF_REFERENCE"
            or node.get("nodeType") != "SCHEMA"
            or identity not in independently_proven
        ):
            invalid_loops.append(edge["edgeId"])
    recursive_nonloops = [
        edge["edgeId"] for edge in edges
        if edge.get("recursiveStatus") != "NOT_RECURSIVE" and edge["sourceNodeId"] != edge["targetNodeId"]
    ]
    if invalid_loops or recursive_nonloops or len(loops) != len(independently_proven):
        raise AssertionError({
            "invalidAuthoritativeSelfLoops": invalid_loops[:50],
            "recursiveStatusesOnNonloops": recursive_nonloops[:50],
            "authoritativeLoopCount": len(loops), "provenLoopCount": len(independently_proven),
        })
    classifications = list(iter_jsonl(KG / "SELF_LOOP_CLASSIFICATION.jsonl"))
    if any(row.get("invalidSelfLoopRemaining") for row in classifications):
        raise AssertionError("SELF_LOOP_CLASSIFICATION reports an invalid remaining self-loop")
    loop_ids = {edge["edgeId"] for edge in loops}
    valid_rows = [
        row for row in classifications
        if row.get("v2Classification") == "VALID_SCHEMA_SELF_REFERENCE"
    ]
    if {row.get("replacementEdgeId") for row in valid_rows} != loop_ids:
        raise AssertionError("every valid authoritative self-loop must have one directly bound classification record")
    for row in classifications:
        replacement = row.get("replacementEdgeId")
        if row.get("v2Classification", "").startswith("REPAIRED_"):
            matches = [edge for edge in edges if edge["edgeId"] == replacement]
            if len(matches) != 1 or matches[0]["sourceNodeId"] == matches[0]["targetNodeId"]:
                raise AssertionError(f"self-loop repair classification is not bound to a non-loop replacement: {row.get('loopId')}")
    return {
        "status": "PASS", "authoritativeSelfLoops": len(loops),
        "validSchemaSelfReferences": len(loops), "invalidSelfLoops": 0,
        "classificationRecords": len(classifications),
    }


def rust_module_declarations() -> list[tuple[str, str, str]]:
    declarations: list[tuple[str, str, str]] = []
    pattern = re.compile(
        r'(?m)(?:^\s*#\s*\[\s*path\s*=\s*"([^"]+)"\s*\]\s*\n)?'
        r'^\s*(?:pub(?:\s*\([^)]*\))?\s+)?mod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;',
    )
    for path in sorted(CODEBASE.rglob("*.rs")):
        text = path.read_text(encoding="utf-8")
        scan = mask_comments(text, r"/\*.*?\*/", r"//[^\n]*$")
        source = "Codebase/" + path.relative_to(CODEBASE).as_posix()
        for match in pattern.finditer(scan):
            custom_path, module = match.groups()
            module_directory = path.parent if path.name in {"lib.rs", "main.rs", "mod.rs"} else path.with_suffix("")
            candidates = [path.parent / custom_path] if custom_path else [
                module_directory / f"{module}.rs",
                module_directory / module / "mod.rs",
            ]
            targets = [candidate for candidate in candidates if candidate.is_file()]
            if len(targets) != 1:
                raise AssertionError({
                    "rustModuleSource": source, "module": module,
                    "candidateTargets": [candidate.as_posix() for candidate in candidates],
                    "resolvedTargets": [target.as_posix() for target in targets],
                })
            target = "Codebase/" + targets[0].relative_to(CODEBASE).as_posix()
            declarations.append((source, module, target))
    return declarations


def cargo_dependency_tables(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    tables: list[tuple[str, dict[str, Any]]] = []
    for key in ("dependencies", "dev-dependencies", "build-dependencies"):
        value = data.get(key)
        if isinstance(value, dict):
            tables.append((key, value))
    targets = data.get("target", {})
    if isinstance(targets, dict):
        for target_name, target in targets.items():
            if not isinstance(target, dict):
                continue
            for key in ("dependencies", "dev-dependencies", "build-dependencies"):
                value = target.get(key)
                if isinstance(value, dict):
                    tables.append((f"target.{target_name}.{key}", value))
    return tables


def validate_rust_resolution(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    file_nodes = {node["path"]: node for node in nodes if node.get("isFileRecord")}
    modules = rust_module_declarations()
    missing_module_edges: list[tuple[str, str]] = []
    for source, module, target in modules:
        source_node = file_nodes.get(source)
        target_node = file_nodes.get(target)
        if not source_node or not target_node:
            missing_module_edges.append((source, target))
            continue
        matches = [
            edge for edge in edges
            if edge["sourceNodeId"] == source_node["nodeId"]
            and edge["targetNodeId"] == target_node["nodeId"]
            and edge.get("declaringPath") == source
            and edge.get("relation") in {"STATIC_IMPORT", "TYPE_DEPENDENCY", "MODULE_DECLARATION"}
            and edge.get("targetResolutionStatus") in INTERNAL_RESOLUTION_STATES
        ]
        if not matches:
            missing_module_edges.append((source, f"{module}->{target}"))
    if missing_module_edges:
        raise AssertionError({"unmappedRustModuleDeclarations": missing_module_edges[:50]})

    cargo_manifests = sorted(CODEBASE.rglob("Cargo.toml"))
    cargo_data: dict[Path, dict[str, Any]] = {}
    package_manifests: dict[str, Path] = {}
    for manifest in cargo_manifests:
        with manifest.open("rb") as handle:
            data = tomllib.load(handle)
        cargo_data[manifest.resolve()] = data
        package_name = data.get("package", {}).get("name")
        if isinstance(package_name, str) and package_name:
            if package_name in package_manifests:
                raise AssertionError(f"duplicate local Cargo package name: {package_name}")
            package_manifests[package_name] = manifest.resolve()
    root_manifest = (CODEBASE / "Cargo.toml").resolve()
    workspace = cargo_data[root_manifest].get("workspace", {})
    members: set[Path] = set()
    for member_pattern in workspace.get("members", []):
        for member in CODEBASE.glob(str(member_pattern)):
            manifest = (member / "Cargo.toml").resolve() if member.is_dir() else member.resolve()
            if manifest.is_file():
                members.add(manifest)
    excluded: set[Path] = set()
    for exclude_pattern in workspace.get("exclude", []):
        for item in CODEBASE.glob(str(exclude_pattern)):
            excluded.add(((item / "Cargo.toml") if item.is_dir() else item).resolve())
    members -= excluded
    if not members:
        raise AssertionError("Cargo workspace has no resolved local members")

    package_nodes = {
        node.get("qualifiedName"): node
        for node in nodes
        if node.get("nodeType") == "WORKSPACE_PACKAGE" and node.get("path", "").endswith("Cargo.toml")
    }
    root_relative = "Codebase/Cargo.toml"
    root_node = file_nodes.get(root_relative)
    missing_crates: list[str] = []
    for manifest in sorted(members):
        data = cargo_data.get(manifest)
        package_name = data.get("package", {}).get("name") if data else None
        relative = "Codebase/" + manifest.relative_to(CODEBASE).as_posix()
        package_node = package_nodes.get(package_name)
        if not data or not package_name or not package_node or package_node.get("path") != relative:
            missing_crates.append(relative)
            continue
        membership_edges = [
            edge for edge in edges
            if root_node and edge["sourceNodeId"] == root_node["nodeId"]
            and edge["targetNodeId"] == package_node["nodeId"]
            and edge.get("targetResolutionStatus") == "RESOLVED_WORKSPACE_PACKAGE"
            and edge.get("relation") in {"BUILD_REFERENCE", "WORKSPACE_MEMBER"}
        ]
        if not membership_edges:
            missing_crates.append(f"{relative}:missing workspace-member edge")
    if missing_crates:
        raise AssertionError({"unresolvedCargoWorkspaceMembers": missing_crates})

    root_workspace_deps = workspace.get("dependencies", {}) if isinstance(workspace, dict) else {}
    local_dependency_expectations: set[tuple[Path, str, Path]] = set()
    for manifest, data in cargo_data.items():
        for _, dependencies in cargo_dependency_tables(data):
            for dependency_name, value in dependencies.items():
                effective = value
                path_base = manifest.parent
                if isinstance(value, dict) and value.get("workspace") is True:
                    effective = root_workspace_deps.get(dependency_name, value)
                    path_base = root_manifest.parent
                target_manifest: Path | None = None
                if isinstance(effective, dict) and isinstance(effective.get("path"), str):
                    target_manifest = (path_base / effective["path"] / "Cargo.toml").resolve()
                elif dependency_name in package_manifests and isinstance(value, dict) and value.get("workspace") is True:
                    target_manifest = package_manifests[dependency_name]
                if target_manifest is not None:
                    local_dependency_expectations.add((manifest, dependency_name, target_manifest))
    missing_dependencies: list[str] = []
    for source_manifest, dependency_name, target_manifest in sorted(local_dependency_expectations):
        source_relative = "Codebase/" + source_manifest.relative_to(CODEBASE).as_posix()
        source_node = file_nodes.get(source_relative)
        target_data = cargo_data.get(target_manifest)
        target_name = target_data.get("package", {}).get("name") if target_data else None
        target_node = package_nodes.get(target_name)
        if not target_manifest.is_file() or not source_node or not target_node:
            missing_dependencies.append(f"{source_relative}:{dependency_name}:missing local manifest/node")
            continue
        matches = [
            edge for edge in edges
            if edge["sourceNodeId"] == source_node["nodeId"]
            and edge["targetNodeId"] == target_node["nodeId"]
            and edge.get("declaringPath") == source_relative
            and edge.get("targetResolutionStatus") == "RESOLVED_WORKSPACE_PACKAGE"
            and edge.get("relation") in {"BUILD_REFERENCE", "WORKSPACE_DEPENDENCY"}
        ]
        if not matches:
            missing_dependencies.append(f"{source_relative}:{dependency_name}->{target_name}")
    if missing_dependencies:
        raise AssertionError({"unresolvedLocalCargoDependencies": missing_dependencies[:50]})
    return {
        "status": "PASS", "rustModuleDeclarations": len(modules),
        "cargoWorkspaceMembers": len(members),
        "localCargoDependencies": len(local_dependency_expectations),
    }


def validate_evidence_objects(evidence: Any, context: str) -> None:
    if not isinstance(evidence, list) or not evidence:
        raise AssertionError(f"{context}: evidence must be a nonempty list")
    for number, item in enumerate(evidence, 1):
        if not isinstance(item, dict):
            raise AssertionError(f"{context}:{number}: evidence must be an object")
        assert_fields(item, ["path", "line", "claim"], f"{context}:{number}")
        path = codebase_path(item["path"], f"{context}:{number}")
        if not path.is_file() or not str(item["claim"]).strip():
            raise AssertionError(f"{context}:{number}: evidence path/claim is not concrete")
        line_match = re.search(r"\d+", str(item["line"]))
        if not line_match:
            raise AssertionError(f"{context}:{number}: evidence line is not numeric")
        line = int(line_match.group())
        if line <= 0 or line > len(path.read_text(encoding="utf-8").splitlines()):
            raise AssertionError(f"{context}:{number}: evidence line is outside the current source")


def validate_generated_provenance(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    nodes_by_id = {node["nodeId"]: node for node in nodes}
    generated_nodes = {
        node["path"]: node
        for node in nodes
        if node.get("isFileRecord") and node.get("layer") == "GENERATED_BINDING"
    }
    provenance_path = KG / "GENERATED_CODE_PROVENANCE.jsonl"
    records = list(iter_jsonl(provenance_path))
    if len(records) != len(generated_nodes):
        raise AssertionError(
            f"generated provenance coverage {len(records)} != generated files {len(generated_nodes)}"
        )
    paths = [row.get("generatedPath") for row in records]
    if len(paths) != len(set(paths)) or set(paths) != set(generated_nodes):
        raise AssertionError({
            "duplicateGeneratedProvenancePaths": sorted(path for path, count in Counter(paths).items() if count > 1)[:50],
            "missingGeneratedProvenance": sorted(set(generated_nodes) - set(paths))[:50],
            "unexpectedGeneratedProvenance": sorted(set(paths) - set(generated_nodes))[:50],
        })
    placeholder = re.compile(r"^(?:unknown|unverified|placeholder|tbd|todo|none|null|n/?a|unresolved|<[^>]+>)$", re.IGNORECASE)
    for number, record in enumerate(records, 1):
        missing = sorted(GENERATED_PROVENANCE_FIELDS - set(record))
        if missing:
            raise AssertionError(f"GENERATED_CODE_PROVENANCE:{number}: missing {missing}")
        context = f"GENERATED_CODE_PROVENANCE:{number}"
        serialized = json.dumps(record, sort_keys=True).upper()
        if "NEAREST_PACKAGE_JSON_HEURISTIC" in serialized or "NEAREST-PACKAGE" in serialized:
            raise AssertionError(f"{context}: nearest-package fallback is asserted as provenance")
        generated_path = record["generatedPath"]
        generated_node = generated_nodes[generated_path]
        source_path = codebase_path(generated_path, context)
        actual_hash = sha256_file(source_path)
        if (
            record["runId"] != RUN_ID
            or record["generatedArtifactNodeId"] != generated_node["nodeId"]
            or record["generatedFileSha256"] != actual_hash
            or generated_node.get("fileSha256") != actual_hash
            or record["language"] != generated_node.get("language")
        ):
            raise AssertionError(f"{context}: generated node/path/hash/language binding is stale")
        producer_ids = record["producerNodeIds"]
        producer_paths = record["producerPaths"]
        if not isinstance(producer_ids, list) or not producer_ids or not isinstance(producer_paths, list) or not producer_paths:
            raise AssertionError(f"{context}: a real producer is required")
        producer_node_paths: set[str] = set()
        for producer_id in producer_ids:
            producer = nodes_by_id.get(producer_id)
            if not producer or not producer.get("path"):
                raise AssertionError(f"{context}: producer node is missing or pathless: {producer_id}")
            producer_node_paths.add(producer["path"])
        if set(producer_paths) != producer_node_paths:
            raise AssertionError(f"{context}: producer node IDs and paths differ")
        for producer_path in producer_paths:
            if not codebase_path(producer_path, context).is_file():
                raise AssertionError(f"{context}: producer does not exist: {producer_path}")
        command = record["generatorCommand"]
        if not isinstance(command, str) or not command.strip() or placeholder.fullmatch(command.strip()):
            raise AssertionError(f"{context}: generatorCommand is missing or a placeholder")
        validate_evidence_objects(record["commandEvidence"], f"{context}:commandEvidence")
        input_paths = record["inputPaths"]
        input_schema_paths = record["inputSchemaPaths"]
        if not isinstance(input_paths, list) or not isinstance(input_schema_paths, list) or not (input_paths or input_schema_paths):
            raise AssertionError(f"{context}: concrete generator inputs or input schemas are required")
        for input_path in [*input_paths, *input_schema_paths]:
            if not codebase_path(input_path, context).is_file():
                raise AssertionError(f"{context}: generator input does not exist: {input_path}")
        consumer_ids = record["consumerNodeIds"]
        consumer_paths = record["consumerPaths"]
        if not isinstance(consumer_ids, list) or not isinstance(consumer_paths, list):
            raise AssertionError(f"{context}: consumer IDs/paths must be lists")
        consumer_node_paths: set[str] = set()
        for consumer_id in consumer_ids:
            consumer = nodes_by_id.get(consumer_id)
            if not consumer or not consumer.get("path"):
                raise AssertionError(f"{context}: consumer node is missing or pathless: {consumer_id}")
            consumer_node_paths.add(consumer["path"])
        if set(consumer_paths) != consumer_node_paths:
            raise AssertionError(f"{context}: consumer node IDs and paths differ")
        if consumer_paths:
            if record.get("consumerDiscoveryStatus") != "EVIDENCE_BACKED":
                raise AssertionError(f"{context}: discovered consumers must be marked EVIDENCE_BACKED")
            for consumer_path in consumer_paths:
                if not codebase_path(consumer_path, context).is_file():
                    raise AssertionError(f"{context}: consumer does not exist: {consumer_path}")
        else:
            if record.get("consumerDiscoveryStatus") != "NO_REPOSITORY_CONSUMER_FOUND":
                raise AssertionError(f"{context}: an empty consumer set requires explicit no-consumer status")
            if not isinstance(record.get("consumerSearchEvidence"), list) or not record["consumerSearchEvidence"]:
                raise AssertionError(f"{context}: an empty consumer set requires search evidence")
        requirements = record["regenerationRequirements"]
        if not isinstance(requirements, list) or not requirements or any(not str(value).strip() for value in requirements):
            raise AssertionError(f"{context}: regeneration requirements must be explicit")
        for status_field in ("provenanceStatus", "reviewStatus"):
            value = str(record[status_field]).strip()
            if not value or placeholder.fullmatch(value) or "HEURISTIC" in value.upper():
                raise AssertionError(f"{context}: {status_field} is not evidence-backed")

    graph = load_json(KG / "GENERATED_CODE_GRAPH.json")
    assert_fields(graph, [
        "provenanceRegistryPath", "provenanceRegistrySha256", "provenanceRecordCount",
        "generatedFilesWithProvenance", "generatedFilesMissingProvenance",
    ], "GENERATED_CODE_GRAPH")
    registry_reference = graph["provenanceRegistryPath"].replace("\\", "/")
    if registry_reference not in {
        "Graphify/05 Dependency and Impact/Knowledge Graph/GENERATED_CODE_PROVENANCE.jsonl",
        "05 Dependency and Impact/Knowledge Graph/GENERATED_CODE_PROVENANCE.jsonl",
    }:
        raise AssertionError("GENERATED_CODE_GRAPH: provenance registry path is not exact")
    if (
        graph["provenanceRegistrySha256"] != sha256_file(provenance_path)
        or graph["provenanceRecordCount"] != len(records)
        or graph["generatedFilesWithProvenance"] != len(generated_nodes)
        or graph["generatedFilesMissingProvenance"] != 0
    ):
        raise AssertionError("GENERATED_CODE_GRAPH: provenance registry hash/coverage binding is stale")
    return {"status": "PASS", "generatedFiles": len(generated_nodes), "provenanceRecords": len(records)}


def first_line_number(value: Any) -> int:
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else 0


def runtime_dimension(
    row: dict[str, Any], values_field: str, status_field: str, evidence_field: str, context: str
) -> None:
    values = row.get(values_field)
    status = row.get(status_field)
    evidence = row.get(evidence_field)
    if not isinstance(values, list):
        raise AssertionError(f"{context}: {values_field} must be a list")
    if status not in RUNTIME_DISCOVERY_STATES:
        raise AssertionError(f"{context}: {status_field} has an invalid explicit state")
    if not isinstance(evidence, list) or not evidence:
        raise AssertionError(f"{context}: {evidence_field} must explain evidence, no-match, unresolved, or suppression")
    if values and status != "EVIDENCE_BACKED":
        raise AssertionError(f"{context}: populated {values_field} must be EVIDENCE_BACKED")
    if not values and status == "EVIDENCE_BACKED":
        raise AssertionError(f"{context}: empty {values_field} cannot claim EVIDENCE_BACKED completeness")


def route_forbidden_source(relative: str, layer: str) -> bool:
    name = relative.replace("\\", "/").lower().rsplit("/", 1)[-1]
    return (
        layer in {"BUILD_AND_CONFIG", "PACKAGING_AND_DEPLOYMENT", "VENDOR_AND_TOOLCHAIN", "DOCUMENTATION_AND_LEGAL"}
        or name in {
            "yarn.lock", "podfile.lock", "package.swift", "build.rs", "package.json",
            "cargo.toml", "cargo.lock", "build.gradle", "build.gradle.kts",
            "settings.gradle", "settings.gradle.kts", "gradle.properties",
        }
        or name.endswith(".lock")
        or ".config." in name
        or name.startswith(("forge.", "capacitor.", "tailwind."))
    )


def runtime_entrypoint_reason(path: str) -> str:
    normalized = path.replace("\\", "/").lower()
    name = normalized.rsplit("/", 1)[-1]
    if name in {
        "main.ts", "main.tsx", "main.js", "main.mjs",
        "app.ts", "app.tsx", "server.ts", "preload.ts", "worker.ts", "bootstrap.ts",
    }:
        return f"explicit runtime-root filename: {name}"
    if any(token in normalized for token in ("/entrypoints/", "/entry-point/")):
        return "runtime-root directory role"
    if re.search(
        r"(?:/packages/frontend/apps/[^/]+/src|/packages/frontend/admin/src|"
        r"/packages/backend/server/src|/blocksuite/playground/apps/[^/]+)/index\."
        r"(?:ts|tsx|js|jsx|mjs|cjs)$",
        normalized,
    ):
        return "application source-root index"
    if re.search(r"/packages/frontend/apps/electron/src/(?:main|preload)/index\.(?:ts|js|mjs|cjs)$", normalized):
        return "Electron process-root index"
    return ""


def validate_runtime_registrations(
    runtime: list[dict[str, Any]], file_nodes: list[dict[str, Any]], capabilities: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> dict[str, Any]:
    files = {node["path"]: node for node in file_nodes}
    capability_ids = {row["capabilityId"] for row in capabilities}
    placeholders = re.compile(
        r"^(?:unknown|unverified|placeholder|tbd|todo|none|null|n/?a|unresolved|dynamic|\{\}|\[\]|<[^>]+>)$",
        re.IGNORECASE,
    )
    registration_ids: set[str] = set()
    runtime_entrypoint_assignments = 0
    maximum_entrypoints = 0
    for number, row in enumerate(runtime, 1):
        context = f"RUNTIME_REGISTRATION:{number}"
        registration_id = row["registrationId"]
        if registration_id in registration_ids:
            raise AssertionError(f"{context}: duplicate registrationId")
        registration_ids.add(registration_id)
        declaring = row["declaringPath"]
        file_node = files.get(declaring)
        if not file_node or not codebase_path(declaring, context).is_file():
            raise AssertionError(f"{context}: declaring source is not a current file node")
        identifier = str(row.get("registeredIdentifier", "")).strip().strip('"\'')
        if not identifier or placeholders.fullmatch(identifier):
            raise AssertionError(f"{context}: registeredIdentifier is blank or a placeholder")
        if not isinstance(row.get("evidence"), list) or not row["evidence"]:
            raise AssertionError(f"{context}: source evidence is required")
        implementations = row.get("implementationPaths")
        if not isinstance(implementations, list) or not implementations:
            raise AssertionError(f"{context}: implementationPaths must be evidence-backed and nonempty")
        for implementation in implementations:
            if implementation not in files or not codebase_path(implementation, context).is_file():
                raise AssertionError(f"{context}: implementation path is not current: {implementation}")
        runtime_dimension(row, "consumerPaths", "consumerDiscoveryStatus", "consumerSearchEvidence", context)
        runtime_dimension(row, "capabilityIds", "capabilityDiscoveryStatus", "capabilitySearchEvidence", context)
        runtime_dimension(row, "runtimeEntrypoints", "entrypointDiscoveryStatus", "entrypointSearchEvidence", context)
        if set(row["consumerPaths"]) - set(files) or set(row["runtimeEntrypoints"]) - set(files):
            raise AssertionError(f"{context}: consumer or entrypoint path is not a current file node")
        if set(row["capabilityIds"]) - capability_ids:
            raise AssertionError(f"{context}: capability discovery references an unknown capability")
        unrelated_capabilities = set(row["capabilityIds"]) - {
            capability_id
            for path in {declaring, *implementations}
            for capability_id in files[path].get("capabilityIds", [])
        }
        if unrelated_capabilities:
            raise AssertionError(
                f"{context}: consumer/entrypoint capability contamination: {sorted(unrelated_capabilities)}"
            )
        entrypoints = row["runtimeEntrypoints"]
        runtime_entrypoint_assignments += len(entrypoints)
        maximum_entrypoints = max(maximum_entrypoints, len(entrypoints))
        if len(entrypoints) > 32:
            raise AssertionError(f"{context}: implausible runtime-root fanout: {len(entrypoints)}")
        for entrypoint in entrypoints:
            if not runtime_entrypoint_reason(entrypoint):
                raise AssertionError(f"{context}: barrel/index path is not an evidence-grounded runtime root: {entrypoint}")
            if not any(
                entrypoint in str(item) and "reverse-import trace" in str(item)
                for item in row["entrypointSearchEvidence"]
            ):
                raise AssertionError(f"{context}: entrypoint lacks a concrete reverse-import trace: {entrypoint}")
        line = first_line_number(row.get("lineRange"))
        source_lines = codebase_path(declaring, context).read_text(encoding="utf-8").splitlines()
        if line <= 0 or line > len(source_lines):
            raise AssertionError(f"{context}: lineRange is not bound to current source")
        source_line = source_lines[line - 1].strip()
        if not source_line or source_line.startswith(("//", "/*", "*", "#", "<!--")):
            raise AssertionError(f"{context}: registration points to a comment/blank line")
        if row["registrationType"] == "ROUTE_REGISTRATION":
            if route_forbidden_source(declaring, file_node["layer"]):
                raise AssertionError(f"{context}: false route registration from config/build/lock manifest")
            source_window = "\n".join(source_lines[max(0, line - 3) : min(len(source_lines), line + 2)])
            route_syntax = re.search(
                r"(?:\b(?:router|app)\.(?:get|post|put|patch|delete|use)\s*\(|"
                r"@(?:Controller|Get|Post|Put|Patch|Delete)\s*\(|"
                r"<Route\b[^>]*\bpath\s*=)",
                source_window,
            )
            if not route_syntax:
                raise AssertionError(f"{context}: route is a comment/config path literal, not registration syntax")
    false_route_edges = [
        edge["edgeId"] for edge in edges
        if edge.get("relation") == "ROUTE_REGISTRATION"
        and edge.get("declaringPath") in files
        and route_forbidden_source(edge["declaringPath"], files[edge["declaringPath"]]["layer"])
    ]
    if false_route_edges:
        raise AssertionError({"falseRouteRegistrationEdges": false_route_edges[:50]})
    cross_application_entrypoints = [
        {
            "registrationId": row["registrationId"],
            "declaringPath": row["declaringPath"],
            "entrypoint": entrypoint,
        }
        for row in runtime
        if row.get("declaringPath", "").startswith(
            "Codebase/packages/backend/server/"
        )
        for entrypoint in row.get("runtimeEntrypoints", [])
        if entrypoint.startswith("Codebase/blocksuite/playground/")
    ]
    if cross_application_entrypoints:
        raise AssertionError({
            "backendRegistrationsReachedFromPlayground": cross_application_entrypoints[:50]
        })
    jsx_route_path = "Codebase/packages/frontend/admin/src/app.tsx"
    jsx_routes = [
        row for row in runtime
        if row.get("registrationType") == "ROUTE_REGISTRATION"
        and row.get("declaringPath") == jsx_route_path
        and row.get("entrypointDiscoveryStatus") == "EVIDENCE_BACKED"
        and first_line_number(row.get("lineRange")) in range(100, 145)
    ]
    if not jsx_routes:
        raise AssertionError("evidence-backed JSX <Route path=...> registrations are missing from frontend admin app.tsx")
    return {
        "status": "PASS", "registrations": len(runtime), "placeholderIdentifiers": 0,
        "falseRoutes": 0, "evidenceBackedAdminJsxRoutes": len(jsx_routes),
        "runtimeEntrypointAssignments": runtime_entrypoint_assignments,
        "maximumEntrypointsPerRegistration": maximum_entrypoints,
        "maximumAllowedEntrypointsPerRegistration": 32,
        "capabilityContamination": 0, "crossApplicationEntrypointContamination": 0,
    }


def validate_representative_mobile_edges(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    nodes_by_id = {node["nodeId"]: node for node in nodes}
    cases = [
        (
            "Swift",
            "Codebase/packages/frontend/apps/ios/App/Packages/AffinePaywall/Sources/AffinePaywall/Page/AffinePaywallPageView.swift",
            "AffineResources",
            "Codebase/packages/frontend/apps/ios/App/Packages/AffineResources/",
        ),
        (
            "Kotlin",
            "Codebase/packages/frontend/apps/android/App/app/src/main/java/app/affine/pro/AuthInitializer.kt",
            "getCurrentServerBaseUrl",
            "Codebase/packages/frontend/apps/android/App/app/src/main/java/app/affine/pro/utils/WebExt.kt",
        ),
    ]
    checked: list[str] = []
    for language, declaring, evidence_token, target_prefix in cases:
        matches = []
        for edge in edges:
            target = nodes_by_id.get(edge["targetNodeId"], {})
            evidence_text = json.dumps([edge.get("context"), edge.get("evidence")], ensure_ascii=False)
            target_path = target.get("path", "")
            if (
                edge.get("declaringPath") == declaring
                and edge.get("relation") in {"STATIC_IMPORT", "TYPE_DEPENDENCY", "BUILD_REFERENCE"}
                and edge.get("targetResolutionStatus") in INTERNAL_RESOLUTION_STATES
                and evidence_token in evidence_text
                and (target_path == target_prefix or target_path.startswith(target_prefix))
            ):
                matches.append(edge)
        if not matches:
            raise AssertionError(f"representative {language} dependency edge is missing: {declaring} -> {evidence_token}")
        checked.append(language)
    package_swift_routes = [
        edge["edgeId"] for edge in edges
        if edge.get("relation") == "ROUTE_REGISTRATION" and edge.get("declaringPath", "").endswith("/Package.swift")
    ]
    if package_swift_routes:
        raise AssertionError({"PackageSwiftFalseRouteEdges": package_swift_routes})
    language_import_keys = {
        (edge.get("declaringPath", ""), edge.get("sourceSpan", ""))
        for edge in edges
        if edge.get("evidenceOrigin") == "V2_LANGUAGE_AWARE_RESOLVER"
        and edge.get("relation") in {
            "STATIC_IMPORT", "TYPE_ONLY_IMPORT", "TYPE_DEPENDENCY", "DYNAMIC_IMPORT", "RE_EXPORT",
        }
    }
    ast_import_conflicts = [
        edge["edgeId"] for edge in edges
        if edge.get("evidenceOrigin") == "V2_VALIDATED_MERGED_AST_CACHE"
        and edge.get("relation") in {"STATIC_IMPORT", "TYPE_ONLY_IMPORT", "DYNAMIC_IMPORT", "RE_EXPORT"}
        and (edge.get("declaringPath", ""), edge.get("sourceSpan", "")) in language_import_keys
    ]
    if ast_import_conflicts:
        raise AssertionError({"ASTImportsShadowingLanguageAwareResolution": ast_import_conflicts[:50]})
    cross_language_ast_conflicts = []
    for edge in edges:
        if edge.get("evidenceOrigin") != "V2_VALIDATED_MERGED_AST_CACHE":
            continue
        source = nodes_by_id.get(edge["sourceNodeId"], {})
        target = nodes_by_id.get(edge["targetNodeId"], {})
        source_family = strict_ast_language_family(source.get("path", ""))
        target_family = strict_ast_language_family(target.get("path", ""))
        if source_family and target_family and source_family != target_family:
            cross_language_ast_conflicts.append(edge["edgeId"])
    if cross_language_ast_conflicts:
        raise AssertionError({"CrossLanguageASTConflicts": cross_language_ast_conflicts[:50]})
    swift_source = (
        "Codebase/packages/frontend/apps/ios/App/Packages/AffinePaywall/"
        "Sources/AffinePaywall/Page/AffinePaywallPageView.swift"
    )
    exact_swift_imports = {
        "L8": (
            "AffineResources",
            lambda target: target.get("nodeType") == "WORKSPACE_PACKAGE"
            and target.get("qualifiedName") == "AffineResources"
            and target.get("path", "").endswith("/AffineResources/Package.swift"),
        ),
        "L9": (
            "SwiftUI",
            lambda target: target.get("nodeType") == "EXTERNAL_PACKAGE"
            and target.get("qualifiedName") == "external:swift:SwiftUI",
        ),
    }
    for span, (specifier, target_check) in exact_swift_imports.items():
        matches = [
            edge for edge in edges
            if edge.get("declaringPath") == swift_source
            and edge.get("sourceSpan") == span
            and edge.get("evidenceOrigin") == "V2_LANGUAGE_AWARE_RESOLVER"
            and specifier in json.dumps([edge.get("context"), edge.get("evidence")], ensure_ascii=False)
            and target_check(nodes_by_id.get(edge["targetNodeId"], {}))
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"Swift import must have one exact language-aware target: {swift_source}:{span} -> {specifier}"
            )
    c_header_source = "Codebase/packages/frontend/apps/ios/App/IOSApp-Bridging-Header.h"
    c_header_target = (
        "Codebase/packages/frontend/apps/ios/App/App/uniffi/"
        "affine_mobile_nativeFFI.h"
    )
    exact_c_header_imports = [
        edge for edge in edges
        if edge.get("declaringPath") == c_header_source
        and edge.get("sourceSpan") == "L4"
        and edge.get("evidenceOrigin") == "V2_LANGUAGE_AWARE_RESOLVER"
        and nodes_by_id.get(edge["targetNodeId"], {}).get("path") == c_header_target
    ]
    if len(exact_c_header_imports) != 1:
        raise AssertionError(
            f"C header import must resolve exactly: {c_header_source}:L4 -> {c_header_target}"
        )
    raw_c_header_imports = [
        edge["edgeId"] for edge in edges
        if edge.get("declaringPath") == c_header_source
        and edge.get("sourceSpan") == "L4"
        and edge.get("evidenceOrigin") == "V2_VALIDATED_MERGED_AST_CACHE"
    ]
    if raw_c_header_imports:
        raise AssertionError({"RawCHeaderImportCollisions": raw_c_header_imports})
    return {
        "status": "PASS", "languages": checked, "representativeEdges": len(checked),
        "astImportConflicts": 0, "crossLanguageAstConflicts": 0,
        "exactSwiftImports": len(exact_swift_imports), "exactCHeaderImports": 1,
    }


def validate_ast_local_binding_collisions(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> dict[str, Any]:
    nodes_by_id = {node["nodeId"]: node for node in nodes}
    raw_path = (
        CONTROL / "Generated Tool Cache" / "v2" / RUN_ID / "ast"
        / "GRAPHIFY_RAW_MERGED.json"
    )
    raw = load_json(raw_path)
    raw_nodes = {
        str(node.get("id", "")): node
        for node in raw.get("nodes", [])
        if node.get("id")
    }
    source_text_cache: dict[str, str] = {}
    conflicts = []
    for edge in edges:
        if (
            edge.get("evidenceOrigin") != "V2_VALIDATED_MERGED_AST_CACHE"
            or edge.get("relation") in {"STATIC_IMPORT", "RE_EXPORT"}
        ):
            continue
        source = nodes_by_id.get(edge["sourceNodeId"], {})
        target = nodes_by_id.get(edge["targetNodeId"], {})
        source_path = source.get("path", "")
        target_path = target.get("path", "")
        if (
            not source_path
            or source_path == target_path
            or strict_ast_language_family(source_path) != "JAVASCRIPT_TYPESCRIPT"
        ):
            continue
        match = re.search(r"raw-edge-index:(\d+)", str(edge.get("context", "")))
        if not match:
            continue
        raw_edge = raw["edges"][int(match.group(1))]
        target_label = str(
            raw_nodes.get(str(raw_edge.get("target", "")), {}).get("label", "")
        ).strip()
        if not re.fullmatch(r"[A-Za-z_$][\w$]*", target_label):
            continue
        if source_path not in source_text_cache:
            source_text_cache[source_path] = (
                (GRAPHIFY.parent / source_path).read_text(
                    encoding="utf-8", errors="ignore"
                )
            )
        if re.search(
            rf"(?m)^[ \t]*(?:export[ \t]+)?(?:const|let|var)[ \t]+"
            rf"{re.escape(target_label)}\b",
            source_text_cache[source_path],
        ):
            conflicts.append(edge["edgeId"])
    if conflicts:
        raise AssertionError({"ASTLocalBindingCollisions": conflicts[:50]})
    return {"status": "PASS", "authoritativeLocalBindingCollisions": 0}


def validate_node_identity(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    manifest_property_symbols = [
        node["nodeId"] for node in nodes
        if node.get("nodeType") == "SYMBOL"
        and Path(str(node.get("path", ""))).name.lower() == "package.json"
    ]
    if manifest_property_symbols:
        raise AssertionError({"packageJsonPropertySymbols": manifest_property_symbols[:50]})
    return {"status": "PASS", "packageJsonPropertySymbols": 0}


def validate_removal_capability_semantics(
    capabilities: list[dict[str, Any]], changes: list[dict[str, Any]]
) -> dict[str, Any]:
    expected = {
        "MR-CAP-041": (
            "MULTIPLE_PRESENT",
            {
                "Codebase/packages/backend/server/src/core/workspaces/doc-realtime.ts",
                "Codebase/packages/frontend/core/src/desktop/pages/workspace/share/share-page.utils.ts",
                "Codebase/packages/frontend/core/src/modules/share-doc/stores/share-docs.ts",
                "Codebase/packages/frontend/core/src/modules/share-doc/stores/share.ts",
                "Codebase/packages/frontend/core/src/modules/share-setting/stores/share-setting.ts",
            },
        ),
        "MR-CAP-055": (
            "PRESENT",
            {"Codebase/blocksuite/affine/blocks/embed/src/embed-iframe-block/configs/providers/google-docs.ts"},
        ),
        "MR-CAP-056": ("NO_ACTIVE_IMPLEMENTATION_FOUND", set()),
        "MR-CAP-057": ("NO_ACTIVE_IMPLEMENTATION_FOUND", set()),
        "MR-CAP-062": (
            "MULTIPLE_PRESENT",
            {
                "Codebase/packages/frontend/core/src/modules/import-template/entities/downloader.ts",
                "Codebase/packages/frontend/core/src/modules/import-template/services/downloader.ts",
                "Codebase/packages/frontend/core/src/modules/import-template/store/downloader.ts",
            },
        ),
    }
    capability_by_id = {row["capabilityId"]: row for row in capabilities}
    change_by_id = {row["capabilityId"]: row for row in changes}
    task_by_id = {
        row["capabilityId"]: row
        for row in iter_jsonl(GRAPHIFY / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl")
    }
    retained_count = 0
    for capability_id, (status, paths) in expected.items():
        capability = capability_by_id[capability_id]
        change = change_by_id[capability_id]
        task = task_by_id[capability_id]
        evidence = capability.get("currentLocationEvidence", {})
        retained = set(evidence.get("retainedExcludedPaths", []))
        expected_allowed = paths | (
            {f"Graphify/08 Cleanup/Quarantine/{capability_id}"} if paths else set()
        )
        allowed = set(task.get("allowedPaths", []))
        forbidden = set(task.get("forbiddenPaths", []))
        retained_count += len(retained)
        if (
            capability.get("currentLocationStatus") != status
            or set(capability.get("currentPaths", [])) != paths
            or set(evidence.get("activeImplementationPaths", [])) != paths
            or paths & retained
            or set(change.get("currentPaths", [])) != paths
            or set(change.get("removeLater", [])) != paths
            or set(task.get("exactCurrentPaths", [])) != paths
            or allowed != expected_allowed
            or allowed & retained
            or not retained <= forbidden
        ):
            raise AssertionError(
                f"source-exact removal capability semantics drifted: {capability_id}"
            )
    return {
        "status": "PASS",
        "capabilitiesChecked": len(expected),
        "activePathCounts": {
            capability_id: len(paths)
            for capability_id, (_, paths) in expected.items()
        },
        "retainedFalsePositiveExclusions": retained_count,
    }


def finalize_graph_validation(
    json_result: dict[str, Any], schema_result: dict[str, Any],
    baseline_result: dict[str, Any], reference_result: dict[str, Any],
) -> dict[str, Any]:
    graph_validation_path = KG / "GRAPH_VALIDATION.json"
    graph_validation = load_json(graph_validation_path, {})
    required_checks = {
        "sourceFilesExist", "sourceHashesCurrent", "jsonParsingPassed",
        "schemaInstancesValidated", "resolverAssertionsPassed", "layerAssertionsPassed",
        "selfLoopAssertionsPassed", "generatedProvenancePassed",
        "runtimeRegistrationAssertionsPassed", "astBatchManifestValidated",
    }
    extraction_path = CONTROL / "Generated Tool Cache" / "v2" / RUN_ID / "ast" / "EXTRACTION_MANIFEST.json"
    merge_path = extraction_path.parent / "MERGE_RECEIPT.json"
    nodes_path = KG / "NODES.jsonl"
    edges_path = KG / "EDGES.jsonl"
    loop_path = KG / "SELF_LOOP_CLASSIFICATION.jsonl"
    provenance_path = KG / "GENERATED_CODE_PROVENANCE.jsonl"
    runtime_path = GRAPHIFY / "02 Architecture Map" / "RUNTIME_REGISTRATION_REGISTRY.jsonl"
    checks = dict(graph_validation.get("checks", {}))
    checks.update({check: True for check in required_checks})
    evidence = {
        "sourceFilesExist": {
            "path": "Graphify/00 Execution Control/GRAPHIFY_REPAIR_MANIFEST.json",
            "sha256": sha256_file(CONTROL / "GRAPHIFY_REPAIR_MANIFEST.json"),
            "count": baseline_result["fileCount"],
        },
        "sourceHashesCurrent": {
            "path": "Graphify/00 Execution Control/GRAPHIFY_REPAIR_BASELINE.json",
            "sha256": sha256_file(CONTROL / "GRAPHIFY_REPAIR_BASELINE.json"),
            "count": baseline_result["fileCount"],
            "treeSha256": baseline_result["afterTreeSha256"],
        },
        "jsonParsingPassed": {
            "path": "Graphify/11 Completion/validate_graphify_mapping.py",
            "sha256": sha256_file(Path(__file__)),
            "count": json_result["jsonFilesParsed"] + json_result["jsonlRecordsParsed"],
        },
        "schemaInstancesValidated": {
            "path": "Graphify/00 Execution Control/schemas",
            "sha256": sha256_bytes(json.dumps(schema_result["schemaInstanceResults"], sort_keys=True).encode("utf-8")),
            "count": schema_result["schemaInstancesValidated"], "errorCount": 0,
        },
        "resolverAssertionsPassed": {
            "path": edges_path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(edges_path), "count": reference_result["directedEdges"],
            "rustModuleDeclarations": reference_result["rustResolution"]["rustModuleDeclarations"],
            "symbolDependencyEdges": reference_result["builderIdempotence"]["symbolDependencyEdges"],
        },
        "layerAssertionsPassed": {
            "path": nodes_path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(nodes_path), "count": reference_result["fileNodes"],
            **reference_result["layerAssertions"],
        },
        "selfLoopAssertionsPassed": {
            "path": loop_path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(loop_path),
            "count": reference_result["selfLoopAssertions"]["classificationRecords"],
            "authoritativeSelfLoops": reference_result["selfLoopAssertions"]["authoritativeSelfLoops"],
        },
        "generatedProvenancePassed": {
            "path": provenance_path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(provenance_path),
            "count": reference_result["generatedProvenance"]["provenanceRecords"],
        },
        "runtimeRegistrationAssertionsPassed": {
            "path": runtime_path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(runtime_path), "count": reference_result["runtimeRegistrations"],
            "jsxRoutes": reference_result["runtimeAssertions"]["evidenceBackedAdminJsxRoutes"],
        },
        "astBatchManifestValidated": {
            "path": extraction_path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(extraction_path), "count": json_result["astValidation"]["batchCount"],
            "mergeReceiptPath": merge_path.relative_to(GRAPHIFY.parent).as_posix(),
            "mergeReceiptSha256": sha256_file(merge_path),
        },
    }
    graph_validation.update({
        "runId": RUN_ID, "status": "PASS", "checks": checks, "evidence": evidence,
        "validationAuthority": "VALIDATOR_ASSERTIONS_COMPLETED_NOT_BUILDER_PREASSERTION",
        "validatedAt": now_utc(),
    })
    write_json(graph_validation_path, graph_validation)
    written = load_json(graph_validation_path)
    if any(written["checks"].get(check) is not True for check in required_checks):
        raise AssertionError("GRAPH_VALIDATION finalization did not persist every passed assertion")
    if any(written["evidence"].get(check) in ({}, [], "", None) for check in required_checks):
        raise AssertionError("GRAPH_VALIDATION finalization lacks concrete per-check evidence")
    return {"status": "PASS", "evidenceBackedChecks": len(required_checks)}


TIMESTAMP_KEYS = {
    "generatedAt", "validatedAt", "completedAt", "startedAt", "finishedAt",
    "lastUpdatedAt", "verificationTimestamp", "timestamp", "updatedAt", "createdAt",
}


def normalize_build_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize_build_value(item)
            for key, item in sorted(value.items())
            if key not in TIMESTAMP_KEYS
        }
    if isinstance(value, list):
        return [normalize_build_value(item) for item in value]
    return value


def normalized_build_output_hash(relative_paths: list[str]) -> str:
    canonical_parts: list[str] = []
    for relative in sorted(relative_paths):
        normalized_relative = relative.replace("\\", "/")
        path = graphify_path(normalized_relative.removeprefix("Graphify/"), "graph build output")
        if not path.is_file() or path.suffix not in {".json", ".jsonl"}:
            raise AssertionError(f"graph build output is missing or not JSON/JSONL: {relative}")
        if path.suffix == ".jsonl":
            value: Any = list(iter_jsonl(path))
        else:
            value = load_json(path)
        normalized = normalize_build_value(value)
        canonical_parts.append(
            normalized_relative + "\0"
            + json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        )
    return sha256_bytes("\n".join(canonical_parts).encode("utf-8"))


def validate_builder_inputs_and_idempotence(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    ast_root = CONTROL / "Generated Tool Cache" / "v2" / RUN_ID / "ast"
    extraction_path = ast_root / "EXTRACTION_MANIFEST.json"
    merge_path = ast_root / "MERGE_RECEIPT.json"
    raw_path = ast_root / "GRAPHIFY_RAW_MERGED.json"
    extraction = load_json(extraction_path)
    merge = load_json(merge_path)
    assert_fields(merge, [
        "schemaVersion", "runId", "status", "inputManifestSha256", "partitionValidation",
        "outputPath", "outputSha256", "nodeCount", "edgeCount", "authoritative", "completedAt",
    ], "AST merge receipt")
    if (
        merge["schemaVersion"] != "mindroom.graphify.merge-receipt.v2"
        or merge["runId"] != RUN_ID
        or merge["status"] != "COMPLETE"
        or merge["inputManifestSha256"] != sha256_file(extraction_path)
        or merge["partitionValidation"] != extraction["partitionValidation"]
        or merge["authoritative"] is not False
    ):
        raise AssertionError("AST merge receipt is stale, incomplete, or not bound to the current extraction manifest")
    expected_raw_relative = raw_path.relative_to(GRAPHIFY).as_posix()
    if merge["outputPath"] != expected_raw_relative or merge["outputSha256"] != sha256_file(raw_path):
        raise AssertionError("AST merge receipt is not bound to current GRAPHIFY_RAW_MERGED")
    raw = load_json(raw_path)
    if (
        raw.get("runId") != RUN_ID
        or raw.get("authoritative") is not False
        or raw.get("extractionPolicyVersion") != AST_POLICY_VERSION
        or not isinstance(raw.get("nodes"), list)
        or not isinstance(raw.get("edges"), list)
        or merge["nodeCount"] != len(raw["nodes"])
        or merge["edgeCount"] != len(raw["edges"])
    ):
        raise AssertionError("GRAPHIFY_RAW_MERGED is stale or differs from its COMPLETE merge receipt")

    builder_path = COMPLETION / "build_graphify_v2.py"
    builder_text = builder_path.read_text(encoding="utf-8")
    active_dependency_input = re.search(
        r"(?m)^\s*(?:OLD_EDGE_PATH|\w*INPUT\w*|\w*DIAGNOSTIC\w*)\s*=\s*"
        r"GRAPHIFY\s*/\s*[\"']05 Dependency and Impact[\"']\s*/\s*[\"']DEPENDENCY_EDGES\.jsonl[\"']",
        builder_text,
    )
    if active_dependency_input:
        raise AssertionError("graph builder reads the active DEPENDENCY_EDGES output as an input")
    for required_literal in ("GRAPHIFY_RAW_MERGED.json", "MERGE_RECEIPT.json", "legacy-v1"):
        if required_literal not in builder_text:
            raise AssertionError(f"graph builder does not declare required fresh/preserved input: {required_literal}")

    nodes_by_id = {node["nodeId"]: node for node in nodes}
    symbol_edges = [
        edge for edge in edges
        if edge.get("relation") != "CONTAINS_SYMBOL"
        and (
            nodes_by_id.get(edge["sourceNodeId"], {}).get("nodeType") == "SYMBOL"
            or nodes_by_id.get(edge["targetNodeId"], {}).get("nodeType") == "SYMBOL"
        )
    ]
    symbol_relations = {edge["relation"] for edge in symbol_edges}
    if len(symbol_edges) < 100 or len(symbol_relations) < 2:
        raise AssertionError({
            "nonContainmentSymbolEdges": len(symbol_edges),
            "symbolDependencyRelationTypes": sorted(symbol_relations),
        })

    receipt_path = COMPLETION / "GRAPH_BUILD_RUNS.jsonl"
    receipts = [row for row in iter_jsonl(receipt_path) if row.get("status") == "COMPLETE"]
    if len(receipts) < 2:
        raise AssertionError("two consecutive COMPLETE graph build receipts are required")
    latest = receipts[-2:]
    required_receipt_fields = {
        "runId", "status", "buildId", "rawMergedSha256", "extractionManifestSha256",
        "mergeReceiptSha256", "builderSha256", "preservedV1DiagnosticPath",
        "preservedV1DiagnosticSha256", "outputPaths", "normalizedOutputSha256",
        "nodeCount", "edgeCount", "symbolEdgeCount", "completedAt",
    }
    current_inputs = {
        "rawMergedSha256": sha256_file(raw_path),
        "extractionManifestSha256": sha256_file(extraction_path),
        "mergeReceiptSha256": sha256_file(merge_path),
        "builderSha256": sha256_file(builder_path),
    }
    for index, receipt in enumerate(latest, 1):
        missing = sorted(required_receipt_fields - set(receipt))
        if missing:
            raise AssertionError(f"GRAPH_BUILD_RUNS latest-{index}: missing {missing}")
        if any(receipt.get(field) != value for field, value in current_inputs.items()):
            raise AssertionError(f"GRAPH_BUILD_RUNS latest-{index}: input hash binding is stale")
        legacy_relative = receipt["preservedV1DiagnosticPath"].replace("\\", "/")
        if "Generated Tool Cache/legacy-v1/" not in legacy_relative:
            raise AssertionError(f"GRAPH_BUILD_RUNS latest-{index}: V1 input is not preserved legacy evidence")
        legacy_path = graphify_path(legacy_relative.removeprefix("Graphify/"), f"GRAPH_BUILD_RUNS latest-{index}")
        if not legacy_path.is_file() or receipt["preservedV1DiagnosticSha256"] != sha256_file(legacy_path):
            raise AssertionError(f"GRAPH_BUILD_RUNS latest-{index}: preserved V1 diagnostic hash is stale")
        if (
            receipt["nodeCount"] != len(nodes)
            or receipt["edgeCount"] != len(edges)
            or receipt["symbolEdgeCount"] != len(symbol_edges)
        ):
            raise AssertionError(f"GRAPH_BUILD_RUNS latest-{index}: graph cardinalities are stale")
    if latest[0]["outputPaths"] != latest[1]["outputPaths"]:
        raise AssertionError("consecutive graph builds did not cover the same output set")
    normalized_hash = normalized_build_output_hash(latest[1]["outputPaths"])
    if {row["normalizedOutputSha256"] for row in latest} != {normalized_hash}:
        raise AssertionError("two consecutive graph builds are not stable after timestamp normalization")
    return {
        "status": "PASS", "rawMergedNodes": len(raw["nodes"]), "rawMergedEdges": len(raw["edges"]),
        "symbolDependencyEdges": len(symbol_edges), "symbolDependencyRelationTypes": len(symbol_relations),
        "consecutiveStableBuilds": 2, "normalizedOutputSha256": normalized_hash,
    }


def validate_references() -> dict[str, Any]:
    nodes = list(iter_jsonl(KG / "NODES.jsonl"))
    edges = list(iter_jsonl(KG / "EDGES.jsonl"))
    node_ids = {node["nodeId"] for node in nodes}
    if len(node_ids) != len(nodes):
        raise AssertionError("duplicate node IDs")
    edge_ids = {edge["edgeId"] for edge in edges}
    if len(edge_ids) != len(edges):
        raise AssertionError("duplicate edge IDs")
    dangling = [edge["edgeId"] for edge in edges if edge["sourceNodeId"] not in node_ids or edge["targetNodeId"] not in node_ids]
    invalid_states = [edge["edgeId"] for edge in edges if edge["sourceResolutionStatus"] not in RESOLUTION_STATES or edge["targetResolutionStatus"] not in RESOLUTION_STATES]
    authoritative_invalid = [edge["edgeId"] for edge in edges if edge["sourceResolutionStatus"] in {"UNRESOLVED_INTERNAL", "INVALID_REFERENCE"} or edge["targetResolutionStatus"] in {"UNRESOLVED_INTERNAL", "INVALID_REFERENCE"}]
    if dangling or invalid_states or authoritative_invalid:
        raise AssertionError({"dangling": dangling[:10], "invalidStates": invalid_states[:10], "invalidAuthoritative": authoritative_invalid[:10]})
    registry = list(iter_jsonl(KG / "NODE_ID_REGISTRY.jsonl"))
    if {row["nodeId"] for row in registry} != node_ids:
        raise AssertionError("node registry and node store differ")
    file_nodes = [node for node in nodes if node.get("isFileRecord")]
    if len(file_nodes) != BASELINE["codebaseFileCount"]:
        raise AssertionError(f"file node coverage {len(file_nodes)} != {BASELINE['codebaseFileCount']}")
    if any(not node.get("layer") for node in file_nodes):
        raise AssertionError("unclassified file node")
    file_node_paths = [node.get("path") for node in file_nodes]
    current_sources = {row["path"]: row for row in source_hash_manifest()}
    if len(file_node_paths) != len(set(file_node_paths)) or set(file_node_paths) != set(current_sources):
        raise AssertionError({
            "duplicateFileNodePaths": sorted(path for path, count in Counter(file_node_paths).items() if count > 1)[:50],
            "missingFileNodes": sorted(set(current_sources) - set(file_node_paths))[:50],
            "unexpectedFileNodes": sorted(set(file_node_paths) - set(current_sources))[:50],
        })
    stale_file_nodes = [
        node["path"] for node in file_nodes
        if node.get("fileSha256") != current_sources[node["path"]]["sha256"]
    ]
    if stale_file_nodes:
        raise AssertionError({"fileNodesWithStaleSourceHashes": stale_file_nodes[:50]})
    layer_result = validate_layer_exclusions(file_nodes)
    self_loop_result = validate_self_loops(nodes, edges)
    rust_result = validate_rust_resolution(nodes, edges)
    generated_result = validate_generated_provenance(nodes)
    mobile_result = validate_representative_mobile_edges(nodes, edges)
    ast_local_binding_result = validate_ast_local_binding_collisions(nodes, edges)
    node_identity_result = validate_node_identity(nodes)
    diagnostics = list(iter_jsonl(GRAPHIFY / "05 Dependency and Impact" / "UNRESOLVED_ENDPOINTS.jsonl"))
    blockers = [row for row in diagnostics if row["remainingBlocker"]]
    if blockers:
        raise AssertionError(f"diagnostic endpoint blockers remain: {len(blockers)}")
    requirements = list(iter_jsonl(GRAPHIFY / "03 Capability Map" / "REQUIREMENT_REGISTRY.jsonl"))
    capabilities = load_json(GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json")["capabilities"]
    changes = list(iter_jsonl(GRAPHIFY / "04 Exact Location Registry" / "CHANGE_LOCATION_REGISTRY.jsonl"))
    trace = list(iter_jsonl(GRAPHIFY / "04 Exact Location Registry" / "CHANGE_TRACEABILITY_MATRIX.jsonl"))
    cap_ids = {cap["capabilityId"] for cap in capabilities}
    req_ids = {req["requirementId"] for req in requirements}
    if len(requirements) != 2055 or len(capabilities) != 161 or len(changes) != 161 or len(trace) != 2055:
        raise AssertionError(f"requirement/capability/change cardinality mismatch: reqs={len(requirements)}, caps={len(capabilities)}, changes={len(changes)}, trace={len(trace)}")
    trace_req_ids = {row["requirementId"] for row in trace if "requirementId" in row}
    trace_exp_req_ids = {rid for row in trace if "requirementIds" in row for rid in row.get("requirementIds", [])}
    if not (trace_req_ids | trace_exp_req_ids).issubset(req_ids):
        raise AssertionError("change trace contains invalid requirement reference")
    if any(set(req["capabilityIds"]) - cap_ids for req in requirements):
        raise AssertionError("requirement references unknown capability")
    if any(cap.get("currentLocationStatus") == "SEARCH_INCOMPLETE" for cap in capabilities):
        raise AssertionError("capability location search remains incomplete")
    removal_semantics_result = validate_removal_capability_semantics(capabilities, changes)
    runtime = list(iter_jsonl(GRAPHIFY / "02 Architecture Map" / "RUNTIME_REGISTRATION_REGISTRY.jsonl"))
    if len(runtime) <= 35:
        raise AssertionError("runtime registration mapping did not expand beyond V1")
    runtime_result = validate_runtime_registrations(runtime, file_nodes, capabilities, edges)
    builder_result = validate_builder_inputs_and_idempotence(nodes, edges)
    output_names = {path.name for path in (COMPLETION / "graphify-out").iterdir() if path.is_file() or path.is_dir()}
    if output_names != ALLOWED_OUT:
        raise AssertionError(f"final graphify-out hygiene failed: {sorted(output_names)}")
    release = load_json(COMPLETION / "FINAL_RELEASE_RECEIPT.json")
    if release.get("status") != "NOT_VERIFIED" or release.get("allGatesPassed") or release.get("completionBannerUnlocked") or not release.get("locked"):
        raise AssertionError("final release receipt is not locked")
    if any(release.get("gates", {}).values()):
        raise AssertionError("application release gate unexpectedly true")
    return {
        "status": "PASS", "nodes": len(nodes), "directedEdges": len(edges), "danglingAuthoritativeEdges": 0,
        "unresolvedInternalEndpoints": 0, "invalidReferences": 0, "fileNodes": len(file_nodes),
        "requirements": len(requirements), "capabilities": len(capabilities), "requiredChanges": len(changes),
        "runtimeRegistrations": len(runtime), "completionOutputFiles": sorted(output_names),
        "layerAssertions": layer_result, "selfLoopAssertions": self_loop_result,
        "rustResolution": rust_result, "generatedProvenance": generated_result,
        "representativeMobileEdges": mobile_result, "nodeIdentity": node_identity_result,
        "astLocalBindingCollisions": ast_local_binding_result,
        "removalCapabilitySemantics": removal_semantics_result, "runtimeAssertions": runtime_result,
        "builderIdempotence": builder_result,
    }


def validate_affine_reference() -> dict[str, Any]:
    reference = GRAPHIFY / "14 AFFiNE Reference"
    manifest = load_json(reference / "AFFINE_REFERENCE_MANIFEST.json")
    source_receipt = load_json(reference / "OFFICIAL_SOURCE_RECEIPT.json")
    parity = load_json(reference / "AFFINE_PARITY_VALIDATION.json")
    inventory = load_json(reference / "AFFINE_PACKAGE_INVENTORY.json")
    index_rows = list(iter_jsonl(reference / "AFFINE_CAPABILITY_INDEX.jsonl"))
    candidates = list(
        iter_jsonl(reference / "AFFINE_TRANSPLANT_CANDIDATES.jsonl")
    )
    capabilities = load_json(
        GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json"
    )["capabilities"]
    capability_by_id = {row["capabilityId"]: row for row in capabilities}
    expected_ids = {row["capabilityId"] for row in index_rows}
    commit = "da7781a75171140fd966c6cfbe05da9f1fb111d6"
    tree_sha = "4f7b0d6657efa7e9ee0c1e3359e09a21eb8e145f"
    version = "0.26.3"
    archive_root = f"AFFiNE-{commit}/"
    archive_path = reference / "Incoming" / "AFFiNE-canary.zip"
    reference_tree = reference / "Reference Tree"

    if (
        manifest.get("status") != "REFERENCE_VERIFIED"
        or manifest.get("parityCompleted") is not True
        or manifest.get("externalBlocker")
        or manifest.get("implementationPerformed") is not False
    ):
        raise AssertionError("AFFiNE manifest is not a completed mapping-only reference")
    verified = manifest.get("verifiedArchiveMetadata", {})
    if (
        verified.get("commit") != commit
        or verified.get("treeSha") != tree_sha
        or verified.get("version") != version
        or not archive_path.is_file()
        or verified.get("sha256") != sha256_file(archive_path)
        or verified.get("sizeBytes") != archive_path.stat().st_size
    ):
        raise AssertionError("AFFiNE archive provenance metadata is stale")

    archive_sha = verified["sha256"]
    extraction_digest = hashlib.sha256()
    extracted_count = 0
    with zipfile.ZipFile(archive_path) as archive:
        if archive.comment.decode("ascii", errors="replace") != commit:
            raise AssertionError("AFFiNE ZIP comment does not pin the expected commit")
        if archive.testzip() is not None:
            raise AssertionError("AFFiNE ZIP CRC validation failed")
        infos = [info for info in archive.infolist() if not info.is_dir()]
        if len(infos) != 10109 or any(
            not info.filename.startswith(archive_root) for info in infos
        ):
            raise AssertionError("AFFiNE archive root or file cardinality is invalid")
        entries = {
            info.filename[len(archive_root) :]: info
            for info in infos
        }
        root_package = json.loads(archive.read(entries["package.json"]))
        if root_package.get("version") != version:
            raise AssertionError("AFFiNE root package version is not 0.26.3")
        for relative in sorted(entries):
            data = archive.read(entries[relative])
            file_sha = sha256_bytes(data)
            extraction_digest.update(
                f"{relative}\0{len(data)}\0{file_sha}\n".encode("utf-8")
            )
            extracted = filesystem_path(reference_tree / relative)
            if (
                not extracted.is_file()
                or extracted.stat().st_size != len(data)
                or sha256_file(extracted) != file_sha
            ):
                raise AssertionError(
                    f"AFFiNE extracted reference differs from archive: {relative}"
                )
            extracted_count += 1

        if (
            len(index_rows) != len(expected_ids)
            or {row.get("capabilityId") for row in index_rows} != expected_ids
            or len(candidates) != len(expected_ids)
            or {row.get("capabilityId") for row in candidates} != expected_ids
        ):
            raise AssertionError("AFFiNE capability/candidate ID coverage is incomplete")
        evidence_pairs = identical_pairs = version_delta_pairs = 0
        active_only_count = 0
        for row in index_rows:
            capability_id = row["capabilityId"]
            if (
                row.get("classification")
                != capability_by_id[capability_id].get("classification")
                or row.get("searchStatus") != "SEARCH_COMPLETE"
                or row.get("comparisonStatus")
                in {"ARCHIVE_UNAVAILABLE", "NOT_COMPUTABLE", "SEARCH_INCOMPLETE"}
                or row.get("blockers")
                or row.get("transplantApproved") is not False
                or row.get("inventionApproved") is not False
            ):
                raise AssertionError(
                    f"AFFiNE parity row is incomplete: {capability_id}"
                )
            for field in ("activePaths", "referencePaths", "activeOnlyPaths"):
                values = row.get(field)
                if not isinstance(values, list) or values != sorted(set(values)):
                    raise AssertionError(
                        f"AFFiNE parity result set is not complete/sorted: {capability_id}:{field}"
                    )
            if not row.get("referenceSearchQueries"):
                raise AssertionError(
                    f"AFFiNE parity row lacks executed queries: {capability_id}"
                )
            evidence = row.get("referencePathEvidence", [])
            if len(
                {
                    (item.get("activePath"), item.get("referencePath"))
                    for item in evidence
                }
            ) != len(evidence):
                raise AssertionError(
                    f"AFFiNE parity evidence duplicates pairs: {capability_id}"
                )
            for item in evidence:
                active_path = CODEBASE.parent / item["activePath"]
                reference_relative = item["referencePath"].removeprefix(
                    "Graphify/14 AFFiNE Reference/Reference Tree/"
                )
                if (
                    not active_path.is_file()
                    or item["activeSha256"] != sha256_file(active_path)
                    or reference_relative not in entries
                    or item["referenceSha256"]
                    != sha256_bytes(archive.read(entries[reference_relative]))
                ):
                    raise AssertionError(
                        f"AFFiNE path/hash evidence is stale: {capability_id}"
                    )
                expected_content_status = (
                    "IDENTICAL"
                    if item["activeSha256"] == item["referenceSha256"]
                    else "VERSION_DELTA"
                )
                if item.get("contentStatus") != expected_content_status:
                    raise AssertionError(
                        f"AFFiNE content classification is wrong: {capability_id}"
                    )
                evidence_pairs += 1
                identical_pairs += expected_content_status == "IDENTICAL"
                version_delta_pairs += expected_content_status == "VERSION_DELTA"
            for active_only in row["activeOnlyPaths"]:
                active_path = CODEBASE.parent / active_only
                relative = active_only.removeprefix("Codebase/")
                if not active_path.is_file() or relative in entries:
                    raise AssertionError(
                        f"AFFiNE active-only result is stale: {capability_id}:{active_only}"
                    )
                active_only_count += 1

        package_rows = inventory.get("packages", [])
        if (
            inventory.get("sourceVersion") != version
            or inventory.get("sourceCommit") != commit
            or inventory.get("sourceTreeSha") != tree_sha
            or inventory.get("archiveSha256") != archive_sha
            or inventory.get("packageCounts", {}).get("total") != 135
            or len(package_rows) != 135
        ):
            raise AssertionError("AFFiNE package inventory is stale")
        for package in package_rows:
            relative = package["manifestPath"].removeprefix(
                "Graphify/14 AFFiNE Reference/Reference Tree/"
            )
            if (
                relative not in entries
                or package.get("manifestSha256")
                != sha256_bytes(archive.read(entries[relative]))
            ):
                raise AssertionError(
                    f"AFFiNE package inventory path/hash is stale: {relative}"
                )

    candidates_by_id = {row["capabilityId"]: row for row in candidates}
    if any(
        row.get("approved") is not False
        or row.get("implementationPerformed") is not False
        or row.get("copiedFiles")
        or row.get("adaptedFiles")
        for row in candidates_by_id.values()
    ):
        raise AssertionError("AFFiNE transplant implementation was unexpectedly approved")
    if (
        parity.get("status") != "PASS"
        or parity.get("capabilityCount") != len(expected_ids)
        or parity.get("searchIncompleteCapabilities") != 0
        or parity.get("archiveSha256") != archive_sha
        or parity.get("evidencePairCount") != evidence_pairs
        or parity.get("identicalPairCount") != identical_pairs
        or parity.get("versionDeltaPairCount") != version_delta_pairs
        or manifest.get("capabilitiesCompared") != len(expected_ids)
        or manifest.get("searchIncompleteCapabilities") != 0
        or manifest.get("capabilityEvidencePairs") != evidence_pairs
        or manifest.get("transplantCandidatesMapped") != len(expected_ids)
        or manifest.get("transplantCandidatesApproved") != 0
    ):
        raise AssertionError("AFFiNE derived parity counters are stale")
    archive_validation = manifest.get("archiveAndExtractionValidation", {})
    if (
        archive_validation.get("status") != "PASS"
        or archive_validation.get("archiveFileCount") != extracted_count
        or archive_validation.get("extractedFileCount") != extracted_count
        or archive_validation.get("canonicalContentTreeSha256")
        != extraction_digest.hexdigest()
    ):
        raise AssertionError("AFFiNE archive/extraction receipt is stale")
    if (
        source_receipt.get("status") != "VERIFIED_PINNED_OFFICIAL_SOURCE"
        or source_receipt.get("archiveSha256") != archive_sha
        or source_receipt.get("commit") != commit
        or source_receipt.get("treeSha") != tree_sha
        or source_receipt.get("version") != version
        or source_receipt.get("expectedContainerHashMatch") is not False
        or not source_receipt.get("mismatchDisposition")
    ):
        raise AssertionError("AFFiNE official-source receipt is incomplete")
    return {
        "status": "PASS",
        "commit": commit,
        "treeSha": tree_sha,
        "version": version,
        "archiveSha256": archive_sha,
        "archiveFiles": extracted_count,
        "capabilities": len(index_rows),
        "evidencePairs": evidence_pairs,
        "identicalPairs": identical_pairs,
        "versionDeltaPairs": version_delta_pairs,
        "activeOnlyPaths": active_only_count,
        "packages": len(package_rows),
        "approvedTransplants": 0,
        "implementationPerformed": False,
    }


def independent_review() -> dict[str, Any]:
    rows = list(iter_jsonl(GRAPHIFY / "13 Agent Swarm" / "AGENT_REVIEWS.jsonl"))
    final = [row for row in rows if row.get("runId") == RUN_ID and row.get("reviewType") == "INDEPENDENT_V2_FINAL"]
    if not final:
        return {"status": "PENDING", "passed": False, "reviewId": ""}
    latest = final[-1]
    required = [
        "Graphify/14 AFFiNE Reference/AFFINE_REFERENCE_MANIFEST.json",
        "Graphify/14 AFFiNE Reference/AFFINE_CAPABILITY_INDEX.jsonl",
        "Graphify/14 AFFiNE Reference/AFFINE_TRANSPLANT_CANDIDATES.jsonl",
        "Graphify/14 AFFiNE Reference/AFFINE_PACKAGE_INVENTORY.json",
        "Graphify/14 AFFiNE Reference/AFFINE_PARITY_VALIDATION.json",
    ]
    artifact_evidence = latest.get("artifactEvidence", {})
    hashes_fresh = all(
        (GRAPHIFY.parent / relative).is_file()
        and artifact_evidence.get(relative)
        == sha256_file(GRAPHIFY.parent / relative)
        for relative in required
    )
    passed = latest.get("decision") == "APPROVED" and hashes_fresh
    return {
        "status": (
            latest.get("decision", "PENDING")
            if hashes_fresh
            else "STALE_ARTIFACT_HASH_BINDING"
        ),
        "passed": passed,
        "reviewId": latest.get("reviewId", ""),
        "reviewer": latest.get("reviewer", ""),
        "artifactHashesFresh": hashes_fresh,
    }


def update_receipt_validation_gates(validation_evidence: str) -> None:
    receipt = load_json(RECEIPT_PATH)
    gate_evidence = receipt.setdefault("gateEvidence", {})
    for gate, passed in receipt.get("gates", {}).items():
        if not passed:
            continue
        records = gate_evidence.get(gate, [])
        if not records:
            raise AssertionError(f"true mapping gate has no evidence record: {gate}")
        refreshed = []
        for record in records:
            relative = record.get("path", "")
            path = GRAPHIFY.parent / relative
            if not relative or not path.is_file():
                raise AssertionError(f"true mapping gate evidence is missing: {gate}: {relative}")
            refreshed.append({"path": relative, "sha256": sha256_file(path)})
        gate_evidence[gate] = refreshed
    evidence_hash = sha256_file(GRAPHIFY.parent / validation_evidence)
    for gate in ("allJsonValidated", "allJsonlValidated", "allSchemasValidated", "referentialIntegrityPassed", "graphHealthPassed"):
        receipt["gates"][gate] = True
        gate_evidence[gate] = [{"path": validation_evidence, "sha256": evidence_hash}]
    all_gates_passed = all(receipt.get("gates", {}).values())
    receipt["allGatesPassed"] = all_gates_passed
    receipt["executionReady"] = all_gates_passed
    receipt["status"] = (
        "VERIFIED_COMPLETE" if all_gates_passed else "NOT_VERIFIED"
    )
    receipt["openMappingBlockers"] = [] if all_gates_passed else receipt.get(
        "openMappingBlockers", []
    )
    receipt["verificationTimestamp"] = now_utc()
    write_json(RECEIPT_PATH, receipt)
    status_path = CONTROL / "status.json"
    status_document = load_json(status_path)
    status_document["mappingStatus"] = receipt["status"]
    status_document.setdefault("v2Repair", {}).update({
        "lastCompletedStep": (
            "GRAPHIFY_MAPPING_VERIFIED_COMPLETE"
            if all_gates_passed
            else "GRAPHIFY_MAPPING_VALIDATED_WITH_OPEN_GATES"
        ),
        "affineArchiveStatus": "REFERENCE_VERIFIED",
        "independentReviewStatus": (
            "APPROVED"
            if receipt["gates"].get("independentReviewPassed")
            else "PENDING"
        ),
        "openMappingBlockers": receipt["openMappingBlockers"],
        "implementationPerformed": False,
    })
    status_document["lastUpdatedAt"] = now_utc()
    write_json(status_path, status_document)
    uppercase_status_path = CONTROL / "STATUS.json"
    uppercase_status = load_json(uppercase_status_path)
    uppercase_status.update({
        "mappingStatus": receipt["status"],
        "currentBatchId": None,
        "currentTaskId": None,
        "lastCompletedTaskId": "task-map-0002",
        "lastUpdatedAt": now_utc(),
    })
    write_json(uppercase_status_path, uppercase_status)
    written = load_json(RECEIPT_PATH)
    for gate, passed in written.get("gates", {}).items():
        if not passed:
            continue
        for record in written.get("gateEvidence", {}).get(gate, []):
            path = GRAPHIFY.parent / record["path"]
            if record.get("sha256") != sha256_file(path):
                raise AssertionError(f"true mapping gate evidence hash is stale after write: {gate}: {record['path']}")


def authoritative_artifact_paths(manifest_path: Path) -> tuple[list[str], list[Path]]:
    roots = [
        "Graphify/Master Plan",
        "Graphify/00 Execution Control/schemas",
        "Graphify/01 Corpus Inventory/GRAPH_LAYER_FILE_REGISTRY.jsonl",
        "Graphify/02 Architecture Map/RUNTIME_REGISTRATION_REGISTRY.jsonl",
        "Graphify/03 Capability Map",
        "Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl",
        "Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl",
        "Graphify/05 Dependency and Impact/Knowledge Graph",
        "Graphify/08 Cleanup/PONYTAIL_AUDIT.jsonl",
        "Graphify/11 Completion",
        "Graphify/14 AFFiNE Reference",
    ]
    extras = {
        CONTROL / "GRAPHIFY_REPAIR_BASELINE.json",
        CONTROL / "GRAPHIFY_REPAIR_MANIFEST.json",
        CONTROL / "V1_EVIDENCE_CLASSIFICATION.jsonl",
        *SCHEMA_INSTANCE_BINDINGS.values(),
    }
    selected: set[Path] = set()
    for relative in roots:
        root = (GRAPHIFY.parent / relative).resolve()
        if root.is_file():
            selected.add(root)
        elif root.is_dir():
            for directory, directories, files in os.walk(root):
                directory_path = Path(directory)
                directories[:] = [
                    name
                    for name in directories
                    if name != "Generated Tool Cache"
                    and not is_preserved_affine_source(directory_path / name)
                ]
                selected.update(
                    (directory_path / name).resolve() for name in files
                )
        else:
            raise AssertionError(f"authoritative artifact root is missing: {relative}")
    selected.update(path.resolve() for path in extras if path.is_file())
    build_runs_path = COMPLETION / "GRAPH_BUILD_RUNS.jsonl"
    if build_runs_path.is_file():
        build_runs = [row for row in iter_jsonl(build_runs_path) if row.get("runId") == RUN_ID]
        if build_runs:
            for relative in build_runs[-1].get("outputPaths", []):
                normalized_relative = str(relative).replace("\\", "/").removeprefix("Graphify/")
                output = graphify_path(normalized_relative, "authoritative build output")
                if output.is_file():
                    selected.add(output)
    exclusions = {
        manifest_path.resolve(),
    }
    paths = sorted(
        path for path in selected
        if path not in exclusions
        and "__pycache__" not in path.parts
        and path.suffix.lower() not in {".pyc", ".pyo"}
        and "Generated Tool Cache" not in path.parts
        and not is_preserved_affine_source(path)
    )
    return roots, paths


def rebuild_authoritative_artifact_manifest() -> dict[str, Any]:
    manifest_path = CONTROL / "AUTHORITATIVE_V2_ARTIFACT_MANIFEST.json"
    roots, paths = authoritative_artifact_paths(manifest_path)
    builder_path = COMPLETION / "build_graphify_v2.py"
    builder_text = builder_path.read_text(encoding="utf-8")
    version_match = re.search(r'^POLICY_VERSION\s*=\s*["\']([^"\']+)["\']', builder_text, re.MULTILINE)
    if not version_match:
        raise AssertionError("graph builder generator version is not declared")
    extraction_manifest = load_json(
        CONTROL / "Generated Tool Cache" / "v2" / RUN_ID / "ast" / "EXTRACTION_MANIFEST.json"
    )
    binding = {
        "runId": RUN_ID,
        "codebaseBaselineSha256": BASELINE["codebaseTreeSha256"],
        "masterPlanHashes": BASELINE["masterPlanHashes"],
        "graphBuilderPath": builder_path.relative_to(GRAPHIFY.parent).as_posix(),
        "graphBuilderSha256": sha256_file(builder_path),
        "graphBuilderGeneratorVersion": version_match.group(1),
        "graphifyExtractorVersion": extraction_manifest["extractorVersion"],
        "extractionPolicyVersion": extraction_manifest["extractionPolicyVersion"],
    }
    binding_sha = sha256_bytes(json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    rows = [
        {
            "path": path.relative_to(GRAPHIFY.parent).as_posix(),
            "sha256": sha256_file(path),
            "sizeBytes": path.stat().st_size,
            "provenanceBindingSha256": binding_sha,
        }
        for path in paths
    ]
    manifest = {
        "schemaVersion": "mindroom.graphify.authoritative-v2-artifact-manifest.v1",
        **binding,
        "provenanceBindingSha256": binding_sha,
        "generatedAt": now_utc(),
        "authoritativeRoots": roots,
        "artifactCount": len(rows),
        "artifacts": rows,
        "selfHashPolicy": "MANIFEST_EXCLUDED_TO_AVOID_RECURSIVE_SELF_HASH",
        "excludedScopes": [
            "Graphify/00 Execution Control/AUTHORITATIVE_V2_ARTIFACT_MANIFEST.json",
            "Graphify/00 Execution Control/Generated Tool Cache/legacy-v1",
            "Graphify/00 Execution Control/Generated Tool Cache/v2/*/ast/history",
            "Graphify/00 Execution Control/Generated Tool Cache/v2/*/ast/CACHE_STATE_EVENTS.jsonl",
            "Graphify/14 AFFiNE Reference/Incoming/**",
            "Graphify/14 AFFiNE Reference/Reference Tree/**",
        ],
        "legacyAndCacheHistoryPolicy": "PRESERVED_NON_AUTHORITATIVE_NOT_INCLUDED_IN_V2_ARTIFACT_HASH_SET",
    }
    write_json(manifest_path, manifest)

    written = load_json(manifest_path)
    if written != manifest or written["artifactCount"] != len(written["artifacts"]):
        raise AssertionError("authoritative artifact manifest write/read mismatch")
    listed_paths = [row["path"] for row in written["artifacts"]]
    if len(listed_paths) != len(set(listed_paths)):
        raise AssertionError("authoritative artifact manifest contains duplicate paths")
    _, current_paths = authoritative_artifact_paths(manifest_path)
    current_relative = {path.relative_to(GRAPHIFY.parent).as_posix() for path in current_paths}
    if set(listed_paths) != current_relative:
        raise AssertionError("authoritative artifact manifest does not exactly cover authoritative roots")
    bindings = {row.get("provenanceBindingSha256") for row in written["artifacts"]}
    if bindings != {binding_sha}:
        raise AssertionError("authoritative artifacts do not share one provenance binding")
    for row in written["artifacts"]:
        path = (GRAPHIFY.parent / row["path"]).resolve()
        if not path.is_file() or row["sha256"] != sha256_file(path) or row["sizeBytes"] != path.stat().st_size:
            raise AssertionError(f"authoritative artifact path/hash/size is stale: {row['path']}")
    return {
        "path": manifest_path.relative_to(GRAPHIFY.parent).as_posix(),
        "artifactCount": len(rows), "provenanceBindingSha256": binding_sha,
    }


def main() -> None:
    json_result = validate_json_files()
    schema_result = validate_schemas_and_contracts()
    baseline_result = validate_baseline()
    reference_result = validate_references()
    affine_result = validate_affine_reference()
    graph_validation_result = finalize_graph_validation(
        json_result, schema_result, baseline_result, reference_result,
    )
    review = independent_review()
    affine = load_json(GRAPHIFY / "14 AFFiNE Reference" / "AFFINE_REFERENCE_MANIFEST.json")
    status = (
        "PASS"
        if review["passed"] and affine_result["status"] == "PASS"
        else "PASS_LOCAL_VALIDATION_INDEPENDENT_REVIEW_PENDING"
    )
    result = {
        "project": "MindRoom", "phase": "GRAPHIFY_V2_MAPPING", "runId": RUN_ID,
        "status": status, "validationType": "ORCHESTRATOR_INTEGRATION_VALIDATION_NOT_INDEPENDENT_REVIEW",
        "jsonValidation": json_result, "schemaValidation": schema_result, "codebaseBaseline": baseline_result,
        "referentialIntegrity": reference_result, "graphHealth": load_json(KG / "GRAPH_HEALTH.json"),
        "graphValidation": graph_validation_result,
        "independentReview": review, "affineReference": affine_result,
        "applicationImplementationPerformed": False, "releaseReceiptLocked": True,
        "openMappingBlockers": ([affine["externalBlocker"]] if affine["externalBlocker"] else []) + ([] if review["passed"] else ["INDEPENDENT_V2_FINAL_REVIEW_NOT_APPROVED"]),
        "validatedAt": now_utc(),
    }
    write_json(RESULT_PATH, result)
    update_receipt_validation_gates("Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json")
    # Reparse the two files touched above to close the validator's own write loop.
    load_json(RESULT_PATH)
    load_json(RECEIPT_PATH)
    result["authoritativeArtifactManifest"] = rebuild_authoritative_artifact_manifest()
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
