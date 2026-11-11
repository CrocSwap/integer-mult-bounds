# Four independent full guards beat their product over every finite field

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written counting proof with exact finite corroboration.
For every finite field K, every m >= 4, every nonzero column u and four
independent rows v_i normalized by v_i u = 1, a uniform complete GL_m(K)
header passes all proper leading-minor guards of I-u v_i with probability
strictly greater than the product of the four individual probabilities.

[PROOF.md](PROOF.md) gives an explicit eight-term exponential formula for
the joint law and proves the sign. A uniform analytic bound covers all
field orders at least 25. Exact tail thresholds cover the remaining field
orders after 56 rational comparisons. The binary case follows directly
from the last-coordinate event.

This resolves the four-covector case of Open next question 1 in
[SHIN09-git's #6710](https://github.com/CrocSwap/integer-mult-bounds/pull/6710).
That package's general subspace law and independent-triple sampling method
are credited premises. The new four-dimensional classification, closed
formula and all-field four-event sign are the contribution here. ToikY's
#6701 and #6703 supply the binary-family and pair-correlation precedents.
Nick Petalas's #4227 and #4807 supply earlier marginal and pair laws.
The retained Ryanson Jonathan, Cinna Davis, source527, commdata2338 and
Jose Manuel BIT/normalizer/compiler lineage keeps its predecessor credit.
The binary and ternary signs are already covered by #6710. The uniform
four-row theorem extends that coverage to every field. No predecessor
executable is imported or replayed.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/independent-four-guard-positive/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/independent-four-guard-positive/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/independent-four-guard-positive
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/independent-four-guard-positive --check-source-history
```

Other machines can substitute their CPython 3.12 interpreter path. The
standalone verifier needs no Git, network or predecessor package. It writes
no artifacts and prints a generated receipt with the SHA256 of all six
package files, followed by `PASS_INDEPENDENT_FOUR_GUARD_POSITIVE`.

The finite check includes all 56 exceptional sign comparisons, all 258
two- and three-dimensional subspaces in the declared interval over fields
of orders 2, 3, 4, 5 and 7, and a separate affine-plane count of ordered
four-point bases in 16 boxes over fields of orders 2, 3, 4 and 5 at m=4.
It checks four altered Mobius terms, distinguishes the independence guess,
and rejects four out-of-domain formula inputs. Every reported comparison
and box count is computed. The written proof supplies the universal scope.

The verifier uses bounded loops, no recursion and functions below 60 lines.
Its largest box has 125 points and 317,750 unordered triples; its largest
stratum check has 57 normal lines and at most 1,296 full-support vectors
per line. CPython dynamic allocation and integer arithmetic are explicit
managed-runtime deviations from fixed allocation. Live collections are
bounded by these fixed domains. Both registered modes treat warnings as
errors and keep explicit checks enabled under optimization.

## Scope and remaining obligations

Only independent normalized covectors and uniform complete general-linear
headers are covered. Dependent families can have a different sign. This
does not price or construct a physical header producer, caller, selection,
dispatch, dirty restoration, stock or precision. The complete recursive
invoice and all selected framework assumptions remain open. No new kappa,
supplier admission, selected-frontier change or complete multiplication
theorem is claimed. Independent human and formal proof-kernel review are
unclaimed. Selected cold replay, Lean and Docker were not run.

The formal-interface-lemma card's scope is changed to this explicitly open
local counting problem. The source pin identifies the question and cited
theorems. Those files are historical provenance, not runtime inputs.
The broader overlap helper reported incomplete sparse local-note coverage;
the target was separately searched in canonical main and live PR bodies.
Its closed-PR API scan timed out. A direct author/date/reference query
found #6793, which cites #6710 as background but studies paid monomial
header costs, rather than the full-GL four-event question here.

## Open next questions

1. Do five or more independent normalized covectors beat their product in
   every dimension? Start with five rows and classify the intermediate
   subspaces through the all-ones vector. Their full-support counts need
   more data than the two four-dimensional classifications used here.
2. Can an actual BIT caller use the four-event count with a fully paid
   uniform complete-header producer? First pin its request tuple and
   header distribution. Selection, emission, dispatch, restoration,
   precision, storage and the full signed bill are unresolved.
