"""Hash-, policy-, partition-, and status-validated Graphify extraction.

Raw extraction is diagnostic evidence only. It is stored under Generated Tool
Cache and never becomes authoritative without the V2 graph validations.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import os
import tempfile

_orig_mkstemp = tempfile.mkstemp
def _safe_mkstemp(*args, **kwargs):
    d = kwargs.get("dir")
    if not d and len(args) >= 3:
        d = args[2]
    if d and isinstance(d, (str, Path)):
        d_str = str(d)
        if not d_str.startswith("\\\\?\\") and os.name == "nt":
            d_str = "\\\\?\\" + os.path.abspath(d_str)
        os.makedirs(d_str, exist_ok=True)
        if "dir" in kwargs:
            kwargs["dir"] = d_str
        elif len(args) >= 3:
            args = (args[0], args[1], d_str) + args[3:]
    return _orig_mkstemp(*args, **kwargs)
tempfile.mkstemp = _safe_mkstemp
import graphify.cache
graphify.cache.mkstemp = _safe_mkstemp

from graphify.extract import extract

from repair_v2_common import (
    CODEBASE,
    CONTROL,
    GRAPHIFY,
    TOOL_CACHE,
    atomic_write_text,
    iter_jsonl,
    load_json,
    now_utc,
    sha256_bytes,
    sha256_file,
    stable_id,
    write_json,
)


SCHEMA_VERSION = "mindroom.graphify.ast-batch-manifest.v2"
POLICY_VERSION = "mindroom-graphify-v2-layered-directed-2"
EXTRACTOR_NAME = "graphify.extract.extract"
SUPPORTED = {
    ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".rs", ".go", ".java", ".c", ".h", ".cc", ".cpp", ".hpp",
    ".cs", ".rb", ".php", ".swift", ".kt", ".kts", ".sql", ".graphql",
    ".gql",
}
EXTRACT_LAYERS = {
    "AUTHORED_RUNTIME", "TEST_AND_FIXTURE", "BUILD_AND_CONFIG",
    "PACKAGING_AND_DEPLOYMENT", "MIGRATION_AND_SCHEMA", "GENERATED_BINDING",
}
REQUIRED_BATCH_FIELDS = {
    "schemaVersion", "runId", "batchId", "extractorName", "extractorVersion",
    "extractionPolicyVersion", "codebaseBaseline", "masterPlanHashes", "rootPath",
    "orderedInputFiles", "inputFileHashes", "configurationHashes", "batchOutputPath",
    "batchOutputSha256", "nodeCount", "edgeCount", "startedAt", "completedAt", "status",
}


def baseline() -> dict[str, Any]:
    return load_json(CONTROL / "GRAPHIFY_REPAIR_BASELINE.json")


def extractor_version() -> str:
    """Return the installed distribution version, never an unverified placeholder."""
    distributions = importlib.metadata.packages_distributions().get("graphify", [])
    for distribution in distributions:
        try:
            return f"{distribution}=={importlib.metadata.version(distribution)}"
        except importlib.metadata.PackageNotFoundError:
            continue
    for distribution in ("graphifyy", "graphify"):
        try:
            return f"{distribution}=={importlib.metadata.version(distribution)}"
        except importlib.metadata.PackageNotFoundError:
            continue
    raise RuntimeError("Graphify extractor distribution version cannot be verified")


def cache_root() -> Path:
    root = TOOL_CACHE / "v2" / str(baseline()["runId"]) / "ast"
    root.mkdir(parents=True, exist_ok=True)
    for base_dir in [root, root / "graphify-out"]:
        ast_dir = base_dir / "cache" / "ast" / "v0.9.28"
        ast_dir.mkdir(parents=True, exist_ok=True)
        for i in range(256):
            (ast_dir / f"{i:02x}").mkdir(parents=True, exist_ok=True)
    return root


def configuration_hashes() -> dict[str, str]:
    candidates = [
        Path(__file__),
        Path(__file__).parent / "repair_v2_common.py",
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


def extraction_files() -> dict[str, list[dict[str, Any]]]:
    """Read and hash every current input; the inventory digest is only a cross-check."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    registry = GRAPHIFY / "01 Corpus Inventory" / "GRAPH_LAYER_FILE_REGISTRY.jsonl"
    mismatches: list[str] = []
    for row in iter_jsonl(registry):
        layer = row["primaryLayer"]
        if layer not in EXTRACT_LAYERS:
            continue
        path = GRAPHIFY.parent / row["path"]
        if path.suffix.lower() not in SUPPORTED:
            continue
        if not path.is_file():
            mismatches.append(f"missing:{row['path']}")
            continue
        actual_hash = sha256_file(path)
        actual_size = path.stat().st_size
        if actual_hash != row.get("sha256") or actual_size != row.get("sizeBytes"):
            mismatches.append(f"changed:{row['path']}")
        grouped[layer].append(
            {
                "path": path,
                "relative": row["path"],
                "sha256": actual_hash,
                "sizeBytes": actual_size,
            }
        )
    if mismatches:
        preview = ", ".join(mismatches[:10])
        raise RuntimeError(f"current source differs from classified baseline ({len(mismatches)}): {preview}")
    for rows in grouped.values():
        rows.sort(key=lambda row: row["relative"])
    return dict(sorted(grouped.items()))


