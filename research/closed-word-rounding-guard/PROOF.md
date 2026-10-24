# Endpoint-conditioned simultaneous rounding

## Statement

Let `A_1,...,A_K` be invertible matrices over the real or complex numbers,
in execution order. Use any induced matrix norm and its compatible vector norm.
Set `F_0=I` and `F_j=A_j...A_1`. Assume

```
max_{0<=j<=K} max(||F_j||, ||F_j^-1||) <= B,  B>=1.
```

Let `C>=1` be a separate upper bound for `||F_K||`. For perturbations
`Delta_j`, define

```
D_j = F_j^-1 Delta_j F_(j-1),
rho = sum_j ||D_j|| < 1,
U = sum_j ||u_j||.
```

The actual trajectory obeys
`y_j=(A_j+Delta_j)y_(j-1)+u_j`, with `||y_0||<=M`. Then

```
||y_K-F_K y_0|| <= C (rho M + B U)/(1-rho).                 (1)
```

In particular, the coefficient-only operator defect is at most
`C rho/(1-rho)`. For two-wire gates with `||Delta_j||<=2 eta`,
`||u_j||<=2 eta`, `M<=1`, and target `p>=0`, the sufficient guard is

```
P = p + ceil(log2(8 K C B^2)),  eta=2^-P.                  (2)
```

This improves the generic `8 K B^3` prescription of ywz65's PR2701 whenever
the endpoint has a smaller certified norm. For `F_K=I`, or a unitary endpoint
in Euclidean norm, one may take `C=1`. The exponent of `B` drops from three
to two. This controls the final output; intermediate outputs still use their
own endpoint norms and need not admit the same reduction.

## Proof of the upper bound

Set `z_j=F_j^-1 y_j`. Keeping the multiplication order gives

```
z_j=(I+D_j)z_(j-1)+F_j^-1 u_j.
```

Every consecutive interaction product has norm at most
`product_i(1+||D_i||) <= 1/(1-rho)`. To see the second inequality, expand
the finite product in elementary symmetric sums. Its degree-r sum is at
most `rho^r`; summing the geometric series gives the bound. Removing the
constant term bounds the full product's difference from `I` by
`rho/(1-rho)`. Each forcing term has norm at most `B||u_j||`, and all
later interaction products satisfy the same bound. Thus

```
||z_K-y_0|| <= (rho M+B U)/(1-rho).
```

Multiplying by the final `F_K` uses `C`, rather than the largest norm of
any intermediate prefix. This proves (1). This is the same standard
interaction-coordinate argument credited to PR2701, with its endpoint
factor retained separately; no new general perturbation method is claimed.

For (2), `rho<=2 K B^2 eta<=1/4`, and `U<=2K eta`. Therefore

```
||y_K-F_K y_0||
 <= (8/3) K C (B^2+B) eta
 <= (16/3) K C B^2 eta
 <= (2/3) 2^-p
 <= 2^-p.
```

The local bounds `2 eta` follow, for example, from the Frobenius estimate
for two complex entry errors per row and from two coordinate arithmetic
errors of magnitude at most `eta`. A production arithmetic kernel must
supply those bounds; the theorem does not implement it.

## Matching elementary words

The following all-size construction shows that the improved quadratic
dependence cannot be replaced by a smaller power in this error model.
It also shows that the original cubic dependence is necessary when the
endpoint norm is allowed to grow with `B`.

Use the induced infinity norm. For integers `q,L>=1`, put

```
b=2^q,  T=diag(2,1/2),  D=T^q,
S(t)=I+t E_21,  S_+=S(1/2),  S_-=S(-1/2).
```

Execute `q` copies of `T`, then `L` pairs `S_+,S_-`, then `q` copies of
`T^-1`. The exact endpoint is `I`. Every exact prefix and its inverse has
norm at most

```
B_* = 3b/2.                                               (3)
```

This is the exact maximum. During the scale runs the prefixes are diagonal
with entries between `1/b` and `b`. During the shear pairs they are `D` or

```
S(1/2)D = [[b,0],[b/2,1/b]],
[S(1/2)D]^-1 = [[1/b,0],[-b/2,b]].
```

The latter inverse has row sum `3b/2`; all other row sums are no larger
because `b>=2`. Every exact gate and its inverse has norm at most two.
All exact gates have determinant one and dyadic entries.

Perturb each of the `2L` active shear coefficients by the same positive
dyadic `eta<=1/4`, leaving all scale gates exact. These are errors in the
already nonzero coefficients, each of norm `eta`. The perturbed gates
also have determinant one and norm at most two. The shear identity
`S(s)S(t)=S(s+t)` gives, with no discarded higher-order terms,

```
Q_closed = D^-1 S(2L eta) D
         = I + 2L b^2 eta E_21.                           (4)
```

Hence unit input `e_1` has exact endpoint error `2L b^2 eta`. The
interaction matrices are all `b^2 eta E_21` at the perturbed sites, so
`rho=2L b^2 eta`. This identity holds at every positive dyadic `eta`;
choosing a smaller one enforces any prescribed small-radius premise.

For the unrestricted-endpoint version, execute `2q` copies of `T^-1`
after the shear pairs. The exact endpoint is `D^-1`, whose norm is `b`;
the exact common prefix bound is still (3). Now

```
Q_open = D^-2 S(2L eta) D
       = D^-1 + 2L b^3 eta E_21.                          (5)
```

All gates retain the same norm and determinant bounds. Thus the additional
factor of the endpoint norm is necessary, even for elementary two-wire
words with uniformly bounded exact gates and inverses.

To compare powers including the gate count, take `L=q` and
`eta=2^(-4q-12)`. Then `K_closed=4q`, `K_open=5q`, and `rho<1/4` for
every `q>=1`. For every fixed `alpha<2`, the ratio of (4)'s error to
`K_closed B_*^alpha eta` grows without bound as `q` grows. Likewise for
every `alpha<3`, the ratio of (5)'s error to
`K_open B_*^alpha eta` grows without bound. Consequently no uniform
constant can replace the quadratic closed-word or cubic unrestricted
power by a smaller one under only these hypotheses. Optimal numerical
constants are not asserted.

The perturbations are admissible bounded coefficient errors. This does not
say that a particular deterministic nearest-rounding rule creates these
errors on these dyadic coefficients. Exploiting such a rule's additional
structure would change the model and is left open.

## Verification boundary

The formulas above prove the all-size claims. Exact finite matrix products
corroborate them, including both independent input columns, every intermediate
prefix, inverse prefixes, simultaneous noncommuting perturbations and
arithmetic forcing. A two-by-two matrix of forcing terms records the two
individual column trajectories in the finite checks. It is not a model of
independent random errors. The replay uses rational infinity norms; it does
not measure Euclidean norms of a production complex compiler.

No production caller, reversible rounded instruction sequence, integer-bit
budget, overflow proof, physical tariff, supplier admission, complete
multiplication theorem or new kappa follows from this result alone.
