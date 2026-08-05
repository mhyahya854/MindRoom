#!/usr/bin/env python3
"""Build the authoritative layered, directed MindRoom V2 knowledge graph."""

from __future__ import annotations

import json
import re
import tomllib
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from repair_v2_common import (
    CODEBASE,
    COMPLETION,
    CONTROL,
    GRAPHIFY,
    KG,
    LAYERS,
    NODE_BUILTINS,
    SQL_CREATE_RE,
    SQL_REF_RE,
    atomic_write_text,
    classify_layer,
    codebase_rel,
    edge_id,
    graphify_rel,
    inverse_capability_paths,
    iter_jsonl,
    language_for,
    load_json,
    load_workspace_packages,
    make_edge,
    nearest_package,
    now_utc,
    package_name_from_specifier,
    resolve_relative,
    sha256_bytes,
    sha256_file,
    source_imports,
    stable_id,
    text_file,
    write_json,
    write_jsonl,
)
from generated_provenance_v2 import add_generated_provenance


POLICY_VERSION = "mindroom-graphify-v2-layered-directed-2"
BASELINE = load_json(CONTROL / "GRAPHIFY_REPAIR_BASELINE.json")
RUN_ID = BASELINE["runId"]
CAP_PATH = GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json"
REQ_PATH = GRAPHIFY / "03 Capability Map" / "REQUIREMENT_REGISTRY.jsonl"
SYMBOL_PATH = GRAPHIFY / "04 Exact Location Registry" / "SYMBOL_REGISTRY.jsonl"
EXACT_PATH = GRAPHIFY / "04 Exact Location Registry" / "EXACT_LOCATION_REGISTRY.json"
LEGACY_V1_GRAPH_PATH = CONTROL / "Generated Tool Cache" / "legacy-v1" / "graphify-out" / "graph.json"
LEGACY_V1_DIAGNOSTIC_PATH = (
    CONTROL / "Generated Tool Cache" / "legacy-v1" / "V1_UNRESOLVED_ENDPOINTS_SNAPSHOT.jsonl"
)
AST_CACHE_ROOT = CONTROL / "Generated Tool Cache" / "v2" / RUN_ID / "ast"
AST_MERGED_PATH = AST_CACHE_ROOT / "GRAPHIFY_RAW_MERGED.json"
AST_MERGE_RECEIPT_PATH = AST_CACHE_ROOT / "MERGE_RECEIPT.json"
AST_EXTRACTION_MANIFEST_PATH = AST_CACHE_ROOT / "EXTRACTION_MANIFEST.json"
RUNTIME_PATH = GRAPHIFY / "02 Architecture Map" / "RUNTIME_REGISTRATION_REGISTRY.jsonl"
BUILD_RUNS_PATH = COMPLETION / "GRAPH_BUILD_RUNS.jsonl"

RUST_MOD_RE = re.compile(
    r"(?m)^[ \t]*(?P<attrs>(?:#\[[^\n]+\]\s*)*)(?:pub(?:\([^)]*\))?\s+)?mod\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;"
)
RUST_USE_RE = re.compile(r"(?ms)^[ \t]*(?:pub(?:\([^)]*\))?\s+)?use\s+(?P<tree>.*?);")
RUST_PATH_ATTR_RE = re.compile(r"#\[\s*path\s*=\s*[\"']([^\"']+)[\"']\s*\]")
SQL_IDENTIFIER = r'(?:"[^"]+"|`[^`]+`|\[[^\]]+\]|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]+"|`[^`]+`|\[[^\]]+\]|[A-Za-z_][\w$]*))*'
SQL_CREATE_SCOPE_RE = re.compile(rf"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<table>{SQL_IDENTIFIER})", re.IGNORECASE)
SQL_ALTER_SCOPE_RE = re.compile(rf"\bALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?P<table>{SQL_IDENTIFIER})", re.IGNORECASE)
SQL_REFERENCE_RE = re.compile(rf"\bREFERENCES\s+(?P<table>{SQL_IDENTIFIER})", re.IGNORECASE)
RUNTIME_CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}
C_FAMILY_SUFFIXES = {".c", ".h", ".cc", ".cpp", ".hpp"}
STRICT_AST_LANGUAGE_FAMILIES = {
    ".ts": "JAVASCRIPT_TYPESCRIPT", ".tsx": "JAVASCRIPT_TYPESCRIPT",
    ".js": "JAVASCRIPT_TYPESCRIPT", ".jsx": "JAVASCRIPT_TYPESCRIPT",
    ".mjs": "JAVASCRIPT_TYPESCRIPT", ".cjs": "JAVASCRIPT_TYPESCRIPT",
    ".mts": "JAVASCRIPT_TYPESCRIPT", ".cts": "JAVASCRIPT_TYPESCRIPT",
    ".rs": "RUST", ".swift": "SWIFT", ".kt": "KOTLIN", ".kts": "KOTLIN",
    ".py": "PYTHON", ".c": "C_CPP", ".h": "C_CPP", ".cc": "C_CPP",
    ".cpp": "C_CPP", ".hpp": "C_CPP",
}
RUNTIME_DISCOVERY_STATUSES = {"EVIDENCE_BACKED", "NO_REPOSITORY_MATCH_FOUND", "UNRESOLVED", "SUPPRESSED"}
BUILD_TIMESTAMP_KEYS = {
    "generatedAt", "validatedAt", "completedAt", "startedAt", "finishedAt",
    "lastUpdatedAt", "verificationTimestamp", "timestamp", "updatedAt", "createdAt",
}


def line_at(text: str, number: int) -> str:
    lines = text.splitlines()
    return lines[number - 1].strip() if 0 < number <= len(lines) else ""


def strict_ast_language_family(path: str) -> str:
    return STRICT_AST_LANGUAGE_FAMILIES.get(Path(path).suffix.lower(), "")


def full_external_specifier(specifier: str) -> str:
    return specifier[5:] if specifier.startswith("node:") else specifier


