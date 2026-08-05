# ADR-0006: Local Semantic Index Architecture

Status: `ACCEPTED`
Decision Date: 2026-07-30T18:27:00.634Z

## Context
MindRoom requires local semantic search and knowledge graph relationship suggestions across documents, notes, canvas blocks, and mind maps without depending on remote cloud AI inference or cloud vector databases.

## Problem
How to provide fast, local-only semantic suggestions while preserving deterministic search as the baseline, preventing unconfirmed suggestions from modifying user documents, and allowing users to delete or rebuild index projections at will.

## Constraints
- 100% local operation; no OpenAI, Gemini, or remote inference APIs.
- Ordinary markdown/JSON files remain the sole authoritative source of truth.
- Vector indexes must be rebuildable projections.
- Explicit user confirmation required before any suggested link becomes permanent.

## Repository Evidence Inspected
- `Codebase/packages/frontend/core/package.json` (Line 1-20) - Core frontend app bundle configuration.
- `Codebase/blocksuite/affine/model/src/elements/mindmap/mindmap.ts` (Line 12-60) - Mindmap element model.

## Options Considered
1. Remote OpenAI embeddings API.
2. Local sqlite-vss vector extension with Transformers.js ONNX embedding pipeline.
3. Pure keyword TF-IDF indexing.

## Selected Architecture
Adopt local sqlite-vss / HNSW vector index projection stored in `.mindroom/indexes/semantic.sqlite`. Deterministic text search remains the authoritative baseline. Local embeddings generated via ONNX runtime serve as an optional, rebuildable projection. Suggestions remain temporary until explicitly confirmed by the user.

## Rejected Alternatives
- Remote OpenAI Embeddings API: Rejected due to cloud privacy breach and offline failure.
- Pure TF-IDF: Rejected due to lack of conceptual semantic matching.

## Detailed Rationale
Using a local SQLite vector projection ensures sub-50ms vector query performance while retaining file-backed durability. Index corruption can be fixed by deleting `semantic.sqlite` and running a local re-index.

## Data Contracts
- `embeddingModel`: `all-MiniLM-L6-v2` (384-dimensional dense vectors).
- `suggestionRecord`: `{ suggestionId, sourceDocId, targetDocId, similarityScore, status: "PENDING" | "ACCEPTED" | "REJECTED" }`.

## Public Interfaces
- `ISemanticIndexService.search(vector: Float32Array, topK: number): Promise<SemanticMatch[]>`
- `ISemanticSuggestionProvider.generateSuggestions(docId: string): Promise<Suggestion[]>`

## Storage Behavior
Authoritative storage: Local markdown/JSON files. Rebuildable index: `.mindroom/indexes/semantic.sqlite`.

## Identity Behavior
Stable doc/block UUIDs preserved across vector updates.

## Privacy and Security Impact
Zero outbound network calls. All embeddings generated in local browser/Electron process.

## Offline Behavior
Operates 100% offline.

## Migration Impact
`NOT_APPLICABLE — REBUILDABLE_LOCAL_PROJECTION`

## Recovery Behavior
Delete `.mindroom/indexes/semantic.sqlite` and execute `SemanticIndexBuilder.rebuild()`.

## Failure Behavior
If local embedding pipeline fails, system falls back to deterministic full-text search.

## Rollback Behavior
Delete `.mindroom/indexes/semantic.sqlite`.

## Testing Requirements
- Unit test vector generation.
- Integration test index rebuild.
- Offline isolation test verifying zero network calls.

## Affected Capabilities
`MR-CAP-154`, `MR-CAP-155`, `MR-CAP-156`, `MR-CAP-157`

## Affected Implementation Tasks
`MR-TASK-154`, `MR-TASK-155`, `MR-TASK-156`, `MR-TASK-157`

## Affected Release Waves
`WAVE_2`

## Dependencies
BlockSuite Model, Local SQLite

## Consequences
Faster semantic discovery with 0 cloud leakage.

## Known Limitations
First index build requires CPU cycles for local ONNX inference.

## Future Extension Points
Pluggable local GGUF / ONNX models via WebGPU.
