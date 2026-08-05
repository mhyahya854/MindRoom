#!/usr/bin/env python3
"""Generate Phase Eight cleanup findings without changing Codebase."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
CLEANUP = ROOT / "Graphify" / "08 Cleanup"
GRAPHIFY = ROOT / "Graphify"
CODEBASE = ROOT / "Codebase"

PROOF_KEYS = [
    "STATIC_IMPORT_ANALYSIS",
    "RE_EXPORT_ANALYSIS",
    "DYNAMIC_IMPORT_ANALYSIS",
    "CALL_GRAPH",
    "STRING_LOOKUP",
    "DI_REGISTRATION",
    "ROUTE_REGISTRATION",
    "COMMAND_REGISTRATION",
    "IPC_REGISTRATION",
    "WORKER_REGISTRATION",
    "BUILD_REFERENCE",
    "PACKAGING_REFERENCE",
    "MIGRATION_REQUIREMENT",
    "FIXTURE_REQUIREMENT",
    "PLATFORM_SPECIFIC_USE",
    "PLANNED_CAPABILITY_DEPENDENCY",
    "USER_DATA_COMPATIBILITY",
    "REPLACEMENT",
    "TESTS",
    "BUILD",
    "GRAPHIFY_IMPACT",
    "INDEPENDENT_REVIEW",
]

CANONICAL_SEQUENCE = [
    ("DISCOVERY", ["STRING_LOOKUP"]),
    (
        "DEPENDENCY_PROOF",
        [
            "STATIC_IMPORT_ANALYSIS",
            "RE_EXPORT_ANALYSIS",
            "DYNAMIC_IMPORT_ANALYSIS",
            "CALL_GRAPH",
            "BUILD_REFERENCE",
            "PACKAGING_REFERENCE",
            "PLANNED_CAPABILITY_DEPENDENCY",
        ],
    ),
    (
        "RUNTIME_REGISTRATION_PROOF",
        [
            "DI_REGISTRATION",
            "ROUTE_REGISTRATION",
            "COMMAND_REGISTRATION",
            "IPC_REGISTRATION",
            "WORKER_REGISTRATION",
        ],
    ),
    (
        "MIGRATION_AND_DATA_COMPATIBILITY_PROOF",
        [
            "MIGRATION_REQUIREMENT",
            "FIXTURE_REQUIREMENT",
            "PLATFORM_SPECIFIC_USE",
            "USER_DATA_COMPATIBILITY",
            "REPLACEMENT",
        ],
    ),
    ("QUARANTINE", []),
    ("IMPORT_EXPORT_REGISTRATION_REPAIR", []),
    ("SCOPED_TESTS", ["TESTS"]),
    ("TYPECHECK", []),
    ("INTEGRATION_TESTS", []),
    ("PRODUCTION_BUILD", ["BUILD"]),
    ("PACKAGING_CHECKS_WHEN_APPLICABLE", []),
    ("GRAPHIFY_UPDATE", ["GRAPHIFY_IMPACT"]),
    ("INDEPENDENT_REVIEW", ["INDEPENDENT_REVIEW"]),
    ("DELETION_RECEIPT_APPROVED", []),
    ("PERMANENT_PURGE", []),
    ("RECEIPT_UPDATED_TO_PURGED", []),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            stream.write("\n")


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


def proof_requirements() -> dict[str, str]:
    return {proof: "NOT_STARTED" for proof in PROOF_KEYS}


def candidate_state() -> dict[str, Any]:
    return {
        "status": "CANDIDATE",
        "executionStatus": "NOT_STARTED",
        "discoveryStatus": "NOT_STARTED",
        "quarantineStatus": "NOT_STARTED",
        "deletionReceiptStatus": "NOT_STARTED",
        "independentReviewStatus": "NOT_STARTED",
        "approved": False,
        "purged": False,
        "implementationPerformed": False,
        "proofRequirements": proof_requirements(),
    }


def capability_sort_key(capability_id: str) -> int:
    return int(capability_id.rsplit("-", 1)[-1])


def compact_path_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for row in rows:
        evidence.append(
            {
                "boundaryId": row["boundaryId"],
                "path": row["path"],
                "sha256": row["sha256"],
                "discoveryBasis": row["discoveryBasis"],
                "mappingConfidence": row["mappingConfidence"],
            }
        )
    return evidence


def make_deletion_candidates() -> tuple[list[dict[str, Any]], dict[str, int]]:
    removal = load_jsonl(
        GRAPHIFY / "05 Dependency and Impact" / "REMOVAL_BLAST_RADIUS.jsonl"
    )
    boundaries = load_jsonl(
        GRAPHIFY
        / "05 Dependency and Impact"
        / "EXCLUDED_SYSTEM_BOUNDARY_MAP.jsonl"
    )
    dead = load_jsonl(
        GRAPHIFY / "05 Dependency and Impact" / "DEAD_CODE_CANDIDATES.jsonl"
    )
    duplicates = load_jsonl(
        GRAPHIFY
        / "05 Dependency and Impact"
        / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl"
    )
    markdown = load_jsonl(
        GRAPHIFY / "01 Corpus Inventory" / "MARKDOWN_MIGRATION_LEDGER.jsonl"
    )

    boundary_by_capability: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in boundaries:
        boundary_by_capability[row["capabilityId"]].append(row)

    candidates: list[dict[str, Any]] = []

    for blast in sorted(removal, key=lambda row: capability_sort_key(row["capabilityId"])):
        cap_id = blast["capabilityId"]
        mapped = sorted(boundary_by_capability.get(cap_id, []), key=lambda row: row["path"])
        paths = sorted(
            set(blast.get("currentPaths", []))
            | {row["path"] for row in mapped}
        )
        symbols = sorted(
            {
                symbol["entityId"]
                for row in mapped
                for symbol in row.get("symbols", [])
                if symbol.get("entityId")
            }
        )
        candidates.append(
            {
                "candidateId": f"MR-DELETE-EXCLUDED-{cap_id}",
                "candidateType": "EXCLUDED_AFFINE_SYSTEM",
                "classification": "REMOVE_OR_ISOLATE_LATER",
                "capabilityIds": [cap_id],
                "capabilityName": blast["capabilityName"],
                "paths": paths,
                "pathDiscoveryStatus": (
                    "EXACT_PATHS_MAPPED"
                    if paths
                    else "NO_CURRENT_PATH_MAPPED_DISCOVERY_REQUIRED"
                ),
                "symbolEntityIds": symbols,
                "reason": (
                    "The locked capability plan classifies this AFFiNE subsystem for "
                    "future removal or isolation; semantic discovery is boundary mapping, "
                    "not deletion proof."
                ),
                "proposedAction": "FUTURE_QUARANTINE_ONLY_AFTER_ALL_PROOFS",
                "replacement": blast.get("replacementCapabilityId")
                or "REPLACEMENT_OR_LOCAL_ADAPTER_PROOF_REQUIRED",
                "risk": {
                    "level": blast["riskLevel"],
                    "applicationReachablePathCount": len(
                        blast.get("applicationReachablePaths", [])
                    ),
                    "incomingDependentPathCount": len(
                        blast.get("incomingDependentPaths", [])
                    ),
                    "outgoingDependencyPathCount": len(
                        blast.get("outgoingDependencyPaths", [])
                    ),
                    "boundaryRecordCount": len(mapped),
                    "falsePositiveControls": [
                        "Capability classification does not prove every semantically matched path belongs exclusively to the excluded subsystem.",
                        "Mixed retained logic, user-data compatibility, platform use, and replacement ownership require independent proof.",
                    ],
                },
                "dependencyCapabilityIds": sorted(
                    blast.get("dependencyCapabilityIds", []),
                    key=capability_sort_key,
                ),
                "dependantCapabilityIds": sorted(
                    blast.get("dependantCapabilityIds", []),
                    key=capability_sort_key,
                ),
                "evidence": {
                    "removalBlastRadiusId": blast["blastRadiusId"],
                    "capabilityEvidenceIds": blast.get("evidence", []),
                    "boundaryRecords": compact_path_evidence(mapped),
                },
                **candidate_state(),
            }
        )

    for row in sorted(dead, key=lambda value: value["path"]):
        candidates.append(
            {
                "candidateId": f"MR-DELETE-{row['candidateId']}",
                "candidateType": "DEAD_OR_ABANDONED_SIGNAL",
                "classification": "LOW_CONFIDENCE_DEAD_CODE_SIGNAL",
                "capabilityIds": [],
                "paths": [row["path"]],
                "symbolEntityIds": [],
                "reason": (
                    "No resolved internal AST incoming or outgoing edge was mapped. "
                    "Zero mapped edges and a name are not deletion proof."
                ),
                "proposedAction": "INVESTIGATE_ONLY",
                "replacement": row.get("replacement", "UNDETERMINED"),
                "risk": {
                    "level": "HIGH_UNTIL_PROVEN",
                    "applicationRuntimeReachability": row.get(
                        "applicationRuntimeReachability", "UNKNOWN"
                    ),
                    "falsePositiveControls": row.get("falsePositiveRisks", []),
                },
                "dependencyCapabilityIds": [],
                "dependantCapabilityIds": [],
                "evidence": {
                    "sourceCandidateId": row["candidateId"],
                    "sha256": row["sha256"],
                    "candidateBasis": row["candidateBasis"],
                    "package": row["package"],
                    "incomingPaths": row.get("incomingPaths", []),
                    "outgoingPaths": row.get("outgoingPaths", []),
                    "runtimeRegistrations": row.get("runtimeRegistrations", []),
                },
                **candidate_state(),
            }
        )

    for row in sorted(duplicates, key=lambda value: value["candidateId"]):
        candidates.append(
            {
                "candidateId": f"MR-DELETE-{row['candidateId']}",
                "candidateType": "DUPLICATE_IMPLEMENTATION_SIGNAL",
                "classification": "EXACT_CONTENT_DUPLICATE_ONLY",
                "capabilityIds": [],
                "paths": row["paths"],
                "symbolEntityIds": row.get("entityIds", []),
                "reason": (
                    "The files have identical SHA-256 content. Content identity does "
                    "not prove ownership equivalence, canonical replacement, or safe deletion."
                ),
                "proposedAction": "SELECT_CANONICAL_OWNER_THEN_PROVE",
                "replacement": row.get("replacement", "UNDETERMINED"),
                "risk": {
                    "level": "HIGH_UNTIL_OWNER_SELECTED",
                    "runtimeReachability": row.get("runtimeReachability", {}),
                    "falsePositiveControls": row.get("falsePositiveRisks", []),
                },
                "dependencyCapabilityIds": [],
                "dependantCapabilityIds": [],
                "evidence": {
                    "sourceCandidateId": row["candidateId"],
                    "sha256": row["sha256"],
                    "packages": row.get("packages", []),
                    "detectionType": row["detectionType"],
                },
                **candidate_state(),
            }
        )

    for row in sorted(markdown, key=lambda value: value["path"]):
        migration_decision = row["migrationDecision"]
        candidates.append(
            {
                "candidateId": stable_id("MR-DELETE-MARKDOWN", row["path"]),
                "candidateType": "MARKDOWN_MIGRATION_OR_RETENTION",
                "classification": migration_decision,
                "capabilityIds": [],
                "paths": [row["path"]],
                "symbolEntityIds": [],
                "reason": (
                    "Repository Markdown must be migrated to its mapped Graphify "
                    "destination, retained as a verified fixture, or explicitly exempted. "
                    "Extension and filename alone never justify deletion."
                ),
                "proposedAction": (
                    "MIGRATE_NOT_DELETE"
                    if migration_decision == "MOVE_TO_GRAPHIFY_LATER"
                    else "RETAIN_AND_ANALYSE_NOT_DELETE"
                ),
                "replacement": row.get("requiredFinalGraphifyDestination")
                or "NO_REPLACEMENT_SELECTED",
                "risk": {
                    "level": (
                        "HIGH"
                        if row.get("legallyRequired") != "NO"
                        or row.get("userWorkspaceContent") != "NO"
                        or row.get("requiresFurtherAnalysis")
                        else "MEDIUM"
                    ),
                    "legallyRequired": row.get("legallyRequired", "UNKNOWN"),
                    "userWorkspaceContent": row.get("userWorkspaceContent", "UNKNOWN"),
                    "buildOrPackagingReferencesIt": row.get(
                        "buildOrPackagingReferencesIt", False
                    ),
                    "linksReferenceIt": row.get("linksReferenceIt", False),
                    "migrationBlockers": row.get("migrationBlockers", []),
                    "falsePositiveControls": [
                        "Do not treat Markdown as cleanup solely because of its extension.",
                        "Preserve fixtures, user content, legal notices, link targets, and distribution documentation until their dedicated checks pass.",
                    ],
                },
                "dependencyCapabilityIds": [],
                "dependantCapabilityIds": [],
                "evidence": {
                    "sha256": row["sha256"],
                    "package": row["package"],
                    "purpose": row["purpose"],
                    "plannedBatch": row["plannedBatch"],
                    "ledgerStatus": row["status"],
                    "ledgerVerificationRequired": row["verificationRequired"],
                },
                **candidate_state(),
            }
        )

    counts = dict(Counter(row["candidateType"] for row in candidates))
    counts["TOTAL"] = len(candidates)
    return candidates, counts


def make_proof_queue(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    category_order = {
        "MARKDOWN_MIGRATION_OR_RETENTION": 1,
        "DUPLICATE_IMPLEMENTATION_SIGNAL": 2,
        "EXCLUDED_AFFINE_SYSTEM": 3,
        "DEAD_OR_ABANDONED_SIGNAL": 4,
    }
    ordered = sorted(
        candidates,
        key=lambda row: (
            category_order[row["candidateType"]],
            row["candidateId"],
        ),
    )
    cap_candidate = {
        row["capabilityIds"][0]: row["candidateId"]
        for row in candidates
        if row["candidateType"] == "EXCLUDED_AFFINE_SYSTEM"
        and row["capabilityIds"]
    }
    queue: list[dict[str, Any]] = []
    for position, candidate in enumerate(ordered, 1):
        dependency_candidates = sorted(
            {
                cap_candidate[capability_id]
                for capability_id in candidate.get("dependencyCapabilityIds", [])
                if capability_id in cap_candidate
            }
        )
        queue.append(
            {
                "queueId": stable_id("MR-PROOF-QUEUE", candidate["candidateId"]),
                "queueOrder": position,
                "categoryOrder": category_order[candidate["candidateType"]],
                "orderingBasis": (
                    "CONSERVATIVE_CATEGORY_ORDER_NO_EXECUTION; dependency capability "
                    "links are recorded but must be independently topologically reviewed"
                ),
                "candidateId": candidate["candidateId"],
                "candidateType": candidate["candidateType"],
                "capabilityIds": candidate["capabilityIds"],
                "paths": candidate["paths"],
                "pathDiscoveryStatus": candidate.get(
                    "pathDiscoveryStatus", "EXACT_PATHS_MAPPED"
                ),
                "dependencyCandidateIds": dependency_candidates,
                "currentState": "CANDIDATE",
                "executionStatus": "NOT_STARTED",
                "proofRequirements": proof_requirements(),
                "canonicalFutureSequence": [
                    {
                        "sequence": index,
                        "stage": stage,
                        "proofRequirements": proofs,
                        "status": "NOT_STARTED",
                    }
                    for index, (stage, proofs) in enumerate(CANONICAL_SEQUENCE, 1)
                ],
                "approvalStatus": "NOT_STARTED",
                "purgeStatus": "NOT_STARTED",
            }
        )
    return queue


def make_duplicate_registry(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_source = {
        row["evidence"]["sourceCandidateId"]: row
        for row in candidates
        if row["candidateType"] == "DUPLICATE_IMPLEMENTATION_SIGNAL"
    }
    source = load_jsonl(
        GRAPHIFY
        / "05 Dependency and Impact"
        / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl"
    )
    rows: list[dict[str, Any]] = []
    for duplicate in sorted(source, key=lambda row: row["candidateId"]):
        deletion = by_source[duplicate["candidateId"]]
        rows.append(
            {
                "duplicateCandidateId": duplicate["candidateId"],
                "deletionCandidateId": deletion["candidateId"],
                "detectionType": duplicate["detectionType"],
                "sha256": duplicate["sha256"],
                "paths": duplicate["paths"],
                "packages": duplicate.get("packages", []),
                "symbolEntityIds": duplicate.get("entityIds", []),
                "runtimeReachability": duplicate.get("runtimeReachability", {}),
                "canonicalOwner": "UNDETERMINED",
                "replacement": "UNDETERMINED",
                "requiredDecision": (
                    "Decide whether the files are intentional platform/package isolation, "
                    "generated copies, fixtures, or one implementation with a shared owner."
                ),
                "falsePositiveControls": [
                    "Exact bytes do not prove equivalent package boundaries or runtime roles.",
                    "Platform variants may be intentionally isolated even when currently identical.",
                    "Generated files and fixtures require generator/test-discovery proof.",
                    "A shared replacement must not introduce a worse cross-package dependency.",
                ],
                "proofRequirements": proof_requirements(),
                "status": "CANDIDATE",
                "executionStatus": "NOT_STARTED",
                "approved": False,
                "purged": False,
            }
        )
    return rows


PONYTAIL_FINDINGS = [
    {
        "rank": 1,
        "tag": "delete",
        "summary": "Delete the legacy i18n cleanup script; build.ts --cleanup already owns the behavior",
        "replacement": "Use build.ts --cleanup as the single cleanup path",
        "paths": [
            "Codebase/packages/frontend/i18n/cleanup.mjs",
            "Codebase/packages/frontend/i18n/build.ts",
        ],
        "estimatedLinesRemoved": 74,
        "estimatedDependenciesRemoved": 0,
        "evidence": "The package scripts expose build.ts, whose cleanupResources covers the same key-scanning and deletion workflow; cleanup.mjs is not exposed by package scripts.",
    },
    {
        "rank": 2,
        "tag": "shrink",
        "summary": "Collapse the five byte-identical desktop/mobile navigation implementations",
        "replacement": "Keep one shared navigation implementation and import it from both shells",
        "paths": [
            "Codebase/packages/frontend/core/src/desktop/components/navigation-panel/tree/root.css.ts",
            "Codebase/packages/frontend/core/src/mobile/components/navigation/tree/root.css.ts",
            "Codebase/packages/frontend/core/src/desktop/components/navigation-panel/sections/collections/index.css.ts",
            "Codebase/packages/frontend/core/src/mobile/components/navigation/sections/collections/index.css.ts",
            "Codebase/packages/frontend/core/src/desktop/components/navigation-panel/nodes/doc/styles.css.ts",
            "Codebase/packages/frontend/core/src/mobile/components/navigation/nodes/doc/styles.css.ts",
            "Codebase/packages/frontend/core/src/desktop/components/navigation-panel/nodes/tag/styles.css.ts",
            "Codebase/packages/frontend/core/src/mobile/components/navigation/nodes/tag/styles.css.ts",
            "Codebase/packages/frontend/core/src/desktop/components/navigation-panel/nodes/folder/operations.tsx",
            "Codebase/packages/frontend/core/src/mobile/components/navigation/nodes/folder/operations.tsx",
        ],
        "estimatedLinesRemoved": 58,
        "estimatedDependenciesRemoved": 0,
        "evidence": "Five Graphify exact-SHA groups pair desktop and mobile files inside the same package; the estimate reserves re-export/import lines.",
    },
    {
        "rank": 3,
        "tag": "shrink",
        "summary": "Collapse four byte-identical upgrade-success style modules",
        "replacement": "Keep one shared style module for all four consumers",
        "paths": [
            "Codebase/packages/frontend/core/src/components/affine/subscription-landing/styles.css.ts",
            "Codebase/packages/frontend/core/src/desktop/pages/ai-upgrade-success/styles.css.ts",
            "Codebase/packages/frontend/core/src/desktop/pages/upgrade-success/styles.css.ts",
            "Codebase/packages/frontend/core/src/desktop/pages/upgrade-success/team/styles.css.ts",
        ],
        "estimatedLinesRemoved": 39,
        "estimatedDependenciesRemoved": 0,
        "evidence": "All four files share one exact SHA-256 and live in @affine/core.",
    },
    {
        "rank": 4,
        "tag": "shrink",
        "summary": "Collapse the duplicate Slack Markdown renderer",
        "replacement": "Keep one tools-level renderer and import it from both tool entrypoints",
        "paths": [
            "Codebase/tools/changelog/markdown.js",
            "Codebase/tools/copilot-result/markdown.js",
        ],
        "estimatedLinesRemoved": 21,
        "estimatedDependenciesRemoved": 0,
        "evidence": "The two 25-line renderers are byte-identical exact-SHA duplicates.",
    },
    {
        "rank": 5,
        "tag": "shrink",
        "summary": "Collapse the three byte-identical workspace-tab style modules",
        "replacement": "Keep one shared tab-root style module",
        "paths": [
            "Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/adapter.css.ts",
            "Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/frame.css.ts",
            "Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/outline.css.ts",
        ],
        "estimatedLinesRemoved": 8,
        "estimatedDependenciesRemoved": 0,
        "evidence": "All three six-line files share one exact SHA-256 inside @affine/core.",
    },
    {
        "rank": 6,
        "tag": "stdlib",
        "summary": "Remove lodash from the GraphQL package for two one-character case helpers",
        "replacement": "Use two local string-first-character helpers",
        "paths": [
            "Codebase/packages/common/graphql/export-gql-plugin.cjs",
            "Codebase/packages/common/graphql/package.json",
        ],
        "estimatedLinesRemoved": 1,
        "estimatedDependenciesRemoved": 1,
        "evidence": "lodash is referenced only by export-gql-plugin.cjs in this package and only for upperFirst/lowerFirst.",
    },
    {
        "rank": 7,
        "tag": "stdlib",
        "summary": "Remove lodash-es and its type package from tools/utils for identity and two memoized calls",
        "replacement": "Use a default identity closure and module-local lazy caches",
        "paths": [
            "Codebase/tools/utils/src/logger.ts",
            "Codebase/tools/utils/src/format.ts",
            "Codebase/tools/utils/src/yarn.ts",
            "Codebase/tools/utils/package.json",
        ],
        "estimatedLinesRemoved": 2,
        "estimatedDependenciesRemoved": 2,
        "evidence": "tools/utils uses lodash-es only for identity and once, and @types/lodash-es supports only that dependency.",
    },
    {
        "rank": 8,
        "tag": "stdlib",
        "summary": "Drop lodash range from the page-history stylesheet",
        "replacement": "Use Array.from with the existing -20 through 19 bounds",
        "paths": [
            "Codebase/packages/frontend/core/src/components/affine/page-history-modal/styles.css.ts"
        ],
        "estimatedLinesRemoved": 1,
        "estimatedDependenciesRemoved": 0,
        "evidence": "The file needs only a fixed integer sequence and the package already depends on lodash-es elsewhere.",
    },
    {
        "rank": 9,
        "tag": "stdlib",
        "summary": "Drop lodash noop from history snapshot error swallowing",
        "replacement": "Use an inline empty rejection handler",
        "paths": ["Codebase/packages/common/nbstore/src/storage/history.ts"],
        "estimatedLinesRemoved": 1,
        "estimatedDependenciesRemoved": 0,
        "evidence": "The file imports lodash-es only for noop; other nbstore files still use lodash-es.",
    },
]


def make_ponytail_candidates() -> list[dict[str, Any]]:
    return [
        {
            "candidateId": f"MR-PONYTAIL-{finding['rank']:03d}",
            **finding,
            "confidence": "HIGH",
            "scope": "WHOLE_CODEBASE_EXACT_EVIDENCE_AND_TARGETED_DEPENDENCY_USAGE",
            "status": "CANDIDATE",
            "executionStatus": "NOT_STARTED",
            "sourceChangesPerformed": False,
            "independentReviewStatus": "NOT_STARTED",
        }
        for finding in PONYTAIL_FINDINGS
    ]


def audit_lines(findings: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for finding in findings:
        path_list = "; ".join(finding["paths"])
        lines.append(
            f"{finding['tag']} {finding['summary']}. "
            f"{finding['replacement']}. [{path_list}]"
        )
    total_lines = sum(row["estimatedLinesRemoved"] for row in findings)
    total_dependencies = sum(
        row["estimatedDependenciesRemoved"] for row in findings
    )
    lines.append(f"net: -{total_lines} lines, -{total_dependencies} deps possible.")
    return lines


def quarantine_plan(counts: dict[str, int]) -> str:
    return f"""# Quarantine Plan

