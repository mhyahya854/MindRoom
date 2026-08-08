# MindRoom Master Plan 03 — How We Will Keep, Delete, Reorganise, and Implement

# 1. Authority

This document defines the autonomous execution method for transforming AFFiNE into MindRoom.

The project root must converge to exactly two project-content folders:

```text
Project Root/
├─ Codebase/
└─ Graphify/
```

`Codebase/` contains the complete working application and **zero repository Markdown files**.

`Graphify/` contains all plans, Markdown files, Graphify intelligence, exact locations, agent state, progress, reviews, evidence, and final reports.

---

# 2. Non-Negotiable Execution Rules

### Supreme Control Block (MANDATORY BINDING RULES)
- **No Routine Permission Requests:** Execute autonomously without repeatedly asking for permission for safe, non-destructive file operations and tests.
- **No User-Data Destruction:** Never delete, overwrite, or corrupt original user data, databases, workspaces, or recordings.
- **No Destructive Git Commands (FORBIDDEN):** Never execute `git reset --hard`, `git clean -fd`, `git checkout .`, `git restore .`, or `git reset --hard HEAD~1`. Never assume the working tree should be clean by deleting files.
- **Git Remediation Rule:** Correct a bad committed batch with `git revert <commit>`. Correct uncommitted mistakes manually without overwriting unrelated user changes. Preserve all staged, unstaged, and untracked user work.
- **Git Baseline Rule:**
  Confirm the real repository root and inspect the existing Git state.

  If Git is absent, empty, broken, or unusable, follow the Provenance-First Git
  Recovery Order in Section 19.1.

  Do not initialise a new Git repository until:

  1. The original repository root has been searched for.
  2. Parent directories have been inspected.
  3. Worktrees and linked Git directories have been checked.
  4. Existing repository metadata has been investigated.
  5. A SHA-256 filesystem baseline has been recorded.
  6. Recovery of the original Git history has been determined to be impossible.
  7. Repository provenance has been documented.
  8. The orchestrator has recorded the decision.

  Creating a new repository must never be described as recovering the original
  history.
- **No False Completion:** Never claim completion without generating required verification proof receipts and passing all release gates.
- **Preservation-First Engineering:** Prioritize preserving working local functionality, historical data, and mature upstream implementations over stylistic rewrites.
- **Real Verification & Testing:** Static typechecks and mocks are insufficient for persistence, IPC, and filesystem boundaries. Require real disposable SQLite/workspace tests, real IPC round trips, real backup/restore tests, and real packaged offline proof.
- **Ordinary Failures are Repair Tasks:** Diagnose root causes of build/test failures, exhaust reasonable repo-local solutions, and record meaningful attempted repairs. Continue until resolved or genuinely externally blocked without fixed ceremonial attempt counts (e.g. "exactly three attempts" is FORBIDDEN). Record in `OPEN_BLOCKERS.md` only when a blocker is genuine and unresolved.
- **Continue Through Complete Plan:** Autonomously iterate through all migration and verification phases until every release gate is proven by evidence.

### Operational Execution Rules
- Work from the real repository, not an assumed folder.
- Preserve pre-existing user changes.
- Do not use destructive resets or broad clean commands.
- Execute autonomously without repeatedly asking for permission.
- Use a real subagent swarm where the environment supports it.
- Do not simulate many agents with one agent pretending to change hats.
- Preserve as much original AFFiNE code as possible.
- When compatible AFFiNE code exists, copy the complete coherent implementation rather than inventing a substitute.
- Do not perform cosmetic mass moves that destroy working package boundaries.
- Reorganise in dependency-safe batches.
- Test after every meaningful batch.
- Update Graphify after every meaningful batch.
- Do not claim completion without evidence.

# 3. Deterministic Execution State and Crash Recovery

To prevent loss of context after crashes, session restarts, or context exhaustion, MindRoom execution relies on a persistent mechanical state machine rather than conversation memory.

Define this authoritative structure under `Graphify/`:
```text
Graphify/00 Execution Control/
├─ status.json
├─ active_tasks.jsonl
├─ completed_tasks.jsonl
├─ blocked_tasks.jsonl
├─ rollback_records.jsonl
├─ tool_status.json
├─ repository_baseline.json
└─ schemas/
```

## 3.1 Mandatory session startup

At the beginning of every execution session, before starting new work:
1. Confirm the current repository root.
2. Read `status.json`.
3. Read the latest records in `active_tasks.jsonl`.
4. Read incomplete rollback records.
5. Inspect Git or filesystem hash state.
6. Verify whether any task is `IN_PROGRESS`.
7. Resume or safely roll back the incomplete task.
8. Do not accept new work until incomplete mutation state is resolved.
9. Do not rely on conversation memory.
10. Treat persisted repository state as authoritative.

## 3.2 status.json minimum schema

Include:
```json
{
  "project": "MindRoom",
  "schemaVersion": 1,
  "projectPhase": "INVENTORY_AND_MAPPING",
  "currentBatchId": null,
  "currentTaskId": null,
  "lastCompletedTaskId": null,
  "lastUpdatedAt": "ISO-8601",
  "repositoryRoot": "",
  "codebaseRoot": "",
  "graphifyRoot": "",
  "gitStatus": "AVAILABLE | MISSING | BROKEN | UNKNOWN",
  "graphifyStatus": "AVAILABLE | MISSING | BROKEN | UNKNOWN",
  "ponytailStatus": "AVAILABLE | MISSING | BROKEN | UNKNOWN",
  "subagentStatus": "AVAILABLE | UNAVAILABLE | LIMIT_REACHED | UNKNOWN",
  "releaseGateStatus": "LOCKED"
}
```

## 3.3 active_tasks.jsonl minimum schema

Include:
```json
{
  "taskId": "task-0001",
  "batchId": "batch-0001",
  "agentId": "agent-0001",
  "capabilityId": "capability-id",
  "status": "IN_PROGRESS",
  "startedAt": "ISO-8601",
  "allowedPaths": [],
  "forbiddenPaths": [],
  "sourcePaths": [],
  "targetPaths": [],
  "plannedMutations": [],
  "testsRequired": [],
  "rollbackInstructions": [],
  "lastCompletedStep": 0,
  "nextStep": 1,
  "lastKnownHashes": {}
}
```

Require append-only completion, blocking, and rollback records where practical. A crashed run must resume from these files rather than restarting the full audit.

---

# 4. Master Plan Location

```text
Graphify/
└─ Master Plan/
   ├─ 01-EVERYTHING-WE-ARE-KEEPING.md
   ├─ 02-EVERYTHING-WE-ARE-DELETING.md
   └─ 03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md
```

Graphify must read all three files before mapping or modifying code.

# 5. Markdown Separation and `.gitignore` Standard

All repository-owned `.md` and `.markdown` files must be moved out of `Codebase/` and into `Graphify/` while preserving their original paths in the migration ledger.

Required legal material inside `Codebase/` must use complete non-Markdown copies such as:

```text
LICENSE.txt
NOTICE.txt
THIRD_PARTY_NOTICES.txt
```

The final scan must return zero Markdown files under `Codebase/` (MANDATORY). Do not allow `.md` licence exceptions; use plain-text `LICENSE`, `NOTICE`, and `THIRD_PARTY_NOTICES`. Third-party installed dependencies inside generated `node_modules/` are not authoritative tracked Codebase source. User-exported Markdown remains allowed.

## 5.1 Path-Specific `.gitignore` Standard (MANDATORY)
- Do not use broad wildcard ignore patterns such as `*.db`, `*.sqlite`, `*.bin`, `*.onnx`, `*.wav`, or `*.mp3` (FORBIDDEN). These may hide required database fixtures, migration fixtures, bundled models, native binaries, test media, or reproducible build inputs.
- Require path-specific exclusions such as `Codebase/node_modules/`, `Codebase/dist/`, `Codebase/release/`, `Codebase/coverage/`, `Codebase/.cache/`, `Codebase/runtime-data/`, and `Codebase/temp/`.
- Inspect each existing asset directory before excluding it.

# 6. Graphify Intelligence Structure and Operational Tiers

The authoritative Graphify operational core must be lean and maintainable. Never maintain duplicate JSON and Markdown mirrors of the same registry. Never require removed or merged files to exist.

Authoritative Execution-State Rule:

`Graphify/00 Execution Control/status.json` is the sole authoritative source for
the current project phase, active batch, active task, tool status, repository
roots, and release-gate lock state.

`RUN_STATE.md`, if generated, is a read-only human-readable summary derived from
`status.json`.

`RUN_STATE.md` must never:

- act as an independent source of truth
- contain state not present in `status.json`
- be manually edited to change execution status
- override `status.json`
- be used to resume a crashed task

If `RUN_STATE.md` conflicts with `status.json`, `status.json` wins and
`RUN_STATE.md` must be regenerated.

## 6.1 Tier 1: Continuously Updated Operational Core (MANDATORY)
These files must be updated continuously after each coherent capability batch:
1. `Graphify/00 Execution Control/status.json`
2. `Graphify/00 Execution Control/active_tasks.jsonl`
3. `Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json` — maps every capability and symbol to its authoritative file path. Do not create a redundant `.md` human mirror.
4. `Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md` — prioritized backlog of migration tasks.
5. `Graphify/11 Completion/COMPLETION_TRACKER.md` — status of release gates and verification receipts.
*Note: `RUN_STATE.md` is optional generated human-readable output derived from `status.json`. `OPEN_BLOCKERS.md` is updated ONLY when an engineering blocker is genuine and remains unresolved after exhausting local repairs.*

## 6.2 Tier 2: Phase-Boundary Registries
Updated at major phase transitions (e.g. completing reorganisation, finishing deletions):
- Repository inventory (`01 Corpus Inventory/`)
- Architecture maps (`02 Architecture Map/` and `03 Capability Map/`)
- Folder ownership (`06 Folder Ownership/`)
- Move ledger (`07 Reorganisation/`) and Deletion ledger (`08 Cleanup/`)
- Third-party code register (under `12 Source Documents/`)
- Test matrix and regression results (`10 Verification/`)

## 6.3 Tier 3: Final-Only or Generated Reports
Generated only upon requirement or at final release verification:
- Dependency graph, import/call map, circular dependency report (`05 Dependency and Impact/`)
- Ponytail audit report (`08 Cleanup/`)
- Final Graphify audit, codebase map, folder tree, capability matrix, change summary, and final handoff (`11 Completion/`)

