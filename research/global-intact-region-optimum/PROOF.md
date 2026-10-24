# Global optimum for intact source regions

Krzysztof Wójt, with substantial OpenAI Codex assistance. Apache-2.0.
The graph model, source implementation and the first three power inequalities
are credited to Cinna Davis's PR4997 and its retained predecessor lineage.

## Statement and boundary

Take either orientation of the literal carried-frame word from Dugongue's
PR4971, head `0130b196145a43a7d305de41f49e56e8e8556378`, as retained in
`research/swap-contact-fusion-gate/inputs/`. Use exactly the graph and regions
defined by PR4997, head `5e1b9843f2b04cee1f4771fce2c62d0ac551d3d6`.
Every consumed file is pinned at this package's canonical-main base in
SOURCES.json. The original source files are unchanged.

**Theorem (finite fixed-model optimum).** For every real `0<t<1`, allowing
**any number** of intact free source regions to change their common binary
chart cannot lower the complete recursive moment. The original source chart
assignment attains the global minimum. Its full paid histogram remains

```text
rank:   1     2    3    4   5  8
count: 2201  412  510  127  40  8
```

The theorem is about both specified finite graphs, with a written reduction
and an exact finite certificate. It is not a universal obstruction to frame
optimization, a new supplier, a theorem about every address dimension, a
formal proof-kernel result, or a new κ.

In detail, the scalar ADD chronology, weighted field exchanges, literal signed
native maps, owners, all start/final charts, and owned-center copy/query/clear
interfaces are fixed. An edge `u -> v` carries an invertible binary map `M`.
Its charts obey `M F_u ⊆ F_v`, with price

`(dim F_v - dim F_u)^t`, with `0^t = 0`.

A region is a connected component of **source** identity-map, zero-rank edges.
Each such edge must remain zero: the entire region has one common new chart.
A region meeting a fixed boundary stays at that boundary chart. Unlike PR4997,
there is no restriction to one or two changed free regions.

All containing subspaces of `F_2^9` are granted; additional physical phase
restrictions are not imposed. This is the predecessor's favorable algebraic
relaxation. Extra paid physical work has no negative refund. The theorem does
not cover splitting a region, changing a fixed boundary, native maps, scalar
dependencies, center operations or the monotone containment rule. In particular,
PR4993's broader variable-boundary/split-region exploration remains separate.

## Fixed-boundary propagation exhausts the chart domain

Contract each intact region and retain **every original edge**, including
parallel edges and internal zero edges. A contracted free vertex is balanced:
its incoming and outgoing edge counts agree. Before contraction, an unfixed
scalar ADD contact has two incoming and two outgoing field strands. Internal
edges cancel in a contracted region. The verifier checks balance literally;
it does not infer balance from a vertex's name.

For each vertex initialize lower/upper spaces as follows:

* fixed vertex: `L_v = U_v =` its source chart;
* free vertex: `L_v = {0}`, `U_v = F_2^9`.

For every edge `u -> v` with map `M`, repeatedly apply

```text
L_v <- L_v + M L_u
U_u <- U_u intersect M^-1 U_v.
```

**Invariant.** Every feasible chart assignment satisfies `L_v ⊆ F_v ⊆ U_v`
at every step. It holds initially. For the lower update, `M L_u ⊆ M F_u ⊆ F_v`;
for the upper update, `M F_u ⊆ F_v ⊆ U_v` implies `F_u ⊆ M^-1 U_v`.
Thus each update preserves the invariant. Fixed values cannot change.
Every strict update changes a dimension, so finite-dimensional propagation
terminates. The source assignment remains a checked feasible witness.

In each orientation the fixed point takes six passes. Among the **768** free
regions, **565** are forced (`L=U`) and **203** have `dim U-dim L=1`.
An interval of dimension difference one has precisely two subspaces, `L` and
`U`: the quotient is one-dimensional. This includes every binary subspace,
not just coordinate subspaces. The verifier refuses a larger residual interval.

Consequently every feasible intact-region assignment is among these `2^203`
binary choices. Propagation alone is only a necessary screen: all original
edge constraints are checked again in the factor tables. No assertion that
every binary choice is feasible is used.

The variable interaction components have sizes/counts

```text
size:  1   2   3  5  17  33
count: 31  2  32  1   2   1
```

This decomposition is observed and checked on the source graphs. The proof
of completeness does not assume that local one/two-region optimality extends
to these components.

## Exact elimination over all simultaneous choices

Initially each original edge supplies a factor on its zero, one or two binary
endpoints. A feasible factor entry is its rank histogram; an infeasible entry
is explicitly absent. Grouping edges with the same scope adds their histograms
and intersects their feasible domains. Every factor owns an explicit disjoint
set of original edge IDs. Zero-rank edges remain counted.

Eliminate a variable `x` by collecting every factor mentioning it. For each
assignment of the remaining neighboring variables (the separator), add the
collected histograms for `x=0` and `x=1`. Discard an infeasible branch. If both
branches are feasible, choose one only after certifying that its price is no
larger **for every `0<t<1`**. Replace the bucket by that pointwise minimum
factor on the separator. Unknown comparisons cause failure, not a numerical
fallback or a tie. The deterministic minimum-degree order encounters at most
three separator variables in the actual graphs.

**Induction.** A factor created by elimination represents the exact minimum
price of its owned edges over its eliminated variables, conditional on its
separator. Initially this is just an edge's literal feasibility and price.
Collecting all factors containing `x` brings in every remaining dependence on
`x`; other factors are independent of it. The two branch minima and their
certified comparison therefore give the exact minimum over `x` as well.
Disjoint edge ownership prevents double charging or omission. The invariant
holds after replacement. At termination the constant factors give the global
minimum. Back substitution reconstructs one attaining assignment, which is
checked against every original edge and every fixed chart.

