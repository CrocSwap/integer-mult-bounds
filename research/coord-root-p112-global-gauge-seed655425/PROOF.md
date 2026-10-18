# Exact identity and bounded cost obstruction

All root lines and normal vectors are the rational E8 model from the pinned `e8lab.py`. The pinned predecessor verifier supplies exact rational frame solving and the all-pairs identity checker.

Let `b_0,...,b_8` be the coordinate-frame-plus-root normals, with exact dependency

```text
sum_k z_k b_k = 0,
z = (-1,-1,-1,-1,0,0,0,0,2).
```

For every one of the 112 live root lines `r_i`, the verifier solves an exact rational row `c_i` with `sum_k c_ik b_k = 2r_i`. Given any integer vector `w`, define `t_i=<r_i,w>` and `D_ik=c_ik+t_i z_k`. Then

```text
sum_k D_ik b_k
= sum_k c_ik b_k + t_i sum_k z_k b_k
= 2 r_i.
```

Thus the row identity is exact throughout the searched box. The cost of term `k` is computed as the binary rank of the E8 label pairing restricted to the exact row support `X_k={i:D_ik != 0}` and normal support `Y_k={j:<r_j,b_k> != 0}`. The total is the sum of all nine term ranks, with no inactive term silently charged as active.

The executable enumerates the Cartesian product `{-1,0,1}^8` without sampling. Exact rational coefficients are scaled by their common denominator before zero tests; rank and census operations are integer/F2 operations. The result is two cost-64 assignments with an empty term, three fully active cost-72 assignments, and 6,556 fully active cost-73 assignments. The full all-active minimum in this finite family is therefore 72.

This conclusion is only about the pinned frame, puncture, shared-gauge rule and finite ternary box. It is not a lower bound for arbitrary per-root gauges or other frames. Exact all-pairs checks of the five cost-at-most-72 representatives confirm the decoder identities; a changed coefficient row gives a negative control.
