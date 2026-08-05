# MindRoom Licence and Attribution Map

Generated: 2026-07-28T01:11:28.262Z

## Scope and decision boundary

This is a repository-evidence map, not a legal approval. No transplantation, redistribution, deletion, or release decision is approved by this document. Unknown or mixed licence status remains blocking until reviewed.

## AFFiNE and BlockSuite scope

- The active tree identifies itself as `@affine/monorepo` version `0.27.0`, authored by `toeverything`, with `MIT` in the root package manifest.
- `Codebase/LICENSE` grants an MIT scope outside named exceptions and delegates third-party components to their original licences.
- `Codebase/packages/backend/**` and `Codebase/packages/common/native/**` are expressly routed to the backend licence. The local backend/native licence text is AFFiNE EE with an MPL-2.0 client-side carveout. These paths are a legal blocker for copying, redistribution, or consolidation without an exact scope determination.
- The BlockSuite subtree is outside those named backend/native exceptions and is therefore mapped to the root MIT scope, subject to embedded component licences and copied-source headers.
- No independent AFFiNE archive, tag, or commit exists locally. Active Codebase cannot establish upstream parity with itself.

## Local licence texts

| Path | Mapped licence | Scope |
|---|---|---|
| `Codebase/LICENSE` | MIXED_SCOPE_DECLARATION | Repository root: MIT outside packages/backend and packages/common/native, subject to third-party component licences. |
| `Codebase/LICENSE-MIT` | MIT | Repository content covered by the root MIT grant. |
| `Codebase/packages/backend/server/LICENSE` | AFFINE_EE_WITH_MPL_2_0_CLIENT_SIDE_CARVEOUT | packages/backend/server and root-declared backend scope. |
| `Codebase/packages/backend/native/LICENSE` | AFFINE_EE_WITH_MPL_2_0_CLIENT_SIDE_CARVEOUT | packages/backend/native. |
| `Codebase/packages/common/native/LICENSE` | AFFINE_EE_WITH_MPL_2_0_CLIENT_SIDE_CARVEOUT | packages/common/native. |
| `Codebase/blocksuite/framework/global/src/gfx/perfect-freehand/LICENSE` | MIT | Vendored perfect-freehand code. |
| `Codebase/blocksuite/affine/blocks/surface/src/utils/rough/LICENSE` | MIT | Vendored rough code. |
| `Codebase/blocksuite/affine/blocks/surface/src/utils/points-on-path/LICENSE` | MIT | Vendored points-on-path code. |
| `Codebase/blocksuite/affine/blocks/surface/src/utils/points-on-curve/LICENSE` | MIT | Vendored points-on-curve code. |
| `Codebase/blocksuite/affine/blocks/surface/src/utils/path-data-parser/LICENSE` | MIT | Vendored path-data-parser code. |

## Copied or derived source headers

| Path | Component | Mapped licence | Evidence |
|---|---|---|---|
| `Codebase/packages/frontend/component/src/lit-react/create-component.ts` | Google Lit React create-component | BSD-3-Clause | SPDX-License-Identifier header |
| `Codebase/blocksuite/framework/global/src/lit/watch.ts` | Google Lit watch directive | BSD-3-Clause | SPDX-License-Identifier header |
| `Codebase/blocksuite/framework/global/src/lit/signal-watcher.ts` | Google Lit SignalWatcher | BSD-3-Clause | SPDX-License-Identifier header |
| `Codebase/packages/frontend/apps/ios/App/Packages/Intelligents/Sources/Intelligents/Extension/Then.swift` | Then.swift | MIT | Complete MIT text in source header |
| `Codebase/blocksuite/affine/shared/src/adapters/markdown/gfm.ts` | mdast-util-gfm-autolink-literal excerpt/adaptation | MIT | MIT notice in source header |
| `Codebase/blocksuite/affine/shared/src/utils/figma-squircle/index.ts` | figma-squircle-derived code | UNKNOWN_FROM_HEADER_ONLY | Copyright/source URL only; no local licence identifier |
| `Codebase/packages/frontend/component/src/ui/toast/toast.ts` | BlockSuite-derived toast code | UNKNOWN_FROM_COMMIT_POINTER_ONLY | Source commit URL only; no local licence identifier in header |

The figma-squircle and toast headers lack a complete local licence identifier. They remain blockers for transplant or distribution decisions affecting those files.

## Dependency and runtime domains

