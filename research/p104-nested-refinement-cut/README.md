# P104: a cut surviving arbitrary nested transport refinements

The frozen native P104 channel cannot become an identity supplier solely by
subdividing its original nested transports into more nested steps, even with
arbitrary interleaving and common-chart linear resynthesis. Its source-to-target
rank is at most **56 arrays** in the model below. More specifically, the 56
sources outside the survivor span can contribute at most **eight arrays**.
Identity on those sources alone needs rank 56 arrays.

This is a **scoped obstruction**, not a new kappa, an attaining correction,
a sharp capacity claim, or a lower bound for arbitrary replacement transports.
It changes the operation alphabet addressed by the fixed-path rank-eight
result in [Jeremy Diviney's PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113).
The weaker numerical upper bound covers every intermediate binary subspace
inside each original nested interval, including charts absent from the old word.
It does not meet the original task card's constructive supplier gate.

## Exact model

Work over a characteristic-zero field containing the native scalar constants,
with each register carrying one `d`-dimensional array. Binary charts are
subspaces of `F_2^9`; the binary geometry is separate from the scalar field.
The pinned input is the PR1972 scalar/frame word distributed by PR1991:

```
research/p104-native-channel/inputs/LOWRANK-WITNESS.json
SHA256 0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e
```

Each of its 1,410 original transport occurrences is retained as an obligation.
An upward occurrence `L -> U` may be replaced by any finite chain
`L = W0 <= W1 <= ... <= Wm = U`. A downward occurrence has the analogous
descending chain. Repeated equal charts can be removed; they add no transport.
Each obligation follows **one array** through its chain and is consumed once.
It cannot fork into two independently descending arrays halfway through.

Grant arbitrary interleaving, arbitrary linear operations among arrays in an
identical chart, and source-independent fresh owned storage with free
common-chart copy/discard. The original scalar instructions need not be kept.
Storage may receive an original transport obligation, but it cannot duplicate
that obligation. There are still only eight descending private lifetimes.
All initial data and final target charts are fixed. The usual fixed external
endpoint adapters are inherited from the native channel.

No other cross-chart interface is granted, including a supposedly free
cross-chart map. A different route outside an original interval, an additional
transport, replacement/fusion of endpoint obligations, or a branched transport
chain is outside this model. Native implementation of every intermediate chart
is generously granted; the obstruction therefore does not require building
those recipes. The argument even grants dirty helpers without requiring their
restoration, so imposing arbitrary-input restoration cannot remove it.

This is distinct from [Ross Richardson's PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127),
which retains the old unsplit occurrences and counts additional transports
with added storage. Here the original occurrences themselves are replaced by
nested chains. Neither result automatically converts new steps into excess
recursive cost or idle progress.

## The interval separator

Write `a_0,...,a_7` for the singleton survivors of the eight private descents,
and `A = span(a_0,...,a_7)`. The exact input gives, in descent order:

```
243, 95, 447, 502, 486, 127, 500, 383
```

These eight compressed labels are independent. Their span has dimension eight.
No ordinary physical dot product on these compressed labels is used: membership
and inclusion are preserved by the native package's fixed binary isometry.

Color a chart `W` **T** exactly when it is proper (`dim W < 9`) and

```
W is contained in A, OR W contains at least two distinct a_i.
```

Every other chart is **R**, including the full nine-dimensional chart.
The source-bound checks establish:

| Exact fact | Count |
|---|---:|
| Initial singleton sources in T / R | 48 / 56 |
| Final target hyperplanes in T | 104 |
| Survivors in each private descent's initial hyperplane | exactly 1 |
| Descending private obligations | 8 |

Each descending initial hyperplane is outside `A`; its endpoint is its unique
survivor line inside `A`. Final target hyperplanes contain 2, 3, 4, 5 or 6
survivors, with respective multiplicities 12, 24, 32, 24 and 12.

Every upward interval falls into one of the following sufficient cases,
applied in this order. The counts and every event index are in
[RESULT.json](RESULT.json).

| Interval condition | Occurrences | Why an ascending refinement cannot cross R -> T |
|---|---:|---|
| Its upper chart contains at most one survivor | 701 | T then means containment in A; ascent cannot enter A from outside it. |
| Its upper chart is contained in A | 421 | Every intermediate chart is T. |
| Its lower chart contains at least two survivors | 136 | Every proper intermediate chart is T; the full endpoint can only produce T -> R. |
| It goes from dimension eight to the full chart | 144 | There is no strict intermediate chart; its endpoint is R. |

For a downward private interval, every chart lies inside its original
hyperplane, which contains only one survivor. Thus T again means containment
in `A`. Once a descending chain enters `A`, all its subsequent charts remain
inside `A`. Its start is R and its end is T. **Each such obligation crosses
R -> T exactly once**, however many steps replace the original rank-seven
child. That crossing carries one array, not seven arrays.

The four upward cases cover all 1,402 upward occurrences. They are sufficient,
not claimed necessary for arbitrary new intervals. Together with the eight
private intervals they prove the separator for all permitted refinements,
without sampling the intermediate charts or assuming a frozen chronology.

## Transcript proof of the rank bound

First vary only the 56 initial R-side source arrays. Fix the other 48 source
arrays, every target input and all source-independent workspace inputs to zero.
The T side initially has no dependence on the varying sources.

Same-chart linear operations stay on one side. No permitted upward refinement
has an R -> T transition. The only possible arrivals of R-source information
are the eight single-array crossings just proved. Record their array values
in execution order as a transcript `z` in a space of dimension `8d`.
Inductively, every T-side value is a linear function of the transcript entries
already seen. T -> R feedback may influence later transcript entries; it does
not create an additional R -> T arrival or invalidate the induction. Copies
after an arrival also remain functions of the same transcript.

Every final target lies on the T side. Its dependence on the 56 varying source
arrays therefore factors through `z`, and has rank at most `8d`. Identity
transfer on these 56 arrays would have rank `56d`, which is impossible.
Restoring the other 48 independent source arrays adds at most `48d` to the
rank, giving the stated total upper bound `56d`. No program attaining that
upper bound is supplied or claimed; the inherited `G/2` word has rank `8d`.

The theorem concerns information capacity. It does **not** say that 48 more
native children would suffice, that an arbitrary new crossing costs a fixed
rank, or that splitting preserves the recursive moment. A changed supplier
still needs actual native operators, dirty restoration and the complete bill.

## Independent decision procedure

The second checker uses literal XOR-span sets and independently decides whether
an upward interval contains any R -> T pair. It does not rely on the preceding
four-case classification to establish absence of a bypass.

For `L <= U`, an ascending R -> T pair cannot enter `A`. Its T endpoint must
contain two distinct survivor lines. If `L` already contains two, no proper
R chart above it exists. If `U` is inside `A`, all charts in the interval are T.
Otherwise enumerate the at most 28 pairs of survivors contained in `U`:

1. If `L` is outside `A`, use `V = L` as the candidate R chart.
2. If `L` is inside `A`, append any one vector of `U` outside `A` to obtain V.
   Then `V intersect A = L`, so V contains the same survivor lines as L.
3. Adjoin the chosen two survivors to V. If the result is proper, it is an
   actual T chart in the interval and exhibits a bypass. If it is full, no
   smaller chart with those requirements exists.

This is exhaustive: any crossing endpoint contains `L`, the selected pair,
and an outside-A vector. When `L` lies in `A`, the required dimension is
`dim(span(L, pair)) + 1`, independent of the selected outside vector.
Otherwise the minimum is simply `span(L, pair)`.
The checker finds no bypass in any of the 1,402 original upward intervals.
It also compares this decision against literal exhaustive comparisons in two
complete 67-chart subspace lattices, one ending at the full chart.

## Direct-read gate and controls

The initial construction attempt considered direct `Y_t += c X_s` reads.
All existing X/Y phases and all strict intermediate positions in their
transports give 728 slots on each side. A common chart B exists for two slots
precisely when their lower-bound join fits inside the intersection of their
upper bounds, with the slots' dimension restrictions. Both checkers evaluate
all **529,984 slot pairs**, covering all 104-by-104 source/target pairs, and
find none. No timing constraint is used, so arbitrary retiming cannot help this
particular direct-read attempt. The helper-mediated obstruction is the separate
transcript proof above.

Meaningful controls include an actual excluded new route
`span(x) -> span(x,a_0,a_1)` for `x` outside A, and a new `0 -> full` lift.
Both admit R -> T crossings and are rejected by the original-interval premise.
Dependent survivors, a ninth descent, a full-to-line replacement and nonnested
replacement also reject. Equivalent basis presentations preserve the entire
receipt. Equal dimension alone fails the common-chart test, while identical
charts and compatible strict refinements pass positive controls. The full
chart's exceptional color and the 48 initially T-side sources are checked
explicitly; they cannot be silently counted as R sources to claim rank eight.

## Reproduce

Standard-library Python, read-only by default, no network or Git needed for the
two mathematical checks:

```sh
python3 -I -O -B research/p104-nested-refinement-cut/verify.py
python3 -I -O -B research/p104-nested-refinement-cut/audit.py
python3.12 scripts/research_package.py --package research/p104-nested-refinement-cut
```

`verify.py --out NEW_PATH` writes a computed receipt exclusively; it never
overwrites an existing path. Default replay compares the entire saved receipt.
Exact source and historical task pins are in [SOURCES.json](SOURCES.json).
Both implementations were written by the same author/assistant and are
code-disjoint, not independently human-reviewed. The generic linear transcript
proof is written mathematics, not a proof-assistant certificate. This package
does not replay the original scalar coefficients, native compiler, global
hosting, precision, selected construction or all-size assumptions.

## Open next questions

A changed route must leave at least one original nested interval, add a genuine
cross-chart information transfer, or change another explicit model premise.
Start with an actual bypass such as the small excluded interval above, then
check simultaneous availability and arbitrary dirty-state restoration. The
remaining problem is a legal complete word with a favorable native invoice;
a graph bypass by itself is insufficient.

The sharp capacity of the larger refinement model is also uncomputed. It could
remain eight despite this 56-array upper bound. Only pursue a sharper cut if it
changes a concrete construction decision; identity is already excluded here.
Structured handoffs and stopping criteria are in [TASK.json](TASK.json).

## Credit and provenance

Rohan Arun / PR1972 supplies the channel; Chafik Boukhalfa / PR1991 its native
realization and the source distribution; Adam Gall / PR1940 the schedule.
Geometry and decoder credit continues through Josie Elliston / PR1071,
Ali Romman / PR1125 and the predecessor lineage documented by PR1991.
David Arias / PR2082 and Adam Gall / PR2090 supply frozen-itinerary cuts;
Jeremy Diviney / PR2113 supplies the arbitrary-interleaving fixed-path cut;
Ross Richardson / PR2127 treats arbitrary added storage with retained old
occurrences. Their results are not claimed new here.

The prior fixed-alphabet corroboration is preserved on
[Tairitsu-Aya's public branch](https://github.com/Tairitsu-Aya/integer-mult-bounds/tree/bb473eb4838c271112a95861833847faed55c579/research/p104-chart-alphabet-cut),
without a competing PR. The present contribution is the interval-wide separator,
restricted-source transcript argument and its exact checks. Source files are
read in place and are not copied or modified.

Prepared for Tairitsu-Aya with substantial OpenAI Codex assistance in
mathematics, implementation, source reading and prose. Apache-2.0. No independent
human review, literature-priority guarantee or formal-kernel verification.