def batch_descriptor(
    layer: str,
    index: int,
    batch_size: int,
    rows: list[dict[str, Any]],
    config_hashes: dict[str, str],
) -> dict[str, Any]:
    base = baseline()
    ordered_files = [row["relative"] for row in rows]
    input_hashes = {row["relative"]: row["sha256"] for row in rows}
    canonical = {
        "schemaVersion": SCHEMA_VERSION,
        "runId": base["runId"],
        "extractorName": EXTRACTOR_NAME,
        "extractorVersion": extractor_version(),
        "extractionPolicyVersion": POLICY_VERSION,
        "codebaseBaseline": base["codebaseTreeSha256"],
        "masterPlanHashes": base["masterPlanHashes"],
        "rootPath": str(CODEBASE.resolve()),
        "orderedInputFiles": ordered_files,
        "inputFileHashes": input_hashes,
        "configurationHashes": config_hashes,
        "layer": layer,
        "batchIndex": index,
        "batchSizePolicy": batch_size,
    }
    fingerprint = sha256_bytes(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    batch_id = stable_id("MR-AST-BATCH-V2", layer, str(index), fingerprint)
    return {**canonical, "batchId": batch_id, "inputFingerprint": fingerprint}


def cache_paths(layer: str, index: int) -> tuple[Path, Path]:
    slug = layer.lower().replace("_", "-")
    root = cache_root() / "batches" / slug
    return root / f"batch-{index:04d}.json", root / f"batch-{index:04d}.manifest.json"


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    atomic_write_text(path, existing + json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def preserve_prior(output: Path, manifest_path: Path, reason: str) -> None:
    if not output.exists() and not manifest_path.exists():
        return
    prior_manifest: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            prior_manifest = load_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            prior_manifest = {"parseStatus": "UNREADABLE"}
    identity = stable_id(
        "MR-CACHE-STATE",
        str(manifest_path.relative_to(cache_root())),
        str(prior_manifest.get("inputFingerprint", "missing")),
        sha256_file(manifest_path) if manifest_path.exists() else "missing",
    )
    history = cache_root() / "history" / "stale" / identity
    history.mkdir(parents=True, exist_ok=True)
    archived_output = history / "batch.json"
    archived_manifest = history / "batch.manifest.json"
    if output.exists():
        shutil.copy2(output, archived_output)
    if manifest_path.exists():
        shutil.copy2(manifest_path, archived_manifest)
    event = {
        "schemaVersion": "mindroom.graphify.cache-state-event.v2",
        "runId": baseline()["runId"],
        "eventId": identity,
        "batchId": prior_manifest.get("batchId"),
        "priorStatus": prior_manifest.get("status", "LEGACY_OR_UNKNOWN"),
        "status": "STALE",
        "reason": reason,
        "priorManifestPath": archived_manifest.relative_to(GRAPHIFY).as_posix()
        if archived_manifest.exists() else None,
        "priorOutputPath": archived_output.relative_to(GRAPHIFY).as_posix()
        if archived_output.exists() else None,
        "priorOutputSha256": sha256_file(archived_output) if archived_output.exists() else None,
        "recordedAt": now_utc(),
    }
    append_jsonl(cache_root() / "CACHE_STATE_EVENTS.jsonl", event)


def current_inputs_match(expected: dict[str, Any]) -> tuple[bool, str]:
    for relative in expected["orderedInputFiles"]:
        path = GRAPHIFY.parent / relative
        if not path.is_file():
            return False, f"current input missing: {relative}"
        if sha256_file(path) != expected["inputFileHashes"].get(relative):
            return False, f"current input hash changed: {relative}"
    return True, "current input hashes match"


def valid_cache(output: Path, manifest_path: Path, expected: dict[str, Any]) -> tuple[bool, str]:
    if not output.exists() or not manifest_path.exists():
        return False, "missing output or manifest"
    try:
        manifest = load_json(manifest_path)
        missing = sorted(REQUIRED_BATCH_FIELDS - set(manifest))
        if missing:
            return False, f"required manifest fields missing: {','.join(missing)}"
        if manifest.get("status") != "COMPLETE":
            return False, f"batch status is {manifest.get('status')}"
        for field in (
            "schemaVersion", "runId", "batchId", "extractorName", "extractorVersion",
            "extractionPolicyVersion", "codebaseBaseline", "masterPlanHashes", "rootPath",
            "orderedInputFiles", "inputFileHashes", "configurationHashes", "inputFingerprint",
        ):
            if manifest.get(field) != expected.get(field):
                return False, f"manifest field changed: {field}"
        input_valid, input_reason = current_inputs_match(expected)
        if not input_valid:
            return False, input_reason
        expected_output_path = output.relative_to(GRAPHIFY).as_posix()
        if manifest.get("batchOutputPath") != expected_output_path:
            return False, "batch output path changed"
        if manifest.get("batchOutputSha256") != sha256_file(output):
            return False, "batch output checksum mismatch"
        payload = load_json(output)
        if not isinstance(payload.get("nodes"), list) or not isinstance(payload.get("edges"), list):
            return False, "batch output schema invalid"
        if manifest.get("nodeCount") != len(payload["nodes"]) or manifest.get("edgeCount") != len(payload["edges"]):
            return False, "batch output counts mismatch"
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return False, f"cache parse failed: {error}"
    return True, "source, baseline, plan, policy, extractor, config, status, and output validated"


def build_partition(batch_size: int) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, Any]]:
    if batch_size <= 0:
        raise ValueError("batch size must be positive")
    grouped = extraction_files()
    config_hashes = configuration_hashes()
    descriptors: list[dict[str, Any]] = []
    expected_files: list[str] = []
    for layer, files in grouped.items():
        expected_files.extend(row["relative"] for row in files)
        total = math.ceil(len(files) / batch_size)
        for index in range(total):
            rows = files[index * batch_size : (index + 1) * batch_size]
            descriptors.append(batch_descriptor(layer, index, batch_size, rows, config_hashes))
    memberships = [path for descriptor in descriptors for path in descriptor["orderedInputFiles"]]
    counts = Counter(memberships)
    duplicates = sorted(path for path, count in counts.items() if count != 1)
    omissions = sorted(set(expected_files) - set(memberships))
    unexpected = sorted(set(memberships) - set(expected_files))
    batch_ids = [descriptor["batchId"] for descriptor in descriptors]
    partition = {
        "status": "PASS" if not duplicates and not omissions and not unexpected and len(batch_ids) == len(set(batch_ids)) else "FAIL",
        "expectedFileCount": len(expected_files),
        "partitionedFileCount": len(memberships),
        "uniquePartitionedFileCount": len(set(memberships)),
        "duplicateFiles": duplicates,
        "omittedFiles": omissions,
        "unexpectedFiles": unexpected,
        "duplicateBatchIds": sorted(batch_id for batch_id, count in Counter(batch_ids).items() if count > 1),
        "orderedSourceSetSha256": sha256_bytes("\n".join(expected_files).encode("utf-8")),
    }
    if partition["status"] != "PASS":
        raise RuntimeError(f"invalid extraction partition: {json.dumps(partition, sort_keys=True)}")
    return grouped, descriptors, partition


