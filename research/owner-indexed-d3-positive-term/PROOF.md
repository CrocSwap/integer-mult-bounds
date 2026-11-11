# No D-exponent (0, 1) correction clears the sharp x1 column

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged.

Evidence class: **proof** in the predecessor's formal algebra, under the
hypotheses below. The coefficient `u0` ranges over every finite-support
element of the rational group algebra. This is not an enumeration of words,
not a bounded search, and not a theorem about every quotient or every
owner-mixing map.

## Object

Use the published two-edge feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md),
replayed by `search.replay(one, C1 Q^2)`. The sharp index is the one
recorded by open PR #7033 and used by open PR #7052:

```text
const = -Q^{-1} + Q^{-1} C1 Q C1
m0 = const C1 = -Q^{-1} C1 + Q^{-1} C1 Q
m1 = 0
m2 = Q^{-1} C1 Q^2 C1 Q
m3 = 0
x = Q^2 (I + Q) C1 Q = Q^{-1} C1 Q + Q^2 C1 Q
```

`verify.py` recomputes the fresh image from the replay. It does not import
the unmerged packages. That image has `x0 = A = D1 Q^{-1}`, `y0 = 0`,
`y1 = 0`, and

```text
x1 = R = ρ D1 D3,    ρ = Q^{-1} C1 Q^2 C1 C3.
```

Letters are `1 = Q`, `-1 = Q^{-1}`, `2 = C1`, and `3 = C3`. The algebra is
`search.algebra()`: the rational group algebra of the free product
`C4(Q) * C2(C1) * C2(C3)`, formal D exponents, and `D_i` conjugating only
`C_i` by `Q^{-1}`. Distinct D exponents are basis labels. No relation
`D^4 = I` is imposed. Elements have finite support. Degree `(a, b)` means
the basis label `D1^a D3^b`.

An owner index reads the four stored banks and does not write them. A
D-exponent `(0, k)` correction of the sharp index is a fresh image

```text
S = sum_b (sharp_b + u_b D3^k) · bank b,
```

where each `u_b` has D-exponent `(0, 0)`. The assigned question is `k = 1`,
with two or more of the `u_b` allowed to be nonzero. One homogeneous term
on one bank is already blocked for every degree by the monomial gate of
#7052. That gate is not reproved here. The D-exponent-0 obstruction of
#7033 and the D-exponent `(0, -1)` obstruction of #7052 are not reproved
here either.

## Replayed columns used below

`verify.py` checks these columns against the replay. Banks 0, 1, and 2
have no `C3` in `x0`, `y0`, or `y1`. Bank 1 has empty `x0`, `x1`, and `y1`.
Every `y1` column of banks 0, 1, and 2 is empty.

```text
bank 0, all at degree (1, 0):
  x0 = Q^{-1} C1 + Q^2 C1
  y0 = Q^{-1}
  x1 = -Q^2 C1
bank 2:
  x0 = Q^{-1}                         degree (1, 0)
  y0 = Q^{-1} C1 Q - Q^{-1} C1 Q^2    degree (1, 0)
  x1 = -Q^{-1} + Q^{-1} C1 Q C1       degree (1, 0)
       + Q^{-1} C3                    degree (1, 1)
bank 1, degree (1, 0):
  y0 = C1 Q
bank 3, all at degree (1, 1):
  x0 = C3 Q^{-1} C1
  y0 = C3
  x1 = -I - C3 Q^{-1} C1 + C3 C1
  y1 = C3 Q
```

Left multiplication by `D3^k` adds `(0, k)` to every degree. It fixes `Q`
and `C1`. It replaces each `C3` by `Q^{-k} C3 Q^k`. Consequently every
`C3`-free column is only relabelled by degree, and `x` and `C1` commute
with every power of `D3`.

## Right units

On normal words, right multiplication by `Q` adds `1` mod `4` to the final
Q exponent and fixes the prefix. The four normal forms `I`, `Q`, `Q^2`,
and `Q^{-1}` are distinct, so this map is bijective of order `4`. Right
multiplication by `C_i` deletes a final `C_i` or appends one, and it is an
involution. A degree-0 monomial with nonzero rational coefficient is
therefore a two-sided unit, and right multiplication by it is a linear
automorphism of the rational group algebra.

