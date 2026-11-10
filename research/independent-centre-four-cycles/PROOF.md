# Sharp obstruction for independent four-contact cycles

This is a scoped proof with an exact source-specific finite certificate.
It prices every induced four-cycle in the retained 640-input centre-contact
graph. The paired distance, the unary/correction split, and the four-vertex
census are the geometry already used for induced trees in
`research/independent-centre-quad-trees` (PR6336). This note adds the cycle.

## Statement

Freeze every source chart except the four vertices of one induced four-cycle
in the internal empty-chart graph. Replace each of those four charts
independently by any nontrivial one-transvection neighbour of the empty chart.
Keep every incident edge, every native map, every boundary, and all 408
productive helper targets unchanged.

The internal graph has 176 empty-chart vertices and 256 rank-zero edges.
Its connected induced four-vertex subgraphs are 716 paths, 160 claws, and 62
four-cycles. PR6336 prices the paths and the claws. The theorem here prices
the 62 cycles. For every such cycle, every label assignment, and every
`0<theta<1`, the complete paid-moment change satisfies

    Delta(theta) >= 2(1 + 7^theta - 8^theta) > 0.

The bound is sharp for every such theta at one assignment. In zero-based node
numbers the cycle on vertices `{10875,10876,10898,10899}`, walked as
`(10875,10876,10899,10898)`, with label 59 at every vertex, has rank-histogram
change

    delta_0 = -2, delta_1 = 2, delta_7 = 2, delta_8 = -2,

and every other delta zero. Its capped prefixes are

    (2,2,2,2,2,2,2,0,0).

No other induced four-cycle meets that prefix vector. Across all 62 cycles the
componentwise minima are exactly that vector, so every cycle sits at least as
high as the tree floor `(2,1,1,1,1,1,1,0,0)` and strictly above it on prefixes
2 through 7. Label 59 is normal 30, tag 1, transvection axis 1054.

The selected frontier remains κ = 781451/250000000 from PR6030. The argument
does not sample labels or screen a list of theta values.

## Census and charges

A connected graph with degree sequence `(2,2,2,2)` is a four-cycle. The pinned
predecessor recounts the connected four-vertex blocks by a radius-3 ball census
and by two independent cycle walks: once from each side, and once from opposite
corners. This checker requires those two cycle sets to agree, requires the
shape counts `716 + 160 + 62`, and then prices each of the 62 cycles. Sixteen
empty contacts have internal degree 2 and 160 have internal degree 3. Every
empty contact still has four incident edges in the full graph. The source paid
histogram is

    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.

Productive helper targets remain `{4:28,7:7,8:47,9:326}`, and the independent
centre reward remains zero. Edges incident to a variable contact use the
identity native map. Internal edges start at rank zero.

## Paired distance, unaries, and corrections

The ambient space is `F_2^9 x F_2^9`. The empty Lagrangian and its
one-transvection neighbours are the 1,022 charts of PR6336: partners are
`k xor 1`, and two labels have distance 0, 1, or 2 according as they agree,
share a normal, or do not. The checker compares that distance with literal
frame rank for every pair in widths 1 through 5.

For prefix `j` in `1..9`, write `h_j(r)=min(r,j)`. Let `U_v^j(k)` be the sum of
the changes of `h_j` over edges incident to `v`, when only `v` moves to label
`k`. These unaries are recomputed from the source frame bases. On an old
rank-zero internal edge whose other end stays empty, one unary adds `1` for
every `j>=1`. If both ends move, the two unaries contribute `2`, while the true
capped change is `min(d(i,k),j)`. The correction is

    C_j(i,k) = min(d(i,k),j) - 2.

For `j>=1` this is `-2` on a repeated label, `-1` on a partner, and
`baseline = min(2,j)-2` when the normals differ. An edge with one end in the
block is exact inside that end's unary. An edge with neither end in the block
cancels. The only edges with two ends in an induced cycle are the four cycle
edges. The prefix objective is therefore

    U_0(i)+U_1(k)+U_2(l)+U_3(m)+C(i,k)+C(k,l)+C(l,m)+C(m,i).

## Elimination by pair pattern

A label is a pair index together with a tag in `{0,1}`. Write `m_v(p)` for the
better tag cost of vertex `v` at pair `p`. Tags on a shared pair interact only
along a cycle edge whose two ends use that pair. There are fifteen set
partitions of four vertices, and each one determines the cycle edges that fall
inside a common pair.

1. All four vertices use one pair. The four edges couple the tags. Sixteen tag
   tuples, scored directly, cover the pattern.
2. Three vertices use one pair and the fourth uses another. Those three induce
   a path of two cycle edges. Eight tag tuples score that path. Both edges
   leaving the outsider cross pairs, so each contributes `baseline`, and the
   outsider keeps its better tag. The outsider's pair is the best marginal
   outside the triple's pair.
3. Each of two opposite cycle edges lies in its own pair, and the two pairs
   differ. Each of those edges has four tag tuples. The two crossing edges
   contribute `baseline` each. For each pair on one edge, the other edge uses
   the best different pair.
4. The two diagonals occupy two different pairs. No cycle edge lies inside a
   pair, so all four corrections are `baseline` and all four tags separate.
   The cost is `m_0(p)+m_2(p)+m_1(q)+m_3(q)+4 baseline` for `p≠q`.
5. Exactly one cycle edge lies in a pair, and the other two vertices use two
   further pairs. That edge has four tag tuples. The other three corrections
   are `baseline`. The free pairs are chosen from the four cheapest marginals
   of each free vertex.
