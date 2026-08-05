from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCRIPT_VERSION = "1.0.0"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CODEBASE_ROOT = PROJECT_ROOT / "Codebase"
GRAPHIFY_ROOT = PROJECT_ROOT / "Graphify"
INVENTORY_DIR = GRAPHIFY_ROOT / "01 Corpus Inventory"
ARCHITECTURE_DIR = GRAPHIFY_ROOT / "02 Architecture Map"
CAPABILITY_DIR = GRAPHIFY_ROOT / "03 Capability Map"
OUTPUT_04 = GRAPHIFY_ROOT / "04 Exact Location Registry"
OUTPUT_05 = GRAPHIFY_ROOT / "05 Dependency and Impact"
AST_PATH = GRAPHIFY_ROOT / "11 Completion" / "graphify-out" / ".graphify_ast.json"

EXACT_LOCATION_PATH = OUTPUT_04 / "EXACT_LOCATION_REGISTRY.json"
SYMBOL_PATH = OUTPUT_04 / "SYMBOL_REGISTRY.jsonl"
DEPENDENCY_PATH = OUTPUT_05 / "DEPENDENCY_EDGES.jsonl"
DEPENDENCY_SUMMARY_PATH = OUTPUT_05 / "DEPENDENCY_SUMMARY.md"
CIRCULAR_PATH = OUTPUT_05 / "CIRCULAR_DEPENDENCY_REPORT.json"
REMOVAL_BLAST_PATH = OUTPUT_05 / "REMOVAL_BLAST_RADIUS.jsonl"
REORGANISATION_BLAST_PATH = OUTPUT_05 / "REORGANISATION_BLAST_RADIUS.jsonl"
REACHABILITY_PATH = OUTPUT_05 / "RUNTIME_REACHABILITY_REPORT.jsonl"
DUPLICATE_PATH = OUTPUT_05 / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl"
DEAD_PATH = OUTPUT_05 / "DEAD_CODE_CANDIDATES.jsonl"
EXCLUDED_BOUNDARY_PATH = OUTPUT_05 / "EXCLUDED_SYSTEM_BOUNDARY_MAP.jsonl"

SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cjs",
    ".cpp",
    ".cs",
    ".gql",
    ".gradle",
    ".graphql",
    ".graphqls",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".m",
    ".mjs",
    ".mm",
    ".proto",
    ".py",
    ".rs",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}

AST_RELATION_TYPES = {
    "imports": "STATIC_IMPORT",
    "imports_from": "STATIC_IMPORT",
    "re_exports": "RE_EXPORT",
    "calls": "FUNCTION_CALL",
    "indirect_call": "FUNCTION_CALL",
    "inherits": "CLASS_INHERITANCE",
    "extends": "TYPE_DEPENDENCY",
    "implements": "TYPE_DEPENDENCY",
    "references": "TYPE_DEPENDENCY",
    "triggers": "EVENT_REGISTRATION",
    "reads_from": "ASSET_REFERENCE",
}

REGISTRATION_EDGE_TYPES = {
    "application-event-registration": "EVENT_REGISTRATION",
    "command-registration": "COMMAND_REGISTRATION",
    "command-registration-group": "COMMAND_REGISTRATION",
    "composition-root": "DI_REGISTRATION",
    "di-module": "DI_REGISTRATION",
    "feature-flag-registration": "DI_REGISTRATION",
    "ipc-event-registration": "IPC_REGISTRATION",
    "ipc-registration": "IPC_REGISTRATION",
    "menu-registration": "COMMAND_REGISTRATION",
    "native-event-registration": "EVENT_REGISTRATION",
    "protocol-registration": "ROUTE_REGISTRATION",
    "provider-registration": "DI_REGISTRATION",
    "route-registration": "ROUTE_REGISTRATION",
    "schema-registration": "SCHEMA_REGISTRATION",
    "storage-constructor-registry": "DI_REGISTRATION",
    "worker-service-registry": "WORKER_REGISTRATION",
}

PROOF_REQUIREMENTS = [
    "STATIC_IMPORT_ANALYSIS",
    "RE_EXPORT_ANALYSIS",
    "DYNAMIC_IMPORT_ANALYSIS",
    "CALL_GRAPH",
    "STRING_LOOKUP",
    "DI_REGISTRATION",
    "ROUTE_REGISTRATION",
    "COMMAND_REGISTRATION",
    "IPC_REGISTRATION",
    "WORKER_REGISTRATION",
    "BUILD_REFERENCE",
    "PACKAGING_REFERENCE",
    "MIGRATION_REQUIREMENT",
    "FIXTURE_REQUIREMENT",
    "PLATFORM_SPECIFIC_USE",
    "PLANNED_CAPABILITY_DEPENDENCY",
    "USER_DATA_COMPATIBILITY",
    "REPLACEMENT",
    "TESTS",
    "BUILD",
    "GRAPHIFY_IMPACT",
    "INDEPENDENT_REVIEW",
]

MEANINGFUL_SUFFIXES = (
    "Adapter",
    "Block",
    "Command",
    "Component",
    "Controller",
    "Extension",
    "Handler",
    "Manager",
    "Model",
    "Module",
    "Provider",
    "Repository",
    "Resolver",
    "Route",
    "Schema",
    "Service",
    "Store",
    "View",
    "Worker",
)

METHOD_SIGNAL = re.compile(
    r"(?i)^(?:handle|load|open|register|resolve|run|save|setup|start|stop|sync|"
    r"import|export|dispatch|invoke|send|receive|create|delete|restore)"
)

DYNAMIC_IMPORT = re.compile(
    r"""\bimport\s*\(\s*["'](?P<specifier>[^"']+)["']\s*\)"""
)

EXCLUDED_PATH_SIGNALS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)(?:^|/)(?:cloud)(?:/|[._-])"), "MR-CAP-035"),
    (re.compile(r"(?i)(?:^|/)(?:remote[-_]?sync|sync[-_]?server)(?:/|[._-])"), "MR-CAP-036"),
    (re.compile(r"(?i)(?:^|/)(?:account|accounts)(?:/|[._-])"), "MR-CAP-037"),
    (re.compile(r"(?i)(?:^|/)(?:auth|authentication)(?:/|[._-])"), "MR-CAP-038"),
    (re.compile(r"(?i)(?:^|/)(?:team|teams)(?:/|[._-])"), "MR-CAP-039"),
    (re.compile(r"(?i)(?:^|/)(?:member|members)(?:/|[._-])"), "MR-CAP-040"),
    (re.compile(r"(?i)(?:^|/)(?:share|sharing|shared-link)(?:/|[._-])"), "MR-CAP-041"),
    (re.compile(r"(?i)(?:^|/)(?:invite|invitation|invitations)(?:/|[._-])"), "MR-CAP-042"),
    (re.compile(r"(?i)(?:^|/)(?:collaboration|collab)(?:/|[._-])"), "MR-CAP-043"),
    (re.compile(r"(?i)(?:^|/)(?:publish|publishing)(?:/|[._-])"), "MR-CAP-044"),
    (re.compile(r"(?i)(?:^|/)(?:billing)(?:/|[._-])"), "MR-CAP-045"),
    (re.compile(r"(?i)(?:^|/)(?:subscription|subscriptions)(?:/|[._-])"), "MR-CAP-046"),
    (re.compile(r"(?i)(?:^|/)(?:entitlement|paywall)(?:/|[._-])"), "MR-CAP-047"),
    (re.compile(r"(?i)(?:^|/)(?:ai|copilot)(?:/|[._-])"), "MR-CAP-048"),
    (re.compile(r"(?i)(?:^|/)(?:byok)(?:/|[._-])"), "MR-CAP-049"),
    (re.compile(r"(?i)(?:^|/)(?:embedding|embeddings)(?:/|[._-])"), "MR-CAP-050"),
    (re.compile(r"(?i)(?:^|/)(?:telemetry)(?:/|[._-])"), "MR-CAP-051"),
    (re.compile(r"(?i)(?:^|/)(?:analytics)(?:/|[._-])"), "MR-CAP-052"),
    (re.compile(r"(?i)(?:^|/)(?:graphql)(?:/|[._-])"), "MR-CAP-053"),
    (re.compile(r"(?i)(?:^|/)(?:remote[-_]?api|rest-api)(?:/|[._-])"), "MR-CAP-054"),
    (re.compile(r"(?i)(?:^|/)(?:remote[-_]?office)(?:/|[._-])"), "MR-CAP-055"),
    (re.compile(r"(?i)(?:^|/)(?:conversion|converter)(?:/|[._-])"), "MR-CAP-056"),
    (re.compile(r"(?i)(?:^|/)(?:ocr)(?:/|[._-])"), "MR-CAP-057"),
    (re.compile(r"(?i)(?:^|/)(?:remote[-_]?media)(?:/|[._-])"), "MR-CAP-058"),
    (re.compile(r"(?i)(?:^|/)(?:updater|auto-update)(?:/|[._-])"), "MR-CAP-059"),
    (re.compile(r"(?i)(?:^|/)(?:announcement|announcements)(?:/|[._-])"), "MR-CAP-060"),
    (re.compile(r"(?i)(?:^|/)(?:remote[-_]?flags?|feature-flags?)(?:/|[._-])"), "MR-CAP-061"),
    (re.compile(r"(?i)(?:^|/)(?:remote[-_]?templates?)(?:/|[._-])"), "MR-CAP-062"),
    (re.compile(r"(?i)(?:^|/)(?:enterprise)(?:/|[._-])"), "MR-CAP-063"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(
                json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            )


def stable_id(prefix: str, *values: str) -> str:
    material = "\0".join(values).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(material).hexdigest()[:20]}"