Rank mass is fixed when a balanced free chart changes. Indeed its contribution
to the sum of edge ranks is
`(indegree-outdegree) dim F_v = 0`. Thus two feasible bucket branches with a
fixed separator have equal edge counts and equal rank mass, including their
previously eliminated vertices. The verifier checks both equalities at every
comparison rather than using them as unchecked shortcuts.

The complete elimination trace, including both candidate histograms, chosen
branch, certificate kind and separator state, is in WITNESSES.json.gz. Bounds
and a reconstructed minimizing assignment are included. Replay compares the
decompressed canonical payload, not the platform-dependent gzip container.

## All-exponent comparison certificates

Write `f(r)=r^t`, `f(0)=0`, for `0<t<1`.

Equal histograms tie. Otherwise, if the chosen list of ranks majorizes the
alternative, concavity of `f` proves its price is no larger. The verifier checks
the equivalent hinge criterion at every integer threshold `s`:

`sum chosen_count[r] max(r-s,0) >= sum other_count[r] max(r-s,0)`.

The ranks are integers and hinge sums are piecewise linear between integers,
so those points suffice; equal count and sum are checked first. This is an
exact majorization test, not a sampled exponent test.

The remaining alternatives have a positive integer multiple of one of five
coefficient vectors, normalized by their integer gcd. Zero-rank coefficients
are retained for the edge-count identity, although `f(0)=0` contributes no cost.
The first three functions are from PR4997:

```text
A = -1 + 3*2^t - 3*3^t + 4^t
B = 12 - 8*2^t - 4*3^t + 4*4^t
D = 12 - 9*2^t + 3^t - 3*4^t + 3*5^t.
```

For completeness, their proofs are retained here with credit.
`A = Δ^3 f(1)>0` because `f'''(x)=t(t-1)(t-2)x^(t-3)>0` for `x>0`.

For `b=B/4`, put `l=log 2`, `p=log_2 3`. Since `3^5<2^8`, `p<8/5`, and

`b'''/l^3 = 8*4^t-p^3*3^t-2*2^t >= (8-p^3-2)*4^t > 0`.

Thus `b'` is convex and lies below its endpoint chord. Both endpoints are
negative: `b'(0)=-log 3`, `b'(1)=log(16/27)`. Therefore `b` decreases to
`b(1)=0`, and `B>0` for `t<1`.

For `D`, also put `q=log_2 5`. The integer inequalities `2^23<5^10` and
`23^3>11*10^3` give `q>23/10` and

`D'''/l^3 = 3*q^3*5^t+p^3*3^t-24*4^t-9*2^t >= (3*q^3-33)*5^t > 0`.

Again `D'` is convex, with negative endpoints
`D'(0)=log(375/32768)` and `D'(1)=log(5^15*27/2^42)`.
Hence `D` decreases to `D(1)=0` and is positive before that endpoint.
Every integer inequality used above is checked in the verifier.

The global elimination requires precisely two additional shapes:

```text
E = 12 - 8*2^t - 8*3^t + 12*4^t - 4*5^t
F =  7 - 3*2^t + 5*3^t - 9*4^t + 4*5^t.
```

Let `C_k = 2 f(k)-f(k-1)-f(k+1)`. Strict concavity gives `C_k>0`.
Since `f'''>0`, the sequence `C_k` is nonincreasing. One way to handle the
endpoint at zero rigorously is to apply the third-difference integral to
`(x+epsilon)^t` for `epsilon>0` and pass to `epsilon -> 0` by continuity.
Thus `C_1 >= C_4` as well.

The coefficient identities

```text
E = B + 4 C_4
F = 4(C_1-C_4) + C_2 + C_3
```

prove both functions strictly positive throughout `0<t<1`. Their integer
coefficient vectors are verified exactly. In each orientation, one elimination
comparison uses `E` and one uses `F`. These complete the global certificate;
no real-number root or floating logarithm is evaluated by the verifier.

## Source binding and scope of verification

The retained loader replays the PR4971 source's exact all-632-input endpoint,
dirty-helper, chart and paid-profile checks. The inherited Graph constructor
also checks that each signed native binary map actually carries its declared
chart. The new code authenticates and compiles source bytes directly; imported
bytecode cannot substitute for the pinned scientific modules.

The new solver independently implements binary subspace algebra and literal
edge feasibility. Its source graph contracts the same regions but imposes no
one/two-region bound. Both reconstructed global minima equal their original
strand histograms (29,966 edges forward and 29,974 backward, differing by eight
zero edges); all eight rank-eight center queries are then
added, producing the displayed full paid histogram. Their costs are fixed
and cannot disappear in an optimization factor.

An independently written small-graph oracle enumerates all subspaces of
`F_2^2` as explicit sets and all assignments in its fixtures, rather than
following the propagation or elimination algorithm. With edge ranks at most
two and fixed rank mass `m`, the cost is `m+n_2(2^t-2)`, so maximizing `n_2`
is an exact all-exponent oracle. It checks a coupled four-free-vertex fixture,
nonidentity maps, literal containment, every histogram and necessary bounds.
The receipt records its exact finite coverage. These controls corroborate the
algorithm; they do not alone prove the nine-dimensional source theorem.

No fresh absolute Clifford phase lowering, physical precision/tape price,
native all-column admission, complete controller/compiler/BIT/outer replay,
formal proof assistant or independent human mathematical review is claimed.
The global result is restricted to the precise favorable finite model above.
