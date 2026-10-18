# A dual ceiling of 40 for all Gaussian E8 clique certificates

Prepared by William Lawyer with substantial OpenAI Codex assistance.
Research note / scoped negative result. No new kappa or physical supplier.

## Result and its predecessor boundary

In the fixed 60-line Gaussian E8 geometry, **every nonnegative weighted-clique
certificate for the scalar binary decoder pairing-rank charge has value at
most 40 Gaussian rank units**. The weights may use every nonempty clique,
including singletons, non-maximal cliques, and mixtures of clique sizes.

Sagar Thakrar's PR738 already supplies the valid value-40 certificate, closure
to flats and the abstract decoder interval [40,60]. @chinmayarvind23's PR770
independently reproduces that result and proves the ceiling 40 for all
inclusion-maximal cliques. Its Section 5 explicitly excludes non-maximal
cliques. This note closes that certificate-domain gap. It neither finds a
cost-40 decoder nor improves the already established scalar lower bound.
The matching value-40 primal certificate is inherited from those pinned
sources; their unchanged full flat-pair replay is not repeated here.

## Geometry and the certificate class

Take the 240 doubled E8 roots in Q^8: the 112 vectors with two entries in
{−2,2} and all other entries zero, and the 128 vectors in {−1,1}^8 with an
even number of negative entries. Define J on each coordinate pair by
`(x,y) -> (-y,x)`. The roots are closed under J and J squared is −I.
Their orbits under {I,J,−I,−J} give 60 Gaussian lines in K^4, K=Q(i).
The check also establishes projective distinctness: for different chosen
roots r,s, `(r·s)^2+(r·Js)^2 < 64`, while every root has squared norm 8.

Let G be the graph joining distinct **nonorthogonal** Gaussian lines. For a
support S, write X_S for its K-span and

`c(R,A) = rank_K of the Hermitian pairing X_R by X_A`.

A fitting binary decoder has `B_tt=1` and `B_ts=0` for distinct nonorthogonal
lines t,s; entries at distinct orthogonal lines are free. Thus for any
nonempty clique Q of G, `B[Q,Q]=I_|Q|`.
If `B = sum_j 1_Rj 1_Aj^T` over F2, its restriction to Q has
rank at most `sum_j [Q meets R_j and Q meets A_j]`. This is the predecessor's
principal-identity rank inequality; it permits asymmetric supports and any
finite number of scalar totals.

A weighted-clique certificate is a nonnegative weight w_Q for each clique,
subject to the local domination inequalities

`sum_Q w_Q [Q meets R and Q meets A] <= c(R,A)`

for all source/reader supports (equivalently all their geometric closures).
Closure adds every configuration line in the same K-span: it preserves
pairing rank while only increasing clique-hit indicators. Hence constraints
on all closed supports imply the constraints on every smaller support;
closed supports are themselves permitted supports, proving the equivalence.
Its certified decoder lower bound is `sum_Q |Q| w_Q`. Repeated clique entries
can be combined. An empty clique contributes zero and can be omitted.
Negative weights and other submatrix or algebraic inequalities are outside
this certificate class. The theorem below bounds these certificates, not
arbitrary proofs of a decoder lower bound.

## Exact dual supports and their charges

For each configuration line t, let H_t be the set of configuration lines
orthogonal to t. All 60 H_t have 15 members and span the entire K-hyperplane
`t-perp` (Gaussian dimension three). There are 900 ordered pairs (t,u) of
distinct orthogonal configuration lines.

Retain only the following ordered pairs:

`D = {(t,u): t perpendicular u and |H_t intersection H_u| = 6}`.

Exact geometry gives **180** such pairs. Their undirected graph partitions
the 60 normals into fifteen disjoint four-vertex complete graphs. This is a
diagnostic structural check; the primary incidence calculation directly
counts the ordered pairs and does not need the partition.

For every pair in D, the local charge is exactly **2 Gaussian / 4 rational
rank units**. Indeed `X_Hu^perp=span_K(u)`, and orthogonality puts u in X_Ht.
The pairing kernel on X_Ht therefore has dimension one, so its rank is
`3-1=2`. The six-line intersection selects the useful pairs; it is not the
reason for that charge. Both implementations independently check all
hyperplane dimensions and all 180 pairing ranks by exact elimination.