```text
Graphify/
├─ Master Plan/
├─ 00 Execution Control/
├─ 01 Corpus Inventory/
├─ 02 Architecture Map/
├─ 03 Capability Map/
├─ 04 Exact Location Registry/
├─ 05 Dependency and Impact/
├─ 06 Folder Ownership/
├─ 07 Reorganisation/
├─ 08 Cleanup/
├─ 09 Implementation/
├─ 10 Verification/
├─ 11 Completion/
├─ 12 Source Documents/
├─ 13 Agent Swarm/
├─ 14 AFFiNE Reference/
└─ 15 Processed Plan Snapshots/
```

# 7. Required Graphify Records

For every capability and meaningful symbol, record in `EXACT_LOCATION_REGISTRY.json`:

- Stable capability ID
- Stable symbol ID
- Canonical retention category (`KEEP UNCHANGED`, `KEEP AND RELOCATE`, `KEEP AND WRAP`, `KEEP AND ADAPT`, `KEEP AS DERIVED STATE`, `KEEP FOR COMPATIBILITY`, or `KEEP FOR LICENCE/ATTRIBUTION`)
- Entity type
- Current status (from canonical status model)
- Current repository-relative path
- Symbol, component, function, class, route, command, schema, or unique anchor
- Current line range as secondary convenience
- Graphify node ID
- Current owner
- Intended owner
- Intended final path
- Reason for final ownership
- Dependencies
- Dependants
- Runtime registrations
- Configuration references
- Tests
- Planned changes
- Verification evidence

Do not repeatedly rescan a verified location unless its hash, symbol anchor, dependency graph, or path changed.

# 8. Capability Ownership

Every unique product capability receives one authoritative home.

Every function must belong to the smallest coherent capability module. Do not create a separate physical folder for every tiny function. That would turn a codebase into filing-cabinet confetti.

Candidate capability homes include:

- Workspace
- Page bundles
- Workspace library
- Markdown storage
- File locator
- Universal import
- PDF
- PDF annotations
- Office engine
- Word
- PowerPoint
- Excel
- CSV
- Database
- Kanban
- Whiteboard
- Infinite canvas
- Mind map
- Knowledge graph
- Search
- Photos
- Videos
- Media metadata
- File watcher
- Sync journal
- Conflict resolution
- Atomic writes
- Backups
- Trash
- Restoration
- Graph rebuild
- Search rebuild
- Export
- Offline policy
- Network blocking
- Packaging
- Testing

# 9. AFFiNE Copy and Preservation Procedure

Before replacing or creating any capability:

1. Inspect the active implementation.
2. Inspect the supplied AFFiNE ZIP.
3. Inspect the extracted AFFiNE reference tree.
4. Locate the complete upstream module.
5. Locate its types, stores, services, schemas, workers, styles, assets, tests, initialisation, cleanup, and dependencies.
6. Determine whether it can remain in place unchanged.
7. Determine the smallest necessary adaptation.
8. Copy the coherent implementation when direct reuse is required.
9. Preserve licence headers and attribution.
10. Record the transplant.

Permitted adaptations are limited to:

- Import paths
- Package boundaries
- MindRoom branding
- File-backed persistence
- Page and workspace ownership
- Offline dependency injection
- Local runtime lookup
- Removal of cloud boundaries
- Removal of authentication
- Removal of billing
- Removal of AI
- Removal of telemetry
- Removal of collaboration
- Packaging paths

Do not describe a replacement as inspired by AFFiNE when the actual AFFiNE code is available. Copy it, integrate it, test it.

# 10. Deletion Procedure

There is one canonical deletion procedure across all Master Plan files. Never use direct deletion or `rm` on source files in `Codebase/`.

### 10.1 Canonical Deletion Sequence
```text
CANDIDATE
→ DISCOVERY
→ DEPENDENCY PROOF
→ RUNTIME-REGISTRATION PROOF
→ MIGRATION AND DATA-COMPATIBILITY PROOF
→ QUARANTINE
→ IMPORT/EXPORT/REGISTRATION REPAIR
→ SCOPED TESTS
→ TYPECHECK
→ INTEGRATION TESTS
→ PRODUCTION BUILD
→ PACKAGING CHECKS WHEN APPLICABLE
→ GRAPHIFY UPDATE
→ INDEPENDENT REVIEW
→ DELETION RECEIPT APPROVED
→ PERMANENT PURGE
→ RECEIPT UPDATED TO PURGED
```

### 10.2 Deletion Rules
1. The Deletion Receipt is created while the item is quarantined.
2. The receipt must contain all dependency, registration, migration, test, build, Graphify, and reviewer evidence.
3. The independent reviewer sets:
```text
reviewDecision: "APPROVED"
status: "QUARANTINED"
```
before permanent purge.
4. Permanent purge is forbidden until the approved receipt exists under `Graphify/08 Cleanup/Deletion Receipts/`.
5. After purge, the existing receipt is updated to:
```text
status: "PURGED"
purgedAt: "ISO-8601 timestamp"
```
6. A new receipt must not be created after purge merely to justify an action that already occurred.
7. If review is rejected or any required check fails, the item must be restored and the receipt updated to:
```text
status: "RESTORED"
reviewDecision: "REJECTED"
```

# 11. Reorganisation Procedure and Monolith Decomposition

Perform small, coherent, dependency-safe batches:

1. Select low-dependency leaf modules.
2. Assign an implementation agent.
3. Assign an independent reviewer.
4. Record current and target locations.
5. Preserve or copy AFFiNE code.
6. Move the coherent implementation.
7. Update imports, exports, routes, commands, IPC, workers, aliases, build paths, packaging paths, and tests (MANDATORY: verify `pnpm-workspace.yaml`, `tsconfig.json`, bundler aliases, and test runner configs).
8. Run scoped verification.
9. Run integration verification.
10. Update Graphify.
11. Update exact-location records.
12. Review and integrate.
13. Continue automatically.

Do not perform one enormous blind move and then spend the next geological era repairing it.

## 11.1 Batching & Monolith Decomposition Standard (MANDATORY)
- **Coherent Micro-Batching:** One coherent, dependency-safe capability batch per commit (when Git is available) or per hash-manifest checkpoint (when Git is unavailable). Maximum 5 source files or 1 cohesive leaf module per normal mutation batch. Reject artificial limits such as "one top-level directory per commit".
  - Clarification on Micro-Batch Rules: The 5-file limit applies to source mutations, not read-only analysis. Large coherent AFFiNE modules may exceed five files only when splitting them would create an unsafe partial transplant. The exception must be documented in Graphify before mutation, and the orchestrator and reviewer must approve the exception.
  - Package-boundary changes are separate batches. Database migrations are separate batches. Large files must be moved and behaviourally modified in separate batches when practical. Every batch requires a rollback record and tests. Do not let the numerical rule encourage unsafe fragmentation.
- **Monolith Decomposition Procedure:** Large file size alone is not a reason to split. Do not split a file until multiple real responsibilities are proven. When splitting is justified by evidence, follow this 12-step deterministic procedure based on symbol/caller mapping rather than file size:
  1. Map symbols.
  2. Map callers.
  3. Map runtime registrations.
  4. Assign capability owners.
  5. Add or confirm characterisation tests.
  6. Extract low-risk leaf logic.
  7. Use a temporary compatibility facade only when required.
  8. Migrate callers incrementally.
  9. Run targeted checks (using repository-discovered commands).
  10. Run real IPC or persistence integration tests on disposable file fixtures.
  11. Remove facade when no callers remain.
  12. Prove zero duplicate implementation.

Git-or-Hash Batch Checkpoint Rule:

One coherent, dependency-safe capability batch must correspond to one Git commit
when a valid and usable Git repository is available.

When Git is unavailable, broken, unrecoverable, or intentionally not
reinitialised, one coherent capability batch must correspond to one SHA-256
before-and-after hash-manifest checkpoint.

Each hash-manifest checkpoint must record:

- checkpoint schema version
- batch ID
- task ID
- capability ID
- agent ID
- affected repository-relative paths
- pre-mutation SHA-256 hashes
- post-mutation SHA-256 hashes
- files created
- files modified
- files moved
- files quarantined
- files permanently purged
- previous and new paths for moved files
- rollback instructions
- commands executed
- command working directories
- command exit codes
- verification receipt IDs
- independent reviewer
- review decision
- creation timestamp
- completion timestamp

The checkpoint must be written before the next batch begins.

A hash-manifest checkpoint must provide rollback, review, and verification
evidence equivalent to the evidence normally associated with a Git commit.

Do not claim that a Git commit exists when Git is unavailable.

Do not initialise a new Git repository merely to satisfy this batching rule.

Follow the Provenance-First Git Recovery Order before creating a new repository.

# 12. One Authoritative Implementation

When duplicate implementations exist:

1. Compare behaviour.
2. Compare edge cases.
3. Compare tests.
4. Prefer the complete compatible AFFiNE implementation.
5. Preserve data compatibility.
6. Redirect every caller.
7. Add missing tests.
8. Remove the duplicate.
9. Remove redundant exports and dependencies.
10. Verify one runtime path remains.

## 12.1 Mandatory AFFiNE Anti-Reinvention Receipt Interlock

No new substitute implementation file may be created until a valid `TRANSPLANT_VS_INVENTION_RECEIPT` exists under `Graphify/09 Implementation/Transplant Receipts/`.

Each receipt must match this exact schema:
```json
{
  "receiptId": "transplant-0001",
  "capabilityId": "capability-id",
  "requiredBehaviour": [],
  "activeCodeSearchQueries": [],
  "affineReferenceSearchQueries": [],
  "activeFilesFound": [],
  "affineFilesFound": [],
  "coherentModuleBoundary": [],
  "decision": "KEEP_EXISTING | KEEP_AND_ADAPT | COPY_COHERENT_IMPLEMENTATION | REPAIR_PARTIAL | INVENT_NEW",
  "decisionReason": "",
  "copiedFiles": [],
  "adaptedFiles": [],
  "requiredAdaptations": [],
  "licenceStatus": "APPROVED | BLOCKED | NOT_APPLICABLE",
  "independentReviewer": "",
  "approved": false
}
```

**Anti-Reinvention Rules:**
- `INVENT_NEW` is allowed only when no suitable active or AFFiNE implementation exists.
- The search queries must be recorded.
- Technical incompatibility must be documented.
- Licence review must pass.
- An independent reviewer must approve invention.
- If AFFiNE has a coherent implementation, copy it with its tests, types, styles, assets, workers, registrations, lifecycle handling, and attribution.
- Technical difficulty is not evidence of incompatibility.

# 13. Agent Swarm

Use a real swarm with:

- Master orchestrator
- Graphify mapping agents
- AFFiNE source mapping agents
- Capability implementation agents
- Removal agents
- Data durability agents
- Reviewer agents
- Repair agents
- Integration agents
- Packaging agents
- Final verification agents

