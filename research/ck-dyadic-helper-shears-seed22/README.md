# Exact CK helper matching under two scalar lowerings

**Finite construction and scoped negative result; no new kappa.** On the
fixed target forest of Ross Richardson's [PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917),
allowing disjoint helper shears with coefficients `±1/2, ±1, ±2` lowers the
optimal compensation price from **11,964 to 11,961 component primitives**
under the historical binary-Horner lowering. Under Sagar Thakrar's accepted
[PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) copy/unit
lowering, the exact optimum is **8,434 for either alphabet**. The additional
alphabet has no scalar advantage in that second model.

These are attained matching optima on **one frozen historical target forest**,
not unrestricted circuit optima. Four exact primal/dual certificates, two
separate exhaustive census implementations, literal arbitrary-input execution,
and the unchanged native frame/wrapper checks support the result. The stronger
comparison and the adverse complete-invoice result below are part of the result.

## Reproduce

Python 3.10+ and its standard library, from the repository root:

```sh
python3 -I -O -B research/ck-dyadic-helper-shears-seed22/verify.py
```

Expected final line:

```text
PASS_CK_DYADIC_HELPERS cases=385572x2 old_optima=4400/4403 pr696_optima=3778/3778 columns=725 controls=14+25 no_new_kappa
```

The printed optima are **savings from the corresponding target-only panel**,
whose prices are 16,364 and 12,212. The command writes no repository files,
checks every receipt field, and runs native subprocesses in temporary directories.
Inherited assertion-based native checks run with `-I` without `-O` even when
the parent is optimized. `--record` deliberately regenerates only `EXPECTED.json`.

Additional independent and packaging checks:

```sh
python3 -I -O -B research/ck-dyadic-helper-shears-seed22/independent.py
python3 -I -O -B research/ck-dyadic-helper-shears-seed22/test_package.py
```

The independent command prints its two-model JSON evidence. No solver,
network, Git metadata, or third-party Python package is needed for verification.
`CERTIFICATE.json` contains all four literal matchings and their dual witnesses;
`EXPECTED.json` binds emitted words, counts, prefixes, native receipts and controls.

## Complete finite circuits

The historical provider is PR626 CK: 716 logical registers, including 492
helpers, plus eight private centers and one coefficient-work register. The
112-by-254 compensation matrix `C` uses only eligible frame-zero helpers.
Its target forest is the exact pinned PR917 recipe; it is not reoptimized.

All numbers below count both real components of a complete scalar projection,
including unchanged precondition, A/B work, cleanup, all coefficient work,
source operations and restoration. They are instruction counts, not timings.

| Circuit recipe | Historical forward / backward | PR696 forward / backward | Scalar macros |
|---|---:|---:|---:|
| PR917 predecessor | 149,620 / 149,668 | 104,956 / 104,972 | 15,773 |
| Historical-cost optimal unit matching | 149,618 / 149,666 | 104,952 / 104,968 | 15,773 |
| Historical-cost optimal extended matching | **149,612 / 149,660** | 104,952 / 104,968 | **15,772** |
| PR696-cost optimal unit matching | Not used as a scalar optimum in this model | **104,934 / 104,950** | 15,780 |
| PR696-cost optimal extended matching | Not used as a scalar optimum in this model | **104,934 / 104,950** | 15,779 |

The historical extended witness saves eight real primitives per orientation
against PR917. Six arise from the enlarged alphabet relative to the optimal
unit matching; two arise from improving PR917's greedy matching. Repricing
that same witness with PR696 saves four versus the PR917 recipe, but ties its
unit comparator. The newly optimized PR696 matchings save 22 versus PR917;
that saving is attainable entirely with unit shears.

The historical witness uses 113 helper pairs; the PR696 witnesses use 117.
Both submitted extended matchings contain just one nonunit pair: helper-index
`(218,64)` with coefficient `-1/2`. Indices refer to the ordered `sources` in
the pinned recipe, not the native register numbers. The historical panel has
106 target preparations, 113 helper preparations, 2,102 residual additions,
and 219 inverse restorations: **2,540 macros** versus PR917's 2,541.

