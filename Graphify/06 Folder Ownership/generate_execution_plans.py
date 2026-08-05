#!/usr/bin/env python3
"""Generate deterministic planning-only ownership, reorganisation, and task queues.

This script reads evidence already captured under Graphify.  It never writes to
Codebase and never represents a future mutation as completed.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_DIR = ROOT / "01 Corpus Inventory"
CAPABILITY_DIR = ROOT / "03 Capability Map"
OWNERSHIP_DIR = ROOT / "06 Folder Ownership"
REORG_DIR = ROOT / "07 Reorganisation"
IMPLEMENTATION_DIR = ROOT / "09 Implementation"
GENERATED_AT = "2026-07-28T00:00:00Z"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def flatten_dependencies(package: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for group in package.get("dependencyGroups", {}).values():
        if isinstance(group, dict):
            names.update(str(name) for name in group)
    return sorted(names)


def owner_profile(path: str, package_name: str) -> dict[str, Any]:
    lower = path.lower()
    if path == "Codebase" or path.count("/") == 1:
        purpose = "Repository workspace, package, configuration, or support boundary"
    elif "/blocksuite/" in f"/{lower}/" or lower.startswith("codebase/blocksuite"):
        purpose = "Retained BlockSuite editor, canvas, block, data-view, or widget boundary"
    elif any(token in lower for token in ("/server", "/backend", "/cloud", "/graphql")):
        purpose = "Backend or remote-system boundary requiring retention/removal proof"
    elif any(token in lower for token in ("/test", "/tests", "/__tests__", "/e2e")):
        purpose = "Test, fixture, or verification support boundary"
    elif any(token in lower for token in ("/tool", "/scripts", "/config", "/.github")):
        purpose = "Build, development, migration, or repository tooling boundary"
    elif any(token in lower for token in ("/android", "/ios", "/mobile")):
        purpose = "Platform-specific application or native compatibility boundary"
    elif any(token in lower for token in ("/electron", "/desktop")):
        purpose = "Desktop application or Electron runtime boundary"
    else:
        purpose = "Repository directory classified from inventory and nearest package ownership"

    remote = any(
        token in lower
        for token in (
            "/server/",
            "/backend/",
            "/cloud/",
            "/graphql/",
            "/copilot/",
            "/payment/",
            "/billing/",
            "/telemetry/",
        )
    )
    tests = any(token in lower for token in ("/test", "/__tests__", "/e2e"))
    tooling = any(token in lower for token in ("/tool", "/scripts", "/config", "/.github"))

    if remote:
        disposition = "STAY_PENDING_PROOF; QUARANTINE_LATER_ONLY_IF_APPROVED"
        intended_owner = "Cleanup proof and independent review owner"
    elif tests:
        disposition = "STAY_AND_ADAPT"
        intended_owner = "MindRoom verification owner"
    elif tooling:
        disposition = "STAY_AND_ADAPT"
        intended_owner = "MindRoom build and packaging owner"
    elif "blocksuite" in lower:
        disposition = "STAY"
        intended_owner = "Retained BlockSuite editor owner"
    else:
        disposition = "STAY_OR_ADAPT_IN_PLACE"
        intended_owner = "MindRoom retained runtime owner"

    return {
        "currentPurpose": purpose,
        "currentOwner": package_name or "repository-level ownership",
        "intendedOwner": intended_owner,
        "disposition": disposition,
        "staysInPlace": True,
        "wrapped": False,
        "moves": False,
        "adapted": disposition in {"STAY_AND_ADAPT", "STAY_OR_ADAPT_IN_PLACE"},
        "quarantinedLater": remote,
    }


def target_paths(capability: dict[str, Any]) -> list[str]:
    classification = capability["classification"]
    intended = str(capability.get("intendedFinalPath", ""))
    current = list(dict.fromkeys(capability.get("currentPaths", [])))
    if classification == "REMOVE":
        return [f"Graphify/08 Cleanup/Quarantine/{capability['capabilityId']}"]
    if intended.startswith("PLANNED_RETAIN_IN:") or intended.startswith(
        "PLANNED_RETAIN_OR_ADAPT_IN:"
    ):
        candidate = intended.split(":", 1)[1].strip()
        if " and existing " not in candidate and candidate:
            return [candidate]
        return current or [candidate]
    if intended.startswith("PLANNED:"):
        candidate = intended.split(":", 1)[1].strip()
        return [candidate] if candidate else []
    if intended.startswith("Codebase/") or intended.startswith("Graphify/"):
        return [intended]
    return current


def exact_symbols(capability: dict[str, Any]) -> list[str]:
    output: list[str] = []
    for value in capability.get("currentSymbols", []):
        if isinstance(value, str):
            output.append(value)
        elif isinstance(value, dict):
            symbol = value.get("symbol") or value.get("name") or value.get("symbolId")
            if symbol:
                output.append(str(symbol))
    return list(dict.fromkeys(output))


def main() -> None:
    repo_rows = read_jsonl(INVENTORY_DIR / "REPOSITORY_INVENTORY.jsonl")
    package_inventory = read_json(INVENTORY_DIR / "PACKAGE_INVENTORY.json")
    capability_registry = read_json(CAPABILITY_DIR / "CAPABILITY_REGISTRY.json")
    dependency_order = read_json(CAPABILITY_DIR / "CAPABILITY_DEPENDENCY_ORDER.json")

    directories = [row for row in repo_rows if row.get("entityType") == "DIRECTORY"]
    packages = package_inventory["packages"]
    capabilities = capability_registry["capabilities"]
    cap_by_id = {cap["capabilityId"]: cap for cap in capabilities}
    cap_number = {
        cap["capabilityId"]: int(cap["capabilityId"].rsplit("-", 1)[1])
        for cap in capabilities
    }
    package_by_id = {package["packageId"]: package for package in packages}
    package_by_name = {package["name"]: package for package in packages}

    phase_by_capability: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    for phase in dependency_order["phases"]:
        for capability_id in phase["capabilityIds"]:
            phase_by_capability[capability_id] = phase
            ordered_ids.append(capability_id)
    missing_from_order = sorted(set(cap_by_id) - set(ordered_ids))
    if missing_from_order:
        raise RuntimeError(f"Capabilities missing from dependency order: {missing_from_order}")

    package_dependants: dict[str, set[str]] = defaultdict(set)
    for package in packages:
        for dependency_name in flatten_dependencies(package):
            if dependency_name in package_by_name:
                package_dependants[dependency_name].add(package["name"])

    folder_rows: list[dict[str, Any]] = []
    for index, directory in enumerate(sorted(directories, key=lambda row: row["path"]), 1):
        path = directory["path"]
        package_id = str(directory.get("package", ""))
        package = package_by_id.get(package_id, {})
        package_name = str(package.get("name") or package_id or "repository-level ownership")
        profile = owner_profile(path, package_name)
        folder_rows.append(
            {
                "folderId": f"MR-FOLDER-{index:04d}",
                "currentPath": path,
                "plannedPath": path,
                "folderType": "CURRENT_DIRECTORY",
                **profile,
                "publicEntryPoint": str(
                    package.get("manifestPath") or "NO_DEDICATED_PUBLIC_ENTRYPOINT_MAPPED"
                ),
                "internalOnlyModules": [
                    "Descendants not exposed by the nearest package manifest or a mapped runtime entry"
                ],
                "dependencies": flatten_dependencies(package),
                "dependants": sorted(package_dependants.get(package_name, set())),
                "packageBoundaryImplications": [
                    "Preserve the nearest existing package boundary; no aesthetic split or merge is authorised."
                ],
                "typescriptPathImplications": [
                    "Preserve existing aliases and exports unless a future batch names an exact update."
                ],
                "buildImplications": [
                    "Use repository-discovered package and root checks after any future mutation."
                ],
                "testImplications": [
                    "Run scoped tests plus affected integration coverage after any future mutation."
                ],
                "packagingImplications": [
                    "Verify shipped assets and native outputs when this directory is in a package payload."
                ],
                "evidence": [
                    "Graphify/01 Corpus Inventory/REPOSITORY_INVENTORY.jsonl",
                    "Graphify/01 Corpus Inventory/PACKAGE_INVENTORY.json",
                ],
                "status": "MAPPED_PLANNING_ONLY",
            }
        )

    planned_homes: list[dict[str, Any]] = []
    capability_path_rows: list[dict[str, Any]] = []
    for capability_id in ordered_ids:
        cap = cap_by_id[capability_id]
        targets = target_paths(cap)
        source_paths = list(dict.fromkeys(cap.get("currentPaths", [])))
        classification = cap["classification"]
        planned_homes.append(
            {
                "folderId": f"MR-HOME-{cap_number[capability_id]:03d}",
                "capabilityId": capability_id,
                "capabilityName": cap["name"],
                "currentPath": source_paths,
                "plannedPath": targets,
                "folderType": "PLANNED_CAPABILITY_HOME",
                "currentPurpose": cap["description"],
                "currentOwner": cap["currentOwner"],
                "intendedOwner": cap["intendedOwner"],
                "disposition": (
                    "QUARANTINE_LATER_ONLY_AFTER_PROOF"
                    if classification == "REMOVE"
                    else "CREATE_WITHIN_EXISTING_PACKAGE"
                    if classification == "ADD"
                    else "RETAIN_OR_ADAPT_IN_PLACE"
                ),
                "staysInPlace": classification not in {"ADD", "REMOVE"},
                "wrapped": classification in {"KEEP_AND_ADAPT", "KEEP_FOR_COMPATIBILITY"},
                "moves": False,
                "adapted": classification
                in {"ADD", "KEEP_AND_ADAPT", "KEEP_FOR_COMPATIBILITY", "CONDITIONAL"},
                "quarantinedLater": classification == "REMOVE",
                "publicEntryPoint": cap["publicEntryPoint"],
                "internalOnlyModules": [
                    "Implementation details beneath the mapped public entry point"
                ],
                "dependencies": cap["dependencies"],
                "dependants": cap["dependants"],
                "packageBoundaryImplications": [
                    "Use the mapped existing package; do not create a package solely for this capability."
                ],
                "typescriptPathImplications": [
                    "Add or repair only aliases explicitly listed in the future batch."
                ],
                "buildImplications": [
                    "Future execution requires a successful dependency install and mapped build command."
                ],
                "testImplications": cap["verificationRequirements"],
                "packagingImplications": [
                    "Future packaging verification is required when runtime assets or native components are involved."
                ],
                "evidence": cap["evidence"],
                "status": "NOT_STARTED",
            }
        )
        capability_path_rows.append(
            {
                "capabilityId": capability_id,
                "name": cap["name"],
                "classification": classification,
                "currentPaths": source_paths,
                "targetPaths": targets,
                "symbols": exact_symbols(cap),
                "publicEntryPoint": cap["publicEntryPoint"],
                "currentOwner": cap["currentOwner"],
                "intendedOwner": cap["intendedOwner"],
                "dependencyCapabilityIds": cap["dependencies"],
                "dependantCapabilityIds": cap["dependants"],
                "mappingConfidence": cap["mappingConfidence"],
                "status": "MAPPED_PLANNING_ONLY",
            }
        )

    ownership_document = {
        "schemaVersion": 1,
        "project": "MindRoom",
        "phase": "GRAPHIFY_MAPPING",
        "generatedAt": GENERATED_AT,
        "implementationPerformed": False,
        "sourceMovePerformed": False,
        "coverage": {
            "currentDirectoryCount": len(folder_rows),
            "plannedCapabilityHomeCount": len(planned_homes),
            "packageCount": len(packages),
            "allInventoryDirectoriesMapped": len(folder_rows) == len(directories),
        },
        "currentFolders": folder_rows,
        "plannedCapabilityHomes": planned_homes,
        "limitations": [
            "Ownership is inferred from inventory and nearest package metadata; runtime maintainers were not interviewed.",
            "Remote-looking folders remain in place until full proof and independent review.",
            "No independent AFFiNE reference tree is available for parity decisions.",
        ],
    }
    write_json(OWNERSHIP_DIR / "FOLDER_OWNERSHIP_MATRIX.json", ownership_document)
    write_json(
        OWNERSHIP_DIR / "CAPABILITY_TO_PATH_MAP.json",
        {
            "schemaVersion": 1,
            "project": "MindRoom",
            "phase": "GRAPHIFY_MAPPING",
            "generatedAt": GENERATED_AT,
            "capabilityCount": len(capability_path_rows),
            "implementationPerformed": False,
            "entries": capability_path_rows,
        },
    )

    batch_by_capability = {
        capability_id: f"MR-BATCH-{cap_number[capability_id]:03d}"
        for capability_id in cap_by_id
    }
    task_by_capability = {
        capability_id: f"MR-IMPL-{cap_number[capability_id]:03d}"
        for capability_id in cap_by_id
    }

    batches: list[dict[str, Any]] = []
    moves: list[dict[str, Any]] = []
    config_updates: list[dict[str, Any]] = []
    rollback_rows: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    transplant_rows: list[dict[str, Any]] = []

    for sequence, capability_id in enumerate(ordered_ids, 1):
        cap = cap_by_id[capability_id]
        source_paths = list(dict.fromkeys(cap.get("currentPaths", [])))
        targets = target_paths(cap)
        symbols = exact_symbols(cap)
        dependencies = [batch_by_capability[item] for item in cap["dependencies"]]
        dependants = [batch_by_capability[item] for item in cap["dependants"]]
        allowed_paths = list(dict.fromkeys(source_paths + targets))
        if not allowed_paths:
            allowed_paths = ["NO_CODE_PATH_MAPPED; DISCOVERY_REQUIRED_BEFORE_EXECUTION"]
        exception_required = len(source_paths) > 5
        phase = phase_by_capability[capability_id]
        tests_required = list(dict.fromkeys(cap.get("tests", []) + cap["verificationRequirements"]))
        rollback = [
            "Stop before starting any dependant batch.",
            "Restore every affected path from the pre-mutation SHA-256 manifest.",
            "Remove only files recorded as created by the checkpoint.",
            "Re-run scoped verification and record rollback results.",
            "Do not treat a newly created Git repository as provenance.",
        ]
        config_expected = [
            "Inspect nearest package exports, TypeScript paths, build inputs, tests, and packaging references; update only when the exact move/adaptation requires it."
        ]
        objective = (
            f"Plan verified quarantine/removal of {cap['name']}"
            if cap["classification"] == "REMOVE"
            else f"Plan {cap['classification'].lower()} work for {cap['name']}"
        )
        batch = {
            "batchId": batch_by_capability[capability_id],
            "taskIds": [task_by_capability[capability_id]],
            "capabilityId": capability_id,
            "objective": objective,
            "prerequisites": [
                "All dependency batches have approved receipts.",
                "The Codebase dependency baseline is installed and relevant commands run.",
                "A pre-mutation SHA-256 manifest exists for every affected path.",
                "An independent reviewer is assigned and available.",
            ],
            "allowedPaths": allowed_paths,
            "forbiddenPaths": [
                "All paths not listed in allowedPaths",
                "Graphify/Master Plan/**",
                "User data outside this workspace",
            ],
            "sourcePaths": source_paths,
            "targetPaths": targets,
            "symbols": symbols,
            "maximumNormalSourceFiles": 5,
            "coherentModuleExceptionRequired": exception_required,
            "exceptionReason": (
                f"Mapping identifies {len(source_paths)} related source paths; reviewer must narrow or approve a coherent-module exception."
                if exception_required
                else ""
            ),
            "dependencies": dependencies,
            "dependants": dependants,
            "configurationUpdatesExpected": config_expected,
            "testsRequired": tests_required,
            "rollbackInstructions": rollback,
            "checkpointType": "HASH_MANIFEST",
            "reviewerRole": "Independent capability reviewer distinct from implementer",
            "status": "NOT_STARTED",
            "phaseNumber": phase["phase"],
            "phaseName": phase["name"],
            "implementationPerformed": False,
        }
        batches.append(batch)

        action = (
            "QUARANTINE_THEN_REMOVE_ONLY_AFTER_APPROVED_PROOF"
            if cap["classification"] == "REMOVE"
            else "CREATE_WITHIN_MAPPED_EXISTING_PACKAGE"
            if cap["classification"] == "ADD"
            else "RETAIN_OR_ADAPT_IN_PLACE; NO_AESTHETIC_MOVE"
        )
        moves.append(
            {
                "moveId": f"MR-MOVE-{cap_number[capability_id]:03d}",
                "batchId": batch["batchId"],
                "capabilityId": capability_id,
                "action": action,
                "previousPaths": source_paths,
                "newPaths": targets,
                "physicalMoveRequired": False,
                "futureDecisionRequired": True,
                "status": "NOT_STARTED",
            }
        )
        config_updates.append(
            {
                "updateId": f"MR-CONFIG-{cap_number[capability_id]:03d}",
                "batchId": batch["batchId"],
                "capabilityId": capability_id,
                "imports": "REPAIR_IF_EXACT_MOVE_OR_ADAPTATION_CHANGES_IMPORTS",
                "exports": "PRESERVE_PUBLIC_SURFACE_UNLESS_PLAN_REQUIRES_CHANGE",
                "typescriptPaths": "UPDATE_ONLY_FOR_EXACT_TARGET_PATH",
                "build": "REVALIDATE_DISCOVERED_BUILD_INPUTS",
                "tests": "REVALIDATE_SCOPED_AND_AFFECTED_TESTS",
                "packaging": "REVALIDATE_WHEN_RUNTIME_ASSET_OR_NATIVE_PATH_IS_AFFECTED",
                "status": "NOT_STARTED",
            }
        )
        rollback_rows.append(
            {
                "rollbackId": f"MR-ROLLBACK-{cap_number[capability_id]:03d}",
                "batchId": batch["batchId"],
                "taskId": task_by_capability[capability_id],
                "capabilityId": capability_id,
                "checkpointType": "HASH_MANIFEST",
                "instructions": rollback,
                "verificationReceiptRequired": True,
                "reviewRequired": True,
                "status": "NOT_STARTED",
            }
        )

        task_dependencies = [task_by_capability[item] for item in cap["dependencies"]]
        task_dependants = [task_by_capability[item] for item in cap["dependants"]]
        preliminary_decision = (
            "SEARCH_INCOMPLETE_INDEPENDENT_AFFINE_REFERENCE_NOT_FOUND"
            if cap["classification"] in {"ADD", "KEEP_AND_ADAPT", "KEEP_FOR_COMPATIBILITY"}
            else cap["preliminaryAffineDecision"]
        )
        task = {
            "taskId": task_by_capability[capability_id],
            "capabilityId": capability_id,
            "capabilityName": cap["name"],
            "classification": cap["classification"],
            "sourceRequirements": cap["sourceRequirementIds"],
            "exactCurrentPaths": source_paths,
            "exactTargetPaths": targets,
            "exactSymbols": symbols,
            "requiredAffineSearches": [
                "Search an independently acquired and legally usable AFFiNE reference tree at a pinned commit/tag.",
                "Record exact paths, symbols, licence, commit, and parity evidence before any transplant decision.",
            ],
            "activeCodeSearches": [
                "Search exact current paths and symbols in the active Codebase.",
                "Re-run static, dynamic-import, registration, packaging, and runtime-reachability searches after changes.",
            ],
            "preliminaryTransplantDecision": preliminary_decision,
            "allowedPaths": allowed_paths,
            "forbiddenPaths": batch["forbiddenPaths"],
            "dependencies": task_dependencies,
            "dependantTasks": task_dependants,
            "requiredAdaptations": cap["requiredAdaptations"],
            "prohibitedReinvention": cap["prohibitedChanges"],
            "tests": tests_required,
            "fixtures": cap.get("fixtures", []),
            "verificationReceipts": [
                f"Graphify/10 Verification/test-receipt-{capability_id.lower()}.json",
                f"Graphify/00 Execution Control/hash-manifest-{capability_id.lower()}.json",
            ],
            "reviewer": {
                "role": "Independent capability reviewer",
                "mustDifferFromImplementer": True,
                "decision": "PENDING",
            },
            "rollback": rollback,
            "status": "NOT_STARTED",
            "phaseNumber": phase["phase"],
            "phaseName": phase["name"],
            "implementationPerformed": False,
        }
        tasks.append(task)
        transplant_rows.append(
            {
                "searchId": f"MR-TRANSPLANT-{cap_number[capability_id]:03d}",
                "taskId": task["taskId"],
                "capabilityId": capability_id,
                "capabilityName": cap["name"],
                "activeCodePaths": source_paths,
                "requiredIndependentReference": "AFFiNE source tree pinned to exact commit/tag",
                "referenceAvailable": False,
                "searchStatus": "SEARCH_INCOMPLETE",
                "decision": "NO_TRANSPLANT_AUTHORISED",
                "licenceReviewRequired": True,
                "parityReviewRequired": True,
                "receiptRequired": True,
                "blocker": "Independent AFFiNE reference tree, commit/tag, and parity baseline were not supplied or found.",
            }
        )

    write_jsonl(REORG_DIR / "REORGANISATION_LEDGER.jsonl", batches)
    write_jsonl(REORG_DIR / "MOVE_PLAN.jsonl", moves)
    write_jsonl(REORG_DIR / "IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl", config_updates)
    write_jsonl(REORG_DIR / "ROLLBACK_PLAN.jsonl", rollback_rows)

    phase_lines = [
        "# Batch Execution Plan",
        "",
        "Planning only. No Codebase file has been moved, adapted, quarantined, or deleted.",
        "",
        "All batches use SHA-256 manifests because the supplied Codebase has no valid Git metadata. A future executor must complete dependency installation, baseline checks, scoped verification, and independent review before mutation.",
        "",
    ]
    by_phase: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for batch in batches:
        by_phase[batch["phaseNumber"]].append(batch)
    for phase_number in sorted(by_phase):
        phase_name = by_phase[phase_number][0]["phaseName"]
        phase_lines.extend([f"## Phase {phase_number}: {phase_name}", ""])
        for batch in by_phase[phase_number]:
            phase_lines.append(
                f"- `{batch['batchId']}` / `{batch['taskIds'][0]}` / `{batch['capabilityId']}` — {batch['objective']} — `{batch['status']}`"
            )
        phase_lines.append("")
    phase_lines.extend(
        [
            "## Global stop conditions",
            "",
            "Stop if an allowed path is ambiguous, a dependency receipt is absent, the pre-mutation hash manifest is incomplete, a repository command fails, user-data compatibility is unresolved, or an independent reviewer is unavailable.",
            "",
        ]
    )
    (REORG_DIR / "BATCH_EXECUTION_PLAN.md").write_text(
        "\n".join(phase_lines), encoding="utf-8"
    )

    write_jsonl(IMPLEMENTATION_DIR / "IMPLEMENTATION_TASKS.jsonl", tasks)
    write_jsonl(IMPLEMENTATION_DIR / "TRANSPLANT_SEARCH_QUEUE.jsonl", transplant_rows)
    write_jsonl(
        IMPLEMENTATION_DIR / "ADAPTATION_TASKS.jsonl",
        [
            task
            for task in tasks
            if task["classification"]
            in {"KEEP_AND_ADAPT", "KEEP_FOR_COMPATIBILITY", "CONDITIONAL"}
        ],
    )
    write_jsonl(
        IMPLEMENTATION_DIR / "NEW_CAPABILITY_TASKS.jsonl",
        [task for task in tasks if task["classification"] == "ADD"],
    )

    queue_lines = [
        "# Implementation Queue",
        "",
        "This is a planning queue, not execution authority. Every task is `NOT_STARTED`; no transplant, implementation, source move, quarantine, or deletion was performed.",
        "",
        "The queue follows the validated capability dependency phases rather than folder-name order. All transplant searches remain blocked until an independent AFFiNE tree with an exact commit/tag and licence/parity evidence is available.",
        "",
    ]
    for phase_number in sorted(by_phase):
        phase_name = by_phase[phase_number][0]["phaseName"]
        queue_lines.extend([f"## Phase {phase_number}: {phase_name}", ""])
        for batch in by_phase[phase_number]:
            cap = cap_by_id[batch["capabilityId"]]
            queue_lines.append(
                f"- `{batch['taskIds'][0]}` — `{cap['classification']}` — {cap['name']} — dependencies: {len(cap['dependencies'])} — `NOT_STARTED`"
            )
        queue_lines.append("")
    queue_lines.extend(
        [
            "## Release lock",
            "",
            "Execution remains blocked by unresolved reference provenance/parity, missing installed dependencies and baseline checks, incomplete real-file fixtures, graph-health issues, and unavailable independent review.",
            "",
        ]
    )
    (IMPLEMENTATION_DIR / "IMPLEMENTATION_QUEUE.md").write_text(
        "\n".join(queue_lines), encoding="utf-8"
    )

    # Fail closed if a generated output accidentally claims execution.
    serialised = "\n".join(
        json.dumps(value, ensure_ascii=False)
        for value in (batches, moves, config_updates, rollback_rows, tasks, transplant_rows)
    )
    forbidden_claims = ('"status": "COMPLETED"', '"status": "PURGED"')
    if any(claim in serialised for claim in forbidden_claims):
        raise RuntimeError("Generated planning artifacts contain a forbidden completion claim")

    print(
        json.dumps(
            {
                "currentFolders": len(folder_rows),
                "plannedCapabilityHomes": len(planned_homes),
                "batches": len(batches),
                "implementationTasks": len(tasks),
                "adaptationTasks": sum(
                    task["classification"]
                    in {"KEEP_AND_ADAPT", "KEEP_FOR_COMPATIBILITY", "CONDITIONAL"}
                    for task in tasks
                ),
                "newCapabilityTasks": sum(
                    task["classification"] == "ADD" for task in tasks
                ),
                "transplantSearches": len(transplant_rows),
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
