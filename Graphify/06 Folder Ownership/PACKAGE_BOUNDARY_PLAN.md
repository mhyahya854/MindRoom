# MindRoom Graphify Package Boundary Plan

- Updated: 2026-07-30T18:30:35.167Z
- Package Manager: **Yarn 4.13.0**
- Workspace Glob Match: `packages/*/*` matches `packages/common/mindroom/`
- Shared Package Path: `Codebase/packages/common/mindroom/` (`@mindroom/common`)
- Shared Package Dependency Cycles: **0**

## Domain & Runtime Boundaries
1. **Shared/Domain Layer** (`@mindroom/common`): Pure domain models, zero dependencies on `@affine/core`, admin app, or backend server.
2. **Electron Main Process**: Owns `safeStorage`, atomic file persistence, native SQLite, and worker process orchestration. Zero key exposure to renderer.
3. **Renderer Process**: Interacts exclusively via typed Preload IPC bridge.
4. **Finance Chart Boundary**: `USE_UNDERLYING_CHART_LIBRARY_DIRECTLY` / `REFERENCE_ONLY`. Zero import of `packages/frontend/admin/`.
5. **Finance CSV Boundary**: `CREATE_SHARED_IMPORT_EXPORT_UTILITY` / `REFERENCE_ONLY`. Zero import of `packages/frontend/admin/`.
6. **Calendar Adapters**: Google Calendar and CalDAV isolated as optional adapters in `CalendarAdapterRegistry`. Core calendar operates 100% offline.
7. **Semantic Vector Index**: `SQLite extension providing vector search` (sqlite-vss) with ONNX local embeddings and deterministic search fallback.
8. **Receipt OCR Boundary**: `DEFER` / `OPTIONAL_LATER_CAPABILITY`. Removed from mandatory receipt exit conditions.
