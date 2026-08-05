# MindRoom Codebase Corpus Summary

Generated: `2026-07-28T01:03:31.289325+00:00`

## Scope and evidence

- Source root: `C:\Users\mhyah\Downloads\Code\MindRoom\Codebase`
- Inventory root notation: `Codebase/...`
- Generator: `Graphify/01 Corpus Inventory/generate_inventory.py` version `1.0.0`
- Ordering: case-insensitive relative path, with original path as the tie-breaker
- Repository evidence type: `HASH_MANIFEST`
- Corpus content baseline SHA-256: `951dce8f4ab329f2bbbbd8ddc3d670872f700484450f5aaf5f69d58e10499328`
- Git metadata: absent; `git rev-parse --show-toplevel` failed for `Codebase`
- Tracked-state policy: all `12,628` discovered paths are `UNKNOWN`. A `.gitignore` match cannot prove whether an already-present file was tracked without the Git index.
- Nested Git indicators: None detected.

## Completeness

- Total inventoried paths below `Codebase/`: **12,628**
- Regular files: **10,055**
- Archives represented with `entityType=ARCHIVE`: **25**
- Directories: **2,548**
- Symlinks: **0**
- Junctions/reparse points: **0**
- Total regular-file/archive bytes: **118,418,802**
- Files/archives with SHA-256: **10,080**
- Hash failures: **0**
- Generated paths: **438**
- Vendor paths: **9**
- Binary files/archives: **388**

Exclusions:

None. The deterministic scan completed without path or hash exclusions.

## Package inventory

- Package records: **134**
- Workspace records: **3**
- Manifests with parse failures: **0**

| Ecosystem | Packages |
|---|---:|
| `NPM` | 123 |
| `CARGO` | 8 |
| `GRADLE` | 3 |

Package ownership is assigned to the deepest discovered package root. Rust files prefer a Cargo package at the same root; Android/Gradle files prefer a Gradle module; other files prefer the NPM/Yarn package. Cargo packages not explicitly listed in the root `workspace.members` remain mapped, with membership confirmation deferred rather than guessed.

## Markdown migration inventory

- Markdown files mapped: **207**
- Markdown files with inbound resolved links: **59**
- Markdown files referenced by build/packaging-classified files: **4**
- Unresolved Markdown-like reference tokens found during bounded text scanning: **250**

| Migration decision | Files |
|---|---:|
| `MOVE_TO_GRAPHIFY_LATER` | 158 |
| `RETAIN_IN_CODEBASE_FIXTURE_PENDING_ANALYSIS` | 49 |

No Markdown was moved. Fixture Markdown is retained pending fixture semantics and test-discovery proof. Generated Markdown is mapped separately pending generator-provenance review. Other repository Markdown receives a planned Graphify destination; legal Markdown also receives a planned plain-text distribution notice.

## Binary, runtime, archive, and platform assets

- Binary/runtime inventory records: **1,056**
- Runtime-asset candidates: **924**
- Archive records: **25**
- Platform-file records: **892**

| Detected platform | Files |
|---|---:|
| `IOS` | 735 |
| `ANDROID` | 132 |
| `MACOS` | 26 |
| `WINDOWS` | 15 |
| `LINUX` | 4 |

Mobile paths are represented as `UNKNOWN` in `REPOSITORY_INVENTORY.jsonl` because the locked repository schema only permits Windows, macOS, Linux, cross-platform, or unknown. `PLATFORM_FILE_INVENTORY.jsonl` preserves `ANDROID` and `IOS` explicitly.

## Classification counts

| Classification | Paths |
|---|---:|
| `SOURCE` | 6,520 |
| `UNKNOWN` | 2,336 |
| `TEST` | 1,100 |
| `ASSET` | 673 |
| `GENERATED` | 437 |
| `FIXTURE` | 433 |
| `BUILD` | 388 |
| `MIGRATION` | 244 |
| `DOCUMENTATION` | 198 |
| `PACKAGING` | 196 |
| `CONFIG` | 58 |
| `LEGAL` | 36 |
| `VENDOR` | 9 |

## Language counts

| Language | Files |
|---|---:|
| `TypeScript` | 5,871 |
| `TypeScript JSX` | 1,110 |
| `JSON` | 603 |
| `Swift` | 560 |
| `SVG` | 500 |
| `Markdown` | 207 |
| `GraphQL` | 199 |
| `Rust` | 167 |
| `SQL` | 119 |
| `YAML` | 77 |
| `Kotlin` | 38 |
| `JavaScript` | 34 |
| `XML` | 26 |
| `TOML` | 17 |
| `HTML` | 13 |
| `Plain Text` | 10 |
| `Gradle` | 10 |
| `Shell` | 8 |
| `CSS` | 7 |
| `Vue` | 5 |
| `Lockfile` | 3 |
| `Properties` | 3 |
| `Java` | 2 |
| `Property List` | 2 |
| `C/C++ Header` | 2 |
| `Dockerfile` | 1 |
| `C` | 1 |

## Largest checked-in files

