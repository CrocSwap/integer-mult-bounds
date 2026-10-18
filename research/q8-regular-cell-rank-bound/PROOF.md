# Proof: Q8 regular-action cell-rank floor

Let `Q8 = {1,z,±i,±j,±k}` with `z=-1`, over `F_2`. Let `P_g` be the `8 x 8`
permutation matrix for left multiplication by `g` on the group basis. Let
`B >= 1` be the number of data bits in each address block and set
`Q_g = P_g tensor I_B - I_(8B)` over `F_2` (subtraction is XOR). For `r >= 1`,
let `u,v in F_2^r` satisfy `v^T u = 1`, and set `N = u v^T`. The full dirty
coupling is

```text
D_N(g) = I_(8Br) + N tensor Q_g.
```

This is exactly the address-changing linear map on the `r` roles; roles outside
the rank-one coupling are retained by the identity term.

## Rank of the displacement

The left-regular permutation by an element of order `d` partitions the eight
group elements into `8/d` cycles, each of length `d`. On one cycle, the kernel
of `P_g-I` consists exactly of constant vectors, hence has dimension one over
`F_2`; its rank is `d-1`. Therefore

```text
rank(P_g-I) = 8 - 8/d.
```

This is zero for `g=1`, four for `g=z` (order two), and six for every noncentral
element (order four). Tensoring with `I_B` gives
`rank(Q_g) = B * rank(P_g-I)`. Since `v^T u=1`, `N` has rank one. Matrix tensor
rank is multiplicative, so

```text
rank(D_N(g)-I) = rank(N tensor Q_g) = rank(N) rank(Q_g)
               = 0, 4B, or 6B,
```

for the identity, central, or order-four labels, respectively. This holds for
every allowed `r,u,v,B`; no enumeration hypothesis is used.

## Factor-count consequence

Suppose an implementation is a product `M = M_m ... M_1` of invertible
same-dimension binary linear maps with `rank(M_j-I) <= 1` for each instruction.
For any two square matrices,

```text
AB-I = (A-I)B + (B-I),
rank(AB-I) <= rank(A-I) + rank(B-I).
```

Induction gives `rank(M-I) <= sum_j rank(M_j-I) <= m`. If `M=D_N(g)`, the
preceding identity forces

```text
m >= 4B   when g=z,
m >= 6B   when g has order four.
```

The bound is necessary only. No matching shortest factorization is proved, and
the factors here are bit-cell rank-one updates. A block-wide XOR or a router
may have displacement rank greater than one and therefore falls outside this
instruction count.

## Scope

The result assumes an exact, in-place binary linear implementation of the
regular action on eight equal-width blocks, a rank-one idempotent role coupling,
and a cost of one per invertible rank-one displacement update on the combined
`8Br` data cells. It does not price array allocation, routing, tape/head motion,
hosting, or recursive stock. It says nothing about a native call whose
operation is wider than a rank-one bit-cell update.
