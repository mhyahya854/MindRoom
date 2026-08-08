# MindRoom Master Plan 01 — Everything We Are Keeping

# 1. Authority

This is the authoritative record of everything retained from AFFiNE for MindRoom.

MindRoom is a private, local-first, file-backed second brain. AFFiNE remains the upstream foundation and primary code source. Mature AFFiNE implementations must be preserved whenever they satisfy the requirement.

# 2. Status Meanings, Retention Categories, and Decision Labels

Every retained capability must receive one canonical retention category and be tracked using the canonical status model.

### 2.1 Canonical Retention Categories
- **KEEP UNCHANGED** — retain the existing implementation and integration.
- **KEEP AND RELOCATE** — retain behaviour while moving the code to its authoritative capability location.
- **KEEP AND WRAP** — retain the AFFiNE implementation in its existing package or upstream-compatible location. MindRoom accesses it through a thin public boundary. The wrapper must not duplicate the underlying implementation.
- **KEEP AND ADAPT** — retain the mature implementation while replacing only incompatible cloud, storage, branding, or runtime boundaries.
- **KEEP AS DERIVED STATE** — retain as cache, index, CRDT state, or acceleration layer, but never as the sole source of user data.
- **KEEP FOR COMPATIBILITY** — temporarily retain code required for: existing workspaces, old metadata, old storage formats, old application IDs, upgrade paths, migration, stable UUIDs, historical schema versions, or old file locations. Compatibility code may be removed only after migration and old-workspace tests prove it is no longer needed.
- **KEEP FOR LICENCE/ATTRIBUTION** — retain required upstream notices and source attribution without active product behaviour.

### 2.2 Decision Labels
- **MANDATORY** — non-negotiable requirement for the first release.
- **CONDITIONAL** — required only if specific existing product baseline or target conditions are met (must define default, deviation condition, required evidence, and fallback).
- **OPTIONAL LATER** — explicitly deferred to a subsequent release; do not implement now.
- **FORBIDDEN** — strictly banned from Codebase and runtime.
- **REQUIRES EVIDENCE** — action (such as deletion, refactoring, or adding a new dependency) cannot proceed without documented Graphify proof, benchmarking, or test verification.

### 2.3 Canonical Status Model (Mechanical State Machine)
All tasks, capabilities, and migrations across all three Master Plan files must use this exact state machine:
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

---


# 3. MindRoom Product Definition

The final app is:

> A private, local-first, file-backed second brain combining documents, databases, Kanban boards, infinite canvases, whiteboards, mind maps, knowledge graphs, Office files, PDFs, media, search, and ordinary user-accessible folders.

The defining rule is:

> The user’s information must continue to exist, remain readable, and remain recoverable even if the application is permanently deleted.

AFFiNE already provides the strongest foundation for block documents, Page mode, Edgeless mode, databases, whiteboards, mind maps, local workspaces, and a desktop application. Those are the reasons for retaining AFFiNE rather than rebuilding the app from scratch. 

---

# 4. Complete AFFiNE Retention Scope

## 4.1 AFFiNE’s basic application architecture

Keep as much of the functioning AFFiNE application as possible:

* Existing monorepo organization where moving it would cause unnecessary breakage (MANDATORY: one coherent, dependency-safe capability batch per commit (when Git is available) or per hash-manifest checkpoint (when Git is unavailable); maximum 5 source files or 1 cohesive leaf module per normal mutation batch; reject artificial directory-depth limits)
* Desktop application architecture (MANDATORY: Windows-first desktop application release)
* Electron main process
* Renderer application
* Existing package boundaries that remain technically useful
* Valid macOS and Linux source and configuration (CONDITIONAL — verify only on suitable systems or CI runners; missing Apple or Linux hardware does not block the Windows release; do not claim unverified platforms are proven)
* OS Keyring support (CONDITIONAL — remove if unused; keep only for an explicitly defined local-security requirement such as local encryption keys or encrypted backup keys; do not keep merely because it exists, and do not remove merely because cloud API keys are removed; REQUIRES EVIDENCE)
* Existing build pipeline
* Existing package manager and lockfile
* Existing TypeScript configuration
* Existing bundling and packaging foundations
* Existing worker architecture
* Existing command and event systems
* Existing dependency-injection or module-registration systems
* Existing tested platform abstractions
* Existing performance optimizations
* Existing test utilities and fixtures
* Existing reusable UI primitives
* Existing icons, styles, layout systems, themes, and interaction patterns