6. Exactly one diagonal pair matches, and the other two vertices use new pairs.
   Again every cycle edge crosses, so the cost is four marginals plus
   `4 baseline`, with the free pairs taken from those same four-marginal windows.
7. All four pairs differ. Tags separate and every correction is `baseline`.
   The four pair indices are chosen from the four cheapest marginals of each
   vertex.

These patterns are disjoint and exhaust the assignments. A minimum over them is
a minimum over the whole label domain once each pattern is minimized exactly.

The windows are exact for the following reason. Let `L_t(v)` be the `t+1`
pairs of vertex `v` with the smallest `(marginal, pair index)`. If a feasible
pair `p*` lies outside `L_t(v)` while at most `t` pairs are forbidden, then at
least one pair of `L_t(v)` is allowed and has marginal no larger than
`m_v(p*)`. Replacing `p*` by that pair preserves feasibility and does not raise
the cost. In the one-edge and one-diagonal patterns each free vertex has at
most two forbidden pairs, so its optimum lies in `L_2`, hence in the four-pair
window the search actually uses. In the four-distinct pattern each vertex has
three forbidden indices. Replacing the four coordinates one at a time, each
time inside `L_3` of that vertex and outside the three indices still in use,
produces an optimal tuple inside the product of the four windows. The search
enumerates that product and keeps only distinct tuples. Every matched pair that
is not windowed is scanned in full, and every coupled tag tuple on those pairs
is enumerated.

An independent control fixes one label and eliminates the other three by the
paired min-plus transform

    T f(k) = min(f(k)-2, f(k xor 1)-1, min_{other pairs} f + baseline),

with the closing correction applied to the fixed label. Each transform attains
its minimum on a finite domain, so the fixed-label loop equals the four-label
minimum. It agrees with the partition on the sharp source cycle at all nine
prefixes and on the small exhaustive products below.

## Source certificate

The pinned builder regenerates the graph with 19,197 nodes, 4,429 frames, and
34,830 positive paid edges. The checker solves nine prefix problems on each of
the 62 cycles: 558 integer minimizations. For every returned label tuple it
recomputes the incident-edge rank histogram and requires that prefix coordinate
to equal the reduction. The componentwise minima are `(2,2,2,2,2,2,2,0,0)`.
Exactly one cycle attains the vector in every coordinate, the cycle named
above.

The named assignment was evaluated directly. Its histogram is the displayed
vector, and one full edge scan matches the incident index. The eight edges
whose ranks change are

    (6733,10875): 0→1,  (10874,10875): 8→7,
    (6737,10876): 0→1,  (10876,10877): 0→1,
    (10897,10898): 8→7, (10898,11060): 1→0,
    (10899,10900): 0→1, (10899,11061): 1→0.

No internal cycle edge changes rank: all four charts are label 59, so each
internal distance is 0 and each old internal rank is 0. The resulting prefix
sums are `S_j=2` for `j<=7` and `S_j=0` for `j>=8`.

Small controls, separate from the source minimum, compare the distance with
frame rank through width 5, compare the partition with the full four-label
product on widths 2, 4, 6, and 8, compare the fixed-label transform with that
product on widths at least 4, and include a single-diagonal cost and a
four-distinct-pair cost. Five invalid inputs, three changed graph contracts,
and five altered source files are rejected. Subtracting one from the sharp
unary at label 59 and prefix 1 drops that cycle's minimum from 2 to at most 1.

## From prefixes to every concave power

For a histogram change `delta` define

    S_j = sum_{r=0}^9 delta_r min(r,j),
    q_j = j^theta - (j-1)^theta.

Summation by parts gives

    Delta(theta) = sum_{j=1}^8 S_j (q_j - q_{j+1}) + S_9 q_9.

For `0<theta<1` the map `t ↦ t^theta` is strictly concave and strictly
increasing, so its first differences `q_j` are positive and strictly
decreasing. Every coefficient `q_j-q_{j+1}` and the last coefficient `q_9` are
therefore positive. Every cycle assignment has `S_j >= m_j` for
`m=(2,2,2,2,2,2,2,0,0)`, whether or not one label tuple minimizes every prefix,
because each coordinate `S_j` is the prefix objective of that assignment and
every prefix minimum is at least `m_j`. Hence

    Delta(theta) >= 2 (q_1 - q_8) = 2(1 + 7^theta - 8^theta).

The right-hand side is positive because a strictly concave function lies
strictly above its chords. On `(0,1)`, `t^theta > t`. Applying that at `1/8`
and `7/8` and clearing `8^theta` yields `1+7^theta > 8^theta`. The named
histogram has `S=m`, so equality holds for every theta in the interval.

## Boundary

The identities and the finite census prove the obstruction for every induced
four-cycle in this fixed graph, for the whole interval `0<theta<1`. They do
not prove a source-independent floor. Together with PR6336, every connected
induced four-contact block on this graph raises the paid moment under
independent one-transvection charts, while the 408 productive targets and the
zero independent centre reward stay fixed. Blocks of five or more contacts,
nonempty original charts, second-step neighbours, changed operations, routes,
native maps, helper targets, and endpoints remain outside the priced contract.
No new paid improvement, native construction, physical restoration, rounded
implementation, compiler closure, supplier admission, or multiplication theorem
is established. The selected frontier stays the PR6030 conditional record.
