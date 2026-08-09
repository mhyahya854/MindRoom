# MR-INV-001 — Shared package bootstrap boundary and ownership

## Investigation ID

`MR-INV-001`

## Question

Can `@mindroom/common` be bootstrapped at the frozen target with a coherent workspace boundary, build contract, and unambiguous capability ownership before any Codebase mutation?

## Why it matters

The frozen dependency audit makes `MR-IMPL-BOOTSTRAP-001` a prerequisite of every Wave 0 primary task and the wider implementation graph. A wrong workspace boundary would break package resolution; a wrong capability owner would make task, test, review, and gate receipts non-authoritative.

## Frozen-plan references

- `Graphify/00 Execution Control/PACKAGE_BOUNDARY_BASELINE.json`
- `Graphify/03 Capability Map/CAPABILITY_REGISTRY.json`
- `Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl`
- `Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md`
- `Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl`
- `Graphify/10 Verification/RELEASE_GATE_MATRIX.json`
- `Graphify/11 Completion/TASK_EXECUTION_DEPENDENCY_AUDIT.jsonl`
- `Graphify/12 Source Documents/AFFINE_PROVENANCE.md`

## Repository evidence examined

- The active root manifest uses Yarn `4.13.0`, declares Node `>=22.12.0 <23.0.0`, and includes workspace glob `packages/*/*`.
- `Codebase/.yarnrc.yml` pins the tracked `.yarn/releases/yarn-4.13.0.cjs` binary.
- `Codebase/.nvmrc` pins Node `22.23.1`.
- `Codebase/packages/common/mindroom` does not exist and no `@mindroom/common` package-name collision was found.
- Existing `packages/common/*` TypeScript packages use ESM, direct typed source exports, `tsconfig.web.json`, isolated `src`, and generated project references.
- `Codebase/tools/cli/src/init.ts` derives root and package TypeScript references from Yarn workspace discovery.
- The pinned AFFiNE `0.26.3` reference at commit `da7781a75171140fd966c6cfbe05da9f1fb111d6` uses the same `packages/*/*` workspace glob, Node engine range, and Yarn version.
- `TEST-MR-BOOTSTRAP-001` requires `yarn workspace @mindroom/common build`, zero package cycles, and zero `@affine/core` dependencies.

## External primary sources examined

None. The relevant upstream fact is preserved inside the frozen repository as the pinned official AFFiNE archive and provenance record; no changing external fact was used to close this investigation.

## Tests and commands performed

- Verified clean local/remote alignment with `git status`, `git fetch origin`, `git rev-parse`, and `git ls-remote`.
- Verified `git diff -- Codebase` and `git status --short -- Codebase` were empty.
- Executed the tracked Yarn `4.13.0` binary read-only with `workspaces list --json`; it discovered the existing `packages/common/*` packages through the frozen workspace topology.
- Compared active and pinned-reference root manifest fields read-only.
- Parsed the canonical task, capability, test, release-gate, and dependency audit artifacts.
- Observed the default shell runtime as Node `v24.18.0`; both Codex's bundled Node and the system Node are outside the repository engine range. This is deferred to `MR-INV-006` and is not used to reinterpret the frozen task.

## Findings

1. **PROVEN_FROM_REPOSITORY — workspace placement is feasible.** `packages/*/*` already includes `packages/common/mindroom`, so the new package does not require a root workspace-pattern change.
2. **EMPIRICALLY_VERIFIED_READ_ONLY — the pinned Yarn CLI is present and workspace discovery works.** Yarn `4.13.0` listed the active common packages without modifying Codebase.
3. **PROVEN_FROM_REPOSITORY — no name/path collision exists.** Neither the active Codebase nor the pinned AFFiNE reference contains `@mindroom/common` or `packages/common/mindroom`.
4. **PROVEN_FROM_REPOSITORY — isolation is implementable.** Existing common-package conventions support an ESM package with typed source exports and a dependency-free initial manifest. `TEST-MR-BOOTSTRAP-001` explicitly rejects `@affine/core` dependencies and cycles.
5. **PROVEN_FROM_REPOSITORY — bootstrap ownership is contradictory.** In `IMPLEMENTATION_TASKS.jsonl:1`, `MR-IMPL-BOOTSTRAP-001.capabilityId` and `contract.capabilityId` are `MR-CAP-160`, while its `capabilityIds` field is `MR-CAP-001`. `IMPLEMENTATION_QUEUE.md:9` also labels the bootstrap as `MR-CAP-160`.
6. **PROVEN_FROM_REPOSITORY — MR-CAP-160 already has a different primary task.** `IMPLEMENTATION_TASKS.jsonl:161` assigns `MR-IMPL-160` to `MR-CAP-160` for Stable Identity Across File Movement, with its own Wave 1 tests.
7. **PROVEN_FROM_REPOSITORY — the bootstrap test belongs to MR-CAP-001.** `REQUIREMENT_TEST_MATRIX.jsonl:338` assigns `TEST-MR-BOOTSTRAP-001` to `MR-CAP-001`, and the `MR-CAP-001` contract includes that test.
8. **PROVEN_FROM_REPOSITORY — the ambiguity is foundational.** The frozen task dependency audit records the bootstrap as a prerequisite for all six primary Wave 0 tasks and many later tasks.
9. **UNRESOLVED — there is no authoritative rule allowing the investigation to choose between the singular task/contract/queue owner and the plural task/test/capability-contract owner.** Choosing would be a frozen-plan edit by interpretation.
10. **EMPIRICALLY_VERIFIED_READ_ONLY — the frozen Graphify certification is currently invalid.** `FINAL_FREEZE_CERTIFICATION` failed `BAK-01`, `BAK-02`, `BAK-03`, `BAK-10`, and `BAK-11`. The active immutable backup path recorded in the receipt does not exist, the receipt reports 13,446 source/backup files while the live scan finds 13,447 source files and zero backup files, and the current aggregates do not reproduce the receipt.
11. **EMPIRICALLY_VERIFIED_READ_ONLY — Step 11b fails.** The verifier exits 1 with: `Verified active backup receipt is not the exact canonical post-Phase-9 state.`

