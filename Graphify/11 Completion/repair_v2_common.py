"""Shared deterministic helpers for the MindRoom Graphify V2 repair.

This module is Graphify-only tooling.  It reads the Codebase but never writes to
it.  All identities are content-independent stable keys derived from semantic
referents (path, package name, or qualified name), while source hashes remain
separate freshness evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator


COMPLETION = Path(__file__).resolve().parent
GRAPHIFY = COMPLETION.parent
PROJECT = GRAPHIFY.parent
CODEBASE = PROJECT / "Codebase"
CONTROL = GRAPHIFY / "00 Execution Control"
KG = GRAPHIFY / "05 Dependency and Impact" / "Knowledge Graph"
TOOL_CACHE = CONTROL / "Generated Tool Cache"

LAYERS = (
    "AUTHORED_RUNTIME",
    "TEST_AND_FIXTURE",
    "BUILD_AND_CONFIG",
    "PACKAGING_AND_DEPLOYMENT",
    "MIGRATION_AND_SCHEMA",
    "GENERATED_BINDING",
    "VENDOR_AND_TOOLCHAIN",
    "DOCUMENTATION_AND_LEGAL",
    "ASSET_AND_MEDIA",
    "EXTERNAL_DEPENDENCY",
    "PLANNED_CAPABILITY",
)

NODE_BUILTINS = {
    "assert", "assert/strict", "async_hooks", "buffer", "child_process",
    "cluster", "console", "constants", "crypto", "dgram", "diagnostics_channel",
    "dns", "dns/promises", "domain", "events", "fs", "fs/promises", "http",
    "http2", "https", "module", "net", "os", "path", "path/posix",
    "path/win32", "perf_hooks", "process", "punycode", "querystring",
    "readline", "readline/promises", "repl", "stream", "stream/consumers",
    "stream/promises", "stream/web", "string_decoder", "sys", "timers",
    "timers/promises", "tls", "trace_events", "tty", "url", "util",
    "util/types", "v8", "vm", "wasi", "worker_threads", "zlib", "test",
}

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".rs", ".swift", ".kt", ".kts", ".py", ".sh", ".bash", ".zsh",
    ".sql", ".graphql", ".gql", ".css", ".scss", ".sass", ".less",
}

ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".icns",
    ".mp3", ".wav", ".m4a", ".mp4", ".mov", ".webm", ".pdf", ".ttf",
    ".otf", ".woff", ".woff2", ".zip", ".gz", ".tgz", ".tar", ".7z",
    ".wasm", ".node", ".dylib", ".dll", ".so", ".a", ".jar", ".keystore",
}

CONFIG_NAMES = {
    "package.json", "tsconfig.json", "jsconfig.json", "cargo.toml", "cargo.lock",
    "pyproject.toml", "requirements.txt", "pnpm-workspace.yaml", "yarn.lock",
    ".yarnrc.yml", ".npmrc", ".nvmrc", ".node-version", ".gitignore",
    ".gitattributes", ".prettierrc", ".prettierignore", ".eslintignore",
    "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs", "biome.json",
    "vitest.config.ts", "vite.config.ts", "playwright.config.ts", "turbo.json",
    "nx.json", "rust-toolchain.toml", "rustfmt.toml", "taplo.toml",
    "package.swift", "build.rs", "build.gradle", "build.gradle.kts",
    "settings.gradle", "settings.gradle.kts", "gradle.properties", "podfile",
    "tailwind.config.js", "tailwind.config.cjs", "tailwind.config.mjs",
    "tailwind.config.ts", "postcss.config.js", "postcss.config.cjs",
    "postcss.config.mjs", "postcss.config.ts",
}

IMPORT_RE = re.compile(
    r"(?:\bimport\s+(?:type\s+)?(?:[^;\n]*?\s+from\s+)?|"
    r"\bexport\s+(?:type\s+)?[^;\n]*?\s+from\s+|"
    r"\brequire\s*\(|\bimport\s*\()\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)
CSS_IMPORT_RE = re.compile(r"@(?:import|use|forward)\s+(?:url\()?['\"]([^'\"]+)['\"]")
PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)
RUST_USE_RE = re.compile(r"^\s*(?:pub\s+)?(?:use|mod)\s+([A-Za-z_][\w:]*)", re.MULTILINE)
SQL_CREATE_RE = re.compile(r"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?([\w.]+)", re.I)
SQL_REF_RE = re.compile(r"\bREFERENCES\s+[\"`]?([\w.]+)[\"`]?\s*\(\s*[\"`]?([\w]+)", re.I)
_CASE_SENSITIVE_PATH_INDEXES: dict[int, dict[str, Path]] = {}


def now_utc() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, *parts: str, length: int = 24) -> str:
    canonical = "\x1f".join(str(part).replace("\\", "/") for part in parts)
    return f"{prefix}-{sha256_bytes(canonical.encode('utf-8'))[:length]}"


def codebase_rel(path: Path) -> str:
    return "Codebase/" + path.resolve().relative_to(CODEBASE.resolve()).as_posix()


def graphify_rel(path: Path) -> str:
    return "Graphify/" + path.resolve().relative_to(GRAPHIFY.resolve()).as_posix()


def assert_graphify_write(path: Path) -> None:
    resolved = path.resolve()
    root = GRAPHIFY.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError(f"Refusing non-Graphify write: {resolved}")


def atomic_write_text(path: Path, text: str) -> None:
    assert_graphify_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    materialized = list(rows)
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in materialized)
    atomic_write_text(path, text)
    return len(materialized)


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path}:{number}: {error}") from error


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def is_probably_generated(relative: str, name: str) -> bool:
    lower = relative.lower()
    return any(
        marker in lower
        for marker in (
            "/generated/", "/__generated__/", "/bindings/", "/codegen/",
            ".generated.", ".gen.", ".graphql.swift", "/uniffi/", "/dist/",
        )
    ) or name.lower().endswith((".pb.ts", ".pb.rs"))


def classify_layer_details(path: Path) -> tuple[str, str, list[str], str]:
    """Return primary layer, ordered rule ID, evidence, and confidence.

    Priority is intentional: vendor, generated, tests, migration/schema,
    packaging, build/config, docs/legal, assets, then authored runtime.
    """
    relative = path.relative_to(CODEBASE).as_posix()
    lower = "/" + relative.lower()
    name = path.name.lower()
    suffix = path.suffix.lower()

    if (
        lower.startswith("/.yarn/")
        or "/node_modules/" in lower
        or "/vendor/" in lower
        or "/third_party/" in lower
        or "/third-party/" in lower
        or "/toolchain/" in lower
        or name.endswith((".min.js", ".min.css"))
    ):
        return "VENDOR_AND_TOOLCHAIN", "LAYER-V2-001-VENDOR", [relative, "vendor/toolchain marker"], "CONFIRMED"
    generated_header = ""
    if name.endswith(".d.ts"):
        try:
            generated_header = path.read_text(encoding="utf-8", errors="ignore")[:256].lower()
        except OSError:
            generated_header = ""
    if is_probably_generated(relative, path.name) or "auto-generated by napi-rs" in generated_header:
        return "GENERATED_BINDING", "LAYER-V2-002-GENERATED", [relative, "generated/binding marker"], "CONFIRMED"
    if (
        "/__tests__/" in lower
        or "/__test__/" in lower
        or "/tests/" in lower
        or "/test/" in lower
        or "/src/androidtest/" in lower
        or "/apptests/" in lower
        or "/fixtures/" in lower
        or "/fixture/" in lower
        or re.search(r"\.(?:spec|test|e2e|fixture)\.[^.]+$", name)
        or re.search(r"(?:tests?|uitests?)\.(?:swift|kt|kts|java|m|mm)$", name)
        or re.search(r"(?:^test_.*|.*_test)\.(?:py|rs|go)$", name)
        or name.endswith((".snap", ".snapshot"))
    ):
        return "TEST_AND_FIXTURE", "LAYER-V2-003-TEST", [relative, "test/fixture path or filename"], "CONFIRMED"
    if (
        "/migration" in lower
        or "/migrations/" in lower
        or "/schema/" in lower
        or name in {"schema.sql", "schema.prisma"}
        or (suffix in {".sql", ".prisma"} and "fixture" not in lower)
    ):
        return "MIGRATION_AND_SCHEMA", "LAYER-V2-004-MIGRATION-SCHEMA", [relative, "migration/schema marker"], "CONFIRMED"
    if (
        lower.startswith("/.github/")
        or lower.startswith("/.docker/")
        or "/docker/" in lower
        or "/helm/" in lower
        or "/deploy/" in lower
        or "/deployment/" in lower
        or "/packaging/" in lower
        or "/installer/" in lower
        or "/release/" in lower
        or name.startswith("dockerfile")
        or name in {"docker-compose.yml", "docker-compose.yaml", "electron-builder.yml", "electron-builder.yaml"}
        or name.startswith(("forge.config.", "capacitor.config."))
        or "entitlement" in name
    ):
        return "PACKAGING_AND_DEPLOYMENT", "LAYER-V2-005-PACKAGING", [relative, "packaging/deployment marker"], "CONFIRMED"
    if (
        name in CONFIG_NAMES
        or name.startswith(("tsconfig", "vite.config", "vitest.config", "webpack.config", "rollup.config", "tailwind.config", "postcss.config"))
        or name.endswith((".gradle", ".gradle.kts"))
        or suffix in {".toml", ".yaml", ".yml"}
        or lower.startswith("/scripts/")
        or lower.startswith("/tools/")
        or "/scripts/" in lower
        or "/tools/" in lower
        or (suffix == ".json" and not is_probably_generated(relative, path.name))
    ):
        return "BUILD_AND_CONFIG", "LAYER-V2-006-BUILD-CONFIG", [relative, "build/configuration marker"], "CONFIRMED"
    if (
        suffix in {".md", ".mdx", ".rst", ".txt"}
        or name.startswith(("license", "licence", "notice", "copying", "authors"))
        or lower.startswith("/docs/")
    ):
        return "DOCUMENTATION_AND_LEGAL", "LAYER-V2-007-DOCS-LEGAL", [relative, "documentation/legal marker"], "CONFIRMED"
    if suffix in ASSET_EXTENSIONS:
        return "ASSET_AND_MEDIA", "LAYER-V2-008-ASSET", [relative, f"asset extension {suffix}"], "CONFIRMED"
    return "AUTHORED_RUNTIME", "LAYER-V2-009-AUTHORED-RUNTIME", [relative, "no higher-priority layer rule matched"], "HIGH"


def classify_layer(path: Path) -> str:
    return classify_layer_details(path)[0]


def language_for(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".ts": "TypeScript", ".tsx": "TypeScript JSX", ".mts": "TypeScript",
        ".cts": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript JSX",
        ".mjs": "JavaScript", ".cjs": "JavaScript", ".rs": "Rust",
        ".swift": "Swift", ".kt": "Kotlin", ".kts": "Kotlin",
        ".py": "Python", ".sql": "SQL", ".graphql": "GraphQL", ".gql": "GraphQL",
        ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "Less",
        ".json": "JSON", ".toml": "TOML", ".yaml": "YAML", ".yml": "YAML",
        ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".md": "Markdown",
    }.get(suffix, "")


def package_name_from_specifier(specifier: str) -> str:
    clean = specifier[5:] if specifier.startswith("node:") else specifier
    if clean.startswith("@"):
        parts = clean.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else clean
    return clean.split("/", 1)[0]


def text_file(path: Path, maximum_bytes: int = 4_000_000) -> str | None:
    try:
        if path.stat().st_size > maximum_bytes:
            return None
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def source_imports(path: Path, text: str) -> list[tuple[str, str, str, int]]:
    """Return (relation, specifier, context, line) records."""
    suffix = path.suffix.lower()
    found: list[tuple[str, str, str, int]] = []
    if suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}:
        scan_text = mask_js_comments(text)
        for match in IMPORT_RE.finditer(scan_text):
            prefix = match.group(0)[: max(0, match.start(1) - match.start())]
            relation = "DYNAMIC_IMPORT" if "import(" in prefix.replace(" ", "") else "STATIC_IMPORT"
            if "export" in prefix:
                relation = "RE_EXPORT"
            elif re.search(r"\bimport\s+type\b", prefix):
                relation = "TYPE_ONLY_IMPORT"
            found.append((relation, match.group(1), "language-aware-js", text.count("\n", 0, match.start()) + 1))
    elif suffix in {".css", ".scss", ".sass", ".less"}:
        for match in CSS_IMPORT_RE.finditer(text):
            found.append(("STATIC_IMPORT", match.group(1), "language-aware-css", text.count("\n", 0, match.start()) + 1))
    elif suffix == ".py":
        for match in PY_IMPORT_RE.finditer(text):
            found.append(("STATIC_IMPORT", match.group(1) or match.group(2), "language-aware-python", text.count("\n", 0, match.start()) + 1))
    elif suffix == ".rs":
        for match in RUST_USE_RE.finditer(text):
            found.append(("TYPE_DEPENDENCY", match.group(1), "language-aware-rust", text.count("\n", 0, match.start()) + 1))
    elif suffix == ".swift":
        # Swift imports are module-scoped. Keep the raw module/member spelling;
        # the graph builder resolves local SwiftPM targets before frameworks.
        for match in re.finditer(
            r"^[ \t]*(?:@testable[ \t]+)?import[ \t]+(?:(?:class|enum|func|protocol|struct|typealias|var)[ \t]+)?([A-Za-z_][\w.]*)",
            text,
            re.MULTILINE,
        ):
            found.append(("TYPE_DEPENDENCY", match.group(1), "language-aware-swift", text.count("\n", 0, match.start()) + 1))
    elif suffix in {".kt", ".kts"}:
        # Kotlin imports are fully-qualified declarations or star namespaces.
        for match in re.finditer(
            r"^[ \t]*import[ \t]+([A-Za-z_][\w.]*(?:\.\*)?)(?:[ \t]+as[ \t]+[A-Za-z_]\w*)?[ \t]*$",
            text,
            re.MULTILINE,
        ):
            found.append(("TYPE_DEPENDENCY", match.group(1), "language-aware-kotlin", text.count("\n", 0, match.start()) + 1))
    elif suffix in {".graphql", ".gql"}:
        for match in re.finditer(r"^\s*#import\s+['\"]([^'\"]+)['\"]", text, re.MULTILINE):
            found.append(("STATIC_IMPORT", match.group(1), "language-aware-graphql", text.count("\n", 0, match.start()) + 1))
    return found


def mask_js_comments(text: str) -> str:
    """Replace JS comments with spaces while preserving offsets and newlines."""
    chars = list(text)
    index = 0
    state = "code"
    quote = ""
    while index < len(chars):
        current = chars[index]
        following = chars[index + 1] if index + 1 < len(chars) else ""
        if state == "code":
            if current in {"'", '"', "`"}:
                state = "string"
                quote = current
            elif current == "/" and following == "/":
                chars[index] = chars[index + 1] = " "
                index += 1
                state = "line-comment"
            elif current == "/" and following == "*":
                chars[index] = chars[index + 1] = " "
                index += 1
                state = "block-comment"
        elif state == "string":
            if current == "\\":
                index += 1
            elif current == quote:
                state = "code"
        elif state == "line-comment":
            if current == "\n":
                state = "code"
            else:
                chars[index] = " "
        elif state == "block-comment":
            if current == "*" and following == "/":
                chars[index] = chars[index + 1] = " "
                index += 1
                state = "code"
            elif current != "\n":
                chars[index] = " "
        index += 1
    return "".join(chars)


def resolve_relative(source: Path, specifier: str, all_paths: set[Path]) -> Path | None:
    raw = specifier.split("?", 1)[0].split("#", 1)[0]
    candidate = (source.parent / raw).resolve()
    extensions = (
        "", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs",
        ".json", ".css", ".scss", ".sass", ".less", ".graphql", ".gql",
        ".rs", ".swift", ".kt", ".py", ".sql", ".svg", ".png", ".jpg",
        ".webp", ".wasm", ".node",
    )
    candidates: list[Path] = []
    # ESM-authored TypeScript intentionally imports emitted `.js` specifiers.
    # Resolve those specifiers back to their source declaration before generic
    # extension probing (including names such as `styles.css.js` -> `.css.ts`).
    if candidate.suffix.lower() in {".js", ".jsx", ".mjs", ".cjs"}:
        emitted_stem = candidate.with_suffix("")
        for source_extension in (".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs"):
            candidates.append(Path(str(emitted_stem) + source_extension))
    for extension in extensions:
        candidates.append(Path(str(candidate) + extension))
    for index_name in (
        "index.ts", "index.tsx", "index.mts", "index.js", "index.jsx", "index.mjs",
        "index.json", "index.css", "mod.rs", "__init__.py",
    ):
        candidates.append(candidate / index_name)
    index_key = id(all_paths)
    case_index = _CASE_SENSITIVE_PATH_INDEXES.get(index_key)
    if case_index is None:
        case_index = {codebase_rel(item): item for item in all_paths}
        _CASE_SENSITIVE_PATH_INDEXES[index_key] = case_index
    for item in candidates:
        resolved = item.resolve()
        if CODEBASE.resolve() not in resolved.parents:
            continue
        candidate_key = "Codebase/" + resolved.relative_to(CODEBASE.resolve()).as_posix()
        actual = case_index.get(candidate_key)
        if actual is not None:
            return actual
    return None


def load_workspace_packages() -> tuple[dict[str, dict[str, Any]], dict[Path, str]]:
    packages: dict[str, dict[str, Any]] = {}
    roots: dict[Path, str] = {}
    for manifest in sorted(CODEBASE.rglob("package.json")):
        if any(part in {"node_modules", ".yarn"} for part in manifest.parts):
            continue
        try:
            data = load_json(manifest)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        name = data.get("name")
        if isinstance(name, str) and name:
            packages[name] = {"manifest": manifest, "root": manifest.parent, "data": data}
            roots[manifest.parent.resolve()] = name
    return packages, roots


def nearest_package(path: Path, roots: dict[Path, str]) -> str:
    current = path.parent.resolve()
    while CODEBASE.resolve() in current.parents or current == CODEBASE.resolve():
        if current in roots:
            return roots[current]
        if current == CODEBASE.resolve():
            break
        current = current.parent
    return "@affine/monorepo"


def source_hash_manifest() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(item for item in CODEBASE.rglob("*") if item.is_file()):
        rows.append({"path": codebase_rel(path), "sizeBytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def tree_digest(rows: Iterable[dict[str, Any]]) -> str:
    canonical = "".join(f"{row['path']}\0{row['sizeBytes']}\0{row['sha256']}\n" for row in rows)
    return sha256_bytes(canonical.encode("utf-8"))


def inverse_capability_paths(capabilities: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for capability in capabilities:
        cid = capability["capabilityId"]
        for path in capability.get("currentPaths", []):
            if isinstance(path, str) and path.startswith("Codebase/"):
                result[path].append(cid)
    return {key: sorted(set(value)) for key, value in result.items()}


def edge_id(source: str, target: str, relation: str, declaring_path: str, span: str, context: str, origin: str) -> str:
    return stable_id("MR-EDGE", source, target, relation, declaring_path, span, context, origin, length=24)


def make_edge(
    source: str,
    target: str,
    relation: str,
    declaring_path: str,
    span: str,
    context: str,
    origin: str,
    source_status: str,
    target_status: str,
    layer: str,
    capability_ids: list[str] | None = None,
    evidence: list[str] | None = None,
    recursive_status: str = "NOT_RECURSIVE",
) -> dict[str, Any]:
    return {
        "edgeId": edge_id(source, target, relation, declaring_path, span, context, origin),
        "sourceNodeId": source,
        "targetNodeId": target,
        "relation": relation,
        "declaringPath": declaring_path,
        "sourceSpan": span,
        "context": context,
        "evidenceOrigin": origin,
        "sourceResolutionStatus": source_status,
        "targetResolutionStatus": target_status,
        "layer": layer,
        "capabilityIds": sorted(set(capability_ids or [])),
        "evidence": evidence or [],
        "runtimeRelationship": relation not in {"PLANNED_CAPABILITY_DEPENDENCY", "IMPLEMENTS_CAPABILITY"},
        "reviewStatus": "PENDING_INDEPENDENT_REVIEW",
        "recursiveStatus": recursive_status,
    }
