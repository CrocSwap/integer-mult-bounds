# The sharp direct higher-moment split coefficient

This proof was produced by Nick Petalas. Apache-2.0.

## Theorem

Fix real numbers `0<t<1` and `sigma>1`. For positive integers `R>J`, write
`R=qJ+r`, where `q>=1` and `0<=r<J`, and set

```
split_t(R,J) = q J^t + r^t.
```

There is exactly one `s=s_(t,sigma)` in `(0,1)` satisfying

```
t s^(t-1) + (t-sigma)s^t - sigma = 0.
```

The least coefficient valid for every such integer split is

```
K(t,sigma) = (1+s^t)/(1+s)^sigma
           = (t/sigma) s^(t-1) (1+s)^(1-sigma).

split_t(R,J) <= K(t,sigma) R^sigma J^(t-sigma).
```

It satisfies `1<K(t,sigma)<K(t,1)<2`, where `K(t,1)` is the coefficient
of PR4832. Equality at finite integers occurs exactly when `q=1` and
`r/J=s_(t,sigma)`. The supremum is sharp even when that remainder is irrational.

## Proof

Divide the split charge by `R^sigma J^(t-sigma)` and put `s=r/J`. The ratio is

```
F_q(s) = (q+s^t)/(q+s)^sigma.
```

For a fixed `s` in `[0,1)`, extend `q` temporarily to a real variable `q>=1`.
Its derivative has the sign of

```
(1-sigma)q + s - sigma s^t < 0.
```

Indeed `s<=s^t` and `sigma>1`. Thus every integer `q>1` is strictly worse
than `q=1`. This step retains the denominator's full higher moment, unlike
the linear-rank estimate followed by a separate moment comparison in PR4832.

For `F_1`, the derivative on `(0,1)` has the sign of

```
h(s) = t s^(t-1) + (t-sigma)s^t - sigma,
h'(s) = t(t-1)s^(t-2) + t(t-sigma)s^(t-1) < 0.
```

The function `h` tends to positive infinity at zero and has
`h(1)=2(t-sigma)<0`. It has one zero, and this is the unique maximum of
`F_1` on `[0,1]`. Its stationary equation gives the second expression for K.
Since `F_1(0)=1` and the derivative is positive before that maximum, `K>1`.
At its positive maximizer, division by `(1+s)^(sigma-1)>1` gives
`K(t,sigma)<(1+s^t)/(1+s)<=K(t,1)`. PR4832 supplies `K(t,1)<2`.

For sharpness over integers, let `J` tend to infinity and choose
`r=floor(s_(t,sigma) J)`, `R=J+r`. Eventually `0<r<J`, and continuity makes
the ratio tend to K. Every coefficient smaller than K therefore fails for
some integer split. Strict quotient monotonicity and the unique maximum
also give the stated equality characterization. This proves the theorem.

## An exactly attaining rational-power example

Take `t=1/2`, `sigma=17/10`. Substitution gives `h(1/16)=0`, so

```
s = 1/16,
K = (5/4) (16/17)^(17/10),
K^10 = (5/4)^10 (16/17)^17.
```

Every `J=16n`, `R=17n`, for positive integer n, attains the coefficient.
Exact integer comparisons show `9/8<K<8/7<6/5`. In contrast,
PR4832's cited coefficient `K(1/2,1)=(1+sqrt(2))/2` is greater than `6/5`.
This is a strict improvement of the direct higher-moment coefficient.
It does not by itself specify a realizable productive/paid profile.

## Consequence for retained strictification

Retain every chronological product, native, completion, splitting and compiler
hypothesis of zxv's PR4433, section 2. Let `C=1-t`, `u>C`, `sigma=t+u>1`,
`J=c^v` and `L=b^v`, with `1<c<b<m` and positive integer v. Write `P_x,T_x`
for the raw paid and productive rank moments and B for its productive count.
For every original paid rank R exceeding J, the theorem gives

```
split_t(R,J) <= K(t,t+u) R^(t+u) J^(-u).
```

The predecessor's moment multiplication and its unchanged unsplit overcount
therefore bound the original-paid charge by

```
P_t^v + K(t,t+u) P_(t+u)^v / J^u.
```

Keep its full separate completion bound `2 B^v L J^(-C)` and the lower bound
`T_t^v` on the completed productive moment. The complete sufficient charge is

```
alpha^v + K(t,t+u) gamma_u^v + 2 delta^v,
alpha=P_t/T_t,
gamma_u=P_(t+u)/(c^u T_t),
delta=B b/(c^C T_t).
```

This strictly lowers the coefficient `K(t,1)` in PR4832 whenever `u>C`.
The completion coefficient, unsplit overcount and all realization premises
are retained. No particular inventory, tensor power or admitted supplier is
certified here. The direct compiler of zxv's PR4483 can avoid strictification
for profiles satisfying its own gates; this result makes no comparison to
that compiler's sufficient sizes.

## Exact finite certificate

For rational `t=a/b`, `sigma=c/d`, put `y=s^(1/b)`. The critical equation
becomes the strictly decreasing polynomial

```
ad + (ad-bc)y^b - bc y^(b-a) = 0.
```

The verifier bisects this polynomial using rational arithmetic. At any rational
y, the normalized ratio's d-th power is exactly

```
F_q(y^b)^d = (q+y^a)^d / (q+y^b)^c.
```

Thus its root enclosures, finite split checks and attaining example require
neither floating-point tolerances nor algebraic-number libraries. These checks
corroborate the proof; they are not a universal census or proof-kernel acceptance.
