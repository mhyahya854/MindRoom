from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent
CODEBASE_ROOT = OUTPUT_DIR.parents[1] / "Codebase"
JSONL_FILES = [
    "REPOSITORY_INVENTORY.jsonl",
    "MARKDOWN_MIGRATION_LEDGER.jsonl",
    "BINARY_AND_RUNTIME_ASSET_INVENTORY.jsonl",
    "ARCHIVE_INVENTORY.jsonl",
    "PLATFORM_FILE_INVENTORY.jsonl",
]
REQUIRED_REPOSITORY_FIELDS = {
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


def load_jsonl(name: str) -> list[dict]:
    records = []
    with (OUTPUT_DIR / name).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise AssertionError(f"{name}:{line_number} is not an object")
            records.append(value)
    return records


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def enumerate_paths() -> set[str]:
    paths: set[str] = set()
    for directory, directories, files in os.walk(CODEBASE_ROOT, followlinks=False):
        directories.sort(key=str.casefold)
        files.sort(key=str.casefold)
        directory_path = Path(directory)
        for name in directories + files:
            relative = (directory_path / name).relative_to(CODEBASE_ROOT).as_posix()
            paths.add(f"Codebase/{relative}")
    return paths


def main() -> None:
    repository = load_jsonl("REPOSITORY_INVENTORY.jsonl")
    markdown = load_jsonl("MARKDOWN_MIGRATION_LEDGER.jsonl")
    binaries = load_jsonl("BINARY_AND_RUNTIME_ASSET_INVENTORY.jsonl")
    archives = load_jsonl("ARCHIVE_INVENTORY.jsonl")
    platforms = load_jsonl("PLATFORM_FILE_INVENTORY.jsonl")
    packages = json.loads((OUTPUT_DIR / "PACKAGE_INVENTORY.json").read_text(encoding="utf-8"))
    assert isinstance(packages, dict)

    repository_by_path = {record["path"]: record for record in repository}
    assert len(repository_by_path) == len(repository), "duplicate repository paths"
    actual_paths = enumerate_paths()
    assert set(repository_by_path) == actual_paths, {
        "missingFromInventory": sorted(actual_paths - set(repository_by_path))[:20],
        "staleInventoryPaths": sorted(set(repository_by_path) - actual_paths)[:20],
    }
    assert "Codebase/graphify-out" not in repository_by_path
    assert not (CODEBASE_ROOT / "graphify-out").exists()

    file_count = 0
    directory_count = 0
    for path_name, record in repository_by_path.items():
        assert REQUIRED_REPOSITORY_FIELDS <= record.keys(), path_name
        assert record["trackedState"] == "UNKNOWN", path_name
        relative = path_name.removeprefix("Codebase/")
        path = CODEBASE_ROOT / Path(*relative.split("/"))
        if record["entityType"] in {"FILE", "ARCHIVE"}:
            file_count += 1
            assert re.fullmatch(r"[0-9a-f]{64}", record["sha256"]), path_name
            assert record["sha256"] == digest(path), f"stale hash: {path_name}"
            assert record["sizeBytes"] == path.stat().st_size, f"stale size: {path_name}"
        elif record["entityType"] == "DIRECTORY":
            directory_count += 1
            assert path.is_dir(), path_name

    markdown_expected = {
        path
        for path, record in repository_by_path.items()
        if record["extension"] in {".md", ".markdown"}
    }
    archive_expected = {
        path
        for path, record in repository_by_path.items()
        if record["entityType"] == "ARCHIVE"
    }
    assert markdown_expected == {record["path"] for record in markdown}
    assert archive_expected == {record["path"] for record in archives}

    for subset_name, subset in {
        "binary/runtime": binaries,
        "archive": archives,
        "platform": platforms,
    }.items():
        subset_paths = [record["path"] for record in subset]
        assert len(subset_paths) == len(set(subset_paths)), f"duplicate {subset_name} paths"
        for record in subset:
            source = repository_by_path[record["path"]]
            assert record["sha256"] == source["sha256"], record["path"]
            assert record["sizeBytes"] == source["sizeBytes"], record["path"]

    package_ids = [package["packageId"] for package in packages["packages"]]
    assert len(package_ids) == len(set(package_ids)), "duplicate package IDs"
    for package in packages["packages"]:
        manifest_path = package["manifestPath"]
        if manifest_path:
            source = repository_by_path[manifest_path]
            assert source["sha256"] == package["manifestSha256"], package["packageId"]
        assert package["parseStatus"] != "INVALID", package["packageId"]

    output_hashes = {
        name: digest(OUTPUT_DIR / name)
        for name in [
            "REPOSITORY_INVENTORY.jsonl",
            "PACKAGE_INVENTORY.json",
            "CORPUS_SUMMARY.md",
            "MARKDOWN_MIGRATION_LEDGER.jsonl",
            "BINARY_AND_RUNTIME_ASSET_INVENTORY.jsonl",
            "ARCHIVE_INVENTORY.jsonl",
            "PLATFORM_FILE_INVENTORY.jsonl",
        ]
    }
    print(
        json.dumps(
            {
                "status": "PASS",
                "codebaseGraphifyOutAbsent": True,
                "paths": len(repository),
                "filesAndArchives": file_count,
                "directories": directory_count,
                "packages": len(packages["packages"]),
                "markdown": len(markdown),
                "binaryRuntimeAssets": len(binaries),
                "archives": len(archives),
                "platformFiles": len(platforms),
                "outputSha256": output_hashes,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
