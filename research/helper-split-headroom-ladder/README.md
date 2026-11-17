# Fixed-profile helper-split headroom on the #7000 invoice

This package was produced by Nick Petalas.

Claim type: scoped written proof with exact finite certificates. On the pinned
#7000 invoice, the greatest first crossing obtainable by replacing each helper
with at most two positive-integer-rank pieces is approximately
0.004689286593684114. Allowing all rank-one pieces gives approximately
0.011115356648105199. These are optimistic raw-margin ceilings on
**0 ≤ κ ≤ 0.02**, with the paid profile and every main-origin target fixed.
They do not establish a legal split or a new conditional κ.

## Model and exact statement

The source is `research/shared-wire-split-composition/FULL-RESULT.json`,
SHA256 `d9ba709fa5dcefffe3f3abdcf34600ce188224703cfd743e6db8b58ba4816cb7`.
[SOURCES.json](SOURCES.json) pins its Git blob and base commit. The source
construction and its admission are taken as premises, not replayed here.

Let T_r and P_r be that file's complete productive and paid histograms. Define

    F_0(κ) = Σ_r (T_r − P_r) r^(1−κ).

The helper histogram h_r is:

| r | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h_r | 13 | 18 | 44 | 215 | 68 | 42 | 18 | 67 | 595 |

The invoice has T_r = 18h_r for r ≤ 8 and T_9 = 18h_9 + 416.
All targets above rank 9, and the extra 416 rank-nine targets, are fixed.
There are 1,080 original helpers, with total rank 7,650. The factor 18 counts
the eighteen LOCAL invocations. One helper split means the same replacement
in all eighteen invocations.

Replace an original helper of rank r with a partition λ = (a_1,…,a_j),
a_i ≥ 1 and Σ_i a_i = r. Its change to the complete raw margin is exactly

    Δ_λ(κ) = 18 (Σ_i a_i^(1−κ) − r^(1−κ)).

No new paid jobs are charged in this relaxation. For a piece cap m, let
b(r,m) be the balanced partition of r into min(r,m) parts. If
r = qj + s, 0 ≤ s < j, it has s parts q+1 and j−s parts q. Let

    F_m(κ) = F_0(κ) + Σ_r h_r Δ_b(r,m)(κ).

For each m = 1,…,9, F_m has exactly one zero κ_m on [0,0.02]. Among all
allowed partitions with at most m **final pieces per original helper**, the
largest first zero on this interval is κ_m, attained algebraically by b(r,m)
for every helper. A sequence of binary splits with more than two final pieces
is outside the m=2 row. Any actual split-only continuation satisfying these
hypotheses has its first zero no later than κ_m.

| Maximum final pieces m | κ_m, approximate |
|---:|---:|
| 1 | 0.003630058174688367 |
| 2 | 0.004689286593684114 |
| 3 | 0.005653731986780233 |
| 4 | 0.006587917894714106 |
| 5 | 0.007413801865724420 |
| 6 | 0.008144674208796709 |
| 7 | 0.008982372525120905 |
| 8 | 0.009988261544163143 |
| 9 | 0.011115356648105199 |

[RESULT.json](RESULT.json) gives rational open brackets of width 2×10^-45
for the roots, rather than treating the displayed decimals as exact roots.
The original source's stored crossing is reproduced numerically as a model
calibration. This is not an independent verification of its construction.

## Proof

For 0 < κ ≤ 0.02, x^(1−κ) is strictly concave on the positive reals.
If two integer pieces differ by at least two, moving one rank unit from the
larger to the smaller strictly increases their total credit. Repeating this
finite operation balances every fixed-length partition. If fewer than
min(r,m) pieces are used, splitting a piece of size at least two strictly
increases credit, because a^p+b^p > (a+b)^p for 0<p<1. Thus b(r,m) maximizes
credit for every κ in the stated interval. This classical balancing argument
is also the zero-fee case of #6651; the optimization principle is not new here.
Summing over helpers gives F_candidate(κ) ≤ F_m(κ) pointwise.

Every partition preserves rank mass. Hence every candidate has
F_candidate(0) = F_m(0) = 1,520. The verifier proves F_m(0.02)<0 and strict
monotonicity on [0,0.02]. Consequently each F_m has exactly one zero. At κ_m,
F_candidate ≤ 0, so continuity gives a candidate zero no later than κ_m.
Balanced splitting attains κ_m. The ladder is strictly increasing: at every
κ>0, the 595 rank-nine helpers gain strictly when m rises from 1 through 9.

Here is the numerical part of the uniqueness proof. For coefficients c_r of
one scenario, put

    G(κ) = −F'(κ) = Σ_r c_r r^(1−κ) ln r,
    L = Σ_r |c_r| r (ln r)^2.

For κ≥0, |G'(κ)|≤L. On the eleven grid points κ=j/500, j=0,…,10,
the verifier proves G(κ)>L/500 by outward intervals. Every point in
[0,0.02] is within 1/500 of a grid point, so G>0 throughout. Exact sign
checks at both rational endpoints of each root bracket then certify the
unique root. This argument is applied to every ladder and single-split
scenario, and to the four stock-sufficient plans below.

