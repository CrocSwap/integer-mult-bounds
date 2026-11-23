# Certificate and interpretation

## Graph, field and stock

The input is the full canonical rational graph recovered from the pinned #8072
runtime. Each input role is an independent public coordinate. A negative node
`~i` denotes input coordinate `i`; a move node carries the linear form in its
row from its source chart to its target chart; an output node is a final demand.
The supplied schedule must be topological, and every row reads only values at
its declared source. Every original transfer is checked to connect properly
nested F₂ frames. The frame dimension is its depth, and its charged grade is
the absolute depth difference.

The checker evaluates the 6,965 graph rows over `F_65521`. It verifies that
65,521 is prime and rejects any rational coefficient whose denominator is not
a unit modulo this prime. At each chart it first inserts all original local
inputs, then inserts each arrival in chronological order into an echelon basis
on all 1,291 public input coordinates. All 5,674 insertions find a new pivot.
Thus the entire original stock at each chart is linearly independent over the
field and hence over Q. This includes 977 receiving charts; one additional chart
has only local input stock. It also implies each delivered value is nonzero.
The conclusion includes the local inputs, and is stronger than merely checking
that consecutive arrivals differ.

## Exact rational local-demand rank

For a chart `c`, let `X_c` be its original incoming values and `I_c` its original
inputs. Let `D_c` list every original outgoing transfer value and every final
output read there. The checker confirms each demand row references only an
entry of `X_c` or `I_c`; its coefficients on `X_c` form the matrix `M_c`.
The full-stock result makes `(I_c,X_c)` independent linear forms. Therefore,
for fixed `I_c` and fixed linear demands `D_c`, any linear scalar-arrival
interface must provide at least `rank_Q(M_c)` independent scalar dimensions.
Summing these local lower bounds gives 5,660. This statement is for the fixed
chart demands, with no uncharged side channel or input-dependent timing; it is
not an existence proof for a replacement graph.

For every nondeficient receiver, `M_c` has full column rank modulo 65,521,
which directly proves full column rank over Q. At 14 charts the modular rank is
exactly one less than the arrival count. For each, the supplied nonzero vector
in [null-sources.json](null-sources.json) is checked against every row with
exact `Fraction` arithmetic. That rational right-null vector proves the Q rank
is at most the modular rank, while a nonzero modular minor proves the reverse
inequality. Thus the one-dimensional deficits and their sum are exact over Q.
The source chart, grade, complete support and source groups of every witness
are checked against the graph. Modular rank alone would **not** establish a
rational upper bound.

## A stronger fixed-sender result at chart 595

This certificate allows the transmitted values and the receiver's decoding
basis to change, but fixes the receiver's eight outgoing demands and the
original stocks at its two original senders, charts 3 and 520. Chart 595 has
no original local input, and its original eight arrivals have these two sources.
The exact demand-space rank is seven; call that seven-dimensional Q subspace
`H`. The null witness at 595 has pivot 1 on arrival `97320`. For each other
arrival `j`, the row `h_j = value(j) - null_j * value(97320)` forms a basis of
`H`.

Chart 3 has 907 original input coordinates and no arrivals; public input 0 is
not among those coordinates. Chart 520 has no original input and exactly three
arrivals. The checker evaluates the entire graph on public input coordinate 0
with exact rational arithmetic and finds that `h_95061` has coefficient `-2`,
so `dim(H ∩ S_3) <= 6`. On the ten explicitly listed input coordinates it also
computes the determinant of the seven `h_j` vectors together with all three
chart-520 arrivals: it is `25594` in `F_65521`. This nonzero minor proves that
those ten rational vectors are independent and hence `H ∩ S_520 = {0}`.

Suppose at most seven linear scalar arrivals from these same unchanged sender
stocks suffice to reproduce the fixed seven-dimensional demand space. Their
span must equal `H`, so each transmitted value belongs to `H`. Values sent by
chart 3 lie in `H ∩ S_3`, while values sent by chart 520 lie in `H ∩ S_520`;
together those subspaces span at most six dimensions. This contradicts the
seven-dimensional demand. The original eight arrivals provide the matching
upper bound, so **eight are necessary and sufficient in this fixed-stock,
fixed-demand linear model**, even granting both senders unlimited acausal access
to their original stocks and arbitrary receiver decoding. New sender stocks,
other sending charts, changed demands, uncharged timing and nonlinear encoding
are outside this conclusion. The full witness is in the `chart_595` section of
[RESULT.json](RESULT.json).

