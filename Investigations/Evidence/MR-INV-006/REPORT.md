# Investigation Report: MR-INV-006

## Investigation ID

MR-INV-006

## Question

Are the pinned Node, Yarn, TypeScript, Electron, native-module, and platform command assumptions available and mutually compatible for Wave 0 verification?

## Why it matters

The active default Node runtime is outside the repository engine range. Wave 0 verification must not begin with an unsupported toolchain or a substituted package manager.

## Frozen-plan references

- Graphify/00 Execution Control/PACKAGE_BOUNDARY_BASELINE.json
- Graphify/02 Architecture Map/BUILD_AND_PACKAGING_MAP.md
- Graphify/10 Verification/CROSS_PLATFORM_TEST_MATRIX.md
- Graphify/10 Verification/TEST_COMMAND_REGISTRY.json
- Codebase/package.json
- Codebase/.nvmrc
- Codebase/.yarnrc.yml
- Codebase/.yarn/releases/yarn-4.13.0.cjs
- Codebase/.github/actions/setup-node/action.yml

## Repository evidence examined

- `Codebase/package.json`:
  - `packageManager`: `yarn@4.13.0`
  - `engines.node`: `>=22.12.0 <23.0.0`
  - `build`: `yarn affine build`
  - `test`: `vitest --run`
  - `typecheck`: `tsc -b tsconfig.json --verbose`
- `Codebase/.nvmrc`: `22.23.1`
- `Codebase/.yarnrc.yml`:
  - `nodeLinker`: `node-modules`
  - `yarnPath`: `.yarn/releases/yarn-4.13.0.cjs`
- `Codebase/.yarn/releases/yarn-4.13.0.cjs` exists and, when invoked directly with Node, reports Yarn `4.13.0`.
- `Graphify/00 Execution Control/PACKAGE_BOUNDARY_BASELINE.json` records:
  - package manager: Yarn
  - package manager version: `4.13.0`
  - workspace patterns include `blocksuite/**/*`, `packages/*/*`, and `packages/frontend/apps/*`.
- `Graphify/10 Verification/TEST_COMMAND_REGISTRY.json` records:
  - 20 available commands.
  - 6 unavailable commands.
  - The available commands use the vendored Yarn path `node .yarn/releases/yarn-4.13.0.cjs`.
- `Graphify/10 Verification/CROSS_PLATFORM_TEST_MATRIX.md` supports Windows x64, macOS arm64/x64, and Linux x64, with precompiled `.node` modules and platform-specific safe-storage providers.
- `Graphify/02 Architecture Map/BUILD_AND_PACKAGING_MAP.md` records:
  - Yarn `4.13.0`.
  - custom `affine` CLI.
  - esbuild for Electron layers.
  - Electron Forge packaging and native N-API exports.
- `Codebase/.github/actions/setup-node/action.yml` installs Node using `node-version-file: '.nvmrc'`.

## External primary sources examined

None were required. The toolchain pins are established from repository files, and the current local environment was checked read-only.

## Tests/commands performed

Read-only repository and environment checks:

- `git status --short`
- `git fetch origin --prune`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- Parsed `Codebase/package.json`, `.nvmrc`, `.yarnrc.yml`, and the vendored Yarn file.
- Ran `node Codebase/.yarn/releases/yarn-4.13.0.cjs --version`, which returned `4.13.0`.
- Checked `node --version` (`v24.18.0`), `npm --version` (`11.16.0`), `corepack --version` (`0.35.0`), and `yarn --version` (not found).
- Checked for `nvm`, `fnm`, `volta`, and `nvs`; none were found on `PATH`.
- Parsed `TEST_COMMAND_REGISTRY.json` and the CI `setup-node` action.

No Codebase files were modified.

## Findings