def retire_unlisted_batch_manifests(active_manifest_paths: set[Path]) -> None:
    batches_root = cache_root() / "batches"
    if not batches_root.exists():
        return
    for manifest_path in batches_root.rglob("*.manifest.json"):
        if manifest_path in active_manifest_paths:
            continue
        output = manifest_path.with_name(manifest_path.name.replace(".manifest.json", ".json"))
        preserve_prior(output, manifest_path, "batch not present in current complete partition")
        try:
            row = load_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            row = {}
        row.update({"status": "STALE", "staleReason": "not in current partition", "completedAt": now_utc()})
        write_json(manifest_path, row)


def batch_manifest(
    descriptor: dict[str, Any],
    output: Path,
    started_at: str,
    completed_at: str,
    status: str,
    node_count: int,
    edge_count: int,
    output_sha256: str | None,
    **extra: Any,
) -> dict[str, Any]:
    return {
        **descriptor,
        "batchOutputPath": output.relative_to(GRAPHIFY).as_posix(),
        "batchOutputSha256": output_sha256,
        "nodeCount": node_count,
        "edgeCount": edge_count,
        "startedAt": started_at,
        "completedAt": completed_at,
        "status": status,
        **extra,
    }


def extract_batches(batch_size: int) -> None:
    grouped, descriptors, partition = build_partition(batch_size)
    cache_root().mkdir(parents=True, exist_ok=True)
    active_paths = {cache_paths(row["layer"], row["batchIndex"])[1] for row in descriptors}
    retire_unlisted_batch_manifests(active_paths)
    receipts: list[dict[str, Any]] = []
    reused = 0
    extracted = 0
    invocation_started = now_utc()
    totals_by_layer = Counter(row["layer"] for row in descriptors)
    for descriptor in descriptors:
        layer = descriptor["layer"]
        index = descriptor["batchIndex"]
        total = totals_by_layer[layer]
        rows_by_path = {row["relative"]: row for row in grouped[layer]}
        rows = [rows_by_path[path] for path in descriptor["orderedInputFiles"]]
        output, manifest_path = cache_paths(layer, index)
        valid, reason = valid_cache(output, manifest_path, descriptor)
        if valid:
            reused += 1
            manifest = load_json(manifest_path)
            manifest["cacheDecision"] = "REUSED_AFTER_FULL_VALIDATION"
            manifest["lastValidatedAt"] = now_utc()
            manifest["reuseValidationCount"] = int(manifest.get("reuseValidationCount", 0)) + 1
            write_json(manifest_path, manifest)
            print(f"{layer} batch {index + 1}/{total}: cache validated", flush=True)
        else:
            preserve_prior(output, manifest_path, reason)
            started_at = now_utc()
            try:
                current_valid, current_reason = current_inputs_match(descriptor)
                if not current_valid:
                    raise RuntimeError(current_reason)
                result = extract(
                    [row["path"] for row in rows],
                    cache_root=cache_root(),
                    root=CODEBASE,
                )
                if not isinstance(result.get("nodes"), list) or not isinstance(result.get("edges"), list):
                    raise RuntimeError("extractor returned invalid nodes/edges schema")
                output.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_text(output, json.dumps(result, ensure_ascii=False, separators=(",", ":")))
                manifest = batch_manifest(
                    descriptor,
                    output,
                    started_at,
                    now_utc(),
                    "COMPLETE",
                    len(result["nodes"]),
                    len(result["edges"]),
                    sha256_file(output),
                    inputTokens=result.get("input_tokens", 0),
                    outputTokens=result.get("output_tokens", 0),
                    cacheDecision="REEXTRACTED",
                    cacheInvalidationReason=reason,
                    reuseValidationCount=0,
                )
                write_json(manifest_path, manifest)
                post_valid, post_reason = valid_cache(output, manifest_path, descriptor)
                if not post_valid:
                    raise RuntimeError(f"new batch failed post-write validation: {post_reason}")
                extracted += 1
                print(
                    f"{layer} batch {index + 1}/{total}: {manifest['nodeCount']} nodes, "
                    f"{manifest['edgeCount']} edges ({reason})",
                    flush=True,
                )
            except Exception as error:
                failed = batch_manifest(
                    descriptor, output, started_at, now_utc(), "FAILED", 0, 0, None,
                    cacheDecision="EXTRACTION_FAILED", cacheInvalidationReason=reason,
                    errorType=type(error).__name__, error=str(error),
                )
                write_json(manifest_path, failed)
                append_jsonl(
                    cache_root() / "CACHE_STATE_EVENTS.jsonl",
                    {
                        "schemaVersion": "mindroom.graphify.cache-state-event.v2",
                        "runId": baseline()["runId"],
                        "eventId": stable_id("MR-CACHE-FAILED", descriptor["batchId"], failed["completedAt"]),
                        "batchId": descriptor["batchId"],
                        "status": "FAILED",
                        "reason": str(error),
                        "manifestPath": manifest_path.relative_to(GRAPHIFY).as_posix(),
                        "recordedAt": failed["completedAt"],
                    },
                )
                raise
        receipts.append(manifest)

    if any(row.get("status") != "COMPLETE" for row in receipts):
        raise RuntimeError("one or more extraction batches are not COMPLETE")
    extraction_manifest = {
        "schemaVersion": "mindroom.graphify.extraction-manifest.v2",
        "project": "MindRoom",
        "runId": baseline()["runId"],
        "extractionPolicyVersion": POLICY_VERSION,
        "extractorName": EXTRACTOR_NAME,
        "extractorVersion": extractor_version(),
        "codebaseBaseline": baseline()["codebaseTreeSha256"],
        "masterPlanHashes": baseline()["masterPlanHashes"],
        "rootPath": str(CODEBASE.resolve()),
        "authoritative": False,
        "status": "COMPLETE",
        "batchSizePolicy": batch_size,
        "batchCount": len(receipts),
        "reusedBatchCount": reused,
        "reextractedBatchCount": extracted,
        "fileCount": sum(len(rows) for rows in grouped.values()),
        "layers": {layer: len(rows) for layer, rows in grouped.items()},
        "partitionValidation": partition,
        "batches": [
            {
                "batchId": row["batchId"],
                "layer": row["layer"],
                "batchIndex": row["batchIndex"],
                "inputFingerprint": row["inputFingerprint"],
                "manifestPath": cache_paths(row["layer"], row["batchIndex"])[1].relative_to(GRAPHIFY).as_posix(),
                "batchOutputPath": row["batchOutputPath"],
                "batchOutputSha256": row["batchOutputSha256"],
                "nodeCount": row["nodeCount"],
                "edgeCount": row["edgeCount"],
                "status": row["status"],
            }
            for row in receipts
        ],
        "startedAt": invocation_started,
        "completedAt": now_utc(),
    }
    manifest_path = cache_root() / "EXTRACTION_MANIFEST.json"
    if manifest_path.exists():
        prior_sha = sha256_file(manifest_path)
        history_path = cache_root() / "history" / "extraction-runs" / f"{prior_sha}.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        if not history_path.exists():
            shutil.copy2(manifest_path, history_path)
    write_json(manifest_path, extraction_manifest)
    append_jsonl(
        cache_root() / "EXTRACTION_RUNS.jsonl",
        {
            "schemaVersion": "mindroom.graphify.extraction-run.v2",
            "runId": baseline()["runId"],
            "invocationId": stable_id("MR-AST-RUN", invocation_started, extraction_manifest["completedAt"]),
            "status": "COMPLETE",
            "batchCount": len(receipts),
            "reusedBatchCount": reused,
            "reextractedBatchCount": extracted,
            "partitionStatus": partition["status"],
            "manifestSha256": sha256_file(manifest_path),
            "startedAt": invocation_started,
            "completedAt": extraction_manifest["completedAt"],
        },
    )