Every implementation task requires one accountable implementer and one independent reviewer.

Persist swarm state under `Graphify/13 Agent Swarm/` so a crashed run resumes instead of restarting the entire audit.

# 14. Status Model (Canonical Mechanical State Machine)

Replace all informal status lists with this canonical mechanical state machine:
```text
NOT_STARTED
→ MAPPED
→ READY
→ IN_PROGRESS
→ IMPLEMENTED
→ TESTING
→ READY_FOR_REVIEW
→ CHANGES_REQUESTED
→ READY_TO_INTEGRATE
→ INTEGRATED
→ VERIFIED_COMPLETE
```

Failure and terminal states:
- `BLOCKED` — requires an exact blocker, exact current file or symbol, and exact next action recorded in Graphify.
- `IMPLEMENTED_BUT_FAILING` — code is written but fails automated checks or verification.
- `REGRESSION_FOUND` — previously passing verification failed after an integration or mutation.
- `OBSOLETE` — capability or task superseded by an approved architectural change.
- `REMOVED` — requires a valid Deletion Receipt and independent review approval.

**State Machine Rules:**
- Who may assign: Implementers may assign up to `READY_FOR_REVIEW` and failure states. Reviewers may approve `READY_TO_INTEGRATE` or assign `CHANGES_REQUESTED`. The integration controller may assign `INTEGRATED`.
- `VERIFIED_COMPLETE` requires successful integrated verification on real file fixtures and independent review approval; implementers may not assign `VERIFIED_COMPLETE` to their own work.
- Dependent tasks may start only when upstream dependencies reach `READY_TO_INTEGRATE`, `INTEGRATED`, or `VERIFIED_COMPLETE`.
- Deletion is allowed only after dependency proof, quarantine, and independent review approval.
- Release may proceed only when all applicable tasks reach `VERIFIED_COMPLETE`, `OBSOLETE`, or `REMOVED`.

---

# 15. Anti-Repetition and Token-Efficiency Rules

To prevent context exhaustion and redundant computation:
- Require registry-first lookup, task-ledger lookup, Graphify node lookup, file-hash comparison, handoff lookup, and reviewer-result lookup before rescanning files.
- No full repository rescan for already verified unchanged paths.
- No repeated full corpus scan after small edits.
- Require targeted Graphify updates after each micro-batch.
- Assign one capability per normal implementation task.
- Generate concise structured handoffs between agents.
- Checkpoint state to disk before context exhaustion.
- Resume from disk upon crash or restart.
- Do not restate the entire Master Plan in agent reports.

Repeat work only when:
- Relevant code changed.
- A dependency changed.
- Previous evidence failed or was incomplete.
- Integration exposed a regression.
- Final release verification requires a fresh run.

---


# 16. Complete MindRoom Addition Scope

## 16.1 File-backed workspace architecture

This is the largest new system.

Every important user object receives a visible folder or ordinary source file.

The application can maintain caches and databases, but these must be rebuildable.

---

## 16.2 User-named Markdown pages

Add:

* One user-visible Markdown file per page
* File name based on the user-set page title
* Safe filename sanitization
* Duplicate filename handling
* Invalid filename handling
* Reserved-name handling
* External file rename detection
* App-driven file rename
* Stable UUID identity independent of filename
* `mainMarkdownFile` metadata
* Atomic write behavior
* Backup before risky rename
* Recovery after partial rename

Do not use a fixed `index.md`.

---

## 16.3 Page bundles

Add page-owned directories:

```text
Pages/
└─ page-{uuid}-{slug}/
   ├─ {User Page Name}.md
   ├─ page.meta.json
   ├─ assets/
   ├─ media/
   ├─ imports/
   ├─ databases/
   ├─ kanban/
   ├─ whiteboards/
   ├─ mind-maps/
   └─ exports/
```

Anything imported while inside a page belongs to that page unless explicitly promoted to workspace scope.

---

## 16.4 Workspace library

Add shared workspace-level storage:

```text
WorkspaceLibrary/
├─ assets/
├─ media/
├─ imports/
├─ databases/
├─ kanban/
├─ whiteboards/
├─ mind-maps/
└─ exports/
```

Shared files are stored once and referenced through UUIDs.

---

## 16.5 Page-to-workspace promotion

Add the ability to promote an object from page scope to workspace scope.

Requirements:

* Preserve UUID
* Move source files atomically
* Update references
* Update backlinks
* Update search
* Update graph
* Update metadata
* Preserve backups
* Recover from partial failure
* Avoid duplicate storage

---

## 16.6 Universal file import router

Add one canonical import system that determines:

* Page scope or workspace scope
* File type
* Destination bundle
* Stable UUID
* Safe user-visible filename
* Metadata extractor
* Preview generator
* Text extractor
* Search indexer
* Graph node generator
* Conflict behavior
* Unsupported-file behavior

It must support at minimum:

* Markdown
* PDF
* DOCX
* ODT
* PPTX
* ODP
* XLSX
* ODS
* CSV
* JPG
* PNG
* WebP
* MP4
* Common compatible media
* Unsupported file preservation

---

## 16.7 PDF bundles

Add:

```text
imports/
└─ pdf-{uuid}-{slug}/
   ├─ original/
   │  └─ {User File Name}.pdf
   ├─ metadata.json
   ├─ extracted/
   │  ├─ text.txt
   │  ├─ page-001.txt
   │  └─ images/
   ├─ previews/
   │  ├─ page-001.png
   │  ├─ thumbnail.webp
   │  └─ preview.html
   ├─ annotations/
   │  ├─ annotations.json
   │  └─ annotations.xfdf
   └─ app-import/
```

Add:

* Native PDF viewer
* Thumbnails
* Text extraction
* Corrupt PDF handling
* Encrypted PDF handling
* Annotation persistence
* Optional write-back only after backup
* Rebuildable previews

---

## 16.8 Native Office editing

Add a local Office engine abstraction:

```text
OfficeEngineAdapter
```

Required operations:

```text
detectEngine()
healthCheck()
startEngine()
openDocument(filePath, mode)
renderPreview(filePath, outputPath)
saveDocument(sessionId)
closeDocument(sessionId)
extractText(filePath, outputPath)
exportPdf(filePath, outputPath)
shutdown()
```

Preferred order:

1. LibreOffice/LibreOfficeKit
2. Local Collabora-style embedded editor
3. Headless LibreOffice for conversion/extraction
4. System-open only as unsupported fallback

The engine lives in the installed app runtime, not in each workspace. The Office requirements and offline adapter strategy are explicitly part of the project plan. 

---

## 16.9 Word and ODT bundles

Add:

```text
word-{uuid}-{slug}/
├─ original/
├─ metadata.json
├─ extracted/
├─ previews/
├─ native-edit/
│  ├─ lock.json
│  ├─ session.json
│  └─ autosave/
└─ app-import/
```

Support:

* DOCX
* ODT
* Local opening
* Local editing
* Save to original
* Reopen verification
* Text extraction
* Preview regeneration
* External-edit detection
* Conflict preservation

---

## 16.10 PowerPoint and ODP bundles

Add:

```text
ppt-{uuid}-{slug}/
├─ original/
├─ metadata.json
├─ extracted/
│  ├─ text.txt
│  ├─ slide-001.txt
│  └─ media/
├─ previews/
│  ├─ slide-001.png
│  ├─ preview.html
│  ├─ preview.pdf
│  └─ thumbnail.webp
├─ native-edit/
└─ app-import/
```

Support local viewing, editing, save-back, extraction, previews, external edits, and conflicts.

---

## 16.11 Excel and ODS bundles

Add:

```text
excel-{uuid}-{slug}/
├─ original/
├─ metadata.json
├─ extracted/
│  ├─ workbook.json
│  ├─ sheet-001.csv
│  └─ formulas.json
├─ previews/
│  ├─ sheet-001.html
│  ├─ workbook-preview.html
│  └─ thumbnail.webp
├─ native-edit/
└─ app-import/
```

Support local editing and save-back.

---

## 16.12 CSV editor

Add a native CSV table editor:

* Correct delimiter handling
* Encoding handling
* Quoted-cell handling
* Multiline-cell handling
* Malformed CSV protection
* Large CSV handling
* Atomic save
* External-change detection
* Conflict behavior
* Search indexing
* Database conversion where requested

---

## 16.13 Photo system

Add:

```text
photo-{uuid}-{slug}/
├─ original/
├─ metadata.json
├─ extracted/
│  └─ exif.json
├─ thumbnails/
│  ├─ thumb-small.webp
│  └─ thumb-large.webp
├─ previews/
│  └─ preview.webp
└─ links.json
```

Support:

* Native viewer
* Zoom
* Rotation
* Metadata
* EXIF extraction
* Thumbnails
* Large-image safety
* Corrupt-image behavior
* External edits
* Search and graph indexing

---

## 16.14 Video system

Add:

```text
video-{uuid}-{slug}/
├─ original/
├─ metadata.json
├─ extracted/
│  └─ video-metadata.json
├─ thumbnails/
├─ previews/
│  └─ poster.webp
└─ links.json
```

Support:

* Native playback
* Poster generation
* Bundled local metadata probing
* Duration and dimensions
* Codec information
* Unsupported codec fallback
* Large-video responsiveness
* Streaming instead of unnecessary whole-file buffering
* External-edit detection
* Search and graph indexing

---

## 16.15 File locator and relocation system

Add one canonical file-locator capability:

* Resolve UUID to source path
* Resolve page ownership
* Resolve workspace ownership
* Find moved files
* Detect missing files
* Detect external renames
* Match by size, hash, and metadata
* Repair stale references
* Support repository and workspace relocation
* Avoid hardcoded development paths
* Store relative references where appropriate
* Preserve user-selected external workspace paths

---

## 16.16 File watcher

Add a production filesystem watcher that detects:

* File additions
* File edits
* File renames
* File moves
* File deletions
* Directory changes
* Page Markdown changes
* Imported-file changes
* Database JSON changes
* Whiteboard JSON changes
* Mind-map JSON changes
* Media changes

Requirements:

* Debouncing
* Hash checking
* Size checking
* Modification-time checking
* Rename correlation
* Self-write suppression
* Watcher-loop prevention
* Recovery after restart
* Large-directory performance

---

## 16.17 Two-way synchronization

Add:

```text
App edit → ordinary source file
External edit → app refresh
```

When a file changes:

* Metadata updates
* Preview regenerates
* Extracted content regenerates
* Search updates
* Graph updates
* Open UI refreshes
* Conflicts are created when necessary

This is local disk synchronization—not cloud sync.

---

## 16.18 Sync journal and crash atomicity

Add:

