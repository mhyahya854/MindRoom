# Build, Packaging, Installer, and Test Map

## Toolchain

- Package manager: Yarn `4.13.0` (`package.json:96`, `.yarnrc.yml:1-4`).
- JavaScript/TypeScript: workspace scripts invoke the custom `affine` CLI (`package.json:20-37`).
- Browser bundles: Rspack through `tools/cli/src/bundle.ts`.
- Electron main/preload/helper bundles: esbuild through `packages/frontend/apps/electron/scripts/build-layers.ts`.
- Desktop packaging: Electron Forge, plus standalone NSIS/Squirrel scripts.
- Native code: Cargo workspace (`Cargo.toml:1-9`) and N-API exports (`packages/frontend/native/src/lib.rs:1-14`).
- Unit tests: Vitest and backend AVA.
- E2E: Playwright package suites.

## Command entrypoints

The `affine` CLI registers run/init/clean/build/dev/bundle/cert commands (`tools/cli/src/affine.ts:13-34`). `BuildCommand` delegates to the selected package's `build` script (`tools/cli/src/build.ts:3-16`). Root scripts expose:

- `yarn affine dev`;
- `yarn affine build`;
- TypeScript project build;
- Vitest unit tests;
- lint/format/schema checks.

Evidence: `package.json:20-37`.

## Frontend bundling

Rspack target selection (`tools/cli/src/bundle.ts:53-199`):

| Package | HTML/runtime entries | Worker entries |
|---|---|---|
| `@affine/web` | `src/index.tsx` | workspace profile, PDF, turbo painter, Mermaid, Typst, `nbstore.worker.ts` |
| `@affine/mobile` | `src/index.tsx` | same base set plus nbstore |
| `@affine/ios`, `@affine/android` | `src/index.tsx` | workspace profile, PDF, turbo painter, nbstore |
| `@affine/electron-renderer` | app, shell, popup, backgroundWorker | workspace profile, PDF, turbo painter |
| `@affine/admin` | `src/index.tsx` | none in this switch |
| `@affine/server` | Node target `src/index.ts` | none |

The common worker set is declared at `tools/cli/src/bundle.ts:53-93`; package-specific entries are declared at `tools/cli/src/bundle.ts:96-199`. Production builds clean the package `dist`, compile with parallel Rspack, report errors, and may upload release assets to R2 when credentials are present (`tools/cli/src/bundle.ts:223-270`, `tools/cli/src/bundle.ts:38-50`).

Classification:

- Local/browser/renderer/worker build pipeline: **PRESERVE**.
- R2 release upload: **REVIEW/EXCLUDE** if the hardened distribution is fully offline.

## Electron layers

Electron package scripts (`packages/frontend/apps/electron/package.json:23-33`):

- `start`: Electron loads package `main` (`./dist/main.js`, line 5).
- `dev`: starts Electron with `DEV_SERVER_URL=http://localhost:8080`.
- `build`: executes `scripts/build-layers.ts`.
- `package`: Electron Forge package.
- `make`: Electron Forge make.
- `make-squirrel` and `make-nsis`: standalone Windows installers.

Esbuild inputs are:

- `src/main/index.ts`;
- `src/preload/index.ts`;
- `src/helper/index.ts`.

They output bundled CommonJS to `dist`, target Node 22, copy `.node` assets, and keep Electron/electron-updater/Yjs/semver external (`packages/frontend/apps/electron/scripts/common.ts:79-108`). `build-layers.ts` rejects runtime workspace dependencies that were not bundled and injects build-type definitions (`packages/frontend/apps/electron/scripts/build-layers.ts:8-56`).

## Electron asset assembly

Forge's `generateAssets` hook runs `yarn generate-assets` (`packages/frontend/apps/electron/forge.config.mjs:415-434`). The asset script:

1. validates the release version;
2. bundles `@affine/electron-renderer`;
3. bundles `@affine/electron`;
4. moves renderer `dist` to `electron/resources/web-static`;
5. rewrites updater metadata for internal builds.

Evidence: `packages/frontend/apps/electron/scripts/generate-assets.ts:11-74`.

The application protocol serves renderer assets from `resources/web-static` in packaged builds (`packages/frontend/apps/electron/src/main/protocol.ts:23-24,119-148`).

## Electron Forge package

Forge configuration (`packages/frontend/apps/electron/forge.config.mjs:166-434`) provides:

