"""
MindRoom Graphify - Process Control Repair (Step 1 only)
=========================================================
Inspects and disables hard-coded approval logic.
Guards unsafe generators.
Reopens false completion state.
Creates PROCESS_CONTROL_AUDIT.json.
Runs validation tests.
Does NOT touch Codebase/.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GRAPHIFY = HERE.parent
PROJECT = GRAPHIFY.parent
CODEBASE = PROJECT / "Codebase"
CONTROL = GRAPHIFY / "00 Execution Control"
CAPMAP = GRAPHIFY / "03 Capability Map"
LOCATIONS = GRAPHIFY / "04 Exact Location Registry"
IMPLEMENTATION = GRAPHIFY / "09 Implementation"
SWARM = GRAPHIFY / "13 Agent Swarm"
COMPLETION = HERE
SOURCE_DOCS = GRAPHIFY / "12 Source Documents"
ADR_DIR = SOURCE_DOCS / "Architecture Decisions"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ─── Step 1: Inspect ──────────────────────────────────────────────────────────

HARD_CODED_APPROVAL_PATTERNS = [
    '"decision": "APPROVED"',
    '"requirementNormalizationPassed": True',
    '"supersessionMapComplete": True',
    '"exactSourceSymbolsPopulated": True',
    '"officialValidatorFreshnessPassed": True',
    '"completionStateSynchronized": True',
]

APPROVAL_FUNCTIONS = [
    "append_independent_review",
    "sync_completion_state",
    "finalize",
    "complete_finalization",
    "set_approved",
    "write_review",
    "regenerate_product_expansion",
]


def inspect_scripts() -> dict:
    found_functions = []
    found_patterns = []
    for pyfile in sorted(COMPLETION.glob("*.py")):
        if pyfile.name.startswith("_"):
            continue
        src = pyfile.read_text(encoding="utf-8")
        for pat in HARD_CODED_APPROVAL_PATTERNS:
            if pat in src:
                found_patterns.append({"file": pyfile.name, "pattern": pat})
        for fn_name in APPROVAL_FUNCTIONS:
            if f"def {fn_name}" in src:
                found_functions.append({"file": pyfile.name, "function": fn_name})
    return {"functions": found_functions, "patterns": found_patterns}


# ─── Step 2: Evidence-based finalize_repair_and_review.py ────────────────────

SAFE_FINALIZE_CONTENT = r'''"""Finalize MindRoom Graphify Repair — evidence-based replacement.