We are not rewriting AFFiNE merely to make the repository look original.

---

## 4.2 BlockSuite

Keep BlockSuite as the primary editing and visual-workspace foundation.

Retain:

* Block-based document model
* Text blocks
* Heading blocks
* Lists
* Checklists
* Code blocks
* Quote blocks
* Divider blocks
* Image and attachment blocks
* Embed blocks that work locally
* Database blocks
* Canvas blocks
* Block selection
* Block movement
* Block drag-and-drop
* Block nesting
* Block duplication
* Block deletion
* Block formatting
* Block focus and keyboard navigation
* Slash-command behavior where locally compatible
* Undo and redo
* Clipboard behavior
* Selection behavior
* Document composition
* Existing schemas
* Existing block rendering
* Existing editor performance work

AFFiNE’s block system is fundamental to the product and should not be replaced with a new editor.

---

## 4.3 Page mode

Keep AFFiNE’s conventional document mode:

* Vertical document editing
* Headings
* Paragraphs
* Lists
* Checklists
* Tables
* Embedded files
* Embedded databases
* Inline links
* Page references
* Tags and properties
* Document navigation
* Document outline where present
* Page creation
* Page duplication
* Page rename
* Page deletion through recoverable Trash
* Page history where it can be implemented locally

AFFiNE’s core model already treats documents as collections of blocks and supports both linear Page mode and spatial Edgeless mode. 

---

## 4.4 Edgeless mode and infinite canvas

Keep AFFiNE’s Edgeless/infinite-canvas implementation.

Retain:

* Infinite canvas
* Zooming
* Panning
* Selection
* Multi-selection
* Frames
* Shapes
* Connectors
* Arrows
* Text elements
* Notes
* Images
* Embedded documents
* Embedded blocks
* Object movement
* Object resizing
* Object rotation where supported
* Layer order
* Grouping
* Alignment
* Snapping
* Canvas keyboard shortcuts
* Canvas undo and redo
* Canvas export
* Existing canvas rendering optimizations
* Existing interaction and pointer logic

This is a key AFFiNE capability and must be copied or preserved as a coherent implementation—not recreated from inspiration.

---

## 4.5 Whiteboards

Keep the AFFiNE whiteboard experience and canvas object system.

Adapt persistence so each whiteboard has an ordinary file-backed representation:

```text
whiteboard-{uuid}-{slug}/
├─ board.json
├─ metadata.json
├─ assets/
├─ previews/
│  ├─ preview.png
│  └─ preview.svg
└─ recovery/
```

Keep:

* Canvas UI
* Objects
* Frames
* Connectors
* Text
* Images
* Embeds
* Drawing behavior
* Selection and editing
* Existing serialization logic where usable
* Existing canvas rendering and interaction code

Change:

* The editable whiteboard must not exist only inside AFFiNE’s internal database.
* `board.json` becomes the durable ordinary-file representation.
* PNG/SVG files are derived previews.
* Whiteboard assets must live inside the owning page or workspace bundle.

---

## 4.6 Mind maps

Keep AFFiNE’s mind-map implementation.

Retain:

* Mind-map nodes
* Parent-child relationships
* Node expansion and collapse
* Node creation
* Node deletion
* Node reparenting
* Dragging
* Automatic layout
* Connector rendering
* Styling
* Keyboard interactions
* Canvas integration
* Export behavior
* Existing tests and layout algorithms

Add ordinary-file persistence:

```text
mind-map-{uuid}-{slug}/
├─ mind-map.json
├─ metadata.json
├─ assets/
└─ previews/
   ├─ preview.png
   └─ preview.svg
```

Do not replace AFFiNE’s mature mind-map code with a simpler custom tree.

---

## 4.7 Database blocks

Keep AFFiNE’s database UI and interaction model where compatible.

Retain:

* Database blocks
* Columns/properties
* Text properties
* Number properties
* Checkbox properties
* Date properties
* Select properties
* Multi-select properties
* URL and file properties where supported
* Sorting
* Filtering
* Grouping
* Row creation
* Row editing
* Row deletion
* Table views
* Board/Kanban views
* Existing formulas and relations that can operate locally
* Existing database-block rendering
* Existing database-block interaction code

AFFiNE already uses database-style blocks with structured fields, table-style views, and Kanban-like organization. 

Change the source-of-truth model to ordinary files:

```text
database-{uuid}-{slug}/
├─ schema.json
├─ rows.jsonl
├─ views.json
├─ formulas.json
├─ relations.json
├─ metadata.json
└─ recovery/
```

