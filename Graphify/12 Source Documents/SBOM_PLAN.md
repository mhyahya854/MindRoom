# MindRoom SBOM Plan

Generated: 2026-07-28T01:11:28.262Z

Status: **NOT GENERATED**

## Inputs already mapped

- 123 NPM workspace/package manifests
- 9 Cargo manifests
- `Codebase/yarn.lock`
- `Codebase/Cargo.lock`
- Electron Forge packaging configuration
- 10 explicit local licence texts
- 7 copied/derived source headers
- 4226 current third-party register records

## Tool status

| Tool | Status | Notes |
|---|---|---|
| Repository Yarn 4.13.0 | Available | Run with `node .yarn/releases/yarn-4.13.0.cjs`; global `yarn` is missing and Corepack resolved Yarn 1.22.22. |
| Node.js | Available | Used for deterministic lockfile inventory. |
| Cargo/Rustc | Available | Cargo 1.97.0 / Rustc 1.97.0 observed. |
| Syft | Missing | Needed for packaged-filesystem/runtime SBOM reconciliation. |
| cargo-license | Missing | Needed for Rust licence resolution. |
| cargo-cyclonedx | Missing | Needed for Rust CycloneDX generation. |
| cyclonedx-npm | Missing | Needed for Node CycloneDX generation if selected. |
| license-checker | Missing | Optional NPM licence cross-check. |

## Planned deterministic flow

1. Freeze the repository/hash baseline and exact lockfile hashes.
2. Use the bundled Yarn 4.13.0 runtime; do not silently substitute Yarn 1.
3. Generate an NPM CycloneDX SBOM from the locked dependency graph.
4. Generate Cargo metadata, crate licence inventory, and Cargo CycloneDX output.
5. Build/package using repository-discovered commands in a later phase.
6. Run Syft over the packaged application and installer to capture Electron, native modules, copied binaries, licences, and runtime resources.
7. Merge source-lock and packaged-runtime SBOMs without collapsing distinct versions/platform variants.
8. Add vendored BlockSuite utilities and copied-source headers that package managers cannot see.
9. Add Office/media/PDF runtime components only when actual bundled artefacts exist.
10. Resolve every unknown licence and flag copyleft, source-available, restricted, dual-licensed, or missing terms.
11. Generate `NOTICE.txt` and `THIRD_PARTY_NOTICES.txt`.
12. Verify packaged notices against the final SBOM.
13. Obtain independent licence and release review.

## Required SBOM fields

Each component must include ecosystem, name, version, package URL when known, source/resolution, checksum, direct/transitive status, platform/architecture, licence expression, licence evidence, copyright, notice path, runtime inclusion, source package, modifications, and review decision.

## Release blockers

- Do not release with unresolved licences.
- Do not include restricted AFFiNE EE/MPL-scoped backend/native code without an approved legal determination.
- Do not claim Office/media runtime coverage until packaged artefacts are present and scanned.
- Do not treat lockfile inventory as proof of packaged contents.
- Do not mark the licence, attribution, or SBOM gates complete until installer-level verification passes.
