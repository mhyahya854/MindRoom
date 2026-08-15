# Investigation Report: MR-INV-003

## Investigation ID

MR-INV-003

## Question

What are the actual Electron process, privilege, preload exposure, and IPC registration boundaries that Wave 0 must preserve or constrain?

## Why it matters

Wave 0 tasks `MR-IMPL-002`, `MR-IMPL-003`, and `MR-IMPL-004` are KEEP preservation tasks for Electron main, renderer, and preload. Privileged filesystem and credential operations must remain outside the renderer, so the bridge endpoints, process owners, and security invariants must be known before any Codebase mutation.

## Frozen-plan references

- Graphify/02 Architecture Map/IPC_AND_PRELOAD_MAP.jsonl
- Graphify/02 Architecture Map/COMMAND_AND_EVENT_MAP.jsonl
- Graphify/02 Architecture Map/NETWORK_BOUNDARY_MAP.jsonl
- Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl

## Repository evidence examined

- `Graphify/02 Architecture Map/IPC_AND_PRELOAD_MAP.jsonl` contains 11 Electron IPC/preload registrations:
  - 4 `PRELOAD_EXPOSURE`
  - 4 `IPC_EVENT_LISTENER`
  - 3 `IPC_REGISTRATION`
- `Graphify/02 Architecture Map/COMMAND_AND_EVENT_MAP.jsonl` maps the main-process event families that are delivered over the event bridge.
- `Graphify/09 Implementation/IMPLEMENTATION_TASKS.jsonl` confirms:
  - `MR-IMPL-002` owns Electron main, release wave `WAVE_0`, status `NOT_STARTED`.
  - `MR-IMPL-003` owns Electron renderer, release wave `WAVE_0`, status `NOT_STARTED`.
  - `MR-IMPL-004` owns preload, release wave `WAVE_0`, status `NOT_STARTED`.
  - `MR-IMPL-004` depends on both `MR-IMPL-001` and `MR-IMPL-002`.
- Codebase read-only inspection of:
  - `Codebase/packages/frontend/apps/electron/src/main/index.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/web-preferences.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/security-restrictions.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/handlers.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/events.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/exposed.ts`
  - `Codebase/packages/frontend/apps/electron/src/preload/bootstrap.ts`
  - `Codebase/packages/frontend/apps/electron/src/preload/electron-api.ts`
  - `Codebase/packages/frontend/apps/electron/src/preload/shared-storage.ts`
  - `Codebase/packages/frontend/apps/electron/src/preload/worker.ts`
  - `Codebase/packages/frontend/electron-api/src/index.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/worker/handlers.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/worker/pool.ts`
  - `Codebase/packages/frontend/apps/electron/src/main/helper-process.ts`

## External primary sources examined

None were required. This investigation is answered by the frozen MindRoom mapping and the preserved Codebase, which are authoritative for the pre-code decision.

## Tests/commands performed

Read-only repository inspection:

- `git status --short`
- `git fetch origin --prune`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- Parsed `IPC_AND_PRELOAD_MAP.jsonl` and `COMMAND_AND_EVENT_MAP.jsonl` as JSONL.
- Read the Electron main, preload, shared type, worker, helper-process, and security files listed above.
- Ran `rg` for BrowserWindow/preload/IPC/security anchors.

No Codebase files were modified.

## Findings

1. **The Electron security baseline is explicit and enforced in Codebase.**

   Classification: `PROVEN_FROM_REPOSITORY`

   - `Codebase/packages/frontend/apps/electron/src/main/web-preferences.ts` sets `sandbox: true`, `contextIsolation: true`, and `nodeIntegration: false`.
   - `Codebase/packages/frontend/apps/electron/src/main/index.ts` calls `app.enableSandbox()` before window creation.
   - `registerSecurityRestrictions()` denies external navigation and window creation unless the URL is an internal `assets://` URL.
   - `isInternalUrl()` only accepts the `assets:` protocol with hosts `.` or `another-host`.

2. **Preload exposure is limited to four named context-bridge objects and is conditional on an internal URL.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `preload/bootstrap.ts` exposes:

   - `__appInfo`
   - `__apis`
   - `__events`
   - `__sharedStorage`

   The exposure block executes only when the current preload URL passes `isInternalUrl(currentUrl)`.

