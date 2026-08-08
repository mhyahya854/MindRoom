"""Finalize MindRoom Graphify Repair — evidence-based replacement.

PROCESS-CONTROL-REPAIRED 2026-07-30T18:02:52.475Z
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