The same holds for a monomial of nonzero D degree: the degree shift is a
bijection of `Z^2`, and the word map is right multiplication by one fixed
group element. In particular `C1`, `Q`, `Q^2`, `Q^{-1}`, and every reduced
word are units, and `C1^2 = I`. The syllable-length-4 replay in `verify.py`
is a control for this fold, not a census of `u0`.

Right multiplication by `Q` is free: `w Q^j = w` implies `Q^j = I`. Every
right orbit `{w, wQ, wQ^2, wQ^3}` therefore has four distinct words, and
these orbits partition the group.

## The boundary family

Write `T_b` for left multiplication of bank `b` by `D3^k`. Bank 3's `x0`
and `y0` transports are single monomials at degree `(1, 1+k)`. Banks 0, 1,
and 2 contribute to `x0` and `y0` only at degree `(1, k)`. These degrees
differ. The sharp `x0` column is `A` at degree `(1, 0)` only, and the sharp
`y0` column is zero. For `k ≠ 0`, neither correction degree equals `(1, 0)`
except the bank-3 degree when `k = -1`. In every nonzero case the bank-3
monomial is the only correction term on its degree, so that term vanishes
if and only if

```text
u3 = 0.
```

The degree-`(1, k)` equations are the same word equations for every `k`,
because those columns contain no `C3`. With `p = Q^{-1} C1 Q`,
`r = Q^2 C1 Q`, and `s = Q^{-1} C1 Q^2`,

```text
x = p + r,    T_{2,x0} = Q^{-1},    T_{0,x0} = x Q^{-1},
T_{2,y0} = p - s,    T_{1,y0} = C1 Q,    T_{0,y0} = Q^{-1}.
```

The products `p^2 = I`, `r p = Q^{-1}`, `p s = Q`, and `r s = I` give

```text
x T_{2,y0} = Q^{-1} - Q,    C1 T_{1,y0} = Q,
```

hence `T_{0,y0} = C1 T_{1,y0} + x T_{2,y0}`. Both `x` and `C1` have degree
0, so they associate with a later factor: `(u z) g = u (z g)`. Therefore

```text
(u0 x + u2) T_{2,x0} = 0,    (u0 C1 + u1) T_{1,y0} = 0.
```

The gates `Q^{-1}` and `C1 Q` are monomial units, so every boundary-preserving
correction has

```text
u2 = -u0 x,    u1 = -u0 C1,    u3 = 0.
```

Conversely, every such tuple keeps `x0 = A` and `y0 = 0`. Banks 0, 1, and
2 have zero `y1` transport and `u3 = 0`, so `y1` stays zero as well. The
question does not require that last column; the family keeps it.

Since bank 1's `x1` column is empty,

```text
S_x1 = R + u0 Δ_k,    Δ_k = T_{0,x1} - x T_{2,x1}.
```

The `C3`-free part of this defect does not depend on conjugating `C3`. The
same expansion as below gives, at degree `(1, k)`,

```text
Δ_k = -C1 + (a degree-(1, 1+k) element).
```

## Only exponent 1 meets the residual degree

The raw `x1` supports are degrees `(1, 0)` on banks 0 and 2, degree `(1, 1)`
on the `C3` term of bank 2 and on all three terms of bank 3, and empty on
bank 1. Adding `(0, k)` lands on degree `(1, 1)` only for `k = 1` (from
degree `(1, 0)`) or `k = 0` (from degree `(1, 1)`). Cancellation inside a
column can delete terms. It cannot move a term onto another D degree.

Thus, for every integer `k ∉ {0, 1}` and every coefficient tuple, not only
the boundary family, the degree-`(1, 1)` part of `S_x1` equals `R`. In
particular `S_x1` is not zero. The case `k = -1` is the support gap proved
in #7052. The column supports above are the same gap for every other such
`k`. The boundary analysis and the witness charge of #7052 are not repeated.
The case `k = 0` is the D-exponent-0 obstruction of #7033 and is excluded
here. `verify.py` checks the raw supports and checks the shifted supports
on a finite set of powers. That finite set is a control. The argument is
the support count.

## The exponent-(0, 1) defect

For `k = 1`, bank 0 contributes `T_{0,x1} = -Q^2 C1` at degree `(1, 1)`.
Bank 2 contributes