## State

- Planning only. No Codebase file was edited, moved, quarantined, or deleted.
- `Graphify/08 Cleanup/Quarantine/` must remain empty in this phase.
- `Graphify/08 Cleanup/Deletion Receipts/` contains its existing schema only; no receipt is approved.
- Every candidate is `CANDIDATE`; every execution and proof gate is `NOT_STARTED`.

## Queue inventory

- Excluded AFFiNE capability boundaries: {counts.get("EXCLUDED_AFFINE_SYSTEM", 0)}
- Low-confidence dead or abandoned signals: {counts.get("DEAD_OR_ABANDONED_SIGNAL", 0)}
- Exact-content duplicate groups: {counts.get("DUPLICATE_IMPLEMENTATION_SIGNAL", 0)}
- Markdown migration or retention records: {counts.get("MARKDOWN_MIGRATION_OR_RETENTION", 0)}
- Total records: {counts.get("TOTAL", 0)}

The queues deliberately keep these classes distinct. A REMOVE capability decision is not file-level deletion proof. Zero resolved AST edges is not runtime non-reachability. Exact bytes do not establish common ownership. Markdown requires migration, fixture, user-data, legal, link, and packaging review rather than extension-based deletion.

## Future batch rules

1. Select a narrow candidate batch and an independent reviewer.
2. Re-hash every path and re-run all 22 proof requirements in `DELETION_PROOF_QUEUE.jsonl`.
3. Resolve dependency ordering and any mixed retained capability ownership.
4. Select and verify a replacement before removing imports, exports, registrations, routes, IPC, workers, packaging entries, or persisted-data readers.
5. For Markdown, copy repository documentation to its mapped Graphify destination or retain the fixture/user-content exception; do not delete first.
6. Only after all pre-quarantine proofs pass, move the exact approved batch into Quarantine and create a receipt from the preserved schema.
7. Run scoped tests, typecheck, integration tests, production build, and applicable packaging checks.
8. Update Graphify, obtain independent review, and approve the deletion receipt.
9. Permanent purge is a later explicit action; update a receipt to `PURGED` only after it actually occurs.

