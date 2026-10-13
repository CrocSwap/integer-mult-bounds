# Independent synthesis review

Reviewed the Gaussian scalar implementation, exact phase-endpoint controls, current mixed-center image verifier, completed-child profile verifier and Lean accounting module against PR46 `71b6c960c89295e952522dd44111df9cfc51ae90`.

## Conclusions

The reviewed `(1+i)` arithmetic, inverse butterfly, denominator alignment, exact mixed-center fresh difference and weighted precision accounting are mathematically consistent. The finite controls are appropriately described as scalar/phase reference checks, rather than full physical/tape compilation. No new multiplication exponent was established.

The community source ledger covers PR1–46, with their bodies, full paginated changed-file lists and pinned heads. It records 5,380 cumulative changed-file records. Every nonremoved file blob URL matched the snapshot head. Swapnil's Round6 source is separately pinned at `f2176bc1124821bf17eb63725bd366d7bdc020a3`.

## Phase endpoint and the sign

Put `pi=1+i` and `C=(iI+X)/pi`. For an involution `X`, `C^2=X`. For an eligible binary norm-one line `u`, its translation kernel is the phase operator `T=C_u`. In PR46 the tensor of two triple generators has binary norm one and integer weight nine. Therefore `T^-2=X_u`.

The coordinate tensor `F` commutes with translations. On coordinates selected by `u`, `F X_u` has `C^-1` rather than `C`. Since `C^-1=-i Z C Z`,

```
Z_u F T^-2 Z_u = (-i)^9 F,
i^9 Z_u F T^-2 Z_u = F.
```

The `i^9` sign in `verify_phase_endpoint.py` is correct. Its `mask=511` is a weight-nine norm-one mask. Physical weight-nine positions can be permuted to this mask, and a complete coordinate tensor is invariant under that axis permutation. The finite tests use one parallel column; the written tensor identity extends the scalar factor to `i^(9f)` for `f` columns. The test constructs the retained endpoint formula and audits its correction and normalization; it does not reconstruct the full preceding framed producer schedule.

The paid correction follows by `A=-Fy`, `E=F T^-1`, hence `T^-1 A=-Ey`, so it cancels the dirty `Ey` contribution from `B=F T^-2 x+Ey`. Scalar scratch restoration and physical endpoint `C_F` on each dirty role must remain distinct.

## Norms and a necessary negative control

Every coefficient of `C` has complex modulus `1/sqrt(2)`. The absolute complex row sum of `C^tensor D` is exactly `2^(D/2)`. Unit fourth-root phases and address permutations preserve this quantity.

For the real/imaginary component box norm, the valid integer-bit bound is `2^ceil(D/2)`. It must not be stated as `2^(D/2)` for odd `D`. A concrete negative control is

```
u = 1-i, v = 1+i;
C(u,v) = (2,0).
```

Both input component magnitudes are at most one, but an output component is two. Input complex modulus is `sqrt(2)`, which is consistent with the complex-modulus row-sum bound. This distinction does not invalidate the binary precision charge `ceil(D/2)`.

For even `D`, tensor coefficients have one nonzero real or imaginary component of magnitude `2^(-D/2)`. For odd `D`, each has two components of magnitude `2^(-(D+1)/2)`. Thus the componentwise absolute row sum is `2^ceil(D/2)` directly. Unit phases and permutations preserve the componentwise bound as well.

## Completed-child denominator accounting

For arbitrary input Gaussian integers at one common binary denominator `2^p`, a completed `D`-axis coordinate tensor adds at most `ceil(D/2)` binary denominator bits, with the odd-depth residual parity structure described by the lattice lemma. Different incoming tags must first be aligned; arbitrary old/unfinished physical values cannot inherit a fresh-image parity promise.

The 29-class profile matches the pinned PR46 certificate and its source SHA-256. The accounting is

```
S = sum n_r r = 421548223824,
O = sum_{r odd} n_r = 1142904672,
charge(f) = sum n_r ceil(rf/2)
          = (S f + O (f mod 2))/2,
charge(f) <= 211345564248 f.
```

At `f=1`, the decrease from the old completed-child denominator charge is `210202659576`, or `49.864439629...%`. This is a reduction in that certified precision-accounting component. It is not a 49.86% reduction in total memory, the magnitude guard, physical runtime or multiplication complexity. The scalar `E` term and the all-intermediate guard remain unchanged. Lean proves finite-profile arithmetic and the every-`f` inequality. The final package also proves the recursive finite tensor's execution, precision grid and sharp impulse in `GaussianTensorExecution.lean`; this does not certify the whole physical framed network.

## Mixed-center fusion boundary

See `FRAME_REVIEW.md` for the coefficient proof and common-frame restrictions. The h28,d19 producer has `delta B_i=2G_i`, `delta D_i=T-G_i`, and `sum delta B_i-2sum delta D_i=-32T`. Combining center, complete disjoint and intersection-two terms before division recovers the source exactly with no extra fresh-scalar binary denominator.

The root verifier uses an actual regenerated DAG, independent exact 0/1/2 coefficient bitplanes, every source/target coefficient pair, dirty-value finite controls and off-image/frame-mismatch negatives. Generic-scatter and fused quotients count two explicit reference schedules; they do not establish optimality or tape-runtime gains. An exact quotient guard alone cannot characterize the entire producer image; a checked incoming image certificate or stronger image validation is needed before using the fast path as a public standalone API.

## Matching exploration boundary

No new carrier-matching candidate was tested. The required GCC/Clang `unsigned __int128` toolchain was not located; no WSL installation was available. An optimizer dependency was staged locally before this exploratory branch was stopped. The absence of a result is not evidence that PR44's floating first-order matching is globally optimal. Its pinned candidate remains independently certified only for the profile it produces.
