# Six necessary forms for odd-width optimal sectors

This contribution was produced by Nick Petalas. New work is Apache-2.0.

For the four-field shortest-query root with full stages at sites 0,1,3,4,
every odd-width optimum has a common endpoint sector of dimension exactly q.
Write q=2k+1. Its AB,BC,CD,ABC,BCD,ABCD sector dimensions must be

```text
(x,y,z,h,j,w) = (2k+a, k+2-a-b, 2k+b, h, k+1-h, 2k+1)
a,b >= 0, a+b <= 2,
max(0,1-a) <= h <= k+1-max(0,1-b).
```

There are six pairs (a,b) and exactly 3(q+1) inventories in this integer
relaxation. The two odd-site stage ranks each lie in {3q-1,3q,3q+1} and
differ by at most two. These are necessary conditions for actual optimal
words. This package does not claim all remaining inventories are attainable.

## Result and predecessor

The claim type is a scoped algebraic proof with finite integer corroboration.
[PROOF.md](PROOF.md) derives the exact odd integer slack and solves the
stated relaxation in both directions. It takes the sharp minimum ceil(21q/2),
sector reduction and individual image/row capacity inequalities from
[CubeJerry's PR #6781](https://github.com/CrocSwap/integer-mult-bounds/pull/6781),
at `a7f01042216c9f891157e3884beae9053e049c2f`, as mathematical premises.
That source explicitly leaves odd-q ceiling-equality inventories open.
This adds a necessary six-form reduction and a precise remaining count;
it does not recheck its matrix proof, fixtures or reported numbers.
[TASK.json](TASK.json) records the exact external proof URL and byte hashes.
The cited manuscript is not an executable dependency. The universal integer
argument is self-contained once its displayed premises are assumed.

Credit CubeJerry for PR #6781 and #6773; Ali Romman for the mixed-projector
root and coupled normal form; thu-nmrc for the coupled stage-rank bounds;
ToikY for the retained leakage and odd-pair work; Cinna Davis and the retained
query/controller contributors. Predecessor credit and mathematical claims
remain theirs. This package addresses an algebraic side question on the
complex-decoder card; its complete physical-boundary and paid-invoice gate
is not met.

## Reproduce

CPython 3.12 and the standard library suffice. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-odd-optimal-sectors/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p104-odd-optimal-sectors/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-odd-optimal-sectors
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-odd-optimal-sectors --check-source-history
```

A reviewer may replace the absolute interpreter path with another CPython 3.12.
The direct marker is `PASS_ODD_OPTIMAL_SECTOR_REDUCTION`. The generic markers
are `PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The last command requires the package to be committed.

The standalone verifier enumerates all x,y,z in [0,4q], determines w and h+j
from the ambient and optimum equations, and then tests every nonnegative h,j.
It applies the original inequalities directly, without using the six-form
parameterization to prune. At q=1,3,...,15 it compares the entire accepted
set with the new formulas, enumerates its count and checks stage-rank
consequences. Seven invalid-input controls, four changed inventories, four rank-inequality
controls and an endpoint-support control must reject. Every run prints a generated JSON
receipt binding its output to all six package-file SHA256 hashes. Nothing
is written by the verifier and no receipt is handwritten.

The finite domain corroborates the written all-width proof; it is not a
finite word census or a proof by extrapolation. No predecessor executable,
solver, network, third-party module or Git process runs in the verifier.

## Implementation and limits

The verifier has fixed q<=15, at most 61 cubed candidate triples per width,
and at most 61 h choices per triple. All eight widths and six source-file
reads are explicitly bounded. It retains accepted inventories and the
six-form comparison sets, each of at most 48 tuples. Python allocates
managed integers and collections dynamically; bounded enumeration and
small local sets are the explicit memory-allocation deviation from the
Power of Ten fixed-allocation rule. Functions stay below 60 lines,
there is no recursion, and explicit exceptions keep checks active under -O.
Warnings-as-errors normal and optimized commands are registered. No new
shared code or CI configuration is changed.

Actual-word attainability, characteristic two, other full-stage placements,
noncommuting stages, changed query counts, physical native alignment,
ownership/erasure, compiler, precision/tape, stock and analytic recovery
are outside this result. No complete invoice, new kappa, selected-frontier
change or complete multiplication theorem is claimed. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed. No selected cold replay is run.

## Open next questions

Which of the 3(q+1) inventories can an actual word realize? Start at q=1
and q=3 with the ordered joint-projector support and orthogonality equations
for these six forms, retaining actual-prefix compatibility. This matters
because realizable output masks, followed by a complete native and recursive
bill, are needed before the inventory can contribute to a supplier.
No sufficiency theorem for those matrix equations is supplied here.
