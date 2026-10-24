# The actual scalar boundary solve against the original Schur matrix

This independently audits one implication in Jose Manuel / `jmbarrancoml`'s
[PR3851 physical Gaussian core](../physical-gaussian-core/PROOF.md), retained
at `7ab67b4a84d28cd562b9711aa315ca5b47822b37`. It addresses a sub-obligation
of [PR5081's local-defect handoff](../tensor-compression-error-refinement/README.md):
the unchanged scalar `BandedSolve` compared with the **original** old-H
Schur matrix. It does not prove the complete Core approximation theorem.

Two setup perturbations must remain distinct. `Window.prepare_schur` first
rounds the exact Schur matrix and computes exact LU of that rounded matrix.
`prepare_bands` then rounds the strict triangular factors and the **pivot
reciprocals**. The online upper diagonal is consequently the inverse of a
stored reciprocal. It is not the rounded original upper diagonal.

## 1. Quantified statement and inherited premises

For a complex vector use `||v||_infinity=max_i |v_i|`, where `|.|` is complex
modulus; for a matrix use the induced row-sum norm `max_i sum_j |M_ij|`.
The matrices in this caller are real, but right-hand sides may be complex.
All rounding below acts separately on real and imaginary components.
`BandedSolve` is a scalar owner: the complex statement pairs its two real
component executions with the same factors, as in `Core.scalar`.

Let `p>=101` be an integer, `P=32768p`, and `eta=2^-P`. Let `H` be the
source's finite global real old-H matrix with positive diagonal and row gap

```text
H_ii - sum_(j!=i) |H_ij| >= 1/(8p).
```

Let `H_W` be an admitted principal window, partitioned into interior `I`
and nonempty boundary `B`. Empty `I` is allowed. Define the exact reference

```text
S = H_BB - H_BI H_II^-1 H_IB,
Sbar = round_P(S),       Sbar = L U.
```

The following source premises are retained, rather than inferred from a
successful parse or finite execution:

1. The page is produced from this original `H_W` and this exact `S`.
   Its boundary order has half-bandwidth `b=2w<=2p`, and exact no-pivot
   LU of `Sbar` has unit lower diagonal, positive upper pivots, and the
   same half-bandwidth. The source's stored zero padding preserves it.
2. These exact factors satisfy `||L||<=65p^2` and `||U||<2`.
   These are the retained factor-growth caps for `LU(round_P(S))`, not
   caps assumed for an unrelated factorization of `S`.
3. Signed records, exact products and complete dot products implement their
   stated arithmetic before truncation, and the invocation satisfies its
   storage/width, ownership and extent contracts. We analyze unbounded
   integer arithmetic first; this note does not prove full-Core headroom.

The global gap itself, matching coefficient/old-H production, bandwidth,
positive pivots and factor caps are inherited analytic/setup obligations.
We derive the inverse estimates used below from these premises. Neither
`||L^-1||` nor `||U^-1||` is an additional premise for this argument.

For every represented complex P-grid right-hand side `r` satisfying premise3,
let `x` be the actual two-pass boundary return in physical value units.
Then, with `R=max(1,||r||)`,

```text
||x - S^-1 r|| < 2^17 p^5 eta R.                           (1)
```

The constant is independent of `|B|`, the number of cells and the number
of completed rows. This recovers the explicit noncyclic allowance in the retained
[RaD phase-cell report](../../references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md);
it is not a new precision policy or a cost saving.

## 2. The exact reference has inverse norm at most 8p

Restricting a row to a principal set only removes off-diagonal absolute
values, so both `H_W` and a nonempty `H_II` retain the same gap. For any
complex vector `v`, choose `i` with `|v_i|=||v||`. The reverse triangle
inequality gives

```text
|(H_W v)_i| >= (H_ii - sum_(j!=i,j in W)|H_ij|) ||v||
             >= ||v||/(8p).
```

Thus `H_W` and `H_II` are invertible, with inverse norm at most `8p`.
The exact block inverse identity says `(H_W^-1)_BB=S^-1`. Equivalently,
solve `H_W z=(0,r_B)` and eliminate `z_I`; its boundary equation is
`S z_B=r_B`. Boundary injection and restriction both have norm one, hence

```text
||S^-1|| <= ||H_W^-1|| <= 8p.                              (2)
```

For empty `I`, `S=H_W` and the conclusion is immediate. This argument
does not replace the old-H inverse by the local q-model inverse.

## 3. Both setup roundings and the effective upper diagonal

Write `tau_P` for truncation toward zero to the eta grid. The actual
`Rational.rounded` computes that operation. Each real entry moves by less
than `eta`. A row of `S` has at most `2b+1<=4p+1<=5p` nonzero positions;
zero entries stay zero. Therefore

```text
E0 = Sbar-S,             ||E0|| < 5p eta.                  (3)
```

In `prepare_bands`, let `Lhat` have exact unit diagonal and rounded strict
lower entries; let `uhat_ij=tau_P(U_ij)` for `j>i`. For every pivot put

```text
q_i=1/U_ii,       qhat_i=tau_P(q_i),
(Ueff)_ii=1/qhat_i,       (Ueff)_ij=uhat_ij for j>i.
```

Since `0<U_ii<2`, `q_i>1/2`. Also `eta<=1/4`, so `qhat_i>1/4` is positive.
The effective diagonal satisfies

```text
|1/qhat_i-U_ii| = U_ii |q_i-qhat_i|/qhat_i < 8 eta.
```

This explicitly prices reciprocal rounding. Counting the band entries gives

```text
DL=Lhat-L,       ||DL|| < 2p eta,
DU=Ueff-U,       ||DU|| < (2p+8)eta <= 3p eta,
||Lhat|| <= 65p^2+2p eta <= 66p^2.                         (4)
```

For `T=Lhat Ueff`, expand the product rather than multiplying rounded
inverse bounds:

```text
E1=T-Sbar = DL U + L DU + DL DU,
||E1|| < (4p+195p^3)eta+6p^2 eta^2 < 200p^3 eta.           (5)
```

The final inequality uses `p>=101`, `4p<=4p^3`, and `6eta<p`; it follows
for every stated p, not from a sampled precision table. Combining (3),(5),

```text
||T-S|| < (200p^3+5p)eta <= 205p^3 eta.                   (6)
```

Here is a separate Neumann step for each setup perturbation. For every
positive integer p, `p<=2^p`. Consequently

```text
40p^2 eta < 2^(6-32766p) < 1/2,
3200p^4 eta < 2^(12-32764p) < 1/2.
```

Equations (2),(3) therefore give `||Sbar^-1||<=16p`; equations (5) and
that bound give

```text
||T^-1|| <= 32p.                                         (7)
```

Thus the source's product-inverse bound concerns the effective factor
product actually solved online. It incorporates the initial Schur rounding,
not just rounding of factors from an assumed exact `S`.

## 4. Exact residual of the executed two-pass program

The row order and rounding sites in `gaussian_boundary.py` are:

```text
y_i = tau_P(r_i - sum_(j<i) Lhat_ij y_j),
x_i = tau_P(qhat_i (y_i - sum_(j>i) uhat_ij x_j)).
```

The first pass runs forward; the second runs backward with its stored
future-value buffer. `subtract_row` accumulates the full dot product exactly
on the 2P grid. The upper pass multiplies this **unrounded** residual by
the stored reciprocal, then truncates from the 3P grid to the P grid.
There is no intermediate upper-residual truncation. These are statements
about the unchanged source, not a replacement evaluation order.

Define residuals at these actual computed states:

```text
e_f = Lhat y-r,           e_b = Ueff x-y.
```

Each real and imaginary component of `e_f` has absolute value below `eta`, so
`||e_f||<sqrt(2)eta<2eta`. If `epsilon_i` is the final upper truncation
error, each of its real/imaginary components is below `eta`, and
`(e_b)_i=epsilon_i/qhat_i`. Hence

```text
||e_b|| < 4sqrt(2)eta < 8eta.
```

In particular `e_b` is not just the final truncation error. The reciprocal
conversion is necessary even when the stored reciprocal is exact.
Substitution gives the exact completed residual identity

```text
rho = T x-r = e_f + Lhat e_b.                             (8)
```

By (4),

```text
||rho|| < (2+528p^2)eta <= 530p^2 eta.                    (9)
```

This is a maximum over rows. No factor proportional to the number of rows
appears. Neither the computed solver nor its individual rounded passes are
assumed linear, Lipschitz, or exact inverses of one another.

## 5. Error against the original old-H Schur system

Let `v=S^-1 r`. From (8) obtain the identity

```text
x-v = T^-1 [rho-(T-S)v].                                 (10)
```

The error has two independent sources: the completed online residual and
both setup perturbations. Using (2),(6),(7),(9) in (10) yields

```text
||x-v|| < 32p [530p^2 eta + 205p^3 eta (8p||r||)]
         = 16960p^3 eta + 52480p^5 eta ||r||
         <= 69440p^5 eta max(1,||r||)
         < 131072p^5 eta max(1,||r||).
```

This proves (1), including `r=0`; no strict inequality is inferred from a
zero input-scaled term. The larger `max(1,||r||)` allowance is intentional.
The right-hand side may already contain errors from Core's first interior
pass. The theorem compares with `S^-1` on **that same actual r**. Transport
of its earlier error is a separate completed-Core obligation.

## Evidence, attribution and remaining obligations

Finite evidence should check the actual rounded-factor serialization,
forward and backward values, (8) and (10), and distinguish initial Schur
rounding from factor rounding. A reduced page is arithmetic conformance
evidence; it does not establish the global gap, factor caps or production
admission. The package receipt records the particular observations and
controls actually run. Those observations do not prove the quantified
inequalities above, and their observed error is not a fitted bound.

Credit Jose Manuel / `jmbarrancoml` for the unchanged PR3851 producer/solver
and its claimed scalar error allowance; Chafik Boukhalfa / PR489 and the
retained RaD (`hipotures`), Gaussian, word and manuscript lineage; and
James Reed's [factor-perturbation-margin](../factor-perturbation-margin/README.md)
for the already-covered scalar perturbation/growth comparisons. That note
explicitly leaves the product-inverse cap and actual Core outside its scope.
JoyboyBrian's PR5081 identifies the local-defect handoff, and
[PR5059](../physical-boundary-pages/README.md) explicitly separates original
S from `LU(round(S))`. Its inverse-block ABI is different and is not installed
here. The #4100 uniform-transfer discussion supplies broader motivation,
not the definition of this scalar program or a newly accepted global premise.

This note retains exact primitive and stored-width correctness; original
Gaussian coefficient, global gap, bandwidth and factor-growth proofs;
the interior q-model/old-H comparison; both interior applications and
coupling errors; locality, H-to-N resolvent and normalization; tensor/chirp,
CRT recovery, all physical costs and complete supplier admission. It proves
one conditional scalar boundary bridge, not all of #5081 OQ1 or the complete
multiplication theorem. No selected-frontier, algorithm or precision change
is made. Prepared by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex
assistance. Apache-2.0; no independent human or proof-kernel acceptance claimed.
