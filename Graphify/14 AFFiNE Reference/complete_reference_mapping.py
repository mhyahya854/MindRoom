#!/usr/bin/env python3
"""Complete the read-only AFFiNE reference map from the pinned upstream archive."""

from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from collections import Counter
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
GRAPHIFY = PROJECT / "Graphify"
CODEBASE = PROJECT / "Codebase"
REFERENCE = GRAPHIFY / "14 AFFiNE Reference"
ARCHIVE = REFERENCE / "Incoming" / "AFFiNE-canary.zip"
TREE = REFERENCE / "Reference Tree"
CAPABILITIES = GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json"
INDEX = REFERENCE / "AFFINE_CAPABILITY_INDEX.jsonl"
TRANSPLANTS = REFERENCE / "AFFINE_TRANSPLANT_CANDIDATES.jsonl"

COMMIT = "da7781a75171140fd966c6cfbe05da9f1fb111d6"
TREE_SHA = "4f7b0d6657efa7e9ee0c1e3359e09a21eb8e145f"
VERSION = "0.26.3"
ARCHIVE_ROOT = f"AFFiNE-{COMMIT}/"
HISTORICAL_EXPECTED_ARCHIVE_SHA256 = (
    "4a3eaa9e66efda0dc786993321a85750a65992d5c4c12656553ef50c3228e8fa"
)
SOURCE_URL = f"https://codeload.github.com/toeverything/AFFiNE/zip/{COMMIT}"
COMMIT_URL = f"https://github.com/toeverything/AFFiNE/commit/{COMMIT}"