Every changed panel is substituted into both complete orientations. Literal
integer-dyadic replay covers all **725 arbitrary logical/private input columns**;
the historical baseline and improved word also receive the retained separate
Fraction replay. The new independent checker imports no constructor or prior
arithmetic code: it rebuilds the matrices/census, prices literal microcircuits,
and tests 726 four-input helper identities for each lowering, including private
dirt. The complete endpoints restore all 492 public helpers and erase private
work. Logical inverse transposes are emitted in the original chronological
order before primitive lowering; destructive clears are not inverted.

All candidate full-word positive-prefix bounds are **41/65 bits**, within the
inherited **192-bit local allowance**. The maximum reduced denominator powers
remain **3/8**. These finite measurements are not a uniform precision theorem.
All non-scalar events retain their order. The unchanged native checker admits
the three distinct optimal extended/PR696-unit macro words and runs its 25
adverse controls on each. The paid child histogram remains
`{1:2596,2:552,3:304,4:160,5:70,6:8,8:8}`, totaling 3,698.

## Identity, complete price and matching certificate

Let `T` denote the frozen target change of basis and `D=T C`. Prepare the
target forest deepest-first and restore it in reverse. For one helper shear
`h_a <- h_a + q h_b`, write `H=I+q e_a e_b^T`. Since `a != b`,
`H^-1=I-q e_a e_b^T`; only residual column `b` changes:

```text
D_b <- D_b - q D_a.
```

Prepare register-disjoint helper shears, add `T C H^-1` to the targets, then
restore helpers and targets. The endpoint is
`T^-1(T y + T C H^-1 H h) = y + C h`, with arbitrary helper dirt restored.
Every helper appears in at most one pair, so the column changes and savings
add. Both shear endpoints are among the 254 pinned eligible helpers; no new
helper, child, physical source register or frame transition is introduced.
Every coefficient-work copy is charged by its lowering.

For reduced nonzero `q=a/2^d`, historical component cost is
`p(q)=3+floor(log2(abs(a)))+popcount(abs(a))+d`; `p(0)=0` means no gate.
This pays the initial work clear, all source additions/doublings/halvings,
target accumulation and final clear. PR696 costs `p(q)-2` for `abs(q)=1`
and `p(q)-1` otherwise. Thus helper preparation plus inverse restoration costs
8/10 historically and 4/8 under PR696 for unit/nonunit choices respectively.

The fully paid gain of an ordered pair is

```text
g(a,b,q) = sum_i p(D_ib) - sum_i p(D_ib - q D_ia) - 2 p(q).
```

For an unordered pair use the largest gain over both orientations and the
permitted coefficients. Nonpositive choices may be omitted. Maximizing the
sum of gains over disjoint pairs is precisely non-perfect maximum-weight
matching; its optimum subtracted from the fixed target-only price is the
compensation minimum in this class.

Each certificate supplies nonnegative integer doubled vertex duals `d_v`,
nonnegative integer odd-set duals `z_S`, and a disjoint matching. All odd sets
contain distinct valid vertices and have odd cardinality at least three.
The checker verifies, for every positive eligible choice,

```text
d_a + d_b + 2 sum_(S contains a,b) z_S >= 2 g(a,b,q).
```

A matching has at most `(|S|-1)/2` edges inside an odd set. Summing these
inequalities bounds twice its total gain by
`sum_v d_v + sum_S (|S|-1) z_S`. Equality with the submitted matching proves
optimality. The doubled primal/dual totals are **8,800 / 8,806** historically
and **7,556 / 7,556** with PR696. The proof needs no solver trust, laminarity,
or exhaustive enumeration of matchings. It establishes only the stated finite
matching optimum; it is not a formal proof of multiplication.

## Full local allowance: a contrary result

The retained invoice also charges a conservative reserve depending on macro
count. With `M` the maximum orientation macro count and `P` the maximum real
primitive count, the pinned `invoice_allcold.py` formula is

```text
A = 16 (M + 3698 + 716 + 8) + 64*73
B = P + A * 64*74^3 = P + A * 25,934,336.
```

The recounted local allowances include the retained adapter reserve and its
child-count term; recursive calls remain separately charged. Relevant witnesses
are:

