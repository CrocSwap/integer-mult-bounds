# Bilateral Gaussian LDU and a fixed-width periodic inverse bound

Independent audit of the parent's infinite-LDU observation. This is an analytic norm theorem. It does **not** assert that the bilateral factors already have a fully priced fast implementation.

## Statement

Let `1<rho=t/s<=2`, `theta=rho-1`, `q_i=floor(rho*i+1/2)` for all integers i, and `beta_i=rho*i-q_i`. For any `a>=1`, define on Z

`G_ij=exp(-a[(rho*j-q_i)^2-beta_j^2])`.

Let `r=exp(2a rho)` and `c=prod_(m>=1)(1-r^-m)>0`. Then G has an exact factorization on bounded bilateral sequences

`G=L C U`,

where L is unit lower triangular, U is unit upper triangular, C is diagonal, and all factors and their inverses are bounded. Moreover all six factors are invariant under simultaneous index translation by s. Their periodizations therefore factor the periodic Gaussian matrix N, and

`||N^-1||_infinity <= c^-4 exp(a/2)/(1-exp(-a rho theta))^2`.

In particular, at the fixed choice `a=1`,

`||N^-1||_infinity < 16 theta^-2`.

Any fixed a>=1, including a=4pi if an integer alpha>=2 is retained, gives a constant times theta^-2. No lower bound proportional to log(1/theta) on a is needed for this norm theorem.

## 1. Finite-origin factorization and the shift correction

Write `x_i=r^q_i`, `d_i=exp(-a q_i^2)`, and `e_i=exp(-a rho^2 i^2+a beta_i^2)`. Then `G_ij=d_i x_i^j e_j`, including negative indices, and `d_i x_i^i e_i=1`.

For a finite square principal interval `[l,r0]`, the Vandermonde powers must begin at zero. The correct shifted row diagonal is **d_i x_i^l**, and the power is `j-l`. This removes a possible erroneous origin-dependent diagonal from the upper factor.

Put

`C_i(l)=prod_(l<=k<i)(1-x_k/x_i)`.

Finite Newton elimination gives the pivot `C_i(l)` and

`L^l_ij=G_ij prod_(l<=k<j)(1-x_k/x_i)/C_j(l)`, `i>=j`,

`U^l_ij=(e_j/e_i) h_(j-i)(x_l,...,x_i)`, `j>=i`.

Here h is the complete symmetric polynomial, h_0=1. Upper and lower inverses are

`(U^l)^-1_ij=(-1)^(j-i)(e_j/e_i) e_(j-i)(x_l,...,x_(j-1))`,

`(L^l)^-1_ij=(-1)^(i-j) exp(E_ij) C_i(l)/(C_j(l) D_ij)`,

where

`D_ij=prod_(j<k<=i)(1-x_j/x_k)`,

`E_ij=a[-beta_i^2+beta_j^2-rho^2(i-j)+2rho sum_(j<k<=i)beta_k]`.

These formulas are independent of the right endpoint whenever their indices exist.

## 2. Uniform bounds before taking limits

Because each q-gap is at least 1,

`c<=C_i(l),D_ij<=1`.

The normalized complete symmetric polynomial satisfies

`h_h(x_l,...,x_i)/x_i^h <= c^-1`.

Indeed, its generating function after division by x_i^h has variables 1 and a subset bounded by r^-1,r^-2,...; coefficient h is bounded by the sum of all coefficients of the remaining product, which is at most c^-1. Consequently

`0<=L^l_ij<=c^-1 G_ij`, `0<=U^l_ij<=c^-1 G_ij`.

For the elementary polynomial, compare each h-subset of the prefix with its h largest nodes. The deficits form a partition and give

`e_h(x_l,...,x_(j-1))/prod_(j-h<=k<j)x_k <= c^-1`.

The two inverse bounds are therefore

`|(L^l)^-1_ij|<=c^-2 exp(a/4) exp(-a rho theta(i-j))`, `i>=j`,

`|(U^l)^-1_ij|<=c^-1 exp(a/4) exp(-a rho theta(j-i))`, `j>=i`.

Both use only `-1/2<=beta_k<1/2`. Thus their row norms are at most the corresponding constants divided by `1-exp(-a rho theta)`, uniformly in l and the finite size.

The row sum of G is uniformly finite, since

`G_i,i+h <= exp(a/4) exp(-a(rho*|h|-1/2)^2)`.

The same positive Gaussian bound controls all finite-origin L and U factors.

## 3. Letting the left origin tend to minus infinity

For fixed i,j, C_i(l) converges to

`C_i=prod_(k<i)(1-x_k/x_i)` in `[c,1]`.

The lower products converge absolutely. The upper homogeneous and elementary polynomials converge because `sum_(k<=i)x_k` is finite; the estimates above remain valid. Define L,U,Linv,Uinv by these limits.

For each fixed i,j, the finite-origin identity for G is a sum over `l<=k<=min(i,j)`. Every summand is bounded by `c^-2 G_ik G_kj`. That bilateral Gaussian product is summable in k, so dominated convergence gives `G=L C U` entrywise.

For two lower triangular matrices, a fixed product entry has only the finitely many intermediate indices between its column and row. Therefore the finite-origin identities `(L^l)^-1 L^l=L^l(L^l)^-1=I` pass directly to the limit. The upper-triangular identities work the same way. All four matrices have uniformly bounded row sums, so these entrywise products are also bounded-operator identities on l-infinity; absolute convergence justifies applying them to every bounded input.

This argument does not require operator-norm convergence of the finite sections. Such convergence is not asserted.

## 4. Periodization is a bounded algebra homomorphism

Since `q_(i+s)=q_i+t` and `beta_(i+s)=beta_i`, G is invariant under simultaneous translation `(i,j)->(i+s,j+s)`. Every displayed factor has the same invariance: ratios `x_k/x_i` are preserved, and the Gaussian/prefix expressions shift together. C_i is s-periodic.

For an invariant matrix A with bounded absolute row sums, set

`Pi(A)_ij=sum_(n in Z) A_(i,j+ns)`, `0<=i,j<s`.

Then `||Pi(A)||<=||A||`. If A and B are two such matrices, absolute row summability permits rearrangement after writing each intermediate index as `k=l+ms`. Simultaneous invariance yields

`Pi(AB)=Pi(A) Pi(B)`.

Thus `N=Pi(G)=Pi(L) Pi(C) Pi(U)`, and its inverse is

`N^-1=Pi(Uinv) Pi(C^-1) Pi(Linv)`.

The diagonal periodization Pi(C) is simply diag(C_0,...,C_(s-1)). Multiplying the established norm bounds proves

`||N^-1||<=c^-4 exp(a/2)/(1-exp(-a rho theta))^2`.

For a=1, r>=e^2>7, and the elementary product bound gives `c>=1-sum_(m>=1)r^-m>5/6`. Also `1-exp(-rho theta)>=theta/2` for 0<theta<=1. Hence the displayed bound is below `4(6/5)^4 exp(1/2) theta^-2<16 theta^-2`.

## Algorithmic boundary

This removes Woodbury from the *analytic factorization*. A direct implementation could still choose Woodbury for convenience. The identity for a Woodbury audit is: if `N=N0+UV`, then with `S=I+V N0^-1 U`,

`S^-1=I-V N^-1 U`.

The inverse on the right is that of the updated N, not the base N0. The fixed-a bound above may be used analytically to bound that right-hand side even before an algorithm for N inverse is available.

A fast upper-factor algorithm and the precision/layout needed to tensorize it remain separate obligations. No multiplication exponent follows just from this theorem.
