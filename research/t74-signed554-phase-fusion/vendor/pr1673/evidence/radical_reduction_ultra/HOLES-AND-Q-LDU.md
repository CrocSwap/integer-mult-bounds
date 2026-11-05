# Independent checks of Gaussian interpolation and holes completion

Status: exact algebraic identities and analytic bounds below; no complete new inverse implementation, and no final kappa claim. This continues the parent investigation after the first outer-reduction package.

## 1. Local scaled Vandermonde identity

Write `a=pi*alpha^2`, `rho=t/s`, `q_i=floor(rho*i+1/2)`, and `beta_j=rho*j-q_j`. On any nonwrapping index interval,

```
N_ij = exp[-a*(rho*j-q_i)^2 + a*beta_j^2]
     = exp[-a*q_i^2] * (exp[2a*rho*q_i])^j
       * exp[-a*rho^2*j^2+a*beta_j^2].
```

Translations of both index origins preserve a diagonally scaled Vandermonde representation. If the local span is L, centered nodes have logarithms O(aL), and the product-tree polynomials, Lagrange denominators, and outer diagonals have logarithmic height O(aL^2+L). Thus L=O(sqrt(p/a)) is compatible with Cp-bit working precision. Distinct nodes are explicitly separated, so the inverse of a *single supplied principal block* can be computed by multipoint interpolation with that precision and O(L p polylog p) bit cost.

This does not justify independent short blocks. The current inverse has strong directed coupling near the end of a phase cell. Its exact q-LDU below shows why a halo of width merely sqrt(p/a) can lose much more than 2^-p.

## 2. Exact Gaussian Toeplitz LDU in a no-gap phase cell

Within a cell `q_i=i+c`, put `theta=rho-1`,

```
q=exp(-a*rho), Q=q^2,
P_j=product_(k=1..j) (1-Q^k), P_0=1,
D_i=exp(a*theta*i^2-2a*c*i),
G_ij=q^((i-j)^2).
```

Then `N=diag(D_i)*G*diag(D_i)^-1`. With the Gaussian binomial

```
{i choose j}_Q = P_i/(P_j*P_(i-j)),
```

the exact lower factor and its inverse are

```
L_ij    = q^((i-j)^2) * {i choose j}_Q,          i>=j,
Linv_ij = (-q)^(i-j) * {i choose j}_Q,           i>=j,
G       = L * diag(P_j) * L^T.
```

These follow from the ordinary Newton factorization of the Vandermonde matrix at nodes Q^-i; eliminating its successive monic Newton polynomials gives the displayed Gaussian binomial factors and pivot P_j. The inverse follows from the finite q-binomial theorem, or multiplying the two triangular factors and grouping equal powers of Q. `check_q_ldu.py` verifies both identities exactly at 30 rational q/size choices (1,155 matrix entries), including diagonal conjugations.

Each triangular application is a diagonally scaled Toeplitz convolution:

```
L = diag(P_i) T_(q^(h^2)/P_h) diag(P_i)^-1,
Linv = diag(P_i) T_((-q)^h/P_h) diag(P_i)^-1.
```

The N factors add only the D_i conjugations. Their inverse lower entries have exponent

```
a*((2*beta_i-rho)*h - theta*h^2), h=i-j.
```

Since beta_i<=1/2,

```
abs((D Linv D^-1)_ij)
 <= C exp[-a*theta*h*(h+1)],
C = product_(k>=1)(1-Q^k)^-1.
```

The upper inverse obeys the same bound using beta_i>=-1/2. For a>=pi and rho>1, C<2 by a geometric bound on the logarithm of the infinite product. Hence both inverse triangular factors have row norm O(1+(a theta)^-1/2). The P_j diagonal is bounded between 1/C and 1. This avoids using cancellation of exponentially large factors to bound the *completed* inverse. Over one cell, the explicit D_i range costs O(a/theta) guard bits, so the retained condition alpha^2/theta=O(p) still suffices for a straightforward implementation.

This supplies a clean alternative to the retained Gohberg–Semencul interior solve. The latter already has linear convolution cost; a new exponent requires treating the gaps between cells or their boundary system.

## 3. Exact complementary hole positions

Let 1<rho=t/s<2, H=t-s, rho'=t/H, and select the distinct positions q_j for 0<=j<s in [0,t). The missing positions, in increasing order, satisfy exactly

```
h_l = ceil(rho'*(l+1/2)-1/2), 0<=l<H.
```

In particular `abs(h_l-rho'*(l+1/2))<=1/2`, including all half-integer ties. To prove this, the number of selected positions <=k is `ceil((k+1/2)*s/t)`, so the number of holes <=k is

