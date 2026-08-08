# ADR-0010: Finance Transaction Storage Format

Status: `ACCEPTED`
Decision Date: 2026-07-30T18:27:00.638Z

## Context
MindRoom Finance requires an append-safe, audit-verifiable local transaction storage model.

## Problem
How to store financial accounts, transactions, and transfers accurately without floating-point rounding errors or data corruption.

## Constraints
- Monetary amounts must use decimal strings (e.g. `"125.50"`).
- Double-entry transaction ledger history is append-only and immutable.
- SQLite used strictly for rebuildable query projections.
- Zero dependence on Stripe, RevenueCat, or commercial billing SDKs.

## Repository Evidence Inspected
- `Codebase/blocksuite/affine/blocks/database/src/database-block.ts` (Line 10-50) - Database block model.
- `Codebase/packages/backend/server/src/base/storage/index.ts` (Line 15-60) - Storage provider.

## Options Considered
1. Floating-point numbers in a single JSON file.
2. Append-only JSONL transaction ledger + JSON metadata + rebuildable SQLite projections.

## Selected Architecture
Adopt versioned append-only JSONL (`ledger.jsonl`) for immutable transaction history. Account balances and query views are derived projections stored in local SQLite (`finance_queries.sqlite`). Monetary amounts stored as explicit decimal strings with currency codes.

## Rejected Alternatives
- Floating-point storage: Rejected due to IEEE 754 precision loss.
- Stripe/RevenueCat billing SDKs: Rejected due to commercial cloud dependency.

## Detailed Rationale
Append-only JSONL prevents accidental loss of transaction history and permits complete audit verification and projection rebuilds.

## Data Contracts
- `LedgerTransactionRecord`: `{ recordId, transactionId, timestamp, accountId, amount: "1250.00", currency: "USD", type: "DEBIT" | "CREDIT", categoryId, description, status: "POSTED" }`

## Public Interfaces
- `IFinanceLedger.postTransaction(record: TransactionInput): Promise<TransactionReceipt>`
- `IFinanceProjectionBuilder.rebuildProjections(): Promise<void>`

## Storage Behavior
Authoritative storage: `MindRoom/finance/ledger.jsonl`. Derived projection: `finance_queries.sqlite`.

## Identity Behavior
Immutable `transactionId`, `accountId`, `transferId` UUIDs.

## Privacy and Security Impact
Local file storage; no remote payment API integration.

## Offline Behavior
100% offline execution.

## Migration Impact
`NOT_APPLICABLE — NEW_FINANCE_LEDGER`

## Recovery Behavior
Execute `FinanceProjectionBuilder.rebuildProjections()` from `ledger.jsonl`.

## Failure Behavior
Failed write leaves `ledger.jsonl` untouched; transaction rejected cleanly.

## Rollback Behavior
Revert `ledger.jsonl` to last verified record offset.

## Testing Requirements
- Unit test decimal string arithmetic.
- Integration test projection rebuild from ledger.

## Affected Capabilities
`MR-CAP-016`, `MR-CAP-121`, `MR-CAP-122`, `MR-CAP-123`, `MR-CAP-125`, `MR-CAP-126`, `MR-CAP-129`

## Affected Implementation Tasks
`MR-TASK-016`, `MR-TASK-121`, `MR-TASK-122`, `MR-TASK-123`, `MR-TASK-125`, `MR-TASK-126`, `MR-TASK-129`

## Affected Release Waves
`WAVE_1`

## Dependencies
BlockSuite DB

## Consequences
Exact, audit-verifiable local finance ledger.

## Known Limitations
Large ledgers (>500k entries) require background thread projection rebuilds.

## Future Extension Points
Custom budget categorization rules.
