from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CODEBASE_ROOT = PROJECT_ROOT / "Codebase"
GRAPHIFY_ROOT = PROJECT_ROOT / "Graphify"
OUTPUT_04 = GRAPHIFY_ROOT / "04 Exact Location Registry"
OUTPUT_05 = GRAPHIFY_ROOT / "05 Dependency and Impact"
INVENTORY_PATH = GRAPHIFY_ROOT / "01 Corpus Inventory" / "REPOSITORY_INVENTORY.jsonl"
CAPABILITY_PATH = GRAPHIFY_ROOT / "03 Capability Map" / "CAPABILITY_REGISTRY.json"
AST_PATH = GRAPHIFY_ROOT / "11 Completion" / "graphify-out" / ".graphify_ast.json"

REQUIRED = [
    OUTPUT_04 / "EXACT_LOCATION_REGISTRY.json",
    OUTPUT_04 / "SYMBOL_REGISTRY.jsonl",
    OUTPUT_05 / "DEPENDENCY_EDGES.jsonl",
    OUTPUT_05 / "DEPENDENCY_SUMMARY.md",
    OUTPUT_05 / "CIRCULAR_DEPENDENCY_REPORT.json",
    OUTPUT_05 / "REMOVAL_BLAST_RADIUS.jsonl",
    OUTPUT_05 / "REORGANISATION_BLAST_RADIUS.jsonl",
    OUTPUT_05 / "RUNTIME_REACHABILITY_REPORT.jsonl",
    OUTPUT_05 / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl",
    OUTPUT_05 / "DEAD_CODE_CANDIDATES.jsonl",
    OUTPUT_05 / "EXCLUDED_SYSTEM_BOUNDARY_MAP.jsonl",
]


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            assert isinstance(value, dict), f"{path.name}:{line_number} not object"
            yield value


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def source_path(path: str) -> Path:
    return CODEBASE_ROOT / Path(*path.removeprefix("Codebase/").split("/"))


