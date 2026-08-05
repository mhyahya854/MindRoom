# MindRoom Master Plan 02 — Everything We Are Deleting

# 1. Authority

This is the authoritative removal register for MindRoom.

A listed feature is not deleted merely because its UI is hidden or its filename looks unused. Deletion requires Graphify mapping, dependency analysis, runtime-registration analysis, migration analysis, packaging analysis, tests, and independent review.

# 2. Removal Statuses, Status Model, and Tool Discovery

### 2.1 Removal Statuses
- **REMOVE COMPLETELY** — remove UI, routes, services, state, workers, registrations, dependencies, tests, and runtime behaviour.
- **REMOVE REMOTE BOUNDARY** — retain the useful local feature while removing its cloud or account dependency.
- **REMOVE AFTER CONSOLIDATION** — redirect every caller to the authoritative implementation before deleting the duplicate.
- **REMOVE AFTER MIGRATION** — preserve compatibility until existing user data has been migrated and tested.
- **PRESERVE FOR LICENCE/ATTRIBUTION** — remove active product behaviour but retain mandatory notices and historical source records.

### 2.2 Canonical Status Model (Mechanical State Machine)
All removal and cleanup tasks must follow the canonical state machine:
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
Failure and terminal states: `BLOCKED`, `IMPLEMENTED_BUT_FAILING`, `REGRESSION_FOUND`, `OBSOLETE`, and `REMOVED` (which requires a valid Deletion Receipt and independent review approval).

### 2.3 Tool Discovery Standard (No Hardcoded Package Managers)
Do not assume `npm`, `pnpm`, `yarn`, or any hardcoded command. Discover the actual repository-defined command from package manifests, workspace configuration, scripts, and lockfiles.
Every test or build receipt (for typecheck, lint, unit tests, integration tests, end-to-end tests, renderer build, Electron build, production build, and packaging) must record the exact command used:
```json
{
  "command": "",
  "workingDirectory": "",
  "packageManager": "",
  "startedAt": "ISO-8601",
  "finishedAt": "ISO-8601",
  "exitCode": null,
  "result": "PASS | FAIL | BLOCKED",
  "relevantOutput": "",
  "failureClassification": "",
  "repairApplied": "",
  "rerunReceiptId": null
}
```

---


# 3. Complete AFFiNE Removal Scope

These systems are not merely hidden. Their UI, routes, services, workers, registrations, state, dependencies, and network behavior must be removed or isolated after dependency proof.

## 3.1 AFFiNE Cloud

Remove:

* AFFiNE Cloud integration
* Cloud workspace creation
* Cloud workspace opening
* Cloud workspace metadata
* Cloud storage
* Cloud upload
* Cloud download
* Cloud synchronization
* Cloud workspace switching
* Cloud status UI
* Cloud capacity UI
* Cloud quota handling
* Cloud errors
* Cloud URLs
* Cloud-specific feature flags
* Cloud-only tests

---

## 3.2 Remote synchronization

Remove:

* Remote workspace sync
* Remote CRDT synchronization
* Multi-device cloud sync
* Cloud sync queues
* Remote sync status
* Remote conflict services
* Server reconciliation
* Remote retry workers
* Sync credentials
* Remote sync endpoints

The local file watcher is not removed. It replaces remote synchronization for disk-to-app and app-to-disk behavior.

---

## 3.3 Accounts and authentication

Remove:

* Login
* Registration
* Logout
* Account profiles
* Account settings
* Password flows
* OAuth
* Magic-link login
* Session tokens
* Refresh tokens
* Authentication guards
* Account-related navigation
* Account-required workspace logic
* Remote user avatars
* Account deletion
* Device/account management

The application must open directly into local workspaces.

---

## 3.4 Teams and members

Remove:

* Team workspaces
* Team administration
* Member lists
* Workspace roles
* Permissions backed by remote users
* Organization management
* Team billing
* Member limits
* Team invitations
* Team presence
* Team dashboards