def normalize_codebase_path(value: str) -> str:
    if not value:
        return ""
    value = value.replace("\\", "/")
    if value.startswith("Codebase/"):
        return value
    if value == "Codebase":
        return value
    return f"Codebase/{value.lstrip('./')}"


def relative_source(path: str) -> str:
    return path[len("Codebase/") :] if path.startswith("Codebase/") else path


@lru_cache(maxsize=None)
def source_lines(path: str) -> tuple[str, ...]:
    if not path.startswith("Codebase/"):
        return ()
    target = CODEBASE_ROOT / Path(*relative_source(path).split("/"))
    try:
        return tuple(target.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return ()


def first_line_number(line_range: str) -> int:
    match = re.search(r"\d+", str(line_range))
    return int(match.group()) if match else 1


def line_anchor(path: str, line_number: int, symbol: str) -> str:
    lines = source_lines(path)
    if lines and 1 <= line_number <= len(lines):
        anchor = lines[line_number - 1].strip()
        if anchor:
            return anchor[:500]
    return symbol


def clean_symbol(label: str) -> str:
    value = label.strip().lstrip(".")
    return value[:-2] if value.endswith("()") else value


def entity_kind(
    symbol: str, line: str, path: str, file_anchor_kind: str = ""
) -> str:
    if file_anchor_kind:
        return file_anchor_kind
    lower_path = path.lower()
    lowered = symbol.lower()
    if "/preload/" in lower_path:
        return "PRELOAD_API"
    if "/ipc" in lower_path or "/handlers" in lower_path and "electron" in lower_path:
        return "IPC_HANDLER"
    if "/workers/" in lower_path or ".worker." in lower_path or symbol.endswith("Worker"):
        return "WORKER"
    if "/routes/" in lower_path or symbol.endswith("Route"):
        return "ROUTE"
    if "/commands/" in lower_path or symbol.endswith("Command"):
        return "COMMAND"
    if "resolver" in lowered:
        return "RESOURCE_RESOLVER"
    if symbol.endswith("Service"):
        return "SERVICE"
    if symbol.endswith("Store"):
        return "STORE"
    if symbol.endswith("Adapter"):
        return "ADAPTER"
    if symbol.endswith("Schema") or "/schema" in lower_path:
        return "SCHEMA"
    if symbol.endswith(("Component", "Block", "View", "Element")):
        return "COMPONENT"
    if symbol.endswith(("Handler", "Controller")):
        return "HANDLER"
    if symbol.endswith(("Provider", "Manager", "Repository")):
        return "SERVICE"
    if re.search(r"\b(class|struct|enum)\b", line):
        return "EXPORTED_CLASS"
    if re.search(r"\b(interface|type|trait)\b", line):
        return "EXPORTED_TYPE"
    if re.search(r"\b(fn|function)\b", line) or symbol.endswith(")"):
        return "EXPORTED_FUNCTION"
    return "EXPORTED_VALUE"


def is_exported(line: str, extension: str) -> bool:
    stripped = line.strip()
    if extension in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
        return bool(re.match(r"^(?:export|declare\s+global\b)", stripped))
    if extension == ".rs":
        return bool(re.match(r"^pub(?:\([^)]*\))?\s+", stripped))
    if extension in {".swift", ".kt", ".java", ".cs"}:
        return bool(re.match(r"^(?:public|open)\s+", stripped))
    if extension in {".py"}:
        return not stripped.startswith("_")
    return False


def meaningful_symbol(symbol: str, line: str, path: str, exported: bool) -> bool:
    if exported:
        return True
    if symbol.endswith(MEANINGFUL_SUFFIXES):
        return True
    lower_path = path.lower()
    return any(
        marker in lower_path
        for marker in (
            "/commands/",
            "/handlers",
            "/preload/",
            "/routes/",
            "/schema",
            "/services/",
            "/stores/",
            "/workers/",
        )
    ) and not symbol.startswith("_")


def tarjan_scc(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph.get(node, set()):
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] == indices[node]:
            component = []
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.append(current)
                if current == node:
                    break
            components.append(sorted(component))

    for node in sorted(set(graph) | {item for values in graph.values() for item in values}):
        if node not in indices:
            visit(node)
    return components


def transitive_files(roots: set[str], graph: dict[str, set[str]]) -> set[str]:
    reached = set(roots)
    queue = deque(sorted(roots))
    while queue:
        source = queue.popleft()
        for target in graph.get(source, set()):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def resolve_dynamic_import(
    source_path: str, specifier: str, inventory_paths: set[str]
) -> tuple[str, str]:
    if not specifier.startswith("."):
        return f"external:{specifier}", "EXTERNAL_REFERENCE"
    source_relative = PurePosixPath(relative_source(source_path))
    base = source_relative.parent / specifier
    candidates = [base]
    for extension in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json"):
        candidates.append(PurePosixPath(str(base) + extension))
        candidates.append(base / f"index{extension}")
    for candidate in candidates:
        normalized: list[str] = []
        for part in candidate.parts:
            if part == "..":
                if normalized:
                    normalized.pop()
            elif part not in {"", "."}:
                normalized.append(part)
        path = normalize_codebase_path(str(PurePosixPath(*normalized)))
        if path in inventory_paths:
            return path, "PATH"
    return f"unresolved:{specifier}", "UNRESOLVED_REFERENCE"


def main() -> None:
    OUTPUT_04.mkdir(parents=True, exist_ok=True)
    OUTPUT_05.mkdir(parents=True, exist_ok=True)
    inventory = read_jsonl(INVENTORY_DIR / "REPOSITORY_INVENTORY.jsonl")
    inventory_by_path = {record["path"]: record for record in inventory}
    inventory_paths = set(inventory_by_path)
    files = {
        path: record
        for path, record in inventory_by_path.items()
        if record["entityType"] in {"FILE", "ARCHIVE"}
    }
    package_inventory = read_json(INVENTORY_DIR / "PACKAGE_INVENTORY.json")
    capabilities_document = read_json(CAPABILITY_DIR / "CAPABILITY_REGISTRY.json")
    capabilities = capabilities_document["capabilities"]
    capability_by_id = {item["capabilityId"]: item for item in capabilities}
    capability_order = read_json(CAPABILITY_DIR / "CAPABILITY_DEPENDENCY_ORDER.json")
    architecture_nodes = read_jsonl(ARCHITECTURE_DIR / "ARCHITECTURE_NODES.jsonl")
    entrypoints = read_jsonl(
        ARCHITECTURE_DIR / "ENTRYPOINT_AND_BOOTSTRAP_REGISTRY.jsonl"
    )
    registrations = read_jsonl(
        ARCHITECTURE_DIR / "RUNTIME_REGISTRATION_REGISTRY.jsonl"
    )
    ipc_boundaries = read_jsonl(ARCHITECTURE_DIR / "IPC_AND_PRELOAD_MAP.jsonl")
    ast = read_json(AST_PATH)
    ast_nodes = ast["nodes"]
    ast_edges = ast["edges"]
    ast_node_by_id = {node["id"]: node for node in ast_nodes}

    capability_exact_paths: dict[str, list[str]] = defaultdict(list)
    capability_directory_paths: list[tuple[str, str]] = []
    for capability in capabilities:
        for path in capability.get("currentPaths", []):
            normalized = normalize_codebase_path(path)
            if normalized in inventory_by_path:
                capability_exact_paths[normalized].append(capability["capabilityId"])
                if inventory_by_path[normalized]["entityType"] == "DIRECTORY":
                    capability_directory_paths.append(
                        (normalized, capability["capabilityId"])
                    )

    def capability_ids_for_path(path: str) -> list[str]:
        exact = capability_exact_paths.get(path, [])
        inherited = [
            capability_id
            for directory, capability_id in capability_directory_paths
            if path.startswith(directory + "/")
        ]
        return sorted(set(exact + inherited))

    package_by_path = {
        path: record.get("package", "") for path, record in inventory_by_path.items()
    }
    runtime_by_path: dict[str, list[str]] = defaultdict(list)
    for registration in registrations:
        for raw_path in [
            registration.get("declaringPath", ""),
            registration.get("implementationPath", ""),
            *registration.get("consumerPaths", []),
        ]:
            path = normalize_codebase_path(raw_path)
            if path in inventory_by_path:
                runtime_by_path[path].append(registration["registrationId"])
    for boundary in ipc_boundaries:
        for field in ("declaringPath", "producerPath", "consumerPath"):
            path = normalize_codebase_path(boundary.get(field, ""))
            if path in inventory_by_path:
                runtime_by_path[path].append(boundary["boundaryId"])

    entities_by_key: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    ast_to_entity: dict[str, str] = {}

    def add_entity(
        path: str,
        symbol: str,
        kind: str,
        line_number: int,
        *,
        ast_node_id: str = "",
        evidence: list[dict[str, Any]] | None = None,
        explicit_capability_ids: list[str] | None = None,
        export_status: str = "NOT_APPLICABLE",
    ) -> str:
        path = normalize_codebase_path(path)
        if path not in inventory_by_path:
            return ""
        file_record = inventory_by_path[path]
        symbol = clean_symbol(symbol) or PurePosixPath(path).name
        key = (path, symbol, kind, line_number)
        capability_ids = sorted(
            set(capability_ids_for_path(path) + (explicit_capability_ids or []))
        )
        primary = capability_ids[0] if capability_ids else ""
        capability = capability_by_id.get(primary, {})
        entity_id = stable_id("MR-LOC", path, symbol, kind, str(line_number))
        anchor = line_anchor(path, line_number, symbol)
        new_evidence = evidence or []
        new_evidence.append(
            {
                "source": "CODEBASE",
                "path": path,
                "lineRange": f"{line_number}-{line_number}",
                "anchor": anchor,
                "fileSha256": file_record.get("sha256", ""),
            }
        )
        if key in entities_by_key:
            current = entities_by_key[key]
            current["capabilityIds"] = sorted(
                set(current["capabilityIds"] + capability_ids)
            )
            current["capabilityId"] = current["capabilityIds"][0] if current["capabilityIds"] else ""
            current["runtimeRegistrations"] = sorted(
                set(current["runtimeRegistrations"] + runtime_by_path.get(path, []))
            )
            current["evidence"].extend(
                item for item in new_evidence if item not in current["evidence"]
            )
            if ast_node_id:
                current["astNodeIds"] = sorted(
                    set(current.get("astNodeIds", []) + [ast_node_id])
                )
                ast_to_entity[ast_node_id] = current["entityId"]
            return current["entityId"]

        entity = {
            "entityId": entity_id,
            "entityType": kind,
            "capabilityId": primary,
            "capabilityIds": capability_ids,
            "currentStatus": "MAPPED",
            "currentPath": path,
            "symbol": symbol,
            "uniqueAnchor": anchor,
            "lineRange": f"{line_number}-{line_number}",
            "fileSha256": file_record.get("sha256", ""),
            "package": package_by_path.get(path, ""),
            "currentOwner": capability.get(
                "currentOwner", package_by_path.get(path, "") or "UNRESOLVED_OWNER"
            ),
            "intendedOwner": capability.get(
                "intendedOwner", "UNRESOLVED_PENDING_FOLDER_OWNERSHIP"
            ),
            "intendedFinalPath": capability.get(
                "intendedFinalPath", "UNRESOLVED_PENDING_FOLDER_OWNERSHIP"
            ),
            "publicEntryPoint": capability.get(
                "publicEntryPoint", "NOT_ESTABLISHED"
            ),
            "dependencies": [],
            "dependants": [],
            "runtimeRegistrations": sorted(set(runtime_by_path.get(path, []))),
            "configurationReferences": [],
            "tests": [],
            "plannedChanges": capability.get("requiredAdaptations", []),
            "verificationRequirements": capability.get(
                "verificationRequirements",
                ["Independent exact-location review", "Current hash revalidation"],
            ),
            "evidence": new_evidence,
            "astNodeIds": [ast_node_id] if ast_node_id else [],
            "exportStatus": export_status,
            "mappingConfidence": "CONFIRMED" if file_record.get("sha256") else "PARTIAL",
        }
        entities_by_key[key] = entity
        if ast_node_id:
            ast_to_entity[ast_node_id] = entity_id
        return entity_id

    # File anchors supplied by authoritative capability and architecture registries.
    for capability in capabilities:
        for raw_path in capability.get("currentPaths", []):
            path = normalize_codebase_path(raw_path)
            record = inventory_by_path.get(path)
            if record and record["entityType"] in {"FILE", "ARCHIVE"}:
                add_entity(
                    path,
                    PurePosixPath(path).name,
                    "CAPABILITY_FILE_ANCHOR",
                    1,
                    explicit_capability_ids=[capability["capabilityId"]],
                    evidence=[
                        {
                            "source": "CAPABILITY_REGISTRY",
                            "capabilityId": capability["capabilityId"],
                            "classification": capability["classification"],
                        }
                    ],
                )

    for package in package_inventory["packages"]:
        path = package.get("manifestPath", "")
        if path in inventory_by_path:
            add_entity(
                path,
                package["name"] or package["packageId"],
                "PACKAGE_MANIFEST",
                1,
                evidence=[
                    {
                        "source": "PACKAGE_INVENTORY",
                        "packageId": package["packageId"],
                        "ecosystem": package["ecosystem"],
                    }
                ],
            )

    for path, record in files.items():
        extension = record["extension"]
        lower_path = path.lower()
        kind = ""
        if record["classification"] == "BUILD":
            kind = "BUILD_ENTRYPOINT"
        elif record["classification"] == "MIGRATION":
            kind = "MIGRATION"
        elif record["classification"] == "TEST" and extension in SOURCE_EXTENSIONS:
            kind = "TEST_SUITE"
        elif (
            record["classification"] == "FIXTURE"
            and extension in SOURCE_EXTENSIONS
            and re.search(r"(?i)(?:fixture|loader)", PurePosixPath(path).name)
        ):
            kind = "FIXTURE_LOADER"
        elif (
            "schema" in PurePosixPath(path).name.lower()
            or "/schema/" in lower_path
            or extension in {".gql", ".graphql", ".graphqls"}
        ):
            kind = "SCHEMA"
        if kind:
            add_entity(path, PurePosixPath(path).name, kind, 1)

    architecture_sources = [
        ("ARCHITECTURE_NODE", item, "nodeId", "paths", "name")
        for item in architecture_nodes
    ]
    for kind, item, id_field, paths_field, symbol_field in architecture_sources:
        for raw_path in item.get(paths_field, []):
            path = normalize_codebase_path(raw_path)
            if path in files:
                evidence_item = next(
                    (
                        evidence
                        for evidence in item.get("evidence", [])
                        if normalize_codebase_path(evidence.get("path", "")) == path
                    ),
                    {},
                )
                line = first_line_number(evidence_item.get("lineRange", "1"))
                symbol = evidence_item.get("symbol", item[symbol_field])
                add_entity(
                    path,
                    symbol,
                    kind,
                    line,
                    evidence=[
                        {
                            "source": "ARCHITECTURE_NODES",
                            "architectureNodeId": item[id_field],
                            "confidence": item.get("confidence", ""),
                        }
                    ],
                )

    for entrypoint in entrypoints:
        path = normalize_codebase_path(entrypoint["declaringPath"])
        if path in files:
            add_entity(
                path,
                entrypoint["symbolOrAnchor"],
                "ENTRYPOINT",
                first_line_number(entrypoint.get("lineRange", "1")),
                evidence=[
                    {
                        "source": "ENTRYPOINT_REGISTRY",
                        "entrypointId": entrypoint["entrypointId"],
                        "entrypointType": entrypoint["entrypointType"],
                        "confidence": entrypoint["confidence"],
                    }
                ],
            )

    for registration in registrations:
        path = normalize_codebase_path(registration["declaringPath"])
        if path in files:
            registration_kind = {
                "route-registration": "ROUTE",
                "command-registration": "COMMAND",
                "command-registration-group": "COMMAND",
                "schema-registration": "SCHEMA",
                "worker-service-registry": "WORKER",
                "ipc-registration": "IPC_HANDLER",
                "ipc-event-registration": "IPC_HANDLER",
            }.get(registration["registrationType"], "RUNTIME_REGISTRATION")
            add_entity(
                path,
                registration["symbolOrAnchor"],
                registration_kind,
                first_line_number(registration.get("lineRange", "1")),
                evidence=[
                    {
                        "source": "RUNTIME_REGISTRATION_REGISTRY",
                        "registrationId": registration["registrationId"],
                        "registrationType": registration["registrationType"],
                        "confidence": registration["confidence"],
                    }
                ],
                explicit_capability_ids=registration.get("capabilityIds", []),
            )

    for boundary in ipc_boundaries:
        path = normalize_codebase_path(boundary["declaringPath"])
        if path in files:
            add_entity(
                path,
                boundary.get("channel")
                or ", ".join(boundary.get("exposedIdentifiers", []))
                or boundary["boundaryId"],
                "PRELOAD_API"
                if "preload" in boundary["boundaryType"]
                or boundary["boundaryType"] == "context-bridge"
                else "IPC_BOUNDARY",
                first_line_number(boundary.get("lineRange", "1")),
                evidence=[
                    {
                        "source": "IPC_AND_PRELOAD_MAP",
                        "boundaryId": boundary["boundaryId"],
                        "boundaryType": boundary["boundaryType"],
                        "confidence": boundary["confidence"],
                    }
                ],
            )

    # AST top-level declarations and selected meaningful methods.
    nodes_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    root_node_by_file: dict[str, str] = {}
    for node in ast_nodes:
        source_file = node.get("source_file", "")
        path = normalize_codebase_path(source_file)
        if path not in files:
            continue
        nodes_by_file[path].append(node)
        if (
            node.get("source_location") == "L1"
            and node.get("label") == PurePosixPath(source_file).name
        ):
            root_node_by_file[path] = node["id"]
    top_level_ids: set[str] = set()
    method_edges: list[dict[str, Any]] = []
    for edge in ast_edges:
        relation = edge.get("relation")
        if relation == "contains":
            source_node = ast_node_by_id.get(edge["source"], {})
            path = normalize_codebase_path(source_node.get("source_file", ""))
            if root_node_by_file.get(path) == edge["source"]:
                top_level_ids.add(edge["target"])
        elif relation == "method":
            method_edges.append(edge)

    for node_id in sorted(top_level_ids):
        node = ast_node_by_id.get(node_id)
        if not node:
            continue
        path = normalize_codebase_path(node.get("source_file", ""))
        record = files.get(path)
        if not record or record["classification"] in {
            "ASSET",
            "DOCUMENTATION",
            "LEGAL",
            "VENDOR",
        }:
            continue
        symbol = clean_symbol(node.get("label", ""))
        line_number = first_line_number(node.get("source_location", "1"))
        line = line_anchor(path, line_number, symbol)
        exported = is_exported(line, record["extension"])
        if not meaningful_symbol(symbol, line, path, exported):
            continue
        kind = entity_kind(symbol, line, path)
        add_entity(
            path,
            symbol,
            kind,
            line_number,
            ast_node_id=node_id,
            export_status="EXPORTED" if exported else "INTERNAL_MEANINGFUL",
            evidence=[
                {
                    "source": "GRAPHIFY_AST",
                    "astNodeId": node_id,
                    "sourceLocation": node.get("source_location", ""),
                }
            ],
        )

    selected_parent_nodes = set(ast_to_entity)
    for edge in method_edges:
        if edge["source"] not in selected_parent_nodes:
            continue
        target = ast_node_by_id.get(edge["target"])
        parent = ast_node_by_id.get(edge["source"], {})
        if not target:
            continue
        path = normalize_codebase_path(target.get("source_file", ""))
        symbol = clean_symbol(target.get("label", ""))
        parent_symbol = clean_symbol(parent.get("label", ""))
        lower_path = path.lower()
        if not (
            METHOD_SIGNAL.match(symbol)
            or any(
                marker in lower_path
                for marker in (
                    "/commands/",
                    "/handlers",
                    "/preload/",
                    "/routes/",
                    "/workers/",
                )
            )
        ):
            continue
        line_number = first_line_number(target.get("source_location", "1"))
        add_entity(
            path,
            f"{parent_symbol}.{symbol}",
            entity_kind(symbol, line_anchor(path, line_number, symbol), path),
            line_number,
            ast_node_id=target["id"],
            export_status="CLASS_MEMBER",
            evidence=[
                {
                    "source": "GRAPHIFY_AST",
                    "astNodeId": target["id"],
                    "parentAstNodeId": edge["source"],
                    "relation": "method",
                }
            ],
        )

    entities = sorted(
        entities_by_key.values(),
        key=lambda item: (
            item["currentPath"].casefold(),
            first_line_number(item["lineRange"]),
            item["symbol"].casefold(),
            item["entityType"],
        ),
    )
    entity_by_id = {entity["entityId"]: entity for entity in entities}
    entity_ids_by_path: dict[str, list[str]] = defaultdict(list)
    for entity in entities:
        entity_ids_by_path[entity["currentPath"]].append(entity["entityId"])

    # Dependency edges retain AST endpoint namespaces even when a node is intentionally
    # not promoted to a meaningful exact-location entity.
    dependencies: list[dict[str, Any]] = []
    dependency_keys: set[tuple[str, str, str, str, str]] = set()

    def endpoint_for_ast(node_id: str) -> dict[str, Any]:
        if node_id in ast_to_entity:
            entity_id = ast_to_entity[node_id]
            entity = entity_by_id[entity_id]
            return {
                "endpointType": "LOCATION_ENTITY",
                "endpointId": entity_id,
                "path": entity["currentPath"],
                "symbol": entity["symbol"],
                "resolved": True,
            }
        node = ast_node_by_id.get(node_id)
        if node:
            path = normalize_codebase_path(node.get("source_file", ""))
            return {
                "endpointType": "AST_NODE",
                "endpointId": node_id,
                "path": path if path in inventory_paths else "",
                "symbol": clean_symbol(node.get("label", "")),
                "resolved": True,
            }
        return {
            "endpointType": (
                "EXTERNAL_REFERENCE"
                if node_id.startswith("ref_")
                else "UNRESOLVED_AST_REFERENCE"
            ),
            "endpointId": node_id,
            "path": "",
            "symbol": node_id.removeprefix("ref_"),
            "resolved": False,
        }

    def path_endpoint(path: str) -> dict[str, Any]:
        normalized = normalize_codebase_path(path)
        if normalized in inventory_paths:
            return {
                "endpointType": "PATH",
                "endpointId": f"path:{normalized}",
                "path": normalized,
                "symbol": "",
                "resolved": True,
            }
        return {
            "endpointType": "UNRESOLVED_PATH_REFERENCE",
            "endpointId": f"unresolved-path:{path}",
            "path": normalized,
            "symbol": "",
            "resolved": False,
        }

    def add_dependency(
        edge_type: str,
        source: dict[str, Any],
        target: dict[str, Any],
        declaring_path: str,
        source_location: str,
        *,
        confidence: str,
        origin: str,
        context: str = "",
        evidence: Any = None,
    ) -> str:
        key = (
            edge_type,
            source["endpointId"],
            target["endpointId"],
            declaring_path,
            source_location,
        )
        if key in dependency_keys:
            return stable_id("MR-DEP", *key)
        dependency_keys.add(key)
        edge_id = stable_id("MR-DEP", *key)
        source_path = source.get("path", "")
        target_path = target.get("path", "")
        dependencies.append(
            {
                "edgeId": edge_id,
                "edgeType": edge_type,
                "sourceId": source["endpointId"],
                "sourceEndpointType": source["endpointType"],
                "sourcePath": source_path,
                "sourceSymbol": source.get("symbol", ""),
                "sourceResolved": source["resolved"],
                "targetId": target["endpointId"],
                "targetEndpointType": target["endpointType"],
                "targetPath": target_path,
                "targetSymbol": target.get("symbol", ""),
                "targetResolved": target["resolved"],
                "declaringPath": declaring_path,
                "sourceLocation": source_location,
                "confidence": confidence,
                "evidenceOrigin": origin,
                "context": context,
                "capabilityIds": sorted(
                    set(
                        capability_ids_for_path(source_path)
                        + capability_ids_for_path(target_path)
                    )
                ),
                "evidence": evidence if evidence is not None else {},
                "reviewStatus": "NOT_INDEPENDENTLY_REVIEWED",
            }
        )
        return edge_id

    excluded_ast_source_classes = {
        "ASSET",
        "DOCUMENTATION",
        "LEGAL",
        "UNKNOWN",
        "VENDOR",
    }
    for edge in ast_edges:
        relation = edge.get("relation", "")
        if relation not in AST_RELATION_TYPES:
            continue
        declaring_path = normalize_codebase_path(edge.get("source_file", ""))
        source_record = inventory_by_path.get(declaring_path)
        if not source_record or source_record["classification"] in excluded_ast_source_classes:
            continue
        source = endpoint_for_ast(edge["source"])
        target = endpoint_for_ast(edge["target"])
        edge_type = AST_RELATION_TYPES[relation]
        target_record = inventory_by_path.get(target.get("path", ""))
        if target_record:
            edge_type = {
                "ASSET": "ASSET_REFERENCE",
                "BUILD": "BUILD_REFERENCE",
                "FIXTURE": "FIXTURE_REFERENCE",
                "MIGRATION": "MIGRATION_DEPENDENCY",
                "PACKAGING": "PACKAGING_REFERENCE",
            }.get(target_record["classification"], edge_type)
        add_dependency(
            edge_type,
            source,
            target,
            declaring_path,
            edge.get("source_location", ""),
            confidence=edge.get("confidence", "EXTRACTED"),
            origin="GRAPHIFY_AST",
            context=edge.get("context", relation),
            evidence={"astRelation": relation, "astOrigin": edge.get("_origin", "")},
        )

    # Dynamic imports are absent as a separate AST relation, so extract literal calls.
    for path, record in files.items():
        if (
            record["extension"] not in SOURCE_EXTENSIONS
            or record["classification"] in excluded_ast_source_classes
        ):
            continue
        lines = source_lines(path)
        if not lines:
            continue
        for line_number, line in enumerate(lines, 1):
            for match in DYNAMIC_IMPORT.finditer(line):
                endpoint_id, endpoint_type = resolve_dynamic_import(
                    path, match.group("specifier"), inventory_paths
                )
                target_path = (
                    endpoint_id if endpoint_type == "PATH" else ""
                )
                target = (
                    path_endpoint(target_path)
                    if endpoint_type == "PATH"
                    else {
                        "endpointType": endpoint_type,
                        "endpointId": endpoint_id,
                        "path": "",
                        "symbol": match.group("specifier"),
                        "resolved": endpoint_type == "EXTERNAL_REFERENCE",
                    }
                )
                add_dependency(
                    "DYNAMIC_IMPORT",
                    path_endpoint(path),
                    target,
                    path,
                    f"L{line_number}",
                    confidence="EXTRACTED",
                    origin="LITERAL_DYNAMIC_IMPORT_SCAN",
                    context="import()",
                    evidence={"specifier": match.group("specifier")},
                )

    for planned in capability_order.get("edges", []):
        source_cap = planned["fromCapabilityId"]
        target_cap = planned["toCapabilityId"]
        source = {
            "endpointType": "CAPABILITY",
            "endpointId": f"capability:{source_cap}",
            "path": "",
            "symbol": capability_by_id[source_cap]["name"],
            "resolved": True,
        }
        target = {
            "endpointType": "CAPABILITY",
            "endpointId": f"capability:{target_cap}",
            "path": "",
            "symbol": capability_by_id[target_cap]["name"],
            "resolved": True,
        }
        add_dependency(
            "PLANNED_CAPABILITY_DEPENDENCY",
            source,
            target,
            "",
            "",
            confidence="INFERRED_FROM_LOCKED_PLAN",
            origin="CAPABILITY_DEPENDENCY_ORDER",
            context=planned.get("evidenceStatus", ""),
            evidence=planned,
        )

    for registration in registrations:
        source = path_endpoint(registration["declaringPath"])
        targets = [
            registration.get("implementationPath", ""),
            *registration.get("consumerPaths", []),
        ]
        for target_path in dict.fromkeys(item for item in targets if item):
            add_dependency(
                REGISTRATION_EDGE_TYPES.get(
                    registration["registrationType"], "DI_REGISTRATION"
                ),
                source,
                path_endpoint(target_path),
                normalize_codebase_path(registration["declaringPath"]),
                registration.get("lineRange", ""),
                confidence=registration.get("confidence", "CONFIRMED"),
                origin="RUNTIME_REGISTRATION_REGISTRY",
                context=registration["registrationType"],
                evidence={"registrationId": registration["registrationId"]},
            )

    for boundary in ipc_boundaries:
        source = path_endpoint(boundary["declaringPath"])
        edge_type = (
            "PRELOAD_EXPOSURE"
            if boundary["boundaryType"]
            in {"context-bridge", "preload-adapter", "dynamic-api-generation"}
            else "IPC_REGISTRATION"
        )
        for target_path in dict.fromkeys(
            item
            for item in (
                boundary.get("producerPath", ""),
                boundary.get("consumerPath", ""),
            )
            if item
        ):
            add_dependency(
                edge_type,
                source,
                path_endpoint(target_path),
                normalize_codebase_path(boundary["declaringPath"]),
                boundary.get("lineRange", ""),
                confidence=boundary.get("confidence", "CONFIRMED"),
                origin="IPC_AND_PRELOAD_MAP",
                context=boundary["boundaryType"],
                evidence={"boundaryId": boundary["boundaryId"]},
            )

    for entrypoint in entrypoints:
        source = path_endpoint(entrypoint["declaringPath"])
        edge_type = (
            "WORKER_REGISTRATION"
            if "worker" in entrypoint["entrypointType"]
            else "BUILD_REFERENCE"
        )
        for loaded in entrypoint.get("loads", []):
            normalized = normalize_codebase_path(loaded)
            target = (
                path_endpoint(normalized)
                if normalized in inventory_paths
                else {
                    "endpointType": "EXTERNAL_OR_SYMBOLIC_REFERENCE",
                    "endpointId": f"symbolic:{loaded}",
                    "path": "",
                    "symbol": loaded,
                    "resolved": False,
                }
            )
            add_dependency(
                edge_type,
                source,
                target,
                normalize_codebase_path(entrypoint["declaringPath"]),
                entrypoint.get("lineRange", ""),
                confidence=entrypoint.get("confidence", "CONFIRMED"),
                origin="ENTRYPOINT_REGISTRY",
                context=entrypoint["entrypointType"],
                evidence={"entrypointId": entrypoint["entrypointId"]},
            )

    dependencies.sort(key=lambda item: item["edgeId"])
    dependency_by_id = {item["edgeId"]: item for item in dependencies}

    # File-level dependency graph and entity relationships.
    file_outgoing: dict[str, set[str]] = defaultdict(set)
    file_incoming: dict[str, set[str]] = defaultdict(set)
    file_edge_ids: dict[str, list[str]] = defaultdict(list)
    static_graph: dict[str, set[str]] = defaultdict(set)
    for edge in dependencies:
        source_path = edge["sourcePath"]
        target_path = edge["targetPath"]
        if source_path in files:
            file_edge_ids[source_path].append(edge["edgeId"])
        if source_path in files and target_path in files and source_path != target_path:
            file_outgoing[source_path].add(target_path)
            file_incoming[target_path].add(source_path)
            if edge["edgeType"] in {"STATIC_IMPORT", "RE_EXPORT"}:
                static_graph[source_path].add(target_path)
        if edge["sourceEndpointType"] == "LOCATION_ENTITY":
            source_entity = entity_by_id[edge["sourceId"]]
            if edge["targetEndpointType"] == "LOCATION_ENTITY":
                source_entity["dependencies"].append(edge["targetId"])
                entity_by_id[edge["targetId"]]["dependants"].append(edge["sourceId"])
            if edge["edgeType"] in {
                "BUILD_REFERENCE",
                "PACKAGING_REFERENCE",
                "SCHEMA_REGISTRATION",
            }:
                source_entity["configurationReferences"].append(edge["edgeId"])

    test_paths = {
        path
        for path, record in files.items()
        if record["classification"] in {"TEST", "FIXTURE"}
    }
    for entity in entities:
        entity["dependencies"] = sorted(set(entity["dependencies"]))
        entity["dependants"] = sorted(set(entity["dependants"]))
        entity["configurationReferences"] = sorted(
            set(entity["configurationReferences"])
        )
        entity["tests"] = sorted(
            path
            for path in file_incoming.get(entity["currentPath"], set())
            if path in test_paths
        )

    # Runtime reachability roots.
    direct_runtime_evidence: dict[str, list[str]] = defaultdict(list)
    application_roots: set[str] = set()
    build_roots: set[str] = set()
    test_roots: set[str] = set(test_paths)
    for entrypoint in entrypoints:
        path = normalize_codebase_path(entrypoint["declaringPath"])
        if path not in files:
            continue
        entry_type = entrypoint["entrypointType"]
        runtime = entrypoint.get("runtime", "").lower()
        if "test" in entry_type or "test" in runtime:
            test_roots.add(path)
            direct_runtime_evidence[path].append(entrypoint["entrypointId"])
        elif entry_type in {"cli", "workspace-command-surface", "unit-test-aggregator"} or any(
            term in runtime for term in ("build", "developer", "tool")
        ):
            build_roots.add(path)
            direct_runtime_evidence[path].append(entrypoint["entrypointId"])
        else:
            application_roots.add(path)
            direct_runtime_evidence[path].append(entrypoint["entrypointId"])
    for registration in registrations:
        for raw_path in [
            registration.get("declaringPath", ""),
            registration.get("implementationPath", ""),
            *registration.get("consumerPaths", []),
        ]:
            path = normalize_codebase_path(raw_path)
            if path in files:
                application_roots.add(path)
                direct_runtime_evidence[path].append(registration["registrationId"])
    for boundary in ipc_boundaries:
        for field in ("declaringPath", "producerPath", "consumerPath"):
            path = normalize_codebase_path(boundary.get(field, ""))
            if path in files:
                application_roots.add(path)
                direct_runtime_evidence[path].append(boundary["boundaryId"])
    for path, record in files.items():
        if record["classification"] == "BUILD":
            build_roots.add(path)

    application_reachable = transitive_files(application_roots, file_outgoing)
    build_reachable = transitive_files(build_roots, file_outgoing)
    test_reachable = transitive_files(test_roots, file_outgoing)

    reachability: list[dict[str, Any]] = []
    reachability_class_by_path: dict[str, str] = {}
    for path, record in sorted(files.items()):
        if path in application_reachable:
            reach_class = "APPLICATION_REACHABLE"
            application_value = "YES"
        elif path in build_reachable:
            reach_class = "BUILD_OR_TOOL_REACHABLE"
            application_value = "NO"
        elif path in test_reachable or record["classification"] in {"TEST", "FIXTURE"}:
            reach_class = "TEST_OR_FIXTURE_REACHABLE"
            application_value = "NO"
        elif record["classification"] in {"DOCUMENTATION", "LEGAL", "VENDOR"}:
            reach_class = "NON_APPLICATION_DOCUMENT_OR_VENDOR"
            application_value = "NO"
        elif record["classification"] in {"ASSET", "PACKAGING"}:
            reach_class = "RUNTIME_ASSET_CANDIDATE"
            application_value = "UNKNOWN"
        else:
            reach_class = "UNKNOWN"
            application_value = "UNKNOWN"
        reachability_class_by_path[path] = reach_class
        reachability.append(
            {
                "path": path,
                "sha256": record["sha256"],
                "classification": record["classification"],
                "package": record["package"],
                "capabilityIds": capability_ids_for_path(path),
                "applicationRuntimeReachable": application_value,
                "reachabilityClass": reach_class,
                "directRegistrationEvidence": sorted(
                    set(direct_runtime_evidence.get(path, []))
                ),
                "incomingInternalPaths": sorted(file_incoming.get(path, set())),
                "outgoingInternalPaths": sorted(file_outgoing.get(path, set())),
                "dependencyEdgeIds": sorted(set(file_edge_ids.get(path, []))),
                "removalRisk": (
                    "CRITICAL"
                    if application_value == "YES"
                    else "HIGH"
                    if application_value == "UNKNOWN"
                    else "MEDIUM"
                ),
                "confidence": (
                    "CONFIRMED"
                    if direct_runtime_evidence.get(path)
                    else "STRONG"
                    if reach_class
                    in {
                        "APPLICATION_REACHABLE",
                        "BUILD_OR_TOOL_REACHABLE",
                        "TEST_OR_FIXTURE_REACHABLE",
                    }
                    else "PARTIAL"
                ),
                "evidenceBasis": [
                    "Graphify AST internal import/re-export closure",
                    "Architecture entrypoint, registration, and IPC registries",
                    "Corpus classification",
                ],
                "requiresFurtherAnalysis": application_value == "UNKNOWN",
            }
        )

    # Circular import SCCs.
    components = tarjan_scc(static_graph)
    circular_components = [component for component in components if len(component) > 1]
    self_loops = sorted(
        path for path, targets in static_graph.items() if path in targets
    )
    circular_report = {
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "graphType": "FILE_LEVEL_STATIC_IMPORT_AND_RE_EXPORT",
        "status": "MAPPED_NOT_REPAIRED",
        "nodeCount": len(set(static_graph) | {t for v in static_graph.values() for t in v}),
        "edgeCount": sum(len(values) for values in static_graph.values()),
        "stronglyConnectedComponentCount": len(circular_components),
        "selfLoopCount": len(self_loops),
        "stronglyConnectedComponents": [
            {
                "componentId": stable_id("MR-CYCLE", *component),
                "size": len(component),
                "paths": component,
                "packages": sorted(
                    set(package_by_path.get(path, "") for path in component)
                    - {""}
                ),
                "capabilityIds": sorted(
                    set(
                        capability_id
                        for path in component
                        for capability_id in capability_ids_for_path(path)
                    )
                ),
                "status": "CYCLE_REQUIRES_REVIEW",
            }
            for component in sorted(
                circular_components, key=lambda value: (-len(value), value)
            )
        ],
        "selfLoops": self_loops,
        "limitations": [
            "Only internal file targets resolved by the structural AST are included.",
            "Dynamic imports are mapped separately and are not included in static SCCs.",
            "A cycle is architectural evidence, not a correctness or deletion finding.",
        ],
    }

    # Removal and reorganisation blast radii.
    removal_blast: list[dict[str, Any]] = []
    reorganisation_blast: list[dict[str, Any]] = []
    for capability in capabilities:
        current_paths = sorted(
            set(
                normalize_codebase_path(path)
                for path in capability.get("currentPaths", [])
                if normalize_codebase_path(path) in inventory_paths
            )
        )
        incoming_paths = sorted(
            set(
                source
                for path in current_paths
                for source in file_incoming.get(path, set())
                if source not in current_paths
            )
        )
        outgoing_paths = sorted(
            set(
                target
                for path in current_paths
                for target in file_outgoing.get(path, set())
                if target not in current_paths
            )
        )
        runtime_ids = sorted(
            set(
                registration_id
                for path in current_paths
                for registration_id in runtime_by_path.get(path, [])
            )
        )
        test_references = sorted(path for path in incoming_paths if path in test_paths)
        app_reachable_paths = sorted(
            path for path in current_paths if path in application_reachable
        )
        if capability["classification"] == "REMOVE":
            removal_blast.append(
                {
                    "blastRadiusId": stable_id(
                        "MR-REMOVAL-BLAST", capability["capabilityId"]
                    ),
                    "capabilityId": capability["capabilityId"],
                    "capabilityName": capability["name"],
                    "classification": capability["classification"],
                    "currentPaths": current_paths,
                    "incomingDependentPaths": incoming_paths,
                    "outgoingDependencyPaths": outgoing_paths,
                    "runtimeRegistrations": runtime_ids,
                    "applicationReachablePaths": app_reachable_paths,
                    "testReferences": test_references,
                    "dependantCapabilityIds": capability.get("dependants", []),
                    "dependencyCapabilityIds": capability.get("dependencies", []),
                    "replacementCapabilityId": capability.get(
                        "replacementCapabilityId"
                    ),
                    "riskLevel": (
                        "CRITICAL"
                        if runtime_ids or app_reachable_paths
                        else "HIGH"
                        if incoming_paths
                        else "MEDIUM"
                    ),
                    "requiredProofs": {
                        proof: "NOT_RUN" for proof in PROOF_REQUIREMENTS
                    },
                    "status": "CANDIDATE_BOUNDARY_NOT_AUTHORIZED_FOR_DELETION",
                    "evidence": capability.get("evidence", []),
                }
            )
        if current_paths and capability["classification"] != "ADD":
            reorganisation_blast.append(
                {
                    "blastRadiusId": stable_id(
                        "MR-REORG-BLAST", capability["capabilityId"]
                    ),
                    "capabilityId": capability["capabilityId"],
                    "capabilityName": capability["name"],
                    "classification": capability["classification"],
                    "currentPaths": current_paths,
                    "intendedFinalPath": capability.get("intendedFinalPath", ""),
                    "incomingDependentPaths": incoming_paths,
                    "outgoingDependencyPaths": outgoing_paths,
                    "runtimeRegistrations": runtime_ids,
                    "configurationReferences": sorted(
                        edge["edgeId"]
                        for edge in dependencies
                        if edge["declaringPath"] in current_paths
                        and edge["edgeType"]
                        in {"BUILD_REFERENCE", "PACKAGING_REFERENCE"}
                    ),
                    "testReferences": test_references,
                    "packageBoundaryImplications": sorted(
                        set(package_by_path.get(path, "") for path in current_paths)
                        - {""}
                    ),
                    "riskLevel": (
                        "CRITICAL"
                        if runtime_ids
                        else capability.get("riskLevel", "MEDIUM")
                    ),
                    "requiredVerification": capability.get(
                        "verificationRequirements", []
                    ),
                    "status": "PLANNED_NOT_MOVED",
                }
            )

    # Exact-content duplicate candidates.
    duplicate_groups: dict[str, list[str]] = defaultdict(list)
    code_classifications = {
        "BUILD",
        "CONFIG",
        "GENERATED",
        "MIGRATION",
        "PACKAGING",
        "SOURCE",
    }
    for path, record in files.items():
        if (
            record["classification"] in code_classifications
            and record["sizeBytes"] >= 128
            and record["sha256"]
            and record["extension"] in SOURCE_EXTENSIONS
        ):
            duplicate_groups[record["sha256"]].append(path)
    duplicate_candidates = []
    for digest, paths in sorted(duplicate_groups.items()):
        if len(paths) < 2:
            continue
        duplicate_candidates.append(
            {
                "candidateId": stable_id("MR-DUPLICATE", digest),
                "detectionType": "EXACT_SHA256_CODE_DUPLICATE",
                "sha256": digest,
                "paths": sorted(paths),
                "packages": sorted(
                    set(package_by_path.get(path, "") for path in paths) - {""}
                ),
                "entityIds": sorted(
                    entity_id for path in paths for entity_id in entity_ids_by_path[path]
                ),
                "runtimeReachability": {
                    path: reachability_class_by_path[path] for path in sorted(paths)
                },
                "replacement": "UNDETERMINED",
                "requiredProofs": {
                    proof: "NOT_RUN" for proof in PROOF_REQUIREMENTS
                },
                "confidence": "CONFIRMED_IDENTICAL_CONTENT_ONLY",
                "status": "CANDIDATE_NOT_DELETION_PROOF",
                "falsePositiveRisks": [
                    "Generated files, platform variants, fixtures, and intentional package isolation may be byte-identical.",
                    "Exact content identity does not establish equivalent ownership or runtime role.",
                ],
            }
        )

    # Dead-code candidates: structural isolation and plan-designated abandoned paths only.
    abandoned_capability_paths = set(
        normalize_codebase_path(path)
        for path in capability_by_id.get("MR-CAP-066", {}).get("currentPaths", [])
    )
    dead_candidates = []
    for path, record in sorted(files.items()):
        if record["classification"] not in {"SOURCE", "GENERATED"}:
            continue
        plan_signal = path in abandoned_capability_paths
        isolated = (
            not file_incoming.get(path)
            and not file_outgoing.get(path)
            and path not in application_roots
            and path not in build_roots
            and path not in test_roots
            and not capability_ids_for_path(path)
            and PurePosixPath(path).name
            not in {"index.ts", "index.tsx", "index.js", "index.mjs"}
            and not PurePosixPath(path).name.endswith(".d.ts")
        )
        if not (plan_signal or isolated):
            continue
        dead_candidates.append(
            {
                "candidateId": stable_id("MR-DEAD", path),
                "path": path,
                "sha256": record["sha256"],
                "package": record["package"],
                "candidateBasis": (
                    "LOCKED_PLAN_ABANDONED_CODE_SEARCH_RESULT"
                    if plan_signal
                    else "NO_RESOLVED_INTERNAL_AST_INCOMING_OR_OUTGOING_EDGES"
                ),
                "applicationRuntimeReachability": reachability_class_by_path[path],
                "runtimeRegistrations": runtime_by_path.get(path, []),
                "incomingPaths": sorted(file_incoming.get(path, set())),
                "outgoingPaths": sorted(file_outgoing.get(path, set())),
                "replacement": "UNDETERMINED",
                "requiredProofs": {
                    proof: "NOT_RUN" for proof in PROOF_REQUIREMENTS
                },
                "confidence": "LOW",
                "status": "CANDIDATE_NOT_DELETION_PROOF",
                "falsePositiveRisks": [
                    "String lookup, native registration, package exports, generated loading, and unresolved aliases may bypass AST edges.",
                    "Zero resolved AST edges is not proof of non-reachability.",
                ],
            }
        )

    # Excluded-system boundary records, authoritative capability paths plus path signals.
    excluded_capabilities = {
        capability_id: capability_by_id[capability_id]
        for capability_id in (
            f"MR-CAP-{number:03d}" for number in range(35, 64)
        )
    }
    boundary_sources: dict[tuple[str, str], str] = {}
    for capability_id, capability in excluded_capabilities.items():
        for raw_path in capability.get("currentPaths", []):
            path = normalize_codebase_path(raw_path)
            if path in inventory_paths:
                boundary_sources[(capability_id, path)] = "CAPABILITY_REGISTRY_CURRENT_PATH"
    for path, record in files.items():
        if record["classification"] not in {
            "BUILD",
            "CONFIG",
            "GENERATED",
            "PACKAGING",
            "SOURCE",
            "TEST",
        }:
            continue
        relative = relative_source(path)
        for pattern, capability_id in EXCLUDED_PATH_SIGNALS:
            if pattern.search(relative):
                boundary_sources.setdefault(
                    (capability_id, path), "PATH_SEMANTIC_DISCOVERY_SIGNAL"
                )

    excluded_boundaries = []
    for (capability_id, path), basis in sorted(boundary_sources.items()):
        capability = excluded_capabilities[capability_id]
        other_caps = [
            item
            for item in capability_ids_for_path(path)
            if item != capability_id
        ]
        retained_caps = [
            item
            for item in other_caps
            if capability_by_id[item]["classification"] != "REMOVE"
        ]
        registration_ids = sorted(set(runtime_by_path.get(path, [])))
        ipc_ids = [
            boundary["boundaryId"]
            for boundary in ipc_boundaries
            if path
            in {
                normalize_codebase_path(boundary.get("declaringPath", "")),
                normalize_codebase_path(boundary.get("producerPath", "")),
                normalize_codebase_path(boundary.get("consumerPath", "")),
            }
        ]
        symbol_entities = [
            entity_by_id[entity_id] for entity_id in entity_ids_by_path.get(path, [])
        ]
        excluded_boundaries.append(
            {
                "boundaryId": stable_id(
                    "MR-EXCLUDED", capability_id, path
                ),
                "capabilityId": capability_id,
                "subsystem": capability["name"],
                "path": path,
                "sha256": inventory_by_path[path].get("sha256", ""),
                "package": package_by_path.get(path, ""),
                "symbols": [
                    {
                        "entityId": entity["entityId"],
                        "symbol": entity["symbol"],
                        "entityType": entity["entityType"],
                        "lineRange": entity["lineRange"],
                    }
                    for entity in symbol_entities
                ],
                "uiEntry": any(
                    entity["entityType"] == "COMPONENT"
                    for entity in symbol_entities
                ),
                "route": [
                    entity["entityId"]
                    for entity in symbol_entities
                    if entity["entityType"] == "ROUTE"
                ],
                "command": [
                    entity["entityId"]
                    for entity in symbol_entities
                    if entity["entityType"] == "COMMAND"
                ],
                "store": [
                    entity["entityId"]
                    for entity in symbol_entities
                    if entity["entityType"] == "STORE"
                ],
                "service": [
                    entity["entityId"]
                    for entity in symbol_entities
                    if entity["entityType"] in {"SERVICE", "ADAPTER"}
                ],
                "worker": [
                    entity["entityId"]
                    for entity in symbol_entities
                    if entity["entityType"] == "WORKER"
                ],
                "apiBoundary": [
                    entity["entityId"]
                    for entity in symbol_entities
                    if entity["entityType"]
                    in {"IPC_BOUNDARY", "IPC_HANDLER", "PRELOAD_API"}
                ],
                "ipcBoundaries": ipc_ids,
                "runtimeRegistrations": registration_ids,
                "configurationReferences": sorted(
                    edge["edgeId"]
                    for edge in dependencies
                    if edge["declaringPath"] == path
                    and edge["edgeType"]
                    in {"BUILD_REFERENCE", "PACKAGING_REFERENCE"}
                ),
                "environmentVariables": sorted(
                    set(
                        re.findall(
                            r"\b[A-Z][A-Z0-9_]{3,}\b",
                            "\n".join(source_lines(path)[:500]),
                        )
                    )
                )[:100],
                "tests": sorted(
                    source
                    for source in file_incoming.get(path, set())
                    if source in test_paths
                ),
                "dependencies": sorted(file_outgoing.get(path, set())),
                "dependants": sorted(file_incoming.get(path, set())),
                "localReusableLogicMixedInside": bool(retained_caps),
                "mixedRetainedCapabilityIds": retained_caps,
                "requiredReplacement": capability.get(
                    "replacementCapabilityId"
                )
                or "REQUIRES_REPLACEMENT_OR_LOCAL_ADAPTER_PROOF",
                "removalClassification": "REMOVE_LATER_ONLY_AFTER_RECEIPT_PROOF",
                "dataCompatibilityRole": (
                    "REQUIRES_COMPATIBILITY_REVIEW"
                    if any(
                        term in capability["name"].lower()
                        for term in ("account", "auth", "sync", "collaboration")
                    )
                    else "NO_COMPATIBILITY_CONCLUSION_YET"
                ),
                "licenceImplications": "REQUIRES_SEPARATE_LICENCE_REVIEW",
                "plannedQuarantineBatch": "UNASSIGNED_FUTURE_BATCH",
                "verificationRequired": PROOF_REQUIREMENTS,
                "runtimeReachability": reachability_class_by_path.get(
                    path, "DIRECTORY_OR_UNKNOWN"
                ),
                "removalRisk": (
                    "CRITICAL"
                    if registration_ids
                    or path in application_reachable
                    or retained_caps
                    else "HIGH"
                    if file_incoming.get(path)
                    else "MEDIUM"
                ),
                "discoveryBasis": basis,
                "mappingConfidence": (
                    "STRONG"
                    if basis == "CAPABILITY_REGISTRY_CURRENT_PATH"
                    else "PARTIAL_SEMANTIC_SIGNAL"
                ),
                "status": "MAPPED_BOUNDARY_NOT_AUTHORIZED_FOR_REMOVAL",
                "evidence": [
                    {
                        "path": path,
                        "sha256": inventory_by_path[path].get("sha256", ""),
                        "basis": basis,
                    }
                ],
            }
        )

    # Location indexes and compact symbol ledger.
    by_path = {
        path: sorted(entity_ids)
        for path, entity_ids in sorted(entity_ids_by_path.items())
    }
    by_capability: dict[str, list[str]] = defaultdict(list)
    for entity in entities:
        for capability_id in entity["capabilityIds"]:
            by_capability[capability_id].append(entity["entityId"])
    exact_document = {
        "project": "MindRoom",
        "phase": "GRAPHIFY_MAPPING",
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "generatorVersion": SCRIPT_VERSION,
        "status": "MAPPED_NOT_INDEPENDENTLY_REVIEWED",
        "implementationPerformed": False,
        "deletionOrQuarantinePerformed": False,
        "sourceEvidence": {
            "repositoryInventory": "Graphify/01 Corpus Inventory/REPOSITORY_INVENTORY.jsonl",
            "architectureMap": "Graphify/02 Architecture Map",
            "capabilityRegistry": "Graphify/03 Capability Map/CAPABILITY_REGISTRY.json",
            "structuralAst": "Graphify/11 Completion/graphify-out/.graphify_ast.json",
        },
        "entityCount": len(entities),
        "entities": entities,
        "indexes": {
            "byPath": by_path,
            "byCapability": {
                capability_id: sorted(entity_ids)
                for capability_id, entity_ids in sorted(by_capability.items())
            },
            "byEntityType": {
                kind: sorted(
                    entity["entityId"]
                    for entity in entities
                    if entity["entityType"] == kind
                )
                for kind in sorted(set(entity["entityType"] for entity in entities))
            },
        },
        "limitations": [
            "Meaningful symbols include exported/top-level AST declarations and selected runtime-significant class methods; local variables are intentionally excluded.",
            "Line ranges are evidence aids; unique declaration anchors and current file SHA-256 are relocation-resistant evidence.",
            "Capability assignment follows exact currentPaths and mapped directory ownership; unassigned symbols remain explicit rather than guessed.",
        ],
    }
    symbol_records = [
        {
            "symbolId": stable_id(
                "MR-SYM",
                entity["currentPath"],
                entity["symbol"],
                entity["entityType"],
                entity["lineRange"],
            ),
            "locationEntityId": entity["entityId"],
            "symbol": entity["symbol"],
            "symbolKind": entity["entityType"],
            "exportStatus": entity["exportStatus"],
            "currentPath": entity["currentPath"],
            "lineRange": entity["lineRange"],
            "uniqueAnchor": entity["uniqueAnchor"],
            "fileSha256": entity["fileSha256"],
            "capabilityIds": entity["capabilityIds"],
            "astNodeIds": entity["astNodeIds"],
            "mappingConfidence": entity["mappingConfidence"],
            "status": "MAPPED",
        }
        for entity in entities
        if entity["entityType"]
        not in {
            "ARCHITECTURE_NODE",
            "BUILD_ENTRYPOINT",
            "CAPABILITY_FILE_ANCHOR",
            "PACKAGE_MANIFEST",
            "TEST_SUITE",
        }
    ]

    # Human summary.
    edge_type_counts = Counter(edge["edgeType"] for edge in dependencies)
    endpoint_type_counts = Counter(
        endpoint_type
        for edge in dependencies
        for endpoint_type in (
            edge["sourceEndpointType"],
            edge["targetEndpointType"],
        )
    )
    top_incoming = sorted(
        file_incoming.items(), key=lambda item: (-len(item[1]), item[0])
    )[:25]
    top_outgoing = sorted(
        file_outgoing.items(), key=lambda item: (-len(item[1]), item[0])
    )[:25]
    edge_rows = "\n".join(
        f"| `{kind}` | {count:,} |" for kind, count in edge_type_counts.most_common()
    )
    endpoint_rows = "\n".join(
        f"| `{kind}` | {count:,} |"
        for kind, count in endpoint_type_counts.most_common()
    )
    incoming_rows = "\n".join(
        f"| `{path}` | {len(values):,} |" for path, values in top_incoming
    )
    outgoing_rows = "\n".join(
        f"| `{path}` | {len(values):,} |" for path, values in top_outgoing
    )
    dependency_summary = f"""# MindRoom Dependency and Impact Summary

Generated: `{utc_now()}`

## Scope

- Exact-location entities: **{len(entities):,}**
- Meaningful symbol records: **{len(symbol_records):,}**
- Dependency edges: **{len(dependencies):,}**
- Internal file dependency sources: **{len(file_outgoing):,}**
- Static import/re-export SCCs with more than one file: **{len(circular_components):,}**
- Removal blast-radius records: **{len(removal_blast):,}**
- Reorganisation blast-radius records: **{len(reorganisation_blast):,}**
- Runtime reachability records: **{len(reachability):,}**
- Exact duplicate-code candidates: **{len(duplicate_candidates):,}**
- Dead/abandoned code candidates: **{len(dead_candidates):,}**
- Excluded-system boundary records: **{len(excluded_boundaries):,}**

## Dependency types

| Edge type | Count |
|---|---:|
{edge_rows}

## Endpoint namespaces

| Endpoint type | Count |
|---|---:|
{endpoint_rows}

`LOCATION_ENTITY`, `AST_NODE`, `PATH`, and `CAPABILITY` endpoints validate against their authoritative registry. External, symbolic, and unresolved endpoints are explicitly typed and never presented as local resolved symbols.

## Highest internal file fan-in

| Path | Distinct internal dependant files |
|---|---:|
{incoming_rows}

## Highest internal file fan-out

| Path | Distinct internal dependency files |
|---|---:|
{outgoing_rows}

## Safety conclusions

- No dead-code or duplicate-code record is deletion proof.
- No source was moved, rewritten, quarantined, deleted, or implemented.
- Removal boundaries with runtime registrations, application reachability, retained-capability overlap, or internal dependants are marked high/critical risk.
- Dynamic import evidence is limited to literal `import("...")` calls; computed specifiers remain a required future string-lookup proof.
- AST call/reference edges are structural evidence, not proof of application runtime execution.
- Static SCCs are reported without repair recommendations; cycles require independent architectural review.
"""

    # Validate before writing.
    entity_ids = set(entity_by_id)
    ast_ids = set(ast_node_by_id)
    capability_ids = set(capability_by_id)
    errors: list[str] = []
    if len(entity_ids) != len(entities):
        errors.append("Duplicate exact-location entity IDs")
    for entity in entities:
        if entity["currentPath"] not in inventory_paths:
            errors.append(f"Missing exact-location path {entity['currentPath']}")
        record = inventory_by_path[entity["currentPath"]]
        if record["entityType"] in {"FILE", "ARCHIVE"} and entity["fileSha256"] != record["sha256"]:
            errors.append(f"Stale exact-location hash {entity['entityId']}")
        if any(item not in capability_ids for item in entity["capabilityIds"]):
            errors.append(f"Unknown entity capability {entity['entityId']}")
    for edge in dependencies:
        checks = [
            (
                edge["sourceEndpointType"],
                edge["sourceId"],
                edge["sourcePath"],
                edge["sourceResolved"],
            ),
            (
                edge["targetEndpointType"],
                edge["targetId"],
                edge["targetPath"],
                edge["targetResolved"],
            ),
        ]
        for endpoint_type, endpoint_id, path, resolved in checks:
            if endpoint_type == "LOCATION_ENTITY" and endpoint_id not in entity_ids:
                errors.append(f"Unknown location endpoint {endpoint_id}")
            elif endpoint_type == "AST_NODE" and endpoint_id not in ast_ids:
                errors.append(f"Unknown AST endpoint {endpoint_id}")
            elif endpoint_type == "PATH" and path not in inventory_paths:
                errors.append(f"Unknown path endpoint {path}")
            elif endpoint_type == "CAPABILITY":
                capability_id = endpoint_id.removeprefix("capability:")
                if capability_id not in capability_ids:
                    errors.append(f"Unknown capability endpoint {endpoint_id}")
            elif endpoint_type in {
                "EXTERNAL_OR_SYMBOLIC_REFERENCE",
                "EXTERNAL_REFERENCE",
                "UNRESOLVED_AST_REFERENCE",
                "UNRESOLVED_PATH_REFERENCE",
                "UNRESOLVED_REFERENCE",
            } and resolved and endpoint_type.startswith("UNRESOLVED"):
                errors.append(f"False resolved endpoint {endpoint_id}")
    forbidden_status = re.compile(r"\b(?:APPROVED|DELETED|PURGED)\b")
    for record in (
        removal_blast
        + duplicate_candidates
        + dead_candidates
        + excluded_boundaries
    ):
        if forbidden_status.search(json.dumps(record)):
            errors.append(f"Forbidden completion status in {record}")
    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors[:100]))

    write_json(EXACT_LOCATION_PATH, exact_document)
    write_jsonl(SYMBOL_PATH, symbol_records)
    write_jsonl(DEPENDENCY_PATH, dependencies)
    DEPENDENCY_SUMMARY_PATH.write_text(
        dependency_summary, encoding="utf-8", newline="\n"
    )
    write_json(CIRCULAR_PATH, circular_report)
    write_jsonl(REMOVAL_BLAST_PATH, removal_blast)
    write_jsonl(REORGANISATION_BLAST_PATH, reorganisation_blast)
    write_jsonl(REACHABILITY_PATH, reachability)
    write_jsonl(DUPLICATE_PATH, duplicate_candidates)
    write_jsonl(DEAD_PATH, dead_candidates)
    write_jsonl(EXCLUDED_BOUNDARY_PATH, excluded_boundaries)

    # Parse all emitted JSON/JSONL.
    read_json(EXACT_LOCATION_PATH)
    read_json(CIRCULAR_PATH)
    for path in (
        SYMBOL_PATH,
        DEPENDENCY_PATH,
        REMOVAL_BLAST_PATH,
        REORGANISATION_BLAST_PATH,
        REACHABILITY_PATH,
        DUPLICATE_PATH,
        DEAD_PATH,
        EXCLUDED_BOUNDARY_PATH,
    ):
        read_jsonl(path)

    print(
        json.dumps(
            {
                "status": "PASS",
                "exactLocationEntities": len(entities),
                "symbolRecords": len(symbol_records),
                "dependencyEdges": len(dependencies),
                "circularComponents": len(circular_components),
                "removalBlastRecords": len(removal_blast),
                "reorganisationBlastRecords": len(reorganisation_blast),
                "runtimeReachabilityRecords": len(reachability),
                "duplicateCandidates": len(duplicate_candidates),
                "deadCodeCandidates": len(dead_candidates),
                "excludedBoundaryRecords": len(excluded_boundaries),
                "codebaseMutated": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
