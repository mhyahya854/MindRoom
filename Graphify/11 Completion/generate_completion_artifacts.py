#!/usr/bin/env python3
"""Generate the required, non-duplicative Graphify completion summaries."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


COMPLETION = Path(__file__).resolve().parent
GRAPHIFY = COMPLETION.parent


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def write(name: str, lines: list[str]) -> None:
    COMPLETION.joinpath(name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    baseline = load_json(GRAPHIFY / "00 Execution Control" / "repository_baseline.json")
    inventory = load_jsonl(GRAPHIFY / "01 Corpus Inventory" / "REPOSITORY_INVENTORY.jsonl")
    packages = load_json(GRAPHIFY / "01 Corpus Inventory" / "PACKAGE_INVENTORY.json")["packages"]
    capabilities = load_json(GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json")["capabilities"]
    requirements = load_jsonl(GRAPHIFY / "03 Capability Map" / "REQUIREMENT_REGISTRY.jsonl")
    order = load_json(GRAPHIFY / "03 Capability Map" / "CAPABILITY_DEPENDENCY_ORDER.json")
    path_map = load_json(GRAPHIFY / "06 Folder Ownership" / "CAPABILITY_TO_PATH_MAP.json")["entries"]
    tasks = load_jsonl(GRAPHIFY / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl")
    validation = load_json(COMPLETION / "GLOBAL_VALIDATION_RESULT.json")
    mapping_receipt = load_json(COMPLETION / "GRAPHIFY_MAPPING_RECEIPT.json")
    graph_health = validation["graphHealth"]
    reference_manifest = load_json(GRAPHIFY / "14 AFFiNE Reference" / "AFFINE_REFERENCE_MANIFEST.json")
    release_matrix = load_json(GRAPHIFY / "10 Verification" / "RELEASE_GATE_MATRIX.json")
    task_by_cap = {row["capabilityId"]: row for row in tasks}
    path_by_cap = {row["capabilityId"]: row for row in path_map}
    phase_by_cap: dict[str, tuple[int, str]] = {}
    for phase in order["phases"]:
        for capability_id in phase["capabilityIds"]:
            phase_by_cap[capability_id] = (phase["phase"], phase["name"])

    blocker_rows = [
        ("MR-BLOCK-001", "External", "Independent AFFiNE source/reference tree, exact commit or tag, and parity baseline are unavailable.", "Supply a legally usable pinned AFFiNE tree; rerun the 110 transplant searches and independent parity/licence review."),
        ("MR-BLOCK-002", "Repository-local mapping", "MR-CAP-060 Remote announcements and MR-CAP-064 Dead code have no exact active Codebase path; MR-CAP-093 Quarantine and MR-CAP-105 SBOM are planned additions with no current path.", "Map exact active locations for the two removal capabilities; keep planned additions pathless until implementation creates approved targets."),
        ("MR-BLOCK-003", "Repository-local mapping", f"Dependency registry contains {validation['referentialIntegrity']['unresolvedSourceEndpoints']} unresolved source endpoints and {validation['referentialIntegrity']['unresolvedTargetEndpoints']} unresolved target endpoints.", "Resolve internal AST references, explicitly classify genuine external endpoints, and rerun exact-location/dependency validation."),
        ("MR-BLOCK-004", "Repository-local/tool", f"Graphify health reports {graph_health['danglingEndpointEdges']} dangling endpoint edges and {graph_health['selfLoopEdges']} self-loops.", "Repair or explicitly suppress producer defects, rebuild graph.json/graph.html, and require zero unresolved graph-health blockers."),
        ("MR-BLOCK-005", "External", "No independent consistency reviewer could run after the real mapping wave because the external subagent usage limit was reached.", "Run a role-separated reviewer over every major Graphify domain; populate AGENT_REVIEWS.jsonl only with real decisions."),
        ("MR-BLOCK-006", "Environment/repository-local", "Codebase/node_modules is absent; typecheck, lint, tests, builds, packaging, installer launch, offline verification, and app-deletion survival are blocked or not run.", "In the later execution phase, install with the pinned Yarn release under an approved hash checkpoint, then run TEST_COMMAND_REGISTRY commands."),
        ("MR-BLOCK-007", "Repository-local/external fixtures", "Seventeen required fixture basenames are absent; the existing sample.pdf has unresolved suitability and legal-reuse evidence.", "Acquire or generate legally usable real fixtures and complete every fixture-by-QA-cell receipt."),
        ("MR-BLOCK-008", "Legal/external", "Restricted EE/MPL-scoped backend/native paths and incomplete third-party lockfile licence metadata prevent transplant, licence, attribution, and SBOM approval.", "Resolve provenance/licence records, required notices, redistribution obligations, and SBOM evidence before approval."),
        ("MR-BLOCK-009", "Tool", "Graphify semantic extraction was not run because no Gemini key was available; seven MP4 transcriptions failed with tuple-index errors.", "Provide an authorised semantic backend if required and repair the transcription tool path; never infer missing transcripts."),
    ]

    gate_lines = [
        "# Completion Tracker",
        "",
        "Verdict: `NOT_VERIFIED`. Mapping outputs are extensive, but the locked completion gate is not met and Codebase execution is blocked.",
        "",
        "| # | Locked mapping gate | Status | Evidence or blocker |",
        "|---:|---|---|---|",
    ]
    locked_gates = [
        ("Real project root confirmed", "PASS", "repository_baseline.json"),
        ("Three Master Plans read and hashed", "PASS", "Three SHA-256 hashes reverified"),
        ("Every Codebase path inventoried/excluded", "PASS", "12,628 paths; no exclusions or hash failures"),
        ("Every package mapped", "PASS", "134 packages"),
        ("Every application entry point mapped", "PASS", "25 entrypoint records"),
        ("Every meaningful runtime registration mapped", "PASS", "35 runtime-registration records plus IPC/commands/workers"),
        ("Every requirement has a stable ID", "PASS", "1,420 unique requirement IDs"),
        ("Every requirement maps to capability", "PASS", "1,420 trace rows"),
        ("Every capability has stable ID", "PASS", "110 unique capability IDs"),
        ("Every capability has current paths and intended ownership", "BLOCKED", "Four capabilities have no current path; two are unresolved removal scopes and two are planned additions"),
        ("Every meaningful symbol has exact location", "BLOCKED", "19,591 symbols mapped, but 31,709 dependency endpoints remain unresolved"),
        ("Dependency and impact edges recorded", "PASS", "132,356 typed dependency edges"),
        ("Excluded remote systems mapped", "PASS", "33 removal blast-radius records"),
        ("All Codebase Markdown mapped", "PASS", "207 migration/retention records"),
        ("Independent AFFiNE reference source indexed", "BLOCKED", reference_manifest["referenceStatus"]),
        ("AFFiNE transplant candidates identified", "PASS", "110 candidates; all SEARCH_INCOMPLETE and unapproved"),
        ("No substitute invention without search evidence", "PASS", "All transplant decisions fail closed"),
        ("Folder ownership defined", "PASS", "2,548 current folders plus 110 planned homes"),
        ("Target architecture avoids fragmentation", "PASS", "Existing package boundaries retained; no one-folder-per-function design"),
        ("Reorganisation batches dependency ordered", "PASS", "110 topologically validated batches"),
        ("Deletion candidates mapped, not deleted", "PASS", "366 candidates; zero quarantine entries; zero approved/purged"),
        ("Implementation tasks complete and ordered", "PASS", "110 planning tasks; all NOT_STARTED"),
        ("Test/build commands discovered", "PASS", "TEST_COMMAND_REGISTRY.json"),
        ("Fixture QA requirements mapped", "PASS", "18 fixture classes × 20 QA dimensions mapped"),
        ("Packaging/offline verification mapped", "PASS", "Plans and release-gate matrix present; execution NOT_RUN"),
        ("Licence/attribution obligations mapped", "PASS", "4,226 third-party register rows; approval remains blocked"),
        ("JSON/JSONL validate", "PASS", f"{validation['jsonValidation']['jsonFilesParsed']} JSON and {validation['jsonValidation']['jsonlFilesParsed']} JSONL files parsed"),
        ("Cross-references resolve", "BLOCKED", "Explicit unresolved dependency endpoints remain"),
        ("Independent review passes", "BLOCKED", "AGENT_REVIEWS.jsonl intentionally empty"),
        ("Codebase tracked source remains unmodified", "PASS", "10,080 file hashes and 2,548 directory paths match baseline"),
        ("FINAL_RELEASE_RECEIPT remains locked", "PASS", "NOT_VERIFIED; all application gates false"),
        ("GRAPHIFY_MAPPING_RECEIPT all gates pass", "BLOCKED", "allGatesPassed=false; executionReady=false"),
    ]
    for index, (name, status, evidence) in enumerate(locked_gates, 1):
        gate_lines.append(f"| {index} | {cell(name)} | `{status}` | {cell(evidence)} |")
    gate_lines.extend(["", "Resume with the exact tasks in `UNRESOLVED_MAPPING_ISSUES.md`; do not begin Codebase mutation while any blocked gate remains.", ""])
    write("COMPLETION_TRACKER.md", gate_lines)

    audit_lines = [
        "# Graphify Final Audit",
        "",
        "Audit result: `PASS_WITH_OPEN_MAPPING_BLOCKERS`. This is orchestrator self-validation, not independent review or execution approval.",
        "",
        "## Validated evidence",
        "",
        f"- Parsed {validation['jsonValidation']['jsonFilesParsed']} JSON files and {validation['jsonValidation']['jsonlFilesParsed']} JSONL files containing {validation['jsonValidation']['jsonlRecordsParsed']} records.",
        f"- Validated {validation['schemaValidation']['schemaInstancesValidated']} instances against the required schemas.",
        f"- Reverified {len(validation['masterPlanHashes']['verified'])} Master Plan SHA-256 hashes.",
        "- Rehashed all 10,080 Codebase files and compared all 2,548 directory paths: zero added, missing, or changed paths/files.",
        "- Revalidated the exact-location/dependency generator and the ownership, batch, implementation, and cleanup validators.",
        "- Confirmed no implementation, quarantine, deletion, purge, approved transplant, or release-gate completion claim exists.",
        "",
        "## Blocking findings",
        "",
    ]
    for blocker_id, locality, issue, next_task in blocker_rows:
        audit_lines.append(f"- `{blocker_id}` ({locality}): {issue} Next: {next_task}")
    audit_lines.extend(["", "The mapping receipt remains `NOT_VERIFIED`; the final release receipt remains locked.", ""])
    write("GRAPHIFY_FINAL_AUDIT.md", audit_lines)

    codebase_lines = [
        "# Codebase Map",
        "",
        f"Mapped repository: `{baseline['codebaseRoot']}` using `{baseline['repositoryRevision']}`. Codebase was read-only.",
        "",
        "| Domain | Evidence | Count/status |",
        "|---|---|---:|",
        f"| Corpus | `01 Corpus Inventory/REPOSITORY_INVENTORY.jsonl` | {baseline['counts']['allPaths']} paths |",
        f"| Packages | `01 Corpus Inventory/PACKAGE_INVENTORY.json` | {len(packages)} |",
        "| Architecture nodes | `02 Architecture Map/ARCHITECTURE_NODES.jsonl` | 44 |",
        "| Entrypoints | `02 Architecture Map/ENTRYPOINT_REGISTRY.jsonl` | 25 |",
        "| Runtime registrations | `02 Architecture Map/RUNTIME_REGISTRATION_REGISTRY.jsonl` | 35 |",
        "| IPC/preload | `02 Architecture Map/IPC_AND_PRELOAD_REGISTRY.jsonl` | 35 |",
        "| Commands/events | `02 Architecture Map/COMMAND_AND_EVENT_REGISTRY.jsonl` | 25 |",
        "| Workers | `02 Architecture Map/WORKER_REGISTRY.jsonl` | 16 |",
        "| Network boundaries | `02 Architecture Map/NETWORK_BOUNDARY_REGISTRY.jsonl` | 24 |",
        f"| Exact locations | `04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json` | {validation['referentialIntegrity']['exactLocations']} |",
        f"| Meaningful symbols | `04 Exact Location Registry/SYMBOL_REGISTRY.jsonl` | {validation['referentialIntegrity']['symbols']} |",
        f"| Dependency edges | `05 Dependency and Impact/DEPENDENCY_EDGES.jsonl` | {validation['referentialIntegrity']['dependencyEdges']} |",
        "",
        "Retain useful AFFiNE/BlockSuite package boundaries, desktop/Electron surfaces, editor foundations, local models, tests, and packaging infrastructure. Adapt retained runtime behind local-first/file-backed owners. Add durable file/workspace, sync/import, document/media, restoration, offline, packaging, and audit capabilities inside mapped existing packages. Isolate 33 remote/cloud/account/team/billing/AI/telemetry/backend capability scopes only through receipt-backed future batches.",
        "",
        "Authoritative detail lives in the registries above; this file is a navigation map, not a duplicate source of truth.",
        "",
    ]
    write("CODEBASE_MAP.md", codebase_lines)

    top: dict[str, dict[str, int]] = defaultdict(lambda: {"paths": 0, "files": 0, "directories": 0})
    for row in inventory:
        parts = row["path"].split("/")
        name = parts[1] if len(parts) > 1 else "(root)"
        top[name]["paths"] += 1
        if row["entityType"] == "DIRECTORY":
            top[name]["directories"] += 1
        else:
            top[name]["files"] += 1
    tree_lines = [
        "# Folder Tree",
        "",
        "Current top-level Codebase tree from the exhaustive inventory. Exact ownership for every directory is in `../06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json`; the future target tree is in `../06 Folder Ownership/TARGET_CODEBASE_TREE.md`.",
        "",
        "```text",
        "Codebase/",
    ]
    for name in sorted(top):
        data = top[name]
        tree_lines.append(f"├─ {name}/  [{data['files']} files; {data['directories']} directories]")
    tree_lines.extend(["```", "", "No physical reorganisation was performed. Future changes are limited to the 110 batches in `../07 Reorganisation/REORGANISATION_LEDGER.jsonl`.", ""])
    write("FOLDER_TREE.md", tree_lines)

    matrix_lines = [
        "# Capability Matrix",
        "",
        "All 110 stable capabilities. Exact current/target paths and symbols remain authoritative in `../06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json` and the implementation queue.",
        "",
        "| Capability | Classification | Phase | Current paths | Target paths | Task | Dependencies |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for cap in sorted(capabilities, key=lambda row: row["capabilityId"]):
        mapped = path_by_cap[cap["capabilityId"]]
        task = task_by_cap[cap["capabilityId"]]
        phase_number, _ = phase_by_cap[cap["capabilityId"]]
        matrix_lines.append(
            f"| `{cap['capabilityId']}` {cell(cap['name'])} | `{cap['classification']}` | {phase_number} | {len(mapped['currentPaths'])} | {len(mapped['targetPaths'])} | `{task['taskId']}` `NOT_STARTED` | {len(cap['dependencies'])} |"
        )
    matrix_lines.append("")
    write("CAPABILITY_MATRIX.md", matrix_lines)

    req_counts = Counter(row["requirementType"] for row in requirements)
    decision_counts = Counter(row["decisionLabel"] for row in requirements)
    coverage_lines = [
        "# Requirement Coverage Report",
        "",
        "Coverage result: all 1,420 Master Plan requirements have stable IDs, at least one capability, and one traceability row. Implementation and verification remain `NOT_STARTED` unless a baseline receipt says otherwise.",
        "",
        "| Requirement type | Count |",
        "|---|---:|",
    ]
    for name in ("KEEP", "REMOVE", "ADD", "PROCESS", "VERIFY", "LEGAL", "COMPATIBILITY"):
        coverage_lines.append(f"| {name} | {req_counts[name]} |")
    coverage_lines.extend(["", "| Decision label | Count |", "|---|---:|"])
    for name, count in sorted(decision_counts.items()):
        coverage_lines.append(f"| {cell(name)} | {count} |")
    coverage_lines.extend(
        [
            "",
            "Referential validation confirms 1,420 unique requirement IDs, 1,420 trace rows, 110 capability IDs, and no orphan requirement-to-capability references. Open path, endpoint, parity, review, fixture, legal, and execution blockers are tracked separately; coverage does not imply implementation.",
            "",
        ]
    )
    write("REQUIREMENT_COVERAGE_REPORT.md", coverage_lines)

    unresolved_lines = [
        "# Unresolved Mapping Issues",
        "",
        "Each issue is an execution blocker until its exact next task passes and receives role-separated review.",
        "",
        "| ID | Locality | Exact issue | Exact next task |",
        "|---|---|---|---|",
    ]
    for blocker_id, locality, issue, next_task in blocker_rows:
        unresolved_lines.append(
            f"| `{blocker_id}` | {cell(locality)} | {cell(issue)} | {cell(next_task)} |"
        )
    unresolved_lines.extend(["", "No blocker authorises Codebase mutation, transplant, quarantine, deletion, or purge.", ""])
    write("UNRESOLVED_MAPPING_ISSUES.md", unresolved_lines)

    handoff_lines = [
        "# Final Handoff",
        "",
        "## Resume point",
        "",
        f"Repository: `{baseline['codebaseRoot']}`. Evidence: `{baseline['repositoryRevision']}` with 10,080 file hashes and 2,548 directory paths. Read `../00 Execution Control/status.json`, this handoff, `UNRESOLVED_MAPPING_ISSUES.md`, and `../09 Implementation/IMPLEMENTATION_QUEUE.md` before doing anything else.",
        "",
        "The current result is mapping-only and `NOT_VERIFIED`. Do not begin a Codebase batch until external/reference, endpoint, fixture, dependency-baseline, and independent-review blockers have been cleared and the mapping receipt is reissued with every gate true.",
        "",
        "## Retain, adapt, remove later, add",
        "",
        "- Retain the 19 `KEEP` capabilities and useful AFFiNE/BlockSuite, Electron, editor, model, test, and packaging boundaries named in `CAPABILITY_MATRIX.md`.",
        "- Adapt 12 `KEEP_AND_ADAPT`, three `KEEP_FOR_COMPATIBILITY`, and three `CONDITIONAL` capabilities only through their exact task paths.",
        "- Add 40 capabilities in phases 3–6 within mapped existing packages; avoid one-package or one-folder-per-function fragmentation.",
        "- Isolate/remove 33 capabilities only in phase 7 after every proof, compatibility check, quarantine receipt, scoped check, build/package check, graph update, and independent review passes.",
        "",
        "Current and final paths for every capability are in `../06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json`. Exact symbols are in `../04 Exact Location Registry/SYMBOL_REGISTRY.jsonl`. Public/package ownership is in `../06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json`.",
        "",
        "## AFFiNE transplant rule",
        "",
        "No independent AFFiNE implementation is approved for copying. The active Codebase is the only AFFiNE tree and must be retained/adapted in place where mapped. Do not reinvent coherent AFFiNE editor/runtime capabilities and do not invent substitutes: first obtain a pinned, legally usable independent AFFiNE tree, rerun exact searches, record parity/licence evidence, and obtain independent review. All 110 current transplant records are `SEARCH_INCOMPLETE` and `approved=false`.",
        "",
        "## Execution order",
        "",
    ]
    for phase in order["phases"]:
        handoff_lines.append(
            f"{phase['phase'] + 1}. Phase {phase['phase']} — {phase['name']} ({len(phase['capabilityIds'])} batches)."
        )
    handoff_lines.extend(
        [
            "",
            "Within each phase, use the exact ordering and dependencies in `../07 Reorganisation/REORGANISATION_LEDGER.jsonl`. Normal batches affect at most five source files; a larger coherent-module batch requires its recorded exception and reviewer approval.",
            "",
            "## Checkpoints, verification, and rollback",
            "",
            "Git metadata is unavailable, so every future mutation batch must use the required SHA-256 before/after manifest schema. Record affected, created, modified, moved, quarantined, and purged paths; commands, working directories, exit codes, receipts, reviewer, and rollback. On failure, stop dependants, restore pre-mutation hashes, remove only checkpoint-listed created files, and rerun scoped checks.",
            "",
            "Use exact commands from `../10 Verification/TEST_COMMAND_REGISTRY.json`. Required levels include scoped tests, typecheck/lint, integration/E2E, renderer/electron/production builds, Windows packaging/launch when applicable, offline verification, app-deletion survival, fixture QA, licence/attribution, SBOM, and independent review. Baseline failures caused by missing dependencies are environment/repository-baseline failures, not product regressions.",
            "",
            "## Deletion receipts",
            "",
            "A deletion candidate advances only through the canonical 17-step proof sequence in `../08 Cleanup/DELETION_PROOF_QUEUE.jsonl`. Quarantine must precede repair/tests/build/package/graph/review. Permanent purge requires an approved deletion receipt and must update that receipt to `PURGED`. Mapping completion alone never authorises deletion.",
            "",
            "## Forbidden mutation scope",
            "",
            "Do not modify `Graphify/Master Plan/**`, paths outside a batch's `allowedPaths`, user data outside this workspace, or any unrelated Codebase path. Do not create Git metadata as substitute provenance. Do not delete or quarantine source during mapping.",
            "",
            "## Why the application is not complete",
            "",
            f"All {release_matrix['gateCount']} application release gates remain `NOT_VERIFIED`; implementation was not performed. The exact mapping blockers are in `UNRESOLVED_MAPPING_ISSUES.md`. `FINAL_RELEASE_RECEIPT.json` is locked, `allGatesPassed=false`, and `completionBannerUnlocked=false`.",
            "",
        ]
    )
    write("FINAL_HANDOFF.md", handoff_lines)

    print(
        json.dumps(
            {
                "status": "GENERATED",
                "completionArtifacts": 8,
                "capabilityRows": len(capabilities),
                "requirementRows": len(requirements),
                "blockers": len(blocker_rows),
                "mappingReceiptStatus": mapping_receipt["status"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
