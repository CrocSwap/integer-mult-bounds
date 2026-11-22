# A complete upper-inverse data algorithm with linear precision overhead

Status: the construction below closes the one-dimensional **data application** of the nonperiodic upper inverse in `O(s p polylog p)` bit operations, after fixed per-axis coefficient preprocessing, using `C p` internal precision for an absolute constant C. It does not obtain logarithmic internal guard bits and does not prove tensor fusion. The lower-factor algorithm in LOWER-FACTOR.md does have logarithmic guard overhead.

Let `p` be the required output precision, `a>=1`, `theta>=p^-O(1)`, and `a=O(p)`. In the target family a is fixed or logarithmic and every line length s grows faster than any fixed power of p. Preprocessing depending on the axis is shared by all its lines, as allowed by the parent reduction; it is not charged anew for every line. The coefficient words actually read by one data application have total `O(s p polylog p)` bits.

## 1. Upper inverse is a stable suffix scan plus bandwidth O(p/a)

Use the column diagonal `e_i=exp(-a rho^2 i^2+a beta_i^2)`. Define

`B_j=e_j prod_(0<=k<j)x_k`

`   =exp(-a rho^2 j+a beta_j^2-2a rho sum_(0<=k<j)beta_k)`.

For `j>=i`, write

`C_i,j=e_(j-i)(x_0,...,x_(j-1))/prod_(i<=k<j)x_k`.

Then

`(U^-1)_ij=(-1)^(j-i)(B_j/B_i) C_i,j`.

The elementary-symmetric recurrence proves

`C_i,j+1-C_i,j=e_(j-i+1)(x_0,...,x_(j-1))/prod_(i<=k<=j)x_k`.

This is nonnegative and, by the partition bound, at most `c^-1 x_(i-1)/x_j <= c^-1 r^(-(j-i+1))`; at i=0 the difference is zero. Therefore C_i,j increases to a limit C_i,infinity in `[1,c^-1]`, and

`0<=C_i,infinity-C_i,j<=c^-1 r^(-(j-i+1))/(1-r^-1)`.

The primary ratio has the uniform bound

`|B_j/B_i|<=exp(a/4-a rho theta(j-i))`.

Consequently replace C_i,j by C_i,infinity globally, using one backward weighted scan, and retain the correction only for `j-i<W`, where

`W=O((p+a+log(1/theta))/a+1)`.

The discarded correction has row norm below `2^-p`. The scan is stable on arbitrary signed input, using exactly the same polynomial row-sum argument as the lower prefix scan. Coefficients C_i,infinity can be precomputed without raw B_i values; only adjacent B ratios are used at run time.

Use W-record pages. Compute the correction on every diagonal page and immediately adjacent upper page; omit it elsewhere. Subtracting the scan contribution on retained blocks avoids double counting. Recursive ordered cross tiles inside one page have depth O(log W), and the exact diagonal entries are 1.

## 2. A cross tile factors through bounded small-root prefix polynomials

Take row indices `I=[l,m)` and column indices `J=[m,r0)`. Define

`alpha_d=e_d(x_0/x_m,...,x_(m-1)/x_m)`,

`beta_j,h=e_h(x_m/x_m,...,x_m/x_(j-1))`,

with beta_m,0=1 and beta_m,h=0 for h>0. Put `d=m-i`,

`gamma_i=(U^-1)_i,m`,

`tau_j=(-1)^(j-m)(B_j/B_m)`.

An exact Laurent-polynomial coefficient identity gives

`(U^-1)_ij=gamma_i tau_j sum_(h>=0) (alpha_(d+h)/alpha_d) beta_j,h`.

The signs are already in gamma and tau; the remaining coefficient sum is nonnegative. Both gamma and tau are polynomially bounded, with the same exponential-distance primary bounds as before.

To verify the identity, write X=x_m Z and factor

`P_j(X)=X^m prod_(k<m)(1-x_k/X)`

`        *(-1)^(j-m) prod_(m<=k<j)x_k prod_(m<=k<j)(1-X/x_k)`.

Extract coefficient i=m-d. Every term has common sign (-1)^(j-i), and division by the h=0 term gives the formula.

For a weighted input define

`M_h=sum_(j in J) tau_j u_j beta_j,h`.

