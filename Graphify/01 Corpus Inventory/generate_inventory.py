from __future__ import annotations

import fnmatch
import glob
import hashlib
import json
import mimetypes
import os
import re
import stat
import tarfile
import tomllib
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote


SCRIPT_VERSION = "1.0.0"
OUTPUT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = OUTPUT_DIR.parents[1]
CODEBASE_ROOT = PROJECT_ROOT / "Codebase"

REPOSITORY_INVENTORY = OUTPUT_DIR / "REPOSITORY_INVENTORY.jsonl"
PACKAGE_INVENTORY = OUTPUT_DIR / "PACKAGE_INVENTORY.json"
CORPUS_SUMMARY = OUTPUT_DIR / "CORPUS_SUMMARY.md"
MARKDOWN_LEDGER = OUTPUT_DIR / "MARKDOWN_MIGRATION_LEDGER.jsonl"
BINARY_INVENTORY = OUTPUT_DIR / "BINARY_AND_RUNTIME_ASSET_INVENTORY.jsonl"
ARCHIVE_INVENTORY = OUTPUT_DIR / "ARCHIVE_INVENTORY.jsonl"
PLATFORM_INVENTORY = OUTPUT_DIR / "PLATFORM_FILE_INVENTORY.jsonl"

ARCHIVE_EXTENSIONS = {
    ".7z",
    ".aab",
    ".apk",
    ".asar",
    ".bz2",
    ".cab",
    ".crate",
    ".deb",
    ".dmg",
    ".gz",
    ".ipa",
    ".iso",
    ".jar",
    ".rar",
    ".rpm",
    ".tar",
    ".tar.bz2",
    ".tar.gz",
    ".tar.xz",
    ".tgz",
    ".war",
    ".whl",
    ".xz",
    ".zip",
}

BINARY_EXTENSIONS = ARCHIVE_EXTENSIONS | {
    ".a",
    ".ai",
    ".avif",
    ".avi",
    ".bin",
    ".bmp",
    ".class",
    ".dat",
    ".db",
    ".dll",
    ".doc",
    ".docx",
    ".dylib",
    ".eot",
    ".exe",
    ".flac",
    ".gif",
    ".heic",
    ".icns",
    ".ico",
    ".jpeg",
    ".jpg",
    ".lib",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".node",
    ".odg",
    ".odp",
    ".ods",
    ".odt",
    ".ogg",
    ".otf",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".psd",
    ".pyc",
    ".rlib",
    ".so",
    ".sqlite",
    ".sqlite3",
    ".ttf",
    ".tif",
    ".tiff",
    ".wav",
    ".wasm",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
    ".xls",
    ".xlsx",
}

TEXT_EXTENSIONS = {
    "",
    ".c",
    ".cc",
    ".cfg",
    ".cjs",
    ".cmake",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".dockerignore",
    ".editorconfig",
    ".env",
    ".gitattributes",
    ".gitignore",
    ".gql",
    ".gradle",
    ".graphql",
    ".graphqls",
    ".h",
    ".hbs",
    ".hpp",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".json5",
    ".jsonc",
    ".jsx",
    ".kt",
    ".kts",
    ".less",
    ".lock",
    ".m",
    ".markdown",
    ".md",
    ".mdx",
    ".mjs",
    ".mm",
    ".mustache",
    ".plist",
    ".properties",
    ".proto",
    ".ps1",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svg",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}

SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cjs",
    ".cpp",
    ".cs",
    ".go",
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
    ".php",
    ".proto",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}

ASSET_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".css",
    ".csv",
    ".eot",
    ".flac",
    ".gif",
    ".heic",
    ".hbs",
    ".html",
    ".icns",
    ".ico",
    ".jpeg",
    ".jpg",
    ".json",
    ".lottie",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".mustache",
    ".ogg",
    ".otf",
    ".png",
    ".svg",
    ".ttf",
    ".wav",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
}

LANGUAGES = {
    ".c": "C",
    ".cc": "C++",
    ".cjs": "JavaScript",
    ".cmake": "CMake",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".csv": "CSV",
    ".gql": "GraphQL",
    ".gradle": "Gradle",
    ".graphql": "GraphQL",
    ".graphqls": "GraphQL",
    ".h": "C/C++ Header",
    ".hbs": "Handlebars",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".json": "JSON",
    ".json5": "JSON5",
    ".jsonc": "JSON with Comments",
    ".jsx": "JavaScript JSX",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".less": "Less",
    ".lock": "Lockfile",
    ".m": "Objective-C",
    ".markdown": "Markdown",
    ".md": "Markdown",
    ".mdx": "MDX",
    ".mjs": "JavaScript",
    ".mm": "Objective-C++",
    ".plist": "Property List",
    ".properties": "Properties",
    ".proto": "Protocol Buffers",
    ".ps1": "PowerShell",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".scss": "SCSS",
    ".sh": "Shell",
    ".sql": "SQL",
    ".svg": "SVG",
    ".swift": "Swift",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsx": "TypeScript JSX",
    ".txt": "Plain Text",
    ".vue": "Vue",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}

GENERATED_SEGMENTS = {
    ".next",
    ".nx",
    ".nyc_output",
    ".swc",
    "build",
    "coverage",
    "dist",
    "graphify-out",
    "node_modules",
    "out",
    "out-tsc",
    "playwright-report",
    "storybook-static",
    "target",
    "test-results",
}

VENDOR_SEGMENTS = {
    ".yarn",
    "third_party",
    "third-party",
    "vendor",
    "vendored",
}

FIXTURE_SEGMENTS = {
    "__fixtures__",
    "__snapshots__",
    "fixture",
    "fixtures",
    "snapshots",
    "test-data",
    "testdata",
}

TEST_SEGMENTS = {"__tests__", "e2e", "test", "tests"}
RUNTIME_ASSET_SEGMENTS = {
    "assets",
    "fonts",
    "icons",
    "images",
    "locales",
    "media",
    "public",
    "resources",
    "static",
    "templates",
}

PLATFORM_PATH_MARKERS = {
    "WINDOWS": {"win", "win32", "windows"},
    "MACOS": {"darwin", "mac", "macos", "osx"},
    "LINUX": {"linux"},
    "ANDROID": {"android"},
    "IOS": {"ios", "iphoneos", "xcodeproj", "xcworkspace"},
}

PLATFORM_EXTENSIONS = {
    ".app": "MACOS",
    ".deb": "LINUX",
    ".desktop": "LINUX",
    ".dll": "WINDOWS",
    ".dylib": "MACOS",
    ".entitlements": "IOS",
    ".exe": "WINDOWS",
    ".icns": "MACOS",
    ".ipa": "IOS",
    ".msi": "WINDOWS",
    ".rpm": "LINUX",
    ".so": "LINUX",
    ".swift": "IOS",
    ".xcodeproj": "IOS",
    ".xcworkspace": "IOS",
}

PLATFORM_CONTENT_PATTERNS = {
    "WINDOWS": re.compile(
        r"""(?ix)
        target_os\s*=\s*["']windows["'] |
        cfg!?\s*\(\s*windows\s*\) |
        process\.platform\s*={2,3}\s*["']win32["'] |
        NodeJS\.Platform.*win32
        """
    ),
    "MACOS": re.compile(
        r"""(?ix)
        target_os\s*=\s*["']macos["'] |
        cfg!?\s*\(\s*(?:target_os\s*=\s*)?["']?macos["']?\s*\) |
        process\.platform\s*={2,3}\s*["']darwin["']
        """
    ),
    "LINUX": re.compile(
        r"""(?ix)
        target_os\s*=\s*["']linux["'] |
        cfg!?\s*\(\s*(?:target_os\s*=\s*)?["']?linux["']?\s*\) |
        process\.platform\s*={2,3}\s*["']linux["']
        """
    ),
    "ANDROID": re.compile(
        r"""(?ix)
        target_os\s*=\s*["']android["'] |
        cfg!?\s*\(\s*(?:target_os\s*=\s*)?["']?android["']?\s*\) |
        com\.android\.(?:application|library)
        """
    ),
    "IOS": re.compile(
        r"""(?ix)
        target_os\s*=\s*["']ios["'] |
        cfg!?\s*\(\s*(?:target_os\s*=\s*)?["']?ios["']?\s*\) |
        capacitor.*ios
        """
    ),
}