---

## 3.5 Sharing and collaboration

Remove:

* Workspace sharing
* Page sharing
* Public-share URLs
* Invite links
* Email invitations
* Real-time remote collaboration
* Remote cursors
* Remote presence
* Collaboration servers
* Remote comments tied to user accounts
* Shared permissions
* Published cloud pages

Local export remains.

Local file sharing through ordinary folders remains possible outside the app.

---

## 3.6 Billing and subscriptions

Remove:

* Paid plan UI
* Billing portal
* Subscription checks
* Premium entitlement checks
* Upgrade dialogs
* Pricing links
* Trial logic
* Payment services
* Storage-plan limits
* Team-plan limits
* Subscription event handlers
* Commercial cloud entitlement middleware

---

## 3.7 AFFiNE AI

Remove:

* AFFiNE AI
* Remote AI endpoints
* AI writing
* AI summarization
* AI rewriting
* AI mind-map generation
* AI presentation generation
* AI chat
* AI credits
* AI subscription UI
* AI usage limits
* Model selectors
* BYOK interfaces
* API-key storage
* Remote embeddings
* Remote vector search
* Cloud AI workers
* AI telemetry

Mind maps remain. AI-generated mind maps do not.

**Generative AI Exclusion (FORBIDDEN):**
Generative AI is strictly excluded from the first release. Delete all recommendations, endpoints, or paths for note summarisation, action-item extraction, local LLMs, llama-server, or generative enhancement. Semantic search remains required; generative AI remains outside the first release.

---

## 3.8 Telemetry and analytics

Remove:

* Product analytics
* Usage analytics
* Event tracking
* Crash telemetry sent remotely
* Session analytics
* Marketing attribution
* User-behavior tracking
* Remote performance reporting
* Feature-experiment telemetry
* Analytics identifiers
* Tracking cookies
* Remote diagnostic uploads

Local logs remain.

Local crash reports may remain if they never leave the device unless the user manually exports them.

---

## 3.9 Remote APIs and GraphQL

Remove or disable:

* Remote GraphQL clients
* Cloud API clients
* Remote REST APIs
* Account API
* Workspace cloud API
* Billing API
* AI API
* Collaboration API
* Remote file API
* Remote conversion API
* Remote OCR API
* Remote search API
* Remote metadata API

Local IPC is allowed.

Localhost-only communication with bundled Office or media processes is allowed.

---

## 3.10 Remote document services

Remove:

* Cloud document conversion
* Cloud Office editor integration
* Google Docs API
* Microsoft Graph API
* Remote Collabora services
* Remote PDF conversion
* Cloud OCR
* Cloud thumbnail generation
* Cloud media probing

The replacement must be local and packaged.

---

## 3.11 Remote updater and network-dependent checks

Remove or disable unless explicitly redesigned as a privacy-safe optional feature:

* Automatic network update checks
* Remote release checks
* Remote announcements
* Remote feature flags
* Remote configuration
* Remote onboarding content
* Network-fetched templates
* Network-fetched icons or assets

The core application must not require network access.

**Runtime vs. Build-Time Downloads (MANDATORY):**
- Runtime model, binary, or asset downloading is FORBIDDEN in the installed application.
- Build-time acquisition may remain only as developer/CI tooling and must not be reachable from the installed runtime.
- Required release assets must be bundled or imported from local offline packs. The installed application must never fetch them over the network.

---

## 3.12 Enterprise/backend-only architecture

Remove backend or enterprise packages only after dependency analysis proves that they exclusively support excluded features.

Do not blindly delete an entire backend directory if local code still imports reusable schemas, types, or utilities.

The target is:

* Remove active cloud/server product functionality
* Preserve reusable open-source local components
* Preserve required legal notices
* Avoid importing commercially restricted server code without licence review

---

## 3.13 Dead, duplicate, and abandoned code

Remove after proof:

