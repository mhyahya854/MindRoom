# Investigation Report: MR-INV-005

## Investigation ID

MR-INV-005

## Question

Can Wave 0 satisfy its no-cloud, no-telemetry, offline-capable invariants while local-only network enforcement is scheduled in Wave 1?

## Why it matters

The active AFFiNE-derived shell contains cloud-adjacent systems, while every Wave 0 contract asserts local-only behavior. If Wave 0 gate completion implicitly required final network enforcement, the plan would be self-contradictory and Wave 0 could not start.

## Frozen-plan references

- Graphify/02 Architecture Map/NETWORK_BOUNDARY_MAP.jsonl
- Graphify/05 Dependency and Impact/EXCLUDED_SYSTEM_BOUNDARY_MAP.jsonl
- Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
- Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
- Graphify/10 Verification/OFFLINE_TEST_PLAN.md
- Graphify/10 Verification/RELEASE_GATE_MATRIX.json
- Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
- Graphify/11 Completion/FINAL_TEST_WAVE_OWNERSHIP.jsonl

## Repository evidence examined

- `NETWORK_BOUNDARY_MAP.jsonl` contains 24 classified network boundary entries:
  - 19 `EXCLUDE_LATER`
  - 3 `PRESERVE_REVIEW`
  - 1 `PRESERVE_ADAPT`
  - 1 `MIXED`
- `IMPLEMENTATION_QUEUE.md` places all seven Wave 0 tasks under `WAVE_0` and explicitly places `MR-IMPL-099` (`Local-only network enforcement`) under `WAVE_1`.
- `IMPLEMENTATION_TASKS.jsonl` confirms:
  - Wave 0 tasks `MR-IMPL-BOOTSTRAP-001` and `MR-IMPL-001` through `MR-IMPL-006` have `releaseWave: WAVE_0`.
  - `MR-IMPL-099` has `releaseWave: WAVE_1`.
  - Wave 0 tasks are preservation/verification tasks, not removal or network-enforcement tasks.
- `RELEASE_GATE_MATRIX.json`:
  - `GATE-WAVE_0.requiredTaskIds` contains exactly the seven Wave 0 task IDs and does not contain `MR-IMPL-099`.
  - `GATE-MR-CAP-099.releaseWave` is `WAVE_1`.
  - `GATE-WAVE_0.passCriteria` requires that tasks remain unauthorized until the wave starts, mapped tests pass, and Codebase execution requires explicit user authorization. It does not assert that all network code has already been removed.
- `REQUIREMENT_TEST_MATRIX.jsonl`:
  - Wave 0 tests are `offlineRequired: true`.
  - Their integration steps are scoped local write, process restart, and local-storage load operations.
  - Their failure conditions include attempted outbound network fetch, but only within those scoped offline tests.
  - `TEST-MR-CAP-099-*` are owned by `WAVE_1`, not `GATE-WAVE_0`.
- `OFFLINE_TEST_PLAN.md` states the final product rule: documents, canvas, mindmaps, calendar, finance, explicit links, backlinks, and search operate 100% offline, optional external adapters must not block local editing, and local embeddings execute in local background workers.
- Codebase read-only inspection:
  - `Codebase/packages/frontend/core/src/bootstrap/browser.ts` imports `./telemetry`.
  - `Codebase/packages/frontend/core/src/bootstrap/electron.ts` imports `./telemetry`.
  - `Codebase/packages/frontend/core/src/modules/telemetry/index.ts` imports from `../cloud`.
  - `Codebase/packages/common/nbstore/src/telemetry/manager.ts` contains HTTP and Socket.IO telemetry send paths.
  - `Codebase/packages/frontend/core/src/modules/cloud/index.ts` registers cloud services including auth, GraphQL, EventSource, and realtime services.
  - These are the cloud/telemetry paths that the frozen plan classifies as `EXCLUDE_LATER` and does not modify in Wave 0.

## External primary sources examined

None were required for this sequencing investigation. The conclusion is derived from the frozen MindRoom repository and the preserved Codebase, both of which are authoritative for the pre-code decision.

## Tests/commands performed

Read-only repository inspection:

