# MR-INV-002 — Wave 0 application architecture preservation boundary

## Investigation ID

`MR-INV-002`

## Title

Wave 0 application architecture preservation boundary

## Question

Which application entrypoints, package boundaries, and registrations must Wave 0 preserve, and which exact changes are actually required by `MR-IMPL-001`?

## Why required before implementation

`MR-IMPL-001` is the Wave 0 prerequisite for Electron main, renderer, preload, testing, performance, office, and runtime-bundling work. Its `KEEP` contract must identify a truthful, internally consistent architecture boundary before downstream work can rely on its hashes, tests, or receipts.

## Frozen-plan references

- `Graphify/03 Capability Map/CAPABILITY_REGISTRY.json` — `MR-CAP-001`.
- `Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json` — `locations.MR-CAP-001`.
- `Graphify/04 Exact Location Registry/SYMBOL_REGISTRY.jsonl` — synthetic `MR_CAP_001_CoreSymbol` record.
- `Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl:5` — `MR-IMPL-001`.
- `Graphify/02 Architecture Map/RUNTIME_REGISTRATION_REGISTRY.jsonl` — 33 task-linked runtime registrations.
- `Graphify/02 Architecture Map/BUILD_AND_PACKAGING_MAP.md:28-39` — actual Rspack entries and generated `dist` behavior.
- `Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl` — `TEST-MR-CAP-001-UNIT-001` and `TEST-MR-CAP-001-INTEG-002`.

## Codebase evidence

Evidence classification: `PROVEN_FROM_REPOSITORY` and `EMPIRICALLY_VERIFIED_READ_ONLY`.

- The root is Yarn `4.13.0`; its workspace patterns include `packages/*/*` and `packages/frontend/apps/*`. The root `build` command delegates to `yarn affine build`.
- `@affine/web`, `@affine/mobile`, `@affine/ios`, `@affine/android`, and `@affine/electron-renderer` are distinct workspace packages. Each uses `affine bundle` and depends on `@affine/core` through `workspace:*`.
- `@affine/core` exports `./*` and `./bootstrap`; the platform `app.tsx` composition roots import their runtime modules through those package exports.
- `Codebase/tools/cli/src/bundle.ts:107-174` proves the real bundle entrypoints:
  - web, mobile, iOS, Android: `src/index.tsx`;
  - Electron renderer: `app/index.tsx`, `shell/index.tsx`, `popup/index.tsx`, and `background-worker/index.ts`;
  - package-specific and shared worker entries are also emitted.
- Each of the seven React `index.tsx` entry files exists, calls `createRoot`, imports its adjacent `App`, and renders it.
- All 33 `MR-IMPL-001.runtimeRegistrations` resolve in `RUNTIME_REGISTRATION_REGISTRY.jsonl`; all 33 declaring paths exist, all 33 frozen line snippets exactly match current source, all 33 registered identifiers resolve, and every recorded runtime entrypoint exists.
- All 12 `MR-IMPL-001.exactCurrentPaths` exist. Their SHA-256 values were recorded in `EVIDENCE.json`.
- `Codebase/packages/frontend/core/package.json` exactly matches the frozen file SHA-256 `08ef2498d84d2312b4fc252b4577987993bdd03db4840db795123e0c4e536739`, but it is ordinary JSON and contains neither `MR_CAP_001_CoreSymbol` nor `export interface MR_CAP_001_CoreSymbol`.

## External primary evidence

Evidence classification: `PROVEN_FROM_PRIMARY_EXTERNAL_SOURCE`.

The frozen official AFFiNE reference is repository `toeverything/AFFiNE`, commit `da7781a75171140fd966c6cfbe05da9f1fb111d6`, tree `4f7b0d6657efa7e9ee0c1e3359e09a21eb8e145f`, preserved under `Graphify/14 AFFiNE Reference/Reference Tree/`. Twelve of the sixteen targeted current/reference files are byte-identical, including all seven React `index.tsx` entrypoints and the Electron app/popup/shell composition files. The pinned reference therefore confirms that the real `index.tsx -> App` and multi-entry Electron renderer topology is upstream architecture, not an investigation invention.

