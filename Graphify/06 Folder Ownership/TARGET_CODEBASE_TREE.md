# MindRoom Target Codebase Tree Layout

- Updated: 2026-07-30T18:30:35.170Z

```text
Codebase/
├── packages/
│   ├── common/
│   │   ├── mindroom/                # [NEW] Shared MindRoom Domain Package (@mindroom/common)
│   │   │   ├── package.json
│   │   │   ├── tsconfig.json
│   │   │   └── src/
│   │   │       ├── calendar/
│   │   │       ├── finance/
│   │   │       ├── canvas/
│   │   │       ├── mindmap/
│   │   │       └── linking/
│   ├── frontend/
│   │   ├── core/                    # Retained AFFiNE Frontend Core
│   │   ├── electron/                # Retained Electron Main Process & safeStorage Provider
│   │   └── admin/                   # REFERENCE_ONLY (Excluded from Finance runtime imports)
```