Internal databases may cache this data, but they must be rebuildable.

---

## 4.8 Kanban boards

Keep the AFFiNE database board/Kanban interface where possible.

Retain:

* Columns
* Cards
* Drag-and-drop
* Card ordering
* Column ordering
* Grouping by property
* Filters
* Sorting
* Card editing
* Card detail views
* Database integration
* Existing board rendering
* Existing pointer interactions

Add a clear file-backed representation:

```text
kanban-{uuid}-{slug}/
├─ board.json
├─ cards.jsonl
├─ views.json
├─ metadata.json
└─ recovery/
```

Kanban may remain a database view internally, but the user’s board and cards must remain recoverable without the app database.

---

## 4.9 Collections and local organization

Keep AFFiNE Collections or an equivalent local smart-folder system.

Retain:

* Property-based grouping
* Tag-based grouping
* Saved filters
* Dynamic page collections
* Local organization of pages
* Manual folders where introduced
* Favorites
* Recent pages
* Pinned pages
* Local navigation

Collections must operate without AFFiNE Cloud.

Collection definitions should be stored as ordinary JSON metadata.

---

## 4.10 Search

Keep AFFiNE’s local search UI and reusable indexing logic where compatible.

Retain:

* Search dialog
* Search results UI
* Page search
* Block search
* Highlighting
* Filtering
* Keyboard navigation
* Recent searches where stored locally
* Search-related interaction patterns

Change:

* Search must index ordinary workspace files.
* Search indexes are derived.
* Search can be deleted and rebuilt.
* Search cannot be the only repository of content.
* Preserve the current working local search/indexing implementation initially (MANDATORY). Replace or refactor (e.g., Qdrant, sqlite-vec) only after baseline search works and evidence/benchmarking justifies it based on search quality, recall, latency, startup reliability, recovery, index corruption handling, package size, and maintenance complexity (REQUIRES EVIDENCE). Do not add new database/vector dependencies before evidence justifies it.

Search sources include:

* Markdown
* PDF extracted text
* Word/ODT extracted text
* PowerPoint/ODP slide text
* Excel/ODS values
* CSV values
* Database rows
* Kanban cards
* Whiteboard text
* Mind-map text
* Media metadata
* Tags and properties
* File names and paths

---

## 4.11 Existing attachment and media UI

Keep compatible AFFiNE:

* Attachment blocks
* File cards
* Image blocks
* File-selection interfaces
* Drag-and-drop import
* Copy/paste import
* Image rendering
* Basic media display
* Download/export actions
* File icons
* File metadata UI
* Existing attachment interactions

Replace the storage destination with page bundles or `WorkspaceLibrary`.

---

## 4.12 PDF functionality

Keep AFFiNE’s PDF-related code wherever it is complete and local.

Retain or transplant:

* PDF block/file integration
* PDF opening
* Page rendering
* Scrolling
* Zoom
* Page navigation
* Thumbnail sidebar
* Text selection where available
* Existing PDF.js integration
* Existing PDF styles and controls
* Existing tests

Add the missing durable PDF bundle and annotation model.

---

## 4.13 Keyboard, commands, selection, and editing behavior

Keep:

* Keyboard shortcuts
* Command registration
* Context menus
* Slash commands that operate locally
* Undo/redo
* Selection state
* Drag-and-drop
* Clipboard support
* Focus handling
* Navigation shortcuts
* Canvas shortcuts
* Database shortcuts
* Existing accessibility behavior
* Existing tested interaction patterns

Do not remove command infrastructure simply because one visible command is removed.

---

## 4.14 Existing tests, fixtures, and performance work

Keep:

* Relevant unit tests
* Integration tests
* End-to-end tests
* BlockSuite tests
* Canvas tests
* Database tests
* PDF tests
* Interaction tests
* Test utilities
* Existing fixture generators
* Existing performance optimizations
* Existing resource cleanup
* Existing worker offloading
* Existing virtualization
* Existing lazy loading
* Existing streaming behavior

When copying an AFFiNE feature, copy its associated tests, styles, assets, dependencies, and lifecycle behavior.

**Testing & Mocking Standard (MANDATORY):**
- Mocks are allowed for pure unit logic, failure injection, and deterministic edge cases where the real boundary is separately tested.
- Mocks are strictly insufficient as final proof for SQLite/local persistence, database migration, IPC round trips (renderer/preload/main), filesystem import/export, backup and restore, packaged runtime behaviour, or runtime network enforcement.
- A capability may use mocked unit tests during development, but cannot be marked fully verified unless required real integration tests also pass on disposable real test fixtures.

