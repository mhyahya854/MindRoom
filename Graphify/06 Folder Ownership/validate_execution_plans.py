#!/usr/bin/env python3
"""Fail-closed validation for ownership, reorganisation, and implementation plans."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


GRAPHIFY = Path(__file__).resolve().parents[1]
WORKSPACE = GRAPHIFY.parent


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise AssertionError(f"{path}:{number}: {error}") from error
    return rows


def main() -> None:
    ownership = load_json(GRAPHIFY / "06 Folder Ownership" / "FOLDER_OWNERSHIP_MATRIX.json")
    path_map = load_json(GRAPHIFY / "06 Folder Ownership" / "CAPABILITY_TO_PATH_MAP.json")
    capabilities_doc = load_json(GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json")
    capabilities = capabilities_doc["capabilities"]
    cap_by_id = {row["capabilityId"]: row for row in capabilities}
    valid_caps = set(cap_by_id)

    inventory_dirs = {
        row["path"]
        for row in load_jsonl(
            GRAPHIFY / "01 Corpus Inventory" / "REPOSITORY_INVENTORY.jsonl"
        )
        if row["entityType"] == "DIRECTORY"
    }
    mapped_dirs = {row["currentPath"] for row in ownership["currentFolders"]}
    assert mapped_dirs == inventory_dirs, "folder matrix does not exactly cover inventory directories"
    assert ownership["coverage"]["currentDirectoryCount"] == len(inventory_dirs)
    assert ownership["sourceMovePerformed"] is False
    assert ownership["implementationPerformed"] is False
    for row in ownership["currentFolders"]:
        assert (WORKSPACE / row["currentPath"]).is_dir(), row["currentPath"]
        required = {
            "currentPurpose",
            "currentOwner",
            "intendedOwner",
            "staysInPlace",
            "wrapped",
            "moves",
            "adapted",
            "quarantinedLater",
            "publicEntryPoint",
            "internalOnlyModules",
            "dependencies",
            "dependants",
            "packageBoundaryImplications",
            "typescriptPathImplications",
            "buildImplications",
            "testImplications",
            "packagingImplications",
        }
        assert required <= set(row), row["folderId"]

    homes = ownership["plannedCapabilityHomes"]
    assert {row["capabilityId"] for row in homes} == valid_caps
    assert len(homes) == len(valid_caps)
    assert path_map["capabilityCount"] == len(valid_caps)
    assert {row["capabilityId"] for row in path_map["entries"]} == valid_caps

    reorg = GRAPHIFY / "07 Reorganisation"
    batches = load_jsonl(reorg / "REORGANISATION_LEDGER.jsonl")
    moves = load_jsonl(reorg / "MOVE_PLAN.jsonl")
    configs = load_jsonl(reorg / "IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl")
    rollbacks = load_jsonl(reorg / "ROLLBACK_PLAN.jsonl")
    assert all(len(rows) == len(valid_caps) for rows in (batches, moves, configs, rollbacks))
    assert {row["capabilityId"] for row in batches} == valid_caps
    batch_ids = {row["batchId"] for row in batches}
    assert len(batch_ids) == len(batches)
    required_batch = {
        "batchId",
        "taskIds",
        "capabilityId",
        "objective",
        "prerequisites",
        "allowedPaths",
        "forbiddenPaths",
        "sourcePaths",
        "targetPaths",
        "symbols",
        "maximumNormalSourceFiles",
        "coherentModuleExceptionRequired",
        "exceptionReason",
        "dependencies",
        "dependants",
        "configurationUpdatesExpected",
        "testsRequired",
        "rollbackInstructions",
        "checkpointType",
        "reviewerRole",
        "status",
    }
    position = {row["batchId"]: index for index, row in enumerate(batches)}
    for row in batches:
        assert required_batch <= set(row), row["batchId"]
        assert row["status"] == "NOT_STARTED"
        assert row["implementationPerformed"] is False
        assert row["checkpointType"] == "HASH_MANIFEST"
        assert row["maximumNormalSourceFiles"] == 5
        assert row["capabilityId"] in valid_caps
        assert set(row["dependencies"]) <= batch_ids
        assert set(row["dependants"]) <= batch_ids
        assert all(position[dependency] < position[row["batchId"]] for dependency in row["dependencies"]), (
            f"non-topological batch dependency: {row['batchId']}"
        )
        cap = cap_by_id[row["capabilityId"]]
        expected_dependencies = {
            f"MR-BATCH-{int(item.rsplit('-', 1)[1]):03d}" for item in cap["dependencies"]
        }
        assert set(row["dependencies"]) == expected_dependencies
        assert row["coherentModuleExceptionRequired"] == (len(row["sourcePaths"]) > 5)

    implementation = GRAPHIFY / "09 Implementation"
    tasks = load_jsonl(implementation / "IMPLEMENTATION_TASKS.jsonl")
    transplant = load_jsonl(implementation / "TRANSPLANT_SEARCH_QUEUE.jsonl")
    adaptations = load_jsonl(implementation / "ADAPTATION_TASKS.jsonl")
    additions = load_jsonl(implementation / "NEW_CAPABILITY_TASKS.jsonl")
    assert len(tasks) == len(transplant) == len(valid_caps)
    assert len({row["taskId"] for row in tasks}) == len(tasks)
    assert {row["capabilityId"] for row in tasks} == valid_caps
    task_ids = {row["taskId"] for row in tasks}
    required_task = {
        "taskId",
        "capabilityId",
        "sourceRequirements",
        "exactCurrentPaths",
        "exactTargetPaths",
        "exactSymbols",
        "requiredAffineSearches",
        "activeCodeSearches",
        "preliminaryTransplantDecision",
        "allowedPaths",
        "forbiddenPaths",
        "dependencies",
        "dependantTasks",
        "requiredAdaptations",
        "prohibitedReinvention",
        "tests",
        "fixtures",
        "verificationReceipts",
        "reviewer",
        "rollback",
        "status",
    }
    for row in tasks:
        assert required_task <= set(row), row["taskId"]
        assert row["status"] == "NOT_STARTED"
        assert row["implementationPerformed"] is False
        assert row["reviewer"]["decision"] == "PENDING"
        assert set(row["dependencies"]) <= task_ids
        assert set(row["dependantTasks"]) <= task_ids
        assert set(row["sourceRequirements"]) == set(
            cap_by_id[row["capabilityId"]]["sourceRequirementIds"]
        )
    expected_adapt = {
        row["taskId"]
        for row in tasks
        if row["classification"]
        in {"KEEP_AND_ADAPT", "KEEP_FOR_COMPATIBILITY", "CONDITIONAL"}
    }
    expected_add = {row["taskId"] for row in tasks if row["classification"] == "ADD"}
    assert {row["taskId"] for row in adaptations} == expected_adapt
    assert {row["taskId"] for row in additions} == expected_add
    assert all(row["searchStatus"] == "SEARCH_INCOMPLETE" for row in transplant)
    assert all(row["decision"] == "NO_TRANSPLANT_AUTHORISED" for row in transplant)

    for markdown_path in (
        reorg / "BATCH_EXECUTION_PLAN.md",
        implementation / "IMPLEMENTATION_QUEUE.md",
    ):
        text = markdown_path.read_text(encoding="utf-8")
        assert "planning" in text.lower()
        assert "NOT_STARTED" in text

    print(
        json.dumps(
            {
                "status": "PASS",
                "currentFolders": len(mapped_dirs),
                "plannedCapabilityHomes": len(homes),
                "batches": len(batches),
                "implementationTasks": len(tasks),
                "adaptationTasks": len(adaptations),
                "newCapabilityTasks": len(additions),
                "transplantSearches": len(transplant),
                "codebaseMutationPerformed": False,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
