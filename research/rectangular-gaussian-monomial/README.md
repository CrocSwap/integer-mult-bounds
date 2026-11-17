# Exact two-sided monomial symmetries of rectangular Gaussian blocks

For a diagonal-weight Gaussian matrix between two Cartesian index grids,
each pair of monomial maps satisfying $UG=GV$ uses the same signed
coordinate permutation on the row and column grids. An axis can exchange
with another exactly when both grid lengths and the effective weight
$\gamma_i s_i t_i$ agree. Here $\gamma_i$ is the Gaussian weight and
$s_i,t_i$ are the row and column spacings. Every allowed pair lifts to
monomial maps, and the weights of the lift are unique up to one common
scalar. The number of permutation pairs is $2^d\prod_C |C|!$, where
each $C$ is a class of identical triples.

[PROOF.md](PROOF.md) gives a scoped written proof with finite exact
corroboration. A four-entry ratio cancels arbitrary invertible complex
diagonal gauges, and its mixed term determines both affine maps.
Consequently a rectangular Gaussian symmetry proposal must preserve the
axis triples. If all triples are distinct, both permutation parts have
only one- and two-vertex cycles.

Jerry Chen's [PR #7597](https://github.com/CrocSwap/integer-mult-bounds/pull/7597)
classifies the monomial centralizer of matching square Gaussian blocks.
Its [proof at the exact submitted head](https://github.com/CubeJerry/integer-mult-bounds/blob/85c29864062620f16e428c12f291f63632dd5a66/research/gauged-physical-gaussian-symmetries/PROOF.md)
asks about rectangular or independently indexed blocks. The new result
uses a mixed row/column invariant and derives the paired action even
when the grids have different sizes, origins and spacings. The proof and
verifier are self-contained.

## Evidence and reproduction

The verifier tries all 18,444 permutation pairs across four small rational
fixtures. It solves for monomial weights from one row and one column and
checks the complete endpoint for each candidate. It also verifies the
centered factorization and the explicit monomial lifts in five fixtures.
These yield 34 predicted pairs and 1,836 lifted endpoint entry checks.
The largest fixture is an $8\times12$ rectangle with a legal axis
exchange. Four controls check a row-only reflection, missing gauges, a
single changed monomial coefficient and the zero-weight degeneration.

From the repository root with CPython 3.12 and its standard library:

~~~sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rectangular-gaussian-monomial/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rectangular-gaussian-monomial/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rectangular-gaussian-monomial
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rectangular-gaussian-monomial --check-source-history
~~~

Any CPython 3.12 executable can replace the absolute path. Expected pass
markers are PASS_RECTANGULAR_GAUSSIAN_MONOMIAL,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The verifier only reads its fixed in-source fixtures and prints results.

## Scope

The proof covers unrounded Gaussian blocks with nondegenerate Cartesian
row and column grids. Physical source matching, perturbation and rounding,
native implementation, and the cost of applying the two gauges are open.
The repository's five framework assumptions remain in force. This is a
local result for Gaussian coefficient structure. It supplies no new kappa
or complete multiplication theorem. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

- Which actual rectangular blocks in the fine-prime source admit this
  factorization? Start with one pair of unrounded same-cell row and column
  intervals and derive its four-entry ratios. Periodic aliases and
  nonseparable phases must be accounted for before using the classification.
- When a source block matches, do the two permutation orbits reduce the
  complete generator bill? Start by pricing one row and column layout and
  the two diagonal adapters. Precision, routing and access costs are open.

## Credit

This contribution was produced by Nick Petalas. Credit Jerry Chen for the
question, the square Gaussian invariant and the symmetry-orbit work in
[#7591](https://github.com/CrocSwap/integer-mult-bounds/pull/7591),
[#7594](https://github.com/CrocSwap/integer-mult-bounds/pull/7594) and
[#7597](https://github.com/CrocSwap/integer-mult-bounds/pull/7597). Credit
Sebastian Egner and Markus Püschel for the established paired monomial
symmetry framework. [Automatic Generation of Fast Discrete Signal Transforms](https://people.inf.ethz.ch/markusp/papers/autgen.pdf).
Apache-2.0.
