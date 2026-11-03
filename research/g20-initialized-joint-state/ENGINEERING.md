# Implementation bounds and checks

The engineering-mode playbook is **Autonomous local run**. Its exit predicate
is one original, checked scoped result or a concrete negative handoff. The
first joint-closure experiment supplied a smaller state representation; no
larger family search followed. Build the Lever led to the rerunnable constructor
and integer-prefix checker. Prove It Works led to every-edge checking and
complete forward/output/return executions. Unslop guided the prose.

Only the new package changes. The source column and existing packages are
read-only. The verifier never imports or runs predecessor scientific code.
No global mutable registry, reflection, generated executable code or recursion
is introduced. The constructor, forward and reverse paths call fixed functions.
Every changed function is below 60 physical lines. Checks use explicit
exceptions and remain enabled under optimized Python.

## Power of Ten bounds

- Initialization constructs at most 32,768 states, each with thirteen threshold
  integers and four comparison flags. The actual closure has 23,789 states.
  Each state has exactly 32 outgoing edges. Every transition, state-label and
  active-rank insertion is range-checked before storage. There are at most
  1,048,576 edges, each with one 16-bit target and one 8-bit active rank.
- Inverse construction has 32 bounded passes over those states. It retains
  at most one inverse entry per edge. Every prefix witness uses at most 128
  binary rows, checked before retention. The source file has a fixed checked
  size of 212,442 bytes and is authenticated before its operation list is used.
- Executable streams contain at most 4,097 immutable nine-bit tuples. The
  history register has at most `bit_length(3248^4097-1)` bits. Forward and reverse
  each process exactly the stream length, with at most four comparison steps
  per row. Integer temporaries and direct modular-oracle inputs inherit that
  width bound. Empty, invalid-canonical and ill-typed inputs have separate checks.
- Static diagnostic loops use 32 letters, at most 32,768 states, at most
  `5^4` canonical active inputs per displayed modulus, 64 dirty outputs,
  exactly `32^3` short streams, seven long lengths and ten negative controls.
  No waits, retries, queues or process creation occur in the retained code.
- Runtime checks enforce source identity, state/rank capacities, closure,
  exact integer-prefix semantics, inverse consistency, packet/validity,
  nonzero history rejection and all prepared-state restoration. Return values
  are checked, propagated or intentionally used as diagnostic output.
- The package hook runs `-W error` in normal and optimized Python. No separate
  Python compiler, type checker or linter is required by this isolated
  standard-library package; `ruff` and `mypy` were unavailable on PATH. Syntax
  and diagnostics are exercised through the real imports and both replays.
  Existing shared tooling is unchanged.

## Managed-runtime deviation

Rule: 3, fixed allocation before steady operation.
Location: `model.py`, `verify.py` and their Python runtime.
Reason: Python integers, tuples, dictionaries and arithmetic allocate during
operation; static allocation would require a separate packed native backend.
Scope: the finite compiler, bounded verifier and sample logical producer.
Compensating control: explicit state, edge, source-byte, witness-depth and stream
limits above bound live structures and integer widths. Each invocation is a
single process with a 120-second registered timeout. No persistent files or
child processes are created.
Verification: complete construction, all-edge and inverse checks, a 4,097-row
return and rejection of a 4,098-row stream run in both diagnostic modes.
Follow-up: any physical storage claim must replace these Python containers with
an emitted packed backend and measure its entire allocation and lookup cost.

The ideal packed table capacity is a declared layout count, not an allocation
measurement. The all-width mathematical induction does not remove the explicit
bounds on this executable. Physical runtime and peak heap measurements are not
claimed. All five selected framework assumptions remain outside this check.