| Recipe and lowering | Local allowance B |
|---|---:|
| PR917, historical | 8,501,068,015,780 |
| Historical extended winner, historical | 8,500,653,066,396 |
| PR917, PR696 | 8,501,067,971,084 |
| Historical extended winner, PR696 | **8,500,653,021,704** |
| PR696 scalar-optimal unit recipe | 8,503,972,616,694 |
| PR696 scalar-optimal extended recipe | 8,503,557,667,318 |

Thus the historical extended recipe improves its predecessor's local allowance
in both lowerings. But the PR696 scalar-optimal recipes **lose to it under the
complete conservative allowance**: saving another 18 scalar primitives introduces
more macros. The dual certificates do not optimize `B`, and the displayed
best allowance is not asserted globally optimal. Equal scalar optima also do
not imply equal adapter costs; the two PR696 winners differ by one macro.

The recursive child terms and moment equation are unchanged. These are
historical local recounts: changed-word global owner/hosting/provider bindings,
shared maxima across the 72-call selection, global precision and outer assembly
are not rebuilt. The paid recursive moment is unchanged, and no changed global
supplier or outer assembly has been admitted. No new κ or practical speedup
is claimed.

## Search domain, provenance and limits

Base: **`2921874911956718fcaaaf9396fe8267b3cfa9f0`**. At this base the selected
conditional result is **PR942, κ = 0.001661960547713947**; this experiment
intentionally studies historical PR626 CK and leaves the selected result alone.
`SOURCES.json` pins all runtime inputs by bytes, or decompressed payload for
compressed data. Principal source heads:

- PR626, Chafik Boukhalfa: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- PR622, Jeremy Kothe and contributors: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- PR917, Ross Richardson: `085c32a25e2a09b029fa816195b97fa93d6f0788`.
- PR696, Sagar Thakrar: `5a3f983715027c4fd83f50bc9001d4b18463bed1`.

The OS-random assignment seed is **22**, complex-supplier track. Each model
covers all `254*253*6 = 385,572` ordered pair/coefficient choices. The unit
subdomain has 128,524 choices. Each loop ends only on exhausting this domain;
there is no timeout, stochastic pruning or omitted parameter region. The two
independent full-census hashes agree. The original greedy seed-22 unit/extended
gains were 4,394/4,397, both below PR917's 4,399: that failed initial comparison
is retained here. Moving to certified matching closes the allocation question
for the same explicit alphabet and forest.

NetworkX 3.6.1 nominated the four matchings during discovery. Seed 22 breaks
equal-weight representative/insertion ties via SHA-256; stored dual variables
were extracted from the completed solver. Only the resulting exact certificates
are verifier inputs, and every primal/dual obligation is independently rechecked.
Neither solver optimality messages nor their internal assertions are evidence.
No external solver code is copied into this package.

The newly examined class differs from PR917's unit-only greedy construction.
PR964's power-of-two **target-parent** obstruction does not address helper
shears. PR807's helper basis and PR816's target forest are credited predecessors.
PR769 coefficient sharing and pending PR1036 direct small-coefficient lowering
use other models and are not composed here. PR696 is a stronger retained
comparator, not a claim to cover the cheapest currently conceivable lowering.
No result here bounds overlapping helpers, a different target forest, arbitrary
dyadic coefficients, additional work registers, cross-macro sharing, or a
complete invoice optimum.

## Credit, license and assistance

Prepared for **steph4n-gh**, with substantial **OpenAI Codex assistance** in
mathematics, coding, experiment selection, checking and writing. A separate AI
worker wrote the independent census/primitive/dual checker; another reviewed
the identity, cost model and scope. This is implementation independence, not
independent human peer review.

Credit Ross Richardson's PR917 two-sided construction, David Awad's PR807
helper pairs, @dd-hemant's PR816 target forest, Sricharan Vagvala's PR749 target
basis, Oscar Fennell's PR759 forest reduction, and Sagar Thakrar's PR696 lowering.
The retained scalar compiler, native frames, wrappers and historical supplier
also credit icekylinx, DreamingOfClouds, Jeremy Kothe, Chafik Boukhalfa and their
source-notice lineage. Their files and notices remain unchanged. New files are
under the repository's [Apache-2.0 license](../../LICENSE).

All-size/compiler, common-label/mutable-source realization, physical hosting,
precision/tape/exact recovery, analytic transfer and bit-interface assumptions
remain inherited. Verification is finite and scoped. The package does not
supply a full Lean multiplication theorem.