```
k+1-ceil((k+1/2)*s/t)
 = floor((k+1/2)*H/t+1/2).
```

Invert this increasing count. `check_holes.py` checks every pair s,t in its stated finite range, retaining tie cases.

## 4. Exact holes-completion factorization

Let r>1, x_k=r^k, and V_t=(x_k^j)_(0<=k,j<t). Let P(X)=product_(k<t)(X-x_k), with coefficients p_j and p_t=1. Restrict V_t^-1 to the H missing-node columns and the H highest-degree rows, reversing those rows. This H-by-H matrix A factors as

```
A = T * V_holes^T * diag(1/P'(x_h)),
T_(j,k) = p_(t-(j-k)) for j>=k, and 0 otherwise,
(V_holes^T)_(j,h) = x_h^j.
```

The coefficient of X^(t-1-j) in P(X)/(X-x_h) equals
`sum_(k=0..j) p_(t-k) x_h^(j-k)`, by synthetic division from the leading end. Lagrange interpolation gives the identity.

Given values only on selected nodes, set the H missing values initially to zero and do one full interpolation. Solve A for the missing values that cancel the H degree-tail coefficients, then interpolate with the completed values. The resulting polynomial has degree<s and interpolates all supplied values. `check_holes.py` compares this construction with direct inversion of the s-by-s selected Vandermonde matrix at 70 exact rational instances.

There is an equivalent erasure-polynomial construction: E(X)=product_(h in holes)(X-x_h); interpolate E(x_i)*y_i at all t nodes, assigning zero at every hole, then divide the degree<t result by E. The quotient has degree<s and equals the desired source interpolant. This is an exact Reed–Solomon erasure identity; it does not by itself establish stable fast arithmetic in the original normalization.

## 5. The complementary Vandermonde is favorably conditioned after scaling

