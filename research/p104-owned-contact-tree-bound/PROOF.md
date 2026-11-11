# Dimension floor for independently relabeled owned contacts

Fix the literal #7277 scalar chronology, role incidences and all
public or mixed contacts. An eligible vertex is an owned INIT, CLEAR
or SCALE, or an ADD or COPY whose operands are both owned. Each shared
scalar contact receives one chart label. A role edge joins consecutive
contacts of the same lifetime. Edges with one fixed endpoint inherit
that endpoint's original chart. Each component covers all its incident
role edges, and two components cannot touch the same edge.

## Lower bound for replacement transport

For two canonical charts corresponding to subspaces U and V, the
relative Clifford rank is bounded below by

```text
dim(U) + dim(V) − 2 dim(U ∩ V) ≥ |dim(U) − dim(V)|.
```

The signed price at the specified probe is
`H(r) = r^(1−κ)` with `H(0) = 0`. A single transport costs at least
`H(|dim(U) − dim(V)|)`. A sequence of intermediate transports also
costs at least this amount. Triangle inequality bounds the sum of
successive dimension differences and subadditivity of H bounds the
price of their sum. This argument grants access to arbitrary chart
labels and charges no incremental phase, ownership, precision,
routing, restoration, tape or scalar work. Any physical replacement
under these fixed contact premises is subject to the lower bound.

Every fixed endpoint has dimension in `[0,9]`. Clamping any proposed
dimension to this interval preserves those endpoints and cannot
increase any absolute difference. The optimization over dimensions
0 through 9 therefore lower-bounds the minimum paid transport over
every chart dimension. It includes labelings that may lack actual
charts or fail signed operator compatibility. Those extra possibilities
make the computed cost a lower bound.

## Exact tree recurrence

Combine each parallel edge into one link with multiplicity m. The
reconstructed 138 components are trees after that step. For a node u
with dimension d, its fixed boundary cost is the sum of
`H(|d−b|)` over the multiset of its fixed endpoint dimensions b.
Orient the component away from one root. A child v contributes

```text
min over q in [0,9] of (child subtree cost at q + m H(|d−q|)).
```

The tree gives disjoint child subproblems conditioned on d. Summing
the boundary and child terms and minimizing at the root therefore
gives the entire relaxed component minimum. The 118 components with
no original paid rank have nonnegative replacement cost and cannot
save. The old edges in the remaining 20 components are nested and
the original paid rank equals the absolute dimension difference.

The replay first computes a lower bound with downward-rounded
tariffs. Subtracting this lower bound from upward-rounded original
cost yields total apparent saving at most `119/(5 × 10^47)` over all
17 copies. A second leaf-elimination pass compares exact histograms.
For two histograms, subtract their counts and use the lower tariff
for positive differences and the upper tariff for negative ones.
A nonnegative resulting lower bound proves that the chosen
histogram minimizes the actual moment. All 6,100 comparisons resolve
at the incumbent probe. In each paid component the certified
minimizer histogram equals the old one. The total saving upper is
therefore exactly zero there. This assertion establishes an
attained minimum cost, allowing different label assignments or
tied histograms when the prices agree.

## Complete invoice

All native productive fields are fixed because the public boundaries
stay fixed. The verified original 17-copy invoice has 110,536 paid
jobs, 22,461 productive positions and rank surplus 1,424. We keep all
caller costs and productive fields. The probe is the exact upper
endpoint of #7277's independently certified crossing enclosure,

```text
91141748217473298207420876011401/25000000000000000000000000000000000.
```

The directed complete net upper remains

```text
−2004494395516543389/1000000000000000000000000000000000000000000000000.
```

The negative sign excludes a strict step clearing this probe by this
mechanism. The result leaves changes inside the old crossing enclosure,
changed scalar chronology or role incidences, coupled public/owned
labels and new caller or provider contracts as separate questions.