## Canonical future sequence

`CANDIDATE -> DISCOVERY -> DEPENDENCY PROOF -> RUNTIME-REGISTRATION PROOF -> MIGRATION AND DATA-COMPATIBILITY PROOF -> QUARANTINE -> IMPORT/EXPORT/REGISTRATION REPAIR -> SCOPED TESTS -> TYPECHECK -> INTEGRATION TESTS -> PRODUCTION BUILD -> PACKAGING CHECKS WHEN APPLICABLE -> GRAPHIFY UPDATE -> INDEPENDENT REVIEW -> DELETION RECEIPT APPROVED -> PERMANENT PURGE -> RECEIPT UPDATED TO PURGED`

## Limitations and blockers

- `Graphify/07 Reorganisation/` contains planning evidence only; no batch is completed, so no deletion may rely on an assumed target move.
- Dynamic imports, string lookup, DI, route, command, IPC, worker, build, packaging, platform, fixture, migration, and user-data checks remain `NOT_STARTED`.
- Dead-code signals are intentionally low confidence; native tools, shell scripts, package exports, generated loading, aliases, CI, and deployment systems can bypass the mapped AST graph.
- Duplicate candidates have no canonical owner selected.
- Excluded-system boundary discovery used semantic signals and may include mixed retained logic.
- The Ponytail audit is an estimates-only human review surface, not authority to implement its suggestions.

