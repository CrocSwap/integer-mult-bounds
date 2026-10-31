# One-conjugation paid-query floor with arbitrary retained route chains

## Proposition and changed premise

Fix the final #5708 word and its 2,369 directed singleton routes, at the source
hashes in SOURCES.json. Delete one pair of equal ADD transvections and insert
the characteristic-two A2 correction after each intervening noncommuting
contact, at that contact's original frame. An erased outer operand or reversed
ADD is a barrier. Include the two eligible zero-contact cancellations.

Permit each requested frame transition to use **any finite directed path of
retained route edges**, including paths absent from the original direct table.
Retain the original row-sensitive source emitter contract: an identically zero
source omits its ADD and both routes; a zero destination's route is uncharged
but must exist; only owned whole-zero headers may initialize freely; all public
final returns and owned teardown remain included.

For every exponent 0<t<1, the minimum change in the complete emitted local paid
query moment is exactly zero over this domain. This is a fixed-source finite
circuit-class result with a written all-path/all-exponent argument. It is not
a universal BIT-supplier barrier, a new supplier, or an improvement in κ.

The changed premise is route closure. #6290 covers direct-table one-to-three
contacts; #6305 covers direct-table four-or-more contacts and explicitly leaves
new routes open. This package composes only their already supplied native
edges. It creates no new primitive native route and moves no correction frame.

## Exact path lower bound

The retained graph has 636 vertices, one root (frame 1), and an integer potential
L satisfying L(b)-L(a)=r on every edge (a,b,r). The potential is uniquely fixed
by L(1)=0. Its levels and populations are

| L | 0 | 1 | 2 | 4 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| Frames | 1 | 120 | 180 | 70 | 153 | 111 | 1 |

All ranks are positive. Hence the graph is acyclic and every path's total rank
telescopes to the endpoint difference. Exact DAG closure and a separate DFS
implementation agree on all 23,560 reachable ordered pairs. A missing pair has
no finite path in this edge alphabet, not merely no path of a searched length.

For positive x,y and 0<t<1, put s=x/(x+y). Since s^t>s and (1-s)^t>1-s,
x^t+y^t>(x+y)^t. Iteration gives, for any nonempty path with edge ranks r_i,

    sum_i r_i^t >= (sum_i r_i)^t = (L(target)-L(source))^t.

Equality holds for a one-edge path; a path of two or more positive edges is
strictly more expensive. This is an optimistic lower bill: it does not pretend
an absent direct edge exists. A zero payload has no paid query and remains
zero through the route; a nonzero normalized payload stays nonzero under the
retained invertible frame operators. Thus the source emitter's zero tests do
not depend on which path is chosen. The normal-form/telescoping interpretation
of retained native edges is inherited from #5708; only graph/rank accounting
is re-established here.

## Exhaustive source-bound census

The source contains 11,930 scalar records and 685 roles. All 2,787 pairs of equal
ADD records are inspected, with 517 first encountered reversed-contact barriers
and no first encountered erasure barrier. The remaining 2,270 eligible intervals consist of
2,268 noncommuting A2 rewrites (one through 33 corrections) and two commuting
cancellations. The latter have index pairs (5846,5852) and (7339,7340), using
zero-based indices in the scalar record list.

Each eligible rewritten scalar program is checked on all 685 formal initial
columns over F2. Owned initialization and erasure are retained; every public
endpoint remains the intended identity/shear, and owned final rows are zero.
Its entire chronology is emitted using exact reachability, charging the
collapsed rank difference for every nonzero route and including final returns.

| Outcome | Intervals |
|---|---:|
| No retained-edge path for a required transition | 2,035 |
| Reachable, strictly positive lower moment change | 213 |
| Reachable, zero lower change attained by direct paid routes | 22 |

The complete per-interval output is in ONE-STEP.json. Every strictly positive
signed delta is either a sum of positive terms or has the form
sum_i H_(r_i)-H_(sum_i r_i), with at least two positive summands, H_r=r^t.
The preceding strict subadditivity proof settles every exponent in (0,1)
without floating-point powers or numerical root finding. The twenty extra
reachable intervals relative to the direct-table census all lose; no additional
neutral rewrite is created by route closure.

All 22 zero lower bounds have every paid requested transition in the original
direct table. Selecting those direct edges attains the zero paid delta; any
zero-payload route remains uncharged. This proves attainability and therefore
the exact minimum, rather than just a nonnegative relaxation bound.

## Scope and costs not decided

Every paid local route, including final returns, is charged. The word's entrance,
exit and productive-target inventory stay fixed. The proposition is about the
paid-query component: scalar ordinary allowances are not optimized here. It
does not establish that the overall physical runtime of every rewrite is
larger. Two or more conjugations, moved corrections, new native edges,
changed targets/ownership, and alternative words remain outside the domain.
Neither selected cold replay, native phases, the complete caller, compiler,
precision/tape costs nor the outer integer-multiplication theorem are re-audited.
The selected frontier and all five framework assumptions remain unchanged.

Credit Ali Romman (#5708) and the retained source geometry/native/caller lineage;
unpaidmoon (#6290) and Nick Petalas (#6305) for the exact direct-route questions
and coverage. Prepared for @CubeJerry with substantial OpenAI Codex assistance.
