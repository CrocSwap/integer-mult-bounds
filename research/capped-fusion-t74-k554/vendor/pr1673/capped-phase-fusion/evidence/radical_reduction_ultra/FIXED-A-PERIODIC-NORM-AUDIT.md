# Independent audit: fixed-width Gaussian inverse is polynomially bounded

This independently checks the stronger bilateral-LDU proof proposed by the parent and Gaussian-factor agent. It supersedes the need for `a=Theta(log(1/theta))` in the earlier nearest-neighbor norm argument. It does **not** assert a new fast data algorithm or a final exponent.

Let rho=t/s>1, theta=rho-1, q_i=floor(rho i+1/2), beta_i=rho i-q_i for all integer i. Define

```
x_i=exp(2a rho q_i), e_i=exp(-a rho^2 i^2+a beta_i^2),
G_ij=exp(-a q_i^2) x_i^j e_j,
r=exp(2a rho), c=product_(m>=1)(1-r^-m)>0.
```

The sequence x_i increases at least by a factor r at every step and tends geometrically to zero toward minus infinity.

## Finite-origin identities

For an integer origin l, Newton interpolation of columns j>=l gives, on every finite principal interval starting at l,

```
C_i(l)=product_(l<=k<i)(1-x_k/x_i),
L_ij(l)=G_ij product_(l<=k<j)(1-x_k/x_i)/C_j(l), i>=j,
U_ij(l)=(e_j/e_i) h_(j-i)(x_l,...,x_i), j>=i,
G=L(l) diag(C_i(l)) U(l).
```

Here h denotes complete homogeneous symmetric polynomials, and both triangular factors have diagonal one. The powers arising from moving the monomial origin from zero to l cancel exactly: the pivot is C_i(l), not a residual power of x_i.

Since C_i(l)>=c and the normalized complete-homogeneous coefficient is at most c^-1,

```
|L_ij(l)| <= c^-1 G_ij,
|U_ij(l)| <= c^-1 G_ij.
```

All limits as l tends to minus infinity exist, including fixed-degree h over the infinite summable past. The displayed Gaussian domination permits passing the factorization to the bilateral limit.

## Inverse factors

For i>=j and h=i-j,

```
(L(l)^-1)_ij=(-1)^h C_i(l)/C_j(l)
 * exp(a[-beta_i^2+beta_j^2-rho^2 h+2rho sum_(j<k<=i)beta_k])
 / product_(j<k<=i)(1-x_j/x_k).
```

For j>=i and h=j-i,

```
(U(l)^-1)_ij=(-1)^h (e_j/e_i) e_h(x_l,...,x_(j-1)).
```

The latter e_h is elementary symmetric, distinct from the scalar normalization e_j. Its dominant product consists of x_i,...,x_(j-1), so its normalized value is at most c^-1.

Using |beta_i|<=1/2 in the two exact exponents gives uniform estimates

```
|(L(l)^-1)_ij| <= c^-2 exp(a/4-a rho theta h),
|(U(l)^-1)_ij| <= c^-1 exp(a/4-a rho theta h).
```

These pass to the bilateral limits. Products of triangular factors and their inverse factors have only finitely many terms for each supported matrix entry, so both inverse identities survive directly. All four factors define bounded absolutely row-summable operators.

## Periodization

Every limiting factor is simultaneously s-periodic in its row and column indices. For a bounded absolutely row-summable periodic array A, define

```
Pi(A)_ij=sum_(n in Z) A_(i,j+ns), 0<=i,j<s.
```

Absolute summability and periodicity give `Pi(AB)=Pi(A)Pi(B)` by reindexing
`B_(k,j+ns)=B_(k+ms,j+(n+m)s)`. Also `||Pi(A)||_infinity<=||A||_infinity` and Pi(I)=I_s. The retained periodic Gaussian matrix is exactly N=Pi(G). Therefore

```
N^-1=Pi(U^-1 diag(C)^-1 L^-1),
||N^-1||_infinity <= c^-4 exp(a/2)/(1-exp(-a rho theta))^2.
```

For **any fixed a>=1**, this is O(theta^-2), with a constant depending only on a. Thus a fixed admissible integer Gaussian width alpha suffices for the norm and perturbation estimates. No logarithmic growth of alpha is needed for conditioning.

The theorem changes an analytic parameter constraint. Applying these factors quickly on the tape remains a separate constructive obligation.
