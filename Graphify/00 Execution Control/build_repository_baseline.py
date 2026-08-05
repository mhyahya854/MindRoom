"""Derive the Git-less repository baseline from the corrected corpus inventory."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
INVENTORY = ROOT / "Graphify/01 Corpus Inventory/REPOSITORY_INVENTORY.jsonl"
SUMMARY = json.loads(
    (ROOT / "Graphify/01 Corpus Inventory/inventory_run.stdout.txt").read_text(
        encoding="utf-8"
    )
)
records = [
    json.loads(line)
    for line in INVENTORY.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
classifications = Counter(record["classification"] for record in records)
entity_types = Counter(record["entityType"] for record in records)

manifest_records = [
    {
        "path": record["path"],
        "sha256": record["sha256"],
        "sizeBytes": record["sizeBytes"],
    }
    for record in records
    if record["entityType"] in {"FILE", "ARCHIVE"}
]
(Path(__file__).parent / "filesystem_baseline.sha256.jsonl").write_text(
    "".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        for record in manifest_records
    ),
    encoding="utf-8",
)

baseline = {
    "schemaVersion": 1,
    "baselineType": "HASH_MANIFEST",
    "repositoryRevision": f"sha256:{SUMMARY['treeSha256']}",
    "baselineTimestamp": "2026-07-28T01:03:31.289325+00:00",
    "repositoryRoot": str(ROOT).replace("\\", "/"),
    "codebaseRoot": str(ROOT / "Codebase").replace("\\", "/"),
    "graphifyRoot": str(ROOT / "Graphify").replace("\\", "/"),
    "masterPlanHashes": {
        "Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md": "9EBC9C47CF89F98F19CCB039D26031CD7D85E466B57C3A38FD3338EAC618D2E0",
        "Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md": "9065986168858C42E6E4CA7C7050E189265F619C9CB0C902F9BE276A99C08043",
        "Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md": "8AA9DAB09A432361B6CD0CEB26F6911AAF36BAFDE8ED5634C9A687A4774D2D49",
    },
    "counts": {
        "allPaths": len(records),
        "fileCount": SUMMARY["files"],
        "directoryCount": entity_types["DIRECTORY"],
        "sourceCount": classifications["SOURCE"],
        "testCount": classifications["TEST"],
        "fixtureCount": classifications["FIXTURE"],
        "binaryCount": sum(1 for record in records if record["binary"]),
        "markdownCountUnderCodebase": SUMMARY["markdown"],
        "archiveCount": SUMMARY["archives"],
        "symlinkCount": entity_types["SYMLINK"],
        "junctionCount": entity_types["JUNCTION"],
        "packageCount": SUMMARY["packages"],
    },
    "filesystemTreeSha256": SUMMARY["treeSha256"],
    "filesystemManifest": "Graphify/00 Execution Control/filesystem_baseline.sha256.jsonl",
    "git": {
        "status": "MISSING",
        "repositoryRoot": None,
        "branch": None,
        "commit": None,
        "remotes": [],
        "stagedChanges": "UNKNOWN",
        "unstagedChanges": "UNKNOWN",
        "untrackedPaths": "UNKNOWN",
        "submodules": [],
        "linkedWorktrees": [],
        "shallow": "UNKNOWN",
        "historyIntegrity": "UNAVAILABLE",
        "provenanceSearch": [
            "Project root and Codebase contain no .git directory or .git file.",
            "Parent directories inspected without locating linked metadata for MindRoom.",
            "Codebase/package.json identifies @affine/monorepo version 0.27.0, but no commit or remote can be proven.",
        ],
    },
    "knownBaselineFailures": [
        {
            "classification": "COMMAND_UNAVAILABLE",
            "command": "git -C Codebase rev-parse --show-toplevel",
            "result": "fatal: not a git repository",
        },
        {
            "classification": "ENVIRONMENT_FAILURE",
            "command": "graphify --help",
            "result": "Windows Application Control blocked graphify.exe; Python graphify 0.9.28 is used.",
        },
        {
            "classification": "ROLLED_BACK_TOOL_OUTPUT",
            "command": "Graphify AST extraction with cache_root=Codebase",
            "result": "Generated Codebase/graphify-out was moved out of Codebase and the corrected inventory was regenerated.",
        },
    ],
    "existingUncommittedUserWork": [
        {
            "status": "UNKNOWN",
            "reason": "Authentic Git metadata and index are absent; no tracked/untracked distinction can be proven.",
        }
    ],
}
(Path(__file__).parent / "repository_baseline.json").write_text(
    json.dumps(baseline, indent=2) + "\n", encoding="utf-8"
)
print(
    f"baseline {SUMMARY['treeSha256']}: {len(records)} paths, "
    f"{len(manifest_records)} hashed files/archives"
)
