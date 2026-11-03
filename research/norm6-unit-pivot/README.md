# Norm-six compression with target denominator 64

An explicit integral pivot reduces the common target denominator in the
P48p norm-six feature construction from **256 to 64**, retaining **19,600
factor pairs** and integral source features. This contribution was produced
by Nick Petalas. Apache-2.0.

Claim type: scoped written algebraic proof with an exact finite pivot
certificate and endpoint corroboration. The result concerns coefficient
representability. Optimal denominator, runtime or physical precision savings,
a new kappa and a complete multiplication theorem are unclaimed.

Krzysztof Wojt's [PR5143](https://github.com/CrocSwap/integer-mult-bounds/pull/5143)
provides the predecessor stream with denominator 256. Brian's
[PR5132](https://github.com/CrocSwap/integer-mult-bounds/pull/5132) independently
constructs explicit features with that denominator. These results and the
underlying kernel are cited premises, not audited or replayed here.

## Result

Let G be the pinned integral 48-dimensional P48p Gram matrix and let
q(x)=x^T G x. The credited integer-valued feature family has 19,648 members
and 48 relations x_i(q(x)-6)/2. Choose the 26 diagonal-eight coordinates as
roots. Each remaining coordinate has an entry +1 or -1 to one of these roots.

Remove the linear feature at each root and the square-linear feature
x_i^2 x_parent(i) at every other coordinate. The resulting 48-column relation
minor has determinant of absolute value one. Its integral solve gives

```text
sum_(19,600 retained j) phi_j(x) * eta_j(Gy) / 64
    = ((x^T G y)^3 - 4*x^T G y) / 192,
phi_j(x) and eta_j(Gy) are integers.
```

This holds for every integral x with q(x)=6 and every integral y.
[PROOF.md](PROOF.md) gives the full pivot, formulas and substitution proof.
[compression.py](compression.py) implements them without predecessor code.
The feature set changes, so old and new coefficient arrays cannot be
interchanged. The executable validates 48-dimensional coordinates of
magnitude at most 2^20. The written identity has no coordinate cutoff.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/norm6-unit-pivot
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/norm6-unit-pivot/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/norm6-unit-pivot/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/norm6-unit-pivot --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. Direct success
prints `PASS_NORM6_UNIT_PIVOT` and a generated receipt bound to all seven
package files and the Gram hash. No handwritten receipt is used. The only
live external input is the Gram JSON; other pins are historical provenance.
The direct checker also works in a Git-free export with that input.

Verification checks the new pivot by separate exact rational elimination,
all 2,304 entries of its integral inverse certificate, every eliminated
coefficient on 204 target fixtures, 84 complete new shell-source endpoints
containing 1,646,400 records, and 24 off-shell polynomial cases containing
470,400 records. All four feature families contribute nonzero terms in every
off-shell case. Record order, input preservation, 61 nonzero-term omission
controls and nine boundary/solve controls are checked. This corroborates
the written proof without enumerating the full norm-six shell. Optimized
Python retains every mathematical check.

## Scope and decision

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities
revision 8, selected PR6030. Source-binding orientation passed. The
`coverage-law-change` card is explicitly changed to this algebraic side
result; its complete producer/consumer acceptance gate remains unmet.

The decision is to retain this one integral-pivot improvement and stop.
The obligation removed is denominator growth during feature elimination.
No further search or physical implementation campaign follows. Acquisition,
native maps, frames, owned state, dirty restoration, precision, tape movement,
stock, compiler closure and the full recursive consumer invoice remain
unknown. Unknown costs are not zero. All five selected framework assumptions
retain their status. Previous stream storage and arithmetic bounds are not
asserted to transfer unchanged.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370220)
records the target. Live source bodies, recent account work, open PRs,
handoffs, reservations, main README searches, merged quantity/object searches
and the overlap helper were consulted. Sparse notes, arbitrary historical
diffs and unpublished work remain coverage limits. Classical unimodular
elimination and polynomial substitution retain their credit.

## Open next questions

Can an actual caller exploit the smaller coefficient scale after source
access, preparation, output delivery and restoration are charged? Start
with one chronological source/target block, its required order and the new
feature set. A complete physical contract and a favorable full invoice are
the blockers. No further denominator search is reserved.

## Credit and implementation limits

Krzysztof Wojt / PR5143 supplies the relation-column formulas and stream.
Cinna Davis / PR2222 supplies the kernel, Gram data, integer-valued features
and retained P48p/lattice/chart lineage. Nick Petalas / PR5084 retains the
19,600-term bound; Brian / PR5132 retains the concurrent explicit construction.
David Ganz / PR4494 and DreamingOfClouds / PR2244 retain their factorization
and rank context. Predecessor files and credit remain unchanged. The new
contribution is the unit-edge pivot and denominator-64 factorization.
Independent human and formal proof-kernel review are unclaimed. No selected
scientific cold replay, native suite, Lean or Docker was run.

Loops have fixed bounds: dimension 48, 19,648 feature candidates, 204 target
fixtures and the enumerated endpoint cases. There is no recursion, network,
subprocess or dynamic code generation. Functions remain below sixty lines.
The immutable plan owns its Gram and parent tuples. Managed Python allocation
is a documented deviation from allocation-free execution; fixed dimensions,
input magnitudes and fixture inventories bound object sizes. Verification
materializes at most 19,600 records at once. Warning-strict normal and optimized
runs are the available interpreter diagnostics; no extra static analyzer is
claimed. This is an indexed integer algorithm, not a physical memory tariff.