---

## 4.15 Licences and attribution

Keep:

* Original licence texts
* Upstream author credits
* Required copyright notices
* Dependency notices
* AFFiNE attribution
* BlockSuite attribution
* Third-party licence headers
* Git history where available

Branding can be changed. Attribution cannot be erased.

**Third-Party Code Register (MANDATORY):**
For any retained, copied, or transplanted third-party code, maintain a register recording: source repository, exact commit/tag, licence, copied files, copied tests, destination, modifications, removed unwanted coupling, new dependencies, and verification evidence. Copied code must be reviewed semantically to guarantee zero active cloud calls, auth, telemetry, updater checks, runtime network downloads, or duplicate implementations.

**AFFiNE Anti-Reinvention Principle (MANDATORY INTERLOCK):**
No new substitute implementation file may be created until a valid `TRANSPLANT_VS_INVENTION_RECEIPT` exists under `Graphify/09 Implementation/Transplant Receipts/`. If AFFiNE has a coherent implementation, copy it with its tests, types, styles, assets, workers, registrations, lifecycle handling, and attribution. Technical difficulty is not evidence of incompatibility.

---

# 5. AFFiNE Systems Retained With Fundamental Adaptation

## 5.1 AFFiNE local storage

AFFiNE’s local database and CRDT architecture may remain as:

* Active editing state
* Transaction state
* Collaboration-free local CRDT state
* Cache
* Performance acceleration
* Search acceleration
* Renderer state
* Session state
* Autosave staging
* Derived index

It must no longer be the only source of truth.

The app must be able to rebuild itself from visible workspace files.

---

## 5.2 CRDT data

Keep CRDT logic where it improves:

* Editing
* Undo/redo
* Structured block state
* Whiteboard interaction
* Local transaction safety
* Temporary merge behavior

But:

* CRDT blobs must not be the only surviving representation.
* Documents must export continuously or transactionally to ordinary files.
* Whiteboards, mind maps, databases, and Kanban must have durable JSON/JSONL representations.
* Deleting internal application databases must not destroy the workspace.

---

## 5.3 AFFiNE workspace

Keep the workspace concept, but change the physical structure.

A workspace becomes a visible user-owned folder rather than an opaque application database.

Example:

```text
Workspace Name/
├─ workspace.json
├─ Pages/
├─ WorkspaceLibrary/
├─ Graph/
├─ Search/
├─ Backups/
├─ Trash/
├─ Conflicts/
├─ Logs/
└─ Recovery/
```

---

## 5.4 Page identity

Keep AFFiNE’s stable internal document/page IDs.

Add:

* Stable UUID
* Human-readable page title
* User-named Markdown file
* Page bundle folder
* File rename synchronization
* External rename detection

Example:

```text
Pages/
└─ page-{uuid}-{slug}/
   ├─ Biochemistry Notes.md
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

`page.meta.json` records:

```json
{
  "id": "stable-uuid",
  "title": "Biochemistry Notes",
  "mainMarkdownFile": "Biochemistry Notes.md"
}
```

The plans explicitly require user-named Markdown files, page bundles, workspace-level bundles, source-file preservation, native document support, rebuildable search/graph, and offline operation. 

---

## 5.5 Graph

Any useful AFFiNE relationship data may be retained, but the final graph becomes a simplified, local, rebuildable knowledge graph.

`graph.json` is not source of truth.

The graph is reconstructed from:

* Page links
* Backlinks
* Tags
* File ownership
* Database relations
* Kanban references
* Whiteboard embeds
* Mind-map references
* Media links
* Shared file references
* Page-to-workspace promotion references

---

## 5.6 Version history

Remove dependence on cloud “time machine” services.

Replace with local:

* Backups
* Snapshots
* Recovery entries
* Journal records
* Conflict copies
* Optional local version history

---

---

# 6. MindRoom-Specific Retention Rule

For every retained capability, Graphify must record:

- Stable capability ID
- Canonical retention category (`KEEP UNCHANGED`, `KEEP AND RELOCATE`, `KEEP AND WRAP`, `KEEP AND ADAPT`, `KEEP AS DERIVED STATE`, `KEEP FOR COMPATIBILITY`, or `KEEP FOR LICENCE/ATTRIBUTION`)
- Current status from the canonical status model (`NOT_STARTED`, `MAPPED`, `READY`, `IN_PROGRESS`, `IMPLEMENTED`, `TESTING`, `READY_FOR_REVIEW`, `CHANGES_REQUESTED`, `READY_TO_INTEGRATE`, `INTEGRATED`, `VERIFIED_COMPLETE`, `BLOCKED`, `OBSOLETE`, or `REMOVED`)
- Current repository-relative path (under `Codebase/` or `Graphify/`)
- Current symbol or unique anchor
- Current line range as secondary evidence
- Graphify node ID
- Current owner
- Final owner
- Final authoritative folder
- Dependencies and dependants
- Runtime registrations
- Tests
- Required adaptations
- Preservation status
- Independent review status

Working AFFiNE code must not be rewritten merely to make MindRoom look more original. Humans have already invented enough needless rewrites.
<!-- mindroom-product-expansion-20260729-155104:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-product-expansion-20260729-155104`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130207:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130207`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130301:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130301`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130347:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130347`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130433:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130433`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130534:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130534`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130637:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130637`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-131323:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-131323`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-131954:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-131954`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-132635:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-132635`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-133353:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-133353`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-134102:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-134102`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-134744:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-134744`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-135536:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-135536`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-140415:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-140415`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-141300:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-141300`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-141342:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-141342`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-142249:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-142249`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-143506:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-143506`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

