"""Create the immutable product-expansion baseline and preservation inventory.

This Graphify-only tool reads Codebase and the three original Master Plans.  It
never writes to Codebase or to a Master Plan.  Its outputs are the evidence
required before the additive product-expansion sections may be appended.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_ID = "mindroom-product-expansion-20260729-155104"
HERE = Path(__file__).resolve().parent
GRAPHIFY = HERE.parent
PROJECT = GRAPHIFY.parent
CODEBASE = PROJECT / "Codebase"
CONTROL = GRAPHIFY / "00 Execution Control"
PLANS = GRAPHIFY / "Master Plan"
SNAPSHOTS = GRAPHIFY / "15 Processed Plan Snapshots"
MANIFEST_PATH = CONTROL / "PRODUCT_EXPANSION_MANIFEST.json"
BASELINE_PATH = CONTROL / "PRODUCT_EXPANSION_BASELINE.json"
INVENTORY_PATH = SNAPSHOTS / "ORIGINAL_MASTER_PLAN_PRESERVATION_INVENTORY.json"

PLAN_NAMES = (
    "01-EVERYTHING-WE-ARE-KEEPING.md",
    "02-EVERYTHING-WE-ARE-DELETING.md",
    "03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md",
)

DECISION_TOKENS = ("KEEP", "ADAPT", "REMOVE", "ADD", "CONDITIONAL")
SAFETY_RE = re.compile(
    r"\b(?:MANDATORY|FORBIDDEN|MUST|MUST NOT|NEVER|DO NOT|CANNOT|ONLY|"
    r"REQUIRES EVIDENCE|EVIDENCE|SAFETY|PRESERVE|PRESERVATION|INTERLOCK|"
    r"NO|NO DESTRUCTIVE|NO USER-DATA)\b",
    re.IGNORECASE,
)
GATE_RE = re.compile(
    r"\b(?:GATE|VERIF|TEST|PROOF|RECEIPT|REVIEW|QA|FIXTURE|COMPLETE|"
    r"PASS|FAIL|RELEASE|COMPLETION|TYPECHECK|LINT|BUILD|PACKAG)\w*",
    re.IGNORECASE,
)
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
DIRECT_DECISION_RE = re.compile(r"\b(KEEP|ADAPT|REMOVE|ADD|CONDITIONAL)\b", re.IGNORECASE)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def graphify_rel(path: Path) -> str:
    return "Graphify/" + path.resolve().relative_to(GRAPHIFY.resolve()).as_posix()


def atomic_write_json(path: Path, value: Any) -> None:
    resolved = path.resolve()
    if GRAPHIFY.resolve() not in resolved.parents:
        raise RuntimeError(f"Refusing non-Graphify write: {resolved}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def codebase_files() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(item for item in CODEBASE.rglob("*") if item.is_file()):
        rows.append(
            {
                "path": "Codebase/" + path.relative_to(CODEBASE).as_posix(),
                "sizeBytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def codebase_directories() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [{"path": "Codebase/"}]
    for path in sorted(item for item in CODEBASE.rglob("*") if item.is_dir()):
        rows.append({"path": "Codebase/" + path.relative_to(CODEBASE).as_posix() + "/"})
    return rows


def file_tree_digest(rows: list[dict[str, Any]]) -> str:
    canonical = "".join(
        f"{row['path']}\0{row['sizeBytes']}\0{row['sha256']}\n" for row in rows
    )
    return sha256_bytes(canonical.encode("utf-8"))


def directory_tree_digest(rows: list[dict[str, Any]]) -> str:
    canonical = "".join(f"{row['path']}\n" for row in rows)
    return sha256_bytes(canonical.encode("utf-8"))


def heading_stack_text(stack: list[tuple[int, str]]) -> str:
    return " > ".join(text for _, text in stack)


def inventory_plan(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    relative = graphify_rel(path)
    headings: list[dict[str, Any]] = []
    statements: list[dict[str, Any]] = []
    capabilities: list[dict[str, Any]] = []
    safety_rules: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    raw_lines: list[dict[str, Any]] = []
    stack: list[tuple[int, str]] = []
    contextual_decision: str | None = None

    for number, line in enumerate(lines, 1):
        raw_lines.append(
            {
                "lineNumber": number,
                "text": line,
                "sha256": sha256_bytes(line.encode("utf-8")),
            }
        )
        stripped = line.strip()
        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            contextual_decision = None
            headings.append(
                {
                    "inventoryId": f"MR-ORIG-H-{path.stem}-{number:04d}",
                    "path": relative,
                    "lineNumber": number,
                    "level": level,
                    "text": line,
                    "headingPath": heading_stack_text(stack),
                }
            )

        lower = stripped.lower().rstrip(":")
        if lower in {"keep", "retain", "add", "remove", "change", "adapt", "allow"}:
            contextual_decision = {
                "keep": "KEEP",
                "retain": "KEEP",
                "add": "ADD",
                "remove": "REMOVE",
                "change": "ADAPT",
                "adapt": "ADAPT",
                "allow": "CONDITIONAL",
            }[lower]
        elif stripped == "---":
            contextual_decision = None

        if not stripped or stripped in {"```", "---"}:
            continue

        context = heading_stack_text(stack)
        statement = {
            "inventoryId": f"MR-ORIG-R-{path.stem}-{number:04d}",
            "path": relative,
            "lineNumber": number,
            "text": line,
            "headingPath": context,
            "classification": "ORIGINAL_SEMANTIC_STATEMENT",
        }
        statements.append(statement)

        is_list_item = bool(LIST_RE.match(line))
        scope_context = bool(
            re.search(
                r"\b(?:scope|retain|keeping|deleting|addition|capabilit|product|"
                r"workspace|page|canvas|mind map|database|kanban|search|graph|"
                r"pdf|office|word|powerpoint|excel|csv|photo|video|file)\b",
                context,
                re.IGNORECASE,
            )
        )
        if is_list_item and scope_context:
            capabilities.append(
                {
                    **statement,
                    "inventoryId": f"MR-ORIG-C-{path.stem}-{number:04d}",
                    "classification": "ORIGINAL_CAPABILITY_OR_PRODUCT_FUNCTION",
                }
            )

        if SAFETY_RE.search(stripped):
            safety_rules.append(
                {
                    **statement,
                    "inventoryId": f"MR-ORIG-S-{path.stem}-{number:04d}",
                    "classification": "ORIGINAL_MANDATORY_SAFETY_OR_SCOPE_RULE",
                }
            )

        if GATE_RE.search(stripped) or re.search(
            r"\b(?:verification|testing|release|proof|receipt|review|completion|qa)\b",
            context,
            re.IGNORECASE,
        ):
            gates.append(
                {
                    **statement,
                    "inventoryId": f"MR-ORIG-G-{path.stem}-{number:04d}",
                    "classification": "ORIGINAL_RELEASE_OR_VERIFICATION_GATE",
                }
            )

        direct_decisions = {match.upper() for match in DIRECT_DECISION_RE.findall(stripped)}
        if contextual_decision and is_list_item:
            direct_decisions.add(contextual_decision)
        for decision in sorted(direct_decisions):
            if decision in DECISION_TOKENS:
                decisions.append(
                    {
                        **statement,
                        "inventoryId": f"MR-ORIG-D-{path.stem}-{number:04d}-{decision}",
                        "decision": decision,
                        "classification": "ORIGINAL_EXPLICIT_DECISION",
                    }
                )

    return {
        "path": relative,
        "bytes": len(raw),
        "lineCount": len(lines),
        "endsWithLf": raw.endswith(b"\n"),
        "sha256": sha256_bytes(raw),
        "rawLines": raw_lines,
        "headings": headings,
        "requirements": statements,
        "capabilitiesAndProductFunctions": capabilities,
        "mandatorySafetyRules": safety_rules,
        "releaseAndVerificationGates": gates,
        "explicitDecisions": decisions,
        "counts": {
            "rawLines": len(raw_lines),
            "headings": len(headings),
            "requirements": len(statements),
            "capabilitiesAndProductFunctions": len(capabilities),
            "mandatorySafetyRules": len(safety_rules),
            "releaseAndVerificationGates": len(gates),
            "explicitDecisions": len(decisions),
        },
    }


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest["runId"] != RUN_ID:
        raise RuntimeError("Run ID mismatch in product-expansion manifest")
    if manifest["mutationInterlocks"]["masterPlanMutationAuthorized"]:
        raise RuntimeError("Baseline tool must run before Master Plan mutation authorization")

    file_rows = codebase_files()
    directory_rows = codebase_directories()
    plans = [inventory_plan(PLANS / name) for name in PLAN_NAMES]
    created_at = now_utc()

    baseline = {
        "schemaVersion": 1,
        "artifactRole": "IMMUTABLE_PRE_MUTATION_BASELINE",
        "project": "MindRoom",
        "runId": RUN_ID,
        "createdAt": created_at,
        "authority": "AUTHORITATIVE",
        "codebase": {
            "root": "Codebase/",
            "fileCount": len(file_rows),
            "directoryCount": len(directory_rows),
            "fileTreeSha256": file_tree_digest(file_rows),
            "directoryTreeSha256": directory_tree_digest(directory_rows),
            "files": file_rows,
            "directories": directory_rows,
        },
        "originalMasterPlans": [
            {
                "path": plan["path"],
                "bytes": plan["bytes"],
                "lineCount": plan["lineCount"],
                "sha256": plan["sha256"],
            }
            for plan in plans
        ],
        "interlocks": {
            "codebaseMustRemainByteIdentical": True,
            "codebaseFileSetMustRemainIdentical": True,
            "codebaseDirectorySetMustRemainIdentical": True,
            "masterPlansMayOnlyReceiveAdditiveOrCorrectivePreservingChanges": True,
            "historicalEvidenceMustBePreserved": True,
        },
    }
    atomic_write_json(BASELINE_PATH, baseline)

    inventory = {
        "schemaVersion": 1,
        "artifactRole": "ORIGINAL_MASTER_PLAN_PRESERVATION_INVENTORY",
        "project": "MindRoom",
        "runId": RUN_ID,
        "createdAt": created_at,
        "authority": "AUTHORITATIVE_PRE_EDIT_EVIDENCE",
        "method": {
            "requirements": "Every nonblank, non-fence, non-separator semantic source line is inventoried as an original requirement/context statement; this deliberately over-includes rather than risking omission.",
            "capabilitiesAndProductFunctions": "Every list item in a product/capability/scope context is inventoried.",
            "mandatorySafetyRules": "Every semantic line containing mandatory, forbidden, must, never, do-not, only, evidence, safety, or preservation language is inventoried.",
            "releaseAndVerificationGates": "Every line matching gate, verification, test, proof, receipt, review, QA, fixture, completion, build, packaging, or release semantics is inventoried.",
            "explicitDecisions": "Direct KEEP, ADAPT, REMOVE, ADD, or CONDITIONAL tokens and list items governed by explicit decision labels are inventoried.",
            "rawCoverage": "Every original source line, including blank lines and examples, is retained with line number and SHA-256.",
        },
        "plans": plans,
        "totals": {
            key: sum(plan["counts"][key] for plan in plans)
            for key in (
                "rawLines",
                "headings",
                "requirements",
                "capabilitiesAndProductFunctions",
                "mandatorySafetyRules",
                "releaseAndVerificationGates",
                "explicitDecisions",
            )
        },
        "preservationAssertions": {
            "allOriginalLinesRepresented": True,
            "allOriginalHeadingsRepresented": True,
            "allOriginalSemanticStatementsRepresented": True,
            "originalPlanHashesBound": True,
            "masterPlansModifiedByThisTool": False,
        },
    }
    atomic_write_json(INVENTORY_PATH, inventory)

    baseline_hash = sha256_file(BASELINE_PATH)
    inventory_hash = sha256_file(INVENTORY_PATH)
    manifest["status"] = "PRESERVATION_INVENTORY_READY_FOR_REVIEW"
    manifest["baseline"] = {
        "path": graphify_rel(BASELINE_PATH),
        "sha256": baseline_hash,
        "codebaseFileCount": len(file_rows),
        "codebaseDirectoryCount": len(directory_rows),
        "codebaseFileTreeSha256": baseline["codebase"]["fileTreeSha256"],
        "codebaseDirectoryTreeSha256": baseline["codebase"]["directoryTreeSha256"],
    }
    pre_edit = manifest["preservationGuardrail"]["requiredPreEditInventory"]
    pre_edit["complete"] = True
    pre_edit["sha256"] = inventory_hash
    pre_edit["counts"] = inventory["totals"]
    manifest["mutationInterlocks"]["masterPlanMutationAuthorized"] = False
    manifest["independentReviewer"]["currentDecision"] = "PRE_EDIT_INVENTORY_REVIEW_REQUIRED"
    manifest["lastUpdatedAt"] = created_at
    atomic_write_json(MANIFEST_PATH, manifest)

    print(
        json.dumps(
            {
                "runId": RUN_ID,
                "baselinePath": graphify_rel(BASELINE_PATH),
                "baselineSha256": baseline_hash,
                "inventoryPath": graphify_rel(INVENTORY_PATH),
                "inventorySha256": inventory_hash,
                "codebaseFileCount": len(file_rows),
                "codebaseDirectoryCount": len(directory_rows),
                "codebaseFileTreeSha256": baseline["codebase"]["fileTreeSha256"],
                "codebaseDirectoryTreeSha256": baseline["codebase"]["directoryTreeSha256"],
                "inventoryCounts": inventory["totals"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
