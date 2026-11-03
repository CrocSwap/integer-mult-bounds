# Sharp total-budget conditioning of square-zero error words

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Work in a real or complex Euclidean space of fixed dimension n >= 2. Let
K >= 1 be an integer and rho >= 0. For any K linear maps D_i satisfying

```
D_i^2 = 0,       d_i = ||D_i||_2,       sum_i d_i <= rho,
R = (I+D_K) ... (I+D_1),
Phi(t) = (sqrt(t^2+4)+t)/2,
E_K(rho) = Phi(rho/K)^K,
```

all factors and R are invertible, and

```
||R||_2, ||R^-1||_2 <= product_i Phi(d_i) <= E_K(rho),
cond_2(R) <= E_K(rho)^2.
```

The maximum of each of the three quantities over this entire domain is,
respectively, E_K(rho), E_K(rho), and E_K(rho)^2. One two-dimensional word
attains all three simultaneously, and embedding it in dimension n preserves
attainment. The maps need not commute or have rank one. The maximum concerns
this error-word domain, not an independently specified production circuit.

For rho > 0, attaining the total-budget envelope requires every error norm
to equal rho/K. This condition is necessary, not sufficient: the singular
vectors must also align. Every nonzero word has a strictly smaller bound than
Ali Romman's sufficient product `product_i (1+d_i)` in PR5288, when that bound
is evaluated with this same Euclidean norm data.

For every finite K and rho > 0,

```
E_K(rho) < exp(rho/2),
lim_(K->infinity) E_K(rho) = exp(rho/2).
```

Thus the coefficient 1/2 is sharp for a length-independent exponential norm
bound. Its square gives the sharp supremum exp(rho) for condition numbers.
There is no restriction rho < 1. If rho = 0, all maps and products are identity.
In dimension one every square-zero map is zero, so the positive-budget
attainment statement requires n >= 2.

## One square-zero factor

Let H = ker D. Since D^2=0, im D is contained in H. On the orthogonal
sum H direct-sum H-perp, D has the block form

```
D = [ 0  B ],          I+D = [ I  B ].
    [ 0  0 ]                [ 0  I ]
```

Independent unitary bases within H and H-perp put B in singular-value form.
This is a unitary similarity of D. It decomposes I+D into two-dimensional
blocks `[[1,s],[0,1]]`, one for each nonzero singular value s of B, and
identity blocks. The Gram matrix of a two-dimensional block is

```
[ 1    s   ],    determinant 1,    trace s^2+2.
[ s  1+s^2 ]
```

Its singular values are Phi(s) and 1/Phi(s). Phi increases on the nonnegative
real line. Also ||B||_2=||D||_2=d. Consequently

```
||I+D||_2 = ||(I+D)^-1||_2 = Phi(d).
```

The inverse is I-D, which has the same singular values. This calculation is
classical; the new claims concern its sharp composition at a total error budget.
It does not hold with an arbitrary induced norm. For example, the infinity
norm of `[[1,d],[0,1]]` is 1+d.

## Ordered products and the total budget

Apply submultiplicativity to the factors and to the inverse product in its
reverse order. The preceding factor identity proves the product bound for
both R and R^-1. Multiplying their bounds gives the condition-number bound.
No commutation or cancellation has been assumed.

Write f(t)=log Phi(t)=asinh(t/2). Its derivatives are

```
f'(t) = 1/sqrt(t^2+4),
f''(t) = -t/(t^2+4)^(3/2).
```

It is increasing and strictly concave on [0,infinity). Jensen's inequality
and the total-budget constraint give

```
sum_i f(d_i) <= K f((sum_i d_i)/K) <= K f(rho/K).
```

For rho > 0 equality requires that the whole budget be spent and every d_i
be equal. Also sqrt(t^2+4)<t+2 for t>0, so Phi(t)<1+t. This gives the strict
comparison with PR5288's product whenever at least one d_i is nonzero.
Finally asinh(x)<x for x>0 and asinh(x)/x tends to one at zero. These facts
prove the finite-length strict exponential bound and its limit.

## Attainment, including rational certificates

Let d=rho/K, t=Phi(d), so d=t-1/t. Use the alternating factors

```
U = [ 1  d ],     L = U^T,
    [ 0  1 ]

I+D_i = U for odd i, L for even i.
```

Both U-I and L-I are square-zero with Euclidean norm d. Set
v=(1,t) and u=(t,1). They have equal lengths and

```
U v = t u,       L u = t v.
```

Thus the length-K product sends v to t^K times u or v. The product upper
bound is t^K, so the norm is exactly t^K. Its determinant is one; in dimension
two its two singular values have product one. The second is therefore t^-K.
This proves inverse norm t^K and condition number t^(2K), simultaneously.
The identity on n-2 extra coordinates proves attainment in every n >= 2.
The zero-budget case is immediate.

For any rational t >= 1, d=t-1/t, both shears and their complete products are
rational. The Gram eigenvalues t^(2K) and t^(-2K) then permit an exact
certificate without evaluating radicals or logarithms. The finite checker
uses these rational instances. The written proof, rather than extrapolation
from them, covers every real rho and complex dimension.

## Consequence for the retained coefficient-error interface

Use PR5288's notation and hypotheses, now with the Euclidean norm:

```
N_i^2=0,
A_i=I+a_i N_i,       Ahat_i=I+(a_i+e_i)N_i,
F_j=A_j...A_1,       Q_j=Ahat_j...Ahat_1,
D_i=e_i F_(i-1)^-1 N_i F_(i-1).
```

PR5288, following ywz65's PR2701 interaction coordinates, supplies
`F_j^-1 Q_j=(I+D_j)...(I+D_1)` and `D_i^2=0`. These are credited premises,
not replay deliverables here. Applying the new theorem gives, for j >= 1,

```
H_j = product_(i<=j) Phi(||D_i||_2),
||Q_j||_2 <= ||F_j||_2 H_j,
||Q_j^-1||_2 <= ||F_j^-1||_2 H_j,
cond_2(Q_j) <= cond_2(F_j) H_j^2.
```

If only the sum rho_j of these j error norms is known, replace H_j by
E_j(rho_j). The physical-prefix corollary is sufficient; its sharpness for
an additional fixed production word is not claimed. The exact sharp theorem
is for the declared interaction-error domain. An instance with all exact
coefficients zero realizes that domain algebraically, but does not constitute
a production implementation or a storage policy.

No additive arithmetic error or operator-defect improvement is claimed here.
Those budgets require their own suffix/error propagation and physical costs.
A perturbed linear matrix being invertible does not make a rounded grid
instruction reversible. Overflow, coefficient generation/storage, actual
rounding behavior, dirty restoration, native/compiler costs, tape/stock and
the whole signed supplier invoice remain separate. All five selected
framework assumptions retain their status. No new kappa is claimed.