The interval restriction matters. At κ=1 the full-split margin is exactly
24,040>0, while F_9(0.02)<0. Therefore another zero exists above 0.02;
this package does not assert global single crossing or a ceiling on [0,1].

## Exchange rates and stock

RESULT contains all 87 nontrivial integer partitions of ranks 2,…,9. Each row
records Δ_λ at the original crossing, the change in its first root after one
helper replacement, and the least integer n for which

    F_0(w) + n Δ_λ(w) > 0.

The two comparison prices are the complex wrapper's fixed BIT pin
w=0.00376669 and the paired BIT ordinary admission w=0.00385248. The latter
is an accounting comparison point, not a claim that the complex wrapper can
use that price unchanged. These prices come from the two pinned input files.
The least count is proved by a negative interval at n−1 and a positive one
at n. Rows whose counts exceed h_r are explicitly marked unavailable.

At either price the best gain from touching one helper comes from rank nine.
The verifier certifies this against each rank 2,…,8. Available rank-nine stock
suffices, so the following minima hold even when helper ranks may be mixed:

| Comparison price | Any partition | At most two final pieces |
|---|---:|---:|
| 0.00376669 | 43 helpers, all 9→1+…+1 | 137 helpers, all 9→5+4 |
| 0.00385248 | 68 helpers, all 9→1+…+1 | 218 helpers, all 9→5+4 |

For the lower bound, no n−1 touched helpers can supply more than n−1 copies
of the best per-helper gain. For attainability in the relaxation, take n
rank-nine helpers. The stock is 595. Both sides are exact interval checks.
For comparison, using only 9→8+1 needs 269 and 427 helpers respectively.

## Certificate arithmetic and verification limits

`intervals.py` uses integers scaled by Q=10^70. To enclose ln r, write
r=2^a u with 1≤u<2, and use the first 100 terms of
2 atanh z = 2Σ z^(2j+1)/(2j+1), z=(u−1)/(u+1). The nonnegative remainder
is at most 2z^201/(201(1−z²)); the same formula supplies ln 2.
Every conversion to Q is rounded outward.

To enclose r^(1−κ), evaluate r/exp(κ ln r). Here 0≤κ ln r<1/8, since the
largest rank is 145. Eighty positive exponential terms are evaluated with
outward integer rounding. Twice the next term bounds the remaining tail,
since successive ratios are below 1/2. Reciprocal bounds are also outward.
`Decimal` logarithms and Newton steps only nominate rational root endpoints
and printed approximations; they cannot make a failing interval check pass.
All printed receipt approximations have absolute error below 10^-39.

Every rank's power enclosure at κ=1/100 is additionally checked using exact
integer 100th powers. A separate combinations enumeration checks the partition
table, and exact majorization checks corroborate the balancing lemma. Five
negative controls reject a changed helper count, an out-of-range κ, an
unbalanced purported minimizer, a bracket missing the root and reversed
monotonicity. A sixth control checks signs around the original crossing.

Power-of-ten scope is the two Python files. Loops are bounded by the pinned
rank set, ranks 1…9, 100 logarithm terms, 80 exponential terms, 60 Newton
steps, eleven grid points, and the finite partition list. Python's managed
allocation is a rule-3 deviation: both inputs are capped at one megabyte,
there are at most 145 ranks, and the independent enumeration has fewer than
100,000 candidate tuples. No process, network access, recursion or dynamic
code generation is used. Static compilation and `-W error` replays cover the
available Python diagnostics. No shared build configuration is changed.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/helper-split-headroom-ladder/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/helper-split-headroom-ladder/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/helper-split-headroom-ladder
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/helper-split-headroom-ladder --check-source-history
```

The first two commands rebuild the hash-bound receipt and compare every field.
To regenerate it, redirect `verify.py --emit` to a temporary file and compare
before replacing RESULT.json. The receipt binds both verifier files and both
scientific inputs. It does not bind its own bytes.

Legality of the candidate splits, their pivot/cut/boundary bases, their
ADD/SCALE and ordinary costs, native/compiler admission and every outer gate
remain unproved here. No selected replay, Lean or Docker run is claimed.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Which rank-nine helpers admit legal 5+4 splits with no added paid rank?
  A small exact prefix/suffix witness and complete cost ledger would test
  whether the 137-helper wrapper threshold is relevant to construction.
  Physical availability and shared correction costs remain the blockers.
- How does a changed paid profile alter these ceilings? First substitute an
  exact successor invoice and redo its helper-origin decomposition; the
  current ladder does not apply automatically to changed callers or tariffs.

## Credit and related work

Jerry Chen / CubeJerry's #7000 supplies the complete invoice and paired BIT
pin, building on DreamingOfClouds's #6936/#6937, CubeJerry's #6980 caller,
Ali Romman's helper-splitting method and the retained P104 lineage. The
current construction chain includes dillona, ToikY and Rohan Arun. zxv's
#5554 proves a different fixed-local-bill path ceiling. Nick Petalas's #6651
already records classical balanced-partition optimality in a uniform-fee
model; that theorem and its thresholds are not claimed here. The new result
is the source-specific first-crossing ladder, exhaustive exchange table and
stock-constrained helper minima on the #7000 invoice. New material is
Apache-2.0; predecessor files and their notices are unchanged.