- `git status --short`
- `git fetch origin --prune`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- Parsed the JSON/JSONL planning artifacts with PowerShell.
- Ran `rg` over selected Codebase files to confirm the boot-time and cloud-service network paths.

No Codebase files were modified.

## Findings

1. **Wave 0 is a retained-foundation preservation wave, not an offline-enforcement wave.**

   Classification: `PROVEN_FROM_REPOSITORY`

   The implementation queue and task contracts show that Wave 0 preserves/verifies the existing architecture, Electron main, renderer, preload, BlockSuite, and page-mode foundations. It does not schedule `MR-IMPL-099` or any cloud/telemetry removal task.

2. **Local-only network enforcement is explicitly a Wave 1 task and is excluded from GATE-WAVE_0.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `MR-IMPL-099` is `releaseWave: WAVE_1`, its capability gate is `WAVE_1`, and its tests are owned by `WAVE_1`. `GATE-WAVE_0.requiredTaskIds` omits `MR-IMPL-099`.

3. **Wave 0 offline tests are scoped to local persistence and preservation operations.**

   Classification: `PROVEN_FROM_REPOSITORY`

   The Wave 0 integration tests require offline local write/restart/load behavior and fail on attempted outbound fetch during those operations. They do not require the entire installed application to have already completed the later network-removal sequence.

4. **The active Codebase still contains boot-time cloud/telemetry imports, but they are planned for later exclusion.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `bootstrap/browser.ts` and `bootstrap/electron.ts` load telemetry, and the cloud module remains registered. The frozen network boundary map classifies those dependencies as `EXCLUDE_LATER`; Wave 0 preserves them rather than silently mutating them.

5. **The sequencing distinction is compatible, not contradictory.**

   Classification: `INFERENCE`

   Wave 0 establishes that retained local foundations can pass their scoped offline verification. Final no-cloud/no-telemetry behavior is a later release-level requirement implemented by Wave 1 exclusions and enforcement. Because Wave 0 does not claim final product network-removal completeness, there is no unresolved sequencing contradiction.

## Rejected alternatives

- Treating Wave 0 as the final no-cloud/no-telemetry gate was rejected because `GATE-WAVE_0` and the task registry explicitly place enforcement in Wave 1.
- Moving `MR-IMPL-099` into Wave 0 was rejected because that would change the frozen wave ordering without change control.
- Marking this investigation blocked was rejected because every acceptance criterion has a repository-backed answer and no frozen-plan defect was found.

## Decision

Wave 0 can proceed under the existing frozen sequencing: preserve and verify retained foundations, run scoped offline tests, and do not modify cloud/telemetry paths. `MR-IMPL-099` remains a Wave 1 implementation boundary. No frozen-plan change is required.

## Hard blockers

None.

## Soft risks

- A future Wave 0 test harness must keep its integration fixtures truly isolated and offline; otherwise a full app boot could inadvertently trigger still-present cloud or telemetry code.
- The final installed-runtime offline proof remains later work and must not be claimed by `GATE-WAVE_0` alone.

## Implementation consequences

- Wave 0 tasks must preserve the existing cloud/telemetry code and must not attempt final network removal.
- Wave 0 verification must use repository-local structural checks or isolated local fixtures, not a fully launched online product.
- `MR-IMPL-099` and the other `EXCLUDE_LATER` network/telemetry tasks remain authoritative later work.

## What must happen in Wave 0

- Execute only the seven Wave 0 tasks already defined by the frozen queue.
- Verify preserved local foundations and scoped offline persistence without mutating `NETWORK_BOUNDARY_MAP`-classified cloud/telemetry paths.
- Leave `MR-IMPL-099` and the final installed-runtime no-external-traffic proof for their assigned later waves.

## Acceptance criteria results

1. Boot-time and core-path network dependencies are enumerated from actual registrations: **PASS**.
2. Optional/deferred network adapters are separated from mandatory runtime paths: **PASS** at the pre-code evidence level.
3. Wave 0 gate criteria are reconciled with MR-IMPL-099's Wave 1 placement: **PASS**.
4. No unresolved offline-first sequencing contradiction remains: **PASS**.

## Final status

COMPLETE