3. **Every exposed API/event surface has a matching main-process owner.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `main/exposed.ts` re-exports `allHandlers` and `allEvents`.

   `__apis` maps to `main/handlers.ts` and the `AFFINE_API_CHANNEL_NAME` handler. The handler namespaces are:

   - `debug`
   - `ui`
   - `clipboard`
   - `updater`
   - `configStorage`
   - `findInPage`
   - `import`
   - `sharedStorage`
   - `worker`
   - `recording`
   - `popup`
   - `i18n`
   - `byokStorage`
   - `auth`

   `__events` maps to `main/events.ts` and the `AFFINE_EVENT_CHANNEL_NAME` / `AFFINE_EVENT_SUBSCRIBE_CHANNEL_NAME` subscription protocol. The event namespaces are:

   - `applicationMenu`
   - `updater`
   - `ui`
   - `sharedStorage`
   - `recording`
   - `popup`
   - `power`

   `__sharedStorage` maps to `main/shared-storage/handlers.ts` and `main/shared-storage/events.ts`.

4. **`__appInfo` is static preload data, not a privileged main-process RPC surface.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `preload/electron-api.ts` builds `appInfo` from process arguments (`--window-name`, `--view-id`, `scheme`). It exposes only non-privileged renderer metadata and has no main-process handler family.

5. **Helper and worker bridges use MessagePorts and are kept separate from the general IPC surface.**

   Classification: `PROVEN_FROM_REPOSITORY`

   - `helper-process.ts` creates a `MessageChannelMain` and sends `helper-connection` to the renderer.
   - `worker/handlers.ts` invokes `e.sender.postMessage('worker-connect', ...)` with a transferred renderer port.
   - `preload/worker.ts` forwards the port into the renderer window.

6. **Renderer access to privileged operations is bounded by source validation and explicit handler dispatch.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `registerHandlers()` calls `checkSource(e)` before dispatching `AFFINE_API_CHANNEL_NAME`. `registerEvents()` also calls `checkSource(event)` before adding or removing event subscriptions. `checkSource` verifies `senderFrame.url` or `sender.getURL()` against the internal `assets://` origin allowlist.

7. **No hard IPC or security blocker was found.**

   Classification: `INFERENCE`

   The evidence shows a coherent context-isolated preload bridge, sandboxed BrowserWindows, internal-origin checks, and explicit handler/event families. The remaining risks are implementation-bound hardening concerns, not contradictions with the frozen plan.

## Rejected alternatives

- Treating every `ipcRenderer` call as an unconstrained renderer capability was rejected because `checkSource` and the context-bridge exposure boundaries constrain the surface.
- Inventing a new preload schema was rejected because Wave 0 is a KEEP preservation wave and the frozen plan already records the current boundaries.
- Marking the investigation blocked was rejected because all acceptance criteria have direct repository evidence.

## Decision

Wave 0 must preserve the current Electron security baseline and IPC bridge exactly. No frozen-plan change is required. `MR-IMPL-002`, `MR-IMPL-003`, and `MR-IMPL-004` must verify these boundaries without expanding or removing them.

## Hard blockers

None.

## Soft risks

- The `__apis` object intentionally exposes a broad set of main-process namespaces. Future work must keep each namespace's functions narrowly scoped and cannot expand it without a separate security review.
- `worker-connect` and `helper-connection` transfer MessagePorts to the renderer. Their use must remain limited to the existing worker/helper bridge and must not become a general privileged transport.
- The Sentry preload import in `preload/bootstrap.ts` is a later `EXCLUDE_LATER` network/telemetry concern, but it does not change the pre-code IPC boundary decision.

## Implementation consequences

- Wave 0 must not modify `web-preferences.ts`, `security-restrictions.ts`, the three IPC channel constants, or the preload exposure names.
- Wave 0 verification must assert that the four preload exposures and their main-process handler/event families remain equal to the current source.
- `MR-IMPL-004` must remain dependent on `MR-IMPL-002` so the main-process side is preserved before the preload bridge is verified.

## What must happen in Wave 0

- Preserve Electron main process registration and security restrictions.
- Preserve renderer composition roots without changing renderer privilege.
- Preserve preload exposures, channel names, and worker/helper MessagePort bridges.
- Record the same IPC/preload mapping as evidence before any later Codebase mutation.

## Acceptance criteria results

1. BrowserWindow security settings and runtime process owners are proven from Codebase: **PASS**.
2. Every preload exposure and corresponding main-process handler family is mapped: **PASS**.
3. Renderer access to privileged operations is classified and bounded: **PASS**.
4. No unresolved IPC or security architecture risk remains before mutation: **PASS**.

## Final status

COMPLETE