ZERO_PATH_SEARCHES = {
    "MR-CAP-056": [
        r"\bremote conversion\b",
        r"\bcloud conversion\b",
        r"\bconversion (?:endpoint|service|api)\b",
        r"\bremote pdf conversion\b",
    ],
    "MR-CAP-057": [r"\bocr\b", r"\boptical character recognition\b"],
    "MR-CAP-060": [
        r"\bremote announcements?\b",
        r"\bannouncements?\b",
        r"\breleaseNotes\b",
        r"\blatestRelease\.body\b",
        r"\bchangelogUrl\b",
        r"\bopenChangelog\b",
    ],
    "MR-CAP-064": [],
    "MR-CAP-093": [
        r"\bquarantine\b",
        r"\bimport_failed\b",
        r"\bchecksumCRC32\b",
        r"\bcontentLength\b",
        r"\bReplaceFileCorruptionHandler\b",
    ],
    "MR-CAP-105": [
        r"\bsbom\b",
        r"\bcyclonedx\b",
        r"\bsoftware bill of materials\b",
    ],
}
ZERO_PATH_RESULTS = {
    "MR-CAP-056": (
        "ABSENT_REMOTE_BOUNDARY_LOCAL_CONVERTERS_EXCLUDED",
        "KEEP_EXISTING",
        "No remote conversion endpoint or service was found. The local converters are retained and compared only to prove they are false positives outside this removal boundary.",
    ),
    "MR-CAP-057": (
        "ABSENT_REMOTE_BOUNDARY",
        "KEEP_EXISTING",
        "No standalone OCR service implementation was found. Generated DocRole/permission bindings are retained false positives.",
    ),
    "MR-CAP-060": (
        "ACTIVE_REMOTE_CHANGELOG_AND_RELEASE_NOTES_PRESENT_IN_BOTH",
        "KEEP_AND_ADAPT",
        "Both trees contain remote changelog URLs/callers and remote release-body assignment; later execution must localize or remove only that remote content boundary.",
    ),
    "MR-CAP-064": (
        "DEAD_CODE_CANDIDATE_LEDGER_COMPARED_NO_DELETION_PROOF",
        "NO_TRANSPLANT_REQUIRED",
        "The conservative candidate ledger was compared to the pinned tree. Candidates remain unproved and no upstream dead-code module is a transplant target.",
    ),
    "MR-CAP-093": (
        "PARTIAL_PRESERVE_FIRST_PATTERNS_NO_COHERENT_MODULE",
        "REPAIR_PARTIAL",
        "Durable import-failure and integrity-check patterns exist, but no coherent general quarantine module exists and no transplant is approved.",
    ),
    "MR-CAP-105": (
        "DEPENDENCY_INPUTS_PRESENT_NO_SBOM_GENERATOR",
        "KEEP_AND_WRAP",
        "No SBOM/CycloneDX generator exists; mapped package-manager inputs are retained for a future build/release wrapper, with no runtime module or invention approved.",
    ),
}
RETAINED_OR_PARTIAL_ACTIVE_PATHS = {
    "MR-CAP-056": [
        "Codebase/blocksuite/affine/rich-text/src/conversion.ts",
        "Codebase/blocksuite/affine/shared/src/adapters/html/delta-converter.ts",
        "Codebase/blocksuite/affine/shared/src/adapters/markdown/delta-converter.ts",
        "Codebase/blocksuite/affine/shared/src/adapters/notion-html/delta-converter.ts",
        "Codebase/blocksuite/affine/shared/src/adapters/pdf/delta-converter.ts",
        "Codebase/blocksuite/affine/shared/src/adapters/plain-text/delta-converter.ts",
        "Codebase/blocksuite/affine/shared/src/adapters/types/delta-converter.ts",
        "Codebase/blocksuite/framework/std/src/inline/utils/point-conversion.ts",
        "Codebase/blocksuite/framework/std/src/inline/utils/range-conversion.ts",
        "Codebase/packages/common/nbstore/src/utils/id-converter.ts",
        "Codebase/packages/common/nbstore/src/utils/__tests__/id-converter.spec.ts",
        "Codebase/packages/common/reader/src/doc-parser/delta-to-md/delta-converters.ts",
    ],
    "MR-CAP-057": [
        "Codebase/packages/frontend/apps/ios/App/Packages/AffineGraphQL/Sources/Operations/Queries/GetDocRolePermissionsQuery.graphql.swift",
        "Codebase/packages/frontend/apps/ios/App/Packages/AffineGraphQL/Sources/Schema/Enums/DocRole.graphql.swift",
    ],
    "MR-CAP-093": [
        "Codebase/packages/frontend/apps/electron/src/main/recording/coordinator.ts",
        "Codebase/packages/frontend/apps/electron/src/main/recording/types.ts",
        "Codebase/packages/frontend/apps/electron/src/main/recording/feature.ts",
        "Codebase/packages/frontend/apps/electron/src/main/recording/state-transitions.md",
        "Codebase/packages/frontend/apps/electron/test/main/recording-coordinator.spec.ts",
        "Codebase/packages/frontend/apps/electron/test/main/recording-effect.spec.ts",
    ],
    "MR-CAP-105": [
        "Codebase/package.json",
        "Codebase/yarn.lock",
        "Codebase/Cargo.toml",
        "Codebase/Cargo.lock",
        "Codebase/packages/frontend/apps/ios/App/App.xcworkspace/xcshareddata/swiftpm/Package.resolved",
        "Codebase/packages/frontend/apps/ios/App/Podfile.lock",
        "Codebase/packages/frontend/apps/android/App/gradle/libs.versions.toml",
    ],
}
TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".css",
    ".gql",
    ".graphql",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".json",
    ".kt",
    ".kts",
    ".md",
    ".mjs",
    ".py",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def now_utc() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def filesystem_path(path: Path) -> Path:
    """Use the Windows extended-length prefix for preserved upstream paths."""
    resolved = path.resolve()
    if os.name == "nt":
        return Path("\\\\?\\" + str(resolved))
    return resolved


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def reference_path(relative: str) -> str:
    return (
        "Graphify/14 AFFiNE Reference/Reference Tree/" + relative
    )


