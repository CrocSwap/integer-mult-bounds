# Independent one-neighbour pairs on the retained contact graph

This is a source-bound paid-cost ceiling. It uses the fixed graph of #4867,
with all 640 arbitrary input owners, all 408 helper targets, all endpoints,
native logical maps, and scalar operations fixed. It awards no independent
centre job. The only changed objects are the charts at two adjacent variable
contacts. Each is changed to a distance-one Lagrangian neighbour. Rank-zero
edges have zero recursive charge; every other incident edge is recounted.
It is not a ceiling on changed scalar words, changed targets, larger
independently retagged blocks, paid-intermediate reuse, or arbitrary callers.

## Prospective contract and neighbour geometry

The public prospective claim is
https://github.com/CrocSwap/integer-mult-bounds/pull/4867#issuecomment-6353171449.
The frozen graph science is `159eb73dd70ccdb03af6f61435135c026cf9886a`,
final metadata `673b1f38379ee88513dfbe2d828845afa7c2f9ec`.
The source payload SHA256 is
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`.

Write symplectic coordinates as `(x,z)` and the empty chart as
`L0={(0,z):z in F2^9}`. For nonzero x define
`Hx={(0,v):x.v=0}`. A transvection with axis `(x,z)` takes L0 to a
neighbour depending precisely on x and the bit `x.z`. The two neighbours
above Hx are represented by axes `(x,0)` and `(x,e_j)` for any j with
`x_j=1`. Both contain Hx and have dimension nine. They are distinct, so
their intersection is exactly Hx and their mutual distance is one.

Different nonzero x give different Hx. For neighbours above different Hx,
Hy, any common vector has X-coordinate in both lines `<x>` and `<y>`,
and hence has X-coordinate zero. Their intersection is exactly Hx intersect
Hy, of dimension seven, so their distance is two. There are therefore 511
hyperplanes and 1022 neighbours, agreeing with #4841's neighbour enumeration.

The actual graph has 176 variable empty contacts and 256 distinct rank-zero
edges between them, with no parallel edge between a tested endpoint pair.
The bounded opposite-neighbour domain is exactly `256*511*2=261632`.

## Complete invoice for the bounded screen

For a changed paid histogram d, define `S_j(d)=sum_r d_r min(r,j)`.
All 261632 cases were evaluated by direct binary row elimination on each
actual incident edge: 1831424 rank checks, 44 distinct histograms. The
original full bill is `{1:2201,2:412,3:510,4:127,5:40,8:8}`; unchanged
helpers are `{4:28,7:7,8:47,9:326}`. No old or new paid call is dropped.

An independent Python replay computes each endpoint's complete single-change
invoice, then replaces the two singly-changed shared-edge bills with the one
jointly-changed bill. It obtains exactly the same 44 histograms and counts.
Every histogram satisfies, simultaneously,

    (S_1,...,S_9) >= (3,3,3,3,3,3,3,2,2).

The lower vector is attained by `d*={1:+3,7:+1,8:-1}` (and rank-zero
bookkeeping -3), in four cases. For any increasing concave tariff h with
h(0)=0, the finite decomposition into `min(r,j)` tariffs therefore gives

    sum_r d_r h(r) >= 3h(1)+h(7)-h(8).

For `h(r)=r^theta`, `0<=theta<=1`, with h(0)=0 also at theta=0, this is
`3+7^theta-8^theta >= 2`. At the developed comparison
`C=.0030217758`, theta=1-C, its floating value is about 2.0090712929448316.
The exact prefix certificate, not this floating number, closes the family.

## Analytic closure of every rank-zero adjacent pair

This transfers #4867's exact complete single-contact bound
`epsilon=1+7^theta-8^theta` and its common-axis subset ceiling; it does not
claim those predecessor results as new. If both neighbours are identical,
the pair is an old/common-axis subset already covered by #4867.
Opposite neighbours above one hyperplane are the bounded screen above.
For different hyperplanes the shared edge has rank two. Each isolated
single change paid rank one there. With the simple-edge census checked,

    Delta_pair = Delta_single_u + Delta_single_v - 2 + 2^theta
               >= 2*7^theta - 2*8^theta + 2^theta
               >= 2 - 2^theta > 0             (0<=theta<1).

The last inequality is concavity:
`8^theta-7^theta <= 2^theta-1`. This closes all 1022 squared independent
neighbour assignments on each rank-zero internal edge without expanding
the benchmark domain. At theta=1 the lower bound is nonnegative.

## Rank-eight internal edges: stop at the complete optimistic bill

The only other internal edges are eight rank-eight edges. Each joins an
empty contact to a distinct original rank-eight chart group. Both endpoints
have degree four. Apart from the shared edge, each has two rank-zero edges
and one edge of original rank at most two. All these incident native maps
are identity, and there is no parallel shared edge. `RANK8-CENSUS.json`
records every actual endpoint and incident edge.

A nontrivial distance-one neighbour makes each original rank-zero external
edge rank one, paying two units per endpoint. The third external edge can
decrease rank by at most one. For rank at most two and any `0<=theta<=1`,
that saves at most one unit. Thus each endpoint's entire external paid
change is at least one, jointly at least two. The shared rank can decrease
by at most two, so its new rank is at least six. Even granting the best
possible joint rank and the best external changes independently,

    Delta_pair >= 2 + 6^theta - 8^theta
               >= 2 - 2^theta > 0             (0<=theta<1).

Subadditivity gives `8^theta-6^theta <= 2^theta`; strictness holds in the
interior. At theta=1 the bound is nonnegative. Consequently the proposed
8355872 independent-neighbour rank-eight pair scan has no profitable case
under its complete optimistic bill, and was not run. This is a graph and
rank-metric argument, not a full physical compiler witness or a general
obstruction to independent retags on larger contact sets.
