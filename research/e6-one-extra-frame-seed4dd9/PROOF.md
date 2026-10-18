# Exact statement and support-cell proof

## Statement

Fix the 36 E6 root lines in the canonical order reconstructed from the pinned `ade.E6b()` source, the six-row rational basis chosen by its first independent root lines, and the dense pairing `B0` with `B0_tt=1` and off-diagonal `B0_ts=1` exactly when `G_ts=0`. Let `X` be the exact root-coordinate matrix and `H` the Gram matrix of the six basis roots, so `G=XHX^T`.

For each direction `a` in the union of (i) the 36 projective E6 root-coordinate rows and (ii) the 364 projective nonzero vectors in `{-1,0,1}^6`, and each nonzero rational `lambda`, form

```text
p_i = X e_i,                     q_i = X(H e_i - lambda a_i a),  i=1,...,6,
p_7 = X a,                       q_7 = lambda X a.
```

Across all such directions and rational `lambda`, the least sum of the seven block ranks `r_j=rank_F2 B0[supp(p_j),supp(q_j)]` is 40. The least Theorem C charge `sum_j max(5,r_j)` is also 40. This is a finite statement about this declared family, not all seven-term decoders.

## Identity and admissibility

In the six-dimensional coefficient space,

```text
sum_{i=1}^6 e_i (H e_i - lambda a_i a)^T + a(lambda a)^T
  = H^T - lambda a a^T + lambda a a^T
  = H,
```

because `H` is symmetric. Multiplying on the left by `X` and on the right by `X^T` gives `sum_j p_j q_j^T=G`. Each root has norm squared 2, and `B0` has ones only on the diagonal and off-diagonal orthogonal pairs, so `B0` is admissible for this Gram decoder. The verifier reconstructs the 120 E8 root lines, filters the pinned A2-orthogonal E6 subsystem, derives `X` over `Q`, and checks `X H X^T` against all ambient inner products exactly.

The basis root indices are `[0,1,2,4,6,20]` and the first nonsingular ambient coordinate minor is `[0,3,4,5,6,7]`. The exact basis Gram and root-input digest are in [CERTIFICATE.json](CERTIFICATE.json). The F2 rank of `B0` is 7; Theorem C's per-total floor for this unit is `w=5`.

## Why the lambda census is exhaustive

The supports of `p_1,...,p_7` do not depend on `lambda`. For `lambda != 0`, the support of `q_7=lambda Xa` is also fixed. Each coordinate of each other right factor is affine in `lambda`:

```text
q_i(t) = X_t H e_i - lambda * a_i * (X_t a).
```

If its slope is nonzero, it can change zero/nonzero status only at the exact rational breakpoint

```text
lambda = (X_t H e_i) / (a_i * X_t a).
```

If the slope is zero, the coordinate is either identically zero or never zero, so it adds no breakpoint. For each direction the verifier takes the union of every nonzero breakpoint with `0`, evaluates each nonzero breakpoint, and selects one rational point in every open interval, including the two unbounded intervals. The zero point is excluded from the decoder domain but retained as a cut. Thus every allowed rational `lambda` has exactly the same seven supports as one enumerated point. All seven terms are nonzero at every enumerated point; the verifier rejects a degenerate total instead of charging it the per-total floor.

The full union has 365 directions and 1,971 distinct nonzero breakpoints across them. Including 0 as a cut, this gives `2 * (365 + 1,971) = 4,672` point/interval representatives. The 36-root-direction initial slice has 247 nonzero breakpoints and 566 representatives.

## Cost computation and result

For each support pair, binary Gaussian elimination computes `r_j` exactly over `F2`. The raw sum is `sum r_j`; the fully charged sum is `sum max(5,r_j)`. Both histograms and all six minimum witnesses appear in [CERTIFICATE.json](CERTIFICATE.json). The minimum witness directions use `lambda=1`; their raw and charged cost is 40. The six-term reference factorization is checked independently as an exact identity and has ranks `(6,7,6,6,6,6)`, cost 37. The separate square-decoder lower benchmark of 36 comes from the open request and is not used in the finite result.

The verifier also checks two positive exact identities, and negative controls for a reversed correction sign, an omitted seventh term, and an inadmissible pairing edge. No arithmetic for sources, copying, frames, hosting, restoration, precision, interfaces or recursive children is supplied by this factorization; the result therefore makes no multiplication-bound or `kappa` claim.