def main() -> None:
    for path in REQUIRED:
        assert path.is_file() and path.stat().st_size > 0, f"missing/empty {path}"
    assert not (CODEBASE_ROOT / "graphify-out").exists()

    inventory = {record["path"]: record for record in read_jsonl(INVENTORY_PATH)}
    file_paths = {
        path
        for path, record in inventory.items()
        if record["entityType"] in {"FILE", "ARCHIVE"}
    }
    capabilities = json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))[
        "capabilities"
    ]
    capability_ids = {record["capabilityId"] for record in capabilities}
    ast = json.loads(AST_PATH.read_text(encoding="utf-8"))
    ast_ids = {record["id"] for record in ast["nodes"]}

    exact = json.loads(
        (OUTPUT_04 / "EXACT_LOCATION_REGISTRY.json").read_text(encoding="utf-8")
    )
    entities = exact["entities"]
    entity_by_id = {record["entityId"]: record for record in entities}
    assert len(entity_by_id) == len(entities), "duplicate entity IDs"
    hashed_paths: set[str] = set()
    entity_types = Counter()
    for entity in entities:
        path = entity["currentPath"]
        assert path in file_paths, f"entity path not a file {path}"
        assert set(entity["capabilityIds"]) <= capability_ids
        assert entity["fileSha256"] == inventory[path]["sha256"]
        assert re.fullmatch(r"[0-9a-f]{64}", entity["fileSha256"])
        entity_types[entity["entityType"]] += 1
        if path not in hashed_paths:
            assert digest(source_path(path)) == entity["fileSha256"], f"stale {path}"
            hashed_paths.add(path)

    symbols = list(read_jsonl(OUTPUT_04 / "SYMBOL_REGISTRY.jsonl"))
    symbol_ids = {record["symbolId"] for record in symbols}
    assert len(symbol_ids) == len(symbols), "duplicate symbol IDs"
    for symbol in symbols:
        entity = entity_by_id[symbol["locationEntityId"]]
        assert symbol["currentPath"] == entity["currentPath"]
        assert symbol["fileSha256"] == entity["fileSha256"]
        assert set(symbol["capabilityIds"]) <= capability_ids

    edge_ids: set[str] = set()
    edge_types = Counter()
    endpoint_types = Counter()
    unresolved_count = 0
    for edge in read_jsonl(OUTPUT_05 / "DEPENDENCY_EDGES.jsonl"):
        assert edge["edgeId"] not in edge_ids, f"duplicate edge {edge['edgeId']}"
        edge_ids.add(edge["edgeId"])
        edge_types[edge["edgeType"]] += 1
        assert set(edge["capabilityIds"]) <= capability_ids
        for prefix in ("source", "target"):
            endpoint_type = edge[f"{prefix}EndpointType"]
            endpoint_id = edge[f"{prefix}Id"]
            path = edge[f"{prefix}Path"]
            endpoint_types[endpoint_type] += 1
            if endpoint_type == "LOCATION_ENTITY":
                assert endpoint_id in entity_by_id
            elif endpoint_type == "AST_NODE":
                assert endpoint_id in ast_ids
            elif endpoint_type == "PATH":
                assert path in inventory
            elif endpoint_type == "CAPABILITY":
                assert endpoint_id.removeprefix("capability:") in capability_ids
            elif endpoint_type in {
                "EXTERNAL_OR_SYMBOLIC_REFERENCE",
                "EXTERNAL_REFERENCE",
                "UNRESOLVED_AST_REFERENCE",
                "UNRESOLVED_PATH_REFERENCE",
                "UNRESOLVED_REFERENCE",
            }:
                unresolved_count += 1
            else:
                raise AssertionError(f"unknown endpoint type {endpoint_type}")

    circular = json.loads(
        (OUTPUT_05 / "CIRCULAR_DEPENDENCY_REPORT.json").read_text(encoding="utf-8")
    )
    for component in circular["stronglyConnectedComponents"]:
        assert component["size"] == len(component["paths"]) > 1
        assert set(component["paths"]) <= file_paths

    removal = list(read_jsonl(OUTPUT_05 / "REMOVAL_BLAST_RADIUS.jsonl"))
    reorganisation = list(
        read_jsonl(OUTPUT_05 / "REORGANISATION_BLAST_RADIUS.jsonl")
    )
    reachability = list(
        read_jsonl(OUTPUT_05 / "RUNTIME_REACHABILITY_REPORT.jsonl")
    )
    duplicates = list(
        read_jsonl(OUTPUT_05 / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl")
    )
    dead = list(read_jsonl(OUTPUT_05 / "DEAD_CODE_CANDIDATES.jsonl"))
    boundaries = list(
        read_jsonl(OUTPUT_05 / "EXCLUDED_SYSTEM_BOUNDARY_MAP.jsonl")
    )
    assert {record["path"] for record in reachability} == file_paths
    assert all(record["classification"] == "REMOVE" for record in removal)
    assert all(record["capabilityId"] in capability_ids for record in reorganisation)
    assert all(record["capabilityId"] in capability_ids for record in boundaries)
    assert all(set(record["paths"]) <= file_paths for record in duplicates)
    assert all(record["path"] in file_paths for record in dead)

    forbidden = re.compile(r'"status"\s*:\s*"[^"]*(?:PURGED|DELETED|APPROVED)')
    for path in (
        OUTPUT_05 / "REMOVAL_BLAST_RADIUS.jsonl",
        OUTPUT_05 / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl",
        OUTPUT_05 / "DEAD_CODE_CANDIDATES.jsonl",
        OUTPUT_05 / "EXCLUDED_SYSTEM_BOUNDARY_MAP.jsonl",
    ):
        assert not forbidden.search(path.read_text(encoding="utf-8")), path.name

    output_hashes = {path.name: digest(path) for path in REQUIRED}
    print(
        json.dumps(
            {
                "status": "PASS",
                "codebaseGraphifyOutAbsent": True,
                "exactLocationEntities": len(entities),
                "uniqueSourceFilesRehashed": len(hashed_paths),
                "symbolRecords": len(symbols),
                "dependencyEdges": len(edge_ids),
                "unresolvedOrExternalEndpointsExplicitlyTyped": unresolved_count,
                "edgeTypes": dict(edge_types.most_common()),
                "entityTypes": dict(entity_types.most_common()),
                "endpointTypes": dict(endpoint_types.most_common()),
                "circularComponents": circular["stronglyConnectedComponentCount"],
                "removalBlastRecords": len(removal),
                "reorganisationBlastRecords": len(reorganisation),
                "runtimeReachabilityRecords": len(reachability),
                "duplicateCandidates": len(duplicates),
                "deadCodeCandidates": len(dead),
                "excludedBoundaryRecords": len(boundaries),
                "outputSha256": output_hashes,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