| Domain | Locked components | Licence state | Notes |
|---|---:|---|---|
| JavaScript lockfile | 3166 | Unresolved from lockfile alone | `yarn.lock` pins versions but does not provide complete licence texts. |
| Rust lockfile | 1046 | Unresolved from lockfile alone | `Cargo.lock` pins sources/checksums but not complete licence metadata. |
| PDF | 11 | Unresolved | @foliojs-fork/pdfkit@0.15.3, @pdf-lib/standard-fonts@1.0.0, @pdf-lib/upng@1.0.1, @toeverything/pdf-viewer-types@0.1.1, @toeverything/pdf-viewer@0.1.1, @toeverything/pdfium@0.1.1, @types/pdfkit@0.17.3, @types/pdfmake@0.2.12, pdf-lib@1.17.1, pdfmake@0.2.20, pdf_oxide@0.3.65 |
| Office/document | 6 | Unresolved | @octokit/plugin-rest-endpoint-methods@17.0.0, @types/methods@1.1.4, mammoth@1.11.0, methods@1.1.2, libredox@0.1.14, office_oxide@0.1.3 |
| Media | 45 | Unresolved | @borewit/text-codec@0.2.1, @electron-forge/template-webpack-typescript@7.11.1, @electron-forge/template-webpack@7.11.1, @jridgewell/sourcemap-codec@1.5.5, @napi-rs/whisper-darwin-arm64@0.0.4, @napi-rs/whisper-darwin-x64@0.0.4, @napi-rs/whisper-linux-x64-gnu@0.0.4, @napi-rs/whisper@0.0.4, @reforged/maker-appimage@5.2.0, @sentry/webpack-plugin@5.3.0, @types/dom-webcodecs@0.1.15, @types/image-blob-reduce@4.1.4, @vanilla-extract/webpack-plugin@2.3.25, image-blob-reduce@4.1.0, image-size@0.7.5, immediate@3.0.6, jpeg-exif@1.1.4, media-query-parser@2.0.2, media-typer@0.3.0, media-typer@1.1.0, remedial@1.0.8, setimmediate@1.0.5, terser-webpack-plugin@5.4.0, webpack-sources@3.3.4, webpack-virtual-modules@0.6.2, webpack@5.106.0, core-media-rs@0.3.5, core-video-rs@0.3.5, image-webp@0.2.4, image@0.25.10, imagesize@0.13.0, kamadak-exif@0.6.1, libwebp-sys@0.9.6, little_exif@0.6.23, opus-codec@0.1.2, rustls-webpki@0.103.13, symphonia-codec-aac@0.5.5, symphonia-codec-adpcm@0.5.5, symphonia-codec-alac@0.5.5, symphonia-codec-pcm@0.5.5, symphonia-codec-vorbis@0.5.5, webp@0.3.1, webpki-root-certs@1.0.7, webpki-roots@0.26.11, webpki-roots@1.0.6 |
| Native/desktop | 168 | Unresolved | @electron-forge/cli@7.11.1, @electron-forge/core-utils@7.11.1, @electron-forge/core@7.11.1, @electron-forge/maker-base@7.11.1, @electron-forge/maker-deb@7.11.1, @electron-forge/maker-dmg@7.11.1, @electron-forge/maker-flatpak@7.11.1, @electron-forge/maker-squirrel@7.11.1, @electron-forge/maker-zip@7.11.1, @electron-forge/plugin-auto-unpack-natives@7.11.1, @electron-forge/plugin-base@7.11.1, @electron-forge/plugin-fuses@7.11.1, @electron-forge/publisher-base@7.11.1, @electron-forge/shared-types@7.11.1, @electron-forge/template-base@7.11.1, @electron-forge/template-vite-typescript@7.11.1, @electron-forge/template-vite@7.11.1, @electron-forge/tracer@7.11.1, @electron/asar@3.4.1, @electron/fuses@1.8.0, @electron/get@2.0.3, @electron/get@3.1.0, @electron/node-gyp@https://github.com/electron/node-gyp.git#commit=06b29aafb7708acef8b3669835c8a7857ebc92d2, @electron/notarize@2.5.0, @electron/osx-sign@1.3.3, @electron/packager@18.3.6, @electron/rebuild@3.7.2, @electron/rebuild@4.2.0, @electron/universal@2.0.3, @electron/windows-sign@1.2.2, @emnapi/core@1.10.0, @emnapi/core@1.11.1, @emnapi/runtime@1.10.0, @emnapi/runtime@1.11.1, @emnapi/wasi-threads@1.2.1, @emnapi/wasi-threads@1.2.2, @malept/electron-installer-flatpak@0.11.4, @napi-rs/cli@3.5.0, @napi-rs/cross-toolchain@1.0.3, @napi-rs/lzma-android-arm-eabi@1.4.5, @napi-rs/lzma-android-arm64@1.4.5, @napi-rs/lzma-darwin-arm64@1.4.5, @napi-rs/lzma-darwin-x64@1.4.5, @napi-rs/lzma-freebsd-x64@1.4.5, @napi-rs/lzma-linux-arm-gnueabihf@1.4.5, @napi-rs/lzma-linux-arm64-gnu@1.4.5, @napi-rs/lzma-linux-arm64-musl@1.4.5, @napi-rs/lzma-linux-ppc64-gnu@1.4.5, @napi-rs/lzma-linux-riscv64-gnu@1.4.5, @napi-rs/lzma-linux-s390x-gnu@1.4.5, @napi-rs/lzma-linux-x64-gnu@1.4.5, @napi-rs/lzma-linux-x64-musl@1.4.5, @napi-rs/lzma-wasm32-wasi@1.4.5, @napi-rs/lzma-win32-arm64-msvc@1.4.5, @napi-rs/lzma-win32-ia32-msvc@1.4.5, @napi-rs/lzma-win32-x64-msvc@1.4.5, @napi-rs/lzma@1.4.5, @napi-rs/macos-alias-darwin-universal@0.0.4, @napi-rs/macos-alias@0.0.4, @napi-rs/nice-android-arm-eabi@1.1.1, @napi-rs/nice-android-arm64@1.1.1, @napi-rs/nice-darwin-arm64@1.1.1, @napi-rs/nice-darwin-x64@1.1.1, @napi-rs/nice-freebsd-x64@1.1.1, @napi-rs/nice-linux-arm-gnueabihf@1.1.1, @napi-rs/nice-linux-arm64-gnu@1.1.1, @napi-rs/nice-linux-arm64-musl@1.1.1, @napi-rs/nice-linux-ppc64-gnu@1.1.1, @napi-rs/nice-linux-riscv64-gnu@1.1.1, @napi-rs/nice-linux-s390x-gnu@1.1.1, @napi-rs/nice-linux-x64-gnu@1.1.1, @napi-rs/nice-linux-x64-musl@1.1.1, @napi-rs/nice-openharmony-arm64@1.1.1, @napi-rs/nice-win32-arm64-msvc@1.1.1, @napi-rs/nice-win32-ia32-msvc@1.1.1, @napi-rs/nice-win32-x64-msvc@1.1.1, @napi-rs/nice@1.1.1, @napi-rs/simple-git-android-arm-eabi@0.1.22, @napi-rs/simple-git-android-arm64@0.1.22, @napi-rs/simple-git-darwin-arm64@0.1.22 |