## Sender-space extension across 12 receivers

The following calculation generalizes the fixed-stock question to all 14
receivers with a one-dimensional local demand nullspace. It covers 11 new
receivers beyond the stronger chart-595 result above. The exact word, all local
nulls and each full original chart stock are authenticated and replayed by the
existing verifier. Every source stock and each new demand-plus-input basis is
independent modulo 65,521, and therefore has the same dimension over Q.

Fix one receiver with `m = d+1` original arrivals and rank-`d` fixed local
demands. Let `L` be the span of its free original local inputs and let `H` be
the rank-`d` demand space in arrival coordinates, built from the exact null
vector as in the 595 construction. Set `W = H + L`. Because the original
arrivals and local inputs are independent, `dim_Q(W) = d + dim(L)` and `W`
equals the span of the fixed outgoing demands together with `L`.

For an original sender `s`, let `S_s` be the span of **all** its original
inputs and arrivals, even those occurring after the receiver's original
operation. Project the modular `W` rows through elimination by the full modular
basis of `S_s`; let the resulting rank be `q_s`. The map's kernel is precisely
that modular sender stock. Since the modular and rational dimensions of both
`W` and `S_s` agree, while the rational rank of their combined matrix is at
least its modular rank,

`dim_Q(W ∩ S_s) <= dim_Fp(W ∩ S_s) = dim(W) - q_s =: u_s`.

Each quotient rank is checked by a nonzero square minor on recorded row and
input-coordinate indices. The receipt records all 83 receiver–sender pairs,
their stock sizes, original port counts, ranks, upper bounds and actual modular
minor determinants. A modular rank drop on its own is not used as a rational
upper bound; the individual full-rank conditions are essential.

Let `c_s` be the number of original ports from sender `s` to the receiver.
Delete one original port from some sender `r`, retaining at most `c_s` ports
from every other sender and at most `c_r-1` from `r`. This leaves at most `d`
messages. If those messages and the free inputs reproduce all fixed demands,
their span contains `W` and has dimension at most `dim(L)+d = dim(W)`.
Consequently the span equals `W`, so each transmitted value lies in `W`; a
value sent by `s` also lies in `S_s`. The total possible message-space
dimension is therefore at most

`sum_s min(c_s - [s=r], u_s)`.

The checker maximizes this upper bound over every original sender from which a
port might be deleted. If the maximum is less than `d`, no such deletion can
succeed even with arbitrary linear message values and receiver decoding and
unlimited acausal access to all original sender stock. The 12-chart conclusion
retains the original per-sender caps. If instead
`sum_s u_s < d`, the same reasoning excludes **any** allocation of the at
most `d` remaining ports among the original senders. This stronger inequality
holds at eight of the 12 receivers, as shown below; the other four exclusions
require their original per-sender caps. None of these results changes sender
stock or demands, adds a route or free side channel, or permits nonlinear or
input-dependent-timing communication. The existing `d+1`-port graph may use
messages outside `W` that cancel in its decoding; this argument applies once a
port is removed, leaving at most `d` messages.

| Receiver | Demand rank `d` | Best upper bound with original port caps | Sum of sender upper bounds without port caps |
| ---: | ---: | ---: | ---: |
| 243 | 28 | 22 | 39 |
| 394 | 5 | 4 | 7 |
| 477 | 12 | 7 | 7 |
| 517 | 13 | 8 | 8 |
| 518 | 12 | 7 | 7 |
| 529 | 7 | 6 | 7 |
| 531 | 4 | 1 | 1 |
| 541 | 7 | 6 | 7 |
| 543 | 6 | 5 | 5 |
| 591 | 5 | 1 | 1 |
| 595 | 7 | 6 | 6 |
| 1091 | 23 | 16 | 16 |

At 470 the bound is 5 for rank 5, and at 599 it is 8 for rank 8; these two
checks are inconclusive, not constructions or impossibility results. The
separate exact 595 proof above independently permits arbitrary reallocation
of the seven ports between its original two sender stocks. The extension
includes a fresh negative control that zeroes a row of the actual 13-by-13
quotient minor for receiver 477 and sender 288; the replay must reject it.
These local port obstructions do not establish a physical or signed rate gain.

## Directed depth cuts

