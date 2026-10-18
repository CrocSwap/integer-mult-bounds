# Verification boundary and implementation decisions

This package checks only the frozen emitted scalar reference programs. It does
not implement a physical caller, recursive child or frame adapter.

Build the lever shaped the choice to retain two rerunnable envelope interpreters,
rather than a hand-computed denominator census. Prove it works shaped the choice
to regenerate the native streams, check complete endpoints and reject reduced
precision before reporting an envelope.

## Resource and control-flow review

1. New code has no recursion or callback registration. Primary symbolic rows use
   direct sparse rational arithmetic. The audit uses direct integer arithmetic.
2. Input files and decompressed JSON are capped at 8,000,000 bytes. A primary
   stream has at most 30,000 events, 768 live role names, 4096 terms per row and
   256 symbols per reduced warp word. Private/ordinary indices are bounded.
   The audit receives these already-validated, source-bound streams, also caps
   events/row sizes, and independently checks arithmetic divisions/endpoints.
3. Python cannot prohibit steady-state allocation. This is an explicit rule-3
   deviation for the two finite interpreters, not a claim of allocation-free
   execution. The caps above bound live symbolic state; event-local temporary
   rows have at most twice the capped source/target size before validation.
   Rational denominators and row masses are capped at 256 bits and 2^192 after
   every changed row. Follow-up, if promoting this to a production checker, is
   a fixed-capacity integer-row implementation with measured allocator limits.
4. Every new function is at most 60 formatted physical lines. The retained
   native scripts are frozen predecessors, not refactored or extended here.
5. Executable contracts check sources, alphabets, grid bounds, allocation,
   endpoint maps, source alignment and integral division. They remain enabled
   under `-O`. Assertions are reserved for unittest expectations. The retained
   emitters require assertions and run as separate nonoptimized interpreters.
6. State is local to one replay. The only constants are bounds/package paths.
   There are no shared mutable caches or asynchronous workers.
7. Child failures propagate through checked subprocess calls. Every native
   child has a 90-second timeout. Outputs must be fresh and external. A
   TemporaryDirectory owns ordinary replay outputs and removes them on exit.
   Explicit `--work` preserves diagnostics intentionally. Source/output failure
   paths are exercised in the behavioral suite.
8. There is no dynamic evaluation in new code. The native child scripts are
   authenticated byte-for-byte before interpreter execution. Import resolution
   uses package-local source and a fresh bytecode namespace for child processes.
9. New code uses direct calls and shallow immutable tuple keys. Dictionary row
   traversal is the managed-runtime equivalent of reference access, not pointer
   arithmetic. No new dispatch framework is introduced.
10. Applicable correctness/style diagnostics are Ruff E,F,I,B,UP,SIM,RUF,C90
    plus Ruff formatting, Python warnings as errors and source compilation.
    The all-rules inspection also reports annotation/docstring, pytest versus
    unittest, layout and other style preferences that do not define this
    repository's untyped research-script interface. S603 flags the subprocess
    calls; they use direct argument lists, authenticated scripts and no shell,
    with failure/timeout propagation as described above. No diagnostic
    suppression was added. Opt-in registered replay runs both
    mathematical implementations and the behavioral suite on Python 3.12.

## Frozen-source deviations

The native transport/emitter scripts retain their original global state,
assertions, dynamic allocation, function lengths and CRLF source bytes. The
package-local Git whitespace attribute recognizes those preserved line endings. Rewriting those exact
sources would invalidate the intended source-bound comparison and expand this
result into compiler maintenance. Compensating controls are SHA-256 checks
before execution, two 90-second child bounds per provider, bounded emitted
streams, complete native endpoint checks, and two new endpoint/envelope
interpreters. Follow-up compiler hardening belongs in a separate source-pinned
change. This package neither weakens inherited checks nor adds a dependency on
a new native-code path.

## Research decisions

- Reused the idle sparse worktree and preserved its previous branch. Canonical
  main and priority revision 6 were fetched before the new branch.
- Checked live handoffs and complete open-PR/Discussion pagination. A brief
  local centre-repair subgroup probe found no closed group before its cap; it
  supplies no exclusion and is not part of this result.
- Took the concrete PR3081/3080 arithmetic handoff rather than repeating the
  already-covered rank/frame/moment checks. This is a declared scope change.
- Stopped at the exact scalar reference envelope. Unknown physical adapter,
  ownership, routing, clean stock and consumer charges are not zero. No further
  construction or selected-frontier update is justified by this local result.