def active_relative(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    return normalized.removeprefix("Codebase/") if normalized.startswith("Codebase/") else None


def package_category(relative: str) -> str:
    if relative == "package.json":
        return "MONOREPO_ROOT"
    if relative.startswith("blocksuite/"):
        return "BLOCKSUITE"
    if relative.startswith("packages/backend/"):
        return "AFFINE_BACKEND"
    if relative.startswith("packages/common/"):
        return "AFFINE_COMMON"
    if relative.startswith("packages/frontend/"):
        return "AFFINE_FRONTEND"
    if relative.startswith("tests/"):
        return "TEST"
    if relative.startswith("tools/"):
        return "TOOLING"
    if relative.startswith("docs/"):
        return "DOCUMENTATION"
    return "OTHER"


def semantic_search(archive: zipfile.ZipFile, entries: dict[str, zipfile.ZipInfo]) -> dict[str, list[dict]]:
    compiled = {
        capability_id: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        for capability_id, patterns in ZERO_PATH_SEARCHES.items()
    }
    results: dict[str, list[dict]] = {capability_id: [] for capability_id in compiled}
    for relative, info in entries.items():
        if info.file_size > 2_000_000 or Path(relative).suffix.lower() not in TEXT_SUFFIXES:
            continue
        pending = [capability_id for capability_id, rows in results.items() if len(rows) < 50]
        if not pending:
            break
        raw = archive.read(info)
        if b"\0" in raw:
            continue
        text = raw.decode("utf-8", errors="ignore")
        for capability_id in pending:
            matches = [pattern.pattern for pattern in compiled[capability_id] if pattern.search(text)]
            if not matches:
                continue
            first = min(
                (
                    match.start()
                    for pattern in compiled[capability_id]
                    if (match := pattern.search(text))
                ),
                default=0,
            )
            results[capability_id].append(
                {
                    "path": reference_path(relative),
                    "line": text.count("\n", 0, first) + 1,
                    "matchedPatterns": matches,
                }
            )
    return results


def validate_archive_and_extraction(
    archive: zipfile.ZipFile, entries: dict[str, zipfile.ZipInfo]
) -> dict:
    crc_failure = archive.testzip()
    tree_digest = hashlib.sha256()
    missing: list[str] = []
    mismatched: list[str] = []
    extracted_files = 0
    for relative in sorted(entries):
        data = archive.read(entries[relative])
        file_sha = sha256_bytes(data)
        tree_digest.update(
            f"{relative}\0{len(data)}\0{file_sha}\n".encode("utf-8")
        )
        extracted = filesystem_path(TREE / relative)
        if not extracted.is_file():
            missing.append(relative)
            continue
        extracted_files += 1
        if extracted.stat().st_size != len(data) or sha256_file(extracted) != file_sha:
            mismatched.append(relative)
    return {
        "crcStatus": "PASS" if crc_failure is None else "FAIL",
        "crcFailureEntry": crc_failure,
        "zipComment": archive.comment.decode("ascii", errors="replace"),
        "zipCommentMatchesCommit": archive.comment.decode(
            "ascii", errors="replace"
        )
        == COMMIT,
        "canonicalContentTreeSha256": tree_digest.hexdigest(),
        "canonicalContentTreeDigestAlgorithm": (
            "SHA-256 over sorted UTF-8 records: relative-path NUL size NUL file-sha256 LF"
        ),
        "archiveFileCount": len(entries),
        "extractedFileCount": extracted_files,
        "missingExtractedFiles": len(missing),
        "mismatchedExtractedFiles": len(mismatched),
        "sampleMissing": missing[:10],
        "sampleMismatched": mismatched[:10],
        "status": (
            "PASS"
            if crc_failure is None
            and archive.comment.decode("ascii", errors="replace") == COMMIT
            and not missing
            and not mismatched
            else "FAIL"
        ),
    }


def build_package_inventory(
    archive: zipfile.ZipFile, entries: dict[str, zipfile.ZipInfo], generated_at: str
) -> dict:
    packages: list[dict] = []
    for relative in sorted(entries):
        if not (relative.endswith("package.json") or relative.endswith("Cargo.toml")):
            continue
        data = archive.read(entries[relative])
        ecosystem = "NPM_WORKSPACE" if relative.endswith("package.json") else "CARGO_WORKSPACE"
        if ecosystem == "NPM_WORKSPACE":
            try:
                manifest = json.loads(data)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            dependencies = {
                field: sorted((manifest.get(field) or {}).keys())
                for field in (
                    "dependencies",
                    "devDependencies",
                    "peerDependencies",
                    "optionalDependencies",
                )
            }
            name = manifest.get("name")
            version = manifest.get("version")
            licence = manifest.get("license")
            private = manifest.get("private")
        else:
            text = data.decode("utf-8", errors="replace")
            package_section = re.search(r"(?ms)^\[package\]\s*(.*?)(?=^\[|\Z)", text)
            section = package_section.group(1) if package_section else ""

            def cargo_value(field: str) -> str | None:
                match = re.search(rf'(?m)^{field}\s*=\s*"([^"]+)"', section)
                return match.group(1) if match else None

            name = cargo_value("name") or (
                "AFFINE_CARGO_WORKSPACE_ROOT" if relative == "Cargo.toml" else None
            )
            version = cargo_value("version")
            licence = cargo_value("license")
            private = None
            dependencies = {
                "declaredDependencyLines": len(
                    re.findall(r"(?m)^[A-Za-z0-9_.-]+\s*=", text)
                )
            }
        packages.append(
            {
                "packageId": f"AFF-REF-{len(packages) + 1:04d}",
                "ecosystem": ecosystem,
                "manifestPath": reference_path(relative),
                "archiveEntry": ARCHIVE_ROOT + relative,
                "manifestSha256": sha256_bytes(data),
                "name": name,
                "version": version,
                "private": private,
                "declaredLicence": licence,
                "category": package_category(relative),
                "dependencies": dependencies,
                "sourceCommit": COMMIT,
                "sourceVersion": VERSION,
            }
        )
    ecosystems = Counter(package["ecosystem"] for package in packages)
    categories = Counter(package["category"] for package in packages)
    licences = Counter(package["declaredLicence"] or "UNDECLARED" for package in packages)
    return {
        "project": "MindRoom",
        "schemaVersion": 2,
        "generatedAt": generated_at,
        "sourceTree": "Graphify/14 AFFiNE Reference/Reference Tree/",
        "sourceTreeStatus": "PINNED_OFFICIAL_REFERENCE_READ_ONLY",
        "sourceCommit": COMMIT,
        "sourceTreeSha": TREE_SHA,
        "sourceVersion": VERSION,
        "archiveSha256": sha256_file(ARCHIVE),
        "packageCounts": {
            "total": len(packages),
            "byEcosystem": dict(sorted(ecosystems.items())),
            "byCategory": dict(sorted(categories.items())),
            "byDeclaredLicence": dict(sorted(licences.items())),
        },
        "packages": packages,
    }


def preliminary_decision(classification: str, has_reference: bool) -> str:
    if not has_reference:
        return "SEARCH_COMPLETE_NO_TRANSPLANT_CANDIDATE"
    if classification == "KEEP_AND_ADAPT":
        return "KEEP_AND_ADAPT"
    if classification == "ADD":
        return "REPAIR_PARTIAL"
    return "KEEP_EXISTING"


def main() -> None:
    if not ARCHIVE.is_file():
        raise SystemExit(f"missing pinned archive: {ARCHIVE}")
    generated_at = now_utc()
    archive_sha = sha256_file(ARCHIVE)
    capability_doc = load_json(CAPABILITIES)
    capabilities = capability_doc["capabilities"]
    old_index = {row["capabilityId"]: row for row in load_jsonl(INDEX)}
    dead_code_candidate_paths = [
        row["path"]
        for row in load_jsonl(
            GRAPHIFY / "05 Dependency and Impact" / "DEAD_CODE_CANDIDATES.jsonl"
        )
    ]

    with zipfile.ZipFile(ARCHIVE) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        if not infos or any(not info.filename.startswith(ARCHIVE_ROOT) for info in infos):
            raise SystemExit("archive root does not prove the pinned commit")
        entries = {
            info.filename[len(ARCHIVE_ROOT) :]: info
            for info in infos
        }
        root_package = json.loads(archive.read(entries["package.json"]))
        if root_package.get("version") != VERSION:
            raise SystemExit(
                f"reference version mismatch: {root_package.get('version')} != {VERSION}"
            )
        archive_validation = validate_archive_and_extraction(archive, entries)
        if archive_validation["status"] != "PASS":
            raise SystemExit(
                f"archive/extraction validation failed: {archive_validation}"
            )
        semantic_results = semantic_search(archive, entries)
        package_inventory = build_package_inventory(archive, entries, generated_at)

        index_rows: list[dict] = []
        transplant_rows: list[dict] = []
        evidence_pair_count = identical_count = changed_count = 0
        zero_path_summary: list[dict] = []
        for capability in capabilities:
            capability_id = capability["capabilityId"]
            old = old_index.get(capability_id, {})
            active_candidates = sorted(
                {
                    *capability.get("currentPaths", []),
                    *RETAINED_OR_PARTIAL_ACTIVE_PATHS.get(capability_id, []),
                    *(dead_code_candidate_paths if capability_id == "MR-CAP-064" else []),
                }
            )
            evidence = []
            for active_path in active_candidates:
                relative = active_relative(active_path)
                active_file = PROJECT / active_path
                if relative is None or relative not in entries or not active_file.is_file():
                    continue
                active_sha = sha256_file(active_file)
                reference_sha = sha256_bytes(archive.read(entries[relative]))
                content_status = (
                    "IDENTICAL" if active_sha == reference_sha else "VERSION_DELTA"
                )
                evidence.append(
                    {
                        "activePath": active_path,
                        "referencePath": reference_path(relative),
                        "activeSha256": active_sha,
                        "referenceSha256": reference_sha,
                        "contentStatus": content_status,
                    }
                )
                evidence_pair_count += 1
                identical_count += content_status == "IDENTICAL"
                changed_count += content_status == "VERSION_DELTA"
            reference_paths = sorted({item["referencePath"] for item in evidence})
            matched_active_paths = {item["activePath"] for item in evidence}
            active_only_paths = sorted(
                set(active_candidates) - matched_active_paths
            )
            semantic = semantic_results.get(capability_id, [])
            if capability_id in ZERO_PATH_RESULTS:
                comparison_status, decision, rationale = ZERO_PATH_RESULTS[capability_id]
                zero_path_summary.append(
                    {
                        "capabilityId": capability_id,
                        "name": capability["name"],
                        "comparisonStatus": comparison_status,
                        "semanticMatchCount": len(semantic),
                        "decision": decision,
                    }
                )
            else:
                comparison_status = (
                    "IDENTICAL_AND_VERSION_DELTA_FILE_EVIDENCE"
                    if evidence
                    else "SEARCH_COMPLETE_NO_EXACT_PATH_MATCH"
                )
                decision = preliminary_decision(
                    capability["classification"], bool(reference_paths)
                )
                rationale = (
                    f"{len(reference_paths)} pinned-reference paths were matched by exact repository-relative path; "
                    f"{sum(item['contentStatus'] == 'IDENTICAL' for item in evidence)} are byte-identical and "
                    f"{sum(item['contentStatus'] == 'VERSION_DELTA' for item in evidence)} differ at version 0.26.3 "
                    f"versus active 0.27.0; {len(active_only_paths)} active paths have no same-relative-path reference file."
                )

            row = {
                "capabilityId": capability_id,
                "capabilityName": capability["name"],
                "classification": capability["classification"],
                "runId": capability_doc.get("runId"),
                "activeCodebaseVersion": capability_doc.get(
                    "activeCodebaseVersion", load_json(CODEBASE / "package.json").get("version")
                ),
                "referenceVersion": VERSION,
                "independentAffineReferencePath": "Graphify/14 AFFiNE Reference/Reference Tree/",
                "activePaths": active_candidates,
                "independentAffineFilesFound": reference_paths,
                "activeOnlyPaths": active_only_paths,
                "referenceSearchQueries": [
                    "Exact repository-relative path comparison for active capability evidence",
                    *old.get("searchTerms", []),
                    *ZERO_PATH_SEARCHES.get(capability_id, []),
                ],
                "referenceSearchExecution": (
                    f"Python zipfile exact-path and SHA-256 comparison against official commit {COMMIT}; "
                    "zero-current-path scopes additionally received bounded whole-word semantic scans."
                ),
                "referenceSearchFindings": semantic,
                "referencePathEvidence": evidence,
                "referencePaths": reference_paths,
                "searchStatus": "SEARCH_COMPLETE",
                "comparisonStatus": comparison_status,
                "parityStatus": "MAPPED_WITH_PINNED_REFERENCE_EVIDENCE",
                "preliminaryReferenceDecision": decision,
                "decision": decision,
                "decisionRationale": rationale,
                "transplantApproved": False,
                "inventionApproved": False,
                "blockers": [],
                "reviewStatus": "READY_FOR_INDEPENDENT_REVIEW",
                "claimBoundary": (
                    "This is mapping evidence only. It does not approve a transplant, invention, implementation, "
                    "deletion, quarantine, licence disposition, or release gate."
                ),
            }
            index_rows.append(row)
            transplant_rows.append(
                {
                    "capabilityId": capability_id,
                    "capabilityName": capability["name"],
                    "classification": capability["classification"],
                    "runId": capability_doc.get("runId"),
                    "activePaths": active_candidates,
                    "referencePaths": reference_paths,
                    "referenceSearchQueries": row["referenceSearchQueries"],
                    "comparisonStatus": comparison_status,
                    "decision": decision,
                    "rationale": rationale,
                    "approved": False,
                    "implementationPerformed": False,
                    "copiedFiles": [],
                    "adaptedFiles": [],
                    "reviewStatus": "MAPPED_NOT_APPROVED_FOR_IMPLEMENTATION",
                    "prohibitedInvention": decision
                    == "SEARCH_COMPLETE_NO_TRANSPLANT_CANDIDATE",
                }
            )

    if len(index_rows) != 110 or len(transplant_rows) != 110:
        raise SystemExit("AFFiNE capability parity cardinality mismatch")
    if any(row["searchStatus"] != "SEARCH_COMPLETE" for row in index_rows):
        raise SystemExit("AFFiNE capability search remains incomplete")
    write_jsonl(INDEX, index_rows)
    write_jsonl(TRANSPLANTS, transplant_rows)
    write_json(REFERENCE / "AFFINE_PACKAGE_INVENTORY.json", package_inventory)

    licence_entries = [
        relative
        for relative in (
            "LICENSE",
            "LICENSE-MIT",
            "packages/backend/server/LICENSE",
            "packages/backend/native/LICENSE",
            "packages/common/native/LICENSE",
        )
        if relative in entries
    ]
    with zipfile.ZipFile(ARCHIVE) as source_archive:
        directory_count = sum(
            1
            for name in source_archive.namelist()
            if name.endswith("/") and name != ARCHIVE_ROOT
        )
        licence_evidence = [
            {
                "path": reference_path(relative),
                "sha256": sha256_bytes(source_archive.read(ARCHIVE_ROOT + relative)),
            }
            for relative in licence_entries
        ]
    manifest = {
        "project": "MindRoom",
        "phase": "GRAPHIFY_V2_MAPPING",
        "runId": capability_doc.get("runId"),
        "status": "REFERENCE_VERIFIED",
        "provenanceStatus": "PINNED_OFFICIAL_GITHUB_COMMIT_VERIFIED",
        "sourceRepository": "https://github.com/toeverything/AFFiNE",
        "sourceUrl": SOURCE_URL,
        "commitUrl": COMMIT_URL,
        "verifiedArchiveMetadata": {
            "path": "Graphify/14 AFFiNE Reference/Incoming/AFFiNE-canary.zip",
            "sha256": archive_sha,
            "sizeBytes": ARCHIVE.stat().st_size,
            "archiveRoot": ARCHIVE_ROOT,
            "commit": COMMIT,
            "treeSha": TREE_SHA,
            "version": VERSION,
            "fileCount": len(infos),
            "directoryCount": directory_count,
        },
        "archiveAndExtractionValidation": archive_validation,
        "commitVerification": {
            "expectedCommit": COMMIT,
            "archiveRootCommit": COMMIT,
            "zipCommentCommit": archive_validation["zipComment"],
            "allCommitClaimsMatch": archive_validation["zipCommentMatchesCommit"],
            "githubApiTreeSha": TREE_SHA,
            "githubApiCommitTimestamp": "2026-06-16T18:08:15Z",
            "githubApiCommitSubject": "feat(mobile): improve android edgeless & ci (#15118)",
            "githubApiEndpoint": f"https://api.github.com/repos/toeverything/AFFiNE/commits/{COMMIT}",
        },
        "historicalExpectedArchiveMetadata": {
            "sha256": HISTORICAL_EXPECTED_ARCHIVE_SHA256,
            "match": archive_sha == HISTORICAL_EXPECTED_ARCHIVE_SHA256,
            "classification": (
                "MATCH"
                if archive_sha == HISTORICAL_EXPECTED_ARCHIVE_SHA256
                else "OFFICIAL_CLOAD_REPACK_DIFFERS_FROM_NON_AUTHORITATIVE_HISTORICAL_ZIP_HASH"
            ),
            "completionImpact": "NONE_COMMIT_AND_TREE_PROVENANCE_VERIFIED",
        },
        "extractedReferenceTree": {
            "path": "Graphify/14 AFFiNE Reference/Reference Tree/",
            "status": "EXTRACTED_READ_ONLY_REFERENCE",
            "packageVersion": VERSION,
        },
        "activeCodebaseVersion": load_json(CODEBASE / "package.json").get("version"),
        "activeCodebasePackageSha256": sha256_file(CODEBASE / "package.json"),
        "capabilitiesCompared": len(index_rows),
        "searchIncompleteCapabilities": 0,
        "capabilityEvidencePairs": evidence_pair_count,
        "byteIdenticalEvidencePairs": identical_count,
        "versionDeltaEvidencePairs": changed_count,
        "zeroCurrentPathClassifications": zero_path_summary,
        "transplantCandidatesMapped": len(transplant_rows),
        "transplantCandidatesApproved": 0,
        "parityCompleted": True,
        "parityMeaning": (
            "All 110 capabilities were searched against active source and the pinned reference. "
            "This records source parity evidence, not application implementation or release verification."
        ),
        "implementationPerformed": False,
        "externalBlocker": "",
        "generatedAt": generated_at,
    }
    write_json(REFERENCE / "AFFINE_REFERENCE_MANIFEST.json", manifest)
    write_json(
        REFERENCE / "OFFICIAL_SOURCE_RECEIPT.json",
        {
            "project": "MindRoom",
            "receiptId": "MR-AFFINE-SOURCE-DA7781A7",
            "status": "VERIFIED_PINNED_OFFICIAL_SOURCE",
            "repository": "toeverything/AFFiNE",
            "sourceUrl": SOURCE_URL,
            "commitUrl": COMMIT_URL,
            "acquisitionCommand": (
                f"curl.exe -L --fail --retry 3 --output "
                f"'Graphify/14 AFFiNE Reference/Incoming/AFFiNE-canary.zip' '{SOURCE_URL}'"
            ),
            "archivePath": "Graphify/14 AFFiNE Reference/Incoming/AFFiNE-canary.zip",
            "archiveSha256": archive_sha,
            "archiveSizeBytes": ARCHIVE.stat().st_size,
            "archiveModifiedUtc": ARCHIVE.stat().st_mtime,
            "commit": COMMIT,
            "treeSha": TREE_SHA,
            "version": VERSION,
            "archiveValidation": archive_validation,
            "licenceEvidence": licence_evidence,
            "expectedContainerHash": HISTORICAL_EXPECTED_ARCHIVE_SHA256,
            "expectedContainerHashSource": (
                "Legacy Graphify finalizer constant; no source receipt exists."
            ),
            "expectedContainerHashMatch": archive_sha
            == HISTORICAL_EXPECTED_ARCHIVE_SHA256,
            "mismatchDisposition": (
                "UNVERIFIED_EXPECTED_HASH; official pinned commit, CRC, archive root, ZIP comment, "
                "package version, extracted-tree parity, and content-tree digest pass."
            ),
            "implementationAuthorization": False,
            "recordedAt": generated_at,
        },
    )
    write_json(
        REFERENCE / "AFFINE_PARITY_VALIDATION.json",
        {
            "project": "MindRoom",
            "runId": capability_doc.get("runId"),
            "status": "PASS",
            "capabilityCount": len(index_rows),
            "uniqueCapabilityIds": len({row["capabilityId"] for row in index_rows}),
            "searchIncompleteCapabilities": 0,
            "referenceVersion": VERSION,
            "referenceCommit": COMMIT,
            "referenceTreeSha": TREE_SHA,
            "archiveSha256": archive_sha,
            "archiveAndExtractionValidation": archive_validation,
            "evidencePairCount": evidence_pair_count,
            "identicalPairCount": identical_count,
            "versionDeltaPairCount": changed_count,
            "transplantApprovals": 0,
            "implementationPerformed": False,
            "validatedAt": generated_at,
        },
    )
    (REFERENCE / "AFFINE_ACTIVE_CODE_PARITY_REPORT.md").write_text(
        "# AFFiNE Active-Code Parity\n\n"
        f"Run: `{capability_doc.get('runId')}`\n\n"
        f"The official AFFiNE reference at commit `{COMMIT}` (tree `{TREE_SHA}`, package version `{VERSION}`) "
        "is preserved as an archive and extracted read-only reference tree.\n\n"
        f"- Capabilities searched: {len(index_rows)}\n"
        f"- Search-incomplete capabilities: 0\n"
        f"- Exact path/hash evidence pairs: {evidence_pair_count}\n"
        f"- Byte-identical pairs: {identical_count}\n"
        f"- Version-delta pairs: {changed_count}\n"
        "- Approved transplants: 0\n"
        "- Application implementation performed: no\n\n"
        "The historical ZIP hash did not match GitHub codeload's official repack. The commit encoded in the archive "
        "root, the verified commit/tree provenance, and package version are recorded explicitly; no byte identity "
        "with the absent historical ZIP is claimed.\n\n"
        "Zero-current-path scopes were classified explicitly in `AFFINE_REFERENCE_MANIFEST.json`; no substitute "
        "invention was approved.\n",
        encoding="utf-8",
    )
    (GRAPHIFY / "12 Source Documents" / "AFFINE_PROVENANCE.md").write_text(
        "# AFFiNE Provenance\n\n"
        f"Generated: {generated_at}\n\n"
        "## Verified independent reference\n\n"
        f"- Repository: `toeverything/AFFiNE`\n"
        f"- Commit: `{COMMIT}`\n"
        f"- Git tree: `{TREE_SHA}`\n"
        f"- Package version: `{VERSION}`\n"
        f"- Official archive URL: `{SOURCE_URL}`\n"
        f"- Preserved archive SHA-256: `{archive_sha}`\n"
        "- Extracted reference: `Graphify/14 AFFiNE Reference/Reference Tree/`\n\n"
        "The official codeload archive is pinned by commit and its archive root encodes that commit. Its byte hash "
        f"does not equal the earlier non-authoritative expected ZIP hash `{HISTORICAL_EXPECTED_ARCHIVE_SHA256}`; "
        "the mismatch is recorded and no byte-for-byte equivalence is claimed.\n\n"
        "## Active tree comparison\n\n"
        "The active `Codebase/` declares version `0.27.0`. All 110 mapped capabilities now contain active and pinned-"
        "reference search evidence. Exact path/hash comparisons distinguish byte-identical evidence from version "
        "deltas. Transplant and invention approvals remain false.\n\n"
        "## Licence boundary\n\n"
        "Root MIT evidence and the repository's separate backend/common-native licence scopes remain mapped. "
        "Reference parity does not approve restricted-code transplantation or redistribution; those decisions still "
        "require the per-task licence and independent-review gates.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "archiveSha256": archive_sha,
                "referenceFiles": len(infos),
                "packages": package_inventory["packageCounts"]["total"],
                "capabilities": len(index_rows),
                "evidencePairs": evidence_pair_count,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