Let `A` be the public input-to-final-output linear operator recomputed from the
word. For every threshold `h=1,...,9` and each direction, select final outputs
inside that depth side and inputs outside it. The rank of the corresponding
block of `A` over `F_65521` is a lower bound on its rank over Q, and hence on
the number of scalar values that must cross that directed cut in a linear,
fixed-endpoint protocol. Opposite-direction traffic and already local inputs
are allowed. The output matrix and every rank are recomputed; these are modular
lower bounds, not asserted equalities over Q.

Each proper nested transfer crosses exactly `|depth(source)-depth(target)|`
thresholds in its direction. Summing the 18 directed cut bounds gives **9,527**;
summing actual crossings gives **9,639**, the graph's total grade. Any proposed
redesign to which this bound is applied must preserve the same input and final
charts and linear operator, and charge at least one unit for each threshold a
scalar transmission crosses. Cut lower bounds do not supply a scheduling,
storage, owner-return, compiler or κ certificate.

## The 140,277 single-link reroutes

For each original transfer `k: a -> b`, examine every chart `c` with nonempty
original stock for which `c` and `b` are nested and
`0 < |depth(c)-depth(b)| < |depth(a)-depth(b)|`. The checker explicitly
enumerates 140,277 `(k,c)` pairs. In each case, it asks whether `c` can form
**the same original value** of `k` from an arbitrary linear combination of all
its original inputs and arrivals, giving it even the stock created later in the
saved schedule. All other original node functions and dependencies are frozen.

For speed, three deterministic annihilators of each complete modular stock are
formed from a fixed seed. A nonzero pairing with the target is an exact witness
that the target is outside the modular stock span. Randomness affects only
which valid certificates are chosen: it never turns a zero into a rejection.
Exactly 171 pairs pass this preliminary screen; every one is resolved by full
modular elimination with augmented donor coordinates. The full list of cases,
coordinates and a required descendant is in `RESULT.json`. For each case the
coordinate on that descendant is nonzero and the descendant's transitive
original dependency set contains `k`. Even allowing later independent donors
and arbitrary rescheduling, feeding that descendant into `k` would close a
cycle. All 171 are thus excluded; no same-value candidate survives this model.

Why does modular exclusion also exclude Q? Let the original stock rows be `B`.
The stock is independent over `F_p`, so one square full-rank minor `B_I` has a
determinant that is a unit modulo `p`. If a rational vector `v` lay in the Q
span of `B`, its unique coefficients would be `v_I B_I^{-1}`. Because all
original denominators and `det(B_I)` are units modulo `p`, those coefficients
also have a well-defined reduction, and `v mod p` would lie in the modular
span. Thus a nonzero annihilator pairing excludes rational membership. This
argument relies on the full-rank minor; an arbitrary zero modular rank is not a
rational no-go. Likewise, whenever rational membership exists, the unique
rational coordinates reduce to the checked modular coordinates. A modularly
nonzero descendant coefficient therefore forces a nonzero rational descendant
coefficient. If the target is not in the rational span at all, it is excluded
already. The test does not rule out altering other transported values or
rewriting and recoding downstream donor functions.

The signed-rational control uses inputs `x,y`, a transfer `k=10` of `x`, an
earlier alternate copy `13=x` and a later chart with donors `11=x-y/2` and
`12=y/2`. The copy is a permitted source. The second chart expresses `x` only
as `11+12`, and `11` is a descendant of `k`, so that source is rejected. A
second schedule makes `13` later but acyclic and confirms it is classified as
requiring rescheduling rather than as a cycle. These controls run over the
separate prime 65,519.

## Arithmetic bounds

All stored residues lie in `[0,65520]`. The longest literal row has 521 terms;
the largest dot product has 1,291 terms. Therefore each nonnegative integer
accumulation is bounded by

`1291 * 65520^2 = 5,542,095,686,400 < 2^53 < 2^63`.

Integer row updates, matrix elimination and integer annihilator dot products
therefore fit in signed 64-bit arithmetic. For the screening matrix only, NumPy
uses `float64` products: each integer multiplication is exactly representable,
all partial sums are nonnegative and below `2^53`, so every addition is exact
as well. The checker recomputes the bound and compares a screening dot product
to a Python-integer dot product. It then converts the exact integer results to
`int64` before reducing modulo the prime. No floating-point rank decision or
probabilistic zero test is used.
