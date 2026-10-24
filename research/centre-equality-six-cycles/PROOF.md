# The six-cycle case at fifteen owners

This is a written reduction to a finite exact enumeration, together with an
explicit counterexample that can be verified without trusting the reduction.
It is not a proof-kernel formalization. All graphs below are finite and simple.

## 1. Statement and inherited boundary

**Theorem.** Let G be a cubic bipartite graph with parts B and D of size 15.
Suppose G has no four-cycle and each vertex belongs to at most one simple
six-cycle. If G contains a six-cycle, then G is isomorphic, by a map preserving
the two parts, to the graph in [WITNESS.json](WITNESS.json). That graph has
exactly four six-cycles, and they are vertex disjoint. In particular, the
possible numbers of six-cycles are exactly **0 and 4**.

The existence assertion at zero uses the duad/perfect-matching graph already
given by Sagar Thakrar in PR3291. This package makes no new uniqueness claim
for the zero-six-cycle case.

This answers Nick Petalas's PR5182 question at its original boundary. His
cubic reduction and vertex-disjointness argument show that the theorem applies
to equality in PR3291: minimum degree at least three, |B|=15, no C4, and
c6(d)<=1 at degree three, c6(d)<=floor(deg(d)^2/4) otherwise. To make the
dependency explicit, PR3291's local bound is |B|>=5 deg(d)-c6(d). For
4<=deg(d)<=15 its lower bound exceeds 15, so D is cubic. If a B vertex
had degree at least four, rooting at a neighboring D vertex would produce
at least fourteen third-level incidences; at most one collision can save a
vertex, requiring |B|>=3+14-1=16. Hence B is cubic and |D|=15. Two C6s
sharing a B vertex would share an incident edge, and therefore a D vertex,
contradicting its cap. These observations are credited predecessor results,
not claimed as new here. No connectedness assumption is needed.

## 2. The forced neighborhood of a six-cycle

Fix one C6. Label its B vertices b0,b1,b2 and its D vertices d0,d1,d2,
so that bi is adjacent to dj exactly when i differs from j. Indices in this
proof belong to {0,1,2}. A repeated index is not a summation convention.

Write yi for the third D neighbor of bi, and xi for the third B neighbor
of di. These six vertices lie outside the C6: adding the missing bi-di
edge would create a C4. The three yi are distinct; if yi=yj, then bi and
bj would share that neighbor and the third cycle vertex dk, giving a C4.
The same reasoning makes the xi distinct.

There is **no edge xi-yj**. If i differs from j, such an edge closes the
four-cycle xi-di-bj-yj-xi. If i=j, take the two other indices k,l. The
path xi-di-bk-dl-bi-yi-xi would be a second C6 through a vertex of the
fixed cycle. Both alternatives violate a hypothesis.

Let Ui be the two remaining D neighbors of xi, and Vi the two remaining
B neighbors of yi. They are outside the cycle and its six external neighbors.
The Ui are pairwise disjoint. A vertex u in Ui intersect Uj, for i!=j,
would give the second cycle xi-u-xj-dj-bk-di-xi, where k is the third index.
Similarly, the Vi are pairwise disjoint.

Thus each part is partitioned into three cycle vertices, three external
neighbors, six vertices in the three pairs, and three remaining vertices.
Call the remaining sets F_B and F_D, each of size three.

## 3. The only remaining edges

There are no edges from Vi to Uj for i!=j. Such an edge v-u would complete
the second cycle bi-yi-v-u-xj-dj-bi through the fixed cycle.

The edges between Vi and Ui form a matching: two Vi vertices already share
yi, and two Ui vertices already share xi, so a vertex with two neighbors
in the opposite pair would create a C4. Let its size be s_i, at most two.
It is at least one. If s_i were zero, the two Vi vertices would need four
distinct neighbors in F_D: two each, with disjoint sets to avoid a C4
through yi. But |F_D|=3. Therefore

    s_i in {1,2}.

After independently labeling each pair, these matching edges are
v_i0-u_i0, and also v_i1-u_i1 when s_i=2. The remaining neighborhoods
of v_i0,v_i1 in F_D are disjoint and have sizes:

| s_i | v_i0 | v_i1 | Number of assignments to labeled F_D |
|---|---|---|---|
| 1 | one vertex | the other two vertices | 3 |
| 2 | one vertex | a different vertex | 6 |

Exactly the same alternatives hold for the neighbors of u_i0,u_i1 in F_B.
All other unfinished edges lie in F_B x F_D. There the only remaining
choices are the Boolean 3-by-3 matrices satisfying the residual degrees.
Every entry of the whole graph has now been specified or enumerated.

Some such completions still have C4s or excessive C6s. They are retained
until the final literal graph predicates; the reduction does not assume that
all parameter choices are admissible.

## 4. Complete finite domain and symmetry reduction

The verifier uses the following labels on each side:

