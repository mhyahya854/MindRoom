# ADR-0004: Global graph projection versus cache

Status: `ACCEPTED`

Run: `mindroom-graphify-forensic-finalization-20260730-150956`

## Context

This planning decision is governed by the additive MindRoom product-expansion contract, the original hardened Master Plans, local-first/file-backed safety rules, and source-exact AFFiNE preservation requirements.

## Decision

The global graph is a computed federated projection/cache rebuilt from authoritative source files and local maps; it must not duplicate source-map ownership.

## Implementation interlock

The product-level decision is accepted; implementation still requires its mapped task, tests, and independent review.

## Consequences

- No Codebase implementation is authorised by this ADR.
- Existing compatible AFFiNE/BlockSuite behavior remains preserved.
- Ordinary-file durability, offline operation, recovery, provenance, and privacy protections remain mandatory.
