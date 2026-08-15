# Investigation Report: MR-INV-008

## Investigation ID

MR-INV-008

## Question

Do Wave 0 KEEP/ADAPT decisions rely only on legally usable, pinned AFFiNE/BlockSuite evidence, and does any task require a transplant-vs-invention receipt before code?

## Why it matters

Every Wave 0 task requires pinned-reference searches, and restricted backend/native or embedded third-party scopes cannot be copied by assumption.

## Frozen-plan references

- Graphify/12 Source Documents/AFFINE_PROVENANCE.md
- Graphify/12 Source Documents/LICENCE_AND_ATTRIBUTION_MAP.md
- Graphify/12 Source Documents/THIRD_PARTY_CODE_REGISTER.jsonl
- Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
- Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl
- Graphify/14 AFFiNE Reference/AFFINE_ACTIVE_CODE_PARITY_REPORT.md
- Graphify/14 AFFiNE Reference/AFFINE_CAPABILITY_INDEX.jsonl
- Graphify/14 AFFiNE Reference/Reference Tree/package.json

## Repository evidence examined

- `AFFINE_PROVENANCE.md`:
  - Repository: `toeverything/AFFiNE`
  - Commit: `da7781a75171140fd966c6cfbe05da9f1fb111d6`
  - Git tree: `4f7b0d6657efa7e9ee0c1e3359e09a21eb8e145f`
  - Package version: `0.26.3`
  - Official archive URL: `https://codeload.github.com/toeverything/AFFiNE/zip/da7781a75171140fd966c6cfbe05da9f1fb111d6`
  - Preserved archive SHA-256: `1fc573a2143f664d4944df4e82570651f54c75ba8a891c546fe9153820a597c9`
- `AFFINE_ACTIVE_CODE_PARITY_REPORT.md`:
  - 110 capabilities searched
  - 0 search-incomplete capabilities
  - 1210 exact path/hash evidence pairs
  - 1105 byte-identical pairs
  - 105 version-delta pairs
  - 0 approved transplants
- `AFFINE_CAPABILITY_INDEX.jsonl` shows all six Wave 0 capability families are `KEEP_EXISTING` with no transplant or invention approval and no blockers.
- `LICENCE_AND_ATTRIBUTION_MAP.md` separates:
  - root `Codebase/LICENSE`: MIT outside `packages/backend` and `packages/common/native`
  - BlockSuite subtree: root MIT scope, subject to embedded component licences
  - `packages/backend/**` and `packages/common/native/**`: AFFiNE EE with MPL-2.0 client-side carveout
  - embedded third-party headers, including two incomplete local licence headers
- `TRANSPLANT_SEARCH_QUEUE.jsonl` contains older per-task rows that do not yet reflect the verified reference tree; `MR-TRANSPLANT-001` is complete, while `MR-TRANSPLANT-002` through `006` remain marked `SEARCH_INCOMPLETE` in that artifact.

## External primary sources examined

The pinned AFFiNE reference tree is preserved locally in `Graphify/14 AFFiNE Reference/Reference Tree/`. No live external access was required for this investigation.

## Tests/commands performed

Read-only repository inspection:

- `git status --short`
- `git fetch origin --prune`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- Parsed provenance, parity, capability index, licence map, implementation tasks, and transplant queue.
- Compared the six Wave 0 capability families in `AFFINE_CAPABILITY_INDEX.jsonl`.

No Codebase files were modified.

## Findings

1. **The pinned AFFiNE reference is verified from the frozen repository.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `AFFINE_PROVENANCE.md` records commit, tree, package version, official archive URL, and preserved archive SHA-256. The extracted reference tree exists under `Graphify/14 AFFiNE Reference/Reference Tree/`.

2. **Active-versus-reference deltas are classified for all six Wave 0 capability families.**

   Classification: `PROVEN_FROM_REPOSITORY`

   - `MR-CAP-001`: 12 active paths, 12 reference paths, 7 identical, 5 version-delta, `KEEP_EXISTING`.
   - `MR-CAP-002`: 12 active paths, 10 reference paths, 9 identical, 1 version-delta, 2 active-only, `KEEP_EXISTING`.
   - `MR-CAP-003`: 12 active paths, 12 reference paths, 11 identical, 1 version-delta, `KEEP_EXISTING`.
   - `MR-CAP-004`: 11 active paths, 11 reference paths, 8 identical, 3 version-delta, `KEEP_EXISTING`.
   - `MR-CAP-005`: 12 active paths, 12 reference paths, 12 identical, 0 version-delta, `KEEP_EXISTING`.
   - `MR-CAP-006`: 12 active paths, 12 reference paths, 12 identical, 0 version-delta, `KEEP_EXISTING`.

