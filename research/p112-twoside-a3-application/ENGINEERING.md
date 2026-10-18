# Implementation bounds and verification scope

Separate Before Serializing Shared State gave this worker its own branch,
package and cache. Shared Git metadata operations use the orchestration's
short-lived OS-released lock. Prove It Works led to authenticating the exact
pending proof bytes and checking the literal original profile, rather than
inferring applicability from a profile title.

The new verifier has no recursion or dynamic evaluation. The registered
domain has at most 11 pieces; the shared predicate accepts at most 14,
weights 2 through 7, dimension 5 through 8 and allowance 1 through 6.
The registered cell loops over exactly 11,452 multisets; each filter has
at most 8 deletion levels and at most 2^6 bin assignments.
The independent filter uses at most 4 items and subset sums bounded by 28.
All new functions are below 60 physical lines. Exceptions propagate as failed
replays. Explicit require checks remain active under Python optimization.

Power of Ten rules 3 and 9 have managed-runtime deviations. Python and unittest
allocate dynamically and dispatch through framework methods. Input sizes and
the fixed finite domain bound live memory; unittest owns its temporary
directory with scoped cleanup. Authentication allows six retained files, with
each under 100 KiB, and one live data input under 2 MiB. No new callback framework,
ambient singleton or mutable cross-worker state is introduced.

Source scripts retained from PR3154 include recursion and broader loops.
They are unmodified archival text, authenticated but never executed by this
package. No new code relies on their runtime behavior. Their predicates are
reimplemented locally in bounded iterative code.

Diagnostics are warnings-as-errors, standard-library behavioral controls,
available Ruff checks and git diff whitespace validation. The inherited
788,035-flat, 2,025-puncture and root/chamber replays are explicitly unrun.
No formal proof, full selected cold replay, Lean or Docker run is claimed.
