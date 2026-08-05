# ADR-0007: Semantic suggestion persistence

Status: `ACCEPTED`

Run: `mindroom-graphify-forensic-finalization-20260730-150956`

## Context

This planning decision is governed by the additive MindRoom product-expansion contract, the original hardened Master Plans, local-first/file-backed safety rules, and source-exact AFFiNE preservation requirements.

## Decision

Suggestions are derived; confirmations, rejections, dismissals, provenance, and confidence decisions are durable. Silent acceptance is forbidden.

## Implementation interlock

The product-level decision is accepted; implementation still requires its mapped task, tests, and independent review.

## Consequences

- No Codebase implementation is authorised by this ADR.
- Existing compatible AFFiNE/BlockSuite behavior remains preserved.
- Ordinary-file durability, offline operation, recovery, provenance, and privacy protections remain mandatory.
