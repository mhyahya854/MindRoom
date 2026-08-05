# MindRoom Fixture & QA Test Matrix

- Updated: 2026-07-30T18:39:02.850Z
- Total Test Fixtures: 24
- Coverage: Empty workspace, small workspace, large workspace, calendar events, finance ledgers, canvas blocks, mindmap elements, encrypted vaults, offline sandboxes.

| Fixture ID | Domain | Purpose | Source Format | Offline Safety |
|---|---|---|---|---|
| `FIX-empty-workspace` | Core | Initial setup testing | Clean Folder | Local |
| `FIX-calendar-events` | Calendar | RRULE recurrence testing | Local JSON | Local |
| `FIX-finance-ledger` | Finance | Append-only transaction testing | JSONL Ledger | Local |
| `FIX-canvas-surface` | Canvas | BlockSuite edgeless surface testing | Surface JSON | Local |
| `FIX-mindmap-model` | Mindmap | Manual node reparenting testing | Mindmap JSON | Local |
| `FIX-finance-encrypted` | Vault | AES-256-GCM vault envelope testing | Encrypted JSONL | Local |
