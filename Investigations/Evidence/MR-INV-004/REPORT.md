# Investigation Report: MR-INV-004

## Investigation ID

MR-INV-004

## Question

Which BlockSuite packages, editor specs, registrations, and page-mode APIs are the compatible preserved foundation for Wave 0?

## Why it matters

Wave 0 tasks `MR-IMPL-005` and `MR-IMPL-006` preserve BlockSuite and page-mode foundations. Version, API, or spec-registration mistakes would invalidate page mode and downstream Wave 1 editing/canvas capabilities.

## Frozen-plan references

- Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
- Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
- Graphify/05 Dependency and Impact/Knowledge Graph/graph.json
- Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
- Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl
- Graphify/12 Source Documents/AFFINE_PROVENANCE.md
- Graphify/12 Source Documents/LICENCE_AND_ATTRIBUTION_MAP.md
- Graphify/14 AFFiNE Reference/AFFINE_ACTIVE_CODE_PARITY_REPORT.md
- Graphify/14 AFFiNE Reference/AFFINE_CAPABILITY_INDEX.jsonl

## Repository evidence examined

- Active `Codebase/blocksuite/` contains 74 package manifests, all at version `0.27.0`.
- Pinned `Graphify/14 AFFiNE Reference/Reference Tree/blocksuite/` contains 74 package manifests, all at version `0.26.3`.
- The active and pinned package-name sets are equal: 0 active-only packages and 0 reference-only packages.
- `Graphify/14 AFFiNE Reference/AFFINE_ACTIVE_CODE_PARITY_REPORT.md` reports:
  - 110 capabilities searched
  - 0 search-incomplete capabilities
  - 1210 exact path/hash evidence pairs
  - 1105 byte-identical pairs
  - 105 version-delta pairs
  - 0 approved transplants
- `Graphify/14 AFFiNE Reference/AFFINE_CAPABILITY_INDEX.jsonl` shows:
  - `MR-CAP-005` (`BlockSuite`) is `KEEP_EXISTING`.
  - `MR-CAP-006` (`Page mode`) is `KEEP_EXISTING`.
  - Each has 12 active paths, all matched by exact repository-relative reference paths, and all byte-identical to the pinned reference.
- `Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl` confirms:
  - `MR-IMPL-005` is `releaseWave: WAVE_0`, `classification: KEEP`, `preliminaryTransplantDecision: KEEP_EXISTING`.
  - `MR-IMPL-006` is `releaseWave: WAVE_0`, `classification: KEEP`, `preliminaryTransplantDecision: KEEP_EXISTING`.
  - `MR-IMPL-006` depends on `MR-IMPL-005`.
- `Graphify/12 Source Documents/AFFINE_PROVENANCE.md` identifies the pinned AFFiNE reference as commit `da7781a75171140fd966c6cfbe05da9f1fb111d6`, tree `4f7b0d6657efa7e9ee0c1e3359e09a21eb8e145f`, package version `0.26.3`.
- `Graphify/12 Source Documents/LICENCE_AND_ATTRIBUTION_MAP.md` maps the BlockSuite subtree to the root MIT scope outside the backend/native EE/MPL exception, subject to embedded component licences and copied-source headers.

## External primary sources examined

The pinned AFFiNE reference tree is preserved locally in `Graphify/14 AFFiNE Reference/Reference Tree/`. No live external access was required for this investigation.

## Tests/commands performed

Read-only repository inspection:

- `git status --short`
- `git fetch origin --prune`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- Enumerated and parsed active `Codebase/blocksuite/**/package.json`.
- Enumerated and parsed pinned `Graphify/14 AFFiNE Reference/Reference Tree/blocksuite/**/package.json`.
- Compared active and reference package-name sets.
- Parsed `IMPLEMENTATION_TASKS.jsonl`, `TRANSPLANT_SEARCH_QUEUE.jsonl`, `AFFINE_CAPABILITY_INDEX.jsonl`, and provenance/licence documents.
- Read page-editor construction and spec-registration paths in `Codebase/packages/frontend/core/src/blocksuite/`.

No Codebase files were modified.

## Findings

1. **The active BlockSuite package family is internally coherent and version-pinned at 0.27.0.**

   Classification: `PROVEN_FROM_REPOSITORY`

   All 74 active package manifests under `Codebase/blocksuite/` declare version `0.27.0`. The monorepo root workspaces include `blocksuite/**/*`, so the active BlockSuite packages are Yarn workspace packages.

2. **The pinned AFFiNE reference contains the same package-family shape at 0.26.3.**

   Classification: `PROVEN_FROM_REPOSITORY`

   The reference tree contains 74 BlockSuite package manifests at version `0.26.3`, and the active/reference package-name sets have no differences.

3. **BlockSuite and page-mode KEEP decisions are directly supported by pinned-reference parity.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `AFFINE_CAPABILITY_INDEX.jsonl` reports `KEEP_EXISTING` for both `MR-CAP-005` and `MR-CAP-006`. All 12 mapped paths for each capability are byte-identical to the pinned reference.

