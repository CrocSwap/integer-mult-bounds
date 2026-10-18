# Exact exterior-rank floor

Let `b_0,...,b_8` be the coordinate-frame-plus-root normals on the pinned P112 puncture. The exact dependency is

```text
sum_k z_k b_k = 0,     z=(-1,-1,-1,-1,0,0,0,0,2).
```

For every live root line `r_i`, the predecessor solver gives an exact base row `c_i` with `sum_k c_ik b_k=2r_i`. Any rational gauge `t_i` produces another exact row `c_i+t_i z`. Thus arbitrary rational gauges on a selected set of rows preserve the identity, including all 112 squared live pairs.

For term `k`, let `X_k` be the binary pairing rows from the nonzero coefficients and `Y_k` the fixed normal support. If a proposed local edit changes only rows in a selected block union `B`, the untouched exterior rows give a submatrix of the full pairing matrix. Adding rows cannot lower binary rank, so

```text
sum_k rank_F2(X_k,Y_k) >= sum_k rank_F2(X_k restricted to i outside B,Y_k).
```

The verifier constructs a deterministic partition of the 112 live E8 lines: repeatedly take the smallest remaining index and append the smallest remaining lines orthogonal to all already chosen until an eight-line block forms. It certifies 14 disjoint orthogonal blocks covering P112. For each of the 14 individual blocks and 91 unordered block pairs, it computes the exact exterior-row rank vector using the canonical per-root sparsest gauges outside the selected union.

The singleton floor histogram is `67:2, 68:12`. The pair floor histogram is `64:1, 67:24, 68:66`; the unique 64 case has fixed ranks `(8,8,8,8,8,8,8,8,0)`. Hence no decoder in this scoped family can beat copied-information cost 64, even with arbitrary rational gauge choices on the changed rows. The argument does not permit coordinated changes on three or more blocks, changes to exterior rows, a different frame, or a different puncture.