## Rejected alternatives

- **Silently treat MR-CAP-001 as authoritative.** Rejected because the canonical task contract and queue explicitly say MR-CAP-160.
- **Silently treat MR-CAP-160 as authoritative.** Rejected because MR-CAP-160 already has primary task MR-IMPL-160 and the bootstrap test is assigned to MR-CAP-001.
- **Proceed because validators previously passed.** Rejected because structural validator success does not reconcile the contradictory semantic ownership needed for future receipts.
- **Repair Graphify during investigation.** Rejected because the frozen plan requires explicit change control.

## Decision

`FROZEN_PLAN_CHANGE_CONTROL_REQUIRED`

The physical package boundary is feasible, but `MR-IMPL-BOOTSTRAP-001` cannot be executed authoritatively until its capability ownership is reconciled consistently across the frozen task record, contract, queue, capability acceptance tests, dependency/ownership derivatives, and validators. Separately, frozen-plan recovery/change control must restore a certifiable immutable backup state and return both mandatory validators to PASS.

## Hard blockers

- `MR-BLOCK-001` — contradictory frozen capability ownership for the foundational bootstrap task.
- `MR-BLOCK-002` — frozen final-certification and Step 11b failure caused by absent active backup and live filesystem drift relative to the protected receipt.

## Frozen-plan verification after evidence

- `validate_final_graphify_freeze.py --mode FINAL_FREEZE_CERTIFICATION --verify-only`: **FAIL**
- Failed checks: `BAK-01`, `BAK-02`, `BAK-03`, `BAK-10`, `BAK-11`
- `verify_step11b_results.py --verify-only`: **FAIL**
- Step 11b reason: `Verified active backup receipt is not the exact canonical post-Phase-9 state.`
- Graphify Git diff/status: clean
- Graphify filesystem authority: not certifiable against the frozen backup receipt

## Soft risks

- The current default Node is `v24.18.0`, while the repository requires Node `>=22.12.0 <23.0.0` and pins `22.23.1`. `MR-INV-006` must establish the supported runtime before any Wave 0 command is executed.

## Implementation consequences

- Do not create `Codebase/packages/common/mindroom`.
- Do not run the bootstrap build acceptance test against a speculative package.
- Do not assign bootstrap receipts to either capability by interpretation.
- All Codebase work remains blocked pending frozen-plan change control and separate explicit Wave 0 authorization.

## What must happen in Wave 0

Nothing yet. Before Wave 0 can start, change control must reconcile bootstrap ownership, restore a valid immutable backup/certification state, and return both mandatory verifiers to PASS. After that and only after explicit Wave 0 authorization, the bootstrap micro-batch may create the isolated workspace package, run the pinned Node/Yarn toolchain, verify build/resolution/cycle constraints, and publish the required receipt.

## Acceptance criteria results

| Criterion | Result | Evidence classification |
|---|---|---|
| Workspace topology discovers the planned path without a root pattern change | PASS | PROVEN_FROM_REPOSITORY |
| Active and pinned reference agree on relevant topology/tool versions | PASS | PROVEN_FROM_REPOSITORY |
| Planned path and package name have no collision | PASS | PROVEN_FROM_REPOSITORY |
| Package can be isolated from renderer/core dependencies | PASS TO PRE-CODE LIMIT | PROVEN_FROM_REPOSITORY |
| Frozen ownership and receipt scope identify one coherent capability | FAIL | PROVEN_FROM_REPOSITORY |
| Codebase remains untouched | PASS | EMPIRICALLY_VERIFIED_READ_ONLY |

## Final status

`BLOCKED`

`frozenPlanContradiction = true`

`codebaseChangeRequiredNext = false`
