# Investigation Report: MR-INV-009

## Investigation ID

MR-INV-009

## Question

What exact Wave 0 micro-batch order and reversible checkpoints satisfy the frozen dependency graph without mixing independent implementation tasks?

## Why it matters

The bootstrap is audited as a prerequisite to every Wave 0 task, while Electron and page-mode tasks have additional same-wave dependencies; rollback must preserve the frozen Codebase baseline and user data.

## Frozen-plan references

- Graphify/00 Execution Control/DEPENDENCY_WAVE_BASELINE.json
- Graphify/05 Dependency and Impact/SAME_WAVE_EXECUTION_ORDER.json
- Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
- Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl
- Graphify/11 Completion/TASK_EXECUTION_DEPENDENCY_AUDIT.jsonl

## Repository evidence examined

- `IMPLEMENTATION_TASKS.jsonl` provides a canonical Wave 0 dependency graph:
  - `MR-IMPL-BOOTSTRAP-001`: no dependencies, no prerequisites.
  - `MR-IMPL-001`: depends on bootstrap.
  - `MR-IMPL-002`: depends on `MR-IMPL-001` and bootstrap.
  - `MR-IMPL-003`: depends on `MR-IMPL-001` and bootstrap.
  - `MR-IMPL-004`: depends on `MR-IMPL-001` and `MR-IMPL-002`.
  - `MR-IMPL-005`: depends on bootstrap.
  - `MR-IMPL-006`: depends on `MR-IMPL-005`.
- `DEPENDENCY_WAVE_BASELINE.json` reports no task cycles, no capability cycles, no backward-wave dependencies, and no unknown dependencies.
- `TASK_EXECUTION_DEPENDENCY_AUDIT.jsonl` confirms the Wave 0 edges above are valid.
- `ROLLBACK_PLAN.jsonl` provides rollback contracts for `MR-CAP-001` through `MR-CAP-006`.
- `BATCH_EXECUTION_PLAN.md` is classified `CURRENT_AUTHORITATIVE`, but its `## WAVE_0` section lists product-expansion capabilities `MR-CAP-132`, `MR-CAP-134`, `MR-CAP-140`, `MR-CAP-158`, `MR-CAP-160`, and `MR-CAP-161` instead of the canonical Wave 0 tasks/capabilities.

## External primary sources examined

None were required. This is an internal frozen-plan consistency investigation.

## Tests/commands performed

Read-only repository inspection:

- `git status --short`
- `git fetch origin --prune`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- Parsed Wave 0 implementation tasks, dependency baseline, same-wave order, batch plan, rollback plan, and dependency audit.

No Codebase files were modified.

## Findings

1. **A deterministic canonical topological order can be derived.**

   Classification: `PROVEN_FROM_REPOSITORY`

   A valid order is:

   1. `MR-IMPL-BOOTSTRAP-001`
   2. `MR-IMPL-001`
   3. `MR-IMPL-002`
   4. `MR-IMPL-003`
   5. `MR-IMPL-005`
   6. `MR-IMPL-004`
   7. `MR-IMPL-006`

   `MR-IMPL-002`, `MR-IMPL-003`, and `MR-IMPL-005` are parallel-safe after their prerequisites; `MR-IMPL-004` must follow `MR-IMPL-002`; `MR-IMPL-006` must follow `MR-IMPL-005`.

2. **Task-level rollback checkpoints exist.**

   Classification: `PROVEN_FROM_REPOSITORY`

   Wave 0 tasks declare rollback actions, rollback contracts, verification receipts, and hash-manifest checkpoint types. `ROLLBACK_PLAN.jsonl` also records rollback contracts for `MR-CAP-001` through `MR-CAP-006`.

3. **A frozen-plan contradiction exists in the batch-execution artifact.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md` is current authoritative, but its `WAVE_0` section lists `MR-CAP-132`, `MR-CAP-134`, `MR-CAP-140`, `MR-CAP-158`, `MR-CAP-160`, and `MR-CAP-161`. This conflicts with the canonical Wave 0 task set and release gate, which list `MR-CAP-001` through `MR-CAP-006` and `MR-IMPL-BOOTSTRAP-001` through `MR-IMPL-006`.

4. **The contradiction is substantive for pre-code execution.**

   Classification: `INFERENCE`

   An authorized Wave 0 executor could read `BATCH_EXECUTION_PLAN.md` and follow a different Wave 0 batch list from the canonical implementation queue and release gate. That is not a safe pre-code boundary.

## Rejected alternatives

- Marking MR-INV-009 complete was rejected because the current authoritative batch plan contradicts the canonical Wave 0 ordering.
- Silently repairing `BATCH_EXECUTION_PLAN.md` was rejected because this investigation loop must not modify frozen Graphify authority without change control.
- Treating the contradiction as irrelevant was rejected because MR-INV-009 explicitly depends on `BATCH_EXECUTION_PLAN.md` and requires no same-wave ordering artifact to contradict the canonical dependency audit.

## Decision

MR-INV-009 is BLOCKED. Frozen-plan change control is required to reconcile `BATCH_EXECUTION_PLAN.md` with the canonical Wave 0 implementation queue and release gate before Codebase execution.

## Hard blockers

- `MR-BLOCK-004`: `BATCH_EXECUTION_PLAN.md` lists noncanonical product-expansion capabilities under `WAVE_0`.

## Soft risks

None additional. The dependency graph itself is otherwise consistent.

## Implementation consequences

No Wave 0 implementation may begin while this contradiction remains.

## What must happen in Wave 0

First, frozen-plan change control must make the Wave 0 batch plan agree with the canonical Wave 0 tasks/capabilities. After that, the derived topological order and rollback checkpoints can be used.

## Acceptance criteria results

1. A deterministic topological order exists for all seven Wave 0 tasks: **PASS**.
2. Parallel-safe and strictly sequential task boundaries are identified: **PASS**.
3. Each micro-batch has scoped pre/post hashes, tests, receipts, and rollback actions: **PASS**.
4. No same-wave ordering artifact contradicts the canonical task dependency audit: **FAIL**.

## Final status

BLOCKED