```text
T_{2,x1} = -Q^{-1} + Q^{-1} C1 Q C1    at degree (1, 1)
           + Q^2 C3 Q                   at degree (1, 2).
```

The degree-`(1, 2)` word is the conjugate of `Q^{-1} C3`: the leading
`Q^{-1}` stays, and `C3` becomes `Q^{-1} C3 Q`, so
`Q^{-1} Q^{-1} C3 Q = Q^2 C3 Q`.

On the degree-`(1, 1)` line,

```text
x Q^{-1} = Q^{-1} C1 + Q^2 C1,
x (Q^{-1} C1 Q C1) = C1 + Q^{-1} C1,
x (-Q^{-1} + Q^{-1} C1 Q C1) = C1 - Q^2 C1.
```

Subtracting from `T_{0,x1}` leaves `-C1`. On the degree-`(1, 2)` line,

```text
x (Q^2 C3 Q) = Q^{-1} C1 Q^{-1} C3 Q + Q^2 C1 Q^{-1} C3 Q
             = (Q^{-1} + Q^2) C1 (Q^{-1} C3 Q).
```

Hence

```text
Δ_+ = -C1
      - (Q^{-1} + Q^2) C1 (Q^{-1} C3 Q),
```

with the first summand at degree `(1, 1)` and the second at degree `(1, 2)`.
Also `Q^{-1} + Q^2 = Q^2 (I + Q)` and
`x = (Q^{-1} + Q^2) C1 Q`, so the right kernel of `x` equals the right
kernel of `I + Q`.

## No coefficient kills both degrees

The two D degrees of `R + u0 Δ_+` separate.

The degree-`(1, 1)` component is `ρ - u0 C1` at that degree. Right
multiplication by `C1` is a linear automorphism, so there is exactly one
solution,

```text
u0 = ρ C1 = Q^{-1} C1 Q^2 C1 C3 C1.
```

Call this monomial `u_*`. It is one basis element, with coefficient `1`.

The degree-`(1, 2)` component is `-u0 (Q^{-1} + Q^2) C1 (Q^{-1} C3 Q)`.
The last two factors are monomial units, so the component is zero if and
only if `u0 (Q^{-1} + Q^2) = 0`. Since `Q^{-1} + Q^2 = Q^2 (I + Q)`,
this says `(u0 Q^2) (I + Q) = 0`. If `u (I + Q) = 0`, then `u Q = -u`,
so `u Q^2 = -(u Q) = u`, and therefore `u (Q^{-1} + Q^2) = 0`. Conversely,
if `(u Q^2) (I + Q) = 0`, set `v = u Q^2`. Then `v Q = -v`, hence
`v Q^2 = -(v Q) = v`. But `v Q^2 = u`, so `u (I + Q) = 0`. The four
conditions

```text
u (Q^{-1} + Q^2) = 0
u Q^2 (I + Q) = 0
u (I + Q) = 0
u Q = -u
```

are equivalent. The last equation forces coefficients `(c, -c, c, -c)` on
every right `Q`-orbit. Over the rationals, a nonzero value on an orbit
occupies all four words. Distinct orbits are disjoint, so every nonzero
solution has support size divisible by 4.

The monomial `u_*` has support size 1, so `u_* (I + Q) ≠ 0`. Explicitly,
`u_*` and `u_* Q` are distinct reduced words, and both coefficients are
`1`. Therefore `u_* Δ_+` has nonzero degree `(1, 2)`. Every other `u0`
leaves a nonzero degree-`(1, 1)` component.

So `R + u0 Δ_+` is never the zero element. Every boundary-preserving
D-exponent `(0, 1)` correction, including every correction that uses two
or more banks, leaves a nonzero fresh `x1` column.

## The two-bank subfamily and the three-bank near-miss

`u2 = -u0 x` does not force a third bank. If `u0 (I + Q) = 0`, then
`u0 x = 0`, so `u2 = 0`, while `u1 = -u0 C1` is nonzero whenever `u0` is
nonzero. The resulting correction uses exactly banks 0 and 1. It kills the
degree-`(1, 2)` defect and leaves

```text
S_x1 = (ρ - u0 C1) D1 D3,
```

which is zero only for `u0 = u_*`. That monomial is not anti-invariant
under `Q`. The witness

```text
σ = I - Q + Q^2 - Q^3
```

