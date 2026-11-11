# The sharp scale-uniform half-shift lower envelope

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Fix an integer N >= 1. For 0 < q < 1 and epsilon in {-1,1}, define the
normalized, untruncated Gaussian section on indices 0,...,N-1 by

```text
T_N^epsilon(q)[i,j] = q^((j-i)^2-epsilon(j-i)).
c_N = 1 / (2 sin(pi/(4N+2))).
```

Then

```text
||T_N^epsilon(q)^(-1)||_2 >= c_N,
inf_(0<q<1) ||T_N^epsilon(q)^(-1)||_2 = c_N.
```

For N >= 2 the first inequality is strict at every admissible q. Its
infimum is approached as q tends to zero. For N = 1 the norm is always 1.
This is an exact infimum at each finite size, uniform over Gaussian scale.
It is not the norm at a specified positive q or a fixed-q asymptotic formula.

In particular c_N/N tends to 2/pi. At any fixed q, the cited upper bound
N/P_(N-1)^3 and P_infinity > 0 show that the half-shift inverse grows in
Theta(N). The new result is the sharp q-uniform envelope, rather than a
claim that every linear-growth consequence is new. Nick Petalas's #5150
already supplies related lower estimates for varying-phase Gaussian cells.

## Cited input and conventions

Jose Manuel / jmbarrancoml's #4193, Section 3a of
`research/shifted-gaussian-conditioning/PROOF.md`, retains Vlado
Vojdanovski's finite Gaussian q-LDU factors. We cite those exact identities
as premises. No predecessor scientific verifier is rerun here.

Put Q=q^2, P_0=1, P_r=product_(h=1)^r(1-Q^h) and
[k choose i]_Q=P_k/(P_i P_(k-i)). For G[i,j]=q^((i-j)^2), the factors imply

```text
G^(-1)[i,j] = (-1)^(i+j) sum_(k=max(i,j))^(N-1)
    q^(2k-i-j) [k choose i]_Q [k choose j]_Q / P_k.
```

Every unsigned summand is positive. The half-shift convention is
T_N^+(q)=D G D^(-1), D[i,i]=q^i. Therefore, for the orthogonal sign matrix
J[i,i]=(-1)^i, B=J T_N^+(q)^(-1) J has entries

```text
B[i,j] = sum_(k=max(i,j))^(N-1)
    Q^(k-j) [k choose i]_Q [k choose j]_Q / P_k.          (1)
```

Equation (1) is only the cited inverse identity under the stated diagonal
conjugation. The new step below uses its whole positive upper triangle.

## Triangular domination

Let U_N[i,j]=1 when i<=j, and zero otherwise. For i<=j, retain the k=j
term in (1). It is

```text
[j choose i]_Q / P_j = 1/(P_i P_(j-i)) >= 1.
```

For i>j every term is positive. Thus B>=U_N entrywise. If real matrices
0<=A<=B entrywise, then ||A||_2<=||B||_2. Indeed, for any complex vector x,
|Ax|<=A|x|<=B|x| coordinatewise. Taking Euclidean norms and a supremum
proves the assertion. Orthogonality of J gives

```text
||T_N^+(q)^(-1)||_2 = ||B||_2 >= ||U_N||_2.              (2)
```

For N>=2, B[N-1,N-1]=1/P_(N-1)>1. A maximizing right singular vector of
U_N can be chosen strictly positive: U_N^T U_N has strictly positive
entries, so the elementary Perron theorem applies. Both U_N x and Bx
are positive and the last coordinate of Bx is strictly larger. Hence (2)
is strict. The negative endpoint is the transpose and has the same norm.

## The classical triangular singular value

Let S have ones on the first superdiagonal and zeros elsewhere.
U_N^(-1)=I-S. The symmetric matrix

```text
(I-S)(I-S)^T
```

has diagonal (2,...,2,1) and neighboring entries -1. Its interior
eigenvector recurrence has solution v_i=sin((i+1)theta) and eigenvalue
lambda=2-2cos(theta). The first boundary is v_(-1)=0. The last boundary
is v_N=v_(N-1), so

```text
theta_k = (2k-1)pi/(2N+1),  k=1,...,N.
```

These give N distinct eigenvalues and hence the complete spectrum. The
least is 4 sin^2(pi/(4N+2)), proving ||U_N||_2=c_N. The same argument
includes N=1. An exact corroborating identity for the characteristic
polynomial p_N is

```text
p_N(2-z-z^(-1)) = sum_(j=-N)^N (-1)^j z^j.             (3)
```

Multiplication by z^N(z+1) gives (-1)^N(z^(2N+1)+1). The root z=-1
is canceled and the remaining paired roots yield the angles above.
These triangular singular values are classical; no priority is claimed
for that elementary matrix calculation.

## Sharpness over scales

Keep N fixed and let q decrease to zero. The integer exponent h(h-1)
is zero exactly at h=0,1 and positive at every other integer. Thus

```text
T_N^+(q) -> I+S,
(I+S)^(-1) = J U_N J.
```

The limiting matrix is invertible. Finite-dimensional inversion and the
Euclidean operator norm are continuous there. Consequently the norms
tend to c_N. Combined with the lower bound, this proves the exact infimum.
Transposition proves the other endpoint. Finally sin(x)/x tends to 1,
giving c_N/N -> 2/pi. No exchange of a q-limit and an N-limit is used.

## Evidence and limits

The new verifier constructs literal rational endpoint kernels and inverts
them with Gauss-Jordan elimination, checking both inverse products. It
checks the new triangular domination directly, positivity, strictness and
size-one equality. It does not reconstruct or audit the predecessor's
q-LDU factors. Exact Laurent coefficients check the entire spectral
identity (3) at every tested size, without floating point trigonometry.
Separate small-q fixtures measure the full rational Frobenius difference
from U_N. All finite counts come from the generated receipt.

The universal quantifiers, strictness and limiting statement rely on this
written proof and its cited q-LDU premise. Finite tests do not establish
them by extrapolation. Independent human and formal proof-kernel review
are unclaimed. No actual raw normalization, production diagonal gauge,
rounding rule, native algorithm, compiler/stock/tape bill or supplier is
provided. Interior shifts are outside the lower bound. The fixed-q sharp
coefficient and growing-parameter estimates remain open.
