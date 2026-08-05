# Ponytail Whole-Repository Audit

Run: `graphify-v2-repair-20260728T095646`

Ponytail mode: READ_ONLY_AUDIT  
Code changes applied: 0  
Dependencies removed: 0  
Files deleted: 0

1. [high] delete 74 lines — i18n cleanup.mjs is a validated future candidate; build.ts owns the registered workflow.
2. [high] remove 1 direct dependency — GraphQL package lodash is a validated future candidate after codegen parity proof.
3. [medium] consolidate 12 lines — workspace-tab styles share one owner and remain a future reviewed batch.
4. [review] navigation duplicates — split platform/ownership cases before any consolidation decision.
5. [review] tools/utils lodash-es — once semantics and build-critical callers require focused proof.
6. [false positive] upgrade styles — keep route-owned styles with future removal batches; isolate orphan proof.
7. [false positive] Slack renderers — separate package ownership outweighs byte identity.
8. [false positive] page-history range — replacement is not smaller and removes no dependency.
9. [false positive] snapshot noop — cosmetic replacement does not simplify ownership or dependencies.

Byte-identical code was not accepted as sufficient consolidation evidence. Every finding was rechecked for callers, exports, runtime/build registration, platform ownership, generated state, tests, packaging, licence scope, and future removal intent.

net: -86 lines, -1 deps possible