```text
sync-journal.jsonl
```

Use crash-safe mutation ordering:

1. Create recovery snapshot
2. Record intent
3. Flush intent
4. Write temporary file
5. Atomically replace destination
6. Flush destination where supported
7. Record completion
8. Rebuild derived state
9. Recover incomplete operations after restart

---

## 16.19 Conflict system

Add:

```text
Backups/
└─ conflicts/
   └─ {timestamp}-{file-uuid}/
      ├─ app-version/
      ├─ external-version/
      ├─ conflict.meta.json
      └─ resolution.json
```

Create conflicts when:

* App saves after an external hash change
* External change occurs while a document is dirty
* Rename occurs during an active session
* Deletion occurs during an active session
* Conversion fails after an external change
* Concurrent database/whiteboard edits cannot be reconciled safely

Never silently overwrite.

---

## 16.20 Trash, backups, quarantine, and recovery

Add:

* Recoverable Trash
* Backup before destructive mutation
* Conflict backups
* Corrupt-file quarantine
* Failed-import quarantine
* Partial-write recovery
* Restore UI
* Local operation journal
* Workspace repair tools
* Rebuild tools
* Data-integrity diagnostics

No hard deletion of user content through ordinary UI operations.

**Data Safety & Copy-Before-Transform Standard (MANDATORY):**
- Use disposable database and workspace copies for all tests.
- Create a timestamped backup before executing any destructive production migration or schema alteration.
- Wrap all migrations in transactions with foreign-key validation, migration journaling, idempotency checks, interrupted migration recovery, and non-empty destination protection.
- Never delete or overwrite original user data during migration or application execution.

---

## 16.21 Rebuildable search

Add complete rebuild commands and diagnostics:

* Delete index
* Scan workspace files
* Extract content
* Recreate entries
* Verify counts
* Report corrupt or unsupported files

---

## 16.22 Rebuildable graph

Add a simplified Obsidian-style graph:

* Stable UUID nodes
* Page nodes
* File nodes
* Database nodes
* Kanban nodes
* Whiteboard nodes
* Mind-map nodes
* Media nodes
* Tag nodes where useful
* Page graph
* Workspace graph
* Filters
* Search
* Local graph
* Global graph
* Regeneration from metadata

`graph.json` remains derived.

---

## 16.23 App-independent restoration

Add restoration after deletion of:

* AFFiNE databases
* Application database
* IndexedDB
* Search index
* Graph index
* Cache
* Session state
* Rebuildable previews

The app must reconstruct the workspace from ordinary files.

The renderer—not just backend tests—must display restored content.

---

## 16.24 Local-only security policy

Add enforcement that blocks:

* Cloud API calls
* Authentication endpoints
* GraphQL cloud endpoints
* Billing
* Analytics
* Telemetry
* Remote AI
* BYOK
* Updater calls
* Remote document services
* External network behavior not explicitly permitted

Allow:

* Local filesystem
* Local IPC
* Bundled child processes
* Loopback-only local Office/media services where necessary (WebSockets or HTTP over loopback are allowed ONLY for an owned bundled local service; external network WebSockets/HTTP are FORBIDDEN)

**External Browser Links Rule (FORBIDDEN in First Release):**
- No runtime external links, no automatic external links, no embedded remote pages, no webviews, and no `shell.openExternal` calls in production.
- Help and About content must be local and bundled.
- URLs may appear as plain text in legal notices or third-party attribution documents.

---

## 16.25 Packaging and runtime bundling

Add:

* Bundled Office runtime
* Bundled media probe/runtime
* Runtime discovery
* Health checks
* Clean-machine testing
* Portable testing
* Installed-app testing
* Offline launch testing
* Path relocation testing
* Installer resource validation
* Original-data preservation testing

**Platform Scope & Portable Archive Standard (MANDATORY / CONDITIONAL):**
- Windows installer and Windows offline launch proof are MANDATORY for the first release.
- Preserve valid macOS and Linux source and configuration; run platform builds only on suitable systems or CI runners. Record unavailable platform proof honestly without blocking the Windows release.
- Portable archive build is CONDITIONAL — VERIFY PRODUCT REQUIREMENT. Check authoritative requirements; keep an existing working portable target and test it if retained, but do not invent a portable archive as a new release obligation if not required.

---

## 16.26 Licence, attribution, and SBOM

Add:

* Complete dependency inventory
* Licence classification
* Redistribution analysis
* Third-party notices
* AFFiNE attribution
* BlockSuite attribution
* Office runtime attribution
* PDF/media library attribution
* Runtime binary attribution
* Software Bill of Materials
* Packaged notice verification

---

## 16.27 Large-file performance

Add or verify:

* Streaming file access
* No unnecessary full-file buffering
* Background workers
* Cancellation
* Progress reporting
* Virtualized views
* Large PDF behavior
* Large spreadsheet behavior
* Large video behavior
* Memory limits
* Resource cleanup
* Worker shutdown
* Long-session stability

---

## 16.28 Complete fixture QA

Test real files:

```text
sample.md
sample.pdf
sample.docx
sample.odt
sample.pptx
sample.odp
sample.xlsx
sample.ods
sample.csv
sample.jpg
sample.png
sample.webp
sample.mp4
corrupt.pdf
corrupt.docx
corrupt.xlsx
unsupported-media-file
large-video.mp4
```

For every applicable type, verify:

* Page import
* Workspace import
* Original preservation
* Metadata
* Preview
* Extraction
* Viewing
* Editing
* Save-back
* External edit
* External rename
* External delete
* Search update
* Graph update
* Restart
* Restore
* Conflict
* Corruption handling
* Unsupported behavior
* Offline behavior

The planned QA matrix explicitly requires real file fixtures, external edits, restart/restore, conflict handling, corrupt files, and offline verification. 

---

# 17. Repository and Engineering Additions

These are not end-user features, but they are required parts of the project.

## 17.1 Two-root structure

```text
project-root/
├─ Codebase/
└─ Graphify/
```

`Codebase/` contains executable application material.

`Graphify/` contains:

* Plans
* Specifications
* Graphify output
* Architecture maps
* Capability maps
* Exact-location registries
* Agent instructions
* Checkpoints
* Handoffs
* Reviews
* Test evidence
* Completion evidence
* AFFiNE reference source
* Processed Markdown snapshots

---

## 17.2 Capability-owned source organization

Every unique feature receives one authoritative home.

Planned capability folders include:

* Workspace
* Page bundles
* Workspace library
* Markdown storage
* File locator
* Universal import
* PDF
* PDF annotations
* Office engine
* Word
* PowerPoint
* Excel
* CSV
* Database
* Kanban
* Whiteboard
* Infinite canvas
* Mind map
* Knowledge graph
* Search
* Photos
* Videos
* Media metadata
* File watcher
* Sync journal
* Conflict resolution
* Atomic writes
* Backups
* Trash
* Restoration
* Graph rebuild
* Search rebuild
* Export
* Offline policy
* Network blocking
* Packaging
* Testing

This does not mean creating one folder per tiny function. Each function belongs to the smallest coherent capability module.

---

## 17.3 Graphify

Graphify is used to map:

* Files
* Symbols
* Imports
* Calls
* Runtime registrations
* Capabilities
* Current locations
* Target locations
* Ownership
* Dependencies
* Dependents
* Tests
* Blast radius
* Circular dependencies
* Dead-code candidates
* Duplicate implementations

Graphify plans and reports live outside the executable Codebase.

---

## 17.4 Ponytail

Ponytail is used after correctness and ownership are established.

It removes:

* Redundant wrappers
* Duplicate helpers
* Unnecessary abstraction layers
* Dead feature flags
* Pass-through services
* Duplicate validation
* Redundant state
* Unused dependencies
* Artificial indirection

It must not remove validation, safety, cleanup, types, readability, or error handling.

---

## 17.5 Agent swarm

The implementation process uses:

* Orchestrator agents
* Feature implementation agents
* Independent reviewer agents
* Repair agents
* Integration agents
* Data-survival agents
* Packaging agents
* Final release agents

Agent state persists so crashed sessions resume instead of restarting.

This is an engineering workflow, not a user-facing app feature.

---

# 18. Exact AFFiNE Copy Rule

Whenever the required implementation exists in the supplied AFFiNE source:

* Copy the complete coherent implementation
* Copy dependent types
* Copy state logic
* Copy tests
* Copy styles
* Copy assets
* Copy icons
* Copy workers
* Copy schemas
* Copy initialization
* Copy teardown behavior
* Copy required dependency declarations
* Preserve licence headers

Permitted changes are limited to:

* Import paths
* Package boundaries
* New product branding
* File-backed persistence adapters
* Offline dependency injection
* Local runtime lookup
* Removal of cloud boundaries
* Removal of authentication
* Removal of billing
* Removal of telemetry
* Removal of collaboration
* Packaging paths

The rule is:

> **Copy, do not imitate. Integrate, do not reinvent.**

---

---

# 19. Final Autonomous Convergence Loop (29-Step Deterministic Sequence)

### 19.1 Provenance-First Git Recovery Order
When `.git` is missing, empty, broken, or unusable:
1. Do not initialise Git immediately.
2. Preserve the working files.
3. Create a SHA-256 filesystem baseline.
4. Search parent directories for the actual repository root.
5. Search for worktrees, linked Git directories, and repository metadata.
6. Inspect project configuration for expected upstream origin.
7. Record whether original Git history can be recovered.
8. Continue repository-safe work using before-and-after hash manifests when necessary.
9. Initialise a new Git repository only when: original history cannot be recovered; repository provenance is documented; current files are backed up or hashed; the action will not conceal lost history; and the orchestrator records the decision.
10. Never claim recovered history if a new repository was created.

### 19.2 Git Safety
Continue to forbid: `git reset --hard`, `git clean -fd`, `git clean -xdf`, `git checkout .`, `git restore .`, force push, and history rewriting. Use `git revert` only when a valid repository and committed batch exist. Use manual repair and hash manifests when Git is unavailable.

### 19.3 Deterministic Execution Loop
Repeat until verified:
```text
1. Confirm repository root.
2. Read all three Master Plan files.
3. Inspect Git state.
4. Preserve existing user changes.
5. Run provenance-first Git recovery if Git is absent or broken.
6. Create path-specific ignore rules.
7. Create untouched baseline.
8. Record baseline failures.
9. Establish lean Graphify core.
10. Run baseline checks (using discovered repository commands).
11. Run initial Graphify deep scan.
12. Map capabilities and exact locations.
13. Classify keep/remove/replace/repair/add/conditional.
14. Correct active product identity.
15. Enforce runtime offline boundary.
16. Remove excluded systems one subsystem at a time (following 17-step canonical sequence).
17. Verify retained capabilities after each removal.
18. Repair damaged retained functionality.
19. Decompose monoliths only where responsibility evidence supports it.
20. Reorganise capability ownership incrementally.
21. Implement missing required local features.
22. Expand real integration tests on disposable file fixtures.
23. Build Windows application (using discovered repository commands).
24. Package Windows installer.
25. Test offline first launch and core workflows.
26. Run Ponytail after architecture stabilises.
27. Run final Graphify scan.
28. Apply the strict release gate and verify Final Release Receipt.
29. Continue until complete or genuinely externally blocked.
```