The polynomial whose coefficients are M_h is a weighted sum of prefix products

`sum_(j in J) tau_j u_j prod_(m<=k<j)(1+(x_m/x_k) Z)`.

Its root parameters are 1, then at most r^-1,r^-2,..., so the coefficient l1 norm of every product is at most

`2 prod_(k>=1)(1+r^-k) <= 2/c`.

A truncated product/sum tree computes M_0,...,M_R in `O((|J|+R) polylog p)` scalar operations. At a split, its exact rule is `S=S_left+P_left S_right`, with P a fixed product. Intermediate norms are bounded by a constant times the absolute weighted input sum, independently of tile length. No large Gaussian diagonal occurs in this step.

## 3. Exponentially small high degrees

The partition bound on alpha and beta gives

`alpha_(d+h)/alpha_d <= c^-1 r^(-d*h-h(h+1)/2)`,

`beta_j,h <= c^-1 r^(-h(h-1)/2)`.

Thus the h-term, after summing input weights, is bounded by

`c^-2 r^(-d*h-h^2) sum_j |tau_j u_j|`.

Group row distances dyadically: D<=d<2D. For that group retain only

`R=min(|J|, O(sqrt(P)), O(P/D))`, `P=(p+a+log(1/theta))/a`,

with sufficiently large absolute constants. If |J| is smaller, the polynomial is already exact. Otherwise all omitted terms sum to less than `2^-p` after allowing the polynomial gamma/tau factors. There are O(log p) row groups.

## 4. Fast normalized Hankel application, with Cp internal bits

The remaining map for a row group is

`y_d=sum_(0<=h<=R) (alpha_(d+h)/alpha_d) M_h`.

Split the d-range into consecutive blocks of length at most R (or the whole group if shorter). For a block beginning at d0, divide all alpha coefficients used by alpha_d0. Then the numerator is one reversed ordinary convolution of that coefficient segment with M. Divide output d by alpha_d/alpha_d0.

The decisive height bound is local, not global. If k>=0, comparing dominant products and using q-gaps in {1,2} gives

`c r^(-2*d0*k-k(k+1)) <= alpha_(d0+k)/alpha_d0 <= c^-1`.

Here the lower bound is needed only when the coefficient exists; every queried alpha index is <=m. If alpha vanishes because its degree exceeds m, store exact zero and never divide by it. Since d0=O(D), k=O(R), and `D R+R^2=O(P)`, every nonzero coefficient ratio and every divisor in this block lies between `exp(-O(aP))` and an absolute constant. Thus **Cp internal precision** suffices for these convolutions and the final divisions.

The number of scalar operations for one row group is `O(D polylog p)`; its separate bounded-prefix computation costs `O((|J|+R) polylog p)`. Summing the O(log p) row groups gives `O((|I|+|J|) polylog p)` scalar operations per ordered tile. Recursing through one W-page or processing adjacent pages therefore costs `O(W p polylog p)` bits. Over all pages the data cost is

`O(s p polylog p)`.

The Gaussian factors gamma and tau can be evaluated from bounded dominant-product ratios rather than raw e_i or B_i. Precomputed alpha tables can similarly be stored with dominant-product gauges. Every alpha segment actually read by the data algorithm has length O(|I|+|J|) per row-group and tile level; this accounts for the coefficient tape scans in the same bound.

A conservative preprocessing implementation may compute every required alpha table from O(poly(p)) nearby nodes separately, and can therefore cost `s poly(p)` per axis. This is a one-time axis cost, not an unpriced per-line cost. In the parent regime it is negligible compared with the full tensor data volume. A uniformly quasi-linear preprocessing theorem is not asserted here.

## 5. Complete nonperiodic and periodic application

Combining this upper map with the lower map and the bounded diagonal gives the complete nonperiodic inverse `G^-1=U^-1 C^-1 L^-1` in `O(s p polylog p)` data time, at Cp internal precision, with polynomial operator norms. Requested final error is achieved by a fixed additional factor in precision plus O(log p+log(1/theta)) endpoint guard bits.

For the periodic matrix one may either implement the bilateral factors in BILATERAL-LDU.md or use a finite boundary correction. The latter needs only two nonperiodic inverse data applications:

