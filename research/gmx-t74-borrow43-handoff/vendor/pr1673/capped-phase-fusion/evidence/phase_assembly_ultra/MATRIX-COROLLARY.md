# Additional corollary using the supplied matrix-exponent theorem

Status: **PASS_CONDITIONAL_MATRIX_PHASE_FUSION_REVIEW**. The independent matrix-transfer and new-parameter layout audits passed, followed by the integrated root review and exact ledger replay. The first, Strassen-based result `kappa=0.001672922349588871` remains separately reviewed and unchanged. Neither result changes the upstream selected certificate.

This corollary has an **additional hypothesis**: the supplied *Matrix Multiplication in Nine Fourths* theorem gives `omega_C<=9/4`. Its complete-source audit is `PROOF-AND-COVERAGE.md`; the effective approximate-bit transfer is `ALGEBRAIC-STABILITY-INDEPENDENT.md`. The result here retains every supplier and all-size assumption of the first phase-fusion theorem.

## Effective matrix operation with the required error interface

Fix `tau=19/8>9/4`. The matrix exponent theorem supplies a fixed block dimension m and rank r with `r<m^tau`. The rank equations have integer coefficients, so their complex solution can be replaced by an algebraic-complex solution. Enumerating finite algebraic tuples and testing the rank equations exactly gives a halting search for one such fixed formula. Its cost is independent of the growing input.

Approximate its finitely many coefficients once by root isolation and precision-doubling Newton iteration. Recursive block multiplication has `O(W^tau)` operations. Its error recurrence is `E_j<=K E_(j-1)+K m^(j-1)` for a fixed K, hence `E_j=W^O(1)`. For input magnitudes at most `2^h`, fractional precision `P+2h+O(log W)` gives absolute output error at most `2^-P`. All intermediate magnitudes have logarithmic size `O(h+log W)`. Therefore a W-square product costs

`O(W^tau M(P+h+log W))`.

Here P,h=O(p), so the old boundary interface still has O(p)-bit records. Any residual logarithmic tape overhead is absorbed by choosing the fixed rank exponent strictly below tau. The finite matrix-base padding is a fixed constant factor for the current square product and is removed at that product's completion; it is not simultaneous tensor-axis padding.

The already reviewed boundary method multiplies W-by-W blocks for W right-hand sides. Since V is **bit volume**, its normalized total cost is

`O(V (d/B) W^(tau-1) [M(p)/p] polylog p)`.

The unconditional short multiplier has `M(p)/p=polylog p`; the new power is consequently `epsilon-xi+(tau-1)/2`. The Gaussian matrices, factor pages, sparse sets, completed norms and local residual argument are unchanged. Only the implementation of one bounded-size matrix product is replaced.

## New parameter balance

Retain the same q, effective bit saving, r0 and zeta as the first result. Put `s_union=10^-5` and

```
xi=(3/2+q-(1+q)*(r0+zeta)+s_union)/(2+q),
epsilon=(1+q*(1-xi-r0-zeta))/(1+q),
beta=1-xi-r0-zeta.
```

Then the main and grouped Gaussian savings coincide, while the basic sparse-union saving is larger by exactly s_union:

```
epsilon*q = 1-epsilon+q*beta,
1-epsilon-beta-1/2+xi = epsilon*q+s_union.
```

The chosen exact rational is

`kappa=0.001673360105405778`.

Its parameters are approximately

```
epsilon = .998745145709950482
xi      = .750213747912678130
beta    = .249785242087321870.
```

The exact minimum saving is

`.001673360115405778453817047951720376...`,

more than 10^-11 above kappa. Boundary algebra has saving

`5/16+xi-epsilon=.063968602202727648...`,

so it is no longer a binding row. The net improvement over the upstream selected saving is `6.9990832886e-7`, and over the first reviewed Strassen transfer it is `4.37755816907e-7`.

## Why the larger group remains legal

The cap is above the bandwidth and below the physical phase-cell scale: `1/2<xi<epsilon`. Its gauge still satisfies `beta+xi+r0=1-zeta`, so `g*a*B=o(p)`. The original one-axis width only has to fit one K-bit neighborhood; no proof requires the whole g-control reservoir to fit one axis. Total support/control size is `O(g polylog p)=o(p)`.

The membership exponent is `beta+2(1-epsilon)=.2522949506...<1`. The active group key has exponent `beta+1-epsilon<1`. The sparse-union fraction still tends to zero because `xi-beta-1/2=.0004285058...>0`. All local coefficient pages remain polynomial in p, while `L^g` remains superpolynomial. Microedge correction has exponent `epsilon+beta-3<-1.75`, including the generous old scalar arithmetic bound. Sparse microhalo key passes remain explicitly paid inside that negligible budget.

All forward q-image group embeddings occur in native axis-major order before the one global low-bit gather. All compression q-image extractions occur after the inverse global gather. The entire Gaussian calculation keeps full dyadic target coordinate ranges, so every globally invoked H stage has complete coarse labels. This schedule needs no per-group gathering of the whole long-axis fields; the q-image scans have the already-paid Vd/g cost.

The **optional full-group-key sort surcharge on the sparse union is omitted** because it is absent from the actual algorithm. The reviewed union routine extracts the complete rectangle `U_i=E_i x [L]^(g-1)`, transposes only its one polynomial-size field, computes its axis operator, and merges it into U in the original order. It does not radix-sort U. Reintroducing that sort is a rejecting control in the new ledger; it would destroy this parameter choice. This omission relies on the existing positive layout proof, not on the matrix theorem.

`check_matrix_corollary.py` verifies 47 exact positive slacks and six rejecting controls and writes `MATRIX-COROLLARY-ARITHMETIC.json`. The rejected variants are endpoint equality, zero group guard, zero union slack, the old Vd row, the old full-cell data gauge, and adding a full-key sort to U. The first theorem's records are not overwritten.