# 20. Final Release Gates and Machine-Verifiable Release Receipt

## 20.1 Mandatory Final Release Receipt Schema
Define `Graphify/11 Completion/FINAL_RELEASE_RECEIPT.json`. No completion banner or release claim is permitted unless all applicable gates are true and supported by documented, reproducible evidence matching this exact schema:
```json
{
  "project": "MindRoom",
  "status": "NOT_VERIFIED",
  "verificationTimestamp": null,
  "repositoryRevision": "",
  "repositoryEvidenceType": "GIT | HASH_MANIFEST",
  "gates": {
    "repositoryRootConfirmed": false,
    "twoRootStructureConfirmed": false,
    "zeroMarkdownInCodebase": false,
    "masterPlanRead": false,
    "fullGraphifyMappingComplete": false,
    "allSourceFilesClassified": false,
    "allCapabilitiesOwned": false,
    "allMeaningfulSymbolsMapped": false,
    "affinePreservationComplete": false,
    "transplantReceiptsComplete": false,
    "cloudPathsInactive": false,
    "accountPathsInactive": false,
    "teamPathsInactive": false,
    "billingPathsInactive": false,
    "aiPathsInactive": false,
    "telemetryPathsInactive": false,
    "externalRuntimeNetworkInactive": false,
    "fileBackedWorkspaceComplete": false,
    "appDeletionSurvivalPassed": false,
    "searchRebuildPassed": false,
    "graphRebuildPassed": false,
    "typecheckPassed": false,
    "lintPassed": false,
    "unitTestsPassed": false,
    "integrationTestsPassed": false,
    "e2eTestsPassed": false,
    "rendererBuildPassed": false,
    "electronBuildPassed": false,
    "productionBuildPassed": false,
    "packagingPassed": false,
    "windowsInstallerLaunchPassed": false,
    "offlineVerificationPassed": false,
    "fixtureMatrixPassed": false,
    "licenceAuditComplete": false,
    "attributionComplete": false,
    "sbomComplete": false,
    "independentReviewApproved": false
  },
  "evidenceReceipts": [],
  "allGatesPassed": false,
  "completionBannerUnlocked": false
}
```

**Release Receipt Rules:**
- Every gate must reference an evidence receipt.
- Every evidence receipt must record the actual command, working directory, exit code, timestamp, and relevant output.
- Do not assume `npm`, `pnpm`, `yarn`, or another package manager. Discover and record the real repository commands.
- The completion banner is forbidden unless all applicable gates are true.
- A missing gate means release rejection.

## 20.2 Release Completion Verdicts

MindRoom is complete only when all applicable gates in `FINAL_RELEASE_RECEIPT.json` pass simultaneously.

**Strict Release Conjunction (MANDATORY):**
Completion requires all applicable gates to pass simultaneously, including: Plan mapping, keep verification, deletion verification, replacement implementation, addition implementation, Codebase/Graphify separation, zero tracked Markdown in Codebase, exact-location registry current, no stale IPC, no stale preload APIs, no active cloud code, no active external runtime network, real SQLite/persistence tests, real integration tests, typecheck, lint, renderer build, Electron build, Windows packaging, Windows installer launch, offline workflow proof, final Graphify scan, and accurate handoff.

If any gate is not proven by a valid automated receipt or test assertion:
```text
PROJECT NOT COMPLETE — RELEASE REJECTED
```

Only when every single gate is supported by documented, reproducible evidence in `Graphify/11 Completion/FINAL_RELEASE_RECEIPT.json`:
```text
PROJECT COMPLETE — FINAL ARCHITECTURE VERIFIED
```

No intermediate, informal, or approximate completion claims are permitted.
<!-- mindroom-product-expansion-20260729-155104:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-product-expansion-20260729-155104`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-130207:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130207`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-130301:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130301`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-130347:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130347`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-130433:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130433`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-130534:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130534`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-130637:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130637`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-131323:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-131323`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-131954:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-131954`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-132635:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-132635`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-133353:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-133353`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-134102:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-134102`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-134744:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-134744`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-135536:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-135536`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-140415:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-140415`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-141300:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-141300`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-141342:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-141342`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-142249:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-142249`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-143506:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-143506`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 21.1 Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 21.2 Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.2.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 21.2.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 21.2.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 21.2.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 21.2.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 21.2.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 21.3 Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 21.3.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 21.3.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 21.3.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 21.3.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 21.3.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 21.3.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 21.3.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 21.3.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 21.4 Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 21.4.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 21.4.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 21.4.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 21.4.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 21.4.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 21.4.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 21.4.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 21.5 Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 21.6 Calendar Requirements

Create formal requirement and capability records for the following.

### 21.6.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 21.6.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 21.6.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 21.6.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 21.6.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 21.6.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 21.6.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 21.6.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 21.6.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 21.6.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 21.7 Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 21.7.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 21.7.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 21.7.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 21.7.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 21.7.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 21.7.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 21.7.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 21.7.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 21.7.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 21.7.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 21.7.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 21.7.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 21.7.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 21.8 Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 21.9 Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 21.10 Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 21.11 Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 21.11.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 21.11.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 21.11.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 21.11.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 21.11.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 21.12 New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 21.13 Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21.14 Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 21.15 Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 21.16 Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 21.17 Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 21.18 Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 21.19 Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.

<!-- mindroom-graphify-forensic-finalization-20260730-150956:ADDITIVE-PRODUCT-EXPANSION -->

# 21. MindRoom Product Expansion Architecture and Execution Plan (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-150956`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add deterministic implementation procedures for every new capability.

Include:

* source-exact discovery;
* capability ownership;
* stable identity design;
* target folder design;
* migration requirements;
* file formats;
* dependency order;
* required tests;
* failure recovery;
* offline validation;
* app-deletion recovery;
* independent review;
* no-reinvention search receipts;
* Graphify update requirements.

Do not mark any implementation step complete.

---

## 8. Required Product Hierarchy

Formalise this ownership model:

```text
MindRoom
└── Workspace
    ├── Workspace Home Canvas
    ├── Workspace Mind Maps
    ├── Workspace Global Knowledge Map
    ├── Folder
    │   ├── Folder Home Canvas
    │   ├── Folder Knowledge Map
    │   ├── Independent Whiteboards
    │   ├── Independent Mind Maps
    │   ├── Notes
    │   ├── Databases
    │   ├── Calendar Items
    │   ├── Finance Items
    │   └── Files
    └── Other folders and independent documents
```

Define these distinct ownership levels:

```text
PAGE
FOLDER
FOLDER_AND_DESCENDANTS
WORKSPACE
SELECTED_SOURCES
GLOBAL_MULTI_WORKSPACE_OPTIONAL
```

The initial release does not need to expose multi-workspace global aggregation unless separately approved.

The architecture must not prevent it later.

---

## 9. Canvas and Whiteboard Requirements

Create dedicated requirements and capabilities for all of the following.

### 9.1 Independent whiteboard documents

Each whiteboard must:

* have its own stable ID;
* have its own content;
* have its own history;
* have its own owner;
* have its own parent folder;
* have its own preview;
* have its own assets;
* be exportable;
* be recoverable;
* be movable without breaking references;
* be independently viewable and editable.

### 9.2 Folder Home Canvas

Every folder may optionally have one designated Folder Home Canvas.

It must:

* belong to one folder;
* serve as a visual entrance to that folder;
* optionally include descendant folders;
* support manually arranged content;
* support dynamic folder-content blocks;
* remain a normal canvas document with special metadata;
* not require a separate canvas engine;
* remain independently exportable;
* remain recoverable if MindRoom is deleted.

Possible default folder views must include:

```text
LIST
GRID
DATABASE
KANBAN
CALENDAR
CANVAS
```

The user may select the default view.

### 9.3 Workspace Home Canvas

Every workspace may optionally have one Workspace Home Canvas.

It must:

* represent workspace-level projects, folders, deadlines, maps, and dashboards;
* be editable independently;
* link to any item in the workspace;
* embed folder-level canvases or previews without copying their source content;
* remain portable and recoverable.

### 9.4 Canvas scope

Each canvas must support one explicit source scope:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

Canvas ownership and canvas source scope are separate concepts.

A canvas may live in one folder while referencing items elsewhere.

### 9.5 Canvas movement

Moving a canvas must:

* preserve its stable ID;
* preserve its content;
* preserve backlinks;
* preserve incoming references;
* update its parent folder;
* update structural relationships;
* update folder-generated views;
* not duplicate the canvas;
* not orphan its assets.

### 9.6 Canvas file-backed persistence

Plan a durable representation such as:

```text
canvas-{uuid}-{slug}/
├─ canvas.json
├─ metadata.json
├─ preview.svg
├─ relationship-index.json
└─ assets/
```

Or a transparent bundle format such as:

```text
{name}.mindcanvas
```

The exact final format must be selected through a documented architecture decision.

The editable canvas must not survive solely in an opaque internal database.

---

## 10. Mind-Map Requirements

Create dedicated requirements and capabilities for all of the following.

### 10.1 Independent mind-map documents

Each mind map must:

* have a stable ID;
* have an explicit owner;
* have an explicit parent folder;
* remain independently editable;
* remain independently exportable;
* remain independently recoverable;
* preserve node IDs;
* preserve layout;
* preserve relationships;
* preserve collapsed state where supported;
* preserve style;
* preserve attachments;
* preserve cross-folder references.

### 10.2 Page-scoped mind maps

A mind map may belong to one page or document.

Its nodes may reference:

* headings;
* blocks;
* linked notes;
* external files;
* database records;
* tasks;
* calendar events;
* financial records.

### 10.3 Folder-scoped mind maps

A folder may have:

* one designated Folder Knowledge Map;
* unlimited independent mind maps;
* generated structural views;
* manually designed hierarchical maps.

