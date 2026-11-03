# Sharp common reserve for the PR6472 example

This is a scoped mathematical proof, produced by Nick Petalas.
It answers the common-ratio optimization question posed by Ali Romman in
[PR6472](https://github.com/CrocSwap/integer-mult-bounds/pull/6472), exact head
`6621e59b773b179a0340627eadbe295eb5254d07`. That package supplies the menu,
the adaptive row contract, the exact total `u=(5,3)` and its reserve ratio `4/5`.
Those are credited inputs, not new results of this package.

## Contract and claim

The two type menus are

```text
R_1 = {(0,6/5), (1/5,1)}
R_2 = {(2/5,0), (0,1/4)}.
T(x)_i = max_{r in R_i} r x.
```

For a positive real weight `w=(x,y)`, let `q(w)` be the smallest number such
that `r w <= q(w) w_i` for every row of type `i`. All four rows are retained.
The new exact optimum is

```text
min_{w>0} q(w) = lambda = (1+sqrt(41))/10.
```

Its minimizing weights have the unique ratio
`x/y=(1+sqrt(41))/4`. Consequently no positive rational weight attains the
minimum. A rational certificate `w=(37,20)` gives `q=137/185 < 4/5`.

For the finite-depth adaptive unit-toll totals
`x_0=0`, `x_{d+1}=1+T(x_d)`, this certificate gives

```text
0 <= u-x_d <= (137/185)^d (111/20,3),
max_i (u_i-x_{d,i})/u_i <= (111/100)(137/185)^d.
```

These are componentwise inequalities. They imply the relative tolerance
`2^-64` at depth 149. The cited `4/5` reserve bound first implies that
tolerance at depth 199. These are exact cutoffs for the two bounds, not a
claim that the actual nonlinear recurrence first meets tolerance at 149.

## Lower bound for every positive real weight

Put `t=x/y>0`. Directly from the four rows,

```text
q(w) = max(6/(5t), 1/5+1/t, 2t/5, 1/4).
```

In particular `q>1/5`, `1/t <= q-1/5` and `t <= 5q/2`.
Multiplying the last two positive inequalities gives
`1 <= (q-1/5)(5q/2)`, hence

```text
5q^2-q-2 >= 0.
```

The polynomial has exactly one positive root, `lambda`, so `q>=lambda`.
This argument quantifies over every positive real weight; the finite
rational-weight checks do not supply this quantifier.

## Attainment and uniqueness

Choose `t=(1+sqrt(41))/4=5 lambda/2`. The equation
`5 lambda^2-lambda-2=0` gives
`1/5+1/t=lambda=2t/5`. Also `t>1`, so
`6/(5t) <= 1/5+1/t`; and `1/4<lambda`. Thus all four rows satisfy the
bound with equality on the two coupled rows.

If `q=lambda`, equality must hold in both inequalities that were multiplied
above. This forces `t=5 lambda/2`. Since 41 is not a square, `t` is irrational.
Positive rational weights therefore cannot attain the optimum. Density and
continuity show that the infimum restricted to rational weights is still
`lambda`.

## Rational certificate and all-depth tail

For `w=(37,20)`, the four row ratios are exactly

```text
24/37, 137/185, 37/50, 1/4.
```

Their maximum is `137/185`. Scaling to `v=(111/20,3)` preserves the ratio,
and `v>=u`. For arbitrary vectors `a,b`, the elementary maximum inequality
and nonnegative rows give

```text
|T(a)_i-T(b)_i| <= max_{r in R_i} r |a-b|.
```

The cited total satisfies `u=1+T(u)`. Starting with `0<=u-x_0=u<=v`, the
displayed inequality proves inductively
`0<=u-x_d<=q^d v` for every integer `d>=0`. Division by `u` gives the
relative bound, since `max_i v_i/u_i=111/100`.

The new componentwise bound is smaller than the cited bound for every `d>=2`.
It suffices to check
`(111/100)(137/148)^2<1`; larger `d` only decrease this expression.
The exact 64-bit cutoff assertions reduce to four rational comparisons:

```text
(111/100)(137/185)^149 <= 2^-64 < (111/100)(137/185)^148,
(4/5)^199 <= 2^-64 < (4/5)^198.
```

The verifier performs these comparisons with integer-backed fractions.

## Credit and scope

Weighted maximum norms, nonnegative matrix theory, and positive-vector
contraction arguments are classical. The selected two coupled rows also
give the classical Perron-root interpretation. No general theorem priority
is claimed. The new contribution is the sharp source-specific reserve
optimization, its rational certificate and the resulting cutoff comparison.
PR6472 retains credit for the row menu, total-bill interface and its proofs.

This synthetic example does not identify a physical supplier menu. Every
actual caller would still need complete child, adapter and restoration
charges, legal independent row choices, native realization, compiler,
storage, precision/tape and outer applicability. All five selected framework
assumptions remain. There is no new kappa or selected-frontier change.