4. **Page editor construction is a thin Lit element that receives preconfigured extension specs.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `Codebase/packages/frontend/core/src/blocksuite/editors/page-editor.ts` defines `PageEditor`, which creates `BlockStdScope({ store: this.doc, extensions: this.specs })`. The specs are supplied by the React adapter, not hard-coded into the element.

5. **Spec registration is centralized through the ViewExtensionManager/ViewProvider pipeline.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `Codebase/packages/frontend/core/src/blocksuite/manager/view.ts` constructs `ViewExtensionManager` from `getInternalViewExtensions()` plus AFFiNE-specific view extensions. `usePatchSpecs('page')` configures foundation, AI, theme, editor config, editor view, cloud, turbo renderer, PDF, mobile, electron, link preview, code preview, icon picker, and comment extensions, then returns `manager.get('page')`.

6. **The AI-specific page spec is an opt-in extension, not the base page foundation.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `Codebase/packages/frontend/core/src/blocksuite/ai/components/page-editor-block-specs.ts` creates a `ViewExtensionManager` and returns a custom page-spec array that overrides `BlockViewIdentifier('affine:page')`. The base `PageEditor` and `ViewProvider` can construct page mode independently; AI extensions are added only through the `.ai(enableAI, framework)` configuration path.

7. **The KEEP decision is licensing-compatible for preservation, not for transplant or distribution.**

   Classification: `PROVEN_FROM_REPOSITORY`

   The BlockSuite subtree is outside the AFFiNE backend/native EE/MPL exception and is mapped to the root MIT scope. Since Wave 0 preserves existing code and authorizes no transplant or redistribution, the KEEP decision is compatible with the current licence boundary. Final distribution still requires later licence/SBOM/notice completion.

8. **A stale transplant-queue field is a soft bookkeeping risk, not a hard blocker.**

   Classification: `INFERENCE`

   `TRANSPLANT_SEARCH_QUEUE.jsonl` still says `referenceAvailable: false` and `SEARCH_INCOMPLETE` for `MR-TRANSPLANT-005/006`, while the more complete pinned-reference artifacts show `SEARCH_COMPLETE`, 0 search-incomplete capabilities, and byte-identical evidence. Because the task decision is `KEEP_EXISTING` and no transplant is authorized, this does not block pre-code investigation, but Wave 0 evidence should reconcile it before execution.

## Rejected alternatives

- Treating BlockSuite 0.27.0 as an unresolvable API risk was rejected because the pinned reference, package-family comparison, and byte-identical path evidence establish a concrete preserved foundation.
- Inventing a new page-editor construction path was rejected because Wave 0 is KEEP and the existing `ViewExtensionManager` pipeline is the frozen foundation.
- Treating the active 0.27.0 versus reference 0.26.3 version delta as a contradiction was rejected because the frozen plan explicitly records version-delta evidence and authorizes no transplant.

## Decision

Wave 0 must preserve the active BlockSuite 0.27.0 workspace family and the existing `ViewExtensionManager` page-spec registration pipeline. AI-specific page extensions are adjacent opt-in config, not the base page foundation. The KEEP decision is compatible with the pinned AFFiNE reference and the current MIT-scoped BlockSuite licence boundary.

## Hard blockers

None.

## Soft risks

- `TRANSPLANT_SEARCH_QUEUE.jsonl` contains stale `referenceAvailable: false`/`SEARCH_INCOMPLETE` rows for `MR-TRANSPLANT-005/006`; Wave 0 should reconcile them with the verified reference evidence.
- Two copied-source headers inside BlockSuite (`figma-squircle` and toast) have incomplete local licence evidence. This does not block KEEP preservation, but it must be resolved before any future transplant or distribution decision.
- The final NPM/Cargo/native dependency licence audit remains unresolved and must be completed before release.

## Implementation consequences

- `MR-IMPL-005` must preserve the active BlockSuite 0.27.0 package family and page-spec pipeline without replacing it.
- `MR-IMPL-006` must preserve page-mode construction and spec registration exactly as provided by `ViewExtensionManager.get('page')`.
- AI-specific page specs must remain separate from the base page foundation and must not be silently merged into non-AI page mode.

## What must happen in Wave 0

- Verify the 74 active BlockSuite package manifests and version 0.27.0.
- Verify the page-editor/spec-registration path in `manager/view.ts` and `lit-adaper.tsx`.
- Verify `MR-CAP-005` and `MR-CAP-006` pinned-reference parity evidence remains byte-identical.
- Leave transplant and licence/SBOM/distribution decisions for their assigned later tasks.

## Acceptance criteria results

1. Active BlockSuite package versions and workspace boundaries are identified: **PASS**.
2. Page editor construction and spec registration paths are proven from Codebase: **PASS**.
3. AI-specific adjacent paths are separated from the non-AI foundation: **PASS**.
4. The KEEP decision is compatible with the pinned AFFiNE reference and licensing boundary: **PASS**.

## Final status

COMPLETE