- DMG for macOS;
- ZIP for macOS/Linux/Windows;
- Squirrel for Windows;
- AppImage, deb, and Flatpak for Linux;
- platform/build-type product names, application IDs, icons, and protocol schemes;
- macOS hardened signing and optional notarization;
- `app-update.yml` and Linux metainfo resources;
- ASAR packaging;
- locale trimming;
- auto-unpack-native plugin;
- Electron fuses disabling RunAsNode/Node options/CLI inspect and enforcing ASAR integrity and ASAR-only load.

Flatpak explicitly grants network access and home filesystem access (`packages/frontend/apps/electron/forge.config.mjs:299-313`). This must be reviewed against the final offline threat model; it is current packaging evidence, not a target recommendation.

## Installers

### macOS

- DMG layout and app link: `packages/frontend/apps/electron/forge.config.mjs:166-203`.
- Developer ID signing and optional notarytool notarization: `packages/frontend/apps/electron/forge.config.mjs:327-343`.

### Windows

- Forge Squirrel maker: `packages/frontend/apps/electron/forge.config.mjs:213-221`.
- Standalone Squirrel produces `RELEASES`, setup executable, and full/delta nupkg artifacts: `packages/frontend/apps/electron/scripts/make-squirrel.ts:22-80`.
- Standalone NSIS uses app-builder-lib with per-user, assisted install, license, custom include, icon/sidebar, and changeable install directory: `packages/frontend/apps/electron/scripts/make-nsis.ts:21-94`.

### Linux

- AppImage: `packages/frontend/apps/electron/forge.config.mjs:222-245`.
- deb with post-install/pre-remove scripts: `packages/frontend/apps/electron/forge.config.mjs:246-263`.
- Flatpak runtime/base/modules/permissions: `packages/frontend/apps/electron/forge.config.mjs:264-317`.
- ZIP: `packages/frontend/apps/electron/forge.config.mjs:204-212`.

## Runtime assets and stale-resource risks

Current packaged runtime assets include:

- `resources/web-static`;
- `resources/app-update.yml`;
- icons, DMG background, NSIS graphics;
- Linux metainfo and deb scripts;
- native `.node` modules;
- source-bundled PDF/Mermaid/Typst/turbo worker assets.

Risks after excluded-system removal:

1. `app-update.yml`, updater dependencies, and update maker metadata may become stale.
2. Sentry build plugins/source-map upload settings may remain despite telemetry removal.
3. R2 asset upload may remain despite an offline release policy.
4. Flatpak network permission may remain broader than needed.
5. AI CDN/template assets may remain reachable from renderer bundles.
6. dead route chunks may still be emitted until registrations/imports are removed.

## Test topology

### Unit/integration

Root Vitest:

- projects: root, Electron, and all BlockSuite Vitest configs;
- root include: common/frontend `*.spec.ts(x)`;
- shared polyfill/Lit/mock/global setup;
- Yjs alias to prevent duplicate module copies;
- Istanbul lcov coverage.

Evidence: `vitest.config.ts:11-78`.

Electron Vitest isolates Electron tests, uses fork pools, a 60-second timeout, and Electron coverage output (`packages/frontend/apps/electron/vitest.config.ts:5-34`).

Backend server uses AVA, with separate copilot, coverage, and E2E scripts (`packages/backend/server/package.json:8-18`).

### Playwright

Test workspaces include:

- `tests/affine-local`;
- `tests/affine-desktop`;
- `tests/affine-cloud`;
- `tests/affine-desktop-cloud`;
- `tests/affine-cloud-copilot`;
- `tests/affine-mobile`;
- `tests/blocksuite`.

Local web E2E starts `affine dev -p @affine/web` at localhost:8080 (`tests/affine-local/playwright.config.ts:16-62`). Desktop E2E optionally starts the Electron renderer dev bundle when `DEV_SERVER_URL` is set (`tests/affine-desktop/playwright.config.ts:16-54`).

Classification:

- BlockSuite/local/desktop tests: **PRESERVE/EXPAND**.
- Cloud/copilot suites: **USE AS REMOVAL EVIDENCE, THEN RETIRE OR REPLACE**.

## Verification performed in this mapping phase

Performed:

- read-only file enumeration;
- exact source-anchor inspection;
- registry and package-script searches;
- JSONL syntax validation after artifact creation.

Not performed:

- dependency installation;
- TypeScript/Cargo compilation;
- unit or E2E tests;
- Electron launch;
- Forge packaging/signing/notarization;
- installer execution;
- network-boundary runtime capture.

Reason: the locked phase authorizes read-only mapping of `Codebase/**`, not source mutation or build/release execution.
