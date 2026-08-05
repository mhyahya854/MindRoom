# ADR-0012: Multi-Currency Behavior

Status: `ACCEPTED`
Decision Date: 2026-07-30T18:27:00.638Z

## Context
MindRoom Finance supports tracking transactions and accounts across multiple currencies.

## Problem
How to handle multi-currency conversions and historical exchange rates without requiring live remote rate feeds or altering historical transaction amounts.

## Constraints
- ISO 4217 currency codes (`USD`, `EUR`, `GBP`, `JPY`, etc.).
- Original transaction amount and currency code are immutable.
- Exchange rate snapshots stored as explicit immutable records.
- Zero mandatory live rate server dependency.

## Repository Evidence Inspected
- `Codebase/blocksuite/affine/blocks/database/src/database-block.ts` (Line 10-50) - Database block model.

## Options Considered
1. Overwriting original amounts with converted base currency values.
2. Preserving original amount/currency + immutable exchange rate snapshots + optional user-entered rates.

## Selected Architecture
Preserve original amount and currency code in all transaction records. Multi-currency reporting uses immutable `ExchangeRateSnapshot` records stored locally. Users can manually enter rates or import CSV rate tables.

## Rejected Alternatives
- Overwriting original amounts: Rejected due to loss of transaction fidelity.

## Detailed Rationale
Preserving original amounts ensures financial history remains accurate regardless of future exchange rate updates.

## Data Contracts
- `ExchangeRateSnapshot`: `{ rateSnapshotId, baseCurrency: "EUR", quoteCurrency: "USD", rate: "1.0850", observedAt: "2026-07-30T00:00:00Z", isUserProvided: true }`

## Public Interfaces
- `ICurrencyConverter.convert(amount: string, from: string, to: string, date: Date): Promise<string>`
- `IRateRepository.addRateSnapshot(snapshot: ExchangeRateSnapshot): Promise<void>`

## Storage Behavior
Rates stored in `MindRoom/finance/rates.json`.

## Identity Behavior
`rateSnapshotId` UUID v4.

## Privacy and Security Impact
Stored locally in user workspace.

## Offline Behavior
100% offline operation.

## Migration Impact
`NOT_APPLICABLE — NEW_MULTI_CURRENCY_SCHEMA`

## Recovery Behavior
Re-read `rates.json` snapshot table.

## Failure Behavior
Missing exchange rate reports unconverted amount with explicit `RATE_UNAVAILABLE` warning.

## Rollback Behavior
Revert `rates.json`.

## Testing Requirements
- Unit test zero-decimal currency (JPY) conversions.
- Unit test multi-currency ledger balance calculations.

## Affected Capabilities
`MR-CAP-131`

## Affected Implementation Tasks
`MR-TASK-131`

## Affected Release Waves
`WAVE_2`

## Dependencies
Finance Ledger Core

## Consequences
Lossless multi-currency accounting.

## Known Limitations
Historical rate lookup defaults to nearest available snapshot date.

## Future Extension Points
Optional manual CSV rate table import.
