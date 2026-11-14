# Exact outward slack from affine periods and sum fibers

## Scope and notation

All norms below are Euclidean. A supremum is over an unbounded integer lattice;
no finite input cutoff is implicit. The pair specialization uses
`G = Z[i]`, identifies `G^2` with `Z^4`, and uses the norm
`||(x,y)||^2 = |x|^2 + |y|^2`.

## Full-rank affine-period theorem

Let `U` be a rational orthogonal `d x d` matrix, `F: Z^d -> Z^d`, and
`Lambda <= Z^d` a full-rank sublattice. Suppose

```text
F(x + lambda) = F(x) + U lambda   for all x in Z^d, lambda in Lambda.
```

Then

```text
sup_x (||F(x)|| - ||x||)
    = max_[x] in Z^d/Lambda ||F(x) - Ux||.
```

Proof. Put `e(x)=F(x)-Ux`. The period law makes `e` constant on each
coset. The quotient is finite because `Lambda` has full rank. On a coset with
error `e`, orthogonality and the triangle inequality give

```text
||F(x)|| - ||x|| = ||Ux+e|| - ||Ux|| <= ||e||.
```

If `e=0`, this bound is attained as equality. Otherwise `v=U^T e` is a
nonzero rational vector. Choose an integer `q>0` clearing its denominators and
an integer `m>0` with `m Z^d <= Lambda`; then `lambda=m q v` belongs to
`Lambda`. For a coset representative `x0`, set `xn=x0+n lambda`. Since
`U lambda=m q e`,

```text
||F(xn)|| - ||xn||
 = ||Ux0 + (n m q + 1)e|| - ||Ux0 + n m q e|| -> ||e||.
```

Thus each coset supremum is its error norm, and the finite quotient turns the
supremum over all inputs into the stated maximum. No injectivity, inverse,
nonexpansion, or rounding rule is assumed. Full rank, orthogonality, an
unbounded domain, and the affine-period identity are substantive hypotheses.

Rationality of `U` may be retained as a convenient hypothesis, but follows
from the others: for an integer basis matrix `B` of `Lambda`, the period law
implies `UB=F(x+B)-F(x)` has integer columns, so `U=(UB)B^-1` is rational.

## The entire bounded-center pair family

Fix `sigma` in `{+1,-1}` and any bounded center rule `c: G -> G` satisfying
the exact output-parity condition

```text
Re(c(s)) + Im(c(s)) = Re(s) + Im(s)  (mod 2).
```

This is the legal-center condition proved in #6509. For `s=x+y` and `d=x-y`,
define the ideal orthogonal pair operator and the rounded map by

```text
C_sigma(x,y) = ((s + sigma*i*d)/2, (s - sigma*i*d)/2)
F_(c,sigma)(x,y)
    = ((s + sigma*i*d + (1-sigma*i)c(s))/2,
       (s - sigma*i*d - (1-sigma*i)c(s))/2).
```

`C_sigma` fixes the sum and multiplies the difference by `sigma*i`; its
adjoint is `C_-sigma`. On the fiber with sum `s`, the error is constant:

```text
e_s = ((1-sigma*i)c(s)/2, -(1-sigma*i)c(s)/2),
||e_s|| = |c(s)|.
```

The fiber is an affine copy of the full-rank tangent lattice
`T={(z,-z): z in G}`. Define

```text
lambda_s = 2 C_sigma^* e_s
         = (-(1+sigma*i)c(s), (1+sigma*i)c(s)).
```

This is an integral Gaussian pair with sum zero, and `C_sigma lambda_s=2e_s`.
For every fixed `s`, the triangle inequality bounds the fiber's outward norm
increment by `|c(s)|`. If `c(s) != 0`, take any `X0` on the fiber and
`Xn=X0+n lambda_s`. Then

```text
C_sigma Xn = C_sigma X0 + 2n e_s,
F_(c,sigma)(Xn) = C_sigma X0 + (2n+1)e_s,
```

so the fiber supremum is exactly `|c(s)|`. For `c(s)=0`, the map is
orthogonal on that fiber and the same value zero holds. Taking the supremum
over all sums gives the exact family formula

```text
sup_(x,y) (||F_(c,sigma)(x,y)|| - ||(x,y)||) = sup_s |c(s)|.
```

This is a fiberwise argument; the center may depend on `s` and need not make
the full map affine-periodic on one global full-rank lattice.

For every legal rule, an odd-parity sum such as `s=1` requires
`Re(c)+Im(c)` odd. Thus `c(s)` is nonzero there and `|c(s)| >= 1`; no legal
rule has uniform outward slack below one. #6509's rule has `c=0` on even
parity sums and chooses a Gaussian unit on odd parity sums, so it attains
`sup_s |c(s)|=1`. The minimum outward slack over the whole bounded-center
family is therefore exactly one, independent of the sign `sigma`.

