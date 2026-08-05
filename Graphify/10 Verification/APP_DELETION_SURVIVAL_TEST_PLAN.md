# MindRoom App-Deletion Survival Test Plan

- Updated: 2026-07-30T18:39:02.850Z
- Purpose: Verify user data persistence across application reinstalls and binary cleanups.

## 9-Step Verification Procedure
1. Create representative user data across documents, calendar, finance, canvas, mindmaps, and relationships.
2. Flush and close application processes.
3. Preserve only user-owned workspace directory (`.mindroom/` and user folders).
4. Delete application binaries, temp files, and rebuildable caches (`semantic.sqlite`).
5. Reinstall application.
6. Rediscover user-owned workspace files.
7. Rebuild local SQLite projections and search indexes.
8. Verify file checksums, event recurrences, ledger balances, and document links.
9. Generate app-deletion survival receipt.