MARKDOWN_SUFFIX = re.compile(r"\.(?:markdown|md)\b", re.IGNORECASE)

ENTITY_ENUM = {"FILE", "DIRECTORY", "SYMLINK", "JUNCTION", "ARCHIVE"}
PLATFORM_ENUM = {"CROSS_PLATFORM", "WINDOWS", "MACOS", "LINUX", "UNKNOWN"}
CLASSIFICATION_ENUM = {
    "SOURCE",
    "TEST",
    "FIXTURE",
    "ASSET",
    "CONFIG",
    "BUILD",
    "PACKAGING",
    "MIGRATION",
    "GENERATED",
    "VENDOR",
    "LEGAL",
    "DOCUMENTATION",
    "UNKNOWN",
}
TRACKED_ENUM = {"TRACKED", "UNTRACKED", "IGNORED", "UNKNOWN"}
REACHABILITY_ENUM = {"YES", "NO", "UNKNOWN"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def posix_relative(path: Path) -> str:
    relative = path.relative_to(CODEBASE_ROOT).as_posix()
    return "" if relative == "." else relative


def codebase_path(relative: str) -> str:
    return f"Codebase/{relative}"


def full_extension(path: Path) -> str:
    lower = path.name.lower()
    for extension in sorted(ARCHIVE_EXTENSIONS, key=len, reverse=True):
        if lower.endswith(extension):
            return extension
    return path.suffix.lower()


def sha256_and_sample(path: Path) -> tuple[str, bytes]:
    digest = hashlib.sha256()
    sample = bytearray()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            if len(sample) < 8192:
                sample.extend(chunk[: 8192 - len(sample)])
    return digest.hexdigest(), bytes(sample)


def detected_binary(extension: str, sample: bytes) -> bool:
    if extension in BINARY_EXTENSIONS:
        return True
    if extension in TEXT_EXTENSIONS:
        return False
    return b"\x00" in sample


def generated_header_evidence(sample: bytes, binary: bool) -> str:
    if binary:
        return ""
    header = "\n".join(
        sample.decode("utf-8", errors="replace").splitlines()[:25]
    )
    markers = [
        (r"(?i)@generated\b", "@generated header marker"),
        (
            r"(?i)\b(?:automatically generated|auto-?generated by)\b",
            "automatic-generation header marker",
        ),
        (
            r"(?i)\b(?:do not edit|do not modify)\b",
            "do-not-edit/modify header marker",
        ),
    ]
    return next((label for pattern, label in markers if re.search(pattern, header)), "")


def is_reparse_point(file_stat: os.stat_result) -> bool:
    attributes = getattr(file_stat, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def scan_paths() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    raw: list[dict[str, Any]] = []
    exclusions: list[dict[str, str]] = []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda item: (item.name.casefold(), item.name))
        except OSError as error:
            exclusions.append(
                {
                    "path": codebase_path(posix_relative(directory)),
                    "reason": f"{type(error).__name__}: {error}",
                }
            )
            return

        for entry in entries:
            path = Path(entry.path)
            relative = posix_relative(path)
            try:
                file_stat = entry.stat(follow_symlinks=False)
                symbolic_link = entry.is_symlink()
                reparse = is_reparse_point(file_stat)
                if symbolic_link:
                    entity_type = "SYMLINK"
                elif reparse:
                    entity_type = "JUNCTION"
                elif entry.is_dir(follow_symlinks=False):
                    entity_type = "DIRECTORY"
                elif full_extension(path) in ARCHIVE_EXTENSIONS:
                    entity_type = "ARCHIVE"
                else:
                    entity_type = "FILE"

                digest = ""
                sample = b""
                hash_error = ""
                link_target = ""
                if entity_type in {"FILE", "ARCHIVE"}:
                    try:
                        digest, sample = sha256_and_sample(path)
                    except OSError as error:
                        hash_error = f"{type(error).__name__}: {error}"
                elif entity_type in {"SYMLINK", "JUNCTION"}:
                    try:
                        link_target = os.readlink(path)
                    except OSError as error:
                        link_target = f"UNRESOLVED: {type(error).__name__}: {error}"

                raw.append(
                    {
                        "absolutePath": path,
                        "relative": relative,
                        "entityType": entity_type,
                        "sizeBytes": file_stat.st_size if entity_type in {"FILE", "ARCHIVE"} else 0,
                        "sha256": digest,
                        "sample": sample,
                        "hashError": hash_error,
                        "linkTarget": link_target,
                    }
                )
                if entity_type == "DIRECTORY":
                    visit(path)
            except OSError as error:
                exclusions.append(
                    {
                        "path": codebase_path(relative),
                        "reason": f"{type(error).__name__}: {error}",
                    }
                )

    visit(CODEBASE_ROOT)
    raw.sort(key=lambda item: (item["relative"].casefold(), item["relative"]))
    return raw, exclusions


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            return {}, "Top-level JSON value is not an object"
        return value, ""
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return {}, f"{type(error).__name__}: {error}"


def read_toml(path: Path) -> tuple[dict[str, Any], str]:
    try:
        with path.open("rb") as stream:
            value = tomllib.load(stream)
        return value, ""
    except (OSError, tomllib.TOMLDecodeError) as error:
        return {}, f"{type(error).__name__}: {error}"


def resolve_yarn_workspace_patterns(
    root_manifest: Path, patterns: list[str], package_manifests: set[Path]
) -> dict[Path, list[str]]:
    resolved: dict[Path, list[str]] = defaultdict(list)
    for pattern in patterns:
        candidate_pattern = str(root_manifest.parent / pattern / "package.json")
        for match in glob.glob(candidate_pattern, recursive=True):
            manifest = Path(match).resolve()
            if manifest in package_manifests:
                resolved[manifest].append(pattern)
    return resolved


def dependency_groups(manifest: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
        "bundledDependencies",
    )
    return {key: manifest.get(key, {}) for key in keys if key in manifest}


def package_inventory(
    raw_paths: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    file_by_relative = {
        item["relative"]: item
        for item in raw_paths
        if item["entityType"] in {"FILE", "ARCHIVE"}
    }
    package_json_paths = sorted(
        (
            item["absolutePath"]
            for item in raw_paths
            if item["entityType"] == "FILE" and item["absolutePath"].name == "package.json"
        ),
        key=lambda value: posix_relative(value).casefold(),
    )
    cargo_paths = sorted(
        (
            item["absolutePath"]
            for item in raw_paths
            if item["entityType"] == "FILE" and item["absolutePath"].name == "Cargo.toml"
        ),
        key=lambda value: posix_relative(value).casefold(),
    )
    settings_paths = sorted(
        (
            item["absolutePath"]
            for item in raw_paths
            if item["entityType"] == "FILE"
            and item["absolutePath"].name in {"settings.gradle", "settings.gradle.kts"}
        ),
        key=lambda value: posix_relative(value).casefold(),
    )

    npm_manifests: dict[Path, tuple[dict[str, Any], str]] = {
        path.resolve(): read_json(path) for path in package_json_paths
    }
    root_package_path = (CODEBASE_ROOT / "package.json").resolve()
    root_package = npm_manifests.get(root_package_path, ({}, "Root package.json not found"))[0]
    raw_workspaces = root_package.get("workspaces", [])
    if isinstance(raw_workspaces, dict):
        raw_workspaces = raw_workspaces.get("packages", [])
    yarn_patterns = [pattern for pattern in raw_workspaces if isinstance(pattern, str)]
    yarn_membership = resolve_yarn_workspace_patterns(
        root_package_path, yarn_patterns, set(npm_manifests)
    )

    root_cargo_path = (CODEBASE_ROOT / "Cargo.toml").resolve()
    root_cargo, root_cargo_error = read_toml(root_cargo_path)
    cargo_members = [
        str(PurePosixPath(member.lstrip("./")))
        for member in root_cargo.get("workspace", {}).get("members", [])
        if isinstance(member, str)
    ]

    packages: list[dict[str, Any]] = []
    ownership_roots: list[dict[str, Any]] = []
    workspaces: list[dict[str, Any]] = []

    for manifest_path in package_json_paths:
        resolved = manifest_path.resolve()
        manifest, parse_error = npm_manifests[resolved]
        root_relative = posix_relative(manifest_path.parent)
        name = manifest.get("name") if isinstance(manifest.get("name"), str) else ""
        package_id = f"npm:{name or root_relative or '(root)'}"
        patterns = yarn_membership.get(resolved, [])
        is_root = resolved == root_package_path
        record = {
            "packageId": package_id,
            "ecosystem": "NPM",
            "name": name,
            "version": manifest.get("version", ""),
            "private": manifest.get("private", False),
            "license": manifest.get("license", ""),
            "packageRoot": codebase_path(root_relative) if root_relative else "Codebase",
            "manifestPath": codebase_path(posix_relative(manifest_path)),
            "manifestSha256": file_by_relative[posix_relative(manifest_path)]["sha256"],
            "packageManager": root_package.get("packageManager", "yarn (root evidence)"),
            "workspaceMembership": {
                "workspaceRoot": "Codebase/package.json",
                "declared": is_root or bool(patterns),
                "matchedPatterns": ["."] if is_root else sorted(patterns),
                "evidence": "Root package.json workspaces",
            },
            "scripts": manifest.get("scripts", {}),
            "dependencyGroups": dependency_groups(manifest),
            "entrypoints": {
                key: manifest[key]
                for key in ("main", "module", "browser", "types", "exports", "bin")
                if key in manifest
            },
            "engines": manifest.get("engines", {}),
            "publishConfig": manifest.get("publishConfig", {}),
            "parseStatus": "VALID" if not parse_error else "INVALID",
            "parseError": parse_error,
            "ownedPathCount": 0,
            "ownedFileCount": 0,
            "ownedSizeBytes": 0,
        }
        packages.append(record)
        ownership_roots.append(
            {
                "root": root_relative,
                "packageId": package_id,
                "ecosystem": "NPM",
            }
        )

    cargo_package_roots: dict[str, str] = {}
    for manifest_path in cargo_paths:
        manifest, parse_error = read_toml(manifest_path)
        root_relative = posix_relative(manifest_path.parent)
        package = manifest.get("package")
        workspace = manifest.get("workspace")
        if workspace is not None:
            workspaces.append(
                {
                    "workspaceId": f"cargo-workspace:{root_relative or '(root)'}",
                    "ecosystem": "CARGO",
                    "root": codebase_path(root_relative) if root_relative else "Codebase",
                    "manifestPath": codebase_path(posix_relative(manifest_path)),
                    "declaredMembers": workspace.get("members", []),
                    "excludedMembers": workspace.get("exclude", []),
                    "resolver": workspace.get("resolver", ""),
                    "parseStatus": "VALID" if not parse_error else "INVALID",
                    "parseError": parse_error,
                }
            )
        if not isinstance(package, dict):
            continue
        name = package.get("name", "")
        package_id = f"cargo:{name or root_relative}"
        explicit = root_relative in cargo_members
        membership = (
            "EXPLICIT_MEMBER"
            if explicit
            else "MANIFEST_IN_WORKSPACE_TREE_REQUIRES_CARGO_METADATA_CONFIRMATION"
        )
        dependency_tables = {
            key: manifest[key]
            for key in ("dependencies", "dev-dependencies", "build-dependencies")
            if key in manifest
        }
        targets = {
            key: manifest[key]
            for key in ("lib", "bin", "example", "test", "bench")
            if key in manifest
        }
        record = {
            "packageId": package_id,
            "ecosystem": "CARGO",
            "name": name,
            "version": package.get("version", ""),
            "private": package.get("publish") is False,
            "license": package.get("license", ""),
            "packageRoot": codebase_path(root_relative),
            "manifestPath": codebase_path(posix_relative(manifest_path)),
            "manifestSha256": file_by_relative[posix_relative(manifest_path)]["sha256"],
            "packageManager": "cargo",
            "workspaceMembership": {
                "workspaceRoot": "Codebase/Cargo.toml",
                "declared": explicit,
                "membershipClassification": membership,
                "evidence": "Root Cargo.toml workspace.members and package manifest location",
            },
            "features": manifest.get("features", {}),
            "dependencyGroups": dependency_tables,
            "targets": targets,
            "buildScript": package.get("build", ""),
            "parseStatus": "VALID" if not parse_error else "INVALID",
            "parseError": parse_error,
            "ownedPathCount": 0,
            "ownedFileCount": 0,
            "ownedSizeBytes": 0,
        }
        packages.append(record)
        cargo_package_roots[root_relative] = package_id
        ownership_roots.append(
            {
                "root": root_relative,
                "packageId": package_id,
                "ecosystem": "CARGO",
            }
        )

    for settings_path in settings_paths:
        root_relative = posix_relative(settings_path.parent)
        text = settings_path.read_text(encoding="utf-8", errors="replace")
        modules = re.findall(r"""(?m)^\s*include\s+['"](:[^'"]+)['"]""", text)
        workspace_id = f"gradle-workspace:{root_relative}"
        workspace_record = {
            "workspaceId": workspace_id,
            "ecosystem": "GRADLE",
            "root": codebase_path(root_relative),
            "manifestPath": codebase_path(posix_relative(settings_path)),
            "declaredMembers": modules,
            "parseStatus": "VALID",
            "parseError": "",
        }
        workspaces.append(workspace_record)
        for module in modules:
            module_relative = module.lstrip(":").replace(":", "/")
            module_root = settings_path.parent / module_relative
            build_candidates = [module_root / "build.gradle", module_root / "build.gradle.kts"]
            build_manifest = next((item for item in build_candidates if item.exists()), None)
            manifest_relative = posix_relative(build_manifest) if build_manifest else ""
            package_root_relative = posix_relative(module_root)
            package_id = f"gradle:{root_relative}:{module}"
            record = {
                "packageId": package_id,
                "ecosystem": "GRADLE",
                "name": module,
                "version": "",
                "private": True,
                "license": "",
                "packageRoot": codebase_path(package_root_relative),
                "manifestPath": codebase_path(manifest_relative) if manifest_relative else "",
                "manifestSha256": (
                    file_by_relative[manifest_relative]["sha256"] if manifest_relative else ""
                ),
                "packageManager": "Gradle",
                "workspaceMembership": {
                    "workspaceRoot": codebase_path(root_relative),
                    "declared": True,
                    "membershipClassification": "EXPLICIT_INCLUDE",
                    "evidence": codebase_path(posix_relative(settings_path)),
                },
                "parseStatus": "VALID" if build_manifest else "MISSING_BUILD_MANIFEST",
                "parseError": "" if build_manifest else "Included module has no build.gradle(.kts)",
                "ownedPathCount": 0,
                "ownedFileCount": 0,
                "ownedSizeBytes": 0,
            }
            packages.append(record)
            ownership_roots.append(
                {
                    "root": package_root_relative,
                    "packageId": package_id,
                    "ecosystem": "GRADLE",
                }
            )

    workspaces.insert(
        0,
        {
            "workspaceId": "yarn-workspace:root",
            "ecosystem": "NPM",
            "root": "Codebase",
            "manifestPath": "Codebase/package.json",
            "declaredMembers": yarn_patterns,
            "packageManager": root_package.get("packageManager", ""),
            "parseStatus": (
                "VALID" if root_package and not npm_manifests[root_package_path][1] else "INVALID"
            ),
            "parseError": npm_manifests.get(root_package_path, ({}, "Missing"))[1],
        },
    )

    gradle_wrapper = next(
        (
            item["absolutePath"]
            for item in raw_paths
            if item["relative"].endswith("gradle-wrapper.properties")
        ),
        None,
    )
    gradle_version = ""
    if gradle_wrapper:
        wrapper_text = gradle_wrapper.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"gradle-([0-9][0-9.]*)-", wrapper_text)
        gradle_version = match.group(1) if match else ""

    package_document = {
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "sourceRoot": str(CODEBASE_ROOT),
        "discoveryBasis": [
            "Every package.json under Codebase",
            "Every Cargo.toml under Codebase",
            "Root package.json workspaces",
            "Root Cargo.toml workspace.members",
            "Every settings.gradle(.kts) include declaration",
        ],
        "packageManagers": [
            {
                "manager": "Yarn",
                "version": str(root_package.get("packageManager", "")).partition("@")[2],
                "evidence": ["Codebase/package.json", "Codebase/yarn.lock", "Codebase/.yarnrc.yml"],
            },
            {
                "manager": "Cargo",
                "version": "",
                "evidence": ["Codebase/Cargo.toml", "Codebase/Cargo.lock"],
            },
            {
                "manager": "Gradle",
                "version": gradle_version,
                "evidence": [
                    codebase_path(posix_relative(settings_path)) for settings_path in settings_paths
                ],
            },
        ],
        "workspaces": sorted(workspaces, key=lambda item: item["workspaceId"]),
        "packages": sorted(packages, key=lambda item: item["packageId"]),
        "limitations": [
            "Cargo workspace membership outside explicit workspace.members is marked for cargo metadata confirmation.",
            "Gradle module discovery is limited to checked-in settings.gradle(.kts) include declarations.",
            "Dependency reachability is not inferred from manifest membership.",
        ],
    }
    return package_document, ownership_roots


def package_for(
    relative: str, extension: str, ownership_roots: list[dict[str, Any]]
) -> str:
    candidates = []
    for package_root in ownership_roots:
        root = package_root["root"]
        if not root or relative == root or relative.startswith(f"{root}/"):
            candidates.append(package_root)
    if not candidates:
        return ""
    depth = max(item["root"].count("/") + bool(item["root"]) for item in candidates)
    candidates = [
        item
        for item in candidates
        if item["root"].count("/") + bool(item["root"]) == depth
    ]
    preferred = "NPM"
    if extension in {".rs"} or PurePosixPath(relative).name == "Cargo.toml":
        preferred = "CARGO"
    elif (
        extension in {".gradle", ".java", ".kt", ".kts"}
        or "/android/" in f"/{relative.lower()}/"
    ):
        preferred = "GRADLE"
    selected = next((item for item in candidates if item["ecosystem"] == preferred), candidates[0])
    return selected["packageId"]


def classify(relative: str, extension: str, entity_type: str) -> tuple[str, bool, bool]:
    if entity_type in {"SYMLINK", "JUNCTION"}:
        return "UNKNOWN", False, False
    parts = [part.lower() for part in PurePosixPath(relative).parts]
    name = parts[-1] if parts else ""
    generated = any(part in GENERATED_SEGMENTS or part.endswith("dist") for part in parts)
    vendor = any(part in VENDOR_SEGMENTS for part in parts)
    fixture = any(part in FIXTURE_SEGMENTS for part in parts)
    test = any(part in TEST_SEGMENTS for part in parts) or bool(
        re.search(r"(?:^|[._-])(?:test|spec)(?:[._-]|$)", name)
    )
    migration = any(part in {"migration", "migrations"} for part in parts)
    legal = bool(
        re.search(
            r"(?:^|[._-])(cla|license|licence|notice|copying|copyright)(?:[._-]|$)",
            name,
        )
    )
    documentation = extension in {".md", ".markdown", ".mdx"} or "docs" in parts
    packaging = (
        any(part in {"installer", "packaging", "resources"} for part in parts)
        or extension in {".app", ".dmg", ".entitlements", ".msi", ".plist"}
        or "electron-builder" in name
    )
    build = (
        name
        in {
            "cargo.lock",
            "cargo.toml",
            "package.json",
            "settings.gradle",
            "settings.gradle.kts",
            "yarn.lock",
        }
        or extension in {".gradle"}
        or any(part in {"workflows", ".github"} for part in parts)
        or bool(
            re.search(
                r"(?:^|[._-])(build|bundle|rollup|vite|vitest|webpack|tsconfig|eslint|prettier)",
                name,
            )
        )
    )
    config = (
        name.startswith(".")
        or extension in {".cfg", ".conf", ".ini", ".jsonc", ".toml", ".yaml", ".yml"}
        or name.endswith(".config.js")
        or name.endswith(".config.mjs")
        or name.endswith(".config.ts")
    )
    asset = extension in ASSET_EXTENSIONS and (
        any(part in RUNTIME_ASSET_SEGMENTS for part in parts)
        or extension not in {".css", ".csv", ".html", ".json"}
    )

    if generated:
        classification = "GENERATED"
    elif vendor:
        classification = "VENDOR"
    elif fixture:
        classification = "FIXTURE"
    elif test:
        classification = "TEST"
    elif migration:
        classification = "MIGRATION"
    elif legal:
        classification = "LEGAL"
    elif packaging:
        classification = "PACKAGING"
    elif build:
        classification = "BUILD"
    elif documentation:
        classification = "DOCUMENTATION"
    elif asset:
        classification = "ASSET"
    elif extension in SOURCE_EXTENSIONS:
        classification = "SOURCE"
    elif config:
        classification = "CONFIG"
    else:
        classification = "UNKNOWN"
    return classification, generated, vendor


def current_role(classification: str, entity_type: str, extension: str, relative: str) -> str:
    if entity_type == "DIRECTORY":
        return f"Repository directory; contents require {classification.lower()} ownership analysis"
    if entity_type == "SYMLINK":
        return "Symbolic link; target preserved as link evidence"
    if entity_type == "JUNCTION":
        return "Filesystem junction/reparse point; target is not traversed"
    if entity_type == "ARCHIVE":
        return f"Checked-in {extension or 'archive'} archive"
    roles = {
        "SOURCE": "Application, library, tool, or support source",
        "TEST": "Automated test or test support source",
        "FIXTURE": "Test fixture, snapshot, or sample input/output",
        "ASSET": "Static application, documentation, or media asset",
        "CONFIG": "Repository or tool configuration",
        "BUILD": "Build, dependency, workspace, or CI definition",
        "PACKAGING": "Installer, application packaging, or runtime resource definition",
        "MIGRATION": "Data or schema migration",
        "GENERATED": "Generated output present in the supplied corpus",
        "VENDOR": "Vendored third-party or package-manager material",
        "LEGAL": "Licence, notice, or legal source document",
        "DOCUMENTATION": "Repository or package documentation",
        "UNKNOWN": "Role not provable from path, extension, or manifest evidence",
    }
    if PurePosixPath(relative).name == "package.json":
        return "NPM/Yarn package manifest"
    if PurePosixPath(relative).name == "Cargo.toml":
        return "Cargo package or workspace manifest"
    return roles[classification]


def path_platforms(relative: str, extension: str) -> tuple[set[str], list[str]]:
    parts = [part.lower() for part in PurePosixPath(relative).parts]
    platforms: set[str] = set()
    evidence: list[str] = []
    for platform, markers in PLATFORM_PATH_MARKERS.items():
        matches = sorted(set(parts) & markers)
        if matches:
            platforms.add(platform)
            evidence.append(f"path segment(s) {', '.join(matches)}")
    if extension in PLATFORM_EXTENSIONS:
        platform = PLATFORM_EXTENSIONS[extension]
        platforms.add(platform)
        evidence.append(f"extension {extension}")
    if any(part.endswith(".xcodeproj") or part.endswith(".xcworkspace") for part in parts):
        platforms.add("IOS")
        evidence.append("Xcode project/workspace path")
    return platforms, evidence


def repository_platform(platforms: set[str]) -> str:
    desktop = platforms & {"WINDOWS", "MACOS", "LINUX"}
    mobile = platforms & {"ANDROID", "IOS"}
    if len(desktop) == 1 and not mobile:
        return next(iter(desktop))
    if len(desktop) > 1:
        return "CROSS_PLATFORM"
    if mobile:
        return "UNKNOWN"
    return "CROSS_PLATFORM"


def create_repository_records(
    raw_paths: list[dict[str, Any]], ownership_roots: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in raw_paths:
        path = item["absolutePath"]
        relative = item["relative"]
        extension = "" if item["entityType"] == "DIRECTORY" else full_extension(path)
        language = LANGUAGES.get(extension, "")
        if path.name in {"Dockerfile", "Containerfile"}:
            language = "Dockerfile"
        elif path.name in {"Makefile", "makefile"}:
            language = "Make"
        binary = (
            detected_binary(extension, item["sample"])
            if item["entityType"] in {"FILE", "ARCHIVE"}
            else False
        )
        classification, generated, vendor = classify(
            relative, extension, item["entityType"]
        )
        generation_evidence = generated_header_evidence(item["sample"], binary)
        if generation_evidence:
            generated = True
            if classification not in {"FIXTURE", "MIGRATION", "TEST", "VENDOR"}:
                classification = "GENERATED"
        platforms, platform_evidence = path_platforms(relative, extension)
        runtime_reachable = (
            "NO"
            if classification
            in {"TEST", "FIXTURE", "DOCUMENTATION", "LEGAL", "GENERATED"}
            else "UNKNOWN"
        )
        requires_analysis = (
            bool(item["hashError"])
            or classification == "UNKNOWN"
            or runtime_reachable == "UNKNOWN"
            or generated
            or binary
            or item["entityType"] in {"SYMLINK", "JUNCTION"}
        )
        record = {
            "path": codebase_path(relative),
            "entityType": item["entityType"],
            "extension": extension,
            "language": language,
            "sizeBytes": item["sizeBytes"],
            "sha256": item["sha256"],
            "package": package_for(relative, extension, ownership_roots),
            "platform": repository_platform(platforms),
            "classification": classification,
            "trackedState": "UNKNOWN",
            "generated": generated,
            "vendor": vendor,
            "binary": binary,
            "currentRole": current_role(
                classification, item["entityType"], extension, relative
            ),
            "likelyCapabilityIds": [],
            "runtimeReachable": runtime_reachable,
            "requiresFurtherAnalysis": requires_analysis,
            "trackedStateEvidence": (
                "No Git metadata/index is present. Ignore patterns cannot prove whether an "
                "existing path was tracked, so state remains UNKNOWN."
            ),
            "platformEvidence": platform_evidence,
            "generationEvidence": generation_evidence,
        }
        if item["hashError"]:
            record["hashError"] = item["hashError"]
        if item["linkTarget"]:
            record["linkTarget"] = item["linkTarget"]
        records.append(record)
    return records


def read_text(path: Path, limit: int = 5 * 1024 * 1024) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def markdown_reference_tokens(text: str) -> list[str]:
    delimiters = set("<>\"' \t\r\n()[]{}")
    tokens: list[str] = []
    for match in MARKDOWN_SUFFIX.finditer(text):
        start = match.start()
        while start > 0 and text[start - 1] not in delimiters:
            start -= 1
        token = text[start : match.end()]
        if token:
            tokens.append(token)
    return tokens


def apply_content_evidence(
    raw_paths: list[dict[str, Any]], records: list[dict[str, Any]]
) -> tuple[dict[str, list[str]], dict[str, list[str]], list[dict[str, str]]]:
    record_by_relative = {
        record["path"][len("Codebase/") :]: record for record in records
    }
    markdown_relatives = {
        relative
        for relative, record in record_by_relative.items()
        if record["extension"] in {".md", ".markdown"}
    }
    exact_references: dict[str, set[str]] = defaultdict(set)
    build_references: dict[str, set[str]] = defaultdict(set)
    unresolved: list[dict[str, str]] = []

    for item in raw_paths:
        if item["entityType"] != "FILE":
            continue
        relative = item["relative"]
        record = record_by_relative[relative]
        if record["binary"]:
            continue
        text = read_text(item["absolutePath"])
        if text is None:
            continue

        if record["classification"] in {"SOURCE", "CONFIG", "BUILD", "PACKAGING"}:
            detected, evidence = path_platforms(relative, record["extension"])
            for platform, pattern in PLATFORM_CONTENT_PATTERNS.items():
                match = pattern.search(text)
                if match:
                    detected.add(platform)
                    line = text.count("\n", 0, match.start()) + 1
                    evidence.append(f"content marker for {platform} at line {line}")
            record["platform"] = repository_platform(detected)
            record["platformEvidence"] = sorted(set(evidence))

        lowered_text = text.lower()
        if ".md" not in lowered_text and ".markdown" not in lowered_text:
            continue
        for token in markdown_reference_tokens(text):
            target = unquote(token).replace("\\", "/")
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^[a-z]+://", target, re.IGNORECASE):
                continue
            if target.startswith("Codebase/"):
                candidate = PurePosixPath(target[len("Codebase/") :])
            elif target.startswith("/"):
                candidate = PurePosixPath(target.lstrip("/"))
            else:
                candidate = PurePosixPath(relative).parent / target
            normalized_parts: list[str] = []
            escaped_root = False
            for part in candidate.parts:
                if part in {"", "."}:
                    continue
                if part == "..":
                    if normalized_parts:
                        normalized_parts.pop()
                    else:
                        escaped_root = True
                    continue
                normalized_parts.append(part)
            normalized = str(PurePosixPath(*normalized_parts))
            if not escaped_root and normalized in markdown_relatives:
                source = codebase_path(relative)
                exact_references[normalized].add(source)
                if record["classification"] in {"BUILD", "PACKAGING"}:
                    build_references[normalized].add(source)
            elif target.lower().endswith((".md", ".markdown")):
                unresolved.append(
                    {
                        "sourcePath": codebase_path(relative),
                        "referenceToken": target,
                        "normalizedCandidate": (
                            "" if escaped_root else codebase_path(normalized)
                        ),
                    }
                )

    return (
        {key: sorted(value) for key, value in exact_references.items()},
        {key: sorted(value) for key, value in build_references.items()},
        sorted(
            unresolved,
            key=lambda item: (
                item["sourcePath"].casefold(),
                item["referenceToken"].casefold(),
            ),
        ),
    )


def markdown_purpose(path: Path, classification: str) -> tuple[str, str]:
    text = read_text(path, 1024 * 1024) or ""
    heading = next(
        (
            match.group(1).strip()
            for line in text.splitlines()
            if (match := re.match(r"^#\s+(.+?)\s*$", line))
        ),
        "",
    )
    name = path.name.lower()
    if classification == "FIXTURE":
        purpose = "Test fixture Markdown"
    elif classification == "GENERATED":
        purpose = "Generated mapping or analysis Markdown"
    elif "readme" in name:
        purpose = "Repository or package README"
    elif "changelog" in name:
        purpose = "Change history"
    elif "security" in name:
        purpose = "Security policy"
    elif "contributing" in name:
        purpose = "Contribution guidance"
    elif (
        name.startswith("cla.")
        or "license" in name
        or "licence" in name
        or "notice" in name
    ):
        purpose = "Legal or attribution document"
    elif "docs" in [part.lower() for part in path.parts]:
        purpose = "Repository documentation"
    else:
        purpose = "Repository Markdown requiring purpose confirmation"
    return purpose, heading


def markdown_records(
    records: list[dict[str, Any]],
    exact_references: dict[str, list[str]],
    build_references: dict[str, list[str]],
) -> list[dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    for repository_record in records:
        if repository_record["extension"] not in {".md", ".markdown"}:
            continue
        relative = repository_record["path"][len("Codebase/") :]
        path = CODEBASE_ROOT / Path(*PurePosixPath(relative).parts)
        purpose, heading = markdown_purpose(path, repository_record["classification"])
        legal = repository_record["classification"] == "LEGAL"
        distribution_legal = bool(
            re.search(
                r"(?:^|[._-])(license|licence|notice|copying|copyright)(?:[._-]|$)",
                path.name.lower(),
            )
        )
        fixture = repository_record["classification"] == "FIXTURE"
        generated = repository_record["generated"]
        repository_documentation = (
            repository_record["classification"] in {"DOCUMENTATION", "LEGAL"}
            and not fixture
            and not generated
        )
        user_workspace_content = "UNKNOWN" if fixture else "NO"

        if fixture:
            decision = "RETAIN_IN_CODEBASE_FIXTURE_PENDING_ANALYSIS"
            destination = ""
            blockers = [
                "Fixture semantics must be verified before replacement, relocation, or exception."
            ]
            verification = ["FIXTURE_QA", "TEST_DISCOVERY", "REFERENCE_RECHECK"]
        elif generated:
            decision = "EXCLUDE_GENERATED_OUTPUT_PENDING_REGENERATION_DECISION"
            destination = (
                "Graphify/11 Completion/Imported Codebase Graphify Output/"
                + relative
            )
            blockers = [
                "Generated provenance and regeneration command must be confirmed."
            ]
            verification = ["GENERATOR_PROVENANCE", "REFERENCE_RECHECK"]
        else:
            decision = "MOVE_TO_GRAPHIFY_LATER"
            destination = "Graphify/12 Source Documents/Codebase Markdown/" + relative
            blockers = []
            verification = ["LINK_CHECK", "REFERENCE_RECHECK"]

        links = exact_references.get(relative, [])
        build_links = build_references.get(relative, [])
        if links:
            blockers.append("Inbound links must be rewritten in the future migration batch.")
        if build_links:
            blockers.append(
                "Build or packaging references must be updated and verified before migration."
            )
            verification.append("BUILD_OR_PACKAGING_CHECK")
        if legal:
            verification.extend(["LEGAL_REVIEW", "DISTRIBUTION_NOTICE_CHECK"])

        ledger.append(
            {
                "path": repository_record["path"],
                "sha256": repository_record["sha256"],
                "sizeBytes": repository_record["sizeBytes"],
                "package": repository_record["package"],
                "purpose": purpose,
                "firstHeading": heading,
                "isRepositoryDocumentation": repository_documentation,
                "generated": generated,
                "userWorkspaceContent": user_workspace_content,
                "legallyRequired": "YES" if distribution_legal else "UNKNOWN",
                "buildOrPackagingReferencesIt": bool(build_links),
                "buildOrPackagingReferences": build_links,
                "linksReferenceIt": bool(links),
                "linkReferences": links,
                "migrationDecision": decision,
                "requiredFinalGraphifyDestination": destination,
                "requiredPlainTextDistributionReplacement": (
                    "Graphify/12 Source Documents/Distribution Notices/"
                    + f"{path.stem}.txt"
                    if distribution_legal
                    else ""
                ),
                "migrationBlockers": sorted(set(blockers)),
                "plannedBatch": "FUTURE_MARKDOWN_MIGRATION_BATCH_UNASSIGNED",
                "verificationRequired": sorted(set(verification)),
                "status": "MAPPED_NOT_MOVED",
                "requiresFurtherAnalysis": fixture
                or generated
                or user_workspace_content == "UNKNOWN"
                or not repository_documentation,
            }
        )
    return ledger


def runtime_asset(record: dict[str, Any]) -> tuple[bool, list[str]]:
    relative = record["path"][len("Codebase/") :]
    parts = {part.lower() for part in PurePosixPath(relative).parts}
    runtime_evidence: list[str] = []
    if record["classification"] in {"ASSET", "PACKAGING"}:
        runtime_evidence.append(f"classification {record['classification']}")
    matching_segments = sorted(parts & RUNTIME_ASSET_SEGMENTS)
    if matching_segments and record["classification"] not in {
        "DOCUMENTATION",
        "FIXTURE",
        "LEGAL",
        "TEST",
    }:
        runtime_evidence.append(
            f"runtime asset path segment(s) {', '.join(matching_segments)}"
        )
    if record["extension"] in {
        ".dll",
        ".dylib",
        ".exe",
        ".node",
        ".so",
        ".wasm",
    } and record["classification"] not in {"FIXTURE", "TEST"}:
        runtime_evidence.append(f"native/runtime extension {record['extension']}")
    evidence = (
        (["binary file detection"] if record["binary"] else []) + runtime_evidence
    )
    return bool(runtime_evidence), evidence


def binary_kind(record: dict[str, Any]) -> str:
    extension = record["extension"]
    if extension in ARCHIVE_EXTENSIONS:
        return "ARCHIVE"
    if extension in {".dll", ".dylib", ".exe", ".node", ".so", ".wasm", ".a", ".lib"}:
        return "NATIVE_OR_EXECUTABLE"
    if extension in {".eot", ".otf", ".ttf", ".woff", ".woff2"}:
        return "FONT"
    if extension in {".bmp", ".gif", ".heic", ".icns", ".ico", ".jpeg", ".jpg", ".png", ".webp"}:
        return "IMAGE"
    if extension in {".avi", ".flac", ".m4a", ".mkv", ".mov", ".mp3", ".mp4", ".ogg", ".wav", ".webm"}:
        return "MEDIA"
    if extension in {".doc", ".docx", ".odg", ".odp", ".ods", ".odt", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"}:
        return "DOCUMENT"
    if extension in {".db", ".sqlite", ".sqlite3"}:
        return "DATABASE"
    return "BINARY_DATA" if record["binary"] else "TEXT_RUNTIME_ASSET"


def binary_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for record in records:
        if record["entityType"] not in {"FILE", "ARCHIVE"}:
            continue
        is_runtime, evidence = runtime_asset(record)
        if not record["binary"] and not is_runtime:
            continue
        output.append(
            {
                "path": record["path"],
                "sha256": record["sha256"],
                "sizeBytes": record["sizeBytes"],
                "extension": record["extension"],
                "package": record["package"],
                "platform": record["platform"],
                "classification": record["classification"],
                "binary": record["binary"],
                "binaryKind": binary_kind(record),
                "runtimeAsset": is_runtime,
                "runtimeReachable": record["runtimeReachable"],
                "evidence": evidence,
                "licenceOrProvenanceStatus": "REQUIRES_SEPARATE_LICENCE_MAPPING",
                "requiresFurtherAnalysis": True,
            }
        )
    return output


def inspect_archive(record: dict[str, Any]) -> dict[str, Any]:
    relative = record["path"][len("Codebase/") :]
    path = CODEBASE_ROOT / Path(*PurePosixPath(relative).parts)
    result = {
        "path": record["path"],
        "sha256": record["sha256"],
        "sizeBytes": record["sizeBytes"],
        "extension": record["extension"],
        "format": record["extension"].lstrip(".").upper(),
        "package": record["package"],
        "platform": record["platform"],
        "classification": record["classification"],
        "inspectionStatus": "METADATA_ONLY_UNSUPPORTED_FORMAT",
        "memberCount": None,
        "uncompressedSizeBytes": None,
        "encryptedMemberCount": None,
        "inspectionError": "",
        "extracted": False,
        "extractionDestination": "",
        "requiresFurtherAnalysis": True,
    }
    try:
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                members = archive.infolist()
                result.update(
                    {
                        "inspectionStatus": "VALID_ZIP_CENTRAL_DIRECTORY",
                        "memberCount": len(members),
                        "uncompressedSizeBytes": sum(member.file_size for member in members),
                        "encryptedMemberCount": sum(
                            bool(member.flag_bits & 0x1) for member in members
                        ),
                        "requiresFurtherAnalysis": any(
                            bool(member.flag_bits & 0x1) for member in members
                        ),
                    }
                )
        elif tarfile.is_tarfile(path):
            with tarfile.open(path, mode="r:*") as archive:
                members = archive.getmembers()
                result.update(
                    {
                        "inspectionStatus": "VALID_TAR_DIRECTORY",
                        "memberCount": len(members),
                        "uncompressedSizeBytes": sum(member.size for member in members),
                        "encryptedMemberCount": 0,
                        "requiresFurtherAnalysis": False,
                    }
                )
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        result["inspectionStatus"] = "INSPECTION_ERROR"
        result["inspectionError"] = f"{type(error).__name__}: {error}"
    return result


def archive_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [inspect_archive(record) for record in records if record["entityType"] == "ARCHIVE"]


def platform_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for record in records:
        if record["entityType"] not in {"FILE", "ARCHIVE"}:
            continue
        evidence = record.get("platformEvidence", [])
        if not evidence:
            continue
        detected = set()
        for platform, markers in PLATFORM_PATH_MARKERS.items():
            relative_parts = {
                part.lower()
                for part in PurePosixPath(record["path"][len("Codebase/") :]).parts
            }
            if relative_parts & markers:
                detected.add(platform)
        if record["extension"] in PLATFORM_EXTENSIONS:
            detected.add(PLATFORM_EXTENSIONS[record["extension"]])
        for platform in PLATFORM_CONTENT_PATTERNS:
            if any(f"content marker for {platform}" in item for item in evidence):
                detected.add(platform)
        output.append(
            {
                "path": record["path"],
                "sha256": record["sha256"],
                "sizeBytes": record["sizeBytes"],
                "extension": record["extension"],
                "package": record["package"],
                "repositoryPlatformValue": record["platform"],
                "detectedPlatforms": sorted(detected),
                "classification": record["classification"],
                "evidence": evidence,
                "detectionConfidence": (
                    "CONFIRMED_PATH_OR_EXTENSION"
                    if any(not item.startswith("content marker") for item in evidence)
                    else "DISCOVERY_SIGNAL_FROM_CONTENT"
                ),
                "runtimeReachable": record["runtimeReachable"],
                "requiresFurtherAnalysis": record["runtimeReachable"] == "UNKNOWN",
            }
        )
    return output


def assign_package_counts(
    package_document: dict[str, Any], records: list[dict[str, Any]]
) -> None:
    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"paths": 0, "files": 0, "bytes": 0}
    )
    for record in records:
        package_id = record["package"]
        if not package_id:
            continue
        counts[package_id]["paths"] += 1
        if record["entityType"] in {"FILE", "ARCHIVE"}:
            counts[package_id]["files"] += 1
            counts[package_id]["bytes"] += record["sizeBytes"]
    for package in package_document["packages"]:
        package_counts = counts[package["packageId"]]
        package["ownedPathCount"] = package_counts["paths"]
        package["ownedFileCount"] = package_counts["files"]
        package["ownedSizeBytes"] = package_counts["bytes"]


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(
                json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            )


def tree_digest(records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        if record["entityType"] not in {"FILE", "ARCHIVE"}:
            continue
        digest.update(record["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def markdown_table(counter: Counter[str], first: str, second: str) -> str:
    rows = [f"| {first} | {second} |", "|---|---:|"]
    rows.extend(f"| `{key or '(blank)'}` | {value:,} |" for key, value in counter.most_common())
    return "\n".join(rows)


def validate(
    raw_paths: list[dict[str, Any]],
    exclusions: list[dict[str, str]],
    records: list[dict[str, Any]],
    packages: dict[str, Any],
    markdown: list[dict[str, Any]],
    binaries: list[dict[str, Any]],
    archives: list[dict[str, Any]],
    platforms: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    required = {
        "path",
        "entityType",
        "extension",
        "language",
        "sizeBytes",
        "sha256",
        "package",
        "platform",
        "classification",
        "trackedState",
        "generated",
        "vendor",
        "binary",
        "currentRole",
        "likelyCapabilityIds",
        "runtimeReachable",
        "requiresFurtherAnalysis",
    }
    if exclusions:
        errors.append(f"Filesystem exclusions occurred: {exclusions!r}")
    if len(records) != len(raw_paths):
        errors.append(f"Record count {len(records)} != discovered path count {len(raw_paths)}")
    paths = [record["path"] for record in records]
    if len(paths) != len(set(paths)):
        errors.append("Duplicate paths in repository inventory")
    for record in records:
        missing = required - record.keys()
        if missing:
            errors.append(f"{record.get('path')}: missing keys {sorted(missing)}")
        if record["entityType"] not in ENTITY_ENUM:
            errors.append(f"{record['path']}: invalid entityType")
        if record["platform"] not in PLATFORM_ENUM:
            errors.append(f"{record['path']}: invalid platform")
        if record["classification"] not in CLASSIFICATION_ENUM:
            errors.append(f"{record['path']}: invalid classification")
        if record["trackedState"] not in TRACKED_ENUM:
            errors.append(f"{record['path']}: invalid trackedState")
        if record["runtimeReachable"] not in REACHABILITY_ENUM:
            errors.append(f"{record['path']}: invalid runtimeReachable")
        if record["entityType"] in {"FILE", "ARCHIVE"} and not re.fullmatch(
            r"[0-9a-f]{64}", record["sha256"]
        ):
            errors.append(f"{record['path']}: missing or invalid SHA-256")

    package_ids = [package["packageId"] for package in packages["packages"]]
    if len(package_ids) != len(set(package_ids)):
        duplicates = sorted(
            package_id for package_id, count in Counter(package_ids).items() if count > 1
        )
        errors.append(f"Duplicate package IDs: {duplicates}")
    record_paths = set(paths)
    for package in packages["packages"]:
        if package["manifestPath"] and package["manifestPath"] not in record_paths:
            errors.append(
                f"{package['packageId']}: missing manifest {package['manifestPath']}"
            )

    expected_markdown = {
        record["path"]
        for record in records
        if record["extension"] in {".md", ".markdown"}
    }
    if expected_markdown != {record["path"] for record in markdown}:
        errors.append("Markdown ledger path set does not match repository Markdown set")
    expected_archives = {
        record["path"] for record in records if record["entityType"] == "ARCHIVE"
    }
    if expected_archives != {record["path"] for record in archives}:
        errors.append("Archive inventory path set does not match repository archives")
    for record in binaries:
        if record["path"] not in record_paths or not (
            record["binary"] or record["runtimeAsset"]
        ):
            errors.append(f"Invalid binary/runtime asset record {record['path']}")
    for record in platforms:
        if record["path"] not in record_paths or not record["evidence"]:
            errors.append(f"Invalid platform record {record['path']}")
    return errors


def build_summary(
    records: list[dict[str, Any]],
    exclusions: list[dict[str, str]],
    packages: dict[str, Any],
    markdown: list[dict[str, Any]],
    binaries: list[dict[str, Any]],
    archives: list[dict[str, Any]],
    platforms: list[dict[str, Any]],
    unresolved_references: list[dict[str, str]],
) -> str:
    entity_counts = Counter(record["entityType"] for record in records)
    class_counts = Counter(record["classification"] for record in records)
    language_counts = Counter(
        record["language"] for record in records if record["language"]
    )
    package_counts = Counter(
        package["ecosystem"] for package in packages["packages"]
    )
    markdown_decisions = Counter(
        record["migrationDecision"] for record in markdown
    )
    platform_counts = Counter(
        platform
        for record in platforms
        for platform in record["detectedPlatforms"]
    )
    largest_files = sorted(
        (
            record
            for record in records
            if record["entityType"] in {"FILE", "ARCHIVE"}
        ),
        key=lambda record: (-record["sizeBytes"], record["path"].casefold()),
    )[:20]
    binary_file_count = sum(
        record["entityType"] in {"FILE", "ARCHIVE"} and record["binary"]
        for record in records
    )
    runtime_assets = sum(record["runtimeAsset"] for record in binaries)
    generated_count = sum(record["generated"] for record in records)
    vendor_count = sum(record["vendor"] for record in records)
    total_bytes = sum(
        record["sizeBytes"]
        for record in records
        if record["entityType"] in {"FILE", "ARCHIVE"}
    )
    nested_git = [
        record["path"]
        for record in records
        if PurePosixPath(record["path"]).name in {".git", ".gitmodules"}
    ]
    unknown_tracked = sum(record["trackedState"] == "UNKNOWN" for record in records)

    largest_rows = "\n".join(
        f"| `{record['path']}` | {record['sizeBytes']:,} | `{record['sha256']}` |"
        for record in largest_files
    )
    exclusion_text = (
        "\n".join(
            f"- `{item['path']}` — {item['reason']}" for item in exclusions
        )
        if exclusions
        else "None. The deterministic scan completed without path or hash exclusions."
    )
    nested_text = (
        ", ".join(f"`{path}`" for path in nested_git)
        if nested_git
        else "None detected."
    )

    return f"""# MindRoom Codebase Corpus Summary

Generated: `{utc_now()}`

## Scope and evidence

- Source root: `{CODEBASE_ROOT}`
- Inventory root notation: `Codebase/...`
- Generator: `Graphify/01 Corpus Inventory/generate_inventory.py` version `{SCRIPT_VERSION}`
- Ordering: case-insensitive relative path, with original path as the tie-breaker
- Repository evidence type: `HASH_MANIFEST`
- Corpus content baseline SHA-256: `{tree_digest(records)}`
- Git metadata: absent; `git rev-parse --show-toplevel` failed for `Codebase`
- Tracked-state policy: all `{unknown_tracked:,}` discovered paths are `UNKNOWN`. A `.gitignore` match cannot prove whether an already-present file was tracked without the Git index.
- Nested Git indicators: {nested_text}

## Completeness

- Total inventoried paths below `Codebase/`: **{len(records):,}**
- Regular files: **{entity_counts['FILE']:,}**
- Archives represented with `entityType=ARCHIVE`: **{entity_counts['ARCHIVE']:,}**
- Directories: **{entity_counts['DIRECTORY']:,}**
- Symlinks: **{entity_counts['SYMLINK']:,}**
- Junctions/reparse points: **{entity_counts['JUNCTION']:,}**
- Total regular-file/archive bytes: **{total_bytes:,}**
- Files/archives with SHA-256: **{entity_counts['FILE'] + entity_counts['ARCHIVE']:,}**
- Hash failures: **{sum(bool(record.get('hashError')) for record in records):,}**
- Generated paths: **{generated_count:,}**
- Vendor paths: **{vendor_count:,}**
- Binary files/archives: **{binary_file_count:,}**

Exclusions:

{exclusion_text}

## Package inventory

- Package records: **{len(packages['packages']):,}**
- Workspace records: **{len(packages['workspaces']):,}**
- Manifests with parse failures: **{sum(package['parseStatus'] == 'INVALID' for package in packages['packages']):,}**

{markdown_table(package_counts, 'Ecosystem', 'Packages')}

Package ownership is assigned to the deepest discovered package root. Rust files prefer a Cargo package at the same root; Android/Gradle files prefer a Gradle module; other files prefer the NPM/Yarn package. Cargo packages not explicitly listed in the root `workspace.members` remain mapped, with membership confirmation deferred rather than guessed.

## Markdown migration inventory

- Markdown files mapped: **{len(markdown):,}**
- Markdown files with inbound resolved links: **{sum(record['linksReferenceIt'] for record in markdown):,}**
- Markdown files referenced by build/packaging-classified files: **{sum(record['buildOrPackagingReferencesIt'] for record in markdown):,}**
- Unresolved Markdown-like reference tokens found during bounded text scanning: **{len(unresolved_references):,}**

{markdown_table(markdown_decisions, 'Migration decision', 'Files')}

No Markdown was moved. Fixture Markdown is retained pending fixture semantics and test-discovery proof. Generated Markdown is mapped separately pending generator-provenance review. Other repository Markdown receives a planned Graphify destination; legal Markdown also receives a planned plain-text distribution notice.

## Binary, runtime, archive, and platform assets

- Binary/runtime inventory records: **{len(binaries):,}**
- Runtime-asset candidates: **{runtime_assets:,}**
- Archive records: **{len(archives):,}**
- Platform-file records: **{len(platforms):,}**

{markdown_table(platform_counts, 'Detected platform', 'Files')}

Mobile paths are represented as `UNKNOWN` in `REPOSITORY_INVENTORY.jsonl` because the locked repository schema only permits Windows, macOS, Linux, cross-platform, or unknown. `PLATFORM_FILE_INVENTORY.jsonl` preserves `ANDROID` and `IOS` explicitly.

## Classification counts

{markdown_table(class_counts, 'Classification', 'Paths')}

## Language counts

{markdown_table(language_counts, 'Language', 'Files')}

## Largest checked-in files

| Path | Bytes | SHA-256 |
|---|---:|---|
{largest_rows}

## Validation

- All seven JSON/JSONL/Markdown deliverables were populated.
- Every discovered file and directory has exactly one repository-inventory record.
- Every regular file and archive has a 64-character lowercase SHA-256.
- Required repository-inventory fields and enums validate.
- JSON and JSONL parse validation passed.
- Markdown, archive, binary/runtime, and platform subset paths resolve to repository-inventory records.
- No Codebase files were written, moved, deleted, formatted, quarantined, or installed into.

## Limitations and handoff

- `trackedState` cannot be resolved beyond `UNKNOWN` without authentic Git metadata and its index.
- Runtime reachability is intentionally `UNKNOWN` unless the inventory role proves non-runtime; architecture/runtime-registration agents must establish executable reachability.
- Platform content detection is a discovery signal, not proof of an executable platform branch.
- Markdown link discovery reads non-binary files up to 5 MiB and resolves explicit `.md`/`.markdown` path tokens; unresolved tokens are counted but are not fabricated as links.
- Archive inspection reads ZIP central directories and TAR metadata without extraction; unsupported formats remain metadata-only.
- Licence/provenance conclusions belong to the separate licence mapping and are not inferred here.
- Ponytail Audit was classification-only in this slice; no cleanup recommendation is promoted to deletion proof and no source change was applied.
"""


def validate_serialized_files() -> None:
    json.loads(PACKAGE_INVENTORY.read_text(encoding="utf-8"))
    for path in (
        REPOSITORY_INVENTORY,
        MARKDOWN_LEDGER,
        BINARY_INVENTORY,
        ARCHIVE_INVENTORY,
        PLATFORM_INVENTORY,
    ):
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ValueError(f"{path.name}:{line_number} is not a JSON object")


def main() -> None:
    if not CODEBASE_ROOT.is_dir():
        raise SystemExit(f"Codebase root not found: {CODEBASE_ROOT}")
    raw_paths, exclusions = scan_paths()
    if exclusions:
        raise SystemExit(
            "Inventory aborted because complete enumeration was not possible: "
            + json.dumps(exclusions, ensure_ascii=False)
        )

    packages, ownership_roots = package_inventory(raw_paths)
    records = create_repository_records(raw_paths, ownership_roots)
    exact_references, build_references, unresolved_references = apply_content_evidence(
        raw_paths, records
    )
    markdown = markdown_records(records, exact_references, build_references)
    binaries = binary_records(records)
    archives = archive_records(records)
    platforms = platform_records(records)
    assign_package_counts(packages, records)

    errors = validate(
        raw_paths,
        exclusions,
        records,
        packages,
        markdown,
        binaries,
        archives,
        platforms,
    )
    if errors:
        raise SystemExit("Inventory validation failed:\n- " + "\n- ".join(errors))

    write_jsonl(REPOSITORY_INVENTORY, records)
    write_json(PACKAGE_INVENTORY, packages)
    write_jsonl(MARKDOWN_LEDGER, markdown)
    write_jsonl(BINARY_INVENTORY, binaries)
    write_jsonl(ARCHIVE_INVENTORY, archives)
    write_jsonl(PLATFORM_INVENTORY, platforms)
    CORPUS_SUMMARY.write_text(
        build_summary(
            records,
            exclusions,
            packages,
            markdown,
            binaries,
            archives,
            platforms,
            unresolved_references,
        ),
        encoding="utf-8",
        newline="\n",
    )
    validate_serialized_files()

    print(
        json.dumps(
            {
                "paths": len(records),
                "files": sum(
                    record["entityType"] in {"FILE", "ARCHIVE"} for record in records
                ),
                "directories": sum(
                    record["entityType"] == "DIRECTORY" for record in records
                ),
                "packages": len(packages["packages"]),
                "workspaces": len(packages["workspaces"]),
                "markdown": len(markdown),
                "binaryRuntimeAssets": len(binaries),
                "archives": len(archives),
                "platformFiles": len(platforms),
                "treeSha256": tree_digest(records),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
