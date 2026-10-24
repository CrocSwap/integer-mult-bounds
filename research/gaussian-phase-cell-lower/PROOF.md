# A matching lower order at a broad Gaussian cell edge

This contribution was produced by Nick Petalas. Apache-2.0.

## Theorem and domain

Let alpha > 0, theta > 0, rho = 1+theta, b0 = pi/alpha^2,
gamma = b0/rho, and c = 1/(2rho). For integers 0 <= k,i < N define

```text
K[k,i] = alpha^-1 exp(-b0 (i-k/rho-c)^2).
```

Assume theta(N-1) <= 1, so beta_k = theta k - 1/2 lies in the
closed phase interval [-1/2,1/2]. For every positive integer m with
2m <= N,

```text
||K^-1||_2 >= alpha m exp(-gamma theta (2m-1)^2).             (1)
```

In particular, if 0 < theta <= 1/16 and
N >= 2 floor(1/(2 sqrt(theta))), then

```text
||K^-1||_2 >= (alpha/4) exp(-pi/alpha^2) theta^(-1/2).       (2)
```

Thus the theta^(-1/2) upper order proved by JoyboyBrian in #5103 is
sharp for fixed alpha on these boundary sections. This is an order theorem,
not Ryanson Jonathan's #4435 proposed sharp leading coefficient. It is not
a lower bound for every section contained anywhere inside a phase cell.

## Cited finite inverse and the new positive rectangle

Put q = exp(-gamma), P_0=1 and
P_s=product_(r=1)^s(1-q^(2r)). The finite Gaussian Toeplitz matrix
G[i,j]=q^((i-j)^2) has the q-LDU factorization retained in Jose Manuel's
#4193 and reproduced in #5103. In the convention
[k choose i]_(q^2)=P_k/(P_i P_(k-i)), its inverse is

```text
G^-1[i,j] = (-1)^(i+j) sum_(k=max(i,j))^(N-1)
    q^(2k-i-j) [k choose i]_(q^2) [k choose j]_(q^2) / P_k.  (3)
```

Every summand after the checkerboard sign is positive. For i <= j, the
k=j summand alone is q^(j-i)/(P_i P_(j-i)), which is at least q^(j-i).
Symmetry gives, for every i,j,

```text
(-1)^(i+j) G^-1[i,j] >= q^|i-j|.                          (4)
```

The factorization and inverse sum are cited predecessor mathematics. The
new step keeps this positive lower term under the broad cell's gauges,
then tests a whole rectangle rather than a single entry.

The exact diagonal factorization K=Dr G Dc is

```text
Dc[i] = exp(-b0 (theta/rho i^2 - 2c i)),
Dr[j] = alpha^-1 exp(b0 (theta/rho^2 j^2 - 2c/rho j - c^2)).
```

These are positive real diagonals. Hence K is invertible, and
K^-1=Dc^-1 G^-1 Dr^-1 has the same checkerboard signs. Multiplying (4)
by the positive inverse gauges gives, when i <= j,

```text
(-1)^(i+j) K^-1[i,j]
 >= alpha exp(b0 beta_j^2/rho^2 - gamma theta (j^2-i^2)).   (5)
```

To verify the exponent, before substituting c it is

```text
b0 (theta/rho i^2 - 2c i - theta/rho^2 j^2
    + 2c/rho j + c^2) - gamma(j-i).
```

Set c=1/(2rho), beta_j=theta j-1/2, and expand. This gives the exponent
in (5) exactly. On 0 <= i < m and m <= j < 2m, its first term is
nonnegative and j^2-i^2 <= (2m-1)^2. Every entry of this m by m
rectangle, after checkerboard signs, is therefore at least

```text
B = alpha exp(-gamma theta (2m-1)^2).
```

Choose x_j=(-1)^j/sqrt(m) on m <= j < 2m and zero elsewhere.
Its Euclidean norm is one. For each of the first m output rows, (5)
shows |(K^-1 x)_i| >= sqrt(m) B, with no cancellation. Summing their
squared magnitudes gives ||K^-1 x||_2 >= m B. This proves (1).

## Matching order and scope

For (2), set m=floor(1/(2 sqrt(theta))). Since theta <= 1/16,
1/(2 sqrt(theta)) >= 2, and floor(x) >= x/2 gives
m >= 1/(4 sqrt(theta)). Also theta(2m-1)^2 <= 1 and
gamma <= pi/alpha^2. Substitution into (1) proves (2).

For example, N=floor(1/theta) meets the size and phase assumptions
for all 0 < theta <= 1/16. This includes N=400 at theta=1/400.
At alpha=3, m=10, the new bound is
30 exp(-361 pi/(3600 rho)), rho=401/400, and in particular exceeds
109/5. A rational certificate uses pi<22/7 and
exp(-t) >= 1-t+t^2/2-t^3/6 for 0<t<1, with
t=(22/63)(361/400), which overestimates the positive exponent.

For completeness, #5103 supplies

```text
||K^-1||_2 <= alpha exp(b0/(4rho^2)) P_(N-1)^(-3)
             (1+sqrt(pi/(gamma theta))).
```

Its cited product estimate is P_(N-1)^(-3) <= exp(pi^2/(4gamma)).
For theta <= 1/16, gamma >= gamma0=16pi/(17alpha^2), giving a
finite fixed-alpha upper constant times theta^(-1/2). Combining that
cited upper result with (2) proves Theta_alpha(theta^(-1/2)) on the
stated family. No upper proof or numerical table of a predecessor is
claimed as new or replayed as a deliverable.

The lower proof also works with arbitrary b0>0 independent of the positive
normalization alpha. The exact rational fixtures use this larger algebraic
family; specializing b0=pi/alpha^2 gives the source kernel. Finite tests
corroborate the inverse-sum, sign, gauge and rectangle steps. The written
argument carries the universal real-parameter claims.

The sharp leading constant, a matching growing-alpha law, rounded inverse
execution, coefficient preparation, circuit prefixes, physical storage/tape,
native admission, outer transfer and integer recovery remain open. This
does not change the selected frontier or prove a multiplication theorem.
