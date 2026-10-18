# Three directed-rounding reciprocal guard bits

This is a written quantified theorem with exact finite corroboration. It is not
a Lean theorem or a physical tape implementation. Section 09 is a downstream
corollary, not a dependency of the selected multiplication construction.

The retained manuscript proves reciprocal correctness using five fractional
guard bits. Hanson Sun's (@bbMisk) PR1528 independently checks that routine
through precision eight and asks for an all-precision proof. Here we retain the
actual directed rounding signs and prove that three suffice. No frozen source
is modified. Classical Newton iteration and the manuscript retain credit.

## Quantified one-step lemma

For every real `c` with `1 <= c < 2`, real `x` with
`|epsilon|=|1-cx| <= 1/2`, and integer `t >= 1`, set

```
delta = 2^-t
R_t(z) = 2^-t floor(2^t z)
c_t = R_t(c)
u = R_t(c_t x)
x_plus = R_t(x(2-u)).
```

Then `x>0`, `cx <= 3/2`, and `cx^2 = (1-epsilon)^2/c <= 9/4`.
Write `h=c-c_t`, `a=c_t x-u`, and `b=x(2-u)-x_plus`.
All three are in `[0,delta)`. Exact expansion gives

```
epsilon_plus = epsilon^2 - c h x^2 - cx a + c b.
```

The separate directed bounds are therefore

```
epsilon^2 - (15/4) delta < epsilon_plus < epsilon^2 + 2 delta.
```

The lower bound uses `cx^2+cx <= 15/4`; the upper uses `c<2`.
Both discarded terms have their correct signs. The lower absolute error need
not add the positive `epsilon^2`. A symmetric estimate loses this information.

## Uniform capped-doubling induction

For every integer target `p>=1`, use the source seed `x=5/8` and one step
at `t=6`. Its initial residual has absolute value at most `3/8`. The lemma gives

```
-15/256 < epsilon_plus < 9/64 + 2/64 = 11/64 < 1/4.
```

This establishes `|epsilon| <= 2^-(m+1)` at `m=1`. While `m<p`, let
`m_prime=min(2m,p)` and use `t=m_prime+3`. For every state satisfying the
invariant, the upper bound is

```
epsilon_plus < 2^-(2m+2) + 2*2^-(m_prime+3)
             <= (1/4 + 1/4)*2^-m_prime = 2^-(m_prime+1).
```

The lower bound is

```
epsilon_plus > -(15/4)*2^-(m_prime+3)
             = -(15/32)*2^-m_prime > -2^-(m_prime+1).
```

Every step preserves the invariant against the **true** input `c`, although
its prefix changes. The strictly increasing capped schedule terminates at `p`.
Thus for every real `c in [1,2)` and integer `p>=1`, the candidate returns
a positive dyadic `x` with

```
|1-cx| < 2^-(p+1),     |x-1/c| < 2^-(p+1).
```

At `p=1` the warm-up supplies the conclusion. The second inequality follows
by dividing the residual by `c>=1`. Stored iterates remain exact: the six-bit
warm-up value is not truncated when the first candidate stage uses five bits.
Its exact product is formed before the stated rounding; a constant extra
significand bit suffices at that stage.

The checker's normalized upper-slack identity is

```
1/2 - v*s^2/4 - c/8
 = (1-v)/4 + v*(1-s^2)/4 + (2-c)/8,
```

where `v=2^-(2m-m_prime) in (0,1]` and
`s=epsilon/2^-(m+1) in [-1,1]`. Its last summand is positive. This is exact
algebraic corroboration, not a kernel proof of the quantified premises.

## Sharpness for propagation from the stated invariant

Three is the least nonnegative integer guard allowance for **every** dyadic
state satisfying the retained invariant. At `m=1`, `m_prime=2`, take
`c=11/8`, `x=35/64`. The initial residual is `127/512<1/4`. With two guards
(`t=4`), `c_t=11/8`, `u=3/4`, `x_plus=5/8`; residual `9/64` exceeds `1/8`.
One guard gives the same output. For zero guards, the distinct fixture
`c=1`, `x=49/64` has initial residual `15/64<1/4`, but `t=2` returns
`x_plus=3/4` with residual `1/4>1/8`.

These witnesses are representable on the warm-up grid, but they are **not**
the corresponding actual warm-up outputs. At `c=11/8` that output is `45/64`.
Therefore this does not prove the seeded two-guard routine fails or that three
is its optimal guard count. A stronger reachable-state invariant may permit
fewer bits; that question remains open.

## What the finite certificate establishes

For targets `p=1,...,8`, a common input cell of width
`2^-max(6,p+5)` fixes every original-input prefix read by the five-guard
baseline and three-guard candidate. All operations are constant on each cell.
The checker compares complete traces from separately written rational and
integer-significand implementations, checking residuals at both cell endpoints
and each intermediate target. Affinity in `c` covers every real input in each
tested cell, including nondyadic inputs. The excluded upper endpoint is checked
conservatively. These finite checks corroborate the preceding uniform proof;
they do not establish arbitrary-precision induction by enumeration.

## Downstream effect and remaining obligations

Only the reciprocal's post-warm-up product precision falls by two fractional
bits. The calls, seed, normalization, exact-product semantics and changing
prefix convention remain. This is a sufficient precision refinement, not a
measured speedup or a kappa change. The root routine's outer five-guard schedule
is outside this theorem.

Integration into root calls still needs source/caller binding and a complete
numerical and final-recovery replay. A kernel-checked rounding/induction theorem,
literal tape execution, head-return and uniform cost proofs, and the selected
supplier/compiler/analytic obligations remain separate.

Prepared for @ToikY with substantial OpenAI Codex assistance. Apache-2.0.
