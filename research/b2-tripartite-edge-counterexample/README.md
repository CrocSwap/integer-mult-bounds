# Nine lines refute the B2 acyclic-edge strengthening

An admissible three-total configuration has

```text
v = 9, H = empty, |F| = 9,
cost(B) = 21 < masE(W[F]) = 27.
```

This settles **open next question 1** of Aaron Wang's
[CR2/B2 audit #2293](https://github.com/CrocSwap/integer-mult-bounds/pull/2293).
The valid vertex version of DreamingOfClouds's
[Theorem B2, section 2.2](https://github.com/CrocSwap/integer-mult-bounds/blob/113a718265c62aec301c5695f4bfb9c421bef7ab/research/char2-jets/README.md)
uses the **number of vertices in a largest induced acyclic subgraph**, not
the number of edges in a largest acyclic edge subset. For this witness the
two numbers are 3 and 27. The full wild pattern equals B's off-diagonal
support, so restricting wild edges to the chosen pairing does not repair
the edge version. The selected frontier is unchanged.

## Inspect or replay

[WITNESS.json](WITNESS.json) contains all nine integer vector pairs and
the complete binary pairing. From the repository root:

```sh
python3 -B research/b2-tripartite-edge-counterexample/verify.py
python3.12 scripts/research_package.py --package research/b2-tripartite-edge-counterexample
```

Expected status: `PASS_B2_TRIPARTITE_EDGE_COUNTEREXAMPLE`. The registered
replay runs normal and optimized Python; its acceptance predicates remain
active under `-O`. Only the standard library is needed.

## Construction in the stated model

PR #2162 uses indexed rational vectors p(t), q(t) in Q^3 with nonzero
diagonal dot products. A binary B is admissible when its diagonal is one
and every off-diagonal one occurs at a zero rational dot product. For
coordinate supports R_j and A_j,

```text
cost(B) = sum_(j=1)^3 rank_F2 B[R_j, A_j].
```

H consists of harmonic lines with two equal diagonal contributions; F
contains indices where both vectors have full support. A wild incidence
is a zero off-diagonal dot product using all three coordinates. Configurations
are indexed lists; the stated model does not require distinct points or lines.

Take k copies of each pair, indexed by (i,a), with i in {1,2,3}, 1<=a<=k:

| i | p_i | q_i |
|---|---|---|
| 1 | (1,1,1) | (6,-5,1) |
| 2 | (1,2,4) | (3,-4,1) |
| 3 | (1,3,9) | (2,-3,1) |

The cross-dot matrix is diag(2,-1,2): evaluate (x-2)(x-3), (x-1)(x-3)
and (x-1)(x-2) at x=1,2,3. Precisely the cross-type pairs are incidences.
All vectors have full support, so H is empty and |F|=v=3k.
With I_k the identity and J_k the all-ones matrix, choose

```text
      [ I_k  J_k  J_k ]
B_k = [ J_k  I_k  J_k ].
      [ J_k  J_k  I_k ]
```

Its off-diagonal ones are exactly the cross-type incidences, so B_k is
admissible. Each of its three coordinate-support blocks is the whole B_k.

## Rank and acyclic counts: proof for every k

Write x in three length-k blocks x_i, and let s_i be the coordinate sum
of x_i in F2. The equation B_k x=0 says

```text
x_1 = (s_2+s_3) 1_k,
x_2 = (s_1+s_3) 1_k,
x_3 = (s_1+s_2) 1_k.
```

For even k, summing each block gives s_i=0, hence x=0. For odd k, the
equations are equivalent to x_i=s_i 1_k and s_1+s_2+s_3=0. Every such
triple is a kernel vector, giving nullity two. Therefore

```text
rank_F2(B_k) = 3k      for even k,
              3k - 2  for odd k;
cost(B_k) = 3 rank_F2(B_k).
```

The wild graph is complete bidirected tripartite with three parts of size k.
An acyclic edge set retains at most one direction of each cross-part pair,
or it would contain a 2-cycle. There are 3k^2 such pairs; ordering the parts
and keeping every forward edge attains that bound. Thus masE=3k^2.
An induced acyclic vertex set lies in one part, since any cross-part pair
forms a 2-cycle; thus masV=k.

Since v-|H|-|F|=0, the proposed edge bound exceeds the actual cost by

```text
masE - cost(B_k) = 3k(k-3)       for even k,
                  3(k-1)(k-2)   for odd k.
```

This is positive for every k>=3. At k=3, rank=7, cost=21, masE=27,
masV=3 and there are 54 directed wild edges. At k=1 the edge inequality
is tight (3=3); k=2 does not violate it (18>12). Thus k=3 is the first
counterexample **in this equal-multiplicity family**.

Repeating the three rational types makes the edge count quadratic but
the rank cost only linear. The proven vertex bound respects repetition.
Neither the vertex theorem nor target (A), cost(B)>=v, is contradicted.

## Independent checks and limits

The verifier imports no predecessor implementation. It checks every rational
dot product, admissibility and actual coordinate support. It derives each
block rank twice: by pivot elimination and by enumerating its entire F2 row
space. It computes masE by exact subset dynamic programming over all vertex
orders and masV by induced-subgraph cycle tests. Both graph searches cover
512 subsets at v=9 without assuming tripartite structure.

Controls reject a zero B diagonal, a within-type nonincidence, a perturbed
rational point and a zero rational diagonal. A directed 2-cycle and dependent
binary rows check the graph/rank primitives. Two simultaneous reindexings
preserve all results; k=1,2 are tight/nonviolating controls. Elimination also
checks the proved rank formula for k=1,...,16; the all-k conclusion rests on
the proof above, not on those finite checks.

This evaluates an explicit B, not its globally minimum cost. No globally
smallest-v claim, physical supplier construction or new kappa follows.
Local normal/optimized replay evidence and environment are recorded in
[TASK.json](TASK.json); maintainer review and hosted CI are separate.

## Coordination and credit

Canonical investigation: [Discussion #2331](https://github.com/CrocSwap/integer-mult-bounds/discussions/2331).
Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
TASK.json records the changed scope from `uniform-transfer-audit` to the
named decoder-bound handoff. [SOURCES.json](SOURCES.json) pins the model and
audit references; the self-contained verifier has no external data inputs.

Aaron Wang's [contemporaneous smaller-core search](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18941591)
received this complementary analytic family in
[a coordination reply](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18941680).
The separate split-minmax audit is outside this package.

The model and B2 are DreamingOfClouds's (#2162, following #2111/#1590).
Aaron Wang, assisted by opencode, identified the edge/vertex distinction and
posed this question in #2293. This counterexample, family proof and verifier
were prepared by ROTl24 with substantial OpenAI Codex assistance.
Checked by the contributing agent; independent human and proof-assistant review remain open.
New work is Apache-2.0.

## Open next questions

The named edge-form question is settled. The downstream correction is to
define MAS explicitly as a maximum **induced acyclic vertex-set cardinality**
when using B2(iii). No further search is required for that correction.
The general three-total target (A) remains open; a smaller counterexample
or a restriction forbidding repeated vectors is not needed to decide this
stated model. This package therefore proposes no additional search.