## Commands/tests performed

- Required Git/GitHub convergence checks and remote main verification.
- Immutable pre-investigation tag creation, push, and remote target verification.
- Read-only Graphify BFS query using graph vocabulary: `application entry bootstrap package boundary register build preserve location workspace electron renderer`.
- Parsed and reconciled `MR-CAP-001`, `MR-IMPL-001`, exact-location, runtime-registration, build-map, and test-matrix records.
- Verified all 33 registration line anchors and runtime entrypoints against current source.
- Verified all 12 task exact-current paths and computed targeted SHA-256 hashes.
- Compared 16 active entry/build files with the pinned official AFFiNE reference.
- Ran `python "11 Completion/validate_final_graphify_freeze.py" --mode FINAL_FREEZE_CERTIFICATION --verify-only`: `PASS`, 198 checks, 0 failures.
- Ran `python "11 Completion/verify_step11b_results.py" --verify-only`: `PASS`, 198/198 validator IDs and 95/95 challenge IDs present.

No application build, test fixture write, dependency change, or Codebase mutation was performed.

## Findings

### Confirmed architecture to preserve

The preserved application boundary is the existing Yarn workspace topology, `@affine/core` package exports, the platform-specific `app.tsx` composition roots, the seven React `index.tsx` roots, the Electron renderer's background-worker entry, the Rspack entry selection in `tools/cli/src/bundle.ts`, and all 33 verified DI/worker registrations linked to `MR-IMPL-001`.

### Proven implementation detail

`MR-IMPL-001` is classified `KEEP`/`KEEP_EXISTING`. The current and target task path arrays are identical, every listed path exists, and every linked runtime-registration source line is intact. Therefore the evidence-backed Codebase action for the task is preservation and verification, not an application rewrite.

### Frozen-plan contradiction

The frozen authority is internally contradictory in four material ways:

1. `MR-CAP-001`, the exact-location registry, the symbol registry, and the unit-test specification claim that `@affine/core/package.json` contains an exported TypeScript interface `MR_CAP_001_CoreSymbol`. The hash-matching file contains no such symbol or anchor.
2. The capability/task contract names `Codebase/packages/frontend/core/package.json` as the owned module and sole included path, while `MR-IMPL-001.exactCurrentPaths`, `exactTargetPaths`, and `allowedPaths` instead name the root manifest, application composition files, and two app configuration pairs. The owner path is not in the allowed list and is therefore also forbidden by the task's catch-all rule.
3. The frozen build map and live bundler prove eight real Rspack entry source files, but none is present in the task's exact/allowed path arrays. The task also omits the iOS, mobile, and web manifests while claiming to preserve those application boundaries.
4. The Wave 0 unit test literally requires validation of the nonexistent interface, and the integration test requires generic write/restart/reload state behavior not defined by this `KEEP` architecture capability. A structural freeze certification cannot make those acceptance criteria executable or truthful.

The production validator and Step 11b both pass because they validate hashes, schemas, joins, counts, backup bindings, and governance state; this investigation empirically proves they do not validate literal existence of the claimed source anchor or semantic agreement between the capability owner and task path boundary.

## Confirmed assumptions

- The active workspace and application packages already form a coherent buildable boundary.
- The task-linked DI and worker registrations are real and current: 33/33 exact checks passed.
- The correct Codebase decision for `MR-IMPL-001` is `KEEP_EXISTING`; no application source or configuration mutation is presently justified.
- Generated bundle output belongs in package `dist` directories and must remain disposable/non-authoritative.

## Rejected assumptions

- The claimed `MR_CAP_001_CoreSymbol` exists in `@affine/core/package.json`.
- The 12 task allowed paths cover the actual application build entrypoints.
- A passing frozen certification proves source-anchor truth or contract/path semantic agreement.
- The owner/path mismatch can safely be deferred until Wave 0.

## Alternatives considered

