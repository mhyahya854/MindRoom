"""Evidence-backed generated-artifact provenance for the MindRoom V2 graph."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import json
from repair_v2_common import (
    CODEBASE,
    CONTROL,
    GRAPHIFY,
    KG,
    codebase_rel,
    make_edge,
    load_json,
    now_utc,
    sha256_file,
    text_file,
    write_json,
    write_jsonl,
)


REGISTRY_PATH = KG / "GENERATED_CODE_PROVENANCE.jsonl"
BASELINE = load_json(CONTROL / "GRAPHIFY_REPAIR_BASELINE.json")


def _existing(builder: Any, paths: list[str]) -> list[str]:
    return sorted({path for path in paths if path in builder.file_nodes})


def _all_under(builder: Any, prefix: str, suffixes: tuple[str, ...] = ()) -> list[str]:
    return sorted(
        path
        for path in builder.file_nodes
        if path.startswith(prefix) and (not suffixes or path.lower().endswith(suffixes))
    )


def _consumer_search(
    builder: Any,
    generated_path: str,
    needles: list[str],
    suffixes: tuple[str, ...] = (),
) -> tuple[list[str], list[dict[str, Any]]]:
    consumers: list[str] = []
    evidence: list[dict[str, Any]] = []
    clean_needles = sorted({needle for needle in needles if needle})
    text_cache = getattr(builder, "_generated_consumer_text_cache", None)
    if text_cache is None:
        text_cache = {
            path: text
            for path in sorted(builder.file_nodes)
            if (text := text_file(GRAPHIFY.parent / path)) is not None
        }
        builder._generated_consumer_text_cache = text_cache
    for path, text in text_cache.items():
        if path == generated_path:
            continue
        if suffixes and not path.lower().endswith(suffixes):
            continue
        matches = [needle for needle in clean_needles if needle in text]
        if matches:
            consumers.append(path)
            evidence.append({
                "path": path,
                "kind": "LITERAL_SYMBOL_OR_MODULE_REFERENCE",
                "claim": "Consumer contains generated symbol/module reference.",
                "matchedNeedles": matches[:10],
            })
    if not evidence:
        evidence.append({
            "path": "Codebase/",
            "kind": "REPOSITORY_LITERAL_SEARCH",
            "claim": "No checked-in consumer matched the generated symbol/module search.",
            "matchedNeedles": clean_needles,
            "scopeSuffixes": list(suffixes),
        })
    return sorted(set(consumers)), evidence


def _graphql_definition_inputs(builder: Any) -> dict[str, list[str]]:
    definitions: dict[str, list[str]] = {}
    for path in sorted(builder.file_nodes):
        if not path.endswith((".gql", ".graphql")):
            continue
        text = text_file(GRAPHIFY.parent / path) or ""
        for match in re.finditer(r"\b(query|mutation|subscription|fragment)\s+([A-Za-z_]\w*)", text):
            kind, name = match.groups()
            definitions.setdefault(name, []).append(path)
            if kind != "fragment":
                generated_name = name[:1].upper() + name[1:] + kind.title()
                definitions.setdefault(generated_name, []).append(path)
    return {name: sorted(set(paths)) for name, paths in definitions.items()}


def _family_record(builder: Any, path: str, graphql_defs: dict[str, list[str]]) -> dict[str, Any]:
    generated_name = Path(path).name
    stem = generated_name.removesuffix(".graphql.swift").removesuffix(".gen.ts")
    language = builder.nodes[builder.file_nodes[path]].get("language", "")
    producer_paths: list[str]
    command: str
    command_evidence: list[dict[str, Any]]
    input_paths: list[str]
    schema_paths: list[str]
    consumer_needles: list[str]
    consumer_suffixes: tuple[str, ...] = ()

    if "/Packages/AffineGraphQL/" in path and path.endswith(".graphql.swift"):
        producer_paths = _existing(builder, [
            "Codebase/packages/frontend/apps/ios/codegen.ts",
            "Codebase/packages/frontend/apps/ios/apollo-codegen-chore.sh",
        ])
        command = "yarn affine @affine/ios codegen 1.25.4"
        command_evidence = [
            {"path": "Codebase/packages/frontend/apps/ios/package.json", "line": 14, "claim": "codegen script dispatches codegen.ts"},
            {"path": "Codebase/packages/frontend/apps/ios/codegen.ts", "line": 15, "claim": "dispatches apollo-codegen-chore.sh"},
            {"path": "Codebase/packages/frontend/apps/ios/apollo-codegen-chore.sh", "line": 20, "claim": "apollo-ios-cli generate uses apollo-codegen-config.json"},
        ]
        input_paths = graphql_defs.get(stem, [])
        schema_paths = _existing(builder, [
            "Codebase/packages/backend/server/src/schema.gql",
            "Codebase/packages/frontend/apps/ios/apollo-codegen-config.json",
        ])
        if not input_paths:
            input_paths = ["Codebase/packages/backend/server/src/schema.gql"]
        consumer_needles = [stem]
        consumer_suffixes = (".swift",)
    elif path == "Codebase/packages/frontend/apps/android/App/app/src/main/java/uniffi/affine_mobile_native/affine_mobile_native.kt":
        producer_paths = _existing(builder, [
            "Codebase/packages/frontend/apps/android/App/app/build.gradle",
            "Codebase/packages/frontend/mobile-native/uniffi-bindgen.rs",
        ])
        command = "cargo run --bin uniffi-bindgen generate --library <android-libaffine_mobile_native.so> --language kotlin --out-dir <app/src/main/java>"
        command_evidence = [{"path": "Codebase/packages/frontend/apps/android/App/app/build.gradle", "line": 204, "claim": "Gradle generate<Variant>UniFFIBindings commandLine"}]
        input_paths = _all_under(builder, "Codebase/packages/frontend/mobile-native/", (".rs", ".toml"))
        schema_paths = _existing(builder, ["Codebase/packages/frontend/mobile-native/Cargo.toml"])
        consumer_needles = ["uniffi.affine_mobile_native."]
        consumer_suffixes = (".kt", ".kts")
    elif "/App/App/uniffi/" in path:
        producer_paths = _existing(builder, [
            "Codebase/packages/frontend/apps/ios/codegen.ts",
            "Codebase/packages/frontend/mobile-native/uniffi-bindgen.rs",
        ])
        command = "cargo run -p affine_mobile_native --features use-as-lib --bin uniffi-bindgen generate --library <libaffine_mobile_native.a> --language swift --out-dir <App/App/uniffi>"
        command_evidence = [{"path": "Codebase/packages/frontend/apps/ios/codegen.ts", "line": 29, "claim": "UniFFI Swift generator command"}]
        input_paths = _all_under(builder, "Codebase/packages/frontend/mobile-native/", (".rs", ".toml"))
        schema_paths = _existing(builder, ["Codebase/packages/frontend/mobile-native/Cargo.toml"])
        consumer_needles = ["affine_mobile_native", generated_name.split(".")[0]]
        consumer_suffixes = (".swift", ".h", ".modulemap", ".pbxproj")
    elif path in {
        "Codebase/packages/backend/native/dts-header.d.ts",
        "Codebase/packages/backend/native/index.d.ts",
    }:
        producer_paths = _existing(builder, ["Codebase/packages/backend/native/package.json", "Codebase/packages/backend/native/Cargo.toml"])
        command = "yarn workspace @affine/server-native build"
        command_evidence = [{"path": "Codebase/packages/backend/native/package.json", "line": 25, "claim": "napi build generates declarations and native output"}]
        input_paths = _all_under(builder, "Codebase/packages/backend/native/", (".rs", ".toml"))
        schema_paths = _existing(builder, ["Codebase/packages/backend/native/package.json", "Codebase/packages/backend/native/dts-header.d.ts"] if generated_name == "index.d.ts" else ["Codebase/packages/backend/native/package.json"])
        consumer_needles = ["@affine/server-native", "server-native"]
        consumer_suffixes = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".json")
    elif path == "Codebase/packages/frontend/native/index.d.ts":
        producer_paths = _existing(builder, ["Codebase/packages/frontend/native/package.json", "Codebase/packages/frontend/native/Cargo.toml"])
        command = "yarn workspace @affine/native build"
        command_evidence = [{"path": "Codebase/packages/frontend/native/package.json", "line": 37, "claim": "napi build generates declarations and native output"}]
        input_paths = _all_under(builder, "Codebase/packages/frontend/native/", (".rs", ".toml"))
        schema_paths = _existing(builder, ["Codebase/packages/frontend/native/package.json"])
        consumer_needles = ["@affine/native"]
        consumer_suffixes = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".json")
    elif path.endswith("/errors.gen.ts"):
        producer_paths = _existing(builder, ["Codebase/packages/backend/server/src/base/error/index.ts"])
        command = "ErrorModule.onModuleInit under env.dev writes errors.gen.ts"
        command_evidence = [{"path": "Codebase/packages/backend/server/src/base/error/index.ts", "line": 23, "claim": "dev module initialization calls generateUserFriendlyErrors and writeFileSync"}]
        input_paths = _existing(builder, ["Codebase/packages/backend/server/src/base/error/def.ts"])
        schema_paths = input_paths[:]
        consumer_needles = ["errors.gen"]
        consumer_suffixes = (".ts", ".tsx")
    elif path.endswith("/i18n.gen.ts"):
        producer_paths = _existing(builder, ["Codebase/packages/frontend/i18n/build.ts"])
        command = "yarn workspace @affine/i18n build"
        command_evidence = [{"path": "Codebase/packages/frontend/i18n/build.ts", "line": 172, "claim": "runCli uses .i18n-codegen.json"}]
        input_paths = _all_under(builder, "Codebase/packages/frontend/i18n/src/resources/", (".json",))
        schema_paths = _existing(builder, ["Codebase/packages/frontend/i18n/.i18n-codegen.json"])
        consumer_needles = ["./i18n.gen", "i18n.gen"]
        consumer_suffixes = (".ts", ".tsx")
    elif path.endswith("/edgeless-templates.gen.ts"):
        producer_paths = _existing(builder, ["Codebase/packages/frontend/templates/build-edgeless.mjs"])
        command = "yarn workspace @affine/templates build"
        command_evidence = [{"path": "Codebase/packages/frontend/templates/package.json", "line": 7, "claim": "build runs build-edgeless.mjs"}]
        input_paths = _all_under(builder, "Codebase/packages/frontend/templates/edgeless-snapshot/")
        schema_paths = []
        consumer_needles = ["@affine/templates/edgeless", "edgeless-templates.gen"]
    elif path.endswith("/stickers-templates.gen.ts"):
        producer_paths = _existing(builder, ["Codebase/packages/frontend/templates/build-stickers.mjs"])
        command = "yarn workspace @affine/templates build"
        command_evidence = [{"path": "Codebase/packages/frontend/templates/package.json", "line": 7, "claim": "build runs build-stickers.mjs"}]
        input_paths = _all_under(builder, "Codebase/packages/frontend/templates/stickers/")
        schema_paths = []
        consumer_needles = ["@affine/templates/stickers", "stickers-templates.gen"]
    elif path.endswith("/workspace.gen.ts"):
        producer_paths = _existing(builder, ["Codebase/tools/cli/src/init.ts"])
        command = "yarn affine init"
        command_evidence = [{"path": "Codebase/tools/cli/src/init.ts", "line": 34, "claim": "init command writes tools/utils/src/workspace.gen.ts"}]
        input_paths = _all_under(builder, "Codebase/", ("package.json",))
        schema_paths = _existing(builder, ["Codebase/package.json", "Codebase/yarn.lock"])
        consumer_needles = ["./workspace.gen"]
        consumer_suffixes = (".ts", ".tsx")
    else:
        raise RuntimeError(f"Generated artifact lacks an evidence-backed family resolver: {path}")

    producer_paths = _existing(builder, producer_paths)
    input_paths = _existing(builder, input_paths)
    schema_paths = _existing(builder, schema_paths)
    if not producer_paths or not command or not input_paths:
        raise RuntimeError(f"Incomplete generated provenance for {path}")
    consumers, consumer_evidence = _consumer_search(
        builder, path, consumer_needles, consumer_suffixes
    )
    generated_at = now_utc()
    return {
        "runId": builder.nodes[builder.file_nodes[path]]["runId"],
        "codebaseBaseline": BASELINE["codebaseTreeSha256"],
        "masterPlanHashes": BASELINE["masterPlanHashes"],
        "generatorVersion": "mindroom-generated-provenance-v2.1",
        "extractionPolicyVersion": "mindroom-graphify-v2-layered-directed-2",
        "generatedAt": generated_at,
        "generatedArtifactNodeId": builder.file_nodes[path],
        "generatedPath": path,
        "generatedFileSha256": sha256_file(GRAPHIFY.parent / path),
        "language": language,
        "producerNodeIds": [builder.file_nodes[item] for item in producer_paths],
        "producerPaths": producer_paths,
        "generatorCommand": command,
        "commandEvidence": command_evidence,
        "inputPaths": input_paths,
        "inputSchemaPaths": schema_paths,
        "consumerNodeIds": [builder.file_nodes[item] for item in consumers],
        "consumerPaths": consumers,
        "consumerDiscoveryStatus": "EVIDENCE_BACKED" if consumers else "NO_REPOSITORY_CONSUMER_FOUND",
        "consumerSearchEvidence": consumer_evidence,
        "regenerationRequirements": [
            "Use the recorded command from the Codebase root with repository-pinned dependencies.",
            "Do not hand-edit the generated artifact.",
            "Verify generated output hashes and consumer compilation after regeneration.",
            "Rerun Graphify source hashes, generated provenance, and independent review.",
        ],
        "provenanceStatus": "EVIDENCE_CONFIRMED",
        "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
    }


def add_generated_provenance(builder: Any) -> list[dict[str, Any]]:
    """Replace heuristic generator edges with verified family-specific records."""
    builder.edges = {
        edge_id: edge
        for edge_id, edge in builder.edges.items()
        if edge.get("relation") != "GENERATES"
    }
    graphql_defs = _graphql_definition_inputs(builder)
    generated_paths = sorted(
        path for path, layer in builder.file_layers.items() if layer == "GENERATED_BINDING"
    )
    rows = [_family_record(builder, path, graphql_defs) for path in generated_paths]
    if len(rows) != len(generated_paths) or len({row["generatedPath"] for row in rows}) != len(generated_paths):
        raise RuntimeError("Generated provenance does not provide exact one-to-one coverage")
    for row in rows:
        target = row["generatedArtifactNodeId"]
        for producer_path, producer in zip(row["producerPaths"], row["producerNodeIds"]):
            builder.add_edge(make_edge(
                producer,
                target,
                "GENERATES",
                producer_path,
                "",
                row["generatorCommand"],
                "GENERATED_PROVENANCE_V2",
                "RESOLVED_INTERNAL_FILE",
                "RESOLVED_GENERATED_ARTIFACT",
                "GENERATED_BINDING",
                evidence=[producer_path, row["generatedPath"], row["generatorCommand"]],
            ))
        for input_path in sorted(set(row["inputPaths"] + row["inputSchemaPaths"])):
            builder.add_edge(make_edge(
                builder.file_nodes[input_path],
                target,
                "GENERATED_FROM",
                input_path,
                "",
                f"generator input:{Path(row['generatedPath']).name}",
                "GENERATED_INPUT_PROVENANCE_V2",
                "RESOLVED_INTERNAL_FILE",
                "RESOLVED_GENERATED_ARTIFACT",
                "GENERATED_BINDING",
                evidence=[input_path, row["generatedPath"], row["generatorCommand"]],
            ))
        for consumer_path, consumer in zip(row["consumerPaths"], row["consumerNodeIds"]):
            builder.add_edge(make_edge(
                consumer,
                target,
                "TYPE_DEPENDENCY",
                consumer_path,
                "",
                f"generated consumer:{Path(row['generatedPath']).name}",
                "GENERATED_CONSUMER_RESOLVER_V2",
                "RESOLVED_INTERNAL_FILE",
                "RESOLVED_GENERATED_ARTIFACT",
                builder.file_layers[consumer_path],
                evidence=[consumer_path, row["generatedPath"]],
            ))
    write_jsonl(REGISTRY_PATH, rows)
    graph_path = KG / "GENERATED_CODE_GRAPH.json"
    if graph_path.is_file():
        graph = load_json(graph_path)
        graph["provenanceRegistrySha256"] = sha256_file(REGISTRY_PATH)
        graph["provenanceRecordCount"] = len(rows)
        graph["generatedFilesWithProvenance"] = len(rows)
        graph["generatedFilesMissingProvenance"] = 0
        write_json(graph_path, graph)
    return rows
