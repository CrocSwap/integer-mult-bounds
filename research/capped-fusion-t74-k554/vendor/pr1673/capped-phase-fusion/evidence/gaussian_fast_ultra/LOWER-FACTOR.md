# A fast, stable application of the general Newton lower factor

Status: a proved one-dimensional **nonperiodic lower-factor** algorithm and exact controls. It does not by itself implement the entire periodic inverse. The upper factor has a polynomial norm bound but its fast normalization/fusion remains to be supplied. No final multiplication exponent is claimed.

## 1. Exact Gaussian LDU

Let `rho=1+theta`, `q_i=floor(rho*i+1/2)`, `beta_i=rho*i-q_i`, `x_i=r^q_i`, `r=exp(2a rho)>1`, and `d_i=exp(-a q_i^2)`, for `0<=i<s`. This section concerns the nonperiodic matrix

`G_ij=exp(-a[(rho*j-q_i)^2-beta_j^2])`.

Write `P_i(X)=prod_(k<i)(X-x_k)`, `C_i=prod_(k<i)(1-x_k/x_i)` (empty products are 1), and

`T_ij=P_j(x_i)/P_j(x_j)` for `i>=j`, zero otherwise.

The ordinary monic Newton expansion of `X^j` gives exactly

`G=L diag(C_i) U`,

where `L=diag(d_i) T diag(d_i)^-1`, `L_ii=U_ii=1`, and

`(U^-1)_ij=(-1)^(j-i) (e_j/e_i) e_(j-i)(x_0,...,x_(j-1))`,

`e_j=exp(-a rho^2 j^2+a beta_j^2)`.

The pivot calculation is exact:

`d_i P_i(x_i) e_i = C_i`.

Define

`A_i=d_i x_i^i C_i/prod_(k<=i)x_k`

`   =C_i exp(-a beta_i^2-a rho^2 i+2a rho sum_(k<=i) beta_k)`.

Divided differences give the exact inverse lower entries

`(L^-1)_ij=(-1)^(i-j) (A_i/A_j)/D_(i,j)`,

`D_(i,j)=prod_(j<k<=i)(1-x_j/x_k)`.

All assertions in this section hold for arbitrary increasing positive `x_i` and arbitrary nonzero `d_i`, except the Gaussian pivot identity and displayed exponential specialization of `A_i`.

## 2. Uniform factor norms

Put `c=prod_(m>=1)(1-r^-m)`. Because `q_(i+1)-q_i>=1`,

`c<=C_i,D_(i,j)<=1`.

For `i>=j`, direct summation gives

`log |A_i/A_j| <= -log c+a/4-a rho theta(i-j)`.

Consequently

`||L^-1||_infinity <= c^-2 exp(a/4)/(1-exp(-a rho theta))`.

For the upper factor, compare every elementary-symmetric term with the product of the largest `j-i` variables. The sorted deficits form a partition, hence

`1<= e_(j-i)(x_0,...,x_(j-1))/prod_(i<=k<j)x_k <= c^-1`.

The dominant exponential is

`(e_j/e_i) prod_(i<=k<j)x_k`

` =exp(-a rho^2(j-i)+a(beta_j^2-beta_i^2)-2a rho sum_(i<=k<j)beta_k)`.

Using `beta_k>=-1/2` gives

`||U^-1||_infinity <= c^-1 exp(a/4)/(1-exp(-a rho theta))`.

Also `||diag(C_i)^-1||<=c^-1`. For `a>=1`, `r>=e^2`, so `c` has an absolute positive lower bound. For `a=O(log(1/theta))`, both factor norms are polynomial in `theta^-1`. These bounds apply to **arbitrary signed/complex input vectors**, not only correlated outputs of another factor.

## 3. One stable scan plus a local correction

Let

`D_j^+=prod_(j<k<s)(1-x_j/x_k)`,

`H_i(x_j)=prod_(i<k<s)(1-x_j/x_k)`.

Then

`(L^-1)_ij=(-1)^(i-j) A_i/(A_j D_j^+) H_i(x_j)`.

Replace `H_i` by 1. This resulting triangular map is applied by

`y_i=-(A_i/A_(i-1)) y_(i-1)+u_i/D_i^+`,

starting from zero, with the evident `i=0` convention. Ratios are evaluated directly from the adjacent beta values and `C_i/C_(i-1)`, never from raw enormous `A_i` values. Products of recurrence multipliers obey the norm estimate in section 2, so accumulated roundoff has the same polynomial bound. No factor proportional to `s` is needed in the precision.

For `h=i-j>=0`,

`0<=1-H_i(x_j)<=sum_(k>i)x_j/x_k <= r^(-h-1)/(1-r^-1)`.

The sum of discarded correction entries for `h>=W` is therefore at most

`c^-2 exp(a/4) r^(-W-1)/[(1-r^-1)(1-exp(-a rho theta)/r)]`.

Thus `W=O((p+a+log(1/theta))/a+1)` makes the omitted correction less than `2^-p` in operator norm. At `a=O(log(1/theta))`, `theta>=p^-O(1)`, this is `O(p/a+1)`.

Partition the line into pages of W indices. Compute the exact correction on each diagonal page and each immediately lower adjacent page, and omit it elsewhere. Every omitted entry has `h>=W`; every retained tile has O(W) rows/columns. A diagonal page is recursively split into ordered cross tiles plus its diagonal. Only O(log W) tree levels are required. The adjacent-page rectangle can use the tile algorithm below directly. Subtracting the scan's contribution on those same tiles gives exactly the desired retained correction.

## 4. The bounded-polynomial cross-tile algorithm