1. Treat `MR_CAP_001_CoreSymbol` as a harmless synthetic marker. Rejected because it is classified as an authoritative implementation symbol with a `uniqueAnchor`, exported entrypoint, source span, and literal unit-test step.
2. Treat `MR-IMPL-001` as a no-op and leave the contradictory records untouched. Rejected because future receipts would falsely validate the nonexistent anchor and could not prove the real entrypoint boundary.
3. Repair the frozen authority during this investigation. Prohibited: substantive Graphify changes require explicit frozen-plan change control.

## Decision

`BLOCKED`.

The Codebase preservation decision is proven, but the canonical owner, exact-location symbol, allowed/forbidden path boundary, and acceptance-test semantics are not coherent. `MR-INV-002` cannot satisfy all acceptance criteria until explicit frozen-plan change control repairs those records and re-certifies the authority.

## Implementation consequence

Do not begin Wave 0 or mutate `Codebase/`. Change control must:

1. replace the nonexistent `MR_CAP_001_CoreSymbol` with truthful source anchors or an explicit non-symbol preservation marker;
2. reconcile `MR-CAP-001` ownership with `MR-IMPL-001` exact/current/target/allowed paths and the actual Rspack entry graph;
3. explicitly classify the real entry sources, worker inputs, and generated `dist` outputs as preserve/read-only/generated boundaries;
4. rewrite the two MR-CAP-001 acceptance tests so they verify the architecture contract rather than a nonexistent symbol or undefined persistent state;
5. add validator/challenge coverage for literal anchor existence and owner/allowed-path semantic agreement;
6. rerun the full authorized frozen change-control certification.

## Hard blockers

- `MR-BLOCK-003` — frozen `MR-CAP-001` exact-location, owner, task path, build-entry, and test semantics disagree with each other and with the hash-matching Codebase.

## Soft risks

- Android and iOS `app.tsx`, the root manifest, and the current bundler differ from the pinned AFFiNE 0.26.3 reference; those version deltas are not themselves blockers because the current entrypoint topology is still proven.
- Offline/cloud-adjacent registrations are deferred to `MR-INV-005`; they were not reclassified here.

## Frozen-plan contradiction

`YES`

`frozenPlanContradiction = true`

## Acceptance criteria

1. **PASS** — active application entrypoints and all 33 task-linked registrations were independently verified against Codebase.
2. **PASS** — required Codebase mutation was separated from preserved behavior: no Codebase change is justified for this `KEEP` task.
3. **FAIL** — allowed/generated/forbidden paths do not reconcile with the actual Rspack entry graph and owner path.
4. **FAIL** — architecture ownership and acceptance-test ambiguity remains.

Result: **2 / 4 passed**.

## Final status

`BLOCKED`

`blockingLevel = HARD`

`frozenPlanChangeControlRequired = true`

`userDecisionRequired = false`

`Codebase modified = NO`

`Graphify modified = NO`


---

## Authorized frozen-plan change-control candidate

Updated: `2026-08-11T11:44:49+03:00`

The original `BLOCKED` finding above remains the immutable discovery history. Explicit user change control was subsequently authorized and the repair candidate now:

- reclassifies `MR_CAP_001_CoreSymbol` as historical/superseded and uses a truthful non-symbol `@affine/core` package-manifest anchor;
- binds MR-CAP-001/MR-IMPL-001 to 40 exact source/configuration inputs, including all eight source-derived Rspack entries and seven composition roots;
- keeps the manifest owner exact, allowed, owned, and not forbidden;
- classifies six package `dist/**` roots as generated/disposable and non-authoritative;
- preserves and re-verifies 33/33 registrations;
- replaces the fake-symbol and generic-persistence tests with executable package/export and application-composition assertions;
- adds production checks `ARCH-01` through `ARCH-09` and challenges `CHALLENGE-ARCH-001` through `006`.

Technical evidence: CORE `204/204`, FULL/FINAL `207/207`, challenges `101/101`, zero exemptions, zero baseline subtraction, and unchanged Codebase tree `bbf383e3418da4f613f58719160bb7cbd5709ffc`.

The four investigation acceptance criteria now pass technically (`4 / 4`). The status remains fail-closed as `BLOCKED` and `MR-BLOCK-003` remains active only until the one authorized fresh independent review returns `VERIFIED`; no MR-INV-003 or Wave 0 work may start.
