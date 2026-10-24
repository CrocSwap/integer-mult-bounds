# All fixed translation-line gauges on the paired wire graph

This result is about the pinned scalar program. It does not give a lower
bound for arbitrary centre encodings or arbitrary frame changes.

Fix any nonzero `a in F_2^9`. On each scalar-connected component, choose
the right gauge `I` or `C_a` independently. Impose only the paired boundary
constraints in `root/BOUNDARY-GAUGE.md`. The minimum change in total native
rank is zero. The constant choice attains zero.

The odd-line part has exact path certificates and a source-derived
checker. Separate-agent review passed. The reviewer rebuilt both source
graphs and used 9-by-9 symplectic pairing matrices to check all 1,609,650
distinct-pair ranks. It checked all 10,488 integer paths and rejected seven
damaged certificates under optimized Python. The receipt is
`encoded-controller/review/ALL-LINE-PATH-REVIEW.json`. The earlier
common-line flow and threshold results also have independent review.

## Exact source and rank prices

The source is commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` and the
selected replay archive named in `GAUGE-RESULTS.md`. The checker verifies
the archive and member hashes. It uses the source and graph reader from
the independently reviewed temporal-reuse lane, at SHA-256
`204fdb8173f0dcf268ab145416b97e4a41c6a54ec877386d3b7aa73fb524c860`.
It does not import the path producer or its rank-price formula.

The exact scalar maps are checked on all 712 input columns in both
orientations. The checker rebuilds all scalar access and boundary
equalities. The graph has 1,979 components and 5,064 native events,
including every old rank-zero wrapper. It has 3,150 distinct ordered
frame pairs. Only eight cleared private components meet no native event.

For each canonical frame, use the binary Lagrangian

    L_U={(u,u+v): u in U, v in U-perp}.

The symplectic action of `C_a` is

    (x,z) -> (x+a(a dot z),z).

This map is an involution and preserves the symplectic form. Therefore a
crossing of the binary gauge bit has the same native rank change from
either side of an edge. Two equal bits leave its rank fixed. The checker
computes each changed rank as `dim(L_U+C_a L_V)-9` by binary elimination.
It checks 806,400 distinct-pair ranks for the 256 odd lines. The 255 even
lines need no cut optimization: each individual changed edge has rank at
least its old rank. That is checked on a further 803,250 pairs.

## An integer path proof for each odd line

Combine parallel graph edges after each native edge is priced. Write the
result as

    E(epsilon)=sum_e w_e [epsilon_u != epsilon_v].

For every negative edge `(u,v)` with weight `-d`, route exactly `d` units
from `u` to `v` along paths that use only positive edges. Use a positive
edge of weight `c` at most `c` times, counting all path amounts. The
receipts store integer amounts and the full vertex path for every route.

For any binary cut, a path crosses the cut at least once when its
endpoints are separated. Thus each negative demand is bounded by the
positive capacity assigned to its paths. Sum this inequality over all
negative edges. No positive capacity is counted too often, so
`E(epsilon)>=0` for every cut. This argument does not require a small
negative-edge vertex cover or a claim about a solver's optimum.

`WIRE-GAUGE-ODD-PATHS.json.gz` has certificates for 255 odd lines.
`WIRE-GAUGE-LINE42-PATHS.json.gz` supplies the remaining line, 42. The
checker verifies that their successful entries cover all 256 odd lines
exactly once. It checks every negative demand, path endpoint, path edge,
integer amount, and positive capacity. A failed greedy path order is
only a failed search, not an obstruction or a negative cut.

The same rank result applies to the backward program. The source graphs
are isomorphic, and `C_a` commutes with the full translation Fourier
operator `F`. In the backward frames `D_U=T_U F^-1`, use the same `C_a`.
Both changed labels differ from the forward labels by the same `F`.

## Limits and continuation

For odd lines outside the 16-line common centre intersection, total rank
does not settle every child moment. A cut of rank change zero could still
have a different rank profile. The path receipts alone do not exclude
that possibility. The common 16-line families have the stronger reviewed
threshold-cost result in `temporal-reuse/GAUGE-REVIEW.md`.

For each even line, every native edge rank is nondecreasing. Therefore any
sum of nondecreasing functions of those ranks is also nondecreasing. This
is a native-rank-cost conclusion. It does not price finite implementation
costs or a changed global hosting construction.

This result permits unrelated wire segments to use different bits. It
does not permit their line `a` to differ: `a` is fixed for the whole
program. It also leaves open general Clifford gauges, new scalar
operations, new controllers, and joint recursive child interfaces.

Before any PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
This note was prepared with OpenAI Codex assistance.