| Role | B label | D label |
|---|---|---|
| cycle | bi=i | di=i |
| external | xi=3+i | yi=3+i |
| pair | v_ik=6+2i+k | u_ik=6+2i+k |
| remaining | 12,13,14 | 12,13,14 |

Permuting the three indices simultaneously on both sides preserves the fixed
cycle and sorts (s0,s1,s2). The four possibilities, in the order used by the
primary checker, are (2,2,2), (1,2,2), (1,1,2), and (1,1,1). Independent
permutations of F_D and F_B put the first pair's attachments in the first
option displayed by `attachment_options`: for s0=1, vertex 0 versus vertices
1,2; for s0=2, vertex 0 versus vertex 1. These relabelings do not constrain
any other unenumerated edge. Pair labels were chosen to put their matching
on the diagonal. Consequently **every admissible graph with a chosen C6 has
at least one enumerated representative**. Uniqueness of representatives is
not assumed.

`verify.py` enumerates all remaining attachments and all 512 Boolean free
blocks, retaining precisely those whose residual row and column sums fit.
It checks cubic degrees, all row-pair intersections for C4s, and every triple
of B vertices for C6s. In a C4-free graph each B pair has at most one common
D neighbor; a B triple forms a C6 exactly when its three common neighbors
exist and are distinct. Equal common neighbors form a claw, not a cycle.
Every six-cycle has exactly one B triple, so this procedure is exhaustive.

The finite result is:

| (s0,s1,s2) | Attachment pairs | Cubic completions | C4-free | Admissible |
|---|---:|---:|---:|---:|
| (2,2,2) | 1296 | 2176 | 496 | 0 |
| (1,2,2) | 1296 | 1728 | 816 | 16 |
| (1,1,2) | 324 | 324 | 112 | 0 |
| (1,1,1) | 81 | 81 | 4 | 0 |

These 16 survivors all have four six-cycles. The ordered, sorted list of
their incidence-row bit masks, serialized by the exact compact JSON command
in the checker, has SHA256
`436a29a84656b5b0e2d172e0c3c1a58077e877935d59d0e7a2a772ddecf57b3e`.
The digest records the result; it does not replace enumeration.

## 5. One isomorphism class

All 16 survivors are explicitly obtained from WITNESS.json using independent
choices of the following four involutions:

1. Exchange B13 and B14.
2. Exchange D13 and D14.
3. Exchange B8 with B9 and D8 with D9 simultaneously.
4. Exchange B10 with B11 and D10 with D11 simultaneously.

`witness_orbit` applies all 16 choices and compares the entire resulting
incidence-matrix set with the entire survivor set. These are explicit maps,
not an assumed graph-isomorphism heuristic. They establish the claimed single
isomorphism class containing a C6. Together with the exhaustive coverage
argument above, this proves the theorem by a finite computation.

## 6. A counterexample independently of classification

The witness's four C6s have B/D vertex sets

    {0,1,2}, {4,8,9}, {5,10,11}, {7,13,14}

on each side. Its other vertices are {3,6,12} on each side. Direct checks
show a connected cubic graph with 45 edges, no C4, and precisely these four
C6s. The four sets are disjoint, so every vertex satisfies the cap. This
alone disproves girth-eight rigidity, even if a reader has not accepted the
normal-form coverage or the isomorphism classification.

For comparison with PR5182, its integer defect E=C C^T C-4C-J has twelve
entries +1, twelve entries -1 and 201 zeros. The positive entries join
opposite vertices on a C6; the negative entries join different C6s. Both
supports are partial matchings on the 12 cycle vertices per side, and
E C^T is symmetric. These checks specialize the predecessor's necessary
identity to a realized nonzero defect; they do not constitute a new proof
of that identity.

## 7. Separate checks and limits

`independent.py` enumerates all eight labeled matching-size patterns and all
attachments, without sorting the patterns or fixing either free-side labeling.
It uses the adjacency fourth-moment identity for C4s and length-three path
counts for C6s. It finds 134,469 cubic completions, 42,948 C4-free cases and
432 admissible cases, all with four C6s. There are 144 survivors in each of
(1,2,2), (2,1,2), (2,2,1). Literal cycle walks corroborate every survivor.
This separately evaluates the supplied normal-form family; the universal
coverage still comes from Sections 2–4, not from two agreeing programs.

`literal_check.py` independently checks the witness by all-root simple-path
DFS and integer matrix multiplication. It also checks the classical zero-C6
duad/perfect-matching example and meaningful rejection controls. Separate AI
implementations are not independent human review.

Neither the abstract witness nor its classification assigns the actual
selected routes or solves scalar coefficient equations. The fifteen-owner
floor is unchanged. The result prevents deleting the six-cycle branch from
a future actual-route search; it does not provide a physical repair saving,
a complete paid invoice, a supplier, a new kappa or an integer-multiplication
theorem. No claim of literature priority for this abstract graph is made.

Prepared for Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
Exact predecessor references and attribution are in README.md and TASK.json.