A Folder Knowledge Map may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
```

### 10.4 Workspace mind maps

A workspace may contain manually created workspace-level mind maps.

These remain independent documents.

### 10.5 Workspace Global Knowledge Map

Each workspace may expose a computed Global Knowledge Map.

This must not be one enormous duplicated mind-map document.

It must be a federated, rebuildable view derived from:

* folder maps;
* independent mind maps;
* pages;
* folders;
* explicit links;
* backlinks;
* tags;
* embeds;
* database relations;
* whiteboard references;
* calendar relationships;
* finance relationships;
* accepted semantic relationships.

### 10.6 Federated aggregation

Local maps remain authoritative independent sources.

The global map must:

* display local maps together;
* preserve map boundaries;
* display folder clusters;
* support opening a source map separately;
* reflect edits to source maps;
* avoid copying source nodes into a second authoritative map;
* avoid creating conflicting duplicate ownership;
* preserve provenance for every displayed node and edge;
* allow users to hide a source from the global view without deleting it;
* allow users to exclude specific relationships from aggregation.

### 10.7 Map-of-maps navigation

The global map must support:

* entering one folder cluster;
* opening one independent map;
* returning to the global map;
* expanding or collapsing folders;
* filtering by source map;
* filtering by folder;
* filtering by relationship type;
* filtering by tags;
* filtering by date;
* filtering by capability;
* filtering by confirmation state.

### 10.8 Mind-map file-backed persistence

Plan a durable representation such as:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ preview.svg
├─ relationships.json
└─ assets/
```

The global knowledge map should normally be reconstructed from source files and relationship indexes rather than stored as a duplicated authoritative copy.

---

## 11. Knowledge-Linking Model

Create a formal relationship taxonomy.

Every relationship must have:

* stable relationship ID;
* source node ID;
* target node ID;
* direction;
* relationship type;
* origin;
* provenance;
* confidence where applicable;
* creation timestamp;
* updated timestamp;
* confirmation state;
* owning workspace;
* source file;
* source anchor where applicable;
* visibility;
* inclusion or exclusion from global views;
* deletion and recovery behavior.

### 11.1 Automatic structural relationships

These are derived automatically from storage and ownership.

Examples:

```text
FILE_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_FOLDER
FOLDER_BELONGS_TO_WORKSPACE
CANVAS_BELONGS_TO_FOLDER
MIND_MAP_BELONGS_TO_FOLDER
EVENT_BELONGS_TO_CALENDAR
TRANSACTION_BELONGS_TO_ACCOUNT
RECEIPT_ATTACHED_TO_TRANSACTION
```

Structural relationships require no manual user linking.

They must update when items move.

They must be rebuildable from file metadata.

### 11.2 Explicit links and backlinks

Explicit links may be created from:

* wiki links;
* document links;
* block references;
* embeds;
* database relation fields;
* whiteboard connectors;
* mind-map node references;
* calendar associations;
* finance associations.

When the user creates one explicit link, MindRoom must automatically create or derive the corresponding backlink index.

The user must not manually create the reverse backlink.

### 11.3 Semantic link suggestions

MindRoom may suggest relationships based on local content similarity.

Requirements:

* local-only by default;
* no remote API requirement;
* no generative AI requirement;
* explain why a relationship was suggested;
* record supporting terms, embeddings, tags, metadata, or shared references;
* assign confidence;
* allow acceptance;
* allow rejection;
* allow dismissal;
* allow “never suggest this relationship again”;
* allow disabling semantic suggestions;
* never silently create permanent conceptual truth;
* never alter source documents merely to establish a suggestion.

Allowed states:

```text
SUGGESTED
ACCEPTED
REJECTED
DISMISSED
EXPIRED
SUPERSEDED
```

When accepted, a semantic suggestion becomes a confirmed relationship while preserving its semantic origin.

### 11.4 Manual conceptual relationships

Users may manually create relationships that are meaningful even when file structure or semantic similarity cannot infer them.

Manual links must:

* remain permanent until removed;
* preserve custom labels;
* preserve direction;
* support optional notes;
* support optional relationship type;
* appear in backlinks and global views;
* survive file movement.

### 11.5 Temporary contextual relationships

Search relevance or temporary session similarity must not automatically become permanent graph relationships.

Classify these as ephemeral:

```text
SEARCH_CONTEXT
SESSION_CONTEXT
RECENTLY_VIEWED_TOGETHER
TEMPORARY_RELEVANCE
```

Do not persist them as permanent knowledge unless the user confirms them.

### 11.6 Relationship types

At minimum, support:

```text
STRUCTURAL
EXPLICIT
BACKLINK
EMBED
DATABASE_RELATION
WHITEBOARD_CONNECTOR
MIND_MAP_PARENT_CHILD
MIND_MAP_REFERENCE
CALENDAR_ASSOCIATION
FINANCE_ASSOCIATION
CONFIRMED_SEMANTIC
SUGGESTED_SEMANTIC
MANUAL_CONCEPTUAL
TEMPORARY_CONTEXTUAL
```

### 11.7 Global graph filters

The global view must support filtering by:

* relationship type;
* structural versus conceptual;
* automatic versus manual;
* confirmed versus suggested;
* folder;
* source map;
* file type;
* tags;
* date;
* confidence;
* workspace;
* calendar;
* finance;
* whiteboard;
* mind map;
* recent changes;
* orphaned nodes;
* unresolved references.

---

## 12. Stable Identity Requirements

Paths must not be the primary permanent identity.

Every durable item must receive a stable UUID or equivalent stable ID.

Required item identities include:

* workspace;
* folder;
* page;
* block;
* database;
* database record;
* canvas;
* whiteboard element;
* mind map;
* mind-map node;
* calendar;
* event;
* reminder;
* task;
* financial account;
* transaction;
* transfer;
* budget;
* savings goal;
* receipt;
* relationship.

Moving or renaming a file must not break:

* backlinks;
* map nodes;
* canvas embeds;
* calendar associations;
* finance associations;
* database relations;
* accepted semantic links.

Record historical paths as aliases where useful.

---

## 13. Calendar Requirements

Create formal requirement and capability records for the following.

### 13.1 Local Calendar Core

MindRoom must include a local-first calendar that works fully offline.

It must not require:

* AFFiNE Cloud;
* Google Calendar;
* CalDAV;
* GraphQL;
* remote accounts;
* network access.

### 13.2 Calendar ownership and scope

Support:

* workspace calendars;
* folder-specific calendars;
* selected-source calendar views;
* global workspace calendar view;
* calendar filters;
* calendar items linked to notes, projects, maps, boards, and financial records.

A folder calendar may display:

```text
THIS_FOLDER_ONLY
THIS_FOLDER_AND_DESCENDANTS
SELECTED_SOURCES
ENTIRE_WORKSPACE
```

### 13.3 Events

Plan support for:

* titled events;
* descriptions;
* start and end time;
* all-day events;
* location;
* status;
* tags;
* attachments;
* linked notes;
* linked folders;
* linked tasks;
* linked finance records;
* stable event IDs;
* local persistence;
* export;
* recovery.

### 13.4 Recurrence

Plan support for:

* daily recurrence;
* weekly recurrence;
* monthly recurrence;
* yearly recurrence;
* custom intervals;
* selected weekdays;
* recurrence end date;
* occurrence count;
* excluded dates;
* edited single occurrences;
* edited future occurrences;
* recurrence-series identity.

Use a standards-compatible recurrence representation where appropriate.

### 13.5 Time zones

Plan for:

* local time zone;
* explicit event time zones;
* floating times where appropriate;
* daylight-saving changes;
* all-day semantics;
* imported time zones;
* workspace default time zone.

### 13.6 Reminders and notifications

Plan support for:

* one or multiple reminders;
* relative reminders;
* absolute reminders;
* local desktop notifications;
* snooze;
* dismiss;
* overdue state;
* reminder recovery after restart;
* no cloud requirement.

### 13.7 Tasks and deadlines

Tasks with dates must appear in calendar views.

Calendar events may link to tasks without becoming the same data entity.

Support:

* due date;
* start date;
* completion;
* overdue state;
* recurring tasks;
* folder and project ownership;
* calendar projection.

### 13.8 Journal integration

Daily notes and journals may display:

* events for the day;
* tasks due;
* finance activity;
* linked notes;
* recently edited files.

Creating a journal entry must not automatically create a calendar event unless the user requests it.

### 13.9 ICS import and export

Plan support for:

* `.ics` import;
* `.ics` export;
* calendar-level export;
* event-level export;
* duplicate detection;
* stable UID handling;
* recurrence;
* time zones;
* unsupported-field preservation where possible.

### 13.10 Optional external calendar adapters

Plan, but do not require for the first local core:

* CalDAV;
* Google Calendar;
* system calendar integration;
* read-only subscribed calendars.

These must be optional adapters.

They must not become the source of truth for local MindRoom calendar data.

External sync conflict behavior must be mapped separately.

---

## 14. Finance Requirements

Create formal requirement and capability records for the following.

MindRoom Finance is a local personal-finance workspace.

It is not AFFiNE billing.

### 14.1 Finance Core

Finance must work locally and offline.

No finance feature may require:

* AFFiNE Cloud;
* Stripe;
* RevenueCat;
* remote billing;
* remote AI;
* telemetry;
* bank credentials in the first core implementation.

### 14.2 Financial accounts

Plan support for:

* cash;
* bank;
* credit card;
* savings;
* investment;
* loan;
* debt;
* custom accounts;
* opening balance;
* current balance;
* archived accounts;
* account notes;
* account attachments;
* stable account IDs.

### 14.3 Transactions

Plan support for:

* income;
* expense;
* adjustment;
* refund;
* transaction date;
* posting date;
* amount;
* currency;
* category;
* tags;
* merchant or payee;
* notes;
* attachments;
* linked calendar event;
* linked project;
* linked folder;
* linked person;
* stable transaction ID.

### 14.4 Transfers

Transfers must be represented as linked financial movements, not unrelated duplicate transactions.

Plan:

* source account;
* destination account;
* transfer amount;
* currency handling;
* transfer fees;
* linked transaction IDs;
* reconciliation;
* reversal.

### 14.5 Categories and tags

Support:

* hierarchical categories;
* custom categories;
* tags;
* category budgets;
* category reports;
* category reassignment;
* archived categories.

### 14.6 Recurring bills and income

Plan support for:

* recurring expenses;
* recurring income;
* bills;
* subscriptions paid by the user;
* salary;
* rent;
* instalments;
* recurrence rules;
* expected amount;
* variable amount;
* due date;
* reminders;
* paid status;
* skipped occurrence;
* calendar projection.

Do not confuse user subscriptions with AFFiNE subscription billing.

### 14.7 Budgets

Plan support for:

* monthly budgets;
* category budgets;
* custom periods;
* planned versus actual;
* rollover as an optional later setting;
* warning thresholds;
* linked transactions;
* local calculations;
* export.

### 14.8 Savings goals