* Duplicate feature implementations
* Old storage implementations
* Unused adapters
* Dead routes
* Dead UI
* Unused state stores
* Abandoned feature flags
* Commented-out implementations
* Temporary migration scripts no longer required
* Empty folders
* Unused exports
* Unused dependencies
* Obsolete tests
* Duplicate assets
* Superseded configurations
* Broken compatibility stubs with no consumer

Do not move these into `old`, `legacy`, or `backup`.

Delete them after Graphify, dependency, runtime-registration, packaging, and test evidence confirms they are unused.

**Naive Forbidden-Token Deletion Ban (FORBIDDEN):**
Do not automatically strip or delete copied code merely because a text search finds strings such as `token`, `auth`, `http`, `cloud`, or `openai`. These strings may appear in comments, licence text, historical migration names, local authentication terminology, tests, or type names. Require semantic inspection and call-path analysis before any deletion (REQUIRES EVIDENCE).

**Historical Migrations & Persistence Layer Rule (MANDATORY):**
- Never delete or rewrite historical database migrations blindly; existing users may still require them. Add new forward migrations to preserve schema-upgrade paths.
- Keep existing type-safe query abstractions (such as Kysely or existing ORM layers) initially when they provide useful local persistence. Remove only when Graphify proves they are used solely by removed systems or duplicate another abstraction, migration is safe, real tests prove no regression, and removal creates a measurable maintenance benefit (REQUIRES EVIDENCE).

---

## 3.14 Markdown files from the executable codebase

The final repository has two primary roots:

```text
project-root/
├─ Codebase/
└─ Graphify/
```

Remove all `.md` and `.markdown` files from `Codebase/`.

Move plans, READMEs, architecture notes, trackers, agent instructions, and reports into `Graphify/`.

Required distribution notices inside `Codebase/` use formats such as:

```text
LICENSE.txt
NOTICE.txt
THIRD_PARTY_NOTICES.txt
```

The Codebase must contain zero Markdown files after verification (MANDATORY). Do not allow `.md` licence exceptions; use plain-text `LICENSE`, `NOTICE`, and `THIRD_PARTY_NOTICES`. Third-party installed dependencies inside generated `node_modules/` are not authoritative tracked Codebase source. User-exported Markdown remains allowed.

---

---

# 4. Canonical Deletion Procedure and Deletion Receipts

There is one canonical deletion procedure across all Master Plan files. Never use direct deletion or `rm` on source files in `Codebase/`.

### 4.1 Canonical Deletion Sequence
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

### 4.2 Deletion Rules
1. The Deletion Receipt is created while the item is quarantined.
2. The receipt must contain all dependency, registration, migration, test, build, Graphify, and reviewer evidence.
3. The independent reviewer sets:
```text
reviewDecision: "APPROVED"
status: "QUARANTINED"
```
before permanent purge.
4. Permanent purge is forbidden until the approved receipt exists.
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

### 4.3 Mandatory Deletion Proof Points
Before any file, folder, package, export, command, route, worker, schema, migration, dependency, or test is quarantined and purged, prove all applicable points:
- No static import or re-export
- No dynamic import or call-graph relationship
- No string-based lookup
- No dependency-injection, route, command, IPC, native-command, or worker registration
- No build or packaging reference
- No migration requirement or fixture dependency
- No platform-specific use or planned capability dependency
- No user-data compatibility role or required side effect
- A replacement exists when the capability remains required
- Scoped tests, integration tests, and production build checks pass while quarantined
- Graphify incremental mapping shows no broken edges
- Independent reviewer approves the deletion

A text search returning zero results is evidence, not proof by itself.

