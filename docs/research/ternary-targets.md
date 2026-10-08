# Direct intersection-two circuits and target frames

This experiment follows Zhihao Chen's F3 five-subset construction in
[PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7), at head
`6725c6a17b17871a35353fd29157f4ed851bc114`. The producer and frame checks below
are separate from the multiplication assembly witness. The rational label
form remains `H=I-(2/25)J`, the center totals are
indexed by pairs, and the three tensor stages and their losses are retained.

## A direct side producer

Instead of separately producing ten common-pair pieces per five-set target,
apply the whole intersection-two matrix recursively. Split the ground set
into left and right halves. For each source size a in the left half, target
size b there, and left intersection u, apply the corresponding left and
right intersection transforms in the cheaper order. Their tensor products
cover disjoint source cases. Combine these cases by disjoint additions.
The existing `intersection_circuit.py` supplies exact small templates.
Compute pair totals by the same recursion with target degree two, and
identify identical source supports across both computations.

The resulting direct circuit has one side output per target. It also changes
the internal additions; it is not just an aggregation appended to the ten old
outputs. Exact small counts are:

| Ground size | Direct additions | Direct outputs | Direct roles | PR #7 small producer roles |
| --- | ---: | ---: | ---: | ---: |
| 8 | 462 | 84 | 546 | 1,044 |
| 10 | 7,345 | 297 | 7,642 | 11,890 |
| 12 | 37,308 | 858 | 38,166 | 54,604 |
| 14 | 124,655 | 2,093 | 126,748 | 159,089 |
| 28 | 10,267,219 | 98,658 | 10,365,877 | 11,840,940 |

For h below 28, the last column is the small producer before its large
four-point-star resynthesis. At h=28 it is the complete PR #7
producer count. The small-size network deficits are negative. At h=28 the
direct producer saves 1,475,063 roles with no additional rank loss.

## Raw source spans need repair

In the direct `h=14` side graph, node 9366 has 270 source five-sets. Their
span has dimension eleven but its restricted Gram matrix has rank ten.
For the current deterministic node ordering, one radical vector is

    (0, 2/3, 2/3, 2/3, 2/3, 2/3, 2/3, 2/3, 2/3, 2/3, 1, 1, 1, 1).

Thus cancellation-free scalar computation does not establish a frame
construction. This node has only one reachable side target,
`{0,10,11,12,13}`. Its target orthogonal complement is nondegenerate and
contains the source span.

The first repair assigns `t_S^perp` to every node with exactly one reachable
side target S and no reachable center total. Such nodes form downstream
regions: after entering one, a path cannot regain another target. All other
nodes retain their source spans. Every frame inclusion is therefore nested.
The enlarged frame at a terminal side output is exactly its injection frame.
Center totals still use their positive `(h-2)`-dimensional spans.

At h=8 and h=10, exact checks cover every output coefficient, every nested
physical edge in both invocation directions, all dirty-scratch basis inputs,
and the corrected three-shear bank exchange. The downward rank per invocation
is unchanged: `C(h,2)(h-2)`, namely 168 and 360. At h=12 the full node-label
and coefficient checks pass. A separate h=14 side-only check found no
degenerate multi-target source span after this repair; this is not a
target-size proof.

The [direct producer](../../scripts/experiments/ternary_target_circuit.py)
exposes the same producer interface used by the
[plateau compiler](../../scripts/experiments/ternary_reuse_plateaus.py).
Its h=8 and h=10 equal-label plateaus give no further role saving, but that
compiler independently checks the exact scalar wrapper.

## A more scalable frame cut

Write S(n) for the rational span of the original five-set indicators in a
node's exact source support, and V(n) for the span of all side-target
indicators reachable from that node. The common source intersection can
only shrink along a producer path.
While it has at least two points, the source span is positive definite by
the PR #7 common-pair identity. After it falls below two points, a candidate
frame is the orthogonal complement of the span of all reachable target
indicators. These complements grow along edges, and every source line is
orthogonal to every reachable side target because the circuit is
cancellation-free. A center total cannot be reachable after this cut:
its source support would force a common pair.

If the reachable targets share a pair, their span is again positive
definite, so the proposed complement is nondegenerate. Only nodes whose
source and target common intersections both have size less than two need
an additional rank audit. At h=14, 1,113 nodes meet this condition; they
have 714 distinct reachable target sets, all with nonsingular exact Gram
forms.

At h=28, the initial cut has 5,355,691 common-pair source nodes and 5,009,808
dual nodes. Among the latter, 4,964,964 have a common target pair. The
remaining 44,844 nodes use 18,943 distinct target families. Exact rational
basis selection and full Gram rank modulo a prime certify 18,883 of these
families. The other 60 families occur at 64 nodes; their Gram forms are
indeed singular (28 have dimension eight and rank seven, 32 have dimension
nine and rank eight). They are not accepted as frames.

Delay the cut past these 64 nodes: add them and every ancestor to the source
region. At this size their ancestors already lie in the common-pair source
region, so exactly 64 nodes change labels. Enumerating 5,544 original source
indicators across those nodes and selecting exact rational bases certifies
that all 64 source spans have nonsingular Gram forms. The final labels are
therefore nondegenerate everywhere.

The resulting source region is ancestor-closed. Thus an edge has one of
three types:

