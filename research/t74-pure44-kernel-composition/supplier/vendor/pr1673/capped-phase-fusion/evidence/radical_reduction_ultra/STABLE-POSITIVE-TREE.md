# Positive interpolation trees and two global inverse tails

Status: exact algebra and an error bound for a compressed inverse representation. This note does not yet claim that the local tree operators admit the pure convolution factorization required for tensor fusion.

## 1. Setup and signs

Let `x_i=r^{q_i}`, `r=exp(2 a rho)>1`, and `q_i=floor(rho i+1/2)` for `0<=i<s`. Put

```
beta_i=rho i-q_i,
d_i=exp(-a rho^2 i^2+a beta_i^2),
P(X)=product_i(X-x_i),
w_i=exp(a q_i^2) y_i/P'(x_i).
```

The finite unwrapped Gaussian matrix is

```
N0_ij=exp[-a(rho j-q_i)^2+a beta_j^2]
     =exp(-a q_i^2) x_i^j d_j.
```

The exact output of its inverse is

```
(N0^-1 y)_j = (-1)^k / d_j * [z^k] R(z), k=s-1-j,
R(z)=sum_i w_i product_(l!=i)(1+x_l z).
```

The only signs in a basis polynomial are the global row sign `(-1)^k`; the factors `1+x_l z` have positive coefficients. The input-dependent signs reside in the scalar leaves `w_i`. The absolute Lagrange sum is exactly the infinity-norm majorant of `N0^-1`, rather than an unrelated upper bound that may hide cancellation. The nearest-neighbor proof in NEAREST-NEIGHBOR-NORM.md also applies to N0: delete the wrap entries of L and U, use their finite nilpotent inverses, and retain the same product and remainder estimates. Thus the same polynomial-in-1/theta bound is available.

## 2. An exact bounded gauge for every interpolation-tree intermediate

Take a contiguous interval of node indices `I=[l,u]`. Define

```
F_I(z)=product_(i in I)(1+x_i z),
R_I(z)=sum_(i in I) w_i product_(j in I, j!=i)(1+x_j z),
c_I=s-1-u,
M_I=product_(j>u) x_j,
W_I(k)=d_(u-k)/M_I, 0<=k<|I|.
```

The equality `u-k=s-1-(k+c_I)` is the connection to the final reversed degree.

Suppose `||y||_infinity<=1` and `||N0^-1||_infinity<=B`. Replace all leaves by their absolute values and call the resulting polynomial `R_I^+`. Completing the interval by the single outside monomial that chooses every node above I and no node below I gives

```
M_I * [z^k] R_I^+ <= [z^(k+c_I)] R_all^+ <= B d_(u-k).
```

Consequently

```
|[z^k] R_I| <= [z^k] R_I^+ <= B W_I(k).
```

This holds for every node of any contiguous binary interpolation tree, for arbitrary signed inputs. It does not require roots to remain correlated after rounding. In particular, it avoids the independently-rounded-erasure-quotient failure in ERASURE-ROUNDING-CONTROL.json.

The merge identity is

```
R_(A union B)=F_B R_A + F_A R_B,
```

where A is the lower child and B the upper child. All fixed polynomial coefficients in this identity are positive. Each intermediate contribution, after multiplication by the chosen outside monomial, is a sub-sum of the final absolute Lagrange sum. Therefore bounded intermediate amplitude follows from the completed inverse bound, including in the presence of cancellation between input leaves.

This is a height bound, not by itself a fast multiplication theorem. The gauges are degree dependent. Ordinary convolution of their unscaled coefficients can still require excessive precision.

## 3. Partition bound for arbitrary selected nodes

For any increasing nodes satisfying `x_(i+1)/x_i>=r`, let `e_k` be the kth elementary symmetric polynomial, and `M_k` the product of the k largest nodes. Comparing a selected k-subset to the k largest indices gives a partition of nonnegative index deficits. Hence

```
1 <= e_k/M_k <= C_r,
C_r=product_(h>=1)(1-r^-h)^-1.
```

For `r>=4`, `C_r<2`. This applies to every interval and to intervals with a node deleted. It controls the normalized fixed polynomial factors used by the tree.

## 4. Two globally compatible far fields

Write `E_k=e_k(x_0,...,x_(s-1))`, with E_0=1. Let `k=s-1-j`.

If `i<=j-m`, then

```
0 <= 1-e_k(X without x_i)/E_k
   = x_i e_(k-1)(X without x_i)/E_k
   <= C_r x_i/x_(j+1)
   <= C_r r^(-m-1).
```

