# Exact tariffs from two permutation order cuts

**A scoped arbitrary-dirty-role lower bound; no new kappa.**

In the literal F2[S_n] rank-one-idempotent model with free scalar GL_r(F2),
price the two exterior adjacent transpositions at beta and every interior
one at alpha, with beta >= alpha > 0. For any finite number of restored
dirty roles, k targets equal to (1,n) cost exactly

    k [3 beta + (2n-6) alpha], n >= 3.

For S4, the same two-cut potential gives the exact sum tariff for every
tuple drawn from an explicit 20-element subset, including (1,4) and the
reversal. At prices (2,1,2), two (1,4) targets cost exactly 16 even with
extra restored dirty spectators; two reversals cost 18. The excluded
one-line targets are 2143, 2413, 3142 and 3412.

[PROOF.md](PROOF.md) contains the all-parameter counting proof and exact
model. [RESULT.json](RESULT.json) contains the complete S4 target table
and attaining words. This addresses the smallest extra-role handoff in
Nick Petalas's [PR2583](https://github.com/CrocSwap/integer-mult-bounds/pull/2583)
and the unequal-conjugate-price next question in David Arias's
[PR2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738).

## Independent finite evidence

Two separately written C++ enumerators agree on all 8,388,608
complementary subsets of the regular S4 set, producing 4,255 distinct
five-charge vectors with identical multiplicities and least witnesses.
The small two-cut witness can be checked without this enumeration.
The independent Python verifier also checks direct words, cut-rank
matrix charges, small-n instances of the counting formulas, corrupted
receipts, mathematical defects, and literal guard-deletion sensitivity.
See [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) for its exact coverage.

The finite census covers coordinate cuts in all finite permutation
S4-sets at the charge-profile level, by a regular-set lifting argument.
It does not cover arbitrary subspace cuts or other representations.

## Reproduce

From the repository root, with Python 3.12+ and a C++17 compiler:

```sh
python3 scripts/research_package.py --package research/s4-permutation-cut-cone --check-only
python3.12 scripts/research_package.py --package research/s4-permutation-cut-cone
```

The package is also self-contained after exporting its directory:

```sh
python3 -I -B verify.py --full
python3 -I -O -B independent.py
```

The default verifiers compare the fixed receipt; they do not regenerate
it. `verify.py --write` is an explicit maintainer regeneration operation.
The C++ compiler and temporary executable are external runtime
requirements; the Python code uses only the standard library.

## Provenance and credit

Prepared by Ross Richardson with substantial OpenAI Codex assistance,
including an independent exact-verification specialist. Independence
means a separately implemented algorithm and mathematical check, not
human or organizational independence. New work is Apache-2.0.

The inherited cut-rank method is due here to Adam Gall PR1941 and Ross
Richardson PR1966/1989. Nick Petalas PR2583 established the (2,1,2)
tariff for all 576 two-role S4 diagonal pairs and isolated the extra-role
question. David Arias PR2738 extended root tariffs to finite-rank
Coxeter systems when prices are constant on reflection conjugacy
orbits. That price hypothesis does not cover the unequal S4 prices here.
Ross Richardson's earlier symmetric-price-cone note in Discussion2570
covered all 576 two-role pairs for 0<=alpha<=beta<=2alpha. The present
result instead proves arbitrary finite dirty-role tariffs for the stated
target family and all beta>=alpha>0; it does not repeat or supersede that
full two-role result.

The complementary [PR2577](https://github.com/CrocSwap/integer-mult-bounds/pull/2577)
proves the one-premium-label tariff for arbitrary S_n diagonal tuples and
dirty roles (head fb620547bbb66fa97c74ff5f8362df9bf9e591db). Here both exterior
labels carry the premium, and the covered target family is stated explicitly.

Exact predecessor heads and verbatim source-file hashes are in
[PROVENANCE.json](PROVENANCE.json). Vendored predecessor notices are
retained unchanged. [SOURCES.json](SOURCES.json) pins canonical-base
provenance, and [TASK.json](TASK.json) records the task-picker scope change,
overlap limitations, scientific boundary and open handoff.

## Open next questions

Does every S4 diagonal tuple retain its direct tariff at (2,1,2) with
arbitrary dirty roles, including tuples mixing one of the four excluded
targets with the exceptional targets? A useful next step is to seek a
common nonnegative cut combination tight on all 24 targets, or explicitly
separate this coordinate-cut method before searching larger circuits.
This package makes no answer claim for that remaining question.
