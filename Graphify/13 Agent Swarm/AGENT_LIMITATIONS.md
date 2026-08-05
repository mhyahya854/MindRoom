# Agent Swarm Limitations

- A real dependency-safe wave ran with three subagents plus the orchestrator, which is the runtime concurrency limit.
- The inventory, architecture/runtime-registration, and capability/plan agents produced the handoffs recorded in `AGENT_HANDOFFS.jsonl`.
- Subsequent agent reuse and the independent-review wave failed because the external subagent usage limit was reached. The orchestrator continued sequentially, as required, and did not invent reviewer activity.
- `AGENT_REVIEWS.jsonl` is intentionally empty: no independent review passed, and implementing/integrating work was not self-approved.
- The orchestrator's deterministic validators are labelled self-validation evidence only. They do not satisfy the locked independent-review gate.
- Codebase remained read-only for every agent. Generated artifacts were restricted to Graphify paths.