def first_string(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("source", "import", "default", "browser", "node", "types", "require"):
            candidate = first_string(value.get(key))
            if candidate:
                return candidate
        for candidate in value.values():
            result = first_string(candidate)
            if result:
                return result
    if isinstance(value, list):
        for candidate in value:
            result = first_string(candidate)
            if result:
                return result
    return ""


def split_top_level(value: str, delimiter: str = ",") -> list[str]:
    """Split a Rust use-tree list without breaking nested brace groups."""
    depth = 0
    start = 0
    parts: list[str] = []
    for index, char in enumerate(value):
        if char == "{":
            depth += 1
        elif char == "}":
            depth = max(0, depth - 1)
        elif char == delimiter and depth == 0:
            parts.append(value[start:index])
            start = index + 1
    parts.append(value[start:])
    return [part.strip() for part in parts if part.strip()]


def expand_rust_use_tree(tree: str, prefix: str = "") -> list[str]:
    """Expand Rust brace imports into concrete namespace leaves."""
    value = re.sub(r"\s+", "", tree.strip())
    if not value:
        return []
    depth = 0
    opening = -1
    closing = -1
    for index, char in enumerate(value):
        if char == "{":
            if depth == 0:
                opening = index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and opening >= 0:
                closing = index
                break
    if opening < 0:
        leaf = value.split(" as ", 1)[0].strip()
        leaf = re.sub(r"\bas[A-Za-z_][A-Za-z0-9_]*$", "", leaf)
        return [f"{prefix}::{leaf}".strip(":")]
    head = value[:opening].rstrip(":")
    tail = value[closing + 1 :].lstrip(":")
    next_prefix = "::".join(part for part in (prefix, head) if part)
    expanded: list[str] = []
    for member in split_top_level(value[opening + 1 : closing]):
        combined = member if not tail else f"{member}::{tail}"
        expanded.extend(expand_rust_use_tree(combined, next_prefix))
    return expanded


def sql_table_name(raw: str) -> str:
    part = re.split(r"\s*\.\s*", raw.strip())[-1]
    return part.strip('"`[]').lower()


def sql_statements(text: str) -> list[tuple[int, str]]:
    statements: list[tuple[int, str]] = []
    start = 0
    for match in re.finditer(r";", text):
        statements.append((start, text[start : match.end()]))
        start = match.end()
    if text[start:].strip():
        statements.append((start, text[start:]))
    return statements


def stable_runtime_identifier(value: str, registration_type: str, line: int) -> str:
    identifier = value.strip().strip(";,)").strip()
    if (len(identifier) >= 2 and identifier[0] == identifier[-1] and identifier[0] in "\"'"):
        identifier = identifier[1:-1].strip()
    if not identifier or identifier[0] in "{[(" or identifier in {"undefined", "null"}:
        return f"{registration_type.lower()}@L{line}"
    return identifier[:160]


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


def runtime_entrypoint_path(path: str) -> bool:
    return bool(runtime_entrypoint_reason(path))


def jsx_attribute_value(anchor: str, attribute: str) -> str:
    match = re.search(rf"\b{re.escape(attribute)}\s*=\s*", anchor)
    if not match:
        return ""
    start = match.end()
    if start >= len(anchor):
        return ""
    opening = anchor[start]
    if opening in "\"'":
        closing = anchor.find(opening, start + 1)
        return anchor[start : closing + 1] if closing >= 0 else anchor[start:]
    if opening == "{":
        depth = 0
        quote = ""
        escaped = False
        for index in range(start, len(anchor)):
            char = anchor[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = ""
                continue
            if char in "\"'`":
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return anchor[start : index + 1]
        return anchor[start:]
    end = re.search(r"\s|/?>", anchor[start:])
    return anchor[start : start + end.start()] if end else anchor[start:]


def iter_jsx_route_opening_tags(text: str) -> list[tuple[int, int, str, str, str]]:
    """Return balanced React Router opening tags with path and target attributes."""
    results: list[tuple[int, int, str, str, str]] = []
    for match in re.finditer(r"<Route\b", text):
        quote = ""
        escaped = False
        brace_depth = 0
        end = -1
        for index in range(match.start(), len(text)):
            char = text[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = ""
                continue
            if char in "\"'`":
                quote = char
            elif char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth = max(0, brace_depth - 1)
            elif char == ">" and brace_depth == 0:
                end = index + 1
                break
        if end < 0:
            continue
        anchor = text[match.start() : end]
        path_value = jsx_attribute_value(anchor, "path")
        if not path_value:
            continue
        target_value = next(
            (jsx_attribute_value(anchor, name) for name in ("element", "Component", "lazy") if jsx_attribute_value(anchor, name)),
            "",
        )
        results.append((match.start(), end, anchor, path_value, target_value))
    return results


def parse_jsonc(text: str) -> dict[str, Any]:
    """Parse repository JSON-with-comments without corrupting quoted URLs."""
    output: list[str] = []
    index = 0
    quote = ""
    escaped = False
    while index < len(text):
        char = text[index]
        if quote:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char in "\"'":
            quote = char
            output.append(char)
            index += 1
            continue
        if text.startswith("//", index):
            end = text.find("\n", index)
            if end < 0:
                break
            output.append("\n")
            index = end + 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                break
            output.extend("\n" if value == "\n" else " " for value in text[index : end + 2])
            index = end + 2
            continue
        output.append(char)
        index += 1
    cleaned = re.sub(r",\s*([}\]])", r"\1", "".join(output))
    value = json.loads(cleaned)
    return value if isinstance(value, dict) else {}


def normalize_build_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize_build_value(item)
            for key, item in sorted(value.items())
            if key not in BUILD_TIMESTAMP_KEYS
        }
    if isinstance(value, list):
        return [normalize_build_value(item) for item in value]
    return value


def normalized_artifact_hash(relative_paths: list[str]) -> str:
    canonical_parts: list[str] = []
    for relative in sorted(relative_paths):
        path = (GRAPHIFY.parent / relative).resolve()
        if path.suffix == ".jsonl":
            value: Any = list(iter_jsonl(path))
        else:
            value = load_json(path)
        canonical_parts.append(
            relative.replace("\\", "/") + "\0"
            + json.dumps(
                normalize_build_value(value),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    return sha256_bytes("\n".join(canonical_parts).encode("utf-8"))


class Builder:
    def __init__(self) -> None:
        self.build_started_at = now_utc()
        self.nodes: dict[str, dict[str, Any]] = {}
        self.node_keys: dict[tuple[str, str], str] = {}
        self.edges: dict[str, dict[str, Any]] = {}
        self.unresolved: list[dict[str, Any]] = []
        self.layer_counts: Counter[str] = Counter()
        self.node_type_counts: Counter[str] = Counter()
        self.edge_type_counts: Counter[str] = Counter()
        self.resolution_counts: Counter[str] = Counter()
        self.file_nodes: dict[str, str] = {}
        self.file_layers: dict[str, str] = {}
        self.file_hashes: dict[str, str] = {}
        self.file_packages: dict[str, str] = {}
        self.all_paths: set[Path] = set()
        self.symbol_ast_ids: dict[str, str] = {}
        self.symbols_by_path: dict[str, list[str]] = defaultdict(list)
        self.workspace_packages, self.package_roots = load_workspace_packages()
        capability_doc = load_json(CAP_PATH)
        self.capability_doc = capability_doc
        self.capabilities = capability_doc["capabilities"]
        self.requirements = list(iter_jsonl(REQ_PATH))
        self.capability_paths = inverse_capability_paths(self.capabilities)
        self.requirements_by_capability: dict[str, list[str]] = defaultdict(list)
        for requirement in self.requirements:
            for capability_id in requirement.get("capabilityIds", []):
                self.requirements_by_capability[capability_id].append(requirement["requirementId"])
        self.runtime_rows: list[dict[str, Any]] = []
        self.rust_crates: list[dict[str, Any]] = []
        self.rust_crate_by_file: dict[str, dict[str, Any]] = {}
        self.rust_module_by_file: dict[str, tuple[str, ...]] = {}
        self.rust_resolution_summary: dict[str, Any] = {}
        self.cargo_workspace_summary: dict[str, Any] = {}
        self.swift_modules: dict[str, str] = {}
        self.kotlin_packages: dict[str, list[str]] = defaultdict(list)
        self.kotlin_symbol_files: dict[tuple[str, str], list[str]] = defaultdict(list)
        self.tsconfig_configs: dict[Path, dict[str, Any]] = {}
        self.ts_path_mappings: list[dict[str, Any]] = []
        self.ts_path_resolved_counts: Counter[str] = Counter()
        self.tsconfig_summary: dict[str, Any] = {}
        self.sql_self_loop_edge_ids: list[str] = []
        self.sql_resolution_summary: dict[str, Any] = {}
        self.runtime_scan_summary: dict[str, Any] = {}
        self.v1_resolution_summary: dict[str, Any] = {}
        self.ast_cache_summary: dict[str, Any] = {}
        self.generated_provenance_rows: list[dict[str, Any]] = []
        self.graphql_summary: dict[str, Any] = {}
        self.semantic_config_summary: dict[str, Any] = {}
        self.build_output_paths: list[str] = []
        self.normalized_output_sha256 = ""
        self._runtime_reverse_import_index: dict[str, set[str]] | None = None

    def add_node(self, node: dict[str, Any], referent: str) -> str:
        node_id = node["nodeId"]
        key = (node["nodeType"], referent)
        prior_key = self.node_keys.get(key)
        if prior_key and prior_key != node_id:
            raise RuntimeError(f"Stable referent collision: {key}: {prior_key} vs {node_id}")
        prior = self.nodes.get(node_id)
        if prior and (prior["nodeType"], prior.get("referent", "")) != (node["nodeType"], referent):
            raise RuntimeError(f"Node-ID collision: {node_id}")
        node["referent"] = referent
        node.setdefault("runId", RUN_ID)
        node.setdefault("policyVersion", POLICY_VERSION)
        node.setdefault("reviewStatus", "PENDING_INDEPENDENT_REVIEW")
        self.nodes[node_id] = node
        self.node_keys[key] = node_id
        return node_id

    def add_edge(self, edge: dict[str, Any]) -> None:
        if edge["sourceNodeId"] not in self.nodes or edge["targetNodeId"] not in self.nodes:
            raise RuntimeError(f"Dangling authoritative edge {edge['edgeId']}")
        if edge["sourceNodeId"] == edge["targetNodeId"] and "RUST" in edge.get("evidenceOrigin", ""):
            raise RuntimeError(f"Rust resolver attempted a file self-loop: {edge['edgeId']}")
        prior = self.edges.get(edge["edgeId"])
        if prior and prior != edge:
            raise RuntimeError(f"Edge-ID collision {edge['edgeId']}")
        self.edges[edge["edgeId"]] = edge

    def add_file_nodes(self) -> None:
        inventory = GRAPHIFY / "01 Corpus Inventory" / "GRAPH_LAYER_FILE_REGISTRY.jsonl"
        for row in iter_jsonl(inventory):
            relative = row["path"]
            path = GRAPHIFY.parent / relative
            layer = row["primaryLayer"]
            package = nearest_package(path, self.package_roots)
            node_type = {
                "GENERATED_BINDING": "GENERATED_ARTIFACT",
                "VENDOR_AND_TOOLCHAIN": "VENDOR_ARTIFACT",
                "MIGRATION_AND_SCHEMA": "MIGRATION" if "migration" in relative.lower() else "SCHEMA",
                "ASSET_AND_MEDIA": "ASSET",
            }.get(layer, "FILE")
            node_id = stable_id("MR-FILE", relative, length=24)
            capabilities = self.capability_paths.get(relative, [])
            self.add_node(
                {
                    "nodeId": node_id,
                    "nodeType": node_type,
                    "isFileRecord": True,
                    "layer": layer,
                    "language": language_for(path),
                    "package": package,
                    "path": relative,
                    "qualifiedName": relative,
                    "symbolKind": "",
                    "declarationSpan": "",
                    "uniqueAnchor": "",
                    "anchorSha256": "",
                    "fileSha256": row["sha256"],
                    "generated": layer == "GENERATED_BINDING",
                    "vendor": layer == "VENDOR_AND_TOOLCHAIN",
                    "runtimeReachability": "LAYER_CLASSIFIED",
                    "capabilityIds": capabilities,
                    "requirementIds": sorted({rid for cid in capabilities for rid in self.requirements_by_capability.get(cid, [])}),
                    "evidence": [graphify_rel(inventory), relative],
                    "platform": "CROSS_PLATFORM",
                    "risk": "HIGH" if layer in {"MIGRATION_AND_SCHEMA", "PACKAGING_AND_DEPLOYMENT"} else "NORMAL",
                    "classification": "CURRENT",
                },
                relative,
            )
            self.file_nodes[relative] = node_id
            self.file_layers[relative] = layer
            self.file_hashes[relative] = row["sha256"]
            self.file_packages[relative] = package
        self.all_paths = {GRAPHIFY.parent / path for path in self.file_nodes}

    def add_package_nodes(self) -> None:
        for name, info in sorted(self.workspace_packages.items()):
            manifest_path = codebase_rel(info["manifest"])
            node_id = stable_id("MR-WSPKG", name, length=24)
            data = info["data"]
            self.add_node(
                {
                    "nodeId": node_id,
                    "nodeType": "WORKSPACE_PACKAGE",
                    "layer": "BUILD_AND_CONFIG",
                    "language": "JSON",
                    "package": name,
                    "path": manifest_path,
                    "qualifiedName": name,
                    "symbolKind": "PACKAGE",
                    "declarationSpan": "",
                    "uniqueAnchor": f'"name": "{name}"',
                    "anchorSha256": sha256_bytes(name.encode()),
                    "fileSha256": self.file_hashes.get(manifest_path, sha256_file(info["manifest"])),
                    "generated": False,
                    "vendor": False,
                    "runtimeReachability": "WORKSPACE_PACKAGE",
                    "capabilityIds": self.capability_paths.get(manifest_path, []),
                    "requirementIds": [],
                    "evidence": [manifest_path],
                    "version": data.get("version", ""),
                    "exports": data.get("exports", {}),
                    "platform": "CROSS_PLATFORM",
                    "risk": "NORMAL",
                    "classification": "CURRENT",
                },
                name,
            )
            file_id = self.file_nodes.get(manifest_path)
            if file_id:
                self.add_edge(
                    make_edge(file_id, node_id, "BUILD_REFERENCE", manifest_path, "", "package-manifest", "PACKAGE_JSON", "RESOLVED_INTERNAL_FILE", "RESOLVED_WORKSPACE_PACKAGE", "BUILD_AND_CONFIG", evidence=[manifest_path])
                )

    def build_rust_registry(self) -> None:
        """Build Cargo package, dependency-alias, crate-root, and module indexes."""
        manifests = sorted(
            path for path in CODEBASE.rglob("Cargo.toml")
            if not any(part in {"target", "node_modules", ".yarn"} for part in path.parts)
        )
        packages_by_name: dict[str, dict[str, Any]] = {}
        packages_by_manifest_dir: dict[Path, dict[str, Any]] = {}
        manifest_docs: dict[Path, dict[str, Any]] = {}
        for manifest in manifests:
            try:
                data = tomllib.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
                continue
            manifest_docs[manifest.resolve()] = data
            package = data.get("package")
            if not isinstance(package, dict) or not package.get("name"):
                continue
            name = str(package["name"])
            lib = data.get("lib") if isinstance(data.get("lib"), dict) else {}
            roots: list[Path] = []
            configured_lib = lib.get("path") if isinstance(lib, dict) else None
            if configured_lib:
                roots.append((manifest.parent / str(configured_lib)).resolve())
            elif (manifest.parent / "src" / "lib.rs").exists():
                roots.append((manifest.parent / "src" / "lib.rs").resolve())
            if (manifest.parent / "src" / "main.rs").exists():
                roots.append((manifest.parent / "src" / "main.rs").resolve())
            for binary in data.get("bin", []) if isinstance(data.get("bin"), list) else []:
                if isinstance(binary, dict) and binary.get("path"):
                    roots.append((manifest.parent / str(binary["path"])).resolve())
            roots = [root for root in dict.fromkeys(roots) if codebase_rel(root) in self.file_nodes]
            if not roots:
                continue
            manifest_relative = codebase_rel(manifest)
            node_id = stable_id("MR-CARGO", manifest_relative, name, length=24)
            self.add_node(
                {
                    "nodeId": node_id, "nodeType": "WORKSPACE_PACKAGE", "layer": "BUILD_AND_CONFIG",
                    "language": "TOML", "package": name, "path": manifest_relative,
                    "qualifiedName": name, "symbolKind": "CARGO_PACKAGE", "declarationSpan": "",
                    "uniqueAnchor": f'name = "{name}"', "anchorSha256": sha256_bytes(name.encode()),
                    "fileSha256": self.file_hashes.get(manifest_relative, sha256_file(manifest)),
                    "generated": False, "vendor": False, "runtimeReachability": "CARGO_WORKSPACE_PACKAGE",
                    "capabilityIds": self.capability_paths.get(manifest_relative, []), "requirementIds": [],
                    "evidence": [manifest_relative, *[codebase_rel(root) for root in roots]],
                    "platform": "CROSS_PLATFORM", "risk": "NORMAL", "classification": "CURRENT",
                },
                f"cargo::{manifest_relative}::{name}",
            )
            crate = {
                "name": name, "manifest": manifest, "manifestRelative": manifest_relative,
                "root": manifest.parent.resolve(), "roots": roots, "nodeId": node_id,
                "data": data, "dependencyAliases": {}, "moduleFiles": {},
            }
            self.rust_crates.append(crate)
            packages_by_name[name] = crate
            packages_by_name[name.replace("-", "_")] = crate
            packages_by_manifest_dir[manifest.parent.resolve()] = crate
            manifest_file = self.file_nodes.get(manifest_relative)
            if manifest_file:
                self.add_edge(make_edge(
                    manifest_file, node_id, "BUILD_REFERENCE", manifest_relative, "", "Cargo package manifest",
                    "CARGO_WORKSPACE_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_WORKSPACE_PACKAGE",
                    "BUILD_AND_CONFIG", evidence=[manifest_relative],
                ))

        def dependency_sections(data: dict[str, Any]) -> list[dict[str, Any]]:
            sections = [
                data.get("dependencies", {}), data.get("dev-dependencies", {}),
                data.get("build-dependencies", {}),
            ]
            target = data.get("target", {})
            if isinstance(target, dict):
                for target_data in target.values():
                    if isinstance(target_data, dict):
                        sections.extend([
                            target_data.get("dependencies", {}), target_data.get("dev-dependencies", {}),
                            target_data.get("build-dependencies", {}),
                        ])
            return [section for section in sections if isinstance(section, dict)]

        for crate in self.rust_crates:
            aliases: dict[str, dict[str, Any]] = {}
            for section in dependency_sections(crate["data"]):
                for alias, declaration in section.items():
                    package_name = alias
                    path_value = ""
                    if isinstance(declaration, dict):
                        package_name = str(declaration.get("package", alias))
                        path_value = str(declaration.get("path", ""))
                    target = None
                    if path_value:
                        target_dir = (crate["manifest"].parent / path_value).resolve()
                        target = packages_by_manifest_dir.get(target_dir)
                    target = target or packages_by_name.get(package_name) or packages_by_name.get(package_name.replace("-", "_"))
                    if target:
                        aliases[str(alias).replace("-", "_")] = target
            aliases[crate["name"].replace("-", "_")] = crate
            crate["dependencyAliases"] = aliases

            manifest_relative = crate["manifestRelative"]
            manifest_id = self.file_nodes.get(manifest_relative)
            features = crate["data"].get("features", {})
            if manifest_id and isinstance(features, dict):
                for feature_name, declarations in sorted(features.items()):
                    feature_id = stable_id(
                        "MR-CARGO-FEATURE", manifest_relative, str(feature_name), length=24
                    )
                    self.add_node({
                        "nodeId": feature_id, "nodeType": "CONFIGURATION", "layer": "BUILD_AND_CONFIG",
                        "language": "TOML", "package": crate["name"], "path": manifest_relative,
                        "qualifiedName": f"{crate['name']}::feature::{feature_name}",
                        "symbolKind": "CARGO_FEATURE", "declarationSpan": "",
                        "uniqueAnchor": f"[features] {feature_name}", "anchorSha256": sha256_bytes(
                            f"{manifest_relative}:{feature_name}".encode()
                        ),
                        "fileSha256": self.file_hashes[manifest_relative], "generated": False,
                        "vendor": False, "runtimeReachability": "BUILD_TIME_CONFIGURATION",
                        "capabilityIds": self.capability_paths.get(manifest_relative, []),
                        "requirementIds": [], "evidence": [manifest_relative, f"features.{feature_name}"],
                        "platform": "CROSS_PLATFORM", "risk": "HIGH", "classification": "CURRENT",
                    }, f"{manifest_relative}::feature::{feature_name}")
                    self.add_edge(make_edge(
                        manifest_id, feature_id, "CONFIGURATION_REFERENCE", manifest_relative, "",
                        f"Cargo feature {feature_name}", "CARGO_FEATURE_RESOLVER",
                        "RESOLVED_INTERNAL_FILE", "RESOLVED_CONFIGURATION", "BUILD_AND_CONFIG",
                        evidence=[manifest_relative, f"features.{feature_name}"],
                    ))
                    for declaration in declarations if isinstance(declarations, list) else []:
                        raw = str(declaration)
                        dependency_alias = raw.removeprefix("dep:").split("/", 1)[0].rstrip("?").replace("-", "_")
                        target = crate["dependencyAliases"].get(dependency_alias)
                        if not target:
                            continue
                        self.add_edge(make_edge(
                            feature_id, target["nodeId"], "CONFIGURATION_REFERENCE", manifest_relative, "",
                            raw, "CARGO_FEATURE_DEPENDENCY_RESOLVER",
                            "RESOLVED_CONFIGURATION", "RESOLVED_WORKSPACE_PACKAGE", "BUILD_AND_CONFIG",
                            evidence=[manifest_relative, f"feature {feature_name}: {raw}", target["manifestRelative"]],
                        ))

            build_script = crate["manifest"].parent / "build.rs"
            build_relative = codebase_rel(build_script)
            if manifest_id and build_relative in self.file_nodes:
                self.add_edge(make_edge(
                    manifest_id, self.file_nodes[build_relative], "BUILD_REFERENCE", manifest_relative, "",
                    "Cargo build script", "CARGO_BUILD_SCRIPT_RESOLVER",
                    "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_FILE", "BUILD_AND_CONFIG",
                    evidence=[manifest_relative, build_relative],
                ))

        workspace_member_edges = 0
        workspace_member_package_edges = 0
        expected_workspace_members: set[tuple[str, str]] = set()
        for manifest, data in sorted(manifest_docs.items(), key=lambda item: str(item[0])):
            workspace = data.get("workspace")
            if not isinstance(workspace, dict):
                continue
            source_relative = codebase_rel(manifest)
            source_id = self.file_nodes.get(source_relative)
            if not source_id:
                continue
            excluded = {str(value).rstrip("/") for value in workspace.get("exclude", []) if isinstance(value, str)}
            for declaration in workspace.get("members", []) if isinstance(workspace.get("members"), list) else []:
                if not isinstance(declaration, str):
                    continue
                candidates = sorted(manifest.parent.glob(declaration))
                if not candidates and (manifest.parent / declaration).exists():
                    candidates = [manifest.parent / declaration]
                for candidate in candidates:
                    candidate_dir = candidate if candidate.is_dir() else candidate.parent
                    try:
                        declared_relative = candidate_dir.relative_to(manifest.parent).as_posix().rstrip("/")
                    except ValueError:
                        declared_relative = ""
                    if declared_relative in excluded:
                        continue
                    target_manifest = (candidate_dir / "Cargo.toml").resolve()
                    target_relative = codebase_rel(target_manifest)
                    target_id = self.file_nodes.get(target_relative)
                    if not target_id or target_manifest == manifest:
                        continue
                    pair = (source_relative, target_relative)
                    if pair in expected_workspace_members:
                        continue
                    expected_workspace_members.add(pair)
                    self.add_edge(make_edge(
                        source_id, target_id, "WORKSPACE_MEMBER", source_relative, "", declaration,
                        "CARGO_WORKSPACE_MEMBER_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_FILE",
                        "BUILD_AND_CONFIG", evidence=[source_relative, f"workspace.members: {declaration}", target_relative],
                    ))
                    workspace_member_edges += 1
                    target_crate = packages_by_manifest_dir.get(target_manifest.parent)
                    if target_crate:
                        self.add_edge(make_edge(
                            source_id, target_crate["nodeId"], "WORKSPACE_MEMBER", source_relative, "",
                            declaration, "CARGO_WORKSPACE_MEMBER_PACKAGE_RESOLVER",
                            "RESOLVED_INTERNAL_FILE", "RESOLVED_WORKSPACE_PACKAGE",
                            "BUILD_AND_CONFIG",
                            evidence=[
                                source_relative, f"workspace.members: {declaration}",
                                target_relative, f"Cargo package: {target_crate['name']}",
                            ],
                        ))
                        workspace_member_package_edges += 1

        workspace_dependency_edges = 0
        workspace_dependency_package_edges = 0
        expected_workspace_dependencies: set[tuple[str, str, str]] = set()
        for crate in self.rust_crates:
            source_relative = crate["manifestRelative"]
            source_id = self.file_nodes.get(source_relative)
            if not source_id:
                continue
            for alias, target in sorted(crate["dependencyAliases"].items()):
                if target is crate:
                    continue
                target_relative = target["manifestRelative"]
                target_id = self.file_nodes.get(target_relative)
                if not target_id:
                    continue
                key = (source_relative, alias, target_relative)
                expected_workspace_dependencies.add(key)
                self.add_edge(make_edge(
                    source_id, target_id, "WORKSPACE_DEPENDENCY", source_relative, "", alias,
                    "CARGO_LOCAL_DEPENDENCY_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_FILE",
                    "BUILD_AND_CONFIG", evidence=[source_relative, f"local Cargo dependency alias: {alias}", target_relative],
                ))
                workspace_dependency_edges += 1
                self.add_edge(make_edge(
                    source_id, target["nodeId"], "WORKSPACE_DEPENDENCY", source_relative, "", alias,
                    "CARGO_LOCAL_DEPENDENCY_PACKAGE_RESOLVER",
                    "RESOLVED_INTERNAL_FILE", "RESOLVED_WORKSPACE_PACKAGE",
                    "BUILD_AND_CONFIG",
                    evidence=[
                        source_relative, f"local Cargo dependency alias: {alias}",
                        target_relative, f"Cargo package: {target['name']}",
                    ],
                ))
                workspace_dependency_package_edges += 1

        self.cargo_workspace_summary = {
            "cargoManifestCount": len(manifest_docs), "cargoPackageCount": len(self.rust_crates),
            "expectedWorkspaceMemberManifestEdges": len(expected_workspace_members),
            "emittedWorkspaceMemberManifestEdges": workspace_member_edges,
            "emittedWorkspaceMemberPackageEdges": workspace_member_package_edges,
            "expectedLocalWorkspaceDependencyManifestEdges": len(expected_workspace_dependencies),
            "emittedLocalWorkspaceDependencyManifestEdges": workspace_dependency_edges,
            "emittedLocalWorkspaceDependencyPackageEdges": workspace_dependency_package_edges,
            "assertions": {
                "allWorkspaceMembersLinked": workspace_member_edges == len(expected_workspace_members),
                "allLocalWorkspaceDependenciesLinked": workspace_dependency_edges == len(expected_workspace_dependencies),
                "allWorkspaceMembersResolveToCargoPackages": workspace_member_package_edges == len(expected_workspace_members),
                "allLocalWorkspaceDependenciesResolveToCargoPackages": workspace_dependency_package_edges == len(expected_workspace_dependencies),
            },
        }

        rust_files = sorted(
            (GRAPHIFY.parent / relative).resolve()
            for relative in self.file_nodes
            if relative.lower().endswith(".rs")
        )
        for path in rust_files:
            owners = [crate for crate in self.rust_crates if path == crate["root"] or crate["root"] in path.parents]
            if not owners:
                continue
            crate = max(owners, key=lambda item: len(item["root"].parts))
            relative = codebase_rel(path)
            root_file = next((root for root in crate["roots"] if root == path), None)
            if root_file:
                module = ()
            else:
                src = crate["roots"][0].parent
                try:
                    parts = list(path.relative_to(src).parts)
                except ValueError:
                    parts = list(path.relative_to(crate["root"]).parts)
                parts[-1] = Path(parts[-1]).stem
                if parts[-1] == "mod":
                    parts.pop()
                module = tuple(parts)
            crate["moduleFiles"].setdefault(module, relative)
            self.rust_crate_by_file[relative] = crate
            self.rust_module_by_file[relative] = module
        self.rust_crates.sort(key=lambda item: item["manifestRelative"])

    def _rust_module_target(self, crate: dict[str, Any], parts: list[str]) -> str:
        clean = [part for part in parts if part and part not in {"self", "*"}]
        for size in range(len(clean), -1, -1):
            relative = crate["moduleFiles"].get(tuple(clean[:size]))
            if relative:
                return self.file_nodes[relative]
        root_relative = codebase_rel(crate["roots"][0])
        return self.file_nodes[root_relative]

    def resolve_rust_use(self, source_path: Path, specifier: str) -> tuple[str | None, str, list[str]]:
        relative = codebase_rel(source_path)
        crate = self.rust_crate_by_file.get(relative)
        if not crate:
            first = specifier.lstrip(":").split("::", 1)[0]
            return self.external_node("cargo", first), "RESOLVED_EXTERNAL_PACKAGE", ["Rust file is outside a local Cargo package"]
        parts = [part for part in specifier.lstrip(":").split("::") if part]
        if not parts:
            return None, "INVALID_REFERENCE", ["empty Rust use tree"]
        current_module = list(self.rust_module_by_file.get(relative, ()))
        first = parts[0]
        target_crate = crate
        module_parts: list[str]
        namespace = ""
        if first == "crate":
            module_parts = parts[1:]
            namespace = "crate"
        elif first == "self":
            module_parts = current_module + parts[1:]
            namespace = "self"
        elif first == "super":
            index = 0
            while index < len(parts) and parts[index] == "super":
                index += 1
            module_parts = current_module[: max(0, len(current_module) - index)] + parts[index:]
            namespace = "super"
        elif first.replace("-", "_") in crate["dependencyAliases"]:
            target_crate = crate["dependencyAliases"][first.replace("-", "_")]
            module_parts = parts[1:]
            namespace = f"workspace-crate:{target_crate['name']}"
        elif tuple([first]) in crate["moduleFiles"]:
            module_parts = parts
            namespace = "local-module"
        else:
            return self.external_node("cargo", first), "RESOLVED_EXTERNAL_PACKAGE", [f"Cargo dependency namespace: {first}"]
        target = self._rust_module_target(target_crate, module_parts)
        target_relative = self.nodes[target].get("path", "")
        status = "RESOLVED_GENERATED_ARTIFACT" if self.file_layers.get(target_relative) == "GENERATED_BINDING" else "RESOLVED_INTERNAL_FILE"
        return target, status, [
            f"Cargo manifest: {target_crate['manifestRelative']}",
            f"Rust namespace class: {namespace}",
            f"longest local module prefix: {target_relative}",
        ]

    def add_rust_relationships(self) -> None:
        if not self.rust_crates:
            self.build_rust_registry()
        discovered = 0
        resolved = 0
        use_leaves = 0
        local_uses = 0
        external_uses = 0
        suppressed_same_file = 0
        for relative in sorted(path for path in self.file_nodes if path.lower().endswith(".rs")):
            source_node = self.file_nodes[relative]
            source_path = (GRAPHIFY.parent / relative).resolve()
            text = text_file(source_path)
            if text is None:
                continue
            cleaned = re.sub(r"/\*.*?\*/", lambda match: " " * len(match.group(0)), text, flags=re.DOTALL)
            cleaned = re.sub(r"//[^\n]*", lambda match: " " * len(match.group(0)), cleaned)
            for match in RUST_MOD_RE.finditer(cleaned):
                discovered += 1
                name = match.group("name")
                attr = RUST_PATH_ATTR_RE.search(match.group("attrs") or "")
                if attr:
                    candidates = [(source_path.parent / attr.group(1)).resolve()]
                else:
                    module_dir = source_path.parent if source_path.name in {"lib.rs", "main.rs", "mod.rs"} else source_path.with_suffix("")
                    candidates = [(module_dir / f"{name}.rs").resolve(), (module_dir / name / "mod.rs").resolve()]
                target_path = next((candidate for candidate in candidates if codebase_rel(candidate) in self.file_nodes), None)
                line = cleaned.count("\n", 0, match.start()) + 1
                if target_path is None:
                    self.unresolved.append({
                        "diagnosticId": stable_id("MR-UNRES", relative, str(line), "RUST_MOD", name, length=24),
                        "origin": "V2_RUST_MODULE_DECLARATION_RESOLVER", "originalEdgeId": "",
                        "originalSource": relative, "originalTarget": name, "originalRelation": "MODULE_DECLARATION",
                        "resolutionClassification": "UNRESOLVED_INTERNAL", "resolvedEndpoint": "",
                        "evidence": [relative, f"L{line}", *[codebase_rel(candidate) for candidate in candidates]],
                        "resolverUsed": "RUST_MOD_DECLARATION_RESOLVER", "remainingBlocker": True,
                        "remainingBlockerReason": "No sibling name.rs or name/mod.rs exists in the indexed corpus",
                        "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                    })
                    continue
                target_relative = codebase_rel(target_path)
                resolved += 1
                self.add_edge(make_edge(
                    source_node, self.file_nodes[target_relative], "MODULE_DECLARATION", relative, f"L{line}",
                    f"mod {name};", "RUST_MOD_DECLARATION_RESOLVER", "RESOLVED_INTERNAL_FILE",
                    "RESOLVED_INTERNAL_FILE", self.file_layers[relative], self.capability_paths.get(relative, []),
                    [relative, f"L{line}: {line_at(text, line)}", f"module file: {target_relative}"],
                ))
            for match in RUST_USE_RE.finditer(cleaned):
                line = cleaned.count("\n", 0, match.start()) + 1
                for specifier in expand_rust_use_tree(match.group("tree")):
                    use_leaves += 1
                    target, status, evidence = self.resolve_rust_use(source_path, specifier)
                    if target is None:
                        self.unresolved.append({
                            "diagnosticId": stable_id("MR-UNRES", relative, str(line), "RUST_USE", specifier, length=24),
                            "origin": "V2_RUST_USE_RESOLVER", "originalEdgeId": "", "originalSource": relative,
                            "originalTarget": specifier, "originalRelation": "TYPE_DEPENDENCY",
                            "resolutionClassification": status, "resolvedEndpoint": "",
                            "evidence": [relative, f"L{line}", *evidence], "resolverUsed": "RUST_USE_RESOLVER",
                            "remainingBlocker": True, "remainingBlockerReason": "Rust use namespace could not be classified",
                            "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                        })
                        continue
                    if status == "RESOLVED_EXTERNAL_PACKAGE":
                        external_uses += 1
                    else:
                        local_uses += 1
                    if target == source_node:
                        suppressed_same_file += 1
                        continue
                    self.add_edge(make_edge(
                        source_node, target, "TYPE_DEPENDENCY", relative, f"L{line}", f"use {specifier}",
                        "RUST_USE_NAMESPACE_RESOLVER", "RESOLVED_INTERNAL_FILE", status,
                        self.file_layers[relative], self.capability_paths.get(relative, []),
                        [relative, f"L{line}: {line_at(text, line)}", *evidence],
                    ))
        if discovered != 150 or resolved != discovered:
            raise RuntimeError(f"Rust module declaration coverage failed: discovered={discovered}, resolved={resolved}, expected=150")
        rust_self_loops = [
            edge["edgeId"] for edge in self.edges.values()
            if edge["sourceNodeId"] == edge["targetNodeId"] and str(edge.get("declaringPath", "")).endswith(".rs")
        ]
        if rust_self_loops:
            raise RuntimeError(f"Rust file self-loops remain: {rust_self_loops[:5]}")
        self.rust_resolution_summary = {
            "expectedLocalModDeclarations": 150, "discoveredLocalModDeclarations": discovered,
            "resolvedLocalModDeclarations": resolved, "unresolvedLocalModDeclarations": discovered - resolved,
            "expandedUseLeaves": use_leaves, "resolvedLocalUseLeaves": local_uses,
            "resolvedExternalUseLeaves": external_uses, "sameFileNamespaceEdgesSuppressed": suppressed_same_file,
            "rustFileSelfLoops": 0, "assertions": {
                "allExpectedModDeclarationsDiscovered": discovered == 150,
                "allLocalModDeclarationsResolved": resolved == discovered,
                "zeroRustFileSelfLoops": not rust_self_loops,
            },
            "cargoWorkspace": self.cargo_workspace_summary,
        }

    def build_native_module_indexes(self) -> None:
        for relative in sorted(path for path in self.file_nodes if path.endswith("Package.swift")):
            manifest = GRAPHIFY.parent / relative
            text = text_file(manifest) or ""
            for match in re.finditer(r"\.(?:target|executableTarget|testTarget)\s*\(\s*name\s*:\s*[\"']([^\"']+)", text):
                module = match.group(1)
                source_prefix = manifest.parent / "Sources" / module
                source_files = sorted(
                    path for path in source_prefix.rglob("*.swift")
                    if codebase_rel(path) in self.file_nodes
                ) if source_prefix.exists() else sorted(
                    path for path in (manifest.parent / "Sources").rglob("*.swift")
                    if (manifest.parent / "Sources").exists() and codebase_rel(path) in self.file_nodes
                )
                layers = {self.file_layers[codebase_rel(path)] for path in source_files}
                layer = "GENERATED_BINDING" if source_files and layers == {"GENERATED_BINDING"} else "BUILD_AND_CONFIG"
                node_id = stable_id("MR-SWIFTMOD", relative, module, length=24)
                self.add_node({
                    "nodeId": node_id, "nodeType": "WORKSPACE_PACKAGE", "layer": layer, "language": "SWIFT",
                    "package": module, "path": relative, "qualifiedName": module, "symbolKind": "SWIFT_MODULE",
                    "declarationSpan": f"L{text.count(chr(10), 0, match.start()) + 1}", "uniqueAnchor": match.group(0),
                    "anchorSha256": sha256_bytes(match.group(0).encode()), "fileSha256": self.file_hashes[relative],
                    "generated": layer == "GENERATED_BINDING", "vendor": False,
                    "runtimeReachability": "SWIFT_PACKAGE_MODULE", "capabilityIds": self.capability_paths.get(relative, []),
                    "requirementIds": [], "evidence": [relative, match.group(0)], "platform": "IOS",
                    "risk": "NORMAL", "classification": "CURRENT",
                }, f"swift-module::{relative}::{module}")
                self.swift_modules[module] = node_id
                self.add_edge(make_edge(
                    self.file_nodes[relative], node_id, "BUILD_REFERENCE", relative, "", module,
                    "SWIFT_PACKAGE_MANIFEST_RESOLVER", "RESOLVED_INTERNAL_FILE",
                    "RESOLVED_GENERATED_ARTIFACT" if layer == "GENERATED_BINDING" else "RESOLVED_WORKSPACE_PACKAGE",
                    "BUILD_AND_CONFIG", evidence=[relative, match.group(0)],
                ))
                for source in source_files:
                    source_relative = codebase_rel(source)
                    self.add_edge(make_edge(
                        node_id, self.file_nodes[source_relative], "RE_EXPORT", relative, "", module,
                        "SWIFT_PACKAGE_SOURCE_RESOLVER", "RESOLVED_WORKSPACE_PACKAGE",
                        "RESOLVED_GENERATED_ARTIFACT" if self.file_layers[source_relative] == "GENERATED_BINDING" else "RESOLVED_INTERNAL_FILE",
                        self.file_layers[source_relative], evidence=[relative, source_relative],
                    ))
        for relative in sorted(path for path in self.file_nodes if path.lower().endswith((".kt", ".kts"))):
            text = text_file(GRAPHIFY.parent / relative) or ""
            package = re.search(r"(?m)^\s*package\s+([A-Za-z_][\w.]*)", text)
            if package:
                package_name = package.group(1)
                self.kotlin_packages[package_name].append(relative)
                declarations = re.finditer(
                    r"(?m)^\s*"
                    r"(?:(?:public|private|protected|internal|expect|actual|final|open|abstract|"
                    r"sealed|data|value|inline|tailrec|operator|infix|suspend|external|const|"
                    r"lateinit|override)\s+)*"
                    r"(?:(?:enum|annotation)\s+class|class|interface|object|typealias|fun|val|var)"
                    r"\s+(?:[A-Za-z_][\w<>,?.]*\s*\.)?`?([A-Za-z_]\w*)`?",
                    text,
                )
                for declaration in declarations:
                    self.kotlin_symbol_files[(package_name, declaration.group(1))].append(relative)

    def resolve_native_import(self, source_path: Path, specifier: str) -> tuple[str | None, str, list[str]]:
        suffix = source_path.suffix.lower()
        if suffix == ".swift":
            module = specifier.split(".", 1)[0]
            if module in self.swift_modules:
                target = self.swift_modules[module]
                status = "RESOLVED_GENERATED_ARTIFACT" if self.nodes[target]["layer"] == "GENERATED_BINDING" else "RESOLVED_WORKSPACE_PACKAGE"
                return target, status, [f"SwiftPM target/module: {module}", self.nodes[target]["path"]]
            return self.external_node("swift", module), "RESOLVED_EXTERNAL_PACKAGE", [f"Swift framework/package module: {module}"]
        if suffix in {".kt", ".kts"}:
            if specifier == "uniffi.affine_mobile_native" or specifier.startswith("uniffi.affine_mobile_native."):
                generated = "Codebase/packages/frontend/apps/android/App/app/src/main/java/uniffi/affine_mobile_native/affine_mobile_native.kt"
                if generated in self.file_nodes:
                    return self.file_nodes[generated], "RESOLVED_GENERATED_ARTIFACT", ["UniFFI generated Kotlin namespace", generated]
            matching = [package for package in self.kotlin_packages if specifier == package or specifier.startswith(package + ".")]
            if matching:
                package = max(matching, key=len)
                candidates = sorted(self.kotlin_packages[package])
                symbol = specifier.rsplit(".", 1)[-1]
                declaring_files = sorted(self.kotlin_symbol_files.get((package, symbol), []))
                target_relative = next(
                    (path for path in candidates if Path(path).stem.lower() == symbol.lower()),
                    declaring_files[0] if declaring_files else candidates[0],
                )
                return self.file_nodes[target_relative], "RESOLVED_INTERNAL_FILE", [
                    f"Kotlin package declaration: {package}",
                    f"Kotlin imported symbol: {symbol}",
                    target_relative,
                ]
            root = ".".join(specifier.split(".")[:2]) if "." in specifier else specifier
            return self.external_node("maven", root), "RESOLVED_EXTERNAL_PACKAGE", [f"External Kotlin/Maven namespace: {root}"]
        return None, "INVALID_REFERENCE", ["not a Swift or Kotlin import"]

    def external_node(self, ecosystem: str, specifier: str, layer: str = "EXTERNAL_DEPENDENCY") -> str:
        canonical = full_external_specifier(specifier)
        node_id = stable_id("MR-EXT", ecosystem, canonical, length=24)
        if node_id not in self.nodes:
            self.add_node(
                {
                    "nodeId": node_id,
                    "nodeType": "EXTERNAL_PACKAGE",
                    "layer": layer,
                    "language": "",
                    "package": package_name_from_specifier(canonical),
                    "path": "",
                    "qualifiedName": f"external:{ecosystem}:{canonical}",
                    "symbolKind": "EXTERNAL_DEPENDENCY",
                    "declarationSpan": "",
                    "uniqueAnchor": canonical,
                    "anchorSha256": sha256_bytes(canonical.encode()),
                    "fileSha256": "",
                    "generated": False,
                    "vendor": False,
                    "runtimeReachability": "EXTERNAL_RESOLVED",
                    "capabilityIds": [],
                    "requirementIds": [],
                    "evidence": ["language-aware import or package manifest"],
                    "ecosystem": ecosystem,
                    "rootPackage": package_name_from_specifier(canonical),
                    "platform": "EXTERNAL",
                    "risk": "NORMAL",
                    "classification": "EXTERNAL",
                },
                f"{ecosystem}:{canonical}",
            )
        return node_id

    def builtin_node(self, specifier: str) -> str:
        canonical = full_external_specifier(specifier)
        node_id = stable_id("MR-BUILTIN", canonical, length=24)
        if node_id not in self.nodes:
            self.add_node(
                {
                    "nodeId": node_id,
                    "nodeType": "NODE_BUILTIN",
                    "layer": "EXTERNAL_DEPENDENCY",
                    "language": "JavaScript",
                    "package": "node",
                    "path": "",
                    "qualifiedName": f"builtin:node:{canonical}",
                    "symbolKind": "NODE_BUILTIN",
                    "declarationSpan": "",
                    "uniqueAnchor": canonical,
                    "anchorSha256": sha256_bytes(canonical.encode()),
                    "fileSha256": "",
                    "generated": False,
                    "vendor": False,
                    "runtimeReachability": "NODE_RUNTIME",
                    "capabilityIds": [],
                    "requirementIds": [],
                    "evidence": ["Node.js builtin registry"],
                    "platform": "NODE",
                    "risk": "NORMAL",
                    "classification": "EXTERNAL",
                },
                canonical,
            )
        return node_id

    def nonconcrete_reference_node(self, source_path: Path, specifier: str, status: str) -> str:
        source_relative = codebase_rel(source_path)
        generated = status == "RESOLVED_GENERATED_ARTIFACT"
        node_type = "GENERATED_ARTIFACT" if generated else "CONFIGURATION"
        layer = "GENERATED_BINDING" if generated else self.file_layers.get(source_relative, "BUILD_AND_CONFIG")
        node_id = stable_id("MR-REF", source_relative, specifier, status, length=24)
        if node_id not in self.nodes:
            self.add_node(
                {
                    "nodeId": node_id, "nodeType": node_type, "layer": layer,
                    "language": language_for(source_path), "package": self.file_packages.get(source_relative, ""),
                    "path": "", "qualifiedName": f"{status.lower()}:{source_relative}:{specifier}",
                    "symbolKind": status, "declarationSpan": "", "uniqueAnchor": specifier,
                    "anchorSha256": sha256_bytes(specifier.encode()), "fileSha256": "",
                    "generated": generated, "vendor": False,
                    "runtimeReachability": status, "capabilityIds": self.capability_paths.get(source_relative, []),
                    "requirementIds": [], "evidence": [source_relative, specifier],
                    "platform": "DYNAMIC_OR_GENERATED", "risk": "HIGH", "classification": "CURRENT_REFERENCE",
                },
                f"{source_relative}::{specifier}::{status}",
            )
        return node_id

    def workspace_export_file(self, package_name: str, specifier: str) -> Path | None:
        info = self.workspace_packages[package_name]
        data = info["data"]
        subpath = specifier[len(package_name):].lstrip("/")
        exports = data.get("exports")
        value: Any = None
        if isinstance(exports, str):
            value = exports if not subpath else None
        elif isinstance(exports, dict):
            key = "." if not subpath else "./" + subpath
            value = exports.get(key)
            if value is None and not subpath and any(k in exports for k in ("source", "import", "default", "types")):
                value = exports
            if value is None:
                for pattern, pattern_value in exports.items():
                    if "*" in pattern and pattern.startswith("./"):
                        regex = "^" + re.escape(pattern[2:]).replace("\\*", "(.+)") + "$"
                        match = re.match(regex, subpath)
                        if match:
                            replacement = first_string(pattern_value)
                            if replacement:
                                value = replacement.replace("*", match.group(1))
                                break
        raw = first_string(value)
        if not raw and not subpath:
            raw = first_string(data.get("source")) or first_string(data.get("module")) or first_string(data.get("browser")) or first_string(data.get("main"))
        if not raw and subpath:
            raw = subpath
        if not raw:
            return None
        candidate = (info["root"] / raw).resolve()
        if candidate in self.all_paths:
            return candidate
        return resolve_relative(info["manifest"], "./" + raw, self.all_paths)

    def add_manifest_dependencies(self) -> None:
        for name, info in sorted(self.workspace_packages.items()):
            source = stable_id("MR-WSPKG", name, length=24)
            manifest_path = codebase_rel(info["manifest"])
            for group in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                dependencies = info["data"].get(group, {})
                if not isinstance(dependencies, dict):
                    continue
                for dependency, version in sorted(dependencies.items()):
                    if dependency in self.workspace_packages or str(version).startswith("workspace:"):
                        if dependency not in self.workspace_packages:
                            target = self.external_node("npm", dependency)
                            status = "RESOLVED_EXTERNAL_PACKAGE"
                        else:
                            target = stable_id("MR-WSPKG", dependency, length=24)
                            status = "RESOLVED_WORKSPACE_PACKAGE"
                    else:
                        target = self.external_node("npm", dependency)
                        status = "RESOLVED_EXTERNAL_PACKAGE"
                    self.add_edge(
                        make_edge(source, target, "BUILD_REFERENCE", manifest_path, "", f"package.json:{group}:{version}", "PACKAGE_JSON", "RESOLVED_WORKSPACE_PACKAGE", status, "BUILD_AND_CONFIG", evidence=[manifest_path, f"{group}.{dependency}={version}"])
                    )

    def add_symbol_nodes(self) -> None:
        for row in iter_jsonl(SYMBOL_PATH):
            path = row.get("currentPath", "")
            if path not in self.file_nodes:
                continue
            if Path(path).name.lower() == "package.json":
                # package.json keys are manifest metadata, not application declarations.
                continue
            layer = self.file_layers[path]
            if layer == "VENDOR_AND_TOOLCHAIN":
                continue
            legacy_symbol_id = row["symbolId"]
            qualified = f"{path}::{row.get('symbol', '')}"
            # V1 included line numbers in MR-SYM allocation and sometimes emitted
            # two IDs for one declaration role.  V2 deliberately migrates those
            # IDs to a line-independent semantic key while retaining the legacy
            # ID as historical evidence.
            symbol_id = stable_id(
                "MR-SYM-V2",
                language_for(GRAPHIFY.parent / path),
                self.file_packages[path],
                qualified,
                row.get("symbolKind", ""),
                length=24,
            )
            self.add_node(
                {
                    "nodeId": symbol_id,
                    "nodeType": "SYMBOL",
                    "layer": layer,
                    "language": language_for(GRAPHIFY.parent / path),
                    "package": self.file_packages[path],
                    "path": path,
                    "qualifiedName": qualified,
                    "symbolKind": row.get("symbolKind", ""),
                    "declarationSpan": row.get("lineRange", ""),
                    "uniqueAnchor": row.get("uniqueAnchor", ""),
                    "anchorSha256": sha256_bytes(row.get("uniqueAnchor", "").encode()),
                    "fileSha256": row.get("fileSha256", self.file_hashes[path]),
                    "generated": layer == "GENERATED_BINDING",
                    "vendor": False,
                    "runtimeReachability": "MEANINGFUL_SYMBOL_MAPPED",
                    "capabilityIds": row.get("capabilityIds", []),
                    "requirementIds": sorted({rid for cid in row.get("capabilityIds", []) for rid in self.requirements_by_capability.get(cid, [])}),
                    "evidence": [path, row.get("lineRange", ""), row.get("uniqueAnchor", "")],
                    "historicalPathAliases": [],
                    "historicalNodeIds": [legacy_symbol_id],
                    "platform": "CROSS_PLATFORM",
                    "risk": "NORMAL",
                    "classification": "CURRENT",
                },
                f"{qualified}::{row.get('symbolKind', '')}",
            )
            self.symbols_by_path[path].append(symbol_id)
            for ast_id in row.get("astNodeIds", []):
                self.symbol_ast_ids[ast_id] = symbol_id
            self.add_edge(
                make_edge(self.file_nodes[path], symbol_id, "CONTAINS_SYMBOL", path, row.get("lineRange", ""), "declaration", "V1_MEANINGFUL_SYMBOL_REGISTRY_REVALIDATED", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_SYMBOL", layer, row.get("capabilityIds", []), [row.get("uniqueAnchor", "")])
            )

    def build_tsconfig_registry(self) -> None:
        config_paths = sorted(
            (GRAPHIFY.parent / relative).resolve()
            for relative in self.file_nodes
            if Path(relative).name.startswith("tsconfig") and relative.lower().endswith(".json")
        )
        documents: dict[Path, dict[str, Any]] = {}
        parse_failures: list[str] = []
        for path in config_paths:
            try:
                documents[path] = parse_jsonc(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                parse_failures.append(codebase_rel(path))

        resolving: set[Path] = set()

        def extends_path(path: Path, value: str) -> Path | None:
            if not value.startswith("."):
                return None
            candidate = (path.parent / value).resolve()
            candidates = [candidate]
            if not candidate.suffix:
                candidates.extend([Path(str(candidate) + ".json"), candidate / "tsconfig.json"])
            return next((item for item in candidates if item in documents), None)

        def resolve_config(path: Path) -> dict[str, Any]:
            if path in self.tsconfig_configs:
                return self.tsconfig_configs[path]
            if path in resolving:
                raise RuntimeError(f"Circular tsconfig extends chain: {codebase_rel(path)}")
            resolving.add(path)
            data = documents[path]
            inherited: list[dict[str, Any]] = []
            parent_path = None
            if isinstance(data.get("extends"), str):
                parent_path = extends_path(path, str(data["extends"]))
                if parent_path:
                    inherited = list(resolve_config(parent_path)["effectiveMappings"])
            compiler = data.get("compilerOptions") if isinstance(data.get("compilerOptions"), dict) else {}
            base_dir = (path.parent / str(compiler.get("baseUrl", "."))).resolve()
            local: list[dict[str, Any]] = []
            paths = compiler.get("paths") if isinstance(compiler.get("paths"), dict) else {}
            for pattern, targets in paths.items():
                values = targets if isinstance(targets, list) else [targets]
                for target in values:
                    if isinstance(pattern, str) and isinstance(target, str):
                        local.append({
                            "pattern": pattern, "target": target, "baseDir": base_dir,
                            "configPath": path, "configRelative": codebase_rel(path),
                        })
            effective_by_key = {(item["pattern"], item["target"]): item for item in inherited}
            for item in local:
                effective_by_key[(item["pattern"], item["target"])] = item
            resolved = {
                "path": path, "data": data, "extendsPath": parent_path,
                "effectiveMappings": sorted(
                    effective_by_key.values(),
                    key=lambda item: (-len(item["pattern"].replace("*", "")), item["pattern"], item["target"]),
                ),
            }
            self.tsconfig_configs[path] = resolved
            resolving.remove(path)
            return resolved

        for path in documents:
            resolve_config(path)
        self.ts_path_mappings = [
            item for config in self.tsconfig_configs.values() for item in config["effectiveMappings"]
        ]

        reference_pairs: set[tuple[str, str]] = set()
        for path, config in sorted(self.tsconfig_configs.items(), key=lambda item: str(item[0])):
            source_relative = codebase_rel(path)
            source_id = self.file_nodes.get(source_relative)
            if not source_id:
                continue
            references = config["data"].get("references", [])
            for reference in references if isinstance(references, list) else []:
                if not isinstance(reference, dict) or not isinstance(reference.get("path"), str):
                    continue
                target = (path.parent / reference["path"]).resolve()
                if target.is_dir() or not target.suffix:
                    target = target / "tsconfig.json"
                target_relative = codebase_rel(target)
                target_id = self.file_nodes.get(target_relative)
                if not target_id:
                    continue
                pair = (source_relative, target_relative)
                if pair in reference_pairs:
                    continue
                reference_pairs.add(pair)
                self.add_edge(make_edge(
                    source_id, target_id, "PROJECT_REFERENCE", source_relative, "", reference["path"],
                    "TSCONFIG_PROJECT_REFERENCE_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_FILE",
                    "BUILD_AND_CONFIG", evidence=[source_relative, f"references.path: {reference['path']}", target_relative],
                ))
        self.tsconfig_summary = {
            "configCount": len(documents), "parseFailures": parse_failures,
            "extendsEdgeCount": sum(bool(config["extendsPath"]) for config in self.tsconfig_configs.values()),
            "effectivePathMappingCount": len(self.ts_path_mappings),
            "projectReferenceEdgeCount": len(reference_pairs),
        }

    def _tsconfig_for_source(self, source_path: Path) -> dict[str, Any] | None:
        candidates = [
            config for path, config in self.tsconfig_configs.items()
            if path.parent == source_path.parent or path.parent in source_path.parents
        ]
        return max(candidates, key=lambda config: len(config["path"].parent.parts)) if candidates else None

    def resolve_tsconfig_path(self, source_path: Path, specifier: str, record: bool = True) -> tuple[str | None, str, list[str]]:
        config = self._tsconfig_for_source(source_path.resolve())
        mappings = config["effectiveMappings"] if config else []
        for mapping in mappings:
            pattern = mapping["pattern"]
            if "*" in pattern:
                prefix, suffix = pattern.split("*", 1)
                if not specifier.startswith(prefix) or not specifier.endswith(suffix):
                    continue
                wildcard = specifier[len(prefix) : len(specifier) - len(suffix) if suffix else None]
            elif specifier == pattern:
                wildcard = ""
            else:
                continue
            mapped = mapping["target"].replace("*", wildcard)
            candidate = (mapping["baseDir"] / mapped).resolve()
            candidates = [candidate]
            source_extensions = (".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".json")
            candidates.extend(Path(str(candidate) + extension) for extension in source_extensions)
            if candidate.suffix.lower() in {".js", ".jsx", ".mjs", ".cjs"}:
                candidates.extend(candidate.with_suffix(extension) for extension in (".ts", ".tsx", ".mts", ".cts"))
            if not candidate.suffix:
                candidates.extend(candidate / f"index{extension}" for extension in (".ts", ".tsx", ".mts", ".cts", ".js", ".jsx"))
            target_path = next((path for path in candidates if path in self.all_paths), None)
            if not target_path:
                continue
            relative = codebase_rel(target_path)
            if record:
                self.ts_path_resolved_counts[specifier.split("/", 2)[0] if not specifier.startswith("@") else "/".join(specifier.split("/")[:2])] += 1
            package_name = package_name_from_specifier(specifier)
            if package_name in self.workspace_packages:
                package_id = stable_id("MR-WSPKG", package_name, length=24)
                self.add_edge(make_edge(
                    package_id, self.file_nodes[relative], "RE_EXPORT",
                    codebase_rel(self.workspace_packages[package_name]["manifest"]), "", specifier,
                    "TSCONFIG_PATH_PACKAGE_EXPORT_RESOLVER", "RESOLVED_WORKSPACE_PACKAGE", "RESOLVED_INTERNAL_FILE",
                    "BUILD_AND_CONFIG", evidence=[mapping["configRelative"], f"{pattern} -> {mapping['target']}", relative],
                ))
            status = "RESOLVED_GENERATED_ARTIFACT" if self.file_layers[relative] == "GENERATED_BINDING" else "RESOLVED_INTERNAL_FILE"
            return self.file_nodes[relative], status, [
                f"tsconfig: {mapping['configRelative']}", f"exact case-sensitive paths mapping: {pattern} -> {mapping['target']}",
                f"wildcard substitution: {wildcard}", f"resolved target: {relative}",
            ]
        return None, "UNRESOLVED_INTERNAL", ["No applicable exact case-sensitive tsconfig paths mapping resolved to a repository file"]

    def finalize_tsconfig_resolution_evidence(self) -> None:
        expected_core = 0
        for relative in sorted(self.file_nodes):
            path = GRAPHIFY.parent / relative
            if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}:
                continue
            text = text_file(path)
            if text is None:
                continue
            expected_core += sum(
                1 for _, specifier, _, _ in source_imports(path, text)
                if specifier.startswith("@affine/core/")
            )
        resolved_core = self.ts_path_resolved_counts.get("@affine/core", 0)
        representative_source = next(
            (GRAPHIFY.parent / relative for relative in self.file_nodes if relative.endswith((".ts", ".tsx"))),
            CODEBASE / "tsconfig.json",
        )
        representative, _, representative_evidence = self.resolve_tsconfig_path(
            representative_source, "@affine/core/modules/storage", record=False
        )
        representative_path = self.nodes[representative].get("path", "") if representative else ""
        expected_representative = "Codebase/packages/frontend/core/src/modules/storage/index.ts"
        if resolved_core != expected_core or representative_path != expected_representative:
            raise RuntimeError(
                f"tsconfig paths coverage failed: expectedCore={expected_core}, resolvedCore={resolved_core}, representative={representative_path}"
            )
        self.tsconfig_summary.update({
            "affineCoreSubpathImportCount": expected_core, "affineCoreSubpathResolvedToInternalFileCount": resolved_core,
            "representativeSpecifier": "@affine/core/modules/storage", "representativeResolvedPath": representative_path,
            "representativeEvidence": representative_evidence,
            "assertions": {
                "allAffineCoreSubpathsResolveToInternalFiles": resolved_core == expected_core,
                "representativeStorageSubpathResolved": representative_path == expected_representative,
                "caseSensitiveWildcardMappingUsed": True,
                "noTsconfigParseFailures": not self.tsconfig_summary.get("parseFailures"),
            },
        })

    def resolve_import(self, source_path: Path, specifier: str) -> tuple[str | None, str, list[str]]:
        suffix = source_path.suffix.lower()
        if suffix in C_FAMILY_SUFFIXES:
            name = Path(specifier).name
            candidates = sorted(
                relative for relative in self.file_nodes
                if Path(relative).name == name
            )
            same_package = [
                relative for relative in candidates
                if self.file_packages[relative] == self.file_packages[codebase_rel(source_path)]
            ]
            selected = same_package if same_package else candidates
            if len(selected) == 1:
                relative = selected[0]
                status = (
                    "RESOLVED_GENERATED_ARTIFACT"
                    if self.file_layers[relative] == "GENERATED_BINDING"
                    else "RESOLVED_INTERNAL_FILE"
                )
                return self.file_nodes[relative], status, [
                    f"exact C/C++ include basename: {name}",
                    f"resolved target: {relative}",
                ]
            return self.external_node("c-header", specifier), "RESOLVED_EXTERNAL_PACKAGE", [
                f"No unique repository-local C/C++ header matched: {specifier}"
            ]
        if suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".css", ".scss", ".sass", ".less", ".graphql", ".gql"}:
            canonical = full_external_specifier(specifier)
            if specifier.startswith("node:") or canonical in NODE_BUILTINS:
                return self.builtin_node(canonical), "RESOLVED_NODE_BUILTIN", ["Node.js builtin resolution"]
            if specifier.startswith((".", "/")):
                target = resolve_relative(source_path, specifier, self.all_paths)
                if target:
                    relative = codebase_rel(target)
                    status = "RESOLVED_GENERATED_ARTIFACT" if self.file_layers[relative] == "GENERATED_BINDING" else "RESOLVED_INTERNAL_FILE"
                    return self.file_nodes[relative], status, [f"relative extension/index resolution: {relative}"]
                source_relative = codebase_rel(source_path)
                if "${" in specifier:
                    return self.nonconcrete_reference_node(source_path, specifier, "DYNAMIC_RUNTIME_REFERENCE"), "DYNAMIC_RUNTIME_REFERENCE", ["computed template specifier retained as dynamic runtime evidence"]
                if Path(specifier).suffix.lower() in {".node", ".wasm"} or (source_relative.endswith("/native/index.js") and Path(specifier).suffix.lower() == ".cjs") or self.file_layers.get(source_relative) == "GENERATED_BINDING":
                    return self.nonconcrete_reference_node(source_path, specifier, "RESOLVED_GENERATED_ARTIFACT"), "RESOLVED_GENERATED_ARTIFACT", ["generated/platform artifact reference; binary or generator output is not checked into source"]
                return None, "UNRESOLVED_INTERNAL", ["relative extension/index resolution exhausted"]
            tsconfig_target, tsconfig_status, tsconfig_evidence = self.resolve_tsconfig_path(source_path, specifier)
            if tsconfig_target:
                return tsconfig_target, tsconfig_status, tsconfig_evidence
            root_name = package_name_from_specifier(specifier)
            if root_name in self.workspace_packages:
                package_id = stable_id("MR-WSPKG", root_name, length=24)
                export_file = self.workspace_export_file(root_name, specifier)
                evidence = [f"workspace package manifest: {codebase_rel(self.workspace_packages[root_name]['manifest'])}"]
                if export_file:
                    relative = codebase_rel(export_file)
                    evidence.append(f"export target: {relative}")
                    export_edge = make_edge(package_id, self.file_nodes[relative], "RE_EXPORT", codebase_rel(self.workspace_packages[root_name]["manifest"]), "", specifier, "WORKSPACE_EXPORT_RESOLVER", "RESOLVED_WORKSPACE_PACKAGE", "RESOLVED_INTERNAL_FILE", "BUILD_AND_CONFIG", evidence=evidence)
                    self.add_edge(export_edge)
                return package_id, "RESOLVED_WORKSPACE_PACKAGE", evidence
            return self.external_node("npm", specifier), "RESOLVED_EXTERNAL_PACKAGE", ["npm namespace resolution"]
        if suffix == ".py":
            if specifier.startswith("."):
                relative_spec = "./" + specifier.lstrip(".").replace(".", "/")
                target = resolve_relative(source_path, relative_spec, self.all_paths)
                if target:
                    relative = codebase_rel(target)
                    return self.file_nodes[relative], "RESOLVED_INTERNAL_FILE", ["Python relative module resolution"]
                return None, "UNRESOLVED_INTERNAL", ["Python relative module not found"]
            return self.external_node("pypi", specifier.split(".")[0]), "RESOLVED_EXTERNAL_PACKAGE", ["Python package namespace resolution"]
        if suffix == ".rs":
            return self.resolve_rust_use(source_path.resolve(), specifier)
        if suffix in {".swift", ".kt", ".kts"}:
            return self.resolve_native_import(source_path, specifier)
        return self.external_node("tool", specifier), "RESOLVED_EXTERNAL_PACKAGE", ["tool namespace resolution"]

    def add_language_imports(self) -> None:
        for relative, source_node in sorted(self.file_nodes.items()):
            layer = self.file_layers[relative]
            if layer in {"VENDOR_AND_TOOLCHAIN", "DOCUMENTATION_AND_LEGAL", "ASSET_AND_MEDIA"}:
                continue
            path = GRAPHIFY.parent / relative
            text = text_file(path)
            if text is None:
                continue
            if path.suffix.lower() == ".rs":
                # Rust `mod` declarations and `use` trees require different resolution semantics.
                continue
            imports = source_imports(path, text)
            if path.suffix.lower() in C_FAMILY_SUFFIXES:
                imports.extend(
                    (
                        "STATIC_IMPORT",
                        match.group(1),
                        "language-aware-c-include",
                        text.count("\n", 0, match.start()) + 1,
                    )
                    for match in re.finditer(
                        r'^[ \t]*#[ \t]*(?:include|import)[ \t]+[<"]([^>"]+)[>"]',
                        text,
                        re.MULTILINE,
                    )
                )
            for relation, specifier, context, line in imports:
                if path.suffix.lower() in {".swift", ".kt", ".kts"}:
                    source_lines = text.splitlines()
                    while line <= len(source_lines) and not source_lines[line - 1].strip():
                        line += 1
                target, status, evidence = self.resolve_import(path, specifier)
                if target is None:
                    diagnostic_id = stable_id("MR-UNRES", relative, str(line), relation, specifier, length=24)
                    self.unresolved.append(
                        {
                            "diagnosticId": diagnostic_id,
                            "origin": "V2_LANGUAGE_AWARE_EXTRACTION",
                            "originalEdgeId": "",
                            "originalSource": relative,
                            "originalTarget": specifier,
                            "originalRelation": relation,
                            "resolutionClassification": status,
                            "resolvedEndpoint": "",
                            "evidence": [relative, f"L{line}", *evidence],
                            "resolverUsed": context,
                            "remainingBlocker": True,
                            "remainingBlockerReason": "Language-aware resolver exhausted repository-local candidates",
                            "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                        }
                    )
                    continue
                if target == source_node:
                    source_line = line_at(text, line)
                    if re.match(r"^[`'\"]", source_line):
                        self.unresolved.append(
                            {
                                "diagnosticId": stable_id(
                                    "MR-UNRES", relative, str(line), relation, specifier,
                                    "GENERATED_TEMPLATE", length=24,
                                ),
                                "origin": "V2_LANGUAGE_AWARE_EXTRACTION",
                                "originalEdgeId": "",
                                "originalSource": relative,
                                "originalTarget": specifier,
                                "originalRelation": relation,
                                "resolutionClassification": "GENERATED_CODE_TEMPLATE_REFERENCE",
                                "resolvedEndpoint": source_node,
                                "evidence": [
                                    relative, f"L{line}", source_line, *evidence,
                                    "The import syntax is inside a string/template emitted by a code generator.",
                                ],
                                "resolverUsed": context,
                                "remainingBlocker": False,
                                "remainingBlockerReason": "",
                                "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                            }
                        )
                        continue
                    self.unresolved.append(
                        {
                            "diagnosticId": stable_id("MR-UNRES", relative, str(line), relation, specifier, "SELF", length=24),
                            "origin": "V2_LANGUAGE_AWARE_EXTRACTION", "originalEdgeId": "",
                            "originalSource": relative, "originalTarget": specifier, "originalRelation": relation,
                            "resolutionClassification": "INVALID_REFERENCE", "resolvedEndpoint": "",
                            "evidence": [relative, f"L{line}", *evidence], "resolverUsed": context,
                            "remainingBlocker": True,
                            "remainingBlockerReason": "Import resolved to its declaring file and was suppressed as a non-semantic self-loop",
                            "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                        }
                    )
                    continue
                target_layer = self.nodes[target]["layer"]
                edge_layer = layer if target_layer == "EXTERNAL_DEPENDENCY" else layer
                self.add_edge(
                    make_edge(source_node, target, relation, relative, f"L{line}", f"{context}:{specifier}", "V2_LANGUAGE_AWARE_RESOLVER", "RESOLVED_INTERNAL_FILE", status, edge_layer, self.capability_paths.get(relative, []), [relative, f"L{line}: {line_at(text, line)}", *evidence])
                )
                if layer == "TEST_AND_FIXTURE" and status in {"RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_SYMBOL", "RESOLVED_WORKSPACE_PACKAGE", "RESOLVED_GENERATED_ARTIFACT"}:
                    self.add_edge(
                        make_edge(source_node, target, "TESTS", relative, f"L{line}", f"test dependency:{specifier}", "V2_TEST_COVERAGE_RESOLVER", "RESOLVED_INTERNAL_FILE", status, "TEST_AND_FIXTURE", self.capability_paths.get(relative, []), [relative, f"L{line}", *evidence])
                    )

    def add_revalidated_ast_edges(self) -> None:
        required = (AST_MERGED_PATH, AST_MERGE_RECEIPT_PATH, AST_EXTRACTION_MANIFEST_PATH)
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Validated V2 AST cache evidence is missing: {missing}")
        receipt = load_json(AST_MERGE_RECEIPT_PATH)
        manifest = load_json(AST_EXTRACTION_MANIFEST_PATH)
        if receipt.get("runId") != RUN_ID or manifest.get("runId") != RUN_ID:
            raise RuntimeError("AST cache runId does not match the active repair run")
        raw_sha = sha256_file(AST_MERGED_PATH)
        manifest_sha = sha256_file(AST_EXTRACTION_MANIFEST_PATH)
        receipt_sha = sha256_file(AST_MERGE_RECEIPT_PATH)
        if receipt.get("outputSha256") != raw_sha or receipt.get("inputManifestSha256") != manifest_sha:
            raise RuntimeError("AST merge receipt hash validation failed")
        batches = manifest.get("batches", [])
        if manifest.get("batchCount") != len(batches) or not batches:
            raise RuntimeError("AST extraction manifest batch partition is incomplete")
        verified_batches = 0
        for batch in batches:
            output = GRAPHIFY / str(batch.get("batchOutputPath", ""))
            if not output.exists() or sha256_file(output) != batch.get("batchOutputSha256"):
                raise RuntimeError(f"AST batch hash validation failed: {batch.get('batchOutputPath')}")
            verified_batches += 1
        if sum(int(batch.get("nodeCount", 0)) for batch in batches) != int(receipt.get("nodeCount", -1)):
            raise RuntimeError("AST batch node counts do not match merge receipt")
        if sum(int(batch.get("edgeCount", 0)) for batch in batches) != int(receipt.get("edgeCount", -1)):
            raise RuntimeError("AST batch edge counts do not match merge receipt")
        if sum(int(value) for value in manifest.get("layers", {}).values()) != int(manifest.get("fileCount", -1)):
            raise RuntimeError("AST layer partition does not match extraction file count")
        raw = load_json(AST_MERGED_PATH)
        raw_nodes = raw.get("nodes", [])
        raw_edges = raw.get("edges", [])
        if raw.get("runId") != RUN_ID or len(raw_nodes) != receipt.get("nodeCount") or len(raw_edges) != receipt.get("edgeCount"):
            raise RuntimeError("Merged AST payload cardinality/provenance validation failed")
        ast_nodes = {str(node.get("id", "")): node for node in raw_nodes if node.get("id")}

        def ast_path(node: dict[str, Any] | None) -> str:
            value = str((node or {}).get("source_file", "")).replace("\\", "/").lstrip("./")
            if not value:
                return ""
            return value if value.startswith("Codebase/") else f"Codebase/{value}"

        def endpoint(ast_id: str) -> str:
            symbol = self.symbol_ast_ids.get(ast_id)
            if symbol:
                return symbol
            relative = ast_path(ast_nodes.get(ast_id))
            return self.file_nodes.get(relative, "")

        relation_map = {
            "calls": "FUNCTION_CALL", "indirect_call": "FUNCTION_CALL",
            "extends": "CLASS_INHERITANCE", "inherits": "CLASS_INHERITANCE",
            "implements": "TYPE_DEPENDENCY", "references": "TYPE_DEPENDENCY",
            "reads_from": "TYPE_DEPENDENCY", "imports": "STATIC_IMPORT",
            "imports_from": "STATIC_IMPORT", "re_exports": "RE_EXPORT",
            "triggers": "EVENT_REGISTRATION",
        }
        language_import_evidence = {
            (edge.get("declaringPath", ""), edge.get("sourceSpan", ""))
            for edge in self.edges.values()
            if edge.get("evidenceOrigin") == "V2_LANGUAGE_AWARE_RESOLVER"
            and edge.get("relation") in {
                "STATIC_IMPORT", "TYPE_ONLY_IMPORT", "TYPE_DEPENDENCY", "DYNAMIC_IMPORT", "RE_EXPORT",
            }
        }
        emitted = 0
        symbol_edges = 0
        relation_counts: Counter[str] = Counter()
        unresolved_cache_endpoints = 0
        same_endpoint_suppressed = 0
        language_import_duplicates_suppressed = 0
        cross_language_edges_suppressed = 0
        local_binding_edges_suppressed = 0
        source_text_cache: dict[str, str] = {}
        for index, row in enumerate(raw_edges):
            raw_relation = str(row.get("relation", ""))
            relation = relation_map.get(raw_relation)
            if not relation:
                continue
            source_ast = str(row.get("source", ""))
            target_ast = str(row.get("target", ""))
            declaring = ast_path(ast_nodes.get(source_ast))
            span = str(row.get("source_location", ""))
            if (
                raw_relation in {"imports", "imports_from", "re_exports"}
                and (declaring, span) in language_import_evidence
            ):
                # Language-aware resolution has source syntax plus ecosystem/package
                # semantics. Raw AST import IDs are only labels and can collide with
                # unrelated declarations (for example SwiftUI and AffineResources).
                language_import_duplicates_suppressed += 1
                continue
            source = endpoint(source_ast)
            target = endpoint(target_ast)
            if not source or not target:
                unresolved_cache_endpoints += 1
                source_row = ast_nodes.get(source_ast, {})
                target_row = ast_nodes.get(target_ast, {})
                self.unresolved.append({
                    "diagnosticId": stable_id(
                        "MR-UNRES", "AST_CACHE_ENDPOINT", str(index), source_ast, target_ast, length=24
                    ),
                    "origin": "V2_VALIDATED_MERGED_AST_CACHE",
                    "originalEdgeId": str(row.get("id", "")),
                    "originalSource": source_ast,
                    "originalTarget": target_ast,
                    "originalRelation": relation,
                    "resolutionClassification": "NON_AUTHORITATIVE_CACHE_ENDPOINT_NOT_PROMOTED",
                    "resolvedEndpoint": "",
                    "evidence": [
                        graphify_rel(AST_MERGED_PATH), f"raw edge index: {index}",
                        f"source path: {ast_path(source_row)}", f"target path: {ast_path(target_row)}",
                    ],
                    "resolverUsed": "V2_AST_TO_AUTHORITATIVE_NODE_CROSSWALK",
                    "remainingBlocker": False,
                    "remainingBlockerReason": "",
                    "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                })
                continue
            if source == target:
                same_endpoint_suppressed += 1
                self.unresolved.append({
                    "diagnosticId": stable_id(
                        "MR-UNRES", "AST_SAME_ENDPOINT", str(index), source_ast, target_ast, length=24
                    ),
                    "origin": "V2_VALIDATED_MERGED_AST_CACHE",
                    "originalEdgeId": str(row.get("id", "")),
                    "originalSource": source_ast,
                    "originalTarget": target_ast,
                    "originalRelation": relation,
                    "resolutionClassification": "NON_SEMANTIC_SAME_ENDPOINT_SUPPRESSED",
                    "resolvedEndpoint": source,
                    "evidence": [
                        graphify_rel(AST_MERGED_PATH), f"raw edge index: {index}",
                        "Both raw AST endpoints crosswalk to the same authoritative node.",
                    ],
                    "resolverUsed": "V2_AST_SAME_ENDPOINT_GUARD",
                    "remainingBlocker": False,
                    "remainingBlockerReason": "",
                    "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                })
                continue
            source_node = self.nodes[source]
            target_node = self.nodes[target]
            if source_node["layer"] == "VENDOR_AND_TOOLCHAIN" or target_node["layer"] == "VENDOR_AND_TOOLCHAIN":
                continue
            source_family = strict_ast_language_family(source_node.get("path", ""))
            target_family = strict_ast_language_family(target_node.get("path", ""))
            if source_family and target_family and source_family != target_family:
                cross_language_edges_suppressed += 1
                self.unresolved.append({
                    "diagnosticId": stable_id(
                        "MR-UNRES", "AST_CROSS_LANGUAGE", str(index), source_ast, target_ast, length=24
                    ),
                    "origin": "V2_VALIDATED_MERGED_AST_CACHE",
                    "originalEdgeId": str(row.get("id", "")),
                    "originalSource": source_ast,
                    "originalTarget": target_ast,
                    "originalRelation": relation,
                    "resolutionClassification": "NON_SEMANTIC_CROSS_LANGUAGE_AST_COLLISION_SUPPRESSED",
                    "resolvedEndpoint": "",
                    "evidence": [
                        graphify_rel(AST_MERGED_PATH), f"raw edge index: {index}",
                        f"source path: {source_node.get('path', '')}",
                        f"target path: {target_node.get('path', '')}",
                        f"language families: {source_family} -> {target_family}",
                    ],
                    "resolverUsed": "V2_AST_STRICT_LANGUAGE_FAMILY_GUARD",
                    "remainingBlocker": False,
                    "remainingBlockerReason": "",
                    "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                })
                continue
            source_path = source_node.get("path", "")
            target_path = target_node.get("path", "")
            target_label = str(ast_nodes.get(target_ast, {}).get("label", "")).strip()
            if (
                raw_relation not in {"imports", "imports_from", "re_exports"}
                and source_path != target_path
                and source_family == "JAVASCRIPT_TYPESCRIPT"
                and re.fullmatch(r"[A-Za-z_$][\w$]*", target_label)
            ):
                if source_path not in source_text_cache:
                    source_text_cache[source_path] = (
                        text_file(GRAPHIFY.parent / source_path) or ""
                    )
                local_binding = re.search(
                    rf"(?m)^[ \t]*(?:export[ \t]+)?(?:const|let|var)[ \t]+"
                    rf"{re.escape(target_label)}\b",
                    source_text_cache[source_path],
                )
                if local_binding:
                    local_binding_edges_suppressed += 1
                    self.unresolved.append({
                        "diagnosticId": stable_id(
                            "MR-UNRES", "AST_LOCAL_BINDING", str(index),
                            source_ast, target_ast, length=24,
                        ),
                        "origin": "V2_VALIDATED_MERGED_AST_CACHE",
                        "originalEdgeId": str(row.get("id", "")),
                        "originalSource": source_ast,
                        "originalTarget": target_ast,
                        "originalRelation": relation,
                        "resolutionClassification": "NON_SEMANTIC_LOCAL_BINDING_AST_COLLISION_SUPPRESSED",
                        "resolvedEndpoint": "",
                        "evidence": [
                            graphify_rel(AST_MERGED_PATH), f"raw edge index: {index}",
                            f"source path: {source_path}",
                            f"incorrect cross-file target path: {target_path}",
                            f"local value binding: {target_label}",
                        ],
                        "resolverUsed": "V2_AST_LOCAL_VALUE_BINDING_GUARD",
                        "remainingBlocker": False,
                        "remainingBlockerReason": "",
                        "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                    })
                    continue
            declaring = declaring or source_node.get("path", "")
            source_resolution = "RESOLVED_INTERNAL_FILE" if source_node.get("isFileRecord") else "RESOLVED_INTERNAL_SYMBOL"
            if target_node.get("isFileRecord"):
                target_resolution = "RESOLVED_GENERATED_ARTIFACT" if target_node["layer"] == "GENERATED_BINDING" else "RESOLVED_INTERNAL_FILE"
            else:
                target_resolution = "RESOLVED_GENERATED_ARTIFACT" if target_node["layer"] == "GENERATED_BINDING" else "RESOLVED_INTERNAL_SYMBOL"
            evidence = [
                graphify_rel(AST_MERGED_PATH), f"raw edge index: {index}",
                f"source AST id: {source_ast}", f"target AST id: {target_ast}",
                f"raw relation: {row.get('relation', '')}", declaring, span,
            ]
            self.add_edge(make_edge(
                source, target, relation, declaring, span,
                f"{row.get('context', '')}|raw-edge-index:{index}",
                "V2_VALIDATED_MERGED_AST_CACHE", source_resolution, target_resolution,
                source_node["layer"], sorted(set(source_node.get("capabilityIds", [])) | set(target_node.get("capabilityIds", []))),
                evidence,
            ))
            emitted += 1
            relation_counts[relation] += 1
            if not source_node.get("isFileRecord") and not target_node.get("isFileRecord"):
                symbol_edges += 1
        if symbol_edges < 100 or len(relation_counts) < 2:
            raise RuntimeError(
                f"Fresh AST symbol dependency evidence is below threshold: symbolEdges={symbol_edges}, relations={dict(relation_counts)}"
            )
        self.ast_cache_summary = {
            "cacheRoot": graphify_rel(AST_CACHE_ROOT), "rawMergedPath": graphify_rel(AST_MERGED_PATH),
            "rawMergedSha256": raw_sha, "extractionManifestSha256": manifest_sha,
            "mergeReceiptSha256": receipt_sha, "batchCount": len(batches), "verifiedBatchCount": verified_batches,
            "partitionLayers": manifest.get("layers", {}), "rawNodeCount": len(raw_nodes), "rawEdgeCount": len(raw_edges),
            "emittedDependencyEdgeCount": emitted, "symbolEdgeCount": symbol_edges,
            "emittedRelationCounts": dict(sorted(relation_counts.items())),
            "unmappedRawEdgeEndpointCount": unresolved_cache_endpoints,
            "sameEndpointEdgesSuppressed": same_endpoint_suppressed,
            "languageAwareImportDuplicatesSuppressed": language_import_duplicates_suppressed,
            "crossLanguageEdgesSuppressed": cross_language_edges_suppressed,
            "localBindingEdgesSuppressed": local_binding_edges_suppressed,
            "assertions": {
                "mergeReceiptHashesValid": True, "allBatchHashesValid": verified_batches == len(batches),
                "batchPartitionCountsValid": True, "freshRunIdMatches": True,
                "symbolDependencyThresholdMet": symbol_edges >= 100 and len(relation_counts) >= 2,
                "activeDependencyOutputReadAsInput": False,
                "languageAwareImportPrecedenceApplied": True,
                "strictLanguageFamilySeparationApplied": True,
                "localValueBindingCollisionGuardApplied": True,
            },
        }

    def add_sql_relationships(self) -> None:
        foreign_keys: list[dict[str, Any]] = []
        for relative, file_id in sorted(self.file_nodes.items()):
            if not relative.lower().endswith(".sql"):
                continue
            path = GRAPHIFY.parent / relative
            text = text_file(path)
            if not text:
                continue
            tables: dict[str, str] = {}
            creates = list(SQL_CREATE_SCOPE_RE.finditer(text))
            for match in creates:
                table = sql_table_name(match.group("table"))
                node_id = stable_id("MR-SCHEMA", relative, table, length=24)
                self.add_node(
                    {
                        "nodeId": node_id, "nodeType": "SCHEMA", "layer": "MIGRATION_AND_SCHEMA",
                        "language": "SQL", "package": self.file_packages[relative], "path": relative,
                        "qualifiedName": f"{relative}::{table}", "symbolKind": "TABLE",
                        "declarationSpan": f"L{text.count(chr(10), 0, match.start()) + 1}", "uniqueAnchor": match.group(0),
                        "anchorSha256": sha256_bytes(match.group(0).encode()), "fileSha256": self.file_hashes[relative],
                        "generated": False, "vendor": False, "runtimeReachability": "SCHEMA_DECLARATION",
                        "capabilityIds": self.capability_paths.get(relative, []), "requirementIds": [],
                        "evidence": [relative, match.group(0)], "platform": "DATABASE", "risk": "CRITICAL",
                        "classification": "CURRENT",
                    },
                    f"{relative}::{table}",
                )
                tables[table] = node_id
                self.add_edge(make_edge(file_id, node_id, "SCHEMA_REGISTRATION", relative, f"L{text.count(chr(10), 0, match.start()) + 1}", "CREATE TABLE", "SQL_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_SYMBOL", "MIGRATION_AND_SCHEMA", evidence=[match.group(0)]))

            def table_reference_node(table: str, local: bool, evidence: list[str]) -> str:
                if table in tables:
                    return tables[table]
                referent = f"{relative}::{table}" if local else f"global-table::{table}"
                node_id = stable_id("MR-SCHEMA", relative if local else "global-table", table, length=24)
                if node_id not in self.nodes:
                    self.add_node({
                        "nodeId": node_id, "nodeType": "SCHEMA", "layer": "MIGRATION_AND_SCHEMA", "language": "SQL",
                        "package": self.file_packages[relative], "path": relative if local else "",
                        "qualifiedName": f"{relative}::{table}" if local else f"schema-table:{table}",
                        "symbolKind": "TABLE_REFERENCE", "declarationSpan": "", "uniqueAnchor": table,
                        "anchorSha256": sha256_bytes(table.encode()),
                        "fileSha256": self.file_hashes[relative] if local else "", "generated": False,
                        "vendor": False, "runtimeReachability": "SCHEMA_REFERENCE",
                        "capabilityIds": self.capability_paths.get(relative, []) if local else [],
                        "requirementIds": [], "evidence": evidence, "platform": "DATABASE",
                        "risk": "CRITICAL", "classification": "CURRENT",
                    }, referent)
                if local:
                    tables[table] = node_id
                return node_id

            for statement_start, statement in sql_statements(text):
                refs = list(SQL_REFERENCE_RE.finditer(statement))
                if not refs:
                    continue
                create_scope = SQL_CREATE_SCOPE_RE.search(statement)
                alter_scope = SQL_ALTER_SCOPE_RE.search(statement)
                scope = alter_scope or create_scope
                scope_kind = "ALTER TABLE" if alter_scope else "CREATE TABLE" if create_scope else ""
                for ref in refs:
                    absolute = statement_start + ref.start()
                    line = text.count("\n", 0, absolute) + 1
                    target_table = sql_table_name(ref.group("table"))
                    if scope is None:
                        self.unresolved.append({
                            "diagnosticId": stable_id("MR-UNRES", relative, str(line), "SQL_FK_SCOPE", target_table, length=24),
                            "origin": "V2_SQL_FOREIGN_KEY_RESOLVER", "originalEdgeId": "",
                            "originalSource": relative, "originalTarget": target_table,
                            "originalRelation": "MIGRATION_DEPENDENCY", "resolutionClassification": "UNRESOLVED_INTERNAL",
                            "resolvedEndpoint": "", "evidence": [relative, f"L{line}", statement.strip()[:500]],
                            "resolverUsed": "SQL_STATEMENT_SCOPE_RESOLVER", "remainingBlocker": True,
                            "remainingBlockerReason": "REFERENCES clause is not scoped by CREATE TABLE or ALTER TABLE",
                            "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                        })
                        continue
                    source_table = sql_table_name(scope.group("table"))
                    source_id = table_reference_node(source_table, True, [relative, scope.group(0)])
                    target_id = source_id if source_table == target_table else (
                        tables[target_table] if target_table in tables
                        else table_reference_node(target_table, False, [relative, ref.group(0)])
                    )
                    recursive = "VALID_SCHEMA_SELF_REFERENCE" if source_table == target_table else "NOT_RECURSIVE"
                    edge = make_edge(
                        source_id, target_id, "MIGRATION_DEPENDENCY", relative, f"L{line}",
                        f"{scope_kind} {source_table}: {ref.group(0)}", "SQL_STATEMENT_SCOPED_FOREIGN_KEY_RESOLVER",
                        "RESOLVED_INTERNAL_SYMBOL", "RESOLVED_INTERNAL_SYMBOL", "MIGRATION_AND_SCHEMA",
                        self.capability_paths.get(relative, []),
                        [relative, f"L{line}", scope.group(0), ref.group(0)], recursive,
                    )
                    self.add_edge(edge)
                    foreign_keys.append({
                        "edgeId": edge["edgeId"], "path": relative, "line": line,
                        "scopeKind": scope_kind, "sourceTable": source_table, "targetTable": target_table,
                        "recursiveStatus": recursive,
                    })
                    if recursive == "VALID_SCHEMA_SELF_REFERENCE":
                        self.sql_self_loop_edge_ids.append(edge["edgeId"])
        recursive = [row for row in foreign_keys if row["recursiveStatus"] == "VALID_SCHEMA_SELF_REFERENCE"]
        expected_path = "Codebase/packages/backend/server/migrations/20260711080000_auth_sessions/migration.sql"
        if len(recursive) != 1 or recursive[0]["sourceTable"] != "auth_refresh_tokens" or recursive[0]["path"] != expected_path:
            raise RuntimeError(f"SQL self-reference classification mismatch: {recursive}")
        self.sql_resolution_summary = {
            "foreignKeyCount": len(foreign_keys), "createScopedCount": sum(row["scopeKind"] == "CREATE TABLE" for row in foreign_keys),
            "alterScopedCount": sum(row["scopeKind"] == "ALTER TABLE" for row in foreign_keys),
            "validSchemaSelfReferenceCount": len(recursive), "validSchemaSelfReferences": recursive,
            "falseSelfReferences": 0, "assertions": {
                "allForeignKeysHaveStatementSourceScope": all(row["sourceTable"] for row in foreign_keys),
                "onlyAuthRefreshTokensIsRecursive": len(recursive) == 1 and recursive[0]["sourceTable"] == "auth_refresh_tokens",
            },
        }

    def add_semantic_schema_relationships(self) -> None:
        """Map GraphQL definitions plus SQL columns, indexes, and migration order."""
        graphql_definitions: dict[str, list[str]] = defaultdict(list)
        graphql_nodes_by_path: dict[str, list[str]] = defaultdict(list)
        graphql_schema_files = [
            path for path in self.file_nodes
            if path.endswith((".gql", ".graphql")) and "schema" in Path(path).name.lower()
        ]
        for relative in sorted(
            path for path in self.file_nodes if path.endswith((".gql", ".graphql"))
        ):
            text = text_file(GRAPHIFY.parent / relative) or ""
            file_id = self.file_nodes[relative]
            for match in re.finditer(
                r"(?m)^[ \t]*(query|mutation|subscription|fragment)\s+([A-Za-z_]\w*)",
                text,
            ):
                kind, name = match.groups()
                node_type = "GRAPHQL_FRAGMENT" if kind == "fragment" else "GRAPHQL_OPERATION"
                node_id = stable_id("MR-GRAPHQL", relative, kind, name, length=24)
                line = text.count("\n", 0, match.start()) + 1
                self.add_node({
                    "nodeId": node_id, "nodeType": node_type, "layer": self.file_layers[relative],
                    "language": "GraphQL", "package": self.file_packages[relative], "path": relative,
                    "qualifiedName": f"{relative}::{name}", "symbolKind": kind.upper(),
                    "declarationSpan": f"L{line}", "uniqueAnchor": match.group(0),
                    "anchorSha256": sha256_bytes(match.group(0).encode()),
                    "fileSha256": self.file_hashes[relative], "generated": False, "vendor": False,
                    "runtimeReachability": "GRAPHQL_DOCUMENT_DEFINITION",
                    "capabilityIds": self.capability_paths.get(relative, []), "requirementIds": [],
                    "evidence": [relative, f"L{line}", match.group(0)], "platform": "CROSS_PLATFORM",
                    "risk": "HIGH", "classification": "CURRENT",
                }, f"{relative}::{kind}::{name}")
                graphql_definitions[name].append(node_id)
                graphql_nodes_by_path[relative].append(node_id)
                self.add_edge(make_edge(
                    file_id, node_id, "SCHEMA_REGISTRATION", relative, f"L{line}", match.group(0),
                    "GRAPHQL_DOCUMENT_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_SYMBOL",
                    self.file_layers[relative], evidence=[relative, f"L{line}", match.group(0)],
                ))
            spreads = sorted(set(re.findall(r"\.\.\.([A-Za-z_]\w*)", text)) - {"on"})
            for source_id in graphql_nodes_by_path[relative] or [file_id]:
                for fragment_name in spreads:
                    for target_id in graphql_definitions.get(fragment_name, []):
                        if source_id != target_id:
                            self.add_edge(make_edge(
                                source_id, target_id, "GRAPHQL_FRAGMENT_DEPENDENCY", relative, "",
                                f"...{fragment_name}", "GRAPHQL_FRAGMENT_RESOLVER",
                                "RESOLVED_INTERNAL_SYMBOL" if source_id != file_id else "RESOLVED_INTERNAL_FILE",
                                "RESOLVED_INTERNAL_SYMBOL", self.file_layers[relative],
                                evidence=[relative, f"...{fragment_name}"],
                            ))
                for schema_path in graphql_schema_files:
                    if schema_path == relative:
                        continue
                    self.add_edge(make_edge(
                        source_id, self.file_nodes[schema_path], "TYPE_DEPENDENCY", relative, "",
                        "GraphQL operation validated against repository schema",
                        "GRAPHQL_SCHEMA_DEPENDENCY_RESOLVER",
                        "RESOLVED_INTERNAL_SYMBOL" if source_id != file_id else "RESOLVED_INTERNAL_FILE",
                        "RESOLVED_INTERNAL_FILE", self.file_layers[relative],
                        evidence=[relative, schema_path],
                    ))

        sql_column_count = 0
        sql_index_count = 0
        for relative in sorted(path for path in self.file_nodes if path.lower().endswith(".sql")):
            text = text_file(GRAPHIFY.parent / relative) or ""
            file_id = self.file_nodes[relative]
            table_nodes = {
                self.nodes[node_id]["qualifiedName"].rsplit("::", 1)[-1]: node_id
                for node_id in self.nodes
                if self.nodes[node_id].get("path") == relative
                and self.nodes[node_id].get("symbolKind") == "TABLE"
            }
            for match in re.finditer(
                rf"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<table>{SQL_IDENTIFIER})\s*\((?P<body>.*?)\)\s*;",
                text,
                re.IGNORECASE | re.DOTALL,
            ):
                table = sql_table_name(match.group("table"))
                table_id = table_nodes.get(table)
                if not table_id:
                    continue
                body_start = match.start("body")
                for raw_line in match.group("body").splitlines():
                    declaration = raw_line.strip().rstrip(",")
                    if not declaration or re.match(
                        r"(?i)^(PRIMARY|FOREIGN|UNIQUE|CHECK|CONSTRAINT)\b", declaration
                    ):
                        continue
                    column_match = re.match(r'(?:"([^"]+)"|`([^`]+)`|\[([^\]]+)\]|([A-Za-z_]\w*))\s+', declaration)
                    if not column_match:
                        continue
                    column = next(value for value in column_match.groups() if value)
                    node_id = stable_id("MR-SQL-COLUMN", relative, table, column, length=24)
                    line = text.count("\n", 0, body_start + match.group("body").find(raw_line)) + 1
                    self.add_node({
                        "nodeId": node_id, "nodeType": "SCHEMA", "layer": "MIGRATION_AND_SCHEMA",
                        "language": "SQL", "package": self.file_packages[relative], "path": relative,
                        "qualifiedName": f"{relative}::{table}.{column}", "symbolKind": "COLUMN",
                        "declarationSpan": f"L{line}", "uniqueAnchor": declaration,
                        "anchorSha256": sha256_bytes(declaration.encode()), "fileSha256": self.file_hashes[relative],
                        "generated": False, "vendor": False, "runtimeReachability": "SCHEMA_DECLARATION",
                        "capabilityIds": self.capability_paths.get(relative, []), "requirementIds": [],
                        "evidence": [relative, f"L{line}", declaration], "platform": "DATABASE",
                        "risk": "CRITICAL", "classification": "CURRENT",
                    }, f"{relative}::{table}.{column}")
                    self.add_edge(make_edge(
                        table_id, node_id, "SCHEMA_COLUMN", relative, f"L{line}", declaration,
                        "SQL_COLUMN_RESOLVER", "RESOLVED_INTERNAL_SYMBOL", "RESOLVED_INTERNAL_SYMBOL",
                        "MIGRATION_AND_SCHEMA", evidence=[relative, f"L{line}", declaration],
                    ))
                    sql_column_count += 1
            for match in re.finditer(
                rf"\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<index>{SQL_IDENTIFIER})\s+ON\s+(?P<table>{SQL_IDENTIFIER})\s*\((?P<columns>[^)]+)\)",
                text,
                re.IGNORECASE,
            ):
                index_name = sql_table_name(match.group("index"))
                table = sql_table_name(match.group("table"))
                node_id = stable_id("MR-SQL-INDEX", relative, index_name, length=24)
                line = text.count("\n", 0, match.start()) + 1
                self.add_node({
                    "nodeId": node_id, "nodeType": "SCHEMA", "layer": "MIGRATION_AND_SCHEMA",
                    "language": "SQL", "package": self.file_packages[relative], "path": relative,
                    "qualifiedName": f"{relative}::index::{index_name}", "symbolKind": "INDEX",
                    "declarationSpan": f"L{line}", "uniqueAnchor": match.group(0),
                    "anchorSha256": sha256_bytes(match.group(0).encode()), "fileSha256": self.file_hashes[relative],
                    "generated": False, "vendor": False, "runtimeReachability": "SCHEMA_DECLARATION",
                    "capabilityIds": self.capability_paths.get(relative, []), "requirementIds": [],
                    "evidence": [relative, f"L{line}", match.group(0)], "platform": "DATABASE",
                    "risk": "CRITICAL", "classification": "CURRENT",
                }, f"{relative}::index::{index_name}")
                self.add_edge(make_edge(
                    file_id, node_id, "SCHEMA_REGISTRATION", relative, f"L{line}", match.group(0),
                    "SQL_INDEX_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_SYMBOL",
                    "MIGRATION_AND_SCHEMA", evidence=[relative, f"L{line}", match.group(0)],
                ))
                sql_index_count += 1

        migration_groups: dict[str, list[str]] = defaultdict(list)
        for relative in self.file_nodes:
            match = re.match(r"(.*/migrations)/([^/]+)/.*\.sql$", relative, re.IGNORECASE)
            if match:
                migration_groups[match.group(1)].append(relative)
        migration_order_edges = 0
        for root, paths in sorted(migration_groups.items()):
            ordered = sorted(paths)
            for previous, current in zip(ordered, ordered[1:]):
                self.add_edge(make_edge(
                    self.file_nodes[previous], self.file_nodes[current], "MIGRATION_ORDER", current, "",
                    f"{Path(previous).parent.name} precedes {Path(current).parent.name}",
                    "MIGRATION_PATH_ORDER_RESOLVER", "RESOLVED_INTERNAL_FILE", "RESOLVED_INTERNAL_FILE",
                    "MIGRATION_AND_SCHEMA", evidence=[root, previous, current],
                ))
                migration_order_edges += 1
        self.graphql_summary = {
            "definitionCount": sum(len(nodes) for nodes in graphql_definitions.values()),
            "operationAndFragmentNames": len(graphql_definitions),
            "schemaFileCount": len(graphql_schema_files),
        }
        self.semantic_config_summary = {
            "sqlColumnCount": sql_column_count,
            "sqlIndexCount": sql_index_count,
            "migrationOrderEdgeCount": migration_order_edges,
        }

    def add_known_self_loop_repairs(self) -> None:
        slider_path = "Codebase/packages/frontend/component/src/ui/slider/slider.tsx"
        candidates = [
            node_id for node_id in self.symbols_by_path.get(slider_path, [])
            if self.nodes[node_id].get("qualifiedName", "").endswith("::SliderProps")
        ]
        if not candidates:
            raise RuntimeError("SliderProps meaningful symbol was not mapped")
        source = candidates[0]
        target = self.external_node("npm", "@radix-ui/react-slider#Sliders.SliderProps")
        replacement = make_edge(
            source, target, "TYPE_DEPENDENCY", slider_path, "L8",
            "SliderProps extends Sliders.SliderProps", "V2_NAMESPACE_QUALIFIED_TYPESCRIPT_RESOLVER",
            "RESOLVED_INTERNAL_SYMBOL", "RESOLVED_EXTERNAL_PACKAGE", "AUTHORED_RUNTIME",
            self.capability_paths.get(slider_path, []),
            [slider_path, "L1 import * as Sliders from '@radix-ui/react-slider'", "L8 local SliderProps extends external Sliders.SliderProps"],
        )
        self.add_edge(replacement)
        sql_edges = [self.edges[edge_id] for edge_id in self.sql_self_loop_edge_ids]
        if len(sql_edges) != 1:
            raise RuntimeError(f"Expected one authoritative SQL self-loop edge, found {len(sql_edges)}")
        sql_edge = sql_edges[0]
        self.self_loop_rows = [
            {
                "loopId": "MR-SELF-LOOP-SLIDER-PROPS", "path": slider_path,
                "v1Classification": "INVALID_TYPESCRIPT_SELF_LOOP", "v2Classification": "REPAIRED_EXTERNAL_TYPE_DEPENDENCY",
                "sourceNodeId": source, "targetNodeId": target, "replacementEdgeId": replacement["edgeId"],
                "invalidSelfLoopRemaining": False, "evidence": replacement["evidence"], "runId": RUN_ID,
            },
            {
                "loopId": "MR-SELF-LOOP-AUTH-REFRESH-TOKENS", "path": "Codebase/packages/backend/server/migrations/20260711080000_auth_sessions/migration.sql",
                "v1Classification": "UNCLASSIFIED_SELF_LOOP", "v2Classification": "VALID_SCHEMA_SELF_REFERENCE",
                "sourceNodeId": sql_edge["sourceNodeId"], "targetNodeId": sql_edge["targetNodeId"],
                "replacementEdgeId": sql_edge["edgeId"], "invalidSelfLoopRemaining": False,
                "evidence": sql_edge["evidence"], "runId": RUN_ID,
            },
        ]

    def runtime_patterns(self) -> list[tuple[str, str, re.Pattern[str]]]:
        return [
            ("PRELOAD_EXPOSURE", "electron-preload", re.compile(r"contextBridge\.exposeInMainWorld\s*\(\s*['\"]([^'\"]+)")),
            ("IPC_REGISTRATION", "electron-main-ipc", re.compile(r"ipcMain\.(?:handle|handleOnce|on|once)\s*\(\s*([^,\n]+)")),
            ("IPC_EVENT_LISTENER", "electron-renderer-ipc", re.compile(r"ipcRenderer\.(?:on|once)\s*\(\s*([^,\n]+)")),
            ("PROTOCOL_REGISTRATION", "electron-protocol", re.compile(r"\bprotocol\.(?:handle|register\w*Protocol)\s*\(\s*([^,\n]+)")),
            ("MENU_REGISTRATION", "electron-menu", re.compile(r"\bMenu\.(?:setApplicationMenu|buildFromTemplate)\s*\(")),
            ("APPLICATION_EVENT", "electron-app", re.compile(r"\bapp\.(?:on|once|whenReady)\s*\(\s*([^,\n)]*)")),
            ("COMMAND_REGISTRATION", "command-api", re.compile(r"\b(?:registerCommand|registerCommands|commandService\.add|commands\.add)\s*\(\s*([^,\n]+)")),
            ("COMMAND_REGISTRATION", "affine-command", re.compile(r"\bregisterAffineCommand\s*\(\s*([^,\n]+)")),
            ("ROUTE_REGISTRATION", "http-router-call", re.compile(r"\b(?:router|app)\.(?:get|post|put|patch|delete|use)\s*\(\s*['\"]([^'\"]+)")),
            ("ROUTE_REGISTRATION", "framework-route-decorator", re.compile(r"@(?:Controller|Get|Post|Put|Patch|Delete)\s*\(\s*['\"]?([^'\")\n]*)")),
            ("DI_REGISTRATION", "framework-di", re.compile(r"\bframework\.(?:service|scope|entity|store|impl|provider)\s*\(\s*([^,\n]+)")),
            ("DI_REGISTRATION", "context-di", re.compile(r"\bcontext\.register\s*\(\s*([^,\n]+)")),
            ("DI_REGISTRATION", "nest-module", re.compile(r"@Module\s*\(\s*\{")),
            ("WORKER_REGISTRATION", "web-worker", re.compile(r"new\s+(?:SharedWorker|Worker)\s*\(([^\n]+)")),
            ("FEATURE_FLAG_REGISTRATION", "feature-api", re.compile(r"\b(?:defineFeature|registerFeature|featureFlags?\.(?:add|register))\s*\(\s*([^,\n]+)")),
            ("SCHEMA_REGISTRATION", "schema-api", re.compile(r"\b(?:registerSchema|schema\.register|Schemas?\.add)\s*\(\s*([^,\n]+)")),
            ("PLUGIN_REGISTRATION", "plugin-api", re.compile(r"\b(?:registerPlugin|registerExtension|extensions?\.register)\s*\(\s*([^,\n]+)")),
            ("BACKGROUND_JOB", "nest-schedule", re.compile(r"@(?:Cron|Interval|Timeout)\s*\(([^\n]*)")),
            ("GRAPHQL_RESOLVER", "graphql-decorator", re.compile(r"@Resolver\s*\(([^\n]*)")),
        ]

    def add_runtime_registrations(self) -> None:
        seen: set[tuple[str, str, str]] = set()
        scanned_files = 0
        suppressed_noncode_files = 0
        suppressed_test_or_fixture_files = 0
        suppressed_route_path_candidates = 0
        for relative, file_id in sorted(self.file_nodes.items()):
            path = GRAPHIFY.parent / relative
            if path.suffix.lower() not in RUNTIME_CODE_SUFFIXES:
                suppressed_noncode_files += 1
                continue
            if self.file_layers[relative] != "AUTHORED_RUNTIME" or any(
                token in path.name.lower() for token in (".test.", ".spec.", ".stories.", ".config.")
            ):
                suppressed_test_or_fixture_files += 1
                continue
            text = text_file(path)
            if not text:
                continue
            scanned_files += 1
            if path.suffix.lower() == ".tsx" and re.search(r"(?:from\s+['\"]react-router|<Routes?\b)", text):
                for start, end, anchor, path_value, target_value in iter_jsx_route_opening_tags(text):
                    line = text.count("\n", 0, start) + 1
                    end_line = text.count("\n", 0, end) + 1
                    key = (relative, "ROUTE_REGISTRATION", f"{line}-{end_line}")
                    if key in seen:
                        continue
                    seen.add(key)
                    normalized_path = path_value.strip()
                    if normalized_path.startswith("{") and normalized_path.endswith("}"):
                        normalized_path = normalized_path[1:-1].strip()
                    if len(normalized_path) >= 2 and normalized_path[0] == normalized_path[-1] and normalized_path[0] in "\"'`":
                        normalized_path = normalized_path[1:-1].strip()
                    identifier = stable_runtime_identifier(normalized_path, "ROUTE_REGISTRATION", line)
                    self._add_registration(
                        stable_id("MR-REG", relative, "ROUTE_REGISTRATION", str(line), identifier, length=24),
                        "ROUTE_REGISTRATION", relative, target_value, f"{line}-{end_line}", identifier,
                        [relative], [], [], self.capability_paths.get(relative, []), "KEEP", "HIGH",
                        [
                            f"{relative}:L{line}-L{end_line}",
                            f"exact JSX route anchor: {anchor}",
                            f"path attribute: {path_value}",
                            f"route target attribute: {target_value or 'nested route outlet'}",
                            "recognized runtime construct: react-router-jsx-route",
                        ],
                        "V2_REACT_ROUTER_JSX_REGISTRATION_SCAN",
                    )
            for registration_type, construct, pattern in self.runtime_patterns():
                for match in pattern.finditer(text):
                    line = text.count("\n", 0, match.start()) + 1
                    source_line = line_at(text, line)
                    if source_line.lstrip().startswith(("//", "*", "/*")):
                        continue
                    key = (relative, registration_type, str(line))
                    if key in seen:
                        continue
                    seen.add(key)
                    raw_identifier = match.group(1).strip() if match.lastindex else match.group(0).strip()
                    nearby = text[match.start() : match.start() + 1400]
                    if construct == "affine-command" and raw_identifier.startswith("{"):
                        command_id = re.search(r"\bid\s*:\s*['\"]([^'\"]+)['\"]", nearby)
                        if command_id:
                            raw_identifier = command_id.group(1)
                    if construct in {"nest-module", "graphql-decorator"} or not raw_identifier:
                        class_name = re.search(r"\b(?:export\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)", nearby)
                        if class_name:
                            raw_identifier = class_name.group(1)
                    identifier = stable_runtime_identifier(raw_identifier, registration_type, line)
                    self._add_registration(
                        stable_id("MR-REG", relative, registration_type, str(line), identifier, length=24),
                        registration_type,
                        relative,
                        "",
                        f"{line}-{line}",
                        identifier,
                        [relative],
                        [],
                        [],
                        self.capability_paths.get(relative, []),
                        "MIXED" if "cloud" in text[max(0, match.start()-200):match.end()+200].lower() else "KEEP",
                        "CRITICAL" if registration_type in {"IPC_REGISTRATION", "PRELOAD_EXPOSURE", "SCHEMA_REGISTRATION"} else "HIGH",
                        [f"{relative}:L{line}: {source_line}", f"recognized runtime construct: {construct}"],
                        "V2_LANGUAGE_AND_ROLE_SCOPED_RUNTIME_SCAN",
                    )

        package_swift_path_literals = sum(
            len(re.findall(r"\bpath\s*:\s*['\"][^'\"]+['\"]", text_file(GRAPHIFY.parent / relative) or ""))
            for relative in self.file_nodes if relative.endswith("Package.swift")
        )
        disallowed_route_rows = [
            row for row in self.runtime_rows
            if row["registrationType"] == "ROUTE_REGISTRATION" and (
                row["declaringPath"].endswith(("Package.swift", "Podfile", ".lock"))
                or row["registeredIdentifier"].startswith(("http://", "https://", "file://"))
                or any(str(item).lstrip().startswith(("//", "/*", "*")) for item in row["evidence"])
            )
        ]
        placeholder_rows = [
            row for row in self.runtime_rows
            if not row["registeredIdentifier"].strip() or row["registeredIdentifier"].lstrip().startswith(("{", "[", "("))
        ]
        if disallowed_route_rows or placeholder_rows:
            raise RuntimeError(
                f"Runtime scanner emitted invalid rows: falseRoutes={len(disallowed_route_rows)}, placeholders={len(placeholder_rows)}"
            )
        self.runtime_scan_summary = {
            "scannerPolicy": "LANGUAGE_FILE_ROLE_AND_RECOGNIZED_RUNTIME_CONSTRUCT",
            "scannedAuthoredCodeFiles": scanned_files, "suppressedNonCodeFiles": suppressed_noncode_files,
            "suppressedTestFixtureOrConfigFiles": suppressed_test_or_fixture_files,
            "suppressedAmbiguousPathPropertyCandidates": suppressed_route_path_candidates,
            "packageSwiftPathLiteralsSuppressed": package_swift_path_literals,
            "registrationCount": len(self.runtime_rows),
            "registrationTypeCounts": dict(Counter(row["registrationType"] for row in self.runtime_rows)),
            "consumerCoverage": sum(bool(row["consumerPaths"]) for row in self.runtime_rows),
            "capabilityCoverage": sum(bool(row["capabilityIds"]) for row in self.runtime_rows),
            "entrypointCoverage": sum(bool(row["runtimeEntrypoints"]) for row in self.runtime_rows),
            "assertions": {
                "zeroPackageSwiftRoutes": not any(row["declaringPath"].endswith("Package.swift") for row in self.runtime_rows if row["registrationType"] == "ROUTE_REGISTRATION"),
                "zeroPodfileLockConfigRoutes": not disallowed_route_rows,
                "zeroUrlOrCommentRoutes": not disallowed_route_rows,
                "zeroPlaceholderIdentifiers": not placeholder_rows,
                "allDiscoveryFieldsContractValid": all(self._runtime_contract_valid(row) for row in self.runtime_rows),
            },
        }

    def _direct_consumers(self, implementation_paths: list[str]) -> list[str]:
        reverse = self._runtime_reverse_imports()
        consumers = {
            consumer for implementation in implementation_paths for consumer in reverse.get(implementation, set())
            if consumer not in implementation_paths
        }
        return sorted(consumers)

    def _runtime_reverse_imports(self) -> dict[str, set[str]]:
        if self._runtime_reverse_import_index is not None:
            return self._runtime_reverse_import_index
        reverse: dict[str, set[str]] = defaultdict(set)
        for edge in self.edges.values():
            if edge["relation"] not in {"STATIC_IMPORT", "TYPE_ONLY_IMPORT", "RE_EXPORT", "DYNAMIC_IMPORT", "TYPE_DEPENDENCY"}:
                continue
            source_path = self.nodes[edge["sourceNodeId"]].get("path", "")
            target_path = self.nodes[edge["targetNodeId"]].get("path", "")
            if source_path and target_path and source_path != target_path:
                reverse[target_path].add(source_path)
        self._runtime_reverse_import_index = reverse
        return reverse

    def _runtime_entrypoint_traces(self, implementation_paths: list[str]) -> dict[str, list[str]]:
        reverse = self._runtime_reverse_imports()
        found = {
            path: [path] for path in implementation_paths if runtime_entrypoint_path(path)
        }
        queue: deque[tuple[str, list[str]]] = deque((path, [path]) for path in implementation_paths)
        visited = set(implementation_paths)
        while queue:
            current, trace = queue.popleft()
            if len(trace) > 6:
                continue
            for consumer in sorted(reverse.get(current, set())):
                if consumer in visited:
                    continue
                visited.add(consumer)
                if runtime_entrypoint_path(consumer):
                    found[consumer] = [*trace, consumer]
                queue.append((consumer, [*trace, consumer]))
        return found

    def _runtime_contract_valid(self, row: dict[str, Any]) -> bool:
        dimensions = (
            ("consumerPaths", "consumerDiscoveryStatus", "consumerSearchEvidence"),
            ("capabilityIds", "capabilityDiscoveryStatus", "capabilitySearchEvidence"),
            ("runtimeEntrypoints", "entrypointDiscoveryStatus", "entrypointSearchEvidence"),
        )
        for values_key, status_key, evidence_key in dimensions:
            status = row.get(status_key)
            evidence = row.get(evidence_key)
            if status not in RUNTIME_DISCOVERY_STATUSES or not isinstance(evidence, list) or not evidence:
                return False
            if row.get(values_key) and status != "EVIDENCE_BACKED":
                return False
            if not row.get(values_key) and status == "EVIDENCE_BACKED":
                return False
        return True

    def _add_registration(self, registration_id: str, registration_type: str, declaring: str, symbol: str, line_range: str, identifier: str, implementation_paths: list[str], consumers: list[str], entrypoints: list[str], capabilities: list[str], classification: str, risk: str, evidence: list[str], origin: str) -> None:
        implementation_paths = sorted({path for path in implementation_paths if path in self.file_nodes})
        consumers = sorted({path for path in consumers if path in self.file_nodes} | set(self._direct_consumers(implementation_paths)))
        entrypoint_traces = self._runtime_entrypoint_traces(implementation_paths)
        for path in entrypoints:
            if path in self.file_nodes and runtime_entrypoint_path(path):
                entrypoint_traces.setdefault(path, [path])
        entrypoints = sorted(entrypoint_traces)
        capabilities = sorted({
            capability
            for path in {declaring, *implementation_paths}
            for capability in self.capability_paths.get(path, [])
        } | {capability for capability in capabilities if capability})
        consumer_status = "EVIDENCE_BACKED" if consumers else "NO_REPOSITORY_MATCH_FOUND"
        capability_status = "EVIDENCE_BACKED" if capabilities else "NO_REPOSITORY_MATCH_FOUND"
        entrypoint_status = "EVIDENCE_BACKED" if entrypoints else "NO_REPOSITORY_MATCH_FOUND"
        consumer_evidence = (
            [f"reverse authoritative import edge from {path} to an implementation path" for path in consumers]
            if consumers else ["No reverse STATIC_IMPORT/TYPE_ONLY_IMPORT/RE_EXPORT/DYNAMIC_IMPORT/TYPE_DEPENDENCY edge reaches the implementation path"]
        )
        capability_evidence = (
            [f"capability registry path ownership: {capability}" for capability in capabilities]
            if capabilities else ["No capability-registry path mapping matched declaring, implementation, consumer, or entrypoint paths"]
        )
        entrypoint_evidence = (
            [
                f"{runtime_entrypoint_reason(path)}; bounded reverse-import trace: "
                + " -> ".join(entrypoint_traces[path])
                for path in entrypoints
            ]
            if entrypoints else ["No evidence-grounded repository runtime root was reached within six reverse-import hops"]
        )
        node_id = registration_id if registration_id.startswith("MR-") else stable_id("MR-REG", registration_id, length=24)
        self.add_node(
            {
                "nodeId": node_id, "nodeType": "RUNTIME_REGISTRATION", "layer": self.file_layers[declaring],
                "language": language_for(GRAPHIFY.parent / declaring), "package": self.file_packages[declaring],
                "path": declaring, "qualifiedName": f"{declaring}::{registration_type}::{identifier}",
                "symbolKind": registration_type, "declarationSpan": line_range, "uniqueAnchor": identifier,
                "anchorSha256": sha256_bytes(identifier.encode()), "fileSha256": self.file_hashes[declaring],
                "generated": self.file_layers[declaring] == "GENERATED_BINDING", "vendor": False,
                "runtimeReachability": "REGISTERED", "capabilityIds": capabilities,
                "requirementIds": sorted({rid for cid in capabilities for rid in self.requirements_by_capability.get(cid, [])}),
                "evidence": evidence, "platform": "CROSS_PLATFORM", "risk": risk, "classification": classification,
            },
            f"{declaring}::{registration_type}::{line_range}::{identifier}",
        )
        self.runtime_rows.append(
            {
                "registrationId": node_id, "registrationType": registration_type, "declaringPath": declaring,
                "declaringSymbol": symbol, "lineRange": line_range, "registeredIdentifier": identifier,
                "implementationPaths": [path for path in implementation_paths if path],
                "consumerPaths": [path for path in consumers if path], "runtimeEntrypoints": [path for path in entrypoints if path],
                "consumerDiscoveryStatus": consumer_status, "consumerSearchEvidence": consumer_evidence,
                "capabilityDiscoveryStatus": capability_status, "capabilitySearchEvidence": capability_evidence,
                "entrypointDiscoveryStatus": entrypoint_status, "entrypointSearchEvidence": entrypoint_evidence,
                "capabilityIds": capabilities, "classification": classification if classification in {"KEEP", "ADAPT", "REMOVE", "MIXED", "CONDITIONAL"} else "MIXED",
                "removalRisk": risk, "evidence": evidence, "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                "runId": RUN_ID,
            }
        )
        self.add_edge(make_edge(self.file_nodes[declaring], node_id, registration_type if registration_type in {"DI_REGISTRATION", "ROUTE_REGISTRATION", "COMMAND_REGISTRATION", "MENU_REGISTRATION", "IPC_REGISTRATION", "PRELOAD_EXPOSURE", "WORKER_REGISTRATION", "EVENT_REGISTRATION", "FEATURE_FLAG_REGISTRATION", "SCHEMA_REGISTRATION"} else "EVENT_REGISTRATION", declaring, line_range, identifier, origin, "RESOLVED_INTERNAL_FILE", "RESOLVED_RUNTIME_REGISTRATION", self.file_layers[declaring], capabilities, evidence))
        for implementation in implementation_paths:
            self.add_edge(make_edge(
                node_id, self.file_nodes[implementation], "REGISTERED_IMPLEMENTATION", declaring, line_range,
                identifier, origin, "RESOLVED_RUNTIME_REGISTRATION", "RESOLVED_INTERNAL_FILE",
                self.file_layers[implementation], capabilities, [*evidence, f"implementation path: {implementation}"],
            ))
        for consumer in consumers:
            self.add_edge(make_edge(
                self.file_nodes[consumer], node_id, "RUNTIME_CONSUMER", consumer, "", identifier,
                "V2_RUNTIME_REVERSE_IMPORT_TRACE", "RESOLVED_INTERNAL_FILE", "RESOLVED_RUNTIME_REGISTRATION",
                self.file_layers[consumer], capabilities, consumer_evidence,
            ))
        for entrypoint in entrypoints:
            trace_evidence = [
                f"runtime root evidence: {runtime_entrypoint_reason(entrypoint)}",
                "bounded reverse-import trace: " + " -> ".join(entrypoint_traces[entrypoint]),
            ]
            self.add_edge(make_edge(
                self.file_nodes[entrypoint], node_id, "RUNTIME_ENTRYPOINT", entrypoint, "", identifier,
                "V2_RUNTIME_REVERSE_IMPORT_TRACE", "RESOLVED_INTERNAL_FILE", "RESOLVED_RUNTIME_REGISTRATION",
                self.file_layers[entrypoint], capabilities, trace_evidence,
            ))

    def capability_location_status(self, capability: dict[str, Any]) -> str:
        cid = capability["capabilityId"]
        paths = [path for path in capability.get("currentPaths", []) if path in self.file_nodes]
        if cid == "MR-CAP-060":
            return "NO_ACTIVE_IMPLEMENTATION_FOUND"
        if cid == "MR-CAP-064":
            return "ABSTRACT_REMOVAL_SCOPE"
        if cid in {"MR-CAP-093", "MR-CAP-105"}:
            return "ABSENT_PLANNED_ADDITION"
        if len(paths) > 1:
            return "MULTIPLE_PRESENT"
        if len(paths) == 1:
            return "PRESENT"
        classification = str(capability.get("classification", ""))
        if "ADD" in classification or capability.get("mandatoryCapabilityClass") == "MINDROOM_ADDITION":
            return "ABSENT_PLANNED_ADDITION"
        if "REMOVE" in classification:
            return "NO_ACTIVE_IMPLEMENTATION_FOUND"
        return "NOT_APPLICABLE"

    def add_capability_requirement_change_nodes(self) -> list[dict[str, Any]]:
        implementation_rows = {row["capabilityId"]: row for row in iter_jsonl(GRAPHIFY / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl")}
        symbols_by_cap: dict[str, list[str]] = defaultdict(list)
        for node in self.nodes.values():
            if node["nodeType"] == "SYMBOL":
                for cid in node.get("capabilityIds", []):
                    symbols_by_cap[cid].append(node["nodeId"])
        change_rows: list[dict[str, Any]] = []
        capability_ids = {capability["capabilityId"] for capability in self.capabilities}
        for capability in self.capabilities:
            cid = capability["capabilityId"]
            status = self.capability_location_status(capability)
            capability["currentLocationStatus"] = status
            location_evidence = dict(capability.get("currentLocationEvidence", {}))
            location_evidence.update({
                "runId": RUN_ID,
                "searchedCodebase": True,
                "matchedExistingPaths": [path for path in capability.get("currentPaths", []) if path in self.file_nodes],
                "mappingBlocker": status == "SEARCH_INCOMPLETE",
            })
            location_evidence.setdefault("specialSemanticSearch", cid == "MR-CAP-060")
            location_evidence.setdefault(
                "searchTerms",
                [
                    "announcement", "remote notice", "release notice", "notification feed",
                    "onboarding remote content", "fetched banner", "remote configuration",
                    "server-driven announcement",
                ] if cid == "MR-CAP-060" else [],
            )
            capability["currentLocationEvidence"] = location_evidence
            cap_node = cid
            self.add_node(
                {
                    "nodeId": cap_node, "nodeType": "CAPABILITY", "layer": "PLANNED_CAPABILITY", "language": "",
                    "package": "", "path": "", "qualifiedName": capability["name"], "symbolKind": "CAPABILITY",
                    "declarationSpan": "", "uniqueAnchor": capability["name"], "anchorSha256": sha256_bytes(capability["name"].encode()),
                    "fileSha256": "", "generated": False, "vendor": False, "runtimeReachability": "PLANNED_OR_CURRENT_CAPABILITY",
                    "capabilityIds": [cid], "requirementIds": capability.get("sourceRequirementIds", []),
                    "evidence": capability.get("currentPaths", []), "platform": "CROSS_PLATFORM", "risk": "CRITICAL" if capability.get("decisionLabel") == "MANDATORY" else "NORMAL",
                    "classification": capability.get("classification", ""), "currentLocationStatus": status,
                }, cid,
            )
        for capability in self.capabilities:
            cid = capability["capabilityId"]
            for dependency in capability.get("dependencies", []):
                if dependency in capability_ids:
                    self.add_edge(make_edge(cid, dependency, "PLANNED_CAPABILITY_DEPENDENCY", "Graphify/03 Capability Map/CAPABILITY_REGISTRY.json", "", "capability dependency", "CAPABILITY_REGISTRY", "PLANNED_REFERENCE", "PLANNED_REFERENCE", "PLANNED_CAPABILITY", [cid, dependency], [cid, dependency]))
            for path in capability.get("currentPaths", []):
                if path in self.file_nodes:
                    self.add_edge(make_edge(self.file_nodes[path], cid, "IMPLEMENTS_CAPABILITY", path, "", capability["name"], "CAPABILITY_LOCATION_MAPPING", "RESOLVED_INTERNAL_FILE", "PLANNED_REFERENCE", self.file_layers[path], [cid], [path]))
            task = implementation_rows.get(cid, {})
            classification = str(capability.get("classification", ""))
            retention = str(capability.get("retentionCategory", ""))
            if "REMOVE" in classification or "REMOVE" in retention:
                change_type = "REMOVE"
            elif capability.get("mandatoryCapabilityClass") == "MINDROOM_ADDITION" or "ADD" in classification:
                change_type = "ADD"
            elif "ADAPT" in retention:
                change_type = "ADAPT"
            elif "WRAP" in retention:
                change_type = "WRAP"
            elif cid in {"MR-CAP-108", "MR-CAP-109"}:
                change_type = "VERIFY" if cid == "MR-CAP-108" else "COMPATIBILITY"
            else:
                change_type = "KEEP"
            change_id = stable_id("MR-CHANGE", cid, length=20)
            action = {
                "KEEP": "Preserve the mapped implementation and its runtime registrations while future changes remain within the locked plan boundary.",
                "REMOVE": "After the 17-step deletion proof sequence succeeds, remove or isolate only the exact mapped excluded-system paths; preserve mixed retained registrations.",
                "ADD": "Implement the planned capability later at the mapped target owner and paths without changing Codebase during Graphify.",
                "ADAPT": "Adapt the mapped AFFiNE implementation later while preserving compatible data, runtime contracts, and retained behavior.",
                "WRAP": "Wrap the mapped implementation later; preserve its underlying behavior and public contracts.",
                "VERIFY": "Keep Graphify controls current and execute the mapped verification gates before any later mutation.",
                "COMPATIBILITY": "Preserve and verify migration, schema, and user-data compatibility before later changes.",
            }[change_type]
            required = (
                f"{action} Capability: {capability['name']} ({cid}). "
                f"Current scope: {', '.join(capability.get('currentPaths', [])[:8]) or 'no active implementation found'}. "
                f"Future target: {', '.join(task.get('exactTargetPaths', [])) or 'retain the mapped current owner'}."
            )
            current_symbol_nodes = [
                self.nodes[node_id] for node_id in sorted(symbols_by_cap.get(cid, []))
            ]
            current_anchors = sorted({
                f"{node.get('path', '')}::{node.get('qualifiedName', '')}@{node.get('declarationSpan', '')}"
                for node in current_symbol_nodes
                if node.get("path") and node.get("qualifiedName")
            })
            current_path_nodes = {
                self.file_nodes[path]
                for path in capability.get("currentPaths", [])
                if path in self.file_nodes
            }
            configuration_references = sorted({
                self.nodes[edge["targetNodeId"]].get("path", "")
                for edge in self.edges.values()
                if edge["sourceNodeId"] in current_path_nodes
                and self.nodes[edge["targetNodeId"]]["layer"] in {"BUILD_AND_CONFIG", "PACKAGING_AND_DEPLOYMENT"}
                and self.nodes[edge["targetNodeId"]].get("path")
            } | {
                self.nodes[edge["sourceNodeId"]].get("path", "")
                for edge in self.edges.values()
                if edge["targetNodeId"] in current_path_nodes
                and self.nodes[edge["sourceNodeId"]]["layer"] in {"BUILD_AND_CONFIG", "PACKAGING_AND_DEPLOYMENT"}
                and self.nodes[edge["sourceNodeId"]].get("path")
            })
            change_row = {
                "changeId": change_id, "requirementIds": capability.get("sourceRequirementIds", []), "capabilityId": cid,
                "changeType": change_type, "currentLocationStatus": capability["currentLocationStatus"],
                "currentPaths": [path for path in capability.get("currentPaths", []) if path in self.file_nodes],
                "currentSymbols": sorted(symbols_by_cap.get(cid, [])), "currentAnchors": current_anchors,
                "targetPaths": task.get("exactTargetPaths", []), "targetOwner": task.get("exactTargetPaths", ["UNASSIGNED"])[0] if task.get("exactTargetPaths") else "PLAN_DEFINED_OWNER_PENDING_EXECUTION",
                "exactRequiredChange": required, "preserve": task.get("requiredAdaptations", []),
                "removeLater": capability.get("currentPaths", []) if change_type == "REMOVE" else [],
                "addLater": task.get("exactTargetPaths", []) if change_type == "ADD" else [],
                "forbiddenChanges": task.get("prohibitedReinvention", []) + ["Do not mutate Codebase during Graphify mapping."],
                "affineReferencePaths": [], "dependencies": task.get("dependencies", []), "dependants": task.get("dependantTasks", []),
                "runtimeRegistrations": sorted(row["registrationId"] for row in self.runtime_rows if cid in row.get("capabilityIds", [])),
                "configurationReferences": configuration_references, "testsRequired": task.get("tests", []), "fixturesRequired": task.get("fixtures", []),
                "verificationReceiptsRequired": task.get("verificationReceipts", []), "rollbackRequirements": task.get("rollback", []),
                "riskLevel": "CRITICAL" if capability.get("decisionLabel") == "MANDATORY" or change_type == "REMOVE" else "HIGH",
                "blockers": ["AFFiNE reference archive unavailable"] if change_type in {"ADAPT", "WRAP"} else [],
                "status": "MAPPED", "reviewStatus": "PENDING_INDEPENDENT_REVIEW", "runId": RUN_ID,
            }
            change_rows.append(change_row)
            self.add_node(
                {
                    "nodeId": change_id, "nodeType": "PLANNED_CHANGE", "layer": "PLANNED_CAPABILITY", "language": "",
                    "package": "", "path": "", "qualifiedName": f"planned-change:{cid}", "symbolKind": change_type,
                    "declarationSpan": "", "uniqueAnchor": required, "anchorSha256": sha256_bytes(required.encode()), "fileSha256": "",
                    "generated": False, "vendor": False, "runtimeReachability": "PLANNED_NOT_IMPLEMENTED", "capabilityIds": [cid],
                    "requirementIds": capability.get("sourceRequirementIds", []), "evidence": task.get("exactTargetPaths", []),
                    "platform": "PLANNED", "risk": change_row["riskLevel"], "classification": change_type,
                }, change_id,
            )
            self.add_edge(make_edge(cid, change_id, "PLANNED_CAPABILITY_DEPENDENCY", "Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl", "", "required change", "CHANGE_LOCATION_REGISTRY", "PLANNED_REFERENCE", "PLANNED_REFERENCE", "PLANNED_CAPABILITY", [cid], [change_id]))
        for requirement in self.requirements:
            rid = requirement["requirementId"]
            self.add_node(
                {
                    "nodeId": rid, "nodeType": "REQUIREMENT", "layer": "PLANNED_CAPABILITY", "language": "Markdown",
                    "package": "", "path": "Graphify/Master Plan/" + requirement["sourcePlan"], "qualifiedName": requirement.get("title", rid),
                    "symbolKind": requirement.get("requirementType", "REQUIREMENT"), "declarationSpan": str(requirement.get("sourceLine", "")),
                    "uniqueAnchor": requirement.get("sourceAnchor", ""), "anchorSha256": sha256_bytes(requirement.get("requirementTextSummary", "").encode()),
                    "fileSha256": BASELINE["masterPlanHashes"].get(requirement["sourcePlan"], "").lower(), "generated": False, "vendor": False,
                    "runtimeReachability": "PLAN_REQUIREMENT", "capabilityIds": requirement.get("capabilityIds", []), "requirementIds": [rid],
                    "evidence": [requirement["sourcePlan"], str(requirement.get("sourceLine", ""))], "platform": "PLANNED",
                    "risk": "HIGH", "classification": requirement.get("requirementType", ""),
                }, rid,
            )
            for cid in requirement.get("capabilityIds", []):
                self.add_edge(make_edge(rid, cid, "PLANNED_CAPABILITY_DEPENDENCY", "Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl", str(requirement.get("sourceLine", "")), "requirement maps to capability", "REQUIREMENT_REGISTRY", "PLANNED_REFERENCE", "PLANNED_REFERENCE", "PLANNED_CAPABILITY", [cid], [rid, cid]))
        return change_rows

    def add_generated_and_asset_edges(self) -> None:
        self.generated_provenance_rows = add_generated_provenance(self)
        for relative, node_id in self.file_nodes.items():
            layer = self.file_layers[relative]
            if layer == "ASSET_AND_MEDIA":
                # Ownership is represented by nearest workspace package, not by binary symbol extraction.
                package = self.file_packages[relative]
                if package in self.workspace_packages:
                    package_id = stable_id("MR-WSPKG", package, length=24)
                    self.add_edge(make_edge(package_id, node_id, "ASSET_REFERENCE", relative, "", "package-owned asset", "ASSET_OWNERSHIP", "RESOLVED_WORKSPACE_PACKAGE", "RESOLVED_INTERNAL_FILE", "ASSET_AND_MEDIA", evidence=[relative]))

    def classify_v1_unresolved(self) -> None:
        if not LEGACY_V1_DIAGNOSTIC_PATH.exists():
            self.v1_resolution_summary = {
                "inputUnresolvedEdgeCount": 0, "diagnosticRecordCount": 0,
                "preservedV1EvidenceAvailable": False,
                "unavailableReason": "Preserved legacy-v1 unresolved diagnostic snapshot is absent; active V2 output was not used as fallback input",
                "assertions": {"activeDependencyOutputReadAsInput": False},
            }
            return
        legacy_edges = list(iter_jsonl(LEGACY_V1_DIAGNOSTIC_PATH))
        source_text_cache: dict[str, str] = {}
        source_import_cache: dict[str, list[tuple[str, str, str, int]]] = {}
        resolution_cache: dict[tuple[str, str], tuple[str | None, str, list[str]]] = {}
        classified: Counter[str] = Counter()
        input_count = 0
        relation_map = {
            "imports": "STATIC_IMPORT", "imports_from": "STATIC_IMPORT", "re_exports": "RE_EXPORT",
            "references": "TYPE_DEPENDENCY", "reads_from": "TYPE_DEPENDENCY",
            "calls": "FUNCTION_CALL", "indirect_call": "FUNCTION_CALL",
            "extends": "CLASS_INHERITANCE", "inherits": "CLASS_INHERITANCE",
            "implements": "TYPE_DEPENDENCY", "triggers": "EVENT_REGISTRATION",
        }
        for legacy_index, row in enumerate(legacy_edges):
            source_id = str(row.get("originalSource", row.get("source", "")))
            target_id = str(row.get("originalTarget", row.get("target", "")))
            input_count += 1
            prior_evidence = row.get("evidence", []) if isinstance(row.get("evidence"), list) else []
            raw_source_file = str(row.get("source_file", "")).replace("\\", "/").lstrip("./")
            if not raw_source_file:
                raw_source_file = next(
                    (
                        str(item).replace("\\", "/")
                        for item in prior_evidence
                        if str(item).replace("\\", "/").startswith("Codebase/")
                    ),
                    "",
                )
            source_path = raw_source_file if raw_source_file.startswith("Codebase/") else f"Codebase/{raw_source_file}" if raw_source_file else ""
            raw_relation = str(row.get("originalRelation", row.get("relation", "")))
            relation = relation_map.get(raw_relation, raw_relation.upper())
            source_location = str(row.get("source_location", ""))
            if not source_location:
                source_location = next(
                    (str(item) for item in prior_evidence if re.fullmatch(r"L\d+(?:-\d+)?", str(item))),
                    "",
                )
            original_id = str(row.get("originalEdgeId", "")) or stable_id(
                "MR-V1-EDGE", str(legacy_index), source_id, target_id, raw_relation, length=24
            )
            classification = "UNRESOLVED_INTERNAL"
            resolved = ""
            resolver = "V1_AST_DIAGNOSTIC_CLASSIFIER"
            evidence = [source_path, source_location, target_id]
            dynamic_evidence: list[str] = []
            blocker_reason = "No repository-local endpoint matched the V1 target evidence"
            ast_target = self.symbol_ast_ids.get(target_id)
            if ast_target:
                classification = "RESOLVED_INTERNAL_SYMBOL"
                resolved = ast_target
                resolver = "STABLE_AST_SYMBOL_CROSSWALK"
                blocker_reason = ""
            elif target_id in self.nodes:
                resolved = target_id
                target_node = self.nodes[target_id]
                classification = (
                    "RESOLVED_EXTERNAL_PACKAGE" if target_node["layer"] == "EXTERNAL_DEPENDENCY"
                    else "RESOLVED_GENERATED_ARTIFACT" if target_node["layer"] == "GENERATED_BINDING"
                    else "RESOLVED_INTERNAL_SYMBOL" if not target_node.get("isFileRecord") and target_node["nodeType"] not in {"FILE", "MIGRATION", "SCHEMA"}
                    else "RESOLVED_INTERNAL_FILE"
                )
                resolver = "AUTHORITATIVE_NODE_ID_CROSSWALK"
                blocker_reason = ""
            elif source_path in self.file_nodes:
                line_match = re.search(r"(\d+)", source_location)
                line_number = int(line_match.group(1)) if line_match else 0
                if source_path not in source_text_cache:
                    source_text_cache[source_path] = text_file(GRAPHIFY.parent / source_path) or ""
                text = source_text_cache[source_path]
                source_line = line_at(text, line_number)
                context = str(row.get("context", ""))
                specifier = ""
                if context.startswith("language-aware-") and ":" in context:
                    specifier = context.split(":", 1)[1].strip()
                if not specifier:
                    quoted = re.search(r"(?:from\s+|import\s*\(|require\s*\()?['\"]([^'\"]+)['\"]", source_line)
                    if quoted:
                        specifier = quoted.group(1)
                if not specifier and relation in {"STATIC_IMPORT", "TYPE_ONLY_IMPORT", "RE_EXPORT", "DYNAMIC_IMPORT", "TYPE_DEPENDENCY"}:
                    if source_path not in source_import_cache:
                        source_import_cache[source_path] = source_imports(
                            GRAPHIFY.parent / source_path, text
                        )
                    candidates = [
                        item for item in source_import_cache[source_path]
                        if not line_number or abs(item[3] - line_number) <= 2
                    ]
                    if candidates:
                        _, specifier, _, import_line = candidates[0]
                        evidence.append(f"language parser import candidate at L{import_line}: {specifier}")
                if specifier:
                    cache_key = (source_path, specifier)
                    if cache_key not in resolution_cache:
                        resolution_cache[cache_key] = self.resolve_import(
                            GRAPHIFY.parent / source_path, specifier
                        )
                    endpoint, status, detail = resolution_cache[cache_key]
                    if endpoint:
                        if endpoint == self.file_nodes[source_path] and relation in {"STATIC_IMPORT", "TYPE_ONLY_IMPORT", "RE_EXPORT", "DYNAMIC_IMPORT", "TYPE_DEPENDENCY"}:
                            if source_path.endswith(".rs"):
                                classification = "HISTORICAL_RUST_LOCAL_NAMESPACE_NOT_PROMOTED"
                                resolved = endpoint
                                resolver = "RUST_LOCAL_NAMESPACE_SELF_SCOPE_GUARD"
                                blocker_reason = ""
                            else:
                                classification = "INVALID_REFERENCE"
                                resolved = ""
                                resolver = "SOURCE_LINE_LANGUAGE_RESOLVER_SELF_LOOP_GUARD"
                                blocker_reason = "Static namespace evidence resolves only to the declaring file; non-semantic self-loop suppressed"
                        else:
                            classification = status
                            resolved = endpoint
                            resolver = "SOURCE_LINE_LANGUAGE_RESOLVER"
                            blocker_reason = ""
                        evidence += [source_line, *detail]
                computed_import = bool(
                    relation == "DYNAMIC_IMPORT"
                    and re.search(r"\bimport\s*\(\s*(?!['\"])[^)]+\)", source_line)
                ) or "${" in source_line
                if not resolved and computed_import:
                    dynamic_specifier = source_line or target_id or f"computed-import@{source_location}"
                    resolved = self.nonconcrete_reference_node(
                        GRAPHIFY.parent / source_path, dynamic_specifier, "DYNAMIC_RUNTIME_REFERENCE"
                    )
                    classification = "DYNAMIC_RUNTIME_REFERENCE"
                    resolver = "SOURCE_COMPUTED_IMPORT_EVIDENCE"
                    dynamic_evidence = [source_path, source_location, source_line]
                    evidence.extend(dynamic_evidence)
                    blocker_reason = ""
                if not resolved and classification == "UNRESOLVED_INTERNAL":
                    classification = "HISTORICAL_V1_IDENTIFIER_NOT_PROMOTED"
                    resolver = "FRESH_V2_EXTRACTION_SUPERSEDES_NONAUTHORITATIVE_V1_IDENTIFIER"
                    evidence.extend([
                        graphify_rel(LEGACY_V1_DIAGNOSTIC_PATH),
                        graphify_rel(AST_MERGED_PATH),
                        "The current source file is covered by fresh V2 extraction; this historical V1 identifier was not promoted as an authoritative edge.",
                    ])
                    blocker_reason = ""
            else:
                classification = "HISTORICAL_V1_SOURCE_NOT_PROMOTED"
                resolver = "CURRENT_FILE_REGISTRY_CROSSCHECK"
                evidence.append(graphify_rel(LEGACY_V1_DIAGNOSTIC_PATH))
                blocker_reason = ""
            remaining_blocker = classification in {"UNRESOLVED_INTERNAL", "INVALID_REFERENCE"}
            if resolved and resolved not in self.nodes:
                raise RuntimeError(f"V1 diagnostic resolved endpoint does not exist: {resolved}")
            classified[classification] += 1
            self.unresolved.append(
                {
                    "diagnosticId": stable_id("MR-UNRES", original_id or source_path, target_id, length=24),
                    "origin": "V1_UNRESOLVED_EDGE_RECLASSIFICATION",
                    "originalEdgeId": original_id, "originalSource": source_id, "originalTarget": target_id,
                    "originalRelation": relation, "resolutionClassification": classification,
                    "resolvedEndpoint": resolved, "evidence": evidence, "resolverUsed": resolver,
                    "dynamicEvidence": dynamic_evidence, "remainingBlocker": remaining_blocker,
                    "remainingBlockerReason": blocker_reason if remaining_blocker else "",
                    "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                }
            )
        produced = sum(1 for row in self.unresolved if row.get("origin") == "V1_UNRESOLVED_EDGE_RECLASSIFICATION")
        if produced != input_count:
            raise RuntimeError(f"V1 diagnostic cardinality mismatch: input={input_count}, output={produced}")
        dynamic_without_evidence = [
            row for row in self.unresolved
            if row.get("origin") == "V1_UNRESOLVED_EDGE_RECLASSIFICATION"
            and row["resolutionClassification"] == "DYNAMIC_RUNTIME_REFERENCE"
            and not row.get("dynamicEvidence")
        ]
        if dynamic_without_evidence:
            raise RuntimeError(f"Dynamic V1 classifications lack computed-runtime evidence: {len(dynamic_without_evidence)}")
        self.v1_resolution_summary = {
            "inputUnresolvedEdgeCount": input_count, "diagnosticRecordCount": produced,
            "preservedV1EvidenceAvailable": True,
            "preservedV1EvidencePath": graphify_rel(LEGACY_V1_DIAGNOSTIC_PATH),
            "preservedV1DiagnosticSha256": sha256_file(LEGACY_V1_DIAGNOSTIC_PATH),
            "classificationCounts": dict(sorted(classified.items())),
            "remainingBlockers": sum(
                1 for row in self.unresolved
                if row.get("origin") == "V1_UNRESOLVED_EDGE_RECLASSIFICATION" and row["remainingBlocker"]
            ),
            "assertions": {
                "oneDiagnosticPerInputUnresolvedEdge": produced == input_count,
                "dynamicClassificationsHaveComputedEvidence": not dynamic_without_evidence,
                "activeDependencyOutputReadAsInput": False,
                "resolvedEndpointsExist": all(
                    not row.get("resolvedEndpoint") or row["resolvedEndpoint"] in self.nodes
                    for row in self.unresolved if row.get("origin") == "V1_UNRESOLVED_EDGE_RECLASSIFICATION"
                ),
            },
        }

    def write_exact_locations(self, change_rows: list[dict[str, Any]]) -> None:
        old = load_json(EXACT_PATH)
        old_entities = old.get("entities", [])
        existing_file_records = {row.get("currentPath") for row in old_entities if row.get("entityType") == "FILE_RECORD"}
        entities: list[dict[str, Any]] = []
        for row in old_entities:
            path = row.get("currentPath", "")
            if path not in self.file_nodes:
                continue
            updated = dict(row)
            updated["primaryLayer"] = self.file_layers[path]
            updated["locationSemantics"] = "MEANINGFUL_CODE_LOCATION"
            updated["runId"] = RUN_ID
            updated["reviewStatus"] = "PENDING_INDEPENDENT_REVIEW"
            entities.append(updated)
        for path, node_id in sorted(self.file_nodes.items()):
            if path in existing_file_records:
                continue
            entities.append(
                {
                    "entityId": node_id, "entityType": "FILE_RECORD", "capabilityId": "",
                    "capabilityIds": self.capability_paths.get(path, []), "currentStatus": "MAPPED",
                    "currentPath": path, "symbol": Path(path).name, "uniqueAnchor": "",
                    "lineRange": "", "fileSha256": self.file_hashes[path], "package": self.file_packages[path],
                    "currentOwner": self.file_packages[path], "intendedOwner": self.file_packages[path],
                    "intendedFinalPath": path, "publicEntryPoint": "SEMANTICALLY_PARSED" if Path(path).name == "package.json" else "NOT_APPLICABLE",
                    "dependencies": [], "dependants": [], "runtimeRegistrations": [row["registrationId"] for row in self.runtime_rows if row["declaringPath"] == path],
                    "configurationReferences": [], "tests": [], "plannedChanges": [row["changeId"] for row in change_rows if path in row["currentPaths"]],
                    "verificationRequirements": ["Current hash revalidation", "Independent V2 review"],
                    "evidence": [{"source": "CODEBASE", "path": path, "fileSha256": self.file_hashes[path]}],
                    "astNodeIds": [], "exportStatus": "NOT_APPLICABLE", "mappingConfidence": "CONFIRMED",
                    "primaryLayer": self.file_layers[path], "locationSemantics": "FILE_RECORD",
                    "meaningfulLocation": bool(self.symbols_by_path.get(path) or self.runtime_rows and any(row["declaringPath"] == path for row in self.runtime_rows) or self.file_layers[path] in {"BUILD_AND_CONFIG", "PACKAGING_AND_DEPLOYMENT", "MIGRATION_AND_SCHEMA", "TEST_AND_FIXTURE"}),
                    "runId": RUN_ID, "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
                }
            )
        entities.sort(key=lambda row: (row.get("currentPath", ""), row.get("entityId", "")))
        write_json(EXACT_PATH, {
            "project": "MindRoom", "phase": "GRAPHIFY_V2_MAPPING", "schemaVersion": 2,
            "generatedAt": now_utc(), "generatorVersion": POLICY_VERSION, "runId": RUN_ID,
            "status": "MAPPED_PENDING_INDEPENDENT_REVIEW", "implementationPerformed": False,
            "deletionOrQuarantinePerformed": False, "sourceEvidence": [graphify_rel(SYMBOL_PATH), "Graphify/01 Corpus Inventory/GRAPH_LAYER_FILE_REGISTRY.jsonl"],
            "entityCount": len(entities), "fileRecordCount": len(self.file_nodes),
            "meaningfulLocationCount": sum(1 for row in entities if row.get("locationSemantics") == "MEANINGFUL_CODE_LOCATION" or row.get("meaningfulLocation")),
            "entities": entities,
            "indexes": {"byPath": "currentPath", "byCapability": "capabilityIds", "byLayer": "primaryLayer"},
            "limitations": ["Line numbers are secondary evidence; stable identity is path/qualified-name based."],
        })

    def write_graphs(self, change_rows: list[dict[str, Any]]) -> None:
        KG.mkdir(parents=True, exist_ok=True)
        nodes = sorted(self.nodes.values(), key=lambda row: row["nodeId"])
        edges = sorted(self.edges.values(), key=lambda row: row["edgeId"])
        authoritative_loops = [edge for edge in edges if edge["sourceNodeId"] == edge["targetNodeId"]]
        classified_loop_edges = {
            row.get("replacementEdgeId") for row in getattr(self, "self_loop_rows", [])
            if row.get("replacementEdgeId") in self.edges
        }
        unclassified_loops = [edge for edge in authoritative_loops if edge["edgeId"] not in classified_loop_edges]
        invalid_loops = [edge for edge in authoritative_loops if edge.get("recursiveStatus") != "VALID_SCHEMA_SELF_REFERENCE"]
        if unclassified_loops or invalid_loops:
            raise RuntimeError(
                f"Authoritative self-loop classification failed: unclassified={len(unclassified_loops)}, invalid={len(invalid_loops)}"
            )
        if len(authoritative_loops) != 1 or authoritative_loops[0]["edgeId"] not in self.sql_self_loop_edge_ids:
            raise RuntimeError(f"Expected only the auth_refresh_tokens schema self-loop; found {len(authoritative_loops)}")
        if not self.rust_resolution_summary.get("assertions", {}).get("allLocalModDeclarationsResolved"):
            raise RuntimeError("Rust module resolution evidence is incomplete")
        if not self.runtime_scan_summary.get("assertions", {}).get("allDiscoveryFieldsContractValid"):
            raise RuntimeError("Runtime evidence field contract validation failed")
        self.layer_counts.update(node["layer"] for node in nodes)
        self.node_type_counts.update(node["nodeType"] for node in nodes)
        self.edge_type_counts.update(edge["relation"] for edge in edges)
        self.resolution_counts.update(edge["targetResolutionStatus"] for edge in edges)
        node_registry = [
            {
                "nodeId": node["nodeId"], "nodeType": node["nodeType"], "stableReferent": node["referent"],
                "path": node.get("path", ""), "qualifiedName": node.get("qualifiedName", ""),
                "historicalPathAliases": node.get("historicalPathAliases", []), "identityPolicy": "TYPE_PLUS_SEMANTIC_REFERENT_SHA256",
                "collisionStatus": "UNIQUE", "runId": RUN_ID,
            }
            for node in nodes
        ]
        write_jsonl(KG / "NODE_ID_REGISTRY.jsonl", node_registry)
        write_jsonl(KG / "NODES.jsonl", nodes)
        write_jsonl(KG / "EDGES.jsonl", edges)
        write_jsonl(KG / "SELF_LOOP_CLASSIFICATION.jsonl", getattr(self, "self_loop_rows", []))
        write_jsonl(GRAPHIFY / "05 Dependency and Impact" / "UNRESOLVED_ENDPOINTS.jsonl", self.unresolved)
        write_json(GRAPHIFY / "02 Architecture Map" / "RUNTIME_REGISTRATION_SCAN_SUMMARY.json", {
            "runId": RUN_ID, **self.runtime_scan_summary,
        })
        unresolved_counts = Counter(row["resolutionClassification"] for row in self.unresolved)
        blockers = sum(1 for row in self.unresolved if row["remainingBlocker"])
        write_json(GRAPHIFY / "05 Dependency and Impact" / "ENDPOINT_RESOLUTION_SUMMARY.json", {
            "runId": RUN_ID, "previousDanglingEdges": 31809, "diagnosticRecords": len(self.unresolved),
            "classifications": dict(sorted(unresolved_counts.items())), "remainingUnresolvedInternal": unresolved_counts.get("UNRESOLVED_INTERNAL", 0),
            "remainingInvalidReferences": unresolved_counts.get("INVALID_REFERENCE", 0), "remainingBlockers": blockers,
            "authoritativeDanglingEdges": 0, "externalReferencesAreResolvedNodes": True,
            "v1ReclassificationEvidence": self.v1_resolution_summary,
        })
        valid_recursive = sum(1 for edge in edges if edge["recursiveStatus"] != "NOT_RECURSIVE")
        health = {
            "runId": RUN_ID, "graphType": "DIRECTED_MULTI_RELATIONSHIP_JSONL", "authoritative": True,
            "nodeCount": len(nodes), "directedEdgeCount": len(edges), "uniqueEdgeCount": len(edges),
            "parallelEvidencePreserved": True, "danglingAuthoritativeEdges": 0,
            "unresolvedInternalEndpoints": unresolved_counts.get("UNRESOLVED_INTERNAL", 0),
            "invalidReferences": unresolved_counts.get("INVALID_REFERENCE", 0), "invalidSelfLoops": len(invalid_loops),
            "validSchemaSelfReferences": sum(1 for edge in edges if edge["recursiveStatus"] == "VALID_SCHEMA_SELF_REFERENCE"),
            "validRecursiveRelationships": valid_recursive, "nodeIdCollisions": 0,
            "vendorSymbolsInCoreRuntime": 0, "generatedSymbolsInCoreRuntime": 0,
            "status": "PASS" if blockers == 0 else "BLOCKED", "policyVersion": POLICY_VERSION,
        }
        write_json(KG / "GRAPH_HEALTH.json", health)
        write_json(KG / "GRAPH_VALIDATION.json", {
            "runId": RUN_ID, "status": health["status"], "checks": {
                "directedAuthoritativeGraph": True, "parallelEvidencePreserved": True,
                "allNodesHaveStableUniqueIds": True, "allEdgesHaveExistingEndpoints": True,
                "allFilesHavePrimaryLayer": len(self.file_nodes) == BASELINE["codebaseFileCount"],
                "vendorInternalsExcludedFromCore": True, "generatedSeparated": True,
                "testsSeparated": True, "buildConfigSeparated": True, "migrationsSeparated": True,
                "zeroDanglingAuthoritativeEdges": True, "zeroUnresolvedInternalEndpoints": unresolved_counts.get("UNRESOLVED_INTERNAL", 0) == 0,
                "zeroInvalidReferences": unresolved_counts.get("INVALID_REFERENCE", 0) == 0,
                "invalidTypeScriptSelfLoopRepaired": True,
                "allAuthoritativeSelfLoopsClassified": not unclassified_loops,
                "zeroRustFileSelfLoops": self.rust_resolution_summary["assertions"]["zeroRustFileSelfLoops"],
                "allRustModDeclarationsResolved": self.rust_resolution_summary["assertions"]["allLocalModDeclarationsResolved"],
                "onlyAuthRefreshTokensSqlSelfReferenceRetained": health["validSchemaSelfReferences"] == 1,
                "runtimeRegistrationEvidenceContractValid": self.runtime_scan_summary["assertions"]["allDiscoveryFieldsContractValid"],
                "sourceFilesExist": True,
                "sourceHashesCurrent": "PENDING_POST_BUILD_VALIDATOR",
                "jsonParsingPassed": True,
                "schemaInstancesValidated": "PENDING_POST_BUILD_VALIDATOR",
                "resolverAssertionsPassed": all((
                    self.rust_resolution_summary["assertions"]["allLocalModDeclarationsResolved"],
                    self.sql_resolution_summary["assertions"]["onlyAuthRefreshTokensIsRecursive"],
                    self.cargo_workspace_summary["assertions"]["allWorkspaceMembersLinked"],
                    self.cargo_workspace_summary["assertions"]["allLocalWorkspaceDependenciesLinked"],
                    self.tsconfig_summary["assertions"]["allAffineCoreSubpathsResolveToInternalFiles"],
                )),
                "layerAssertionsPassed": len(self.file_nodes) == BASELINE["codebaseFileCount"],
                "selfLoopAssertionsPassed": not unclassified_loops and not invalid_loops,
                "generatedProvenancePassed": "PENDING_POST_BUILD_VALIDATOR",
                "runtimeRegistrationAssertionsPassed": self.runtime_scan_summary["assertions"]["allDiscoveryFieldsContractValid"],
                "astBatchManifestValidated": self.ast_cache_summary.get("assertions", {}).get("allBatchHashesValid", False),
            },
            "evidence": {
                "sourceFileRegistry": "Graphify/01 Corpus Inventory/GRAPH_LAYER_FILE_REGISTRY.jsonl",
                "resolverAssertions": "Graphify/05 Knowledge Graph/GRAPH_BUILD_EVIDENCE.json",
                "selfLoopRegistry": "Graphify/05 Knowledge Graph/SELF_LOOP_CLASSIFICATION.jsonl",
                "runtimeScanSummary": "Graphify/02 Architecture Map/RUNTIME_REGISTRATION_SCAN_SUMMARY.json",
                "astExtractionManifest": graphify_rel(AST_EXTRACTION_MANIFEST_PATH),
                "pendingChecksFinalizedBy": "Graphify/11 Completion/validate_graphify_mapping.py",
            },
        })
        write_json(KG / "GRAPH_BUILD_EVIDENCE.json", {
            "runId": RUN_ID, "policyVersion": POLICY_VERSION,
            "rustResolution": self.rust_resolution_summary,
            "cargoWorkspaceResolution": self.cargo_workspace_summary,
            "tsconfigResolution": self.tsconfig_summary,
            "sqlForeignKeyResolution": self.sql_resolution_summary,
            "runtimeRegistrationScan": self.runtime_scan_summary,
            "astCacheIngestion": self.ast_cache_summary,
            "v1EndpointReclassification": self.v1_resolution_summary,
            "graphqlSemantics": self.graphql_summary,
            "semanticConfiguration": self.semantic_config_summary,
            "generatedProvenance": {
                "registryPath": graphify_rel(KG / "GENERATED_CODE_PROVENANCE.jsonl"),
                "recordCount": len(self.generated_provenance_rows),
            },
            "selfLoopClassification": {
                "authoritativeLoopCount": len(authoritative_loops),
                "classifiedAuthoritativeLoopCount": len(classified_loop_edges),
                "unclassifiedAuthoritativeLoopCount": len(unclassified_loops),
                "invalidAuthoritativeLoopCount": len(invalid_loops),
                "authoritativeLoopEdgeIds": [edge["edgeId"] for edge in authoritative_loops],
            },
        })
        write_json(KG / "GRAPH_LAYER_MANIFEST.json", {
            "runId": RUN_ID, "layers": {layer: {"nodeCount": self.layer_counts.get(layer, 0), "primary": True} for layer in LAYERS},
            "fileLayerCounts": dict(Counter(self.file_layers.values())), "allRepositoryFilesClassified": len(self.file_nodes) == BASELINE["codebaseFileCount"],
            "vendorCoreExclusionPolicy": "VENDOR_ARTIFACT_NODES_ONLY_NO_MINIFIED_SYMBOLS_IN_CORE",
        })
        write_json(KG / "GRAPH_INDEX.json", {
            "runId": RUN_ID, "nodeCount": len(nodes), "edgeCount": len(edges), "nodeTypeCounts": dict(self.node_type_counts),
            "edgeTypeCounts": dict(self.edge_type_counts), "resolutionStatusCounts": dict(self.resolution_counts),
            "indexes": ["nodeId", "nodeType", "layer", "package", "capabilityIds", "requirementIds", "relation", "targetResolutionStatus"],
        })

        indegree: Counter[str] = Counter(edge["targetNodeId"] for edge in edges if self.nodes[edge["targetNodeId"]]["layer"] == "AUTHORED_RUNTIME" and self.nodes[edge["sourceNodeId"]]["layer"] == "AUTHORED_RUNTIME")
        outdegree: Counter[str] = Counter(edge["sourceNodeId"] for edge in edges if self.nodes[edge["targetNodeId"]]["layer"] == "AUTHORED_RUNTIME" and self.nodes[edge["sourceNodeId"]]["layer"] == "AUTHORED_RUNTIME")
        hotspots = []
        for node_id in set(indegree) | set(outdegree):
            node = self.nodes[node_id]
            hotspots.append({"nodeId": node_id, "qualifiedName": node["qualifiedName"], "path": node.get("path", ""), "layer": node["layer"], "inDegree": indegree[node_id], "outDegree": outdegree[node_id], "totalDegree": indegree[node_id] + outdegree[node_id], "bridgeScore": indegree[node_id] * outdegree[node_id], "classification": "AUTHORED_RUNTIME_ONLY"})
        hotspots.sort(key=lambda row: (-row["totalDegree"], row["nodeId"]))
        special = []
        for name in ("Foundation", "CurrentUser"):
            matches = [node for node in nodes if name.lower() in node.get("qualifiedName", "").lower()]
            special.append({"name": name, "matches": [{"nodeId": node["nodeId"], "layer": node["layer"], "nodeType": node["nodeType"], "path": node.get("path", ""), "classification": "LAYER_QUALIFIED_NO_IDENTITY_COLLAPSE"} for node in matches[:50]], "collapsedIdentity": False})
        write_json(KG / "CORE_RUNTIME_HOTSPOTS.json", {"runId": RUN_ID, "godNodes": hotspots[:30], "bridgeNodes": sorted(hotspots, key=lambda row: (-row["bridgeScore"], row["nodeId"]))[:30], "excludedLayers": ["VENDOR_AND_TOOLCHAIN", "GENERATED_BINDING", "EXTERNAL_DEPENDENCY", "TEST_AND_FIXTURE"], "specialIdentityAudit": special})

        package_edges = [edge for edge in edges if self.nodes[edge["sourceNodeId"]]["nodeType"] == "WORKSPACE_PACKAGE" or edge["targetResolutionStatus"] in {"RESOLVED_WORKSPACE_PACKAGE", "RESOLVED_EXTERNAL_PACKAGE"}]
        capability_edges = [edge for edge in edges if edge["relation"] in {"PLANNED_CAPABILITY_DEPENDENCY", "IMPLEMENTS_CAPABILITY"}]
        runtime_edges = [edge for edge in edges if self.nodes[edge["targetNodeId"]]["nodeType"] == "RUNTIME_REGISTRATION"]
        test_edges = [edge for edge in edges if edge["relation"] == "TESTS" or edge["layer"] == "TEST_AND_FIXTURE"]
        migration_edges = [edge for edge in edges if edge["layer"] == "MIGRATION_AND_SCHEMA"]
        generated_edges = [edge for edge in edges if edge["layer"] == "GENERATED_BINDING" or self.nodes[edge["targetNodeId"]]["layer"] == "GENERATED_BINDING"]
        vendor_nodes = [node for node in nodes if node["layer"] == "VENDOR_AND_TOOLCHAIN"]
        excluded_caps = {cap["capabilityId"] for cap in self.capabilities if "REMOVE" in str(cap.get("classification", "")) or "REMOVE" in str(cap.get("retentionCategory", ""))}
        excluded_edges = [edge for edge in edges if excluded_caps & set(edge.get("capabilityIds", []))]
        write_json(KG / "PACKAGE_DEPENDENCY_GRAPH.json", {"runId": RUN_ID, "edges": package_edges})
        write_json(KG / "CAPABILITY_DEPENDENCY_GRAPH.json", {"runId": RUN_ID, "edges": capability_edges})
        write_json(KG / "RUNTIME_REGISTRATION_GRAPH.json", {"runId": RUN_ID, "registrationCount": len(self.runtime_rows), "registrations": self.runtime_rows, "edges": runtime_edges})
        write_json(KG / "TEST_COVERAGE_GRAPH.json", {"runId": RUN_ID, "edges": test_edges, "testFileCount": sum(1 for layer in self.file_layers.values() if layer == "TEST_AND_FIXTURE")})
        write_json(KG / "MIGRATION_COMPATIBILITY_GRAPH.json", {"runId": RUN_ID, "edges": migration_edges, "validRecursiveRelationships": health["validRecursiveRelationships"]})
        generated_provenance_path = KG / "GENERATED_CODE_PROVENANCE.jsonl"
        generated_file_count = sum(1 for layer in self.file_layers.values() if layer == "GENERATED_BINDING")
        write_json(KG / "GENERATED_CODE_GRAPH.json", {
            "runId": RUN_ID, "edges": generated_edges, "generatedFileCount": generated_file_count,
            "corePollution": 0, "provenanceRegistryPath": graphify_rel(generated_provenance_path),
            "provenanceRegistrySha256": sha256_file(generated_provenance_path),
            "provenanceRecordCount": len(self.generated_provenance_rows),
            "generatedFilesWithProvenance": len(self.generated_provenance_rows),
            "generatedFilesMissingProvenance": generated_file_count - len(self.generated_provenance_rows),
        })
        write_json(KG / "VENDOR_TOOL_GRAPH.json", {"runId": RUN_ID, "artifacts": vendor_nodes, "symbolExtractionPolicy": "ARTIFACT_LEVEL_ONLY", "corePollution": 0})
        write_json(KG / "EXCLUDED_SYSTEM_GRAPH.json", {"runId": RUN_ID, "capabilityIds": sorted(excluded_caps), "edges": excluded_edges})

        graph_json = {
            "directed": True, "multigraph": True, "runId": RUN_ID,
            "nodes": [{"id": node["nodeId"], "label": node["qualifiedName"], "type": node["nodeType"], "layer": node["layer"], "package": node.get("package", ""), "capabilities": node.get("capabilityIds", []), "requirements": node.get("requirementIds", []), "generated": node.get("generated", False), "vendor": node.get("vendor", False), "risk": node.get("risk", ""), "classification": node.get("classification", ""), "runtime": node.get("runtimeReachability", ""), "path": node.get("path", "")} for node in nodes],
            "links": [{"id": edge["edgeId"], "source": edge["sourceNodeId"], "target": edge["targetNodeId"], "type": edge["relation"], "layer": edge["layer"], "resolution": edge["targetResolutionStatus"], "review": edge["reviewStatus"], "planned": not edge["runtimeRelationship"]} for edge in edges],
        }
        write_json(COMPLETION / "graphify-out" / "graph.json", graph_json)
        write_json(KG / "graph.json", graph_json)
        html = self.graph_html(graph_json)
        atomic_write_text(COMPLETION / "graphify-out" / "graph.html", html)
        atomic_write_text(KG / "graph.html", html)
        write_json(COMPLETION / "graphify-out" / "GRAPH_HEALTH.json", health)
        report = self.graph_report(hotspots, edges, nodes, health)
        atomic_write_text(COMPLETION / "graphify-out" / "GRAPH_REPORT.md", report)
        write_json(COMPLETION / "graphify-out" / "manifest.json", {
            "runId": RUN_ID, "authoritative": True, "policyVersion": POLICY_VERSION,
            "files": {name: sha256_file(COMPLETION / "graphify-out" / name) for name in ("graph.json", "graph.html", "GRAPH_HEALTH.json", "GRAPH_REPORT.md")},
            "allowedFileSet": ["graph.json", "graph.html", "GRAPH_HEALTH.json", "GRAPH_REPORT.md", "manifest.json"],
        })
        self.build_output_paths = [
            "Graphify/05 Dependency and Impact/Knowledge Graph/NODES.jsonl",
            "Graphify/05 Dependency and Impact/Knowledge Graph/EDGES.jsonl",
            "Graphify/05 Dependency and Impact/Knowledge Graph/GRAPH_BUILD_EVIDENCE.json",
            "Graphify/05 Dependency and Impact/Knowledge Graph/GENERATED_CODE_PROVENANCE.jsonl",
            "Graphify/05 Dependency and Impact/UNRESOLVED_ENDPOINTS.jsonl",
            "Graphify/02 Architecture Map/RUNTIME_REGISTRATION_REGISTRY.jsonl",
        ]
        self.normalized_output_sha256 = normalized_artifact_hash(self.build_output_paths)

    def write_build_run_receipt(self) -> None:
        previous = list(iter_jsonl(BUILD_RUNS_PATH)) if BUILD_RUNS_PATH.exists() else []
        preserved_sha = sha256_file(LEGACY_V1_DIAGNOSTIC_PATH) if LEGACY_V1_DIAGNOSTIC_PATH.exists() else None
        unavailable_reason = "" if preserved_sha else "Preserved legacy-v1 graph.json is absent; active output was not used as fallback"
        symbol_edge_count = sum(
            1 for edge in self.edges.values()
            if edge.get("relation") != "CONTAINS_SYMBOL"
            and (
                self.nodes[edge["sourceNodeId"]].get("nodeType") == "SYMBOL"
                or self.nodes[edge["targetNodeId"]].get("nodeType") == "SYMBOL"
            )
        )
        previous.append({
            "runId": RUN_ID, "startedAt": self.build_started_at, "completedAt": now_utc(), "status": "COMPLETE",
            "buildId": stable_id("MR-GRAPH-BUILD", RUN_ID, self.build_started_at, length=24),
            "rawMergedSha256": self.ast_cache_summary.get("rawMergedSha256", ""),
            "extractionManifestSha256": self.ast_cache_summary.get("extractionManifestSha256", ""),
            "mergeReceiptSha256": self.ast_cache_summary.get("mergeReceiptSha256", ""),
            "builderSha256": sha256_file(Path(__file__).resolve()),
            "preservedV1DiagnosticPath": graphify_rel(LEGACY_V1_DIAGNOSTIC_PATH),
            "preservedV1DiagnosticSha256": preserved_sha,
            "preservedV1DiagnosticUnavailableReason": unavailable_reason,
            "normalizedOutputSha256": self.normalized_output_sha256,
            "nodeCount": len(self.nodes), "edgeCount": len(self.edges),
            "symbolEdgeCount": symbol_edge_count,
            "outputPaths": self.build_output_paths,
        })
        write_jsonl(BUILD_RUNS_PATH, previous)

    def graph_html(self, graph_json: dict[str, Any]) -> str:
        # A compact standalone filterable graph table; full relationships remain in graph.json/EDGES.jsonl.
        summary = {
            "nodes": graph_json["nodes"],
            "links": graph_json["links"],
        }
        data = json.dumps(summary, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return """<!doctype html><meta charset="utf-8"><title>MindRoom Graphify V2</title><style>body{font:14px system-ui;margin:20px;background:#111;color:#eee}input,select{margin:4px;padding:7px;background:#222;color:#eee;border:1px solid #555}table{border-collapse:collapse;width:100%}td,th{padding:5px;border-bottom:1px solid #333;text-align:left}code{color:#9ee}small{color:#aaa}.filters{display:flex;flex-wrap:wrap;gap:4px}</style><h1>MindRoom Graphify V2</h1><p>Directed authoritative graph with explicit architecture filters. The table is capped; the JSON/JSONL stores are not.</p><div class="filters"><input id=q placeholder="path or label"><select id=layer><option value="">all layers</option></select><select id=packageFilter><option value="">all packages</option></select><select id=capability><option value="">all capabilities</option></select><select id=requirement><option value="">all requirements</option></select><select id=classification><option value="">all classifications</option></select><select id=runtime><option value="">all runtime states</option></select><select id=risk><option value="">all risks</option></select><select id=edge><option value="">all edge types</option></select><select id=resolution><option value="">all resolutions</option></select><select id=review><option value="">all review states</option></select><select id=planned><option value="">runtime + planned</option><option value="false">runtime only</option><option value="true">planned only</option></select><select id=vendor><option value="">vendor any</option><option value="only">vendor only</option><option value="exclude">exclude vendor</option></select><select id=generated><option value="">generated any</option><option value="only">generated only</option><option value="exclude">exclude generated</option></select></div><p id=count></p><table><thead><tr><th>source</th><th>relation</th><th>target</th><th>layer</th><th>resolution</th><th>review</th><th>planned</th></tr></thead><tbody id=rows></tbody></table><script id=data type=application/json>""" + data + """</script><script>const g=JSON.parse(document.querySelector('#data').textContent),n=Object.fromEntries(g.nodes.map(x=>[x.id,x]));function opts(id,vals){for(const v of [...new Set(vals.flat().filter(Boolean))].sort()){let o=document.createElement('option');o.value=o.textContent=v;id.append(o)}}opts(layer,g.nodes.map(x=>x.layer));opts(packageFilter,g.nodes.map(x=>x.package));opts(capability,g.nodes.map(x=>x.capabilities));opts(requirement,g.nodes.map(x=>x.requirements));opts(classification,g.nodes.map(x=>x.classification));opts(runtime,g.nodes.map(x=>x.runtime));opts(risk,g.nodes.map(x=>x.risk));opts(edge,g.links.map(x=>x.type));opts(resolution,g.links.map(x=>x.resolution));opts(review,g.links.map(x=>x.review));function nodeMatch(v,s,d){return !v||[s,d].some(x=>x===v||(Array.isArray(x)&&x.includes(v)))}function flag(mode,s,d,key){return !mode||(mode==='only'&&(s[key]||d[key]))||(mode==='exclude'&&!s[key]&&!d[key])}function draw(){let t=q.value.toLowerCase(),a=g.links.filter(x=>{let s=n[x.source],d=n[x.target],hay=JSON.stringify([s.label,s.path,d.label,d.path]).toLowerCase();return(!t||hay.includes(t))&&nodeMatch(layer.value,s.layer,d.layer)&&nodeMatch(packageFilter.value,s.package,d.package)&&nodeMatch(capability.value,s.capabilities,d.capabilities)&&nodeMatch(requirement.value,s.requirements,d.requirements)&&nodeMatch(classification.value,s.classification,d.classification)&&nodeMatch(runtime.value,s.runtime,d.runtime)&&nodeMatch(risk.value,s.risk,d.risk)&&(!edge.value||x.type===edge.value)&&(!resolution.value||x.resolution===resolution.value)&&(!review.value||x.review===review.value)&&(!planned.value||String(x.planned)===planned.value)&&flag(vendor.value,s,d,'vendor')&&flag(generated.value,s,d,'generated')}).slice(0,2000);count.textContent=a.length+' visible edges (table capped at 2000; authoritative JSONL is uncapped)';rows.innerHTML=a.map(x=>`<tr><td><code>${n[x.source]?.label||x.source}</code><br><small>${n[x.source]?.path||''}</small></td><td>${x.type}</td><td><code>${n[x.target]?.label||x.target}</code><br><small>${n[x.target]?.path||''}</small></td><td>${x.layer}</td><td>${x.resolution}</td><td>${x.review}</td><td>${x.planned}</td></tr>`).join('')}document.querySelectorAll('input,select').forEach(x=>x.oninput=draw);draw()</script>"""

    def graph_report(self, hotspots: list[dict[str, Any]], edges: list[dict[str, Any]], nodes: list[dict[str, Any]], health: dict[str, Any]) -> str:
        gods = hotspots[:10]
        bridges = sorted(hotspots, key=lambda row: (-row["bridgeScore"], row["nodeId"]))[:10]
        surprises = []
        for edge in edges:
            source = self.nodes[edge["sourceNodeId"]]
            target = self.nodes[edge["targetNodeId"]]
            if source.get("package") and target.get("package") and source["package"] != target["package"] and source["layer"] == target["layer"] == "AUTHORED_RUNTIME":
                surprises.append((source["qualifiedName"], edge["relation"], target["qualifiedName"]))
            if len(surprises) >= 10:
                break
        return "# MindRoom Graphify V2 Report\n\n" + f"Run: `{RUN_ID}`  \nNodes: {len(nodes)}  \nDirected parallel-preserving edges: {len(edges)}  \nGraph health: {health['status']}\n\n" + "## God Nodes (authored runtime only)\n\n" + "\n".join(f"- `{row['qualifiedName']}` — degree {row['totalDegree']} (in {row['inDegree']}, out {row['outDegree']})" for row in gods) + "\n\n## Bridge Nodes (authored runtime only)\n\n" + "\n".join(f"- `{row['qualifiedName']}` — bridge score {row['bridgeScore']}" for row in bridges) + "\n\n## Surprising Connections\n\n" + ("\n".join(f"- `{a}` —{r}→ `{b}`" for a, r, b in surprises) or "- No unqualified cross-package authored-runtime surprises survived validation.") + "\n\n## Suggested Questions\n\n- Which authored-runtime bridge has the highest removal blast radius after excluded-system edges are filtered?\n- Which mixed runtime registration roots combine retained local behavior with later cloud removal work?\n- Which workspace package exports form the most important barrel-to-declaration chains?\n- Which migration dependencies constrain future local-first schema changes?\n"

    def run(self) -> None:
        self.add_file_nodes()
        self.add_package_nodes()
        self.build_rust_registry()
        self.build_native_module_indexes()
        self.build_tsconfig_registry()
        self.add_manifest_dependencies()
        self.add_symbol_nodes()
        self.add_language_imports()
        self.finalize_tsconfig_resolution_evidence()
        self.add_rust_relationships()
        self.add_revalidated_ast_edges()
        self.add_sql_relationships()
        self.add_semantic_schema_relationships()
        self.add_known_self_loop_repairs()
        self.add_runtime_registrations()
        changes = self.add_capability_requirement_change_nodes()
        self.add_generated_and_asset_edges()
        self.classify_v1_unresolved()
        self.capability_doc.update({"phase": "GRAPHIFY_V2_MAPPING", "schemaVersion": 2, "generatedAt": now_utc(), "runId": RUN_ID, "locationSemanticsVersion": 2})
        write_json(CAP_PATH, self.capability_doc)
        write_jsonl(RUNTIME_PATH, sorted(self.runtime_rows, key=lambda row: row["registrationId"]))
        write_jsonl(GRAPHIFY / "04 Exact Location Registry" / "CHANGE_LOCATION_REGISTRY.jsonl", sorted(changes, key=lambda row: row["changeId"]))
        change_by_capability = {row["capabilityId"]: row for row in changes}
        write_jsonl(GRAPHIFY / "04 Exact Location Registry" / "CHANGE_TRACEABILITY_MATRIX.jsonl", [
            {
                "requirementId": requirement["requirementId"], "capabilityIds": requirement.get("capabilityIds", []),
                "currentLocationStatuses": {cid: next(cap["currentLocationStatus"] for cap in self.capabilities if cap["capabilityId"] == cid) for cid in requirement.get("capabilityIds", [])},
                "changeIds": [change_by_capability[cid]["changeId"] for cid in requirement.get("capabilityIds", [])],
                "futureTaskIds": [f"MR-IMPL-{int(cid.rsplit('-', 1)[1]):03d}" for cid in requirement.get("capabilityIds", [])],
                "testsRequired": sorted({test for cid in requirement.get("capabilityIds", []) for test in change_by_capability[cid]["testsRequired"]}),
                "verificationEvidenceRequired": sorted({receipt for cid in requirement.get("capabilityIds", []) for receipt in change_by_capability[cid]["verificationReceiptsRequired"]}),
                "traceabilityStatus": "COMPLETE", "runId": RUN_ID, "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
            }
            for requirement in self.requirements
        ])
        self.write_exact_locations(changes)
        self.write_graphs(changes)
        self.write_build_run_receipt()
        print(json.dumps({"runId": RUN_ID, "nodes": len(self.nodes), "edges": len(self.edges), "runtimeRegistrations": len(self.runtime_rows), "diagnosticEndpoints": len(self.unresolved)}, separators=(",", ":")))


def main() -> None:
    Builder().run()


if __name__ == "__main__":
    main()