For the original Gaussian nodes use r=exp(2a rho). Put `a'=a*rho/rho'`, and shift the complementary row coordinates by rho'/2. Since `h_l=rho'*(l+1/2)+delta_l` with |delta_l|<=1/2, the scaled complementary matrix can be written

```
B_ij = exp[-a'*(rho'*j-(h_i-rho'/2))^2 + a'*delta_j^2].
```

Its diagonal is exactly one. Its Vandermonde nodes are those required by the exact completion, up to an allowed common node/column diagonal scaling, because `a' rho'=a rho`.

At |i-j|=k>=1,

```
abs(B_ij) <= exp[-a*rho*(rho'*k^2-k)].
```

Indeed the relevant distance is at least rho'k-1/2, and the subtractive delta_j^2 is at most 1/4. Thus off-diagonal row sums are bounded by a convergent geometric Gaussian tail, with first exponent a rho(rho'-1). For small theta, rho' is Theta(1/theta), so this exponent is Theta(a/theta). To obtain error 2^-p a direct truncated solve only needs complementary width

```
O(1+sqrt(p/(a*rho*rho'))) = O(1+sqrt(p theta/a)).
```

This rigorously confirms the conditioning and narrow-band part of the parent's holes-completion proposal. It is not a cost proof for the complete original inverse: the Toeplitz T and full geometric interpolation must first be implemented with their enormous diagonal scalings canceled symbolically.

## 6. A useful normalized erasure-coefficient bound

Let hole exponents h_0<...<h_(H-1) have successive gap >=g, let R=r^g>1, and e_k be the kth elementary symmetric polynomial in r^h. Let M_k be the product of the k largest nodes. Then

```
1 <= e_k/M_k <= product_(j>=1)(1-R^-j)^-1.
```

For any selected k-index subset, compare its indices with the k largest indices. Its nonnegative deficits form a partition, and its product divided by M_k is at most R to the negative partition size. Summing over partitions proves the bound. The contribution from deficit >=m is at most

```
R^(-m/2) * product_(j>=1)(1-R^(-j/2))^-1.
```

For R>=4 the latter product is below 4, so retaining deficit less than `m >= (2p+4)/log2 R` suffices for relative error below 2^-p. Thus normalized coefficients have bounded height even when unnormalized coefficients contain Theta(a theta t^2) exponent bits. Only O(p theta/a) partition energy near the subset boundary is relevant.

Likewise, for a nonhole i, pull `product_h max(r^i,r^h)` out of |E(r^i)|. The residual is `product_h(1-r^-|i-h|)`, which lies between `product_(k>=1)(1-r^-k)^2` and 1. It is uniformly bounded away from zero for fixed r>1. These are positive products and sums; the bounds do not depend on fortuitous numerical cancellation.

The unresolved algorithmic question is performing the needed polynomial multiplication/division while storing these *degree-dependent* scales, rather than one common scale. Feeding the raw coefficients to an ordinary FFT requires Theta(a theta t^2) bits; declaring that cost absent is invalid. The positive partition estimates give a concrete starting point for a banded or locally normalized implementation.

## 7. Correct boundary of the result

- Exact q-LDU, exact hole indexing, exact completion, complementary conditioning, and the normalized erasure bounds above are established algebraically.
- `Q-LDU-CONTROLS.json` and `HOLES-CONTROLS.json` contain finite independent checks.
- No stable all-size global holes solver is implemented here. Its fully paid precision/tape cost remains open.
- No final multiplication exponent follows from these identities alone.

## 8. Weighted full-geometric interpolation: a stable local implementation

This is a further positive lemma for one component of holes completion. It does **not** complete the Toeplitz/complement adapters.

Let beta=H/t=theta/rho, let h_l be the actual holes above, and let h*_l=(l+1/2)/beta be the ideal equally spaced holes. For x in [0,t], define

```
R(x) = 2a*rho * sum_l (x-h_l)_+ - a*theta*x^2.
```

This is the logarithm of the dominant erasure evaluation after canceling the full-geometric Gaussian input diagonal, up to a constant independent of x. That constant can be kept symbolically and canceled at the final adapter.

For ideal holes, put m=floor(beta*x+1/2). Then

```
sum_l (x-h*_l)_+ = m*x - m^2/(2beta),
R*(x) = -(a*rho/beta)*(m-beta*x)^2,
-a*rho/(4beta) <= R*(x) <= 0.
```

Since |h_l-h*_l|<=1/2, compare increments on [x,x+v]. Holes below both endpoints give the same increment v under both locations, and holes above both give zero. Only O(beta*v+1) holes whose ideal or actual locations meet the interval can contribute; each contributes an error at most 1/2. Consequently, for 0<=x<=x+v<=t,

```
|[R-R*](x+v)-[R-R*](x)| <= a*theta*v + O(a*rho),
|R(x+v)-R(x)| <= a*theta*v + K,
K <= 4a/theta                 (0<theta<=1/2).
```

The constant K is deliberately loose. This bound allows the absolute values R(x) to have a very large drift; no e^R(x) is represented as an unscaled ordinary fixed-point number.

The inverse lower Gaussian factor has coefficient
`(-q)^v * P_i/(P_(i-v)*P_v)`, with q=exp(-a*rho) and all Pochhammer ratios bounded by a fixed constant. Conjugating by the symbolic R gauge gives

```
abs(weighted coefficient at distance v)
 <= C exp[-a*rho*v + a*theta*v + K]
 =  C exp[-a*v + K].
```

The same estimate holds for the upper factor because the increment bound is two-sided. Hence, for a desired p-bit error after both factors, it suffices to truncate each factor at

```
L = O(p/a + 1/theta).
```

Account for the first factor's `exp(O(K))` norm in the second factor's error; this only changes the constant in L. Under the retained `a/theta=O(p)` condition, each factor's norm is `exp(O(p))`, its discarded tail is below `2^-Cp`, and each local interval of length O(L) has R-range O(p). To see the last statement directly, the count discrepancy `|#{h_l<x}-beta*x|` is O(1), so R has Lipschitz constant O(a) away from its harmless derivative jumps, and `aL=O(p+a/theta)=O(p)`.

Use overlapping intervals of core length L with an L-record halo, recenter R at the first index in each interval, and apply the two triangular Toeplitz kernels by ordinary local convolution. Both input and output diagonal ratios have O(p) logarithmic range on the interval. Pochhammer products are in a fixed interval away from zero; their approximations can be precomputed to Cp bits. Every local product is on O(Lp) bits and costs O(Lp log(Lp)); all factor errors and tail errors use Cp working precision. Total one-axis cost is

```
O(t*p*polylog(p)),
```

because L is polynomial in p under the retained family. Factor pages and local exponent differences can be read sequentially. The number of tapes remains fixed, with the same overlap-buffer construction as the already reviewed microbox algorithm. This removes raw `a*t^2` precision from the weighted *full-geometric interpolation* component. It is an actual localization proof, not a declaration that enormous factors cancel numerically.

What remains to finish the original inverse is to track the exact gauges through the H-dimensional tail Toeplitz solve and complementary interpolation (or equivalently through erasure multiplication/division), and prove the resulting adapters have the same local p-bit implementation. The fact that the full-geometric component is stable does not imply this automatically.