* Source to source: S(a) is contained in S(b), since the supports increase.
* Dual to dual: V(b) is contained in V(a), so V(a)^perp is contained in V(b)^perp.
* Source to dual: every source indicator in S(a) intersects every target
  reachable from b in exactly two points. Their H inner product is zero,
  giving S(a) contained in V(b)^perp.

An edge from dual to source is excluded by ancestor closure. A retained
pair-total node and all its ancestors share that pair and remain source
nodes. For a fixed pair C, write a source combination as `(a,a,y)` on C and
its complement. Since every source has three points outside C, `sum(y)=3a`.
The restricted form is exactly `y dot y`: it is positive definite. All
outside triples span Q^(h-2), so each complete retained-total span has
dimension h-2=26. For a source-labelled side output, exact orthogonality
gives the required inclusion in its target complement; the same inclusion
holds for a dual-labelled side output because its reachable targets include
that designated target. Input labels are their source lines.

These statements provide every nested inclusion used by the retained-total
physical wrapper in both directions. Passing to orthogonal complements
reverses all inclusions while preserving nondegeneracy. The only descents
are the 378 retained-total ports of dimension 26, for downward rank 9,828
per invocation. The three tensor stages, side injections and bank exchange
are retained from PR #7. In particular, the 64 repairs add no rank loss.

The Gram audit is exact rather than a probabilistic screen: primitive
integer elimination selects a basis of original indicator rows over Q;
one full modular Gram rank (using either 1,000,000,007 or 1,000,000,009)
proves that integer determinant is nonzero over Q. A failed modular check
is reassigned to the source region, never accepted as evidence of a valid
dual frame. Checked integer storage guards against arithmetic overflow.

## Why merging completed pair outputs is insufficient

Fix a five-set target S and put `A=[h]\\S`, `n=h-5`. Its complete pair
partial for `C subset S` has sources `C union U` for every three-set U in A.
For a family E of pairs, regard E as a graph on the five vertices of S.
Let P_E be the rational column space of its unoriented incidence matrix.
The union of the source spans is

    { (s,b): s in P_E,  sum(b)=(3/2)sum(s) }.

It has dimension `n-1+rank(P_E)`. After removing the positive outside
zero-sum subspace, its Gram form is

    s dot t - (1/2-9/(4n)) sum(s)sum(t).

The determinant relative to the Euclidean Gram matrix is `1-gamma*w_E`,
where `gamma=1/2-9/(4n)` and `w_E` is the squared norm of the projection of
the all-one vector onto P_E. A nonbipartite connected component contributes
its size to w_E; a bipartite component with part sizes a,b contributes
`4ab/(a+b)`.

At h=28, `gamma=37/92`. All 1,023 nonempty E are nondegenerate: ten are
positive and 1,013 are indefinite. There are 533 full target-complement
spans. Exact determinants verify every case in
[ternary_target_spans.py](../../scripts/experiments/ternary_target_spans.py).

This valid aggregation gives no automatic role saving. Combining t complete
partials adds t-1 additions and replaces t outputs by one, leaving `c+q`
unchanged. A fused region with p inputs and its single summed output has
boundary rank one, hence the same `p+1-1=p` slot count.

Moreover these complete partials cannot serve other five-set targets.
Their spans contain every difference of two coordinates in A. Orthogonality
forces another target's indicator to be constant on A; including all A
would already meet every source in at least three points. It must exclude
A and therefore equal S. This argument applies for `h>=9`. Cross-target
savings must occur before the complete partials, or use a different physical
allocation scheme.

## Exact target-size verification

The local templates and top composition plan can be exported with
`ternary_target_fingerprint.py`. Its C++ fingerprint mode is only a discovery
screen; 256-bit hashes are not exact support equality. The separate
`ternary_target_exact.cpp` mode uses canonical zero-suppressed decision
diagrams, checking disjointness by exact family cardinality at every
addition. Both modes prune unused ancestors after support identification.
Every one of the 98,658 h=28 output families is also compared with a separate
ZDD construction of the expected family: five-set sources intersecting the
side target in exactly two points, or containing the retained pair. The
unpruned circuit has 10,302,667 additions; ancestor pruning retains
10,267,219. These are exact support counts, not fingerprint estimates.

The repeatable producer/frame check is:

```sh
python3 scripts/experiments/ternary_target_certify.py
```

The [driver](../../scripts/experiments/ternary_target_certify.py) compiles the
exact support and frame checkers, reconstructs the complete graph, verifies
every output, audits all final frames, and writes the
[producer certificate](../../certificates/ternary-target-network.json).
The full h=28 run takes about a
minute and several GB of memory on the development machine. Use `--workdir`
to retain its plan and DAG, or `--h 8` for a small exact control. The
certificate contains deterministic plan/DAG hashes, checker/proof hashes,
full-size counts, reassigned-frame statistics, and the proof obligations
connecting those checks to the retained wrapper. Its `unresolved_gram_families`
field counts the initial 60 dual candidates that are replaced; its final
`unresolved_source_nodes` and `final_unresolved_frames` are both zero.

This producer certificate does not by itself certify an integer
multiplication exponent: the [separate assembly checker](../../scripts/ternary_target_network.py)
uses the new role count and rechecks every recurrence and absorption inequality.
