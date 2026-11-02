# Verification contract and limits

The claim is a written all-prime, all-finite-workspace theorem. The verifier
provides exact finite corroboration of its new quotient-loop lemma and
attaining endpoints. PR5242's natural-rank theorem is a cited premise, not
an independently checked deliverable. PR6048's distinct-label floor is
credited prior work. The repeated-label extension and weighted formula are
covered by the proof in this package.

## Bounded checks

The registered normal and optimized commands use CPython 3.12 and no third
party dependencies. Both run the complete verifier. Explicit `require`
checks remain active with assertions disabled. On local CPython 3.12.15,
macOS arm64, the direct commands take less than one second each; the
registered pair takes about one second. Each manifest command has a
60-second timeout. These are check-duration observations, not a speedup.
Fresh JSON receipts are printed to stdout and bind every package file by
SHA256. No stored PASS receipt or generated mathematical artifact is read.

The pair/inverse lookup checks 32,840 pairs and 1,120 loops. A direct
triple enumeration independently checks the finite F4 two-role subcase,
including all 1,728 triples and its 12 loops. This is a second algorithm
in the same verifier, not independent human or proof-kernel review.
Full formal endpoints are compared coefficient by coefficient. Eleven
rejection controls exercise nonbinary, rank-two and nilpotent projectors,
invalid scalars and coefficient ranges, a character-only false positive, unrestored dirty output
and an altered scalar in a loop. The nonbinary counterexample passes in
its enlarged alphabet and demonstrates a real hypothesis boundary.

## Code constraints

Only `algebra.py` and `verify.py` are new executable code. They read no
external mathematical inputs, spawn no processes and write no files.
They use no recursion, dynamic evaluation, decorators or global mutable
state. All arithmetic is exact integer arithmetic over finite fields or
bitsets in the 21-dimensional group algebra. Direct calls and data access
are shallow. The verifier's finite sizes are fixed, not user-controlled.

Every loop is bounded by these constants or finite collections derived
from them: at most three roles, fields of size at most eight, 28 binary
projectors per size, 168 factors per census, 28,224 factor pairs in one
census, 21 group labels, 14 outside labels, six normal labels, 13 count
values per type and nine positive integer prices per type. The group
coefficient extractor has an explicit 21-iteration cap and rejects excess
bits. Field inversion has at most six multiplications. The largest
function is below 60 physical lines. Structured exception controls catch
only the expected `ValueError`; other failures propagate.

Rule 3 deviation: CPython allocates arithmetic objects and collections
inside loops. Fixed allocation after initialization cannot be guaranteed
in this managed runtime. Scope is this finite verifier, with the bounds
above limiting live matrices to 3 by 3, group elements to 21 bits, and one
census list to 168 factors. Pair and triple products are consumed one at
a time. There are no unbounded queues, retained histories or child processes.
The registered timeout is an additional guard. A future parameterized
search must enforce new size/capacity limits before accepting inputs.

Warning-strict source compilation, function-length inspection and normal,
optimized and registered execution cover the changed code. No Python
linter or type checker is installed in the local interpreter; those
checks are unrun. Shared CI or analysis configuration is unchanged.

## Unrun obligations

Independent human review, formal proof-kernel acceptance, native realization,
physical pricing, supplier admission and the selected scientific cold replay
remain unrun. Lean and Docker were not invoked. Hosted replay verifies the
registered finite checks and source metadata, not these obligations or the
universal mathematical proof. No selected-frontier update is requested.