## 7.1 Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

## 7.2 Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

## 7.3 Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

## 7.4 Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

## 7.5 Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---

<!-- mindroom-graphify-forensic-finalization-20260730-150956:ADDITIVE-PRODUCT-EXPANSION -->

# 7. MindRoom Product Expansion Retention and Adaptation (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-150956`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Add formal retention and adaptation sections covering:

### Calendar foundations to retain or adapt

Retain and inspect reusable AFFiNE foundations including, where source inspection confirms relevance:

```text
Codebase/blocksuite/affine/data-view/src/view-presets/calendar/
Codebase/packages/frontend/component/src/ui/date-picker/calendar/
Codebase/packages/frontend/core/src/desktop/pages/workspace/detail-page/tabs/journal/calendar-events.tsx
Codebase/blocksuite/affine/data-view/src/__tests__/calendar.unit.spec.ts
Codebase/blocksuite/affine/data-view/src/__tests__/calendar-layout.unit.spec.ts
Codebase/tests/blocksuite/e2e/database/calendar.spec.ts
```

Inspect but do not automatically retain unchanged:

```text
Codebase/packages/backend/server/src/plugins/calendar/
Codebase/packages/common/graphql/src/graphql/calendar/
Codebase/packages/frontend/core/src/desktop/dialogs/setting/workspace-setting/integration/calendar/
```

Classify remote calendar infrastructure separately from local calendar functionality.

### Canvas and whiteboard foundations to retain

Retain AFFiNE’s mature:

* Edgeless engine;
* surface model;
* canvas renderer;
* shapes;
* connectors;
* frames;
* groups;
* embeds;
* clipboard;
* undo and redo;
* selection;
* layout;
* zoom and pan;
* export;
* previews;
* rendering optimisations;
* keyboard controls;
* canvas tests.

Add the requirement that MindRoom supplies an ownership and scope layer around the retained canvas engine.

### Mind-map foundations to retain

Map and retain the real non-AI BlockSuite mind-map implementation, including source-inspected roots such as:

```text
Codebase/blocksuite/affine/model/src/elements/mindmap/
Codebase/blocksuite/affine/model/src/consts/mindmap.ts
Codebase/blocksuite/affine/gfx/mindmap/
Codebase/blocksuite/integration-test/src/__tests__/edgeless/mindmap.spec.ts
```

Do not use AI mind-map generation as the retained implementation.

### Knowledge relationship foundations

Retain and adapt:

* stable document identities;
* explicit document links;
* backlinks;
* tags;
* database relations;
* embedded-document references;
* whiteboard embeds;
* mind-map references;
* file ownership;
* folder ownership;
* workspace ownership;
* rebuildable local indexes.

### Finance-adjacent reusable foundations

Finance is a new MindRoom product capability.

Do not describe AFFiNE billing as the retained finance implementation.

Only retain genuinely reusable neutral foundations such as:

* local database blocks;
* tables;
* formulas;
* date fields;
* numeric fields;
* select fields;
* relation fields;
* filtered views;
* calendar views;
* Kanban views;
* charts if genuinely available and local;
* attachment handling;
* file import;
* CSV parsing or export utilities;
* local persistence;
* encryption foundations where applicable.

---