For a clique Q, define

`h_D(Q) = # {(t,u) in D: Q meets H_t and Q meets H_u}`.

The exhaustive finite lemma is:

**For every nonempty clique Q of G, `h_D(Q) >= 9 |Q|`.**

Its complete domain and exact minima are:

| Size | Number of cliques | Minimum h_D |
|---:|---:|---:|
| 1 | 60 | 18 |
| 2 | 1,320 | 30 |
| 3 | 14,000 | 42 |
| 4 | 79,200 | 52 |
| 5 | 252,288 | 60 |
| 6 | 474,240 | 78 |
| 7 | 554,880 | 84 |
| 8 | 419,040 | 84 |
| 9 | 203,200 | 92 |
| 10 | 59,904 | 102 |
| 11 | 9,600 | 108 |
| 12 | 640 | 108 |

There are **2,068,372** nonempty cliques and no larger clique. Every inequality
holds in integer arithmetic. CERTIFICATE.json includes one attaining witness
per size, all 180 dual pairs, the frame partition, and the SHA256 of every
clique mask sorted numerically and encoded as eight little-endian bytes.

The primary traversal extends each clique in increasing vertex order. Every
clique has exactly one such sorted path; intersecting the available vertices
with each chosen vertex's neighbors retains exactly its possible extensions.
It visits every nonempty clique once, without a size cutoff or sample.

The independent traversal enumerates inclusion-maximal cliques with
Bron–Kerbosch, then all their submasks and deduplicates them. Every clique in
a finite graph extends to a maximal clique, so this covers exactly the same
domain by a different algorithm. It reconstructs geometry separately and
agrees on the complete domain digest and all size minima. These are exact
finite certificates, not a proof-assistant formalization.

## The all-clique ceiling

Apply each local certificate constraint to `(R,A)=(H_t,H_u)` for the 180
ordered pairs in D and sum. Their total charge is 360, giving

`sum_Q w_Q h_D(Q) <= 360`.

Nonnegative weights and the finite lemma give

`9 sum_Q |Q| w_Q <= sum_Q w_Q h_D(Q) <= 360`.

Therefore the certificate value is at most **40**. This is the explicit
dual, assigning weight **1/9** to each of the 180 local constraints. It
covers arbitrary nonuniform weights on all cliques, not just weights within
an orbit. No solver status or symmetry assumption about the weights is used.
Combined with the predecessor's feasible uniform value-40 certificate, it
settles the optimum of this entire specified certificate method at 40.

## Failed hypothesis and controls

The unmodified PR770 dual cannot simply be extended: with all 900 ordered
orthogonal pairs, a singleton Q={0} has 42 hits, below `45 |Q|`. This is a
concrete counterexample to the proposed extension, not a defect in PR770's
correctly scoped maximal-clique theorem. The retained result uses the
repaired dual above and checks its complete domain.

The primary replay rejects the original singleton inequality, the stronger
coefficient 10 (a size-12 clique has only 108 hits), an orthogonal pair called
a clique, an empty clique in the nonempty domain, the complementary 720-pair
dual with the proposed coefficient 36, and a deleted orthogonality edge.
The independent replay and package tests add their own controls.

## Scope and accounting

This closes a proof mechanism for copied-information lower bounds. It is
not a search for a cheaper decoder, an impossibility theorem for all decoder
mechanisms, or a bound on new geometries. The actual scalar decoder optimum
remains between 40 and 60 Gaussian charge units. Vector or nonlinear totals,
sub-line supports, changed fitting patterns, interacting delivery programs,
and stronger inequalities remain outside this result.

No helper, source-access operation, frame transition, restoration, recursive
child or assembly is implemented or priced as a new supplier. Translating
the abstract pairing-rank charge into physical costs inherits PR446 and the
predecessor's realization premises. The selected PR799 construction retains
its all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape and analytic obligations. This note does not change them or
the selected conditional kappa, and it does not prove the multiplication
theorem.