| Path | Bytes | SHA-256 |
|---|---:|---|
| `Codebase/packages/frontend/core/public/static/githubStar.mp4` | 7,162,602 | `9d3f5f06e71c7df45cc7200bb3839d021fe69baefa81dd50a4ffcd93872c6ffa` |
| `Codebase/packages/frontend/core/public/static/e93536e1be97e3b5206d43bf0793fdef24e60044d174f0abdefebe08.gif` | 7,131,805 | `c3a8d25ed59a04c1410a73d8539c407518bacede00c23b6f3d04028ccce7c4e1` |
| `Codebase/.yarn/releases/yarn-4.13.0.cjs` | 3,004,059 | `730e0619753d39754c9e7613c7e57f084ea18b3244f5ba9a5a60bd3da048450b` |
| `Codebase/packages/frontend/templates/edgeless-snapshot/Marketing/User Journey Map.zip` | 2,397,485 | `176e541a8787c7e6a187645bca63465b8278ed5b5b96babdbc30163f46cb8a9d` |
| `Codebase/packages/frontend/core/src/blocksuite/ai/components/ai-chat-messages/templates/redHat.zip` | 2,040,802 | `0b7d180ddd0b524106cd0ee2815326ec9b5f00790aae48d9cfdc8b703216c4e9` |
| `Codebase/packages/frontend/core/src/blocksuite/ai/components/ai-chat-messages/templates/completeWritingWithAI.zip` | 1,853,515 | `caa0afa8fe5b307833a09ed229f032b03a3b222375ad1c75898d1127564a8a02` |
| `Codebase/packages/frontend/core/public/static/newIssue.mp4` | 1,846,013 | `dced1bb4187dd227525dde816fa0c4f812893dda6cd8518410e6134997f05078` |
| `Codebase/tests/fixtures/affine-preview.png` | 1,801,390 | `4726baa1a7e1a28c4d581a24b66856d941510bf4f83ceb7f36ab4712b20347d3` |
| `Codebase/packages/frontend/core/src/blocksuite/ai/components/ai-chat-messages/templates/freelyCommunicateWithAI.zip` | 1,602,688 | `9ddb39599dda2278035224cbeed8d4122ce756e505f24ddb837c67a71095e524` |
| `Codebase/packages/frontend/core/src/blocksuite/ai/components/ai-chat-messages/templates/TidyMindMapV3.zip` | 1,492,759 | `9fcdb0a09c2b18936b8417bb15dc9fe02521876a4bef98560c9ccf18f12bc772` |
| `Codebase/tests/fixtures/large-image.png` | 1,460,644 | `79e423d3952da64dcfe939b84937df395970d07a1e46b2cce0f7e5c00c6b801f` |
| `Codebase/packages/frontend/core/public/static/9288be57321c8772d04e05dbb69a22742372b3534442607a2d6a9998.gif` | 1,459,339 | `d8b124e2f2a66233b208fff3cc6a4966cd799541fed59cc4343098e9a0fdcea0` |
| `Codebase/yarn.lock` | 1,316,158 | `4d00a2e861c27561ebd229f7d90bd4f03e2d786fdfe8ba0eb289cca0967cb991` |
| `Codebase/packages/frontend/core/public/static/1326bc48553a572c6756d9ee1b30a0dfdda26222fc2d2c872b14e609.gif` | 1,315,689 | `1bf57ddd624f2748a3777166938bfd94a5883495362a08ac758a2f8b27b0fad4` |
| `Codebase/packages/common/native/fixtures/demo.docx` | 1,311,881 | `269329fc7ae54b3f289b3ac52efde387edc2e566ef9a48d637e841022c7e0eab` |
| `Codebase/packages/frontend/core/src/blocksuite/ai/components/ai-chat-messages/templates/readAforeign.zip` | 1,285,629 | `a92f5cfd53ac6424b993107e69b4e4627bbfd9aa0c239caee26899b58d3897c7` |
| `Codebase/packages/frontend/apps/electron/resources/icons/icon.png` | 1,227,964 | `ebe51d85be1c03afcaf1198676013bae7093b920199bcad04e5990a24667a7dc` |
| `Codebase/packages/frontend/component/src/fonts/source-serif-4/SourceSerif4-VariableFont_opsz,wght.ttf` | 1,195,360 | `73ebc46873043020c5764481ccbd3b7ac4bcb33e538e538b5f2648c9291612be` |
| `Codebase/packages/frontend/native/__tests__/fixtures/recording.wav` | 1,042,476 | `404beba47305f97a08f0de2ce24ee4873e67d359337062603a6eaf4aa6ddfe1b` |
| `Codebase/packages/frontend/core/public/static/6aa785ee927547ce9dd9d7b43e01eac948337fe57571443e87bc3a60.png` | 967,286 | `dccb6c26d1407c4205e800ab5c9a7e8d83576726b08e36ade0a556ffb8801c10` |

## Validation

- All seven JSON/JSONL/Markdown deliverables were populated.
- Every discovered file and directory has exactly one repository-inventory record.
- Every regular file and archive has a 64-character lowercase SHA-256.
- Required repository-inventory fields and enums validate.
- JSON and JSONL parse validation passed.
- Markdown, archive, binary/runtime, and platform subset paths resolve to repository-inventory records.
- No Codebase files were written, moved, deleted, formatted, quarantined, or installed into.

## Limitations and handoff

- `trackedState` cannot be resolved beyond `UNKNOWN` without authentic Git metadata and its index.
- Runtime reachability is intentionally `UNKNOWN` unless the inventory role proves non-runtime; architecture/runtime-registration agents must establish executable reachability.
- Platform content detection is a discovery signal, not proof of an executable platform branch.
- Markdown link discovery reads non-binary files up to 5 MiB and resolves explicit `.md`/`.markdown` path tokens; unresolved tokens are counted but are not fabricated as links.
- Archive inspection reads ZIP central directories and TAR metadata without extraction; unsupported formats remain metadata-only.
- Licence/provenance conclusions belong to the separate licence mapping and are not inferred here.
- Ponytail Audit was classification-only in this slice; no cleanup recommendation is promoted to deletion proof and no source change was applied.