## Exact ray for the retained #6509 kernel

For `sigma=+1`, `s=1`, and the source rule's `c(1)=1`, the base point
`X0=(1,0)` has the legal tangent increment `lambda_1=(-(1+i),1+i)`. At
integer `t>=0`,

```text
Xt = (1-t-it, t+it),
F(Xt) = (1+t-it, -t+it),
||Xt||^2 = 4t^2 - 2t + 1,
||F(Xt)||^2 = 4t^2 + 2t + 1.
```

For `t>=1`, let `g_t=||F(Xt)||-||Xt||`. Then

```text
g_t = 4t / (sqrt(4t^2+2t+1) + sqrt(4t^2-2t+1)),
(32t^2-2)/(32t^2+1) < g_t < 1.
```

For the lower bound, put `a=2t+1/2` and `b=2t-1/2`. For positive `z`,
`sqrt(z^2+3/4) < z+3/(8z)`. Hence the denominator above is strictly less
than `4t + 6t/(16t^2-1)`, which gives the displayed lower bound. For the
upper bound, `4(4t^2-2t+1) > (4t-1)^2`, so
`2 sqrt(4t^2-2t+1)+1 > 4t`, equivalent to `g_t<1`.

There is also a closed-unit-ball witness at every dyadic scale. Put
`h=2^-p`, `t=2^(p-1)` for integer `p>=1`, and interpret the integer-grid
kernel inputs and outputs multiplied by `h`. The exact squared norms are

```text
input:  1 - h + h^2 <= 1,
output: 1 + h + h^2 > 1.
```

The executable check below runs the unchanged integer-grid kernel on finite
members of both witness families. The all-size conclusions above follow from
the algebra, not from these runs.

## Source-bound consequences and limits

The exact #6534 two-axis map has a full-rank affine period relative to its
unitary ideal map and sharp uniform error `sqrt(2) h`; the theorem therefore
identifies its outward norm supremum as `sqrt(2) h`. The exact #6536
three-axis matched-coset map has its full-rank source-class period and sharp
uniform error `2h`; its outward norm supremum is `2h`. These are corollaries
of the pinned source theorems, not fresh table or matching checks.

The #6438 five-seed rotation has period `5 Z^2` relative to the rational
orthogonal matrix `[[3,-4],[4,3]]/5`. Its source proves error at most
`sqrt(4/5)` for every seed/input and states that this deterministic bound is
attained by the construction. The lemma therefore gives exact worst outward
slack `sqrt(4/5)` across the five maps; this does not assert that every
individual seed attains that value. The #6758 native theorem similarly gives
sharp forward and inverse error `sqrt(8)` and a full-rank forward period
`Gamma`. For the inverse, `U Gamma` is an integral full-rank lattice: the
forward period law and integer-valued F imply `U lambda` is integral, and
bijectivity gives `F^-1(y+U lambda)=F^-1(y)+lambda`. Applying the theorem to
F and to its inverse relative to `U^*` gives forward and inverse outward
slack `sqrt(8)`. These uses inherit the pinned source results; this package
does not recheck their tables, certificates, or full implementations.

This does not answer #6619's unrestricted outward-slack optimization and
does not imply a positive minimum for every reversible integer-output map.
For a translation `lambda=(a,b)` with sum `u=a+b`, the pair formula gives
`F(X+lambda)-F(X)=C_sigma lambda + e_(s+u)-e_s`. Thus a global period
identity for this translation requires `c(s+u)=c(s)` for every `s`. The
actual #6509 sign-based center has no nonzero additive period: if the
real-plus-imaginary parity of `u` is odd, use `s=0`, where `c(s)=0` but
`c(s+u)` is a Gaussian unit; if both coordinates of `u` are odd, use
`s=1`, where the center changes from `1` to `i` or `-i`; if both are even
and `u != 0`, choose an odd real (respectively imaginary) coordinate `+1`
or `-1` whose sign is reversed by the nonzero real (respectively imaginary)
part of `u`, with the other coordinate zero. In that last case the center
changes from `+1` to `-1` or vice versa, or from `+i` to `-i` or vice versa.
For example, the equal-coordinate shift `(-1,-1)` changes the center from
`c(1)=1` to `c(-1)=-1` and fails the global affine-period identity. A full-rank
period lattice cannot lie wholly in the rank-two sum-zero subspace, so this
source map is not globally affine-periodic on a full-rank lattice. The
fixed-sum fiber argument is precisely why the #6509 result remains valid
without a global period premise.

No new kernel, physical tariff, component guard, selected `kappa`, or
unrestricted optimality result is claimed. The finite kernel replay tests the
retained center rule only; the universal bounded-center theorem is proved by
the formulas above.