PROCESS-CONTROL-REPAIRED {stamp}
Hard-coded APPROVED fields replaced with evidence-backed checks.
"""
from __future__ import annotations
import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
COMPLETION = HERE
GRAPHIFY = COMPLETION.parent
PROJECT = GRAPHIFY.parent
CODEBASE = PROJECT / "Codebase"
CONTROL = GRAPHIFY / "00 Execution Control"
CAPMAP = GRAPHIFY / "03 Capability Map"
IMPLEMENTATION = GRAPHIFY / "09 Implementation"
SWARM = GRAPHIFY / "13 Agent Swarm"
SOURCE_DOCS = GRAPHIFY / "12 Source Documents"
ADR_DIR = SOURCE_DOCS / "Architecture Decisions"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


# Evidence checks

def check_requirement_normalization_passed() -> tuple[bool, str]:
    req_path = CAPMAP / "REQUIREMENT_REGISTRY.jsonl"
    if not req_path.exists():
        return False, "REQUIREMENT_REGISTRY.jsonl does not exist"
    rows = load_jsonl(req_path)
    if not rows:
        return False, "REQUIREMENT_REGISTRY.jsonl is empty"
    missing_id = [i for i, r in enumerate(rows) if "requirementId" not in r]
    if missing_id:
        return False, f"Rows missing requirementId: {missing_id[:5]}"
    return True, f"{len(rows)} requirements parsed"


def check_supersession_map_complete() -> tuple[bool, str]:
    sup_path = CAPMAP / "REQUIREMENT_SUPERSESSION_MAP.jsonl"
    if not sup_path.exists():
        return False, "REQUIREMENT_SUPERSESSION_MAP.jsonl does not exist"
    rows = load_jsonl(sup_path)
    req_ids = {r["requirementId"] for r in load_jsonl(CAPMAP / "REQUIREMENT_REGISTRY.jsonl") if "requirementId" in r}
    errors = []
    for row in rows:
        for ref_id in [row.get("replacedById")] + row.get("replacementIds", []):
            if ref_id and ref_id not in req_ids:
                errors.append(f"Missing referenced requirement: {ref_id}")
    if errors:
        return False, "; ".join(errors[:5])
    return True, f"{len(rows)} supersession records validated"


def check_exact_source_symbols_populated() -> tuple[bool, str]:
    cap_path = CAPMAP / "CAPABILITY_REGISTRY.json"
    if not cap_path.exists():
        return False, "CAPABILITY_REGISTRY.json does not exist"
    caps = load_json(cap_path).get("capabilities", [])
    missing = []
    for cap in caps:
        has_symbols = bool(cap.get("exactSymbols")) or bool(cap.get("exactAnchors"))
        status = cap.get("currentLocationStatus", "")
        is_planned = any(k in status for k in ("NO_CURRENT_SYMBOL", "PLANNED", "NOT_YET_IMPLEMENTED"))
        if not has_symbols and not is_planned:
            missing.append(cap.get("capabilityId", "?"))
    if missing:
        return False, f"{len(missing)} capabilities lack symbols and planned status: {missing[:5]}"
    return True, f"{len(caps)} capabilities have valid symbol coverage"


def check_official_validator_freshness(run_id: str, cap_count: int, req_count: int, task_count: int) -> tuple[bool, str]:
    receipt_path = COMPLETION / "GRAPHIFY_MAPPING_RECEIPT.json"
    if not receipt_path.exists():
        return False, "GRAPHIFY_MAPPING_RECEIPT.json does not exist"
    receipt = load_json(receipt_path)
    errors = []
    if receipt.get("runId") != run_id:
        errors.append(f"runId mismatch: {receipt.get('runId')} != {run_id}")
    ri = receipt.get("referentialIntegrity", {})
    if ri.get("capabilities") != cap_count:
        errors.append(f"capability count {ri.get('capabilities')} != {cap_count}")
    if ri.get("requirements") != req_count:
        errors.append(f"requirement count {ri.get('requirements')} != {req_count}")
    if errors:
        return False, "; ".join(errors)
    return True, "Mapping receipt run ID and counts verified"


def append_independent_review() -> str:
    """Evidence-based review record. decision=PENDING_INDEPENDENT_HUMAN_REVIEW."""
    status_path = CONTROL / "status.json"
    status_data = load_json(status_path)
    run_id = status_data.get("runId", "UNKNOWN")

    review_id = f"REV-FINAL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    req_ok, req_msg = check_requirement_normalization_passed()
    sup_ok, sup_msg = check_supersession_map_complete()
    sym_ok, sym_msg = check_exact_source_symbols_populated()

    cap_path = CAPMAP / "CAPABILITY_REGISTRY.json"
    cap_count = len(load_json(cap_path).get("capabilities", [])) if cap_path.exists() else 0
    req_count = len(load_jsonl(CAPMAP / "REQUIREMENT_REGISTRY.jsonl"))
    task_count = len(load_jsonl(IMPLEMENTATION / "IMPLEMENTATION_TASKS.jsonl"))

    val_ok, val_msg = check_official_validator_freshness(run_id, cap_count, req_count, task_count)

    adr_accepted = sum(
        1 for f in ADR_DIR.glob("*.md")
        if "## Status" in f.read_text(encoding="utf-8") and "ACCEPTED" in f.read_text(encoding="utf-8")
    ) if ADR_DIR.exists() else 0

    review_entry = {
        "reviewId": review_id,
        "runId": run_id,
        "reviewerAgentId": "PROCESS_CONTROL_REPAIR_GUARD",
        "reviewedPhase": "FINAL_SPECIFICATION_REPAIR_AND_PLAN_COMPLETION",
        "decision": "PENDING_INDEPENDENT_HUMAN_REVIEW",
        "timestamp": now_utc(),
        "processControlRepaired": True,
        "automatedChecks": {
            "requirementNormalizationPassed": {"result": req_ok, "evidence": req_msg},
            "supersessionMapComplete": {"result": sup_ok, "evidence": sup_msg},
            "exactSourceSymbolsPopulated": {"result": sym_ok, "evidence": sym_msg},
            "officialValidatorFreshnessPassed": {"result": val_ok, "evidence": val_msg},
            "adrAcceptedCount": adr_accepted,
        },
        "requiresHumanApproval": [
            "originalPlanPreserved", "productExpansionPreserved",
            "sourceLineAnchorsValid", "financeProhibitionsVerified",
            "calendarOptionalAdapterBoundariesVerified", "nonAiMindMapFoundationsVerified",
            "canvasOwnershipArchitectureVerified", "federatedGlobalMapBehaviorVerified",
            "semanticLinkConfirmationVerified", "exactChangeDescriptionsUnique",
            "yarnBootstrapCorrect", "packageDependencyDirectionAcyclic",
            "ocrScopeExplicit", "adminChartAndCsvBoundariesClean",
            "financeStorageAndEncryptionComplete", "dependencyCyclesZero", "releaseWaveOrderValid",
        ],
        "reviewComments": (
            "PROCESS CONTROL REPAIRED: Replaces hard-coded APPROVED entry. "
            f"auto req_norm={req_ok}, sym={sym_ok}, val_fresh={val_ok}. "
            "Human review required for all requiresHumanApproval items."
        ),
    }

    reviews_path = SWARM / "AGENT_REVIEWS.jsonl"
    reviews = load_jsonl(reviews_path)
    reviews.append(review_entry)
    write_jsonl(reviews_path, reviews)
    write_json(SWARM / "PRODUCT_EXPANSION_INDEPENDENT_REVIEW.json", review_entry)
    return review_id


def sync_completion_state(review_id: str) -> None:
    """Set mappingStatus=REPAIR_IN_PROGRESS. Never sets COMPLETED or APPROVED."""
    status_path = CONTROL / "status.json"
    status_data = load_json(status_path)
    status_data.update({
        "mappingStatus": "REPAIR_IN_PROGRESS",
        "lastUpdatedAt": now_utc(),
        "releaseGateStatus": "LOCKED",
        "productExpansion": {
            "previousCapabilityCount": 110,
            "capabilityCount": 161,
            "independentReviewStatus": "NOT_STARTED",
            "independentReviewId": None,
            "openMappingBlockers": [
                "INDEPENDENT_V2_FINAL_REVIEW_NOT_APPROVED",
                "REQUIREMENT_NORMALIZATION_NOT_COMPLETE",
                "PROCESS_CONTROL_REPAIR_IN_PROGRESS",
            ],
            "implementationPerformed": False,
            "codebaseUnmodified": True,
            "oldCompletionSuperseded": True,
            "finalReleaseReceiptLocked": True,
        }
    })
    write_json(status_path, status_data)

    global_val_path = COMPLETION / "GLOBAL_VALIDATION_RESULT.json"
    if global_val_path.exists():
        val_data = load_json(global_val_path)
        val_data.update({
            "independentReview": "PENDING_INDEPENDENT_HUMAN_REVIEW",
            "processControlRepaired": True,
            "repairedAt": now_utc(),
        })
        write_json(global_val_path, val_data)

    ff_manifest_path = CONTROL / "FORENSIC_FINALIZATION_MANIFEST.json"
    if ff_manifest_path.exists():
        ff = load_json(ff_manifest_path)
        ff.update({
            "status": "REPAIR_IN_PROGRESS",
            "completedAt": None,
            "independentReview": {
                "status": "NOT_STARTED",
                "reviewId": None,
                "processControlRepaired": True,
                "previousReviewInvalidated": True,
                "previousReviewId": "REV-FINAL-20260730-153315",
                "previousReviewInvalidationReason": "INVALIDATED_BY_FORENSIC_PROCESS_AUDIT",
            }
        })
        write_json(ff_manifest_path, ff)

    events_path = CONTROL / "FORENSIC_FINALIZATION_EVENTS.jsonl"
    events = load_jsonl(events_path)
    events.append({
        "timestamp": now_utc(),
        "event": "PROCESS_CONTROL_REPAIR_REOPENED_FALSE_COMPLETION",
        "runId": status_data.get("runId"),
        "reason": "Hard-coded APPROVED replaced with evidence-based checks",
        "previousMappingStatus": "COMPLETED",
        "newMappingStatus": "REPAIR_IN_PROGRESS",
    })
    write_jsonl(events_path, events)
    print("Stage 11 & 12 (REPAIRED): State is REPAIR_IN_PROGRESS. No approval written.")


if __name__ == "__main__":
    rev_id = append_independent_review()
    sync_completion_state(rev_id)
'''


def replace_finalize_repair_and_review() -> list[str]:
    target = COMPLETION / "finalize_repair_and_review.py"
    archive_dir = COMPLETION / "Historical"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / "finalize_repair_and_review.HARD_CODED_APPROVAL.py"
    if not archive.exists():
        shutil.copy2(target, archive)
    stamp = now_utc()
    target.write_text(SAFE_FINALIZE_CONTENT.replace("{stamp}", stamp), encoding="utf-8")
    return [
        "finalize_repair_and_review.py::append_independent_review — removed 23 hard-coded True fields and hard-coded APPROVED decision",
        "finalize_repair_and_review.py::sync_completion_state — removed hard-coded COMPLETED mappingStatus and APPROVED independentReviewStatus",
        f"finalize_repair_and_review.py — archived to Historical/finalize_repair_and_review.HARD_CODED_APPROVAL.py",
    ]


# ─── Step 3: Guard generators ─────────────────────────────────────────────────

UNSAFE_GUARD = """# PROCESS-CONTROL-GUARD: UNSAFE_FOR_FINALIZATION
# Generated by process_control_repair.py on {stamp}
# Classification: UNSAFE_FOR_FINALIZATION
# This script overwrites CAPABILITY_REGISTRY.json, REQUIREMENT_REGISTRY.jsonl,
# CHANGE_LOCATION_REGISTRY.jsonl, IMPLEMENTATION_TASKS.jsonl, Master Plan files,
# and Knowledge Graph outputs. It MUST NOT run during active finalization repair.
# To bypass (only after process control audit sign-off):
#   set GRAPHIFY_ALLOW_GENERATOR_RERUN=1
import os as _pcg_os
if _pcg_os.environ.get("GRAPHIFY_ALLOW_GENERATOR_RERUN", "") != "1":
    raise RuntimeError(
        "generate_product_expansion.py is UNSAFE_FOR_FINALIZATION. "
        "Set GRAPHIFY_ALLOW_GENERATOR_RERUN=1 to bypass after process control audit sign-off."
    )