## Required handoff

Request an independent reviewer to verify category separation, path/capability references, proof completeness, ordering, replacement ownership, and the untouched receipt schema/empty Quarantine invariant before any future execution task is opened.
"""


def main() -> None:
    candidates, counts = make_deletion_candidates()
    queue = make_proof_queue(candidates)
    duplicates = make_duplicate_registry(candidates)
    ponytail = make_ponytail_candidates()

    write_jsonl(CLEANUP / "DELETION_CANDIDATES.jsonl", candidates)
    write_jsonl(CLEANUP / "DELETION_PROOF_QUEUE.jsonl", queue)
    write_jsonl(CLEANUP / "DUPLICATE_CODE_CANDIDATES.jsonl", duplicates)
    write_jsonl(CLEANUP / "PONYTAIL_CANDIDATES.jsonl", ponytail)
    (CLEANUP / "PONYTAIL_AUDIT.md").write_text(
        "\n".join(audit_lines(ponytail)) + "\n", encoding="utf-8", newline="\n"
    )
    (CLEANUP / "QUARANTINE_PLAN.md").write_text(
        quarantine_plan(counts), encoding="utf-8", newline="\n"
    )

    print(json.dumps({"counts": counts, "ponytailFindings": len(ponytail)}))


if __name__ == "__main__":
    main()