def merge_batches() -> None:
    manifest_path = cache_root() / "EXTRACTION_MANIFEST.json"
    manifest = load_json(manifest_path)
    if manifest.get("status") != "COMPLETE" or manifest.get("partitionValidation", {}).get("status") != "PASS":
        raise RuntimeError("extraction manifest is not COMPLETE with a PASS partition")
    _, descriptors, current_partition = build_partition(int(manifest["batchSizePolicy"]))
    if current_partition != manifest["partitionValidation"]:
        raise RuntimeError("current complete partition differs from extraction manifest")
    expected_by_id = {row["batchId"]: row for row in descriptors}
    if set(expected_by_id) != {row["batchId"] for row in manifest["batches"]}:
        raise RuntimeError("extraction manifest batch membership differs from current partition")
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    input_tokens = 0
    output_tokens = 0
    for receipt in manifest["batches"]:
        descriptor = expected_by_id[receipt["batchId"]]
        output = GRAPHIFY / receipt["batchOutputPath"]
        batch_manifest_path = GRAPHIFY / receipt["manifestPath"]
        valid, reason = valid_cache(output, batch_manifest_path, descriptor)
        if not valid:
            raise RuntimeError(f"stale, failed, or corrupt batch {receipt['batchId']}: {reason}")
        batch_row = load_json(batch_manifest_path)
        if batch_row["status"] != "COMPLETE" or receipt["status"] != "COMPLETE":
            raise RuntimeError(f"non-COMPLETE batch rejected: {receipt['batchId']}")
        payload = load_json(output)
        nodes.extend(payload["nodes"])
        edges.extend(payload["edges"])
        input_tokens += payload.get("input_tokens", 0)
        output_tokens += payload.get("output_tokens", 0)
    merged = {
        "nodes": nodes,
        "edges": edges,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "authoritative": False,
        "extractionPolicyVersion": POLICY_VERSION,
        "runId": baseline()["runId"],
    }
    destination = cache_root() / "GRAPHIFY_RAW_MERGED.json"
    atomic_write_text(destination, json.dumps(merged, ensure_ascii=False, separators=(",", ":")))
    write_json(
        cache_root() / "MERGE_RECEIPT.json",
        {
            "schemaVersion": "mindroom.graphify.merge-receipt.v2",
            "runId": baseline()["runId"],
            "status": "COMPLETE",
            "inputManifestSha256": sha256_file(manifest_path),
            "partitionValidation": current_partition,
            "outputPath": destination.relative_to(GRAPHIFY).as_posix(),
            "outputSha256": sha256_file(destination),
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "authoritative": False,
            "completedAt": now_utc(),
        },
    )
    print(f"merged diagnostic extraction: {len(nodes)} nodes, {len(edges)} edges", flush=True)


def show_status() -> None:
    manifest = load_json(cache_root() / "EXTRACTION_MANIFEST.json", {})
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["extract", "merge", "status"])
    parser.add_argument("--batch-size", type=int, default=400)
    arguments = parser.parse_args()
    if arguments.action == "extract":
        extract_batches(arguments.batch_size)
    elif arguments.action == "merge":
        merge_batches()
    else:
        show_status()


if __name__ == "__main__":
    main()
