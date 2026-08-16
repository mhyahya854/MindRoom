# MindRoom Execution Governance Architecture

This document is the canonical explanation of the two-phase governance boundary introduced by change control `WAVE0-execution-governance`.

## Lifecycle phases

The repository explicitly supports:

```text
PRE_IMPLEMENTATION_FROZEN
    -> explicit user authorization
IMPLEMENTATION_IN_PROGRESS
    -> successful task receipts
WAVE_BOUNDARY_CERTIFICATION
    -> later waves
FINAL_RELEASE_CERTIFICATION
```

The canonical lifecycle field is `lifecyclePhase` in `Graphify/00 Execution Control/STATUS.json`.

## PRE_IMPLEMENTATION_FROZEN

In this phase:

- `wave0Readiness` is `READY_NOT_STARTED`
- `codebaseExecutionStatus` is `BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION`
- `implementationPerformed` is `false`
- `applicationReleased` is `false`

The only valid governance proof is:

```text
FINAL_FREEZE_CERTIFICATION
```

This certification requires the live Codebase to be byte-identical to the original frozen baseline:

- Git tree: `bbf383e3418da4f613f58719160bb7cbd5709ffc`
- files: `10080`
- directories: `2548`
- aggregate SHA-256: `91600fc76001d8b2c108634d4fa3ceca5e743176f103a44d21b7e0e7273ec748`

`verify_step11b_results.py` remains the pre-start verifier and MUST NOT be used after implementation starts.

## IMPLEMENTATION_IN_PROGRESS

After explicit user authorization and after the first successful task publication, the lifecycle transitions to `IMPLEMENTATION_IN_PROGRESS`.

In this phase:

- `wave0Readiness` is `WAVE_0_IN_PROGRESS`
- `codebaseExecutionStatus` is `AUTHORIZED`
- `implementationPerformed` is `true`
- `applicationReleased` remains `false`
- `EXECUTION_AUTHORIZATION_RECORD.json` records the explicit user authorization

The only valid governance proof is:

```text
IMPLEMENTATION_EXECUTION_CERTIFICATION
```

provided by `validate_execution_state.py` and verified by `verify_execution_state.py`.

The execution certification is fail-closed. Every live Codebase byte must be attributable to a successfully completed canonical implementation task receipt whose:

- starting tree equals the previous trusted ending tree
- ending tree equals the current trusted live tree
- path delta is inside the canonical task allowed scope
- pre/post immutable checkpoints exist
- dependency prerequisites were already complete
- receipt was published to `main`

Failed `wip/**` branches are never completion authority.

## Original baseline is immutable

`EXECUTION_TRUSTED_BASELINE.json` permanently records:

- `originalFrozenCodebaseTree`
- `currentTrustedCodebaseTree`

The original frozen tree is never overwritten. The current trusted tree advances only through valid task receipts.

## Step 11b and the execution verifier

This change control deliberately uses Option B:

- `verify_step11b_results.py` remains the pre-start verifier.
- `verify_execution_state.py` is the post-start verifier.

There is no ambiguous dual authority. The lifecycle phase selects which verifier is canonical.
