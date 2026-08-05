#!/usr/bin/env python3
"""Validate Phase Eight findings and the no-action invariants."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CLEANUP = ROOT / "Graphify" / "08 Cleanup"
GRAPHIFY = ROOT / "Graphify"
CODEBASE = ROOT / "Codebase"
SCHEMA = CLEANUP / "Deletion Receipts" / "deletion-receipt.schema.json"
QUARANTINE = CLEANUP / "Quarantine"
EXPECTED_SCHEMA_SHA256 = (
    "83359c9398a0919ef4141b45e01aa31e5a27578f37f48619d0ba45fc9f52c7fa"
)
PROOF_KEYS = {
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
}
EXPECTED_COUNTS = {
    "EXCLUDED_AFFINE_SYSTEM": 33,
    "DEAD_OR_ABANDONED_SIGNAL": 103,
    "DUPLICATE_IMPLEMENTATION_SIGNAL": 23,
    "MARKDOWN_MIGRATION_OR_RETENTION": 207,
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise AssertionError(f"{path}:{line_number}: invalid JSON: {error}") from error
    return rows


def assert_paths(
    paths: list[str], context: str, path_discovery_status: str = "EXACT_PATHS_MAPPED"
) -> None:
    if not paths:
        assert path_discovery_status == "NO_CURRENT_PATH_MAPPED_DISCOVERY_REQUIRED", (
            f"{context}: empty paths are allowed only with an explicit discovery blocker"
        )
        return
    for path in paths:
        assert path.startswith("Codebase/"), f"{context}: non-Codebase path {path}"
        assert (ROOT / path).is_file(), f"{context}: missing path {path}"


def assert_proofs(proofs: dict[str, str], context: str) -> None:
    assert set(proofs) == PROOF_KEYS, f"{context}: proof key mismatch"
    assert set(proofs.values()) == {"NOT_STARTED"}, (
        f"{context}: proof status is not uniformly NOT_STARTED"
    )


def validate_candidates(
    valid_capabilities: set[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    rows = load_jsonl(CLEANUP / "DELETION_CANDIDATES.jsonl")
    ids = [row["candidateId"] for row in rows]
    assert len(ids) == len(set(ids)), "duplicate deletion candidate IDs"
    counts = Counter(row["candidateType"] for row in rows)
    assert dict(counts) == EXPECTED_COUNTS, (
        f"candidate category counts differ: {dict(counts)}"
    )
    for row in rows:
        context = row["candidateId"]
        assert row["status"] == "CANDIDATE", f"{context}: invalid status"
        assert row["executionStatus"] == "NOT_STARTED", f"{context}: executed"
        assert row["discoveryStatus"] == "NOT_STARTED", f"{context}: discovery ran"
        assert row["quarantineStatus"] == "NOT_STARTED", f"{context}: quarantined"
        assert row["deletionReceiptStatus"] == "NOT_STARTED", (
            f"{context}: receipt changed"
        )
        assert row["independentReviewStatus"] == "NOT_STARTED", (
            f"{context}: review changed"
        )
        assert row["approved"] is False, f"{context}: approved"
        assert row["purged"] is False, f"{context}: purged"
        assert row["implementationPerformed"] is False, f"{context}: implemented"
        assert_proofs(row["proofRequirements"], context)
        assert_paths(row["paths"], context, row.get("pathDiscoveryStatus", ""))
        assert set(row["capabilityIds"]) <= valid_capabilities, (
            f"{context}: invalid capability reference"
        )
        for related in row.get("dependencyCapabilityIds", []) + row.get(
            "dependantCapabilityIds", []
        ):
            assert related in valid_capabilities, (
                f"{context}: invalid related capability {related}"
            )
        if row["candidateType"] == "MARKDOWN_MIGRATION_OR_RETENTION":
            assert row["proposedAction"] in {
                "MIGRATE_NOT_DELETE",
                "RETAIN_AND_ANALYSE_NOT_DELETE",
            }
    return rows, set(ids)


def validate_queue(candidate_ids: set[str], valid_capabilities: set[str]) -> None:
    rows = load_jsonl(CLEANUP / "DELETION_PROOF_QUEUE.jsonl")
    assert len(rows) == len(candidate_ids), "proof queue does not cover every candidate"
    assert [row["queueOrder"] for row in rows] == list(range(1, len(rows) + 1)), (
        "proof queue order is not contiguous"
    )
    assert [row["categoryOrder"] for row in rows] == sorted(
        row["categoryOrder"] for row in rows
    ), "proof queue category order is not monotonic"
    seen: set[str] = set()
    for row in rows:
        context = row["queueId"]
        assert row["candidateId"] in candidate_ids, f"{context}: missing candidate"
        assert row["candidateId"] not in seen, f"{context}: duplicate candidate"
        seen.add(row["candidateId"])
        assert row["currentState"] == "CANDIDATE", f"{context}: invalid state"
        assert row["executionStatus"] == "NOT_STARTED", f"{context}: executed"
        assert row["approvalStatus"] == "NOT_STARTED", f"{context}: approved"
        assert row["purgeStatus"] == "NOT_STARTED", f"{context}: purged"
        assert_proofs(row["proofRequirements"], context)
        assert_paths(row["paths"], context, row.get("pathDiscoveryStatus", ""))
        assert set(row["capabilityIds"]) <= valid_capabilities
        stages = row["canonicalFutureSequence"]
        assert len(stages) == 16, f"{context}: incomplete canonical sequence"
        assert [stage["sequence"] for stage in stages] == list(range(1, 17))
        assert set(stage["status"] for stage in stages) == {"NOT_STARTED"}
        staged_proofs = [
            proof for stage in stages for proof in stage["proofRequirements"]
        ]
        assert len(staged_proofs) == len(set(staged_proofs)), (
            f"{context}: duplicated proof in sequence"
        )
        assert set(staged_proofs) == PROOF_KEYS, (
            f"{context}: sequence does not cover all proof requirements"
        )
        assert set(row["dependencyCandidateIds"]) <= candidate_ids
    assert seen == candidate_ids, "proof queue candidate coverage mismatch"


def validate_duplicates(candidate_ids: set[str]) -> None:
    rows = load_jsonl(CLEANUP / "DUPLICATE_CODE_CANDIDATES.jsonl")
    assert len(rows) == EXPECTED_COUNTS["DUPLICATE_IMPLEMENTATION_SIGNAL"]
    source_rows = load_jsonl(
        GRAPHIFY
        / "05 Dependency and Impact"
        / "DUPLICATE_IMPLEMENTATION_CANDIDATES.jsonl"
    )
    source_by_id = {row["candidateId"]: row for row in source_rows}
    for row in rows:
        context = row["duplicateCandidateId"]
        assert row["deletionCandidateId"] in candidate_ids
        assert row["status"] == "CANDIDATE"
        assert row["executionStatus"] == "NOT_STARTED"
        assert row["approved"] is False
        assert row["purged"] is False
        assert_proofs(row["proofRequirements"], context)
        assert_paths(row["paths"], context)
        source = source_by_id[context]
        assert row["paths"] == source["paths"], f"{context}: path drift"
        assert row["sha256"] == source["sha256"], f"{context}: hash drift"
        for path in row["paths"]:
            actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            assert actual == row["sha256"], f"{context}: source hash drift at {path}"


def validate_ponytail() -> None:
    rows = load_jsonl(CLEANUP / "PONYTAIL_CANDIDATES.jsonl")
    assert len(rows) == 9, "unexpected Ponytail finding count"
    assert [row["rank"] for row in rows] == list(range(1, 10))
    allowed_tags = {"delete", "stdlib", "native", "yagni", "shrink"}
    for row in rows:
        assert row["tag"] in allowed_tags
        assert row["status"] == "CANDIDATE"
        assert row["executionStatus"] == "NOT_STARTED"
        assert row["sourceChangesPerformed"] is False
        assert row["independentReviewStatus"] == "NOT_STARTED"
        assert_paths(row["paths"], row["candidateId"])

    audit = (CLEANUP / "PONYTAIL_AUDIT.md").read_text(encoding="utf-8").splitlines()
    assert len(audit) == len(rows) + 1
    finding_pattern = re.compile(
        r"^(delete|stdlib|native|yagni|shrink) .+\. .+\. \[Codebase/.+\]$"
    )
    assert all(finding_pattern.match(line) for line in audit[:-1]), (
        "PONYTAIL_AUDIT.md finding format mismatch"
    )
    expected_lines = sum(row["estimatedLinesRemoved"] for row in rows)
    expected_deps = sum(row["estimatedDependenciesRemoved"] for row in rows)
    assert audit[-1] == (
        f"net: -{expected_lines} lines, -{expected_deps} deps possible."
    ), "PONYTAIL_AUDIT.md net line mismatch"


def validate_invariants() -> None:
    schema_hash = hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    assert schema_hash == EXPECTED_SCHEMA_SHA256, "deletion receipt schema changed"
    assert QUARANTINE.is_dir(), "Quarantine directory is missing"
    assert not any(QUARANTINE.iterdir()), "Quarantine directory is not empty"
    plan = (CLEANUP / "QUARANTINE_PLAN.md").read_text(encoding="utf-8")
    assert "`Graphify/07 Reorganisation/` contains planning evidence only" in plan
    forbidden = ('"status":"PURGED"', '"status":"APPROVED"', '"approved":true')
    for path in [
        CLEANUP / "DELETION_CANDIDATES.jsonl",
        CLEANUP / "DELETION_PROOF_QUEUE.jsonl",
        CLEANUP / "DUPLICATE_CODE_CANDIDATES.jsonl",
        CLEANUP / "PONYTAIL_CANDIDATES.jsonl",
    ]:
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), (
            f"{path.name}: forbidden completed state"
        )


def main() -> None:
    registry = json.loads(
        (GRAPHIFY / "03 Capability Map" / "CAPABILITY_REGISTRY.json").read_text(
            encoding="utf-8"
        )
    )
    valid_capabilities = {
        capability["capabilityId"] for capability in registry["capabilities"]
    }
    candidates, candidate_ids = validate_candidates(valid_capabilities)
    validate_queue(candidate_ids, valid_capabilities)
    validate_duplicates(candidate_ids)
    validate_ponytail()
    validate_invariants()
    counts = Counter(row["candidateType"] for row in candidates)
    print(
        json.dumps(
            {
                "status": "PASS",
                "candidateCount": len(candidates),
                "categoryCounts": dict(counts),
                "proofRequirementsPerCandidate": len(PROOF_KEYS),
                "quarantineEntries": 0,
                "receiptSchemaSha256": EXPECTED_SCHEMA_SHA256,
                "ponytailFindings": 9,
                "limitations": [
                    "Graphify/07 Reorganisation contains planning evidence only; no batch is completed.",
                    "All proof, review, quarantine, implementation, and purge work remains NOT_STARTED.",
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