3. **No Wave 0 task requires a transplant or invention receipt.**

   Classification: `PROVEN_FROM_REPOSITORY`

   Every Wave 0 capability in `AFFINE_CAPABILITY_INDEX.jsonl` has `transplantApproved: false`, `inventionApproved: false`, and `blockers: []`. The task classifications are `KEEP` and preliminary decisions are `KEEP_EXISTING`.

4. **Licence boundaries are separated correctly for the Wave 0 target families.**

   Classification: `PROVEN_FROM_REPOSITORY`

   Wave 0 targets include frontend core, Electron main/renderer/preload, and BlockSuite/page-mode paths. These are outside the backend/native EE/MPL exception and are mapped to the root MIT scope. BlockSuite is also MIT-scoped, subject to embedded component licences.

5. **The stale transplant-queue rows are a soft bookkeeping risk, not a hard blocker.**

   Classification: `INFERENCE`

   `TRANSPLANT_SEARCH_QUEUE.jsonl` still reports `SEARCH_INCOMPLETE` and `referenceAvailable: false` for `MR-TRANSPLANT-002` through `006`, while the newer `AFFINE_CAPABILITY_INDEX.jsonl` and parity report show the reference tree present, search complete, and KEEP evidence complete. Because no transplant is authorized, Wave 0 remains unblocked.

6. **Final distribution licence work remains later-wave work.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `LICENCE_AND_ATTRIBUTION_MAP.md` records unresolved lockfile/dependency metadata, two incomplete copied-source headers, missing `NOTICE.txt`/`THIRD_PARTY_NOTICES.txt`, and no completed SBOM. These are distribution blockers, not KEEP-preservation blockers.

## Rejected alternatives

- Treating the older `TRANSPLANT_SEARCH_QUEUE` rows as authoritative over the verified reference tree was rejected because the parity report and capability index supersede that stale state.
- Approving any transplant or invention before Wave 0 was rejected because all Wave 0 tasks are `KEEP_EXISTING` and the frozen plan authorizes no transplant/invention.
- Declaring final licence/SBOM readiness was rejected because those tasks remain later work.

## Decision

Wave 0 KEEP decisions are supported by the verified pinned AFFiNE reference and separated licence boundaries. No transplant or invention receipt is required before Wave 0. The stale transplant-queue rows and final distribution licence/SBOM work are later bookkeeping/execution risks, not pre-code blockers.

## Hard blockers

None.

## Soft risks

- `TRANSPLANT_SEARCH_QUEUE.jsonl` should be reconciled with the verified reference/parity evidence before Wave 0 execution.
- Two copied-source headers inside the broader repository have incomplete local licence evidence and must be resolved before distribution/transplant decisions.
- Final dependency licence audit, notices, and SBOM remain later work.

## Implementation consequences

- Wave 0 must preserve existing KEEP targets and must not create substitute implementations.
- Wave 0 must not copy restricted backend/native EE/MPL code into the frontend/BlockSuite target families.
- Later licence/SBOM/notice tasks remain mandatory before release.

## What must happen in Wave 0

- Preserve the six KEEP capability families exactly.
- Record pinned-reference parity evidence for Wave 0 tasks.
- Do not authorize transplants, inventions, or restricted-code copying.
- Leave licence/SBOM/notice completion for later assigned tasks.

## Acceptance criteria results

1. The pinned upstream commit/tree/archive evidence is verified from the frozen repository: **PASS**.
2. Active-vs-reference deltas are classified for all Wave 0 target families: **PASS**.
3. MIT, mixed AFFiNE EE/MPL, and embedded third-party boundaries are separated: **PASS**.
4. Every transplant or invention decision required before Wave 0 is either approved or proven unnecessary: **PASS**.

## Final status

COMPLETE