- Truncate nonzero Gaussian aliases to the two corner blocks of width `b=O(sqrt((p+log(1/theta))/a)+1)`, obtaining `K=G+UV` and a row-norm tail smaller than `2^-Cp`.
- U inserts O(b) boundary coordinates and V reads a bounded O(b)-by-O(b) corner matrix.
- Precompute `S^-1`, `S=I+V G^-1 U`. Its norm is polynomial because `S^-1=I-V K^-1 U` and the periodic inverse norm plus the tiny discarded tail bounds K inverse.
- Apply `x=G^-1 z`, `w=S^-1 Vx`, and return `x-G^-1 Uw`.

The boundary data work is polynomial in p. For the target line lengths s growing faster than every fixed polynomial in p, it is negligible relative to sp. The updated matrix in the Woodbury inverse identity is K, not the base G. The periodic Gaussian tail and final correction error are bounded using the fixed-a theorem in BILATERAL-LDU.md.

## What is still not established

The normalized Hankel step uses Cp working precision because its local alpha divisors may be exp(-Cp). It has not been converted to a circuit whose every intermediate operator has polynomial norm. Therefore this result does not meet the stronger **logarithmic guard at every internal stage** requirement needed by the proposed full-dimensional fusion. It supplies a complete one-dimensional data algorithm and a precise remaining normalization target; it supplies no improved final kappa.

## 6. Direct periodic implementation from the bilateral factors

The bilateral theorem also permits the Woodbury step above to be omitted. This is cleaner in the target regime `s>>W`.

For the bilateral lower inverse, use

`C_i=prod_(k<i)(1-x_k/x_i)`, `D_i^+=prod_(k>i)(1-x_i/x_k)`.

The same lower formula and scan/correction split hold, with the defining products now bilateral. The adjacent A ratio is still given by the beta formula in LOWER-FACTOR.md. For the upper inverse, use elementary polynomials in the infinite prefix `x_k, k<j`. Their normalized coefficient C_i,j satisfies exactly the same monotone recurrence and geometric tail estimate in section 1. Its limit C_i,infinity is periodic in i.

All adjacent scan multipliers are s-periodic. For a lower forward scan the modulus of their product in one full period is at most

`exp(-a rho theta s)=exp(-a rho(t-s))<=exp(-a)`.

The upper backward scan has the same bound. To solve a cyclic first-order recurrence, make one affine pass with the boundary value temporarily zero, recording the resulting offset Q and the full multiplier P. The true boundary value is `Q/(1-P)`; a second pass produces the output. Since `|P|<=exp(-a)`, the division has a uniform denominator gap `|1-P|>=1-exp(-a)`. Intermediate partial products and scan norms have the polynomial bounds already proved. This supplies a stable two-pass scan on the original s records.

Retain the correction only for one-sided distances below W on the integer cover of the circle. With `s>>W`, each retained coefficient belongs to its diagonal page or the single adjacent cyclic page; virtual negative or beyond-s indices are generated by periodic q/beta formulas. The same local tile algorithms apply. Periodization cannot increase the row norm of any discarded tail, so all the previous error estimates remain valid.

In the upper tile algorithm, alpha_d is now the coefficient of the infinite small-root prefix

`prod_(k<m)(1+(x_k/x_m)Z)`.

The partition and alpha-ratio bounds in sections 2–4 continue to hold. To precompute a requested alpha_d to relative error `2^-q`, it is sufficient to retain the K nearest prefix nodes, with `K>=d+O(q/a+1)`: a contribution involving an omitted node has partition deficit at least K-d, and summing the corresponding partition tail gives `O(r^(-(K-d)/2))` relative error (bound the tail by r to half the negative deficit times the convergent partition generating product). For the O(W)-degree tables at q=Cp, this is O(W+p/a) nodes, independent of s. Normalized table storage and data access are unchanged.

Thus, after fixed per-axis coefficient preprocessing, the bilateral factorization itself gives the **periodic** inverse data application in `O(s p polylog p)` time with Cp working precision, in the target regime `s>>poly(p)`. It needs neither a large raw Vandermonde nor a boundary Schur system. The unresolved logarithmic-internal-guard and tensor-fusion qualifications remain exactly as stated above.
