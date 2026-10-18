# Sharp arbitrary-puncture boundary for one-sided E8 masked rigidity

**Scoped boundary theorem and exact counterexample; no new kappa.**
Deleting at most **26 arbitrary E8 root lines** leaves this implication intact:
if one factor is root-linear, exactness on the even-inner-product mask forces
exactness on every pair. At **27 deletions**, an eight-term counterexample exists.
The term count is unrestricted in the implication; the other factor need not be
root-linear. Coefficients may be rational, real or complex, with ordinary transpose.

The new delta over [PR1191](https://github.com/CrocSwap/integer-mult-bounds/pull/1191)
is a sharp deletion-cardinality boundary and the first explicit one-sided
mask-only example. PR1191 supplies the local spanning mechanism and its
orthogonal-set deletion extension; those are predecessor results. This package
does not claim that every small-deletion case is outside that extension.
The general rank-eight rigidity work on particular punctures, including
PR1212/1399/1469/1474/1568, permits both factors outside the root space and has
a different hypothesis. It is not superseded by this result.

## Model and exact local criterion

Let `L` be any live subset of the 120 E8 root lines, `R` its matrix of
norm-squared-two root representatives, and `G = R R^T`. Put

`N(j) = {j} union {i in L : r_i dot r_j = 0}`.

The mask specifies `(D T^T)_ij = 2 G_ij` for every `i in N(j)`: diagonals
and orthogonal pairs. Odd pairs are unspecified. The affine binary label
pairing used for the copied-rank diagnostic is `(G_ij + 1) mod 2`.

If `R` has rank eight, the following statements are equivalent:

1. Every `N(j)` spans eight dimensions.
2. For every finite term count `m` and all `D,T` of size `|L| x m`, if
   `col(D)` is contained in `col(R)` and the masked equations hold, then
   `D T^T = 2G` on all pairs.

The same implication holds when only `T` is root-linear, by transposition.
Necessity in this criterion uses an explicit **eight-term** counterexample;
it does not assert existence for every separately fixed smaller term count.

**Proof.** Write `D = R A`. For each target `j`, masked exactness says
`r_i dot (A t_j - 2 r_j) = 0` for every `i in N(j)`. If those roots span
eight dimensions, their rational nonzero minor remains invertible over the
reals and complexes, so `A t_j = 2 r_j`. This proves every column of the
all-pairs identity. This is PR1191's one-sided argument.

Conversely, if one `N(j)` has deficient rank, choose a nonzero rational
vector `v` annihilating its rows. Since `R` has rank eight, some live root
does not annihilate `v`. Take `D=R`, start with `T=2R`, and change only
row `j` of `T` to `2r_j+v`. Every masked equation remains exact, while at
least one unmasked entry changes. This proves necessity.

## Why the threshold is 27

Each E8 root has 63 orthogonal root lines, forming an E7 section of rank
seven. Every proper root flat of that section contains at most **36** lines.
This is the established PR595/897 finite census; the primary checker here
reconstructs its completeness without importing either predecessor executable.

After at most 26 deletions, at least 37 orthogonal lines remain at every live
target. They cannot lie in a proper flat, so they span the target's full
seven-dimensional perpendicular space. The retained target itself supplies
the eighth dimension. The local criterion applies, and also proves that the
live roots have global rank eight.

For completeness, every proper subspace's root set extends to a rank-six
root-generated flat: repeatedly add roots outside its span until rank six.
The primary checker enumerates all such flats by closed extensions from the
empty flat. At a parent `F`, the nonzero root directions in the quotient by
`span(F)` are grouped projectively. Each group is precisely the root set added
by one closed rank-one extension; every root-generated child has such a
parent. Induction therefore proves complete coverage.

The exact rank-0 through rank-6 counts are
`1, 63, 1281, 10395, 33411, 36435, 8821`. The rank-six size histogram is:

| Lines in flat | Number of flats |
|---:|---:|
| 10 | 5040 |
| 13 | 2016 |
| 16 | 1008 |
| 21 | 666 |
| 30 | 63 |
| 36 | 28 |

Primary elimination uses the prime 65537. Doubled roots are integer vectors
of squared norm eight; Hadamard bounds every square minor of order at most
eight by 4096. Reduction cannot turn a nonzero root minor into zero at that
prime. Thus all root-subset ranks and closure memberships agree with rational
arithmetic. This certified finite-field step is a rational rank certificate,
not an uncertified modular nomination.

Explicit root reflections permute all 120 lines and take the chosen target
to every line. Their formula preserves the ordinary inner product, so the
one-target census applies to every target. The separate checker derives
seven rational fundamental normals from an independently constructed E7
simple system and enumerates their Weyl orbits, checking every flat's rank
with fraction-free integer elimination. Its orbit-completeness premise is
the standard root-flat/parabolic conjugacy statement; the primary method
provides separate finite completeness. Both entire flat-support sets agree
by a canonical digest, beyond agreement on their histograms.

## The exact first-failure example

Use doubled roots `q=2r`, lexicographically sorted with first nonzero entry
positive. Choose

`q_target = (2,2,0,0,0,0,0,0)` and `v = (1,-1,2,0,0,0,0,0)`.

Delete exactly the orthogonal lines with `q_i dot v != 0`. There are 27.
The 93 live roots have rank eight, but the target has only 36 surviving
orthogonal roots plus itself, a neighborhood of rank seven. Set `D=R`,
`T=2R`, then add `v` to the target row of `T`.

Both implementations check all **8649** entries; **4521** are masked.
There are zero masked errors and exactly **56** unmasked errors, all in
the target column. At live root `(2,0,2,0,0,0,0,0)`, the product differs
from `2G` by **3**. Restoring any one of the 27 deleted roots makes the
neighborhood rank eight and rejects this same witness at 26 deletions.
Changing the perturbation to the target root fails on its diagonal.

The complete separate-term copied-rank diagnostic is **eight ranks of nine,
total 72**, for both this example and its coordinate comparator. For
`0<q<=1`, their COPY power bills are equally `8*9^q`; this is not a copied
information saving. No source gathering word, helper endpoints, restoration,
frame itinerary, hosted owner map, physical conversion charge or complete
recursive moment has been constructed. Granting those additional charges
zero cannot turn this particular comparison into a strict COPY improvement.

## Reproduce

Python 3.12, standard library only, no network or third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/masked-e8-puncture-threshold
```

The registered hook replays both engines and the package controls. Direct
optimized replay is also supported:

```sh
python3.12 -I -O -B research/masked-e8-puncture-threshold/verify.py
python3.12 -I -O -B research/masked-e8-puncture-threshold/independent.py
```

Expected markers are `PASS_MASKED_E8_PUNCTURE_THRESHOLD` and
`PASS_MASKED_E8_PUNCTURE_THRESHOLD_INDEPENDENT`. The default commands are
read-only and compare all saved receipt fields. `--write` creates a fresh
receipt and refuses to overwrite an existing file. Source/provenance pins,
the task refinement and overlap limits are in SOURCES.json and TASK.json.

This is a written linear-algebra proof supported by exact finite certificates,
not a proof-assistant theorem. Selected cold replay, native admission,
all-size/compiler realization, arbitrary-dirty physical restoration,
hosting, precision/tape, bit H1-H5 and analytic transfer were not checked.
They remain obligations of any proposed supplier. There is no new exponent,
unrestricted-factor obstruction, or claim that the witness is useful as a
physical decoder.

## Open next questions

Can a one-sided mask-only completion at this first-failure boundary improve
the **complete** separate-term copy bill over an appropriate all-pairs
comparator? First step: vary the one-dimensional deficient-column perturbation
and exactly recount all eight term supports and pairing ranks before building
a physical word. This matters because the existence of a mask-only identity
alone gives no saving. A physical gathering/restoration/frame invoice remains
the blocker for supplier use; general non-root-linear decoders are outside
this question. The structured next question is in TASK.json.

## Credit

- Philipp / @mightyOil, PR1191: one-sided masked rigidity and local-neighbor
  spanning mechanism, including the orthogonal-set deletion extension.
- DreamingOfClouds, PR595: exhaustive E7 flat sizes and design-free geometry;
  PR717: the masked decoder and separate-term copy model.
- DaysSky, PR897: exact E7 hyperplane classification, including its E6 flats.
- @themilkman216, PR968, and @woklerx, PR1077: all-pairs decoder floors and
  their carefully scoped complex-field extension.
- The retained E8 construction and source lineage, including icekylinx,
  Joel Pulikkan / GamingPuzzled, and Douglas Colkitt.

Prepared for @ToikY with substantial OpenAI Codex assistance in mathematics,
implementation, independent implementation, review and writing. Separate
AI checks are not independent human review. New work is Apache-2.0; no
predecessor executable or frozen package is modified or vendored.
