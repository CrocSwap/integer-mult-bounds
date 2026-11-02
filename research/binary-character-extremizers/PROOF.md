# Exact equality in the third binary character mode

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Let k >= 3 and let c be a zero-diagonal k-by-k matrix over F2, with at
least two nonzero entries. Interpret c_ij=1 as an arrow i -> j. Define

```text
Z(c) = sum over s in {0,1,2}^k of
       (-1)^(sum over i,j of c_ij [s_i=1][s_j=2]).
```

Nick Petalas's [PR5146](https://github.com/CrocSwap/integer-mult-bounds/pull/5146)
proves 0 < Z(c) <= 19*3^(k-3). Its second open question asks which graphs
attain the upper bound. The following is the new classification.

**Theorem.** Equality holds if and only if c has exactly two arrows, and
they have a common tail or a common head. Every other vertex is isolated.
There are exactly k(k-1)(k-2) labelled equality matrices. Each has even
entry weight, hence positive sign in the signed character expansion.

The proof uses an exhaustive new local equality lemma. It does not infer
the universal statement by testing a finite list of dimensions.

## The local equality lemma

For a zero-diagonal three-by-three binary matrix a with at least two
arrows and a binary field f=(u_0,v_0,u_1,v_1,u_2,v_2), put

```text
L(a,f) = sum over s in {0,1,2}^3 of
         (-1)^(sum a_ij [s_i=1][s_j=2]
                  + sum_i (u_i[s_i=1]+v_i[s_i=2])).
```

**Finite lemma.** |L(a,f)| <= 19. Equality in absolute value holds exactly
when a consists of two arrows with a common head or tail and f=0.
In those six cases L(a,0)=+19. There are no cases with L(a,f)=-19.

`verify.py:local_equality` proves this finite lemma by enumerating every
one of the (64-1-6)*64=3648 graph/field configurations and all 27 states
for each. The graph bits, in order, are

```text
(0,1), (0,2), (1,0), (1,2), (2,0), (2,1).
```

The complete equality rows are below. The field mask is zero in each row.

| Graph mask | Arrows | L |
|---:|---|---:|
| 3 | 0->1, 0->2 | 19 |
| 10 | 0->2, 1->2 | 19 |
| 12 | 1->0, 1->2 | 19 |
| 20 | 1->0, 2->0 | 19 |
| 33 | 0->1, 2->1 | 19 |
| 48 | 2->0, 2->1 | 19 |

The checker derives its expected equality condition from endpoint
incidence, rather than using this table to compute the sums. It retains
the complete table in the generated receipt. Every test uses explicit
exceptions and also runs under optimized Python.

## Reducing global equality to three vertices

We use PR5146's reciprocal-pair and directed-matching bounds as cited
premises. A reciprocal pair gives Z(c) <= 5*3^(k-2), strictly below the
target. If the arrows form a directed matching with r >= 2 arrows, then

```text
Z(c)/3^k = (7/9)^r <= 49/81 < 19/27.
```

Otherwise some two arrows share a vertex. Their endpoints form a set H
of three vertices with at least two induced arrows. For each fixed
outside assignment t, separate the character exponent into the induced
quadratic part on H, its induced unary field f(t), and its outside
constant q(t). Thus

```text
Z(c) = sum over t in {0,1,2}^(k-3) of (-1)^q(t) L(c_H,f(t)).
```

The finite lemma bounds each real summand above by 19. If the sum equals
19*3^(k-3), every summand must equal +19. At t=0, the field and constant
are both zero. The equality lemma forces c_H to be a two-arrow star.
For every other t it then forces f(t)=0 and q(t)=0, since its only
absolute equality value is L(c_H,0)=+19.

These requirements remove every possible outside arrow. For an outside
vertex v, set all other outside states to zero. The choice t_v=1 gives

```text
coefficient of [s_i=2] in f(t) = c_vi for each i in H.
```

The choice t_v=2 gives the coefficients c_iv of [s_i=1]. Thus f(t)=0
for these two assignments implies that no arrow joins v to H, in either
direction. This holds for each outside vertex.

If an arrow v->w existed entirely outside H, assign t_v=1, t_w=2 and
all other outside states zero. The only possible active outside term is
c_vw=1, even if the reverse arrow exists. Hence q(t)=1, contradicting
q(t)=0. Therefore the outside graph is empty. This proves necessity,
including k=3 where the outside set is empty.

## Attainment, count and signed multiplicity

For a common-tail star, condition on its center. States 0 and 2 each
contribute 9; state 1 contributes (1+1-1)^2=1. The sum is 19. Swapping
states 1 and 2 at every vertex transposes the graph and gives the same
value for a common-head star. Every isolated vertex contributes a factor
3, proving sufficiency.

Choose the center, an unordered pair of other vertices, and one of the
two orientations. The center and orientation are unique in every such
graph, so the exact labelled count is

```text
2*k*binomial(k-1,2) = k(k-1)(k-2).
```

Each matrix has exactly two entries. In PR4275's signed character law
its sign (-1)^|c| is therefore +1. Write its unnormalized power sum as

```text
S_n = sum over zero-diagonal c of (-1)^|c| Z(c)^n.
```

The coefficient of (19*3^(k-3))^n in S_n is exactly k(k-1)(k-2).
The walk count has the additional Fourier factor 2^(-k(k-1)); header
probabilities have their further finite-GL denominator. None of these
normalizations is included in the stated spectral multiplicity. This
is a direct corollary of the classification, not a calculation of the
rest of the spectrum or a new all-dimension probability inequality.

## Dependencies and limits

PR5146 supplies the character interpretation, sharp bound and explicit
equality question. The cited reciprocal and matching bounds are used as
published results, without auditing their predecessors. PR4275 supplies
the signed character law for the multiplicity corollary. Ryanson Jonathan
and PR4607 supply the five-event spectral context. The retained request
and normalizer lineage is credited in README.md.

Zero diagonal, F2 and the exact uniform three-state sum are essential.
The proof supplies no odd-field or weighted analogue, fourth-mode bound,
complete negative-association theorem, header producer, sampling/emission
procedure, native implementation, dirty restoration, complete physical
invoice, new kappa or complete multiplication theorem. The five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.