No tracked `.exe`, `.dll`, `.so`, `.dylib`, `.node`, `.wasm`, or `.bin` runtime asset was found by the Codebase file scan. Packaging configuration supports native modules, but packaged artefacts are not present in the active tree.

No bundled LibreOffice, LibreOfficeKit, Collabora, FFmpeg, or FFprobe runtime was found in MindRoom Codebase. `mammoth` is locked, and PDF libraries/viewers are locked, but their local dependency licence texts are not available in the source tree.

## Redistribution obligations

1. Preserve AFFiNE and BlockSuite copyright, licence, and attribution.
2. Preserve every embedded MIT/BSD notice and copied-source header.
3. Resolve the exact licence for every packaged NPM, Cargo, native, PDF, Office, and media component.
4. Exclude or legally approve restricted AFFiNE EE/MPL-scoped code before distribution.
5. Generate complete plain-text `NOTICE.txt` and `THIRD_PARTY_NOTICES.txt` distribution artefacts.
6. Verify that the installer includes all required notices and no unreviewed runtime downloads.
7. Record exact source commit/tag for any future AFFiNE transplant.

## Current blockers

- Independent AFFiNE reference source and revision are absent.
- AFFiNE backend/native licence scope is mixed and restrictive.
- 4212 locked components have unresolved local licence metadata.
- Two copied-source headers have incomplete local licence evidence.
- Office/media runtime licence evidence is absent because those runtimes are not bundled in Codebase.
- `NOTICE.txt` and `THIRD_PARTY_NOTICES.txt` do not exist.
- No completed SBOM exists.
- Independent legal/attribution review has not occurred.
