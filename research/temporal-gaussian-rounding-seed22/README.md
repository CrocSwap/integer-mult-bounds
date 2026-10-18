# Temporal Gaussian gauges obey common rounding

**Scoped negative result, with a sharp selected-word fixture; no new kappa.**
Allowing a helper's Gaussian-dyadic gauge to change over time cannot improve
the unconstrained scalar-cost optimum over positive real-dyadic temporal
gauges under the separate-transition contract below.

For any finite schedule, write its gauges as
`g = 2^a i^j (1+i)^b`, where `a` is an integer, `j in {0,1,2,3}`, and
`b in {0,1}`. Let `M` count transitions that change `b`, including entry,
checkpoints and return. There are two real schedules, using one common bit
`theta` across **every helper and every time**, for which

```text
C_G >= (C_0 + C_1)/2 + 2 M.
```

The costs include both real channels, coefficient work, all gauge transitions,
and all retained scalar operations. Identity entry and return make `M` even.
Each maximal odd episode contributes two switches, hence a penalty of four
primitives. This generalizes Hanson Sun's PR1490 static `4 N_odd` penalty.
The written argument covers arbitrary finite schedules and all integer
exponents. The finite replay is supporting evidence, not a formal proof.

## What changed from earlier work

[PR1490](https://github.com/CrocSwap/integer-mult-bounds/pull/1490) proved common
rounding for static Gaussian-unit gauges. [PR1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259)
and [PR1380](https://github.com/CrocSwap/integer-mult-bounds/pull/1380) developed
time-varying real gauges, including interacting helpers. This result prices the
new temporal edges in the rounding argument. Rounding independently at different
times can introduce a transition where the Gaussian schedule had none.

The seed-selected k8 pair is **L225/L340**, index 22 in the sorted 2,414-edge
interaction graph of 237 eligible helpers. The package separately optimizes
each helper with at least one odd use, then composes those two schedules and
prices their shared ADD jointly. It does not assert joint optimality.

| Complete scalar invoice | Forward | Backward |
|---|---:|---:|
| Retained word with PR696 lowering | 149,002 | 149,018 |
| Composed Gaussian temporal fixture | 148,532 | 148,556 |
| Either common real rounding | 148,524 | 148,548 |

Both composed schedules have `M=4`. Their eight-primitive rounding penalty
attains the theorem with equality in both orientations. The fixture is cheaper
than the retained word, but this is not a scalar record: prior many-helper real
gauges already have lower bills. The new result is the sharp temporal
obstruction, not a new dyadic saving or a selected supplier.

## Contract and proof

The base scalar word has real dyadic ADD coefficients. Each complex ADD uses
PR1490's macro-local shared-product lowering built from Sagar Thakrar's PR696
real lowerer. A transition acts only on the helper's own two real coordinates,
using signed ADD, doubling, halving and negation, without workspace or sharing
between helpers. It implements its exact invertible map on arbitrary dirt.
Original SCALEs remain separately priced. The only required gauge values are
identity at entry, return and any declared checkpoints. Gauges cannot touch
a carrier with COPY/clear. The k8 fixture also requires identity at every
nonscalar event and excludes wrapped and center helpers.

No transition is fused with another transition, an ADD, or an original SCALE.
No product is shared across distinct ADD macros. There is no additional
precision/admission predicate in the optimization theorem. Those restrictions
are material, not implementation conveniences.

### Unit classification

The units of `Z[1/2,i]` are precisely `2^a i^j (1+i)^b`. For completeness,
write a unit as `(u+iv)/2^s`. Its norm and reciprocal norm are nonnegative
dyadic rationals multiplying to one, so its norm is a power of two. After
removing common factors of two from `u,v`, if exactly one is odd then
`u^2+v^2` is odd and must be one. If both are odd it is two modulo four
and must be two. This gives an axis unit or a diagonal unit. This is the
classification used and credited in PR1490.

### ADD edges

For `q = +/- p 2^e` with positive odd `p`, the exact real PR696 cost is

```text
c(q) = 2 + floor(log2 p) + popcount(p) + |e| - [p=1 and e=0].
```

The coefficient-work register is cleared even at a unit coefficient.
An axis complex coefficient costs `2 c(q)`. A diagonal coefficient
`q(1+i)`, or its unit-phase variants, costs `2 c(q)+2`: compute each source
channel product once, accumulate it into both target channels, then clear
the work. Both work registers may be dirty initially. Signs and channel
exchange do not affect this price.

For one common `theta in {0,1}`, replace each gauge at each time by
`2^(a+theta b)`. Unit phases can be discarded because ADD cost is phase
independent. For a source-to-target ADD, the coefficient changes by
`g_target/g_source`.

If the endpoint parities agree, their odd factors cancel and both rounded
costs equal the Gaussian cost. If they differ, the Gaussian coefficient is
a phase times `r(1+i)`, while the two real coefficient magnitudes are
`|r|` and `|2r|`. The exact elementary inequality

```text
c(2r) - c(r) <= 2
```

gives `c(r)+c(2r) <= 2c(r)+2`. The bound two is necessary at `r=1`;
using one would lose the unit discount. Thus every ADD costs at least
the average cost of its two common roundings, including shared ADDs.
Indeed doubling leaves the odd numerator fixed, changes the absolute exponent
term by at most one, and can lose at most one unit-discount primitive.

### Temporal edges

For a transition from `(a,b,j)` to `(a',b',j')`, set
`d=a'-a` and `e=b'-b in {-1,0,1}`.
The determinant of the real two-coordinate map has magnitude `2^(2d+e)`.
Signed ADDs and negations preserve the determinant's power of two; each
double or halve changes it by one. At least `|2d+e|` scaling operations
are therefore necessary.

If `e != 0`, all four entries of the transition matrix are nonzero.
Starting from a diagonal map, diagonal operations and just one shear cannot
make both off-diagonal entries nonzero. At least two ADD/subtract operations
are also necessary. COPY/clear are singular and cannot occur in an exact
invertible two-register word. Thus every admitted transition costs at least

```text
L(d,e) = |2d+e| + 2|e|.
```

This lower bound applies to every phase difference. At phase zero it is
attained for every integer `d`: real transitions scale both coordinates;
an odd factor uses a two-shear/one-scale word or its inverse. The literal
attaining words are checked in `verify.py`. No minimum for each nonzero
phase difference is claimed or needed.

The corresponding real transitions cost `2|d|` and `2|d+e|`. Because
`d` is integral and `e in {-1,0,1}`,

```text
(|2d| + |2(d+e)|)/2 = |2d+e|.
```

The Gaussian transition therefore costs at least the average rounded
transition plus `2|e|`. Reusing the same theta across time is essential.
For example, changing theta on a constant odd gauge can manufacture a
nonzero real transition at a Gaussian transition of cost zero.

Sum these inequalities over all ADD and temporal edges, and add the
unchanged costs of original SCALEs, COPY/clear and other scalar work.
Identity checkpoints remain identity after rounding. This proves the stated
inequality. At least one rounded schedule is no more expensive than their
average. Positive real schedules are already members of the Gaussian class,
so the two unconstrained scalar-cost infima agree. Any odd episode forces
a strictly cheaper real schedule by at least four primitives per episode.

This is about the declared lowering and transition alphabet. It does not prove
an unrestricted Gaussian circuit lower bound, nor that a rounded schedule
satisfies an independently imposed precision or physical-admission constraint.

## Reproducible evidence and search coverage

Base **ef5f39403610d231a0c27e8a6b4f08c10209bcd6**; OS assignment seed **22**.
Exact Git blobs, SHA256 inputs and predecessor heads are in
[SOURCES.json](SOURCES.json). The selected certificate was followed to PR1094's
actual archived programs, source manifest, assembly and maintainer review.
The accepted conditional kappa remains `836330098538459/500000000000000000`.

Run from the repository root, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/temporal-gaussian-rounding-seed22
```

Expected: `PASS_TEMPORAL_GAUSSIAN_ROUNDING_NO_NEW_KAPPA`,
`PASS_TEMPORAL_GAUSSIAN_EXPORT read_only=1 corruptions=3 optimized=1`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct replay also works with
`python3 -I -O -B research/temporal-gaussian-rounding-seed22/verify.py`.
`--emit` prints a regenerated receipt to stdout and writes no files.

[RESULT.json](RESULT.json) contains the full schedules, source member hashes,
complete invoices and canonical primitive-stream hashes. Coverage is:

- 3,136 transition cases, all four unit phases and exponents -3 through 3;
  full two-column maps, the determinant/mixing floor and phase-zero attainment.
- 36,608 ADD inequalities with odd numerators 1 through 15, dyadic exponents
  -5 through 5, relative gauge exponents -6 through 6, both signs, both
  endpoint parities and all four phase differences. All 1,504 distinct
  emitted macros pass six-column checks, including dirty coefficient work.
- All three-state paths on 32 signed/checkpoint toy words, 864 literal words,
  checked against the planner. These exercise source/target use, internal
  identity checkpoints and the global requirement of at least one odd use.
- Four complete helper/orientation dynamic programs. Real exponents range
  from -4 through 4; odd gauges have a from -4 through 3. This 17-state
  Gaussian domain is closed under both common roundings into the nine-state
  real domain. Every incident ADD is covered: 121 uses for L225 and 119
  for L340. The planner separately returns the best all-real schedule and
  the best schedule with at least one actual odd use. The incident costs
  are 736/740 for L225 and 608/612 for L340 in either orientation.
- The baseline, composed Gaussian word and both common roundings each pass
  712-column exact complex-linear replay in both orientations, equivalent
  to 1,424 real columns. All 480 dirty helpers return correctly; private
  centers and coefficient work clear. Literal primitive invoices include
  all source reads, work preparation, accumulations, transitions and resets.
- A second paired fixture forces unequal odd parity at the shared ADD,
  event 22,762, then repeats all columns and both roundings. This checks a
  genuinely diagonal Gaussian coefficient at the shared operation. It is
  a deliberate fixture perturbation, not a newly optimized schedule.
- Eleven rejection controls cover the unit discount, independent helper/time
  rounding, free mixing, uncleared dirt, a wrong complex sign, omitted inverse,
  invalid coefficients, aliasing and source corruption.
- The export check copies only this package and its two live inputs, makes
  them read-only, and runs optimized Python from outside the checkout.
  Actual receipt, source and pin-inventory corruptions must then fail.

The finite domain completes 230,394 dynamic transition candidates across
the Gaussian and real planners. It is not a global schedule optimum.
The all-integer obstruction comes from the proof, not exhaustion of this box.
The composed pair contains one shared ADD; its coefficient is charged once
using both gauges. Separate helper savings are never simply added.

All seven variants per orientation retain the paid local histogram
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. Positive literal prefix bounds
remain below the inherited 192-bit local allowance. These envelopes do not
establish the all-size precision/tape interface or rounding closure.
The complete selected cold replay, native/global hosting, Linux CI, all-size
compiler/realization, analytic transfer and a Lean theorem are outside this
contribution. A full scalar endpoint replay is not a replay of those interfaces.

## Open next questions

Can a gauge transition fused with an original signed SCALE escape this
separate-transition proof? Start with one signed SCALE and its adjacent
transitions, implement the full two-real-register map, and compare complete
Gaussian and real invoices. A fused minimum-cost lowering and its admission
are not supplied here.

Can a joint transition on two helpers reduce the sum of the standalone
charges? Start with two reciprocal factors and a four-real-register map,
including the inverse, dirty-state restoration and changed coefficients.
That changes the determinant-accounting boundary; no saving is asserted.
More temporal exponent search inside the present contract cannot beat the
real class. Structured next questions are in [TASK.json](TASK.json).

## Credit and disclosure

Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex assistance in
proof, implementation, verification and prose. One agent wrote the package;
no independent human review is claimed. New work is Apache-2.0.

Hanson Sun (@bbMisk), PR1490, supplies the static common-rounding argument,
Gaussian-unit classification and shared-product ADD construction. This package
extends that argument to time and reimplements its small algebraic formulas;
it does not import a pending predecessor executable. Sagar Thakrar's PR696
real lowerer is used unchanged; PR1259/1380 supply the temporal and interacting
schedule context. Credit woklerx's PR1161, Hanson Sun's PR1214, Philipp's
PR1263/1310/1322, and Cinna Davis's PR1388 for neighboring real-gauge work.
The selected k8 word retains Jeremy Kothe, Rohan Arun, Hao Yan/icekylinx and
the full supplier lineage credited in PR1094's maintainer review, including
DreamingOfClouds's PR589 and eumemic's PR555 bit construction.
