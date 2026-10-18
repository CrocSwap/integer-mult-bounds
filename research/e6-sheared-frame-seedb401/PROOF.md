# Exact statement and support-cell proof

## Finite statement

Fix the exact E6 root lines and basis reconstructed from the pinned `ade.E6b()` ordering, their Gram matrix `H`, the coordinate matrix `X`, and the dense pairing `B0` with unit diagonal and off-diagonal ones only on orthogonal root pairs. For every signed elementary transvection

```text
A = I + epsilon E_ij,   i != j,   epsilon in {-1,+1},
```
for every direction `a` in the union of the 36 projective E6 root directions and the 364 projective nonzero ternary vectors in the pinned basis, and for every rational `lambda != 0`, define `c=A^-1 a` and

```text
p_j = X A e_j,      q_j = X(H A^-T e_j - lambda c_j a),  j=1,...,6,
p_7 = X a,           q_7 = lambda X a.
```

The exhaustive support-cell census finds minimum raw cost 37 and minimum active-term Theorem C cost 37. Thus no seven-active decoder in this declared finite family has cost at most 35. The result is not a lower bound for all E6 seven-term decoders.

## Identity

As matrices in the six-dimensional coefficient space, the first six factors have sum

```text
A (H A^-T)^T - lambda (A c) a^T
  = A A^-1 H^T - lambda a a^T
  = H - lambda a a^T,
```

using symmetry of `H` and `A c=a`. The seventh factor contributes `lambda a a^T`. Multiplying by `X` and `X^T` proves `sum_{j=1}^7 p_j q_j^T = X H X^T = G`. Each root has norm squared 2, and `B0` is one only on the diagonal or orthogonal pairs, so `B0` is admissible. The verifier checks this identity for both `A=I` and `A=I+E_01`, then rejects a reversed correction sign and an omitted seventh term.

The first independent basis rows have root indices `[0,1,2,4,6,20]`; the first nonsingular ambient minor uses columns `[0,3,4,5,6,7]`. The canonical root digest, exact basis Gram and `rank_F2(B0)=7` are pinned in [CERTIFICATE.json](CERTIFICATE.json).

## Exhaustive lambda cells

For each `A,a`, the left supports are fixed. The seventh right support is fixed for nonzero lambda. Each coordinate of the remaining right factors is affine:

```text
q_j(t) = X_t H A^-T e_j - lambda * (A^-1 a)_j * (X_t a).
```

A nonzero slope has one exact rational zero. A zero slope gives either an identically zero coordinate or one that never vanishes. The verifier inserts every nonzero zero with `0` as a partition cut, evaluates every nonzero breakpoint itself, and one rational point in every open interval, including both tails. This represents every allowed lambda with exactly the same support. Degenerate terms are counted by their actual active total count; no zero term is charged the floor `w=5`.

Across the 60 signed transvections and 365 directions there are 143,343 distinct nonzero breakpoints. Including the zero cut gives `2*(60*365+143343)=330486` point/interval representatives. The search is split into two reproducible shards of 30 transvections.

## Cost

For each `B0[R_j,A_j]`, binary Gaussian elimination computes `r_j` exactly. The raw cost is `sum r_j`; the full Theorem C charge is `sum max(5,r_j)` over active terms. The complete cost histogram ranges from 37 through 45, with counts in [CERTIFICATE.json](CERTIFICATE.json). The least-cost witness is `A=I+E_23`, `a=(1,-1,1,0,0,1)`, `lambda=1/2`; its ranks are `(6,0,6,6,6,6,7)`, leaving six active totals at cost 37. All seven-active cells also have cost at least 37 because the full histogram contains no cost below 37. The six-term square benchmark 36 is cited from the open request and is not recomputed here.

No source accesses, copied-information realization, frame transitions, hosting, restoration, precision, recursive children or supplier integration are supplied. The result does not change the selected frontier or establish a multiplication bound.