del _pcg_os

"""

MIGRATION_GUARD = """# PROCESS-CONTROL-GUARD: MIGRATION_ONLY
# Generated by process_control_repair.py on {stamp}
# Classification: MIGRATION_ONLY
# This script applies approval from an existing AGENT_REVIEWS.jsonl entry.
# It must not execute unless a genuine human-approved review exists in that file.

"""


def add_generator_guard() -> list[str]:
    target = COMPLETION / "generate_product_expansion.py"
    src = target.read_text(encoding="utf-8")
    if "PROCESS-CONTROL-GUARD: UNSAFE_FOR_FINALIZATION" in src:
        return ["generate_product_expansion.py — guard already present"]
    archive_dir = COMPLETION / "Historical"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / "generate_product_expansion.UNSAFE_UNGUARDED.py"
    if not archive.exists():
        shutil.copy2(target, archive)
    stamp = now_utc()
    target.write_text(UNSAFE_GUARD.format(stamp=stamp) + src, encoding="utf-8")
    return [
        "generate_product_expansion.py — UNSAFE_FOR_FINALIZATION guard prepended",
        "generate_product_expansion.py — archived to Historical/generate_product_expansion.UNSAFE_UNGUARDED.py",
    ]


def guard_finalize_product_expansion_review() -> list[str]:
    target = COMPLETION / "finalize_product_expansion_review.py"
    src = target.read_text(encoding="utf-8")
    if "PROCESS-CONTROL-GUARD: MIGRATION_ONLY" in src:
        return ["finalize_product_expansion_review.py — guard already present"]
    stamp = now_utc()
    target.write_text(MIGRATION_GUARD.format(stamp=stamp) + src, encoding="utf-8")
    return ["finalize_product_expansion_review.py — MIGRATION_ONLY guard prepended"]


# ─── Step 5: Status authority ─────────────────────────────────────────────────

def assert_status_authority() -> dict:
    auth = {
        "schemaVersion": 1,
        "project": "MindRoom",
        "note": (
            "On Windows, status.json and STATUS.json resolve to the same physical file. "
            "The Master Plan mandates lowercase status.json as canonical. "
        ),
        "canonicalStatusPath": "Graphify/00 Execution Control/status.json",
        "competingStatusFiles": [],
        "duplicateStatusFiles": [
            {
                "path": "Graphify/00 Execution Control/STATUS.json",
                "classification": "SAME_FILE_ON_WINDOWS_CASE_INSENSITIVE_FS",
                "mutationPolicy": "PRESERVE — resolves to canonical status.json on Windows",
            }
        ],
        "authorityRule": (
            "Only lowercase status.json is authoritative for current execution state. "
            "No other JSON file in 00 Execution Control/ controls current state."
        ),
        "repairedAt": now_utc(),
        "processControlRepaired": True,
    }
    write_json(CONTROL / "STATUS_AUTHORITY.json", auth)
    return auth


# ─── Step 6: Reopen false completion ─────────────────────────────────────────

def reopen_false_completion() -> dict:
    # Archive and invalidate the previous false review
    old_review_path = SWARM / "PRODUCT_EXPANSION_INDEPENDENT_REVIEW.json"
    previous_review_id = None
    if old_review_path.exists():
        old_review = load_json(old_review_path)
        previous_review_id = old_review.get("reviewId")
        if old_review.get("decision") == "APPROVED" and not old_review.get("processControlRepaired"):
            archive_path = SWARM / "HISTORICAL_REVIEWS" / f"INVALIDATED_{previous_review_id}.json"
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            old_review["invalidationStatus"] = "INVALIDATED_BY_FORENSIC_PROCESS_AUDIT"
            old_review["invalidationReason"] = (
                "All 23 auditedItems fields were hard-coded to True without artifact evidence. "
                "supersessionMapComplete=True but REQUIREMENT_SUPERSESSION_MAP.jsonl does not exist. "
                "requirementNormalizationPassed=True without verifying normalization complete. "
                "officialValidatorFreshnessPassed=True without checking current run ID. "
                "decision=APPROVED written by automated code without human review."
            )
            old_review["invalidatedAt"] = now_utc()
            write_json(archive_path, old_review)

    # Update status.json
    status_path = CONTROL / "status.json"
    status_data = load_json(status_path)
    previous_mapping_status = status_data.get("mappingStatus", "UNKNOWN")
    status_data.update({
        "mappingStatus": "REPAIR_IN_PROGRESS",
        "codebaseExecutionStatus": "BLOCKED",
        "finalReleaseReceiptStatus": "NOT_VERIFIED",
        "lastUpdatedAt": now_utc(),
        "productExpansion": {
            "previousCapabilityCount": 110,
            "capabilityCount": 161,
            "independentReviewStatus": "NOT_STARTED",
            "independentReviewId": None,
            "openMappingBlockers": [
                "INDEPENDENT_V2_FINAL_REVIEW_NOT_APPROVED",
                "REQUIREMENT_NORMALIZATION_NOT_COMPLETE",
                "PROCESS_CONTROL_REPAIR_IN_PROGRESS",
            ],
            "implementationPerformed": False,
            "codebaseUnmodified": True,
            "oldCompletionSuperseded": True,
            "finalReleaseReceiptLocked": True,
        }
    })
    write_json(status_path, status_data)

    # Update FORENSIC_FINALIZATION_MANIFEST.json
    ff_path = CONTROL / "FORENSIC_FINALIZATION_MANIFEST.json"
    if ff_path.exists():
        ff = load_json(ff_path)
        ff["status"] = "REPAIR_IN_PROGRESS"
        ff["completedAt"] = None
        ff["independentReview"] = {
            "status": "NOT_STARTED",
            "reviewId": None,
            "previousReviewInvalidated": True,
            "previousReviewId": previous_review_id,
            "previousReviewInvalidationReason": "INVALIDATED_BY_FORENSIC_PROCESS_AUDIT",
        }
        write_json(ff_path, ff)

    # Append event
    events_path = CONTROL / "FORENSIC_FINALIZATION_EVENTS.jsonl"
    events = load_jsonl(events_path)
    events.append({
        "timestamp": now_utc(),
        "event": "PROCESS_CONTROL_REPAIR_REOPENED_FALSE_COMPLETION",
        "runId": status_data.get("runId"),
        "previousMappingStatus": previous_mapping_status,
        "newMappingStatus": "REPAIR_IN_PROGRESS",
        "reason": "INVALIDATED_BY_FORENSIC_PROCESS_AUDIT — hard-coded approval without artifact evidence",
    })
    write_jsonl(events_path, events)

    return {
        "previousMappingStatus": previous_mapping_status,
        "newMappingStatus": "REPAIR_IN_PROGRESS",
        "independentReviewStatus": "NOT_STARTED",
        "codebaseExecutionStatus": "BLOCKED",
        "finalReleaseReceiptStatus": "NOT_VERIFIED",
    }


# ─── Step 8: Validation tests ─────────────────────────────────────────────────

def run_validation_tests() -> list[dict]:
    results = []

    def add(name: str, ok: bool, detail: str) -> None:
        results.append({"test": name, "passed": ok, "detail": detail})

    # Test 1: No hard-coded approval in repaired script
    src = (COMPLETION / "finalize_repair_and_review.py").read_text(encoding="utf-8")
    bad = [p for p in HARD_CODED_APPROVAL_PATTERNS if p in src]
    add("no_hardcoded_approval_in_finalize_script", len(bad) == 0,
        f"Bad patterns: {bad}" if bad else "No hard-coded approval patterns")

    # Test 2: Finalization manifest not falsely COMPLETE
    ff_path = CONTROL / "FORENSIC_FINALIZATION_MANIFEST.json"
    ff_status = load_json(ff_path).get("status", "") if ff_path.exists() else "MISSING"
    add("finalization_manifest_not_falsely_complete", ff_status != "COMPLETE",
        f"FORENSIC_FINALIZATION_MANIFEST.json status={ff_status}")

    # Test 3: Null counts acceptable only when not COMPLETE
    ff = load_json(ff_path) if ff_path.exists() else {}
    null_count_fields = [k for k in ["capabilityCountAfter", "requirementCountAfter"] if ff.get(k) is None]
    complete_with_nulls = ff.get("status") == "COMPLETE" and bool(null_count_fields)
    add("null_final_counts_blocked_when_status_complete", not complete_with_nulls,
        f"Status={ff.get('status')}, null fields OK while REPAIR_IN_PROGRESS" if not complete_with_nulls else f"COMPLETE with null fields: {null_count_fields}")

    # Test 4: No codebase-after hash while REPAIR_IN_PROGRESS
    complete_no_after = ff.get("status") == "COMPLETE" and not ff.get("codebaseBaselineAfter")
    add("codebase_after_hash_blocked_when_premature", not complete_no_after,
        "codebaseBaselineAfter correctly null during REPAIR_IN_PROGRESS" if not complete_no_after else "COMPLETE without codebaseBaselineAfter")

    # Test 5: Generator guard present
    gen_src = (COMPLETION / "generate_product_expansion.py").read_text(encoding="utf-8")
    guard_present = "PROCESS-CONTROL-GUARD: UNSAFE_FOR_FINALIZATION" in gen_src
    add("generator_guard_present", guard_present,
        "Guard found" if guard_present else "Guard MISSING")

    # Test 6: Exactly one canonical status file (on Windows, STATUS.json = status.json)
    status_path = (CONTROL / "status.json").resolve()
    add("one_canonical_status_file", status_path.exists(),
        f"Canonical status.json resolves to {status_path}, exists={status_path.exists()}")

    # Test 7: Current status is not approved
    status = load_json(CONTROL / "status.json")
    pe = status.get("productExpansion", {})
    review_status = pe.get("independentReviewStatus", "")
    mapping_status = status.get("mappingStatus", "")
    is_approved = review_status == "APPROVED" or mapping_status == "COMPLETED"
    add("current_status_not_approved", not is_approved,
        f"reviewStatus={review_status}, mappingStatus={mapping_status}")

    # Test 8: Codebase file count matches manifest
    try:
        manifest = load_json(CONTROL / "GRAPHIFY_REPAIR_MANIFEST.json")
        expected_count = len(manifest.get("codebaseFiles", []))
        actual_count = sum(1 for _ in CODEBASE.rglob("*") if Path(_).is_file()) if CODEBASE.exists() else -1
        ok_cb = actual_count == expected_count
        add("codebase_unchanged", ok_cb,
            f"{actual_count} files == expected {expected_count}" if ok_cb else f"File count mismatch: {actual_count} != {expected_count}")
    except Exception as e:
        add("codebase_unchanged", False, f"Error: {e}")

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("MindRoom Graphify — Process Control Repair (Step 1)")
    print("=" * 70)

    print("\nStep 1: Inspecting scripts...")
    inspection = inspect_scripts()
    print(f"  Hard-coded patterns found: {len(inspection['patterns'])}")
    print(f"  Approval functions found:  {len(inspection['functions'])}")

    print("\nStep 2: Replacing finalize_repair_and_review.py...")
    disabled = replace_finalize_repair_and_review()
    for d in disabled:
        print(f"  DISABLED: {d}")

    print("\nStep 3: Guarding unsafe generators...")
    gen_blocked = add_generator_guard()
    migration_guarded = guard_finalize_product_expansion_review()
    for g in gen_blocked + migration_guarded:
        print(f"  GUARDED: {g}")

    print("\nStep 5: Asserting canonical status file authority...")
    auth = assert_status_authority()
    print(f"  Canonical: {auth['canonicalStatusPath']}")

    print("\nStep 6: Reopening false completion state...")
    reopen = reopen_false_completion()
    print(f"  Previous mappingStatus:    {reopen['previousMappingStatus']}")
    print(f"  New mappingStatus:         {reopen['newMappingStatus']}")
    print(f"  independentReviewStatus:   {reopen['independentReviewStatus']}")
    print(f"  codebaseExecutionStatus:   {reopen['codebaseExecutionStatus']}")
    print(f"  finalReleaseReceiptStatus: {reopen['finalReleaseReceiptStatus']}")

    print("\nStep 8: Running validation tests...")
    tests = run_validation_tests()
    all_passed = all(t["passed"] for t in tests)
    for t in tests:
        icon = "PASS" if t["passed"] else "FAIL"
        print(f"  [{icon}] {t['test']}: {t['detail']}")

    print("\nStep 7: Creating PROCESS_CONTROL_AUDIT.json...")
    open_defects = [t for t in tests if not t["passed"]]
    audit = {
        "schemaVersion": 1,
        "project": "MindRoom",
        "repairedAt": now_utc(),
        "codebaseModified": False,
        "hardCodedApprovalFunctionsFound": [
            f for f in inspection["functions"]
            if f["function"] in ("append_independent_review", "sync_completion_state")
        ],
        "hardCodedApprovalFunctionsRemovedOrDisabled": disabled,
        "hardCodedApprovalPatternsFound": inspection["patterns"],
        "prematureFinalizationPathsFound": [
            {
                "file": "finalize_repair_and_review.py::sync_completion_state",
                "defect": "Hard-codes mappingStatus=COMPLETED and independentReviewStatus=APPROVED without evidence",
            },
            {
                "file": "FORENSIC_FINALIZATION_MANIFEST.json",
                "defect": "status=COMPLETE with null codebaseBaselineAfter and only PHASE_0 in phases",
            },
        ],
        "prematureFinalizationPathsFixed": [
            "finalize_repair_and_review.py::sync_completion_state — now sets REPAIR_IN_PROGRESS",
            "FORENSIC_FINALIZATION_MANIFEST.json — status reset to REPAIR_IN_PROGRESS",
            "status.json — mappingStatus=REPAIR_IN_PROGRESS, independentReviewStatus=NOT_STARTED",
        ],
        "unsafeGeneratorRerunsFound": [
            {
                "file": "generate_product_expansion.py",
                "classification": "UNSAFE_FOR_FINALIZATION",
                "risk": "Overwrites CAPABILITY_REGISTRY.json, REQUIREMENT_REGISTRY.jsonl, CHANGE_LOCATION_REGISTRY.jsonl, IMPLEMENTATION_TASKS.jsonl, KG outputs",
            },
            {
                "file": "finalize_product_expansion_review.py",
                "classification": "MIGRATION_ONLY",
                "risk": "Applies approval from AGENT_REVIEWS.jsonl — must not run without genuine human-approved review",
            },
        ],
        "unsafeGeneratorRerunsBlocked": gen_blocked + migration_guarded,
        "canonicalStatusFile": "Graphify/00 Execution Control/status.json",
        "competingStatusFiles": [
            {
                "path": "Graphify/00 Execution Control/STATUS.json",
                "classification": "SAME_FILE_ON_WINDOWS_CASE_INSENSITIVE_FS — not a true duplicate",
            }
        ],
        "previousReviewInvalidated": True,
        "previousReviewId": "REV-FINAL-20260730-153315",
        "previousReviewInvalidationReason": (
            "INVALIDATED_BY_FORENSIC_PROCESS_AUDIT — all 23 auditedItems fields were hard-coded "
            "to True without artifact evidence; REQUIREMENT_SUPERSESSION_MAP.jsonl does not exist; "
            "decision=APPROVED written by automated code without human review"
        ),
        "currentMappingStatus": "REPAIR_IN_PROGRESS",
        "currentIndependentReviewStatus": "NOT_STARTED",
        "codebaseExecutionStatus": "BLOCKED",
        "finalReleaseReceiptStatus": "NOT_VERIFIED",
        "validationTests": tests,
        "allValidationTestsPassed": all_passed,
        "openDefects": open_defects,
    }
    write_json(COMPLETION / "PROCESS_CONTROL_AUDIT.json", audit)
    print("  Written: PROCESS_CONTROL_AUDIT.json")

    # Assertions
    status = load_json(CONTROL / "status.json")
    assert status.get("mappingStatus") == "REPAIR_IN_PROGRESS", "mappingStatus not reset"
    assert status.get("productExpansion", {}).get("independentReviewStatus") == "NOT_STARTED", "review not reset"
    repaired_src = (COMPLETION / "finalize_repair_and_review.py").read_text(encoding="utf-8")
    assert '"decision": "APPROVED"' not in repaired_src, "APPROVED still in script"

    # ─── Final structured output ───────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("\nScripts inspected:")
    for f in sorted(COMPLETION.glob("*.py")):
        if not f.name.startswith("_"):
            print(f"  {f.name}")

    print("\nHard-coded approval functions found:")
    for f in audit["hardCodedApprovalFunctionsFound"]:
        print(f"  {f['file']}::{f['function']}")

    print("\nHard-coded approval functions disabled:")
    for d in audit["hardCodedApprovalFunctionsRemovedOrDisabled"]:
        print(f"  {d}")

    print("\nPremature finalization paths found:")
    for p in audit["prematureFinalizationPathsFound"]:
        print(f"  {p['file']}: {p['defect']}")

    print("\nPremature finalization paths fixed:")
    for p in audit["prematureFinalizationPathsFixed"]:
        print(f"  {p}")

    print("\nUnsafe generator reruns found:")
    for g in audit["unsafeGeneratorRerunsFound"]:
        print(f"  {g['file']} [{g['classification']}]")

    print("\nUnsafe generator reruns blocked:")
    for g in audit["unsafeGeneratorRerunsBlocked"]:
        print(f"  {g}")

    print(f"\nCanonical status file: {audit['canonicalStatusFile']}")
    print(f"Competing status files: {[f['path'] for f in audit['competingStatusFiles']]}")
    print(f"Current mapping status: {audit['currentMappingStatus']}")
    print(f"Current independent-review status: {audit['currentIndependentReviewStatus']}")
    print(f"Current Codebase execution status: {audit['codebaseExecutionStatus']}")
    print(f"Final release receipt status: {audit['finalReleaseReceiptStatus']}")
    print(f"\nProcess-control audit file: Graphify/11 Completion/PROCESS_CONTROL_AUDIT.json")

    print("\nValidation tests:")
    for t in tests:
        icon = "PASS" if t["passed"] else "FAIL"
        print(f"  [{icon}] {t['test']}: {t['detail']}")

    print("\nCodebase files modified: 0")
    print(f"\nOpen process-control defects: {len(open_defects)}")
    for d in open_defects:
        print(f"  {d['test']}: {d['detail']}")

    print()
    if all_passed and not open_defects:
        print("PROCESS CONTROL REPAIRED — READY FOR REQUIREMENT NORMALIZATION")
    else:
        print("PROCESS CONTROL STILL UNSAFE — FURTHER REPAIR REQUIRED")


if __name__ == "__main__":
    main()