### 4.4 Exact Deletion Receipt Schema
Define `Graphify/08 Cleanup/Deletion Receipts/`. No purge is permitted without a valid receipt matching this exact schema:
```json
{
  "deletionId": "delete-0001",
  "originalPath": "Codebase/relative/path",
  "quarantinePath": "Graphify/08 Cleanup/Quarantine/Codebase/relative/path",
  "originalSha256": "",
  "classification": "",
  "reason": "",
  "staticImportMatches": 0,
  "reExportMatches": 0,
  "dynamicImportMatches": 0,
  "symbolReferenceMatches": 0,
  "runtimeRegistrationMatches": 0,
  "buildReferenceMatches": 0,
  "packagingReferenceMatches": 0,
  "migrationRequired": false,
  "plannedCapabilityDependency": false,
  "graphifyDependants": 0,
  "tests": [],
  "buildReceipts": [],
  "independentReviewer": "",
  "reviewDecision": "APPROVED | REJECTED",
  "purgedAt": null,
  "status": "QUARANTINED | RESTORED | PURGED"
}
```
<!-- mindroom-product-expansion-20260729-155104:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-product-expansion-20260729-155104`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130207:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130207`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130301:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130301`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130347:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130347`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130433:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130433`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130534:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130534`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-130637:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-130637`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-131323:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-131323`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-131954:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-131954`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-132635:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-132635`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-133353:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-133353`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-134102:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-134102`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-134744:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-134744`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-135536:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-135536`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-140415:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-140415`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-141300:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-141300`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-141342:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-141342`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-142249:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-142249`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-143506:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-143506`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

## 5.1 AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

## 5.2 Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

## 5.3 AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

## 5.4 Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

## 5.5 Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---

<!-- mindroom-graphify-forensic-finalization-20260730-150956:ADDITIVE-PRODUCT-EXPANSION -->

# 5. MindRoom Product Expansion Removal and Isolation Boundaries (2026)

Run: `mindroom-graphify-forensic-finalization-20260730-150956`

Preservation status: **ADDITIVE AND CORRECTIVE**. Every original byte above this marker is preserved. This section supersedes only the prior Graphify-complete claim; it does not supersede or reduce any original product requirement, safety rule, deletion rule, verification gate, workflow, or retained AFFiNE capability.

Clarify the following boundaries:

### AFFiNE billing is not MindRoom Finance

The following concepts belong to AFFiNE monetisation and must not be mistaken for personal-finance functionality:

* Stripe;
* RevenueCat;
* subscription plans;
* paid tiers;
* workspace billing;
* invoices charged by AFFiNE;
* payment-method management for AFFiNE subscriptions;
* upgrade prompts;
* subscription entitlements;
* billing portals;
* cloud quota monetisation.

These remain deletion, isolation, or compatibility candidates under the existing 17-step deletion procedure.

Do not delete any mixed path merely because it contains the word `subscription`, `invoice`, `payment`, or `billing`.

Source-inspect mixed modules first.

### Cloud calendar integration boundary

Do not automatically retain cloud-dependent calendar integrations unchanged.

Classify:

* local calendar UI;
* local event data;
* CalDAV logic;
* Google Calendar logic;
* GraphQL calendar schemas;
* cloud account coupling;
* authentication coupling;
* remote subscription feeds;
* server storage;
* local-only reusable protocol logic.

External calendar integrations must become optional adapters and must not be required for MindRoom’s local calendar core.

### AI mind-map generation remains excluded

Retain manual mind maps.

Delete or isolate:

* AI-generated mind maps;
* AI expansion of mind-map branches;
* cloud copilot mind-map actions;
* generative summaries;
* generative relation creation.

### Remote semantic AI remains excluded

The first release may use deterministic local indexing and optional local embedding-based similarity.

It must not require:

* OpenAI;
* Gemini;
* remote embedding APIs;
* cloud inference;
* uploaded user notes;
* generative recommendations;
* autonomous permanent link creation.

Local semantic similarity is not permission to silently establish permanent truth.

### Finance privacy boundary

MindRoom financial information must never be coupled to:

* telemetry;
* advertising;
* cloud billing;
* AFFiNE subscription systems;
* remote analytics;
* remote AI;
* account monetisation;
* nonessential network calls.

---