Let every column in J precede every row in `I=[l,b]`, and suppose both sets lie in an index interval of length O(W). Put

`z_j=x_j/x_l` (j in J), `v_k=x_l/x_k` (l<k<=b).

Both sequences are bounded by distinct powers of `r^-1`; their sums are at most `1/(r-1)`. The exact entry identity is

`(L^-1)_ij=(-1)^(i-j) (A_i/A_j)/D_(b,j)`

`                *prod_(i<k<=b)(1-z_j v_k)`.

Therefore form

`w_j=(-1)^j (A_l/A_j) u_j/D_(b,j)`

and moments

`M_m=sum_(j in J) w_j z_j^m`, `0<=m<=|I|`.

Output

`(-1)^i (A_i/A_l) sum_m [Z^m]prod_(i<k<=b)(1-v_k Z) M_m`.

Every displayed external diagonal is bounded by `c^-O(1) exp(a/4)`. In fact `sum_j|w_j| <= c^-2 exp(a/4)/(1-exp(-a rho theta))*||u||`, uniformly in tile length.

### Fast moment generation

Use the rational generating function

`sum_(m>=0) M_m Z^m=sum_j w_j/(1-z_j Z)=Q(Z)/P(Z)`.

Build a balanced tree with leaf pairs `(P,Q)=(1-z_j Z,w_j)` and merge by

`P=P_left P_right`,

`Q=Q_left P_right+Q_right P_left`.

Truncate to the needed degree at each node. Since `sum z_j<=1/(r-1)`, all product coefficient l1 norms are at most `exp(1/(r-1))<2`; numerator norms are at most twice the absolute input weight sum. The power-series reciprocal of P has l1 norm at most `c^-1`. Standard fast power-series inversion, or doubling the geometric series of `1-P` (whose l1 norm is <1/2 for r>=e^2), is therefore stable with polynomially bounded intermediates. Product-tree complexity is soft-O(|J|+|I|) scalar operations.

### Fast suffix-polynomial evaluation

The second operation is the transpose of multiplication by the suffix products. Split `[l+1,b]` at m. Right-hand output rows use the moment vector restricted to their degree range. For left rows, replace the moment vector by

`M'_h=sum_k [Z^k]prod_(m<k<=b)(1-v_k Z) M_(h+k)`.

This is one reversed ordinary convolution. Recurse, truncating each child's moment vector to its local output degree. At any level, the multiplying suffix products have disjoint roots; their combined l1 norm is <2. Thus all intermediate moment vectors have norm at most twice the starting moment norm. The total complexity is soft-O(|I|) scalar operations, not |I|*|J|.

### Computing D_(b,j), C_i, and D_j^+

For any fixed boundary b,

`log D_(b,j)=sum_(j<k<=b) log(1-r^(-(q_k-q_j)))`.

This is a single ordinary convolution of the selected-position mask in the physical q-coordinate with the one-sided kernel `f_h=log(1-r^-h)`. On a tile the physical coordinate span is O(W), because consecutive q gaps are 1 or 2. This computes all needed column denominators in soft-O(W) scalar operations, with bounded l1 kernel norm. The global arrays `log C_i` and `log D_i^+` are likewise one-sided convolutions on the physical-coordinate mask. Truncating the kernel after O((p+a+log(1/theta))/a) entries has exponentially small error. Use overlapping pages and include that scalar error in the same precision budget.

### Precision and bit cost

Every convolution, polynomial product, or reciprocal above acts on arrays of polynomial length in p, with coefficient l1 norms bounded by a polynomial in `p` and `theta^-1`, times `exp(O(a))`. Balanced tree depth is O(log p). A standard forward-error induction therefore needs

`p+O(a+log(1/theta)+log p)`

working bits: each primitive convolution has a fixed polynomial error factor in its length, the arithmetic dependency depth is O(log p), and every exact merging/pullback map has norm at most a fixed constant (the external Gaussian diagonals appear only at the endpoints). Even bounding each layer by 3 gives a polynomial amplification. This assumes a fixed fast-convolution implementation with the usual polynomial forward-error bound. No `a/theta`, `aW^2`, or `log s` guard term occurs. Inputs may have arbitrary signs. With quasi-linear integer multiplication, each page costs `O(W p polylog p)` bit operations and the complete lower-factor application costs

`O(s p polylog p)`.

This is one line's data-application statement. Page buffers and product trees have polynomial size in p; a fixed number of multitape tapes suffices using level scans. It does not establish a pure diagonal/convolution factorization with constant-width branching, or automatically establish tensor fusion: the moment and numerator trees contain additions and data-dependent fan-out layouts. Those are separate circuit/interface obligations.

## 5. Remaining obligations

1. A matching stable fast **upper-factor** implementation, or another complete inverse, is still required. Its norm bound above is not an algorithm.
2. Periodic wrap terms must be handled. They are not present in G. Once the full nonperiodic inverse is available, truncating Gaussian wrap terms leaves a polynomial-size boundary Woodbury problem; applying the inverse twice avoids an s-by-boundary dense data multiply. This sketch still requires the full uniform norm/error and tape proof.
3. Tensor fusion must price sums, fan-out, layouts, coefficient generation and precision. This note does not convert the one-dimensional bound into a final kappa.
4. Exact controls are finite evidence for the algebra; they do not replace the analytical proof or establish the missing interface.

## Open next questions

Can the upper-factor nearband be written using the same bounded-root rational moments, while retaining only logarithmic internal normalization? Can the lower-factor numerator/suffix trees be compiled to O(polylog p) width-preserving contractions suitable for full tensor fusion?
