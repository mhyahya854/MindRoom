# MindRoom Windows Packaging Test Plan

Generated: 2026-07-28T01:21:59.174Z

Status: **COMMANDS DISCOVERED — BUILD AND INSTALLER NOT EXECUTED**

## Repository-discovered pipeline

1. Build renderer: `CMD-RENDERER-BUILD`.
2. Build Electron layers: `CMD-ELECTRON-BUILD`.
3. On Windows x64, with the workflow's native/web artifacts present, set `HOIST_NODE_MODULES=1` and `SKIP_WEB_BUILD=1`; run `CMD-WINDOWS-PACKAGE`.
4. Apply the approved signing process to the packaged executables and native binaries.
5. Produce Squirrel with `CMD-WINDOWS-SQUIRREL`.
6. Produce NSIS with `CMD-WINDOWS-NSIS`.
7. Run a future `CMD-INSTALLER-LAUNCH` smoke suite in clean disposable Windows VMs.

The generic root `yarn build` alias is not accepted as proof: the CLI build command needs a package target, while CI uses `affine @affine/electron ...`.

## Required artifact assertions

- Record repository/hash baseline, command, environment variables, cwd, timestamps, exit codes, tool versions, and hashes for every output.
- Install/uninstall both installer formats; launch from Start Menu and direct executable; verify upgrade and clean reinstall.
- Verify application name, version, architecture, icons, publisher/signature, install paths, protocol/file associations, shortcuts, uninstaller, and absence of stale processes.
- Scan packaged files and installers for required runtime assets, native modules, codecs, document engines, licence texts, `NOTICE.txt`, `THIRD_PARTY_NOTICES.txt`, and final SBOM.
- Reconcile packaged contents against the source-lock SBOM; lockfile-only inventory is insufficient.
- Run renderer, Electron, production, desktop E2E, fixture, app-deletion-survival, and offline suites against the installed artifact, not a development server.
- Prove the installed runtime performs no external cloud/auth/telemetry/updater/download/network behavior.

## Network and signing observations

Current release workflows download native/web artifacts, obtain a signer from a CDN, and use a remote signing service. Forge environment configuration also includes a remote `iconUrl` for Squirrel metadata. These are build-time dependencies, not proof of installed-runtime traffic, but they prevent a fully offline/reproducible release pipeline until replaced, vendored, or explicitly approved and evidenced. The installed application must not depend on any of them.

## Licence/SBOM blockers

- `CMD-LICENCE-AUDIT` and `CMD-SBOM` are unavailable.
- The current third-party register has 4,212 unresolved licence records.
- `NOTICE.txt` and `THIRD_PARTY_NOTICES.txt` are not yet produced.
- Restricted AFFiNE EE/MPL-scoped backend/native code requires an approved legal determination before distribution.

## Pass condition

Packaging passes only when both Windows installers are reproducibly generated, signed under the approved policy, installed and launched in clean VMs, scanned, reconciled with a complete SBOM/notices bundle, and proven offline with real fixtures. A successful `electron-forge package` exit alone is insufficient.