has `σ (I + Q) = 0` and support size 4. Then `u1 = -σ C1` has support
size 4, and `S_x1` has five monomials at degree `(1, 1)`, including `R`
with coefficient `1`. The algebraic charge of this two-bank witness is
those eight multiplier monomials, each times `D3`, together with the five
image monomials. No scalar-field minimum and no tape cost are claimed.

Separately, `u_*` is the unique element that clears degree `(1, 1)`. It
uses three banks:

```text
u0 = Q^{-1} C1 Q^2 C1 C3 C1
u1 = -ρ = -Q^{-1} C1 Q^2 C1 C3
u2 = -u_* x
   = -Q^{-1} C1 Q^2 C1 C3 C1 Q^{-1} C1 Q
     -Q^{-1} C1 Q^2 C1 C3 C1 Q^2 C1 Q
u3 = 0.
```

Those are four multiplier monomials, each times `D3`. The fresh `x1`
column is the two degree-`(1, 2)` monomials

```text
-Q^{-1} C1 Q^2 C1 C3 C1 Q^{-1} C1 Q^{-1} C3 Q
-Q^{-1} C1 Q^2 C1 C3 C1 Q^2 C1 Q^{-1} C3 Q.
```

`R` is absent. The column is not zero. The charge of this near-miss is
the four multiplier monomials together with these two image monomials.
There is no solution, so there is no solution support to charge. These two
witnesses are the two obstructions: anti-invariants clear degree `(1, 2)`
and leave degree `(1, 1)`, and `u_*` clears degree `(1, 1)` and leaves
degree `(1, 2)`.

One nonzero bank cannot satisfy the closed form. `u3 = 0` already. If
`u0 = 0`, then `u1 = u2 = 0`. If `u1 = 0` or `u2 = 0` while the other
data match the closed form, then `u0` is respectively zero or
anti-invariant, and the remaining equation still fails as above. This is
the monomial gate of #7052 specialized to exponent `(0, 1)`. The general
gate is not reproved.

## A second boundary-preserving power does not repair the near-miss

Let `N` be the fresh image of `u_*` at exponent `(0, 1)`. Let `C` be any
boundary-preserving correction of exponent `(0, m)` with `m ≠ 1`, and let
`v0` be its free coefficient. The sum is `sharp + (u_* correction) + C`,
so the sharp column `R` is counted once. Its degree-`(1, 1)` part is zero
because `C` contributes nothing there. The degree-`(1, 2)` part of `N` is
the two-monomial element above, written `L`.

`C` contributes `v0 Δ_m`, supported on degrees `(1, m)` and `(1, 1+m)`.
Those degrees meet `(1, 2)` only for `m = 2`. For every other `m`, `L`
survives. For `m = 2`, the same expansions give

```text
Δ_2 = -C1
      - (Q^{-1} + Q^2) C1 (Q^2 C3 Q^2),
```

at degrees `(1, 2)` and `(1, 3)` respectively. Both `C1` and
`Q^2 C3 Q^2` are monomial units, so the degree-`(1, 3)` component vanishes
if and only if `v0 (I + Q) = 0`. The degree-`(1, 2)` component is then
`-v0 C1`, whose support size equals the support size of `v0`. A nonzero
anti-invariant has support size divisible by 4, while `L` has support
size 2. The zero coefficient leaves `L`. Therefore `N + C` is never zero
on `x1`.

In particular, no sum of two boundary-preserving single-power corrections
clears `x1`. If neither power equals 1, the degree-`(1, 1)` part remains
`R`. If both equal 1, the sum is one exponent-`(0, 1)` correction.

## What is not proved

Coefficients at two powers that preserve the boundary only jointly are
outside this statement. Power 1 places bank 3 at degree `(1, 2)`, which is
the degree of the power-2 contribution from banks 0 and 2, so those terms
can cancel each other. No such pair is solved here.

Owner-mixing maps, a feedback edge other than `(I, C1 Q^2)`, and a
physical relation that identifies distinct D exponents are outside this
statement. The omitted relation `D1^4 = I` is open PR #7056 and is not
taken. In a quotient that moves one of the surviving degrees onto another,
a formally nonzero column could become zero. No such quotient is proved
here. The result is not an autonomous decoder, not a new caller bill, and
not a change of the selected conditional κ.