Plan support for:

* target amount;
* current amount;
* target date;
* linked account;
* linked transactions;
* progress;
* calendar deadline;
* notes;
* attachments.

### 14.9 Receipts and financial attachments

Receipts may be attached to transactions.

Plan:

* original file preservation;
* image and PDF support;
* checksum;
* preview;
* optional local text extraction later;
* no remote OCR requirement;
* file ownership;
* export;
* recovery.

### 14.10 Financial dashboards

Plan views for:

* transaction table;
* account dashboard;
* monthly calendar;
* budget view;
* recurring-bills timeline;
* category breakdown;
* savings goals;
* basic net worth;
* cash-flow summary.

Do not mandate advanced investment analytics in the initial core.

### 14.11 CSV import and export

Plan:

* account import;
* transaction import;
* column mapping;
* date-format mapping;
* currency mapping;
* duplicate detection;
* dry run;
* rollback;
* import receipt;
* export to ordinary files.

### 14.12 Multi-currency foundation

Plan a data model that can store original transaction currency.

Do not require live exchange-rate services for the local core.

Optional later exchange-rate adapters must be isolated.

### 14.13 Finance privacy

Plan:

* local storage;
* optional local encryption;
* redacted previews;
* lockable finance spaces;
* no telemetry payloads containing financial data;
* no remote semantic processing;
* secure deletion behavior where technically possible;
* clear backup and recovery behavior.

---

## 15. Calendar–Finance Integration

Create explicit requirements for integration between calendar and finance.

Examples:

* bills appear on the calendar;
* salary dates appear as recurring calendar projections;
* user subscriptions create upcoming-payment reminders;
* budget review dates appear as events or tasks;
* savings goals may have target dates;
* transactions may be viewed through monthly calendar views;
* overdue bills may appear in tasks;
* an event may link to related expenses;
* a trip event may link to a travel budget;
* a project deadline may link to project spending.

The calendar and finance records remain distinct entities connected through stable relationships.

Do not merge all financial transactions into calendar events.

---

## 16. Required New Capabilities

The current capability registry contains 110 capabilities.

Do not reuse existing capability IDs.

Allocate new sequential capability IDs beginning after the highest valid existing ID.

Create distinct capability records for at least the following domains.

Split further only where independent ownership, testing, or release behavior requires it.

```text
Local Calendar Core
Calendar Ownership and Scoped Views
Calendar Events
Calendar Recurrence
Calendar Time Zones
Calendar Reminders and Notifications
Task and Deadline Calendar Integration
Journal Calendar Integration
ICS Import and Export
Optional External Calendar Adapters

MindRoom Finance Core
Financial Accounts
Transactions and Transfers
Finance Categories and Tags
Recurring Bills and Income
Budgets
Savings Goals
Receipts and Financial Attachments
Financial Dashboards
Finance CSV Import and Export
Multi-Currency Foundation
Finance Privacy and Local Protection
Calendar–Finance Integration

Canvas Ownership and Scoping
Independent Whiteboard Documents
Folder Home Canvas
Workspace Home Canvas
Dynamic Folder-Content Canvas Blocks
Canvas Movement and Stable Identity
Canvas File Persistence and Asset Ownership
Cross-Folder Canvas References

Independent Mind-Map Documents
Page-Scoped Mind Maps
Folder-Scoped Mind Maps
Workspace Mind Maps
Folder Knowledge Map
Workspace Global Knowledge Map
Federated Mind-Map Aggregation
Map-of-Maps Navigation
Mind-Map File Persistence
Mind-Map Projection into Knowledge Graph

Automatic Structural Relationships
Explicit Links and Automatic Backlinks
Local Semantic-Link Suggestions
Semantic-Link Review and Confirmation
Manual Conceptual Relationships
Temporary Contextual Relationships
Relationship Provenance and Confidence
Global Knowledge-Graph Filters
Stable Identity Across File Movement
Knowledge-Graph Reconstruction and Recovery
```

Do not collapse these into one vague capability called “Knowledge Graph.”

---

## 17. Required Requirement Records

Create one or more requirement records for every behavior defined in this prompt.

Every requirement must contain:

```json
{
  "requirementId": "MR-REQ-...",
  "title": "",
  "description": "",
  "source": "PRODUCT_EXPANSION_2026",
  "priority": "",
  "releaseWave": "",
  "capabilityIds": [],
  "acceptanceCriteria": [],
  "forbiddenBehaviours": [],
  "offlineRequirement": "",
  "fileBackedRequirement": "",
  "privacyRequirement": "",
  "recoveryRequirement": "",
  "testRequirements": [],
  "status": "MAPPED"
}
```

No requirement may terminate at a capability name without:

* current source evidence;
* current-location status;
* exact required change;
* future target;
* dependencies;
* tests;
* validation evidence.

---

## 18. Source-Exact AFFiNE Discovery

Run semantic source inspection for the reusable foundations.

### 18.1 Calendar searches

Inspect:

* database calendar view model;
* calendar rendering;
* layout;
* drag and drop;
* event positioning;
* calendar actions;
* date-picker components;
* journal calendar events;
* local event models;
* GraphQL calendar schemas;
* backend calendar integrations;
* CalDAV;
* Google Calendar;
* tests;
* registrations;
* storage boundaries;
* cloud dependencies.

Do not assume all files under a calendar folder belong to local calendar core.

### 18.2 Canvas and whiteboard searches

Inspect:

* Edgeless root;
* surface model;
* rendering;
* canvas document model;
* shape storage;
* connector storage;
* group storage;
* frame storage;
* embed references;
* clipboard;
* previews;
* export;
* persistence;
* document ownership;
* workspace ownership;
* existing folder or collection relationships;
* tests.

Distinguish HTML canvas utilities from MindRoom whiteboard architecture.

### 18.3 Mind-map searches

Inspect the real BlockSuite mind-map model, GFX package, rendering, layout, interaction, adapters, serialization, import, export, and tests.

Exclude AI mind-map generation from the retained foundation.

### 18.4 Finance searches

Search for genuinely reusable:

* database tables;
* formulas;
* numeric field types;
* currency display utilities;
* CSV utilities;
* attachment handling;
* charts;
* local persistence;
* encryption;
* import and export;
* transaction-like neutral abstractions.

Treat billing, subscription, invoices, Stripe, RevenueCat, and monetisation modules as excluded-system evidence unless a small neutral utility is source-proven reusable.

### 18.5 Knowledge-link searches

Inspect:

* document links;
* backlinks;
* block references;
* stable IDs;
* tags;
* database relations;
* synced-doc references;
* embeds;
* folder ownership;
* workspace ownership;
* search index;
* semantic-search code;
* local indexing;
* cloud AI coupling;
* graph relationships.

Do not map AI search result UI as the authoritative rebuildable search engine.

---

## 19. New Exact-Change Records

Create one `CHANGE_LOCATION_REGISTRY.jsonl` record for every new capability and major architectural requirement.

Each record must contain:

```json
{
  "changeId": "MR-CHANGE-...",
  "requirementIds": [],
  "capabilityId": "",
  "changeType": "KEEP | WRAP | ADAPT | ADD | REMOVE | VERIFY | ARCHITECTURE_DECISION",
  "currentLocationStatus": "",
  "currentPaths": [],
  "currentSymbols": [],
  "currentAnchors": [],
  "evidenceClassification": [],
  "targetPaths": [],
  "targetOwner": "",
  "exactRequiredChange": "",
  "preserve": [],
  "removeLater": [],
  "addLater": [],
  "forbiddenChanges": [],
  "dependencies": [],
  "dependants": [],
  "runtimeRegistrations": [],
  "storageContracts": [],
  "relationshipContracts": [],
  "testsRequired": [],
  "fixturesRequired": [],
  "verificationReceiptsRequired": [],
  "rollbackRequirements": [],
  "riskLevel": "",
  "blockers": [],
  "releaseWave": "",
  "status": "MAPPED",
  "reviewStatus": ""
}
```

Do not put twelve arbitrary candidate paths into every change record.

Use all and only the semantically relevant roots.

---

## 20. Target Architecture Planning

Update the target Codebase tree and folder-ownership artifacts.

Do not create these folders in Codebase during this phase.

Plan coherent target owners for concepts such as:

```text
packages/frontend/core/src/modules/mindroom-calendar/
packages/frontend/core/src/modules/mindroom-finance/
packages/frontend/core/src/modules/mindroom-canvas-scope/
packages/frontend/core/src/modules/mindroom-knowledge-graph/
packages/frontend/core/src/modules/mindroom-relationships/
packages/common/src/mindroom/calendar/
packages/common/src/mindroom/finance/
packages/common/src/mindroom/relationships/
packages/common/src/mindroom/stable-identity/
```

These paths are planning candidates.

Inspect existing package boundaries before finalising them.

Prefer existing coherent package ownership where appropriate.

Do not create duplicate engines beside BlockSuite.

Canvas and mind-map target modules should add ownership, persistence, federation, and application integration around retained BlockSuite implementations.

---

## 21. Architecture Decision Records

Create planning ADRs under Graphify for unresolved architectural choices.

At minimum:

```text
Graphify/12 Source Documents/Architecture Decisions/
```

Create ADRs for:

1. Canonical file-backed source of truth.
2. Canvas bundle format.
3. Mind-map bundle format.
4. Global graph as computed projection versus persisted cache.
5. Stable ID generation and path aliases.
6. Local semantic-index technology.
7. Semantic suggestion persistence.
8. Calendar recurrence representation.
9. Calendar file format and ICS compatibility.
10. Finance transaction storage format.
11. Finance encryption boundaries.
12. Multi-currency behavior.
13. External calendar adapter boundaries.
14. Folder and workspace inheritance behavior.

Where the product decision is already specified by this prompt, record it as accepted.

Where a technical choice still requires benchmarking, record:

```text
PROPOSED
IMPLEMENTATION_BLOCKED_PENDING_DECISION
```

Do not invent technical certainty merely to turn a gate green.

---

## 22. Release-Wave Planning

Add a realistic implementation roadmap.

The architecture must support the full product vision, but implementation must be phased.

### Wave 0 — Data and identity foundation

* stable IDs;
* ownership model;
* folder and workspace scope;
* file-backed contracts;
* relationship schema;
* recovery rules;
* graph reconstruction;
* baseline migration architecture.

### Wave 1 — Scoped canvas and mind-map foundation

* independent whiteboards;
* folder ownership;
* workspace ownership;
* Folder Home Canvas;
* Workspace Home Canvas;
* independent mind maps;
* folder mind maps;
* workspace mind maps;
* global federated map;
* explicit links;
* backlinks;
* structural relationships.