The endpoint k=0 is exact and is read separately. If `i>=j+m`, then

```
e_k(X without x_i)
 = E_(k+1)/x_i - e_(k+1)(X without x_i)/x_i,
```

and the second term relative to `E_(k+1)/x_i` is at most

```
C_r x_(j-1)/x_i <= C_r r^(-m-1).
```

The endpoint j=0 is again exact. Thus, after allowing a harmless factor `1/(1-C_r r^(-m-1))` to convert the relative approximation to a bound by the true positive entry, the two far fields are

```
(N0^-1 y)_j ~= (-1)^k [
  E_k/d_j       * sum_(i<=j-m) w_i
 +E_(k+1)/d_j   * sum_(i>=j+m) w_i/x_i
 + exact local strip |i-j|<m
].
```

Every high-level tree rank-one tail is a restriction of one of these two global expressions. Their contributions can be accumulated by one prefix sum and one suffix sum; no log(s) separate array updates are necessary.

The entrywise relative error is at most `2 C_r r^(-m-1)` for a sufficiently large m. Therefore the infinity-norm error is at most

```
2 C_r B r^(-m-1).
```

Choosing

```
m >= (p log 2 + log(4 C_r B))/(log r)
```

makes the far-field approximation error at most `2^(-p-1)`. In the retained regime, `log B=O(log d)` and `log r=Theta(a)`, so `m=O(p/a+1)`.

## 5. What must still be paid

The construction reduces the data application problem to two globally compatible weighted running sums and a width-O(p/a) local strip. All coefficients, barycentric weights, and normalized tree factors may be precomputed: the source axis length is exp(O(p/d)), and any fixed polynomial power of it remains negligible compared with the full tensor volume.

For a single axis, bounded positive interpolation trees are a plausible route to the local strip in `O(s p polylog p)` bit operations. To turn this into an exponent improvement, however, one must give a fixed sequence of convolution, diagonal, and permitted data-movement operations that can be fused over many axes. A merge written as a *sum* of two convolutions is not sufficient: tensoring it naively generates exponentially many branches. Neither the positive height bound nor the two-tail representation silently resolves that issue.

## 6. A branch-free reduction of a normalized Sylvester merge

This is an exact algebraic reduction, with a bounded-symbol condition. It reduces the remaining in-place question to one full Toeplitz map rather than a sum of two polynomial products.

Take two children of size b. Choose an anchor zeta strictly between their node sets and rescale the variable. After swapping/scaling the child registers the merge has the form

```
S(B,A)=f(z) B(z)+z^b g(z^-1) A(z),
f(z)=product_(lower nodes x)(1+(x/zeta) z),
g(z^-1)=product_(upper nodes x)(1+(zeta/x) z^-1).
```

If zeta is the geometric mean of the largest lower node and smallest upper node, every displayed root parameter is at most `r^-1/2`. The sum of all parameters on either side is at most

```
eta = r^-1/2/(1-r^-1).
```

Thus the l1 norms of f and g are at most exp(eta), and the l1 norms of their reciprocal series are at most exp(eta/(1-r^-1/2)). All are constant and approach one as a increases.

Let T_f be the 2b-by-2b lower triangular Toeplitz multiplication matrix for f. Put

```
h(z)=g(z^-1)/f(z),
K_ij=h_(i-b-j),
H_ij=h_(i-j),                    0<=i,j<b.
```

All coefficients needed here are finite coefficients of a rational Laurent series, so they can be precomputed exactly or to the required precision. Formal division modulo z^(2b) gives

```
T_f^-1 S = [ I K ; 0 H ].
```

Consequently S is implemented, without expanding the 2b data registers, by:

1. the dirty Toeplitz shear `B <- B+K A`;
2. the full Toeplitz map `A <- H A`;
3. the triangular Toeplitz map `whole <- T_f whole`.

Moreover

```
||H-I||_infinity <= ||g/f-1||_1 = O(r^-1/2).
```

For sufficiently large fixed r, H and H^-1 have uniformly bounded norms. This isolates the unresolved circuit primitive: a stable, length-preserving, polylogarithmic-depth application of a precomputed well-conditioned full Toeplitz matrix H. A dirty shear involving H is not by itself the same primitive, and a work-efficient sequential recursion is not automatically a shallow tensor-fusible circuit.

The anchor normalization concerns this algebraic merge. Across a large original Gaussian interval, translating to this common anchor may itself have quadratic exponent range. The positive intermediate gauges in Section 2 must still be reconciled with local Toeplitz windows; one cannot drop that precision cost.
