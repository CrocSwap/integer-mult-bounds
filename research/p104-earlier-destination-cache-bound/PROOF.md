# Earlier destination-history exclusion for #7481

## Claim

For the frozen 76,475-instruction #7481 native word, none of the 49 MOVE
owners whose current value is exactly reconstructible from the other live
rows in its source coframe can be reconstructed from the cumulative span of
all rows observed in its destination coframe strictly before that MOVE.
There are 18 public and 31 owned candidates, with ranks
`{1:21, 2:12, 3:5, 4:9, 5:2}`. The result is an exact scalar-history
nonmembership screen, not an unconditional lower bound or a supplier change.

## Source and overlap

The bundled compressed word is byte-for-byte pinned by SHA256
`acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
Its original `NOTICE` is retained byte-for-byte. The source-bound screen uses
the normalized latent-row semantics of the retained #7481 native word: ADD,
COPY and nonzero SCALE are exact linear row operations; INIT/CLEAR give zero;
MOVE changes a row's chart and leaves the normalized latent row unchanged.

Earlier work is credited with its actual scopes. #7308 checks the 47 paid
owned MOVE clocks on #7277 against other values live in each fixed destination
chart. #6069 covers the unchanged #6030 word and reports 4,033 leaking
unit-injection classes (including dynamic affine closure of its two remaining
cases), 764 incoming-only MOVE intervals, and five private rank-four query
outputs tested against other live destination-chart values at their immediate
output seam. This package covers every source-span MOVE survivor on the later
#7481 word and the full cumulative destination-coframe history at each cut.
Its claim is limited to this 49-cut, unchanged-history cache class. It does
not assert that #6069 lacked all earlier-history or dynamic affine reasoning.
See `RELATED-SCOPE.json` and `inputs/pr6069-info.json` for the pinned overlap
record.

## Exact method

The source prefilter keeps the full rational relation kernel among all live
normalized rows. For an owner `a` and same-coframe donor set `D`, the value is
in `span(D)` exactly when the current relation kernel contains a relation
with nonzero coefficient at `a` and support contained in `D ∪ {a}`. The
scanner projects relations outside that allowed set, carries the full
relation along an exact rational echelon basis, and detects precisely such a
projected dependency. Its relation updates are the exact changes for INIT,
ADD/COPY, nonzero SCALE and CLEAR; MOVE preserves latent rows. The moving owner
is excluded from its donor set. Live bank membership is keyed by equality of
the complete GF(2) frame subspace, not by literal frame ID.

For each candidate destination class `B`, the history basis starts with all
public entrance rows at `B`. Every nonzero MOVE arrival at `B` is added after
its move. At a candidate cut, membership is tested before changing its chart
or adding the current arrival. This cumulative span contains every earlier
actual coframed bank: initial public rows are included, MOVE arrivals are
inserted, INIT/CLEAR yield zero, and coframed ADD/COPY/SCALE preserve linear
span. Pooling rows from different earlier times only enlarges the tested
span, so its zero hits exclude any one earlier bank as a source of the target
row. No simultaneously available multi-chart cache is inferred.

The package runs three pieces: the exact source-kernel screen; the streaming
exact history filter; and an independent direct exact-rational forward replay
using a separate GF(2) frame canonicalizer and low-pivot Q echelon basis. Both
history engines agree on all 49 strict-before decisions and on each cut's
history rank. The direct replay also reconstructs all 49 source witnesses.
The small independent source-kernel controls compare seven synthetic
relation-space states with a direct rational nullspace, check 44 owner/donor
span decisions and verify 19 emitted witnesses. They include INIT, ADD,
COPY-zero, negative SCALE, dirty-coordinate, CLEAR, singular-prefix and
redundant-frame controls.

The source prefilter covers all 6,279 MOVE events through event 76,474:
6,214 public source-span misses and 18 public survivors, plus 16 owned misses
and 31 owned survivors. The history screen uses 40 destination subspaces,
55 initial public generators and 1,410 nonzero MOVE arrivals, for 1,465
independent history generators. It checks 29,874 coframed ADDs, 1,404 SCALEs
and one COPY by the exact linearity argument. All 49 candidates are outside
their strict-before destination history; there are zero hits.

## Reproduce

Run from any working directory with CPython 3.12 and the standard library:

```sh
python3 -I -B research/p104-earlier-destination-cache-bound/verify.py
python3 -I -B -O research/p104-earlier-destination-cache-bound/verify.py
```

Each command regenerates source and history bases in memory, takes under 180
seconds in the reviewed environment, and writes only its compact JSON receipt
to standard output. It does not write or modify package files. The two modes
returned the same receipt. The 3 MB generator log and the 1.5 MB source census
log are not bundled.

## Limits

The conclusion applies to the exact pinned word, arbitrary independent public
inputs as represented by its normalized linear rows, the stated exact scalar
operations, and one earlier destination-coframe cache. It does not cover
imported external stock, changed earlier operations or histories, correlated
inputs, multi-chart stock, changed later repair, or a physical cache
construction. No new kappa, complete supplier admission or unconditional multiplication
proof is claimed. All five foundational assumptions remain.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance in
research, separate implementations, review and packaging. Retain the original
NOTICE and NOTICE-ADDENDUM; no independent human acceptance is claimed.

## Relation-kernel completeness lemma

Let Y have the live normalized owner rows as its rows, and let
K = {c : c^T Y = 0}. Initially the public rows are independent, so K is zero.
An INIT appends a zero row and hence a new unit relation. For an ADD
`row_a <- row_a + q row_b`, contragredience changes every relation by
`c_b <- c_b - q*c_a`; nonzero SCALE changes `c_a <- c_a/q`.
COPY into a certified zero destination is that same invertible ADD update.
MOVE changes only the chart inventory. On CLEAR, relations among the remaining
owners are exactly the restrictions of `K intersect {c_a=0}`; eliminating
one nonzero a-pivot, if present, computes that intersection exactly.
These rules prove by induction that the scanner retains the complete kernel,
even when a public prefix has lost rank.

For donor set D excluding a, write A=D union {a}. The wanted witness exists
exactly when the projection of K outside A has a kernel vector with nonzero
a-coordinate. Gaussian elimination of those projected rows, while carrying
the full relations, returns generators of this projection kernel. Such a
linear combination has a nonzero a-coordinate iff at least one returned
generator does. Normalizing by `-1/c_a` gives the reconstruction coefficients.
This proves completeness of the prefilter; the bounded independent nullspace
controls corroborate its implementation rather than replace this argument.

## Optimistic budget interpretation

The screen grants all cache preparation, preservation, basis normalization,
ordinary copying and eventual restoration free. It preserves the native public
input/output map and its productive inventory. Even this favorable mechanism
cannot replace a paid MOVE at a cut passing the required live-source premise,
because no corresponding destination value is in the earlier history span.
Adding complete implementation costs cannot rescue an absent provider.
This is a necessary-condition obstruction for that mechanism; it is not a
priced replacement word or a new full caller calculation.