### Wave 2 — Local Calendar Core

* events;
* calendar views;
* scoped calendars;
* tasks and deadlines;
* reminders;
* recurrence;
* journal integration;
* ICS import and export.

### Wave 3 — Finance Core

* accounts;
* transactions;
* transfers;
* categories;
* recurring bills and income;
* basic budgets;
* calendar projections;
* CSV import and export;
* receipts.

### Wave 4 — Knowledge Intelligence

* local semantic index;
* semantic suggestions;
* explanation;
* accept and reject;
* confidence;
* graph filters;
* advanced federation.

### Wave 5 — Advanced Finance and Optional Integrations

* savings goals;
* dashboards;
* multi-currency enhancements;
* optional encryption improvements;
* CalDAV;
* Google Calendar;
* system calendar integration;
* optional exchange-rate adapters.

No Wave 2–5 capability may bypass Wave 0 identity and persistence foundations.

---

## 23. Test and Verification Planning

Update all relevant verification artifacts.

Plan tests for:

### Canvas

* folder ownership;
* workspace ownership;
* moving between folders;
* stable IDs;
* backlinks after movement;
* assets after movement;
* Folder Home Canvas;
* Workspace Home Canvas;
* scoped dynamic blocks;
* export;
* recovery;
* app-deletion survival.

### Mind maps

* independent editing;
* folder map;
* global aggregation;
* no duplication;
* source-map update propagation;
* map filtering;
* stable node IDs;
* cross-folder references;
* export;
* recovery;
* accepted semantic links;
* rejected suggestions;
* source provenance.

### Calendar

* offline creation;
* event editing;
* all-day events;
* recurrence;
* exceptions;
* time zones;
* daylight-saving behavior;
* reminders;
* restart recovery;
* task projection;
* journal integration;
* ICS import;
* ICS export;
* duplicate detection;
* folder-scoped views;
* workspace global view.

### Finance

* account balances;
* income;
* expenses;
* transfers;
* transfer reversal;
* categories;
* recurring transactions;
* bills;
* calendar reminders;
* budgets;
* receipts;
* CSV dry run;
* CSV import;
* duplicate detection;
* rollback;
* export;
* multi-currency storage;
* privacy;
* app-deletion survival.

### Knowledge relationships

* structural links;
* explicit backlinks;
* semantic suggestions;
* no silent acceptance;
* rejection persistence;
* manual conceptual links;
* temporary relationship non-persistence;
* movement without broken links;
* reconstruction from files;
* provenance;
* graph filters.

Add fixtures for:

* nested folders;
* moved folders;
* renamed files;
* missing attachments;
* corrupted canvas bundle;
* corrupted mind-map bundle;
* recurring calendar events;
* time-zone changes;
* transfer pairs;
* duplicate CSV imports;
* semantic false positives;
* rejected semantic suggestions;
* mixed explicit and automatic relationships.

---

## 24. Update Every Affected Graphify Artifact

At minimum, update or regenerate:

```text
Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md
Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md
Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT.md

Graphify/15 Processed Plan Snapshots/
Graphify/15 Processed Plan Snapshots/MASTER_PLAN_MANIFEST.json

Graphify/03 Capability Map/CAPABILITY_REGISTRY.json
Graphify/03 Capability Map/REQUIREMENT_REGISTRY.jsonl
Graphify/03 Capability Map/REQUIREMENT_TRACEABILITY_MATRIX.jsonl
Graphify/03 Capability Map/CAPABILITY_SOURCE_SEARCH_RECEIPTS.jsonl
Graphify/03 Capability Map/CAPABILITY_EVIDENCE.jsonl
Graphify/03 Capability Map/CAPABILITY_DEPENDENCY_ORDER.json
Graphify/03 Capability Map/CAPABILITY_MAP.md

Graphify/04 Exact Location Registry/EXACT_LOCATION_REGISTRY.json
Graphify/04 Exact Location Registry/CHANGE_LOCATION_REGISTRY.jsonl
Graphify/04 Exact Location Registry/CHANGE_TRACEABILITY_MATRIX.jsonl
Graphify/04 Exact Location Registry/EXACT_LOCATION_COVERAGE.json

Graphify/05 Dependency and Impact/DEPENDENCY_EDGES.jsonl
Graphify/05 Dependency and Impact/CAPABILITY_DEPENDENCY_GRAPH.json
Graphify/05 Dependency and Impact/RUNTIME_REACHABILITY_REPORT.jsonl
Graphify/05 Dependency and Impact/REORGANISATION_BLAST_RADIUS.jsonl
Graphify/05 Dependency and Impact/Knowledge Graph/

Graphify/06 Folder Ownership/FOLDER_OWNERSHIP_MATRIX.json
Graphify/06 Folder Ownership/CAPABILITY_TO_PATH_MAP.json
Graphify/06 Folder Ownership/TARGET_CODEBASE_TREE.md
Graphify/06 Folder Ownership/PACKAGE_BOUNDARY_PLAN.md
Graphify/06 Folder Ownership/PUBLIC_ENTRYPOINT_PLAN.jsonl

Graphify/07 Reorganisation/REORGANISATION_LEDGER.jsonl
Graphify/07 Reorganisation/MOVE_PLAN.jsonl
Graphify/07 Reorganisation/BATCH_EXECUTION_PLAN.md
Graphify/07 Reorganisation/IMPORT_AND_CONFIG_UPDATE_MATRIX.jsonl
Graphify/07 Reorganisation/ROLLBACK_PLAN.jsonl

Graphify/09 Implementation/IMPLEMENTATION_QUEUE.md
Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl
Graphify/09 Implementation/ADAPTATION_TASKS.jsonl
Graphify/09 Implementation/NEW_CAPABILITY_TASKS.jsonl
Graphify/09 Implementation/TRANSPLANT_SEARCH_QUEUE.jsonl

Graphify/10 Verification/REQUIREMENT_TEST_MATRIX.jsonl
Graphify/10 Verification/FIXTURE_QA_MATRIX.md
Graphify/10 Verification/RELEASE_GATE_MATRIX.json
Graphify/10 Verification/OFFLINE_TEST_PLAN.md
Graphify/10 Verification/APP_DELETION_SURVIVAL_TEST_PLAN.md

Graphify/11 Completion/COMPLETION_TRACKER.md
Graphify/11 Completion/CAPABILITY_MATRIX.md
Graphify/11 Completion/REQUIREMENT_COVERAGE_REPORT.md
Graphify/11 Completion/CODEBASE_MAP.md
Graphify/11 Completion/GRAPHIFY_MAPPING_RECEIPT.json
Graphify/11 Completion/GLOBAL_VALIDATION_RESULT.json
Graphify/11 Completion/GRAPHIFY_FINAL_AUDIT.md
Graphify/11 Completion/UNRESOLVED_MAPPING_ISSUES.md
Graphify/11 Completion/FINAL_HANDOFF.md
```

Search for all derived artifacts containing:

* old Master Plan hashes;
* capability count `110`;
* old requirement counts;
* old completion run IDs;
* stale dependency order;
* stale implementation order;
* stale “Graphify complete” claims.

Regenerate them or mark them superseded.

Do not manually patch only the summary documents.

---

## 25. Graph Relationship Types to Add

Extend the directed knowledge graph to support relationship types such as:

```text
OWNS
BELONGS_TO
CONTAINS
SCOPED_TO
INCLUDES_DESCENDANTS
REFERENCES
BACKLINK_FROM
EMBEDS
CONNECTED_ON_CANVAS
PARENT_OF_MINDMAP_NODE
PROJECTS_INTO_GLOBAL_MAP
DERIVED_FROM_SOURCE_MAP
LINKED_TO_EVENT
LINKED_TO_TASK
LINKED_TO_ACCOUNT
LINKED_TO_TRANSACTION
LINKED_TO_BUDGET
LINKED_TO_GOAL
ATTACHED_RECEIPT
SUGGESTS_SEMANTIC_RELATION
CONFIRMS_SEMANTIC_RELATION
REJECTS_SEMANTIC_RELATION
MANUAL_CONCEPTUAL_LINK
GENERATES_VIEW
REBUILDS_FROM
IMPORTS_FROM_ICS
EXPORTS_TO_ICS
IMPORTS_FROM_CSV
EXPORTS_TO_CSV
```

Preserve direction and provenance.

Do not collapse distinct relationship types into one generic `RELATED_TO` edge.

---

## 26. Semantic Validation Gates

Add completion gates proving all of the following:

```json
{
  "calendarRequirementsAdded": false,
  "calendarCapabilitiesAdded": false,
  "calendarFoundationsSourceInspected": false,
  "calendarCloudBoundaryMapped": false,
  "calendarFilePersistencePlanned": false,
  "calendarTestsMapped": false,

  "financeRequirementsAdded": false,
  "financeCapabilitiesAdded": false,
  "financeDistinguishedFromAffineBilling": false,
  "financeStoragePlanned": false,
  "financePrivacyMapped": false,
  "financeTestsMapped": false,

  "canvasScopeRequirementsAdded": false,
  "folderHomeCanvasMapped": false,
  "workspaceHomeCanvasMapped": false,
  "canvasMovementAndStableIdentityMapped": false,
  "canvasFilePersistenceMapped": false,

  "mindMapScopeRequirementsAdded": false,
  "folderMindMapsMapped": false,
  "workspaceMindMapsMapped": false,
  "globalFederatedMapMapped": false,
  "mapDuplicationProhibited": false,
  "realBlockSuiteMindMapRootsVerified": false,
  "aiMindMapRootsExcludedFromRetention": false,

  "structuralLinkingMapped": false,
  "explicitLinkingAndBacklinksMapped": false,
  "localSemanticSuggestionsMapped": false,
  "silentSemanticAcceptanceProhibited": false,
  "manualConceptualLinksMapped": false,
  "temporaryContextLinksSeparated": false,
  "relationshipProvenanceMapped": false,
  "globalGraphFiltersMapped": false,

  "stableIdentityModelMapped": false,
  "fileMovementDoesNotBreakLinksMapped": false,
  "folderAndWorkspaceOwnershipMapped": false,
  "calendarFinanceIntegrationMapped": false,

  "allNewRequirementsTraceable": false,
  "allNewCapabilitiesTraceable": false,
  "allNewChangesHaveExactTargets": false,
  "allNewTestsMapped": false,
  "releaseWavesUpdated": false,
  "oldCompletionSuperseded": false,
  "allDerivedArtifactsRegenerated": false,
  "independentReviewPassed": false,
  "codebaseUnmodified": false,
  "finalReleaseReceiptLocked": false
}
```

Every true gate requires evidence paths and hashes.

A record count alone is not sufficient evidence.