1. **The repository pins an exact toolchain.**

   Classification: `PROVEN_FROM_REPOSITORY`

   The authoritative Node range is `>=22.12.0 <23.0.0`, the `.nvmrc` pin is `22.23.1`, and the package manager is vendored Yarn `4.13.0` under `.yarn/releases/yarn-4.13.0.cjs`.

2. **The current local Node runtime is incompatible.**

   Classification: `EMPIRICALLY_VERIFIED_READ_ONLY`

   `node --version` reports `v24.18.0`, which is outside the repository engine range. `yarn` is not on `PATH`, but the vendored Yarn file exists and executes under the installed Node binary.

3. **A deterministic pre-Wave-0 setup action is established.**

   Classification: `INFERENCE`

   Before Wave 0 commands run, the operator must install/use Node `22.23.1` (via `nvm`, `fnm`, `volta`, or the official Node installer) and invoke Yarn through `node .yarn/releases/yarn-4.13.0.cjs`, not Corepack Yarn 1.

4. **CI already uses the same Node pin.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `Codebase/.github/actions/setup-node/action.yml` uses `node-version-file: '.nvmrc'`, confirming `22.23.1` as the canonical runtime.

5. **Wave 0 build and test commands are available through the vendored Yarn command.**

   Classification: `PROVEN_FROM_REPOSITORY`

   `TEST_COMMAND_REGISTRY.json` maps build, typecheck, unit, lint, Electron, renderer, and cross-platform commands to `node .yarn/releases/yarn-4.13.0.cjs`. The unavailable commands are installer/QA, fixture generation, licence audit, SBOM, offline runtime, and app-deletion survival, which are not Wave 0 prerequisites.

6. **Native and Electron module compatibility has no unresolved Wave 0 hard blocker.**

   Classification: `PROVEN_FROM_REPOSITORY`

   The Electron version is `^39.0.0`, `@affine/native` declares N-API targets for Windows, macOS, and Linux x64/arm64, and the cross-platform matrix records precompiled `.node` modules. Wave 0 is KEEP verification; it does not require producing native binaries or installers.

## Rejected alternatives

- Running Wave 0 on the current Node `v24.18.0` was rejected because it violates the repository engine range.
- Substituting Corepack/Yarn 1 was rejected because the repository and `TEST_COMMAND_REGISTRY.json` explicitly require vendored Yarn `4.13.0`.
- Treating missing Yarn on `PATH` as a blocker was rejected because the vendored `.cjs` Yarn is present and executable.

## Decision

Wave 0 is toolchain-compatible after a deterministic pre-flight setup: use Node `22.23.1` and invoke vendored Yarn `4.13.0` with `node .yarn/releases/yarn-4.13.0.cjs`. No Codebase change or frozen-plan change is required.

## Hard blockers

None.

## Soft risks

- The current machine is still on Node `v24.18.0`; the pre-flight Node switch has not yet been executed.
- `yarn` is not on `PATH`; every command must use the vendored Yarn path.
- Native build/package verification and installer QA remain later-wave work and are not proven by this pre-code investigation.

## Implementation consequences

- Wave 0 execution must reject the wrong Node runtime before running any repository command.
- Wave 0 evidence commands must use the vendored Yarn path.
- No package-manager or Codebase manifest changes are required.

## What must happen in Wave 0

- Pre-flight: install/use Node `22.23.1`.
- Pre-flight: run `node .yarn/releases/yarn-4.13.0.cjs --version` and require `4.13.0`.
- Pre-flight: install dependencies immutably only when Wave 0 execution is authorized.
- Run build/test/typecheck commands from `TEST_COMMAND_REGISTRY.json`.

## Acceptance criteria results

1. The exact supported runtime and package-manager versions are proven from repository files: **PASS**.
2. A compatible Node runtime is available or a deterministic pre-Wave-0 setup action is established: **PASS**.
3. Wave 0 build and test commands are portable or have explicit platform-specific owners: **PASS**.
4. Native/Electron module compatibility has no unresolved hard blocker: **PASS**.

## Final status

COMPLETE
