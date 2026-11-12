# A shifted sufficient threshold for the one-step comparison

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Statement

Let `d0,a,b` be positive integers, and put `D=d0*b`. Define

```text
T(a,D) = 1                                    if a>D,
         max(2, ceil((3D-a)/(2a)))             if a<=D.
```

For every integer `m>=T(a,D)`,

```text
(m+1)^D < 2^a m^D.                                      (1)
```

Moreover, `T(a,D)<=ceil(27D/(17a))` for every positive integer `a,D`.
At `(d0,a,b)=(1,1,5)` the new sufficient threshold is the exact minimum
`7`, whereas the cited #7450 sufficient threshold is `8`. At `(1,2,5)`
both sufficient thresholds are the exact minimum `4`.

This is a new application of a classical elementary analytic inequality.
No novelty is claimed for that inequality or for logarithmic differentiation.
The general sufficient threshold is not claimed to be an exact minimum.

## The shifted power inequality

For real `x>0`, put `F(x)=(2x+1) log(1+1/x)`, using natural logarithms.
Differentiation gives

```text
F'(x) = 2 log(1+1/x) - (2x+1)/(x(x+1)).
```

The function `t -> 1/t` is strictly convex on the positive real axis.
On `[x,x+1]` its graph is strictly below the secant except at the endpoints.
Integration therefore gives

```text
log(1+1/x) = integral_x^(x+1) dt/t
          < (1/2)(1/x + 1/(x+1)).
```

Consequently `F'(x)<0`. Since `F(1)=3 log 2`, every real `x>1` satisfies
`F(x)<3 log 2`. Exponentiating, for every integer `m>=2`,

```text
((m+1)/m)^(2m+1) < 8.                                  (2)
```

At `m=1` there is equality, not strict inequality. This endpoint is why
the definition of `T` separates `a>D` and requires `m>=2` otherwise.

## Deriving the threshold

Suppose `m>=2` and `a(2m+1)>=3D`. Raise (2) to the positive integer power
`D` and use that exponent inequality:

```text
((m+1)/m)^(D(2m+1)) < 2^(3D) <= 2^(a(2m+1)).
```

Taking a positive `(2m+1)`-st root proves (1). Its hypothesis holds when
`m>=ceil((3D-a)/(2a))`. Thus the stated `T` works when `a<=D`.

If `a>D`, then for every integer `m>=1`, `(m+1)/m<=2`, so
`((m+1)/m)^D<=2^D<2^a`. Therefore `T=1` works in this case.

All inequalities are strict where required. In particular, equality in
`a(2m+1)>=3D` is allowed because (2) is strict for `m>=2`.

## Comparison with the cited bound

The predecessor #7450 supplies `ceil(27D/(17a))` as a sufficient threshold
through a uniform binomial bound and the pair `3^17<2^27`. That predecessor
result is a cited premise, not a replay target. The following comparison is
also an elementary comparison of the two displayed formulas.

When `a>D`, the old ceiling is at least one, so it is at least `T=1`.
When `a<=D`, put `R=D/a>=1`. The old ceiling is at least two, and

```text
27R/17 - (3R-1)/2 = 3R/34 + 1/2 > 0.
```

Ceiling monotonicity then gives

```text
max(2, ceil((3R-1)/2)) <= ceil(27R/17).
```

Hence the new sufficient threshold never worsens that cited threshold.

## The two sharp examples

For `D=5,a=1`, the new value is `ceil(14/2)=7`. At its predecessor,

```text
7^5 = 16807 > 15552 = 2*6^5.
```

Thus (1) fails at `m=6`. The theorem proves (1) for every `m>=7`;
directly, `8^5=32768<33614=2*7^5`. This makes seven the least integer
threshold valid for all subsequent integers at this triple.

For `D=5,a=2`, the new value is `ceil(13/4)=4`. At its predecessor,

```text
4^5 = 1024 > 972 = 4*3^5.
```

The theorem proves (1) for every `m>=4`; directly,
`5^5=3125<4096=4*4^5`. Thus four remains the exact threshold.

These examples do not make the general formula an exact minimum. For
`D=10,a=1`, it gives fifteen, but (1) already holds at fourteen because
`15^10=576650390625<578509309952=2*14^10`.

## Persistence at the retained comparison

Section 6 of the #7000 application review considers a fixed constant
`C>=1`, an integer degree `d0` and positive rational slack `delta=a/b`.
For positive `d0`, raising its comparison to the power `b` gives

```text
P(j): C^b (j+1)^D <= 2^(aj),       D=d0*b.
```

If `P(j)` holds and `j+1>=T(a,D)`, apply (1) at `m=j+1`:

```text
C^b (j+2)^D < 2^a C^b (j+1)^D <= 2^(a(j+1)).
```

Thus `P(j+1)` holds, and induction proves `P(k)` for every integer `k>=j`.
When `d0=0`, this persistence is immediate without a threshold lemma.
This establishes a smaller sufficient one-step region. It does not supply
an initial `j` satisfying `P(j)`, compute any complete selected cutoff,
or replace the other conditions in the review.

## Evidence and limits

The universal claims above follow from the written argument. The verifier
corroborates (2) for `m=2..256`, and decreasing `F` at consecutive integers
for `m=1..255` by exact cross-multiplication. It checks both threshold
formulas for every `a,D=1..96`, and checks (1) at each new threshold and
the next two integers. These are bounded finite checks of this new result.
They do not replay a predecessor verifier or establish the analytic proof
by enumeration. All arithmetic in the verifier is exact integer arithmetic.

The comparison is an auxiliary threshold lemma, not a physical supplier,
a new kappa, or a complete multiplication theorem. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

Can an elementary rational correction to the shifted bound remove the
remaining sufficient-versus-necessary gap, such as fifteen versus fourteen
at `D=10,a=1`? A first step is an explicit upper bound for
`log(1+1/m)` with one more rational term and a proof that the resulting
integer test is no worse. This may reduce the auxiliary persistence region;
it does not determine the initial selected cutoff or settle physical costs.
