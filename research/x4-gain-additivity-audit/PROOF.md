# The ideal X4 saving is strictly convex in the number of exchanges

This proof concerns the exact arithmetic family obtained from PR799's
explicit profile changes. It does not assert physical realizability for
nonintegral numbers of exchanges.

## Profile identity

Let e_r denote one child of rank r. Each paired exchange changes the local
profile by -2e_1+e_2. All sixteen subsets of the four exchanges pass the
retained builder's scalar-map and frame checks. Subsets with j paired
exchanges have local profile

```text
{1: 2556-2j, 2: 334+j, 3: 430, 4: 194, 5: 56, 8: 8}.
```

The global price uses 72 copies of this local profile and the fixed idle
profile `{1:1, 3:1, 44:1, 48:2396}`. Consequently

\[
H_t=H_0+t(-144e_1+72e_2),\qquad 0\leq t\leq4,
\]

where the interpolation parameter t is real for the proof. Its coefficients
are positive throughout this interval. The rank mass remains 520704, the
moment width is m=73, and the number of live wires is W=7168. Thus the
rank-mass deficit is mW-520704=2560.

The audit checks the identity at all sixteen actual subsets. It also checks
that the selected j=4 profile equals the committed PLAN profile. The fixed
idle-profile arithmetic does not by itself certify all physical admission
obligations of each intermediate word.

## Moment root

Define

\[
F(a,t)=\frac1{mW}\sum_r H_t(r)r(m/r)^a=P(a)-tD(a),
\]

where P(a)=F(a,0) and

\[
D(a)=\frac{144}{mW}m^a(1-2^{-a}).
\]

The saving a(t) is the solution of F(a(t),t)=1. Each coefficient of H_t is
positive and 0<r<m, so F_a>0. At a=0 the moment is 520704/(mW)<1,
independently of t. The exact endpoint checks put the t=4 root below 0.003.
For a>0, D(a)>0 and F(a,t) is decreasing in t. Hence every t in [0,4]
has a unique root with 0<a(t)<0.003. The implicit-function theorem applies
because F_a>0, and

\[
a'(t)=\frac{D(a(t))}{F_a(a(t),t)}>0.
\]

Differentiating the root equation twice, using F_at=-D' and F_tt=0, gives

\[
\frac{a''(t)}{a'(t)^2}
=2\frac{D'(a(t))}{D(a(t))}
-\frac{F_{aa}(a(t),t)}{F_a(a(t),t)}.
\]

## Strict convexity of ideal κ

For a>0,

\[
\frac{D'(a)}{D(a)}
=\log(m/2)+\frac{\log2}{1-\exp(-a\log2)}
>\frac1a.
\]

The strict inequality follows from 1-exp(-x)<x for x>0 and m/2>1.
Also, F_aa/F_a is a weighted average of the numbers log(m/r), with
strictly positive weights. Therefore

\[
\frac{F_{aa}}{F_a}\leq\log m=\log73<5.
\]

The final elementary bound needs no numerical logarithm evaluation.
The first six terms of the positive series for exp(5) sum to 1097/12>73.

For the ideal saving k(t)=a(t)/(1+a(t)), differentiation yields

\[
k''(t)=\frac{a'(t)^2}{(1+a(t))^2}
\left(2\frac{D'}D-\frac{F_{aa}}{F_a}-\frac2{1+a(t)}\right).
\]

The bracket is strictly greater than 2/a(t)-7, which is positive because
0<a(t)<0.003. Thus k''(t)>0 throughout [0,4]. In particular,

\[
k(j+1)-2k(j)+k(j-1)>0,\qquad j=1,2,3,
\]

and

\[
k(4)-k(0)>4\bigl(k(1)-k(0)\bigr).
\]

This proves the failure of exact ideal-gain additivity independently of
the size of the finite second differences computed by the interval engines.
The endpoint certificate supplies the root range used by the proof.

## Exact finite comparison

For each j=0,...,4 the audit encloses a(j) between adjacent multiples of
10^-24. It requires both retained rational moment engines to prove that
the lower endpoint has moment strictly below one and the upper endpoint
has moment strictly above one. Monotonicity then proves the root bracket.

The map a/(1+a) is strictly increasing for a>0, so applying it to both
endpoints gives exact rational brackets for k(j). Interval subtraction
proves the three positive second differences and

\[
8.4541370845\cdot10^{-11}
<k(4)-4k(1)+3k(0)
<8.4541370846\cdot10^{-11}.
\]

These are ideal arithmetic ceilings. The selected witness also uses strict
backoffs, a finite bootstrap and downward selection on a 10^-18 grid.
The current verifier prices the final combined profile before those steps.
This audit identifies no failure of that selected witness.
