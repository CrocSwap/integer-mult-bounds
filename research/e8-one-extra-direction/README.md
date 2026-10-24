# Binary E8 pairing savings require factor-rank sum at least 21

Scoped proof from cited geometric premises. No new kappa or physical decoder.

For the fixed 120-line binary E8 matrix
`K(q,r) = 1 + (q dot r)/2 mod 2`, every finite binary factorization
`K = A B^T` whose actual binary factor ranks sum to at most 20 has rational
source-reader pairing-rank cost at least **72**, regardless of term count.
In particular, adding arbitrarily many terms cannot help when both factor
spaces add at most one direction beyond the rank-nine code.

The reduced rank-(10,10) case has the stronger bound `cost >= 8m - 16`,
where `m` is its term count after zero deletion and duplicate merging.
Thus a reduced twelve-term factorization of that rank pair costs at least 80.
The other boundary follows by choosing a basis from the rank-eleven
factor when the opposite factor has rank nine.

Ali Romman's [#4967](https://github.com/CrocSwap/integer-mult-bounds/pull/4967)
already proves the 72 floor for every factorization with at most eleven
terms. This result removes the term-count restriction for the stated factor
ranks. It does not settle the general twelve-term question. The
[proof](PROOF.md) cites the existing one-coset defect theorem and
minimum-basis theorem for dimensions nine through eleven. Neither
predecessor geometry nor its finite census is rerun as this contribution.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e8-one-extra-direction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B research/e8-one-extra-direction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e8-one-extra-direction --check-source-history
```

The written proof supplies the unbounded-term quantifier. The standalone
verifier corroborates the new algebra steps on a separate six-line rational
configuration. It enumerates 262,144 merge inequalities, 4,096 pairing
inequalities and 8,192 complete normalization fixtures. It checks 92 two-sided
arithmetic cases, 69 one-sided cases and eleven controls. It prints
an automatically generated receipt bound to the package source hashes and
writes no files. Those finite checks do not instantiate or re-prove the
cited E8 geometry.

`SOURCES.json` pins all mathematical predecessors as historical provenance
at canonical main `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
There are no runtime dependencies on predecessor code or data. The current
selected source-binding orientation passed; it is not a scientific replay.

## Limits

The cost is the sum of rational ranks of root-pairing submatrices, with the
binary scalar factorization taken over F2. These are different fields and
must not be interchanged. The theorem uses the full fixed 120-line matrix,
not a punctured or masked matrix or an odd-characteristic factorization.
The geometric premises retain their original author-checked status.
Independent human and formal proof-kernel review are unclaimed.

No shared physical delivery, dirty restoration, native caller, recursive
invoice, supplier admission or complete multiplication theorem is supplied.
The selected frontier is unchanged. No performance number is claimed.

## Open next questions

1. Can factor ranks (10,11) or (11,10) lower the cost at twelve reduced
   terms? These are the smallest two-sided rank pairs outside the new floor.
   Start with the three nonzero quotient cosets of the rank-eleven factor
   and couple their deficits to the opposite factor's single-coset budget.
   The available one-coset budget alone is insufficient.
2. Can the rank-(9,12) case lower the cost? Start with a dimension-twelve
   extension of the rank-nine binary code and its minimum basis support
   cost. The cited eleven-dimensional basis theorem stops one dimension
   short. Neither question is reserved by this package.

## Credit and verification design

This result was produced by Nick Petalas. Ali Romman supplies the fixed binary
matrix, the geometric one-coset defect budget, the eleven-dimensional basis
theorem and the open twelve-term question in #4967. conorholds' #3755 is a
method antecedent for combining two deficiency budgets with product rank,
over a different scalar field and with different code dimensions and prices.
Its theorem is not substituted for the binary geometric premise.
Joel Pulikkan / GamingPuzzled #620, DreamingOfClouds #446 and the retained
E8, scalar-copy and root-code contributors keep their predecessor credit.
Standard rank inequalities and merging are not claimed as new mathematics.

The build-the-lever principle led to an executable normalization checker.
The prove-it-works principle led to full operator and cost comparisons for
each fixture, including optimized Python. Power-of-ten inspection found no
recursion; fixture sizes bound every loop and every function is under 60
lines. Python's managed rational/list allocation and the fixed callbacks
used by rejection controls are deviations from rules 3 and 9. They remain
confined to the six-line, at-most-six-by-six fixtures and the sixteen-term
normalizer. A runtime deployment would require a separately bounded storage
implementation. Normal and optimized replays use explicit exceptions, so
checks are not disabled by `-O`. Warnings-as-errors is registered. No static
type analyzer or proof-assistant build is claimed.

New work is Apache-2.0.
