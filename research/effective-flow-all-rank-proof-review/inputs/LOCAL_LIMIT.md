# An effective interval local limit for the historical paid law

This is a written analytic lemma for the historical raw-p7 law used by
`research/direct-flow-exponent-gate`. It replaces the ineffective use of
Stone's interval theorem in this application by an explicit bound. It is not
a new multiplication exponent, a physical supplier, or a change to the
selected certificate. The estimates are deliberately conservative.

Prepared for @alephnan with substantial OpenAI Codex assistance. The classical
interval approximation is due to Beurling and Selberg; the paid law and its
tilt come from the credited predecessor packages. Apache-2.0 applies to this
new proof.

## 1. Law and finite hypotheses

Write

```
P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300,
     8:1464, 16:448, 32:448, 48:448},
A = sum_r P_r r^alpha,
Pr(X=log r) = P_r r^alpha/A,
E X = a = log 5,
Z = X-a,  v = E Z^2 = sigma^2,  c_sigma = sigma sqrt(2 pi).
```

All logarithms are natural. The predecessor defines the unique tilt alpha by
the displayed mean equation and brackets it in
`[0.98981438244597, 0.98981438244599]`. The new numerical checker must verify
the following six coarse hypotheses from the literal law and that bracket:

```
Pr(X=0) >= 1/4,
Pr(X=log 2) >= 1/8,
Pr(X=log 3) >= 1/16,
2 <= v <= 3,
E |Z|^3 <= 5,
|Z| <= 3 almost surely.                                      (H)
```

For orientation, outward rational interval calculations give the three named
probabilities in `[.289256813142,.289256813143]`,
`[.164687698721,.164687698722]`, and
`[.077288932732,.077288932733]`; the variance lies in
`[2.192503074149,2.192503074150]`, and the third absolute centered moment in
`[3.978639864753,3.978639864755]`. These displayed decimals are not substituted
for the rational checks of (H).

The argument below applies to any finite real law satisfying (H), with atoms
at exactly `0,log 2,log 3` before centering. Other atoms are unrestricted
apart from (H). In this general statement set `a=E X`, `Z=X-a`, and
`v=E Z^2`, so that `E Z=0` is an explicit hypothesis through centering;
the special value `a=log 5` is not needed. Let `Z_n` be a sum of n
independent copies of Z, and let
`G_n` have the normal law with mean zero and variance `nv`.

## 2. Quantitative statement

For every integer `n >= 1296`, define

```
B_n = 3/sqrt(n) + sqrt(n) log(n) exp(-sqrt(n)/320),
A_n = [1+4 B_n]/log(n).
```

For every real x, every b>=0, and every interval I with endpoints x and x+b,
regardless of whether either endpoint is included,

```
sqrt(n) |Pr(Z_n in I)-Pr(G_n in I)| <= A_n + b B_n.             (1)
```

Consequently

```
|sqrt(n) Pr(Z_n in I)
 - b exp(-x^2/(2nv))/c_sigma|
 <= A_n + b B_n + b^2/(4 sqrt(n)).                            (2)
```

At b=0 this includes both the singleton `{x}` and the empty interval.
The estimates are uniform in x. In particular, for `0<=b<=5000` and
`n>=2^100`, the right sides of both (1) and (2) are at most `2/log(n)`.
Set, symbolically,

```
n_LLT = 2^(10^12).
```

Then for every integer `n>=n_LLT`, every such interval with `b<=5000`,

```
|c_sigma sqrt(n) Pr(Z_n in I)
 - b exp(-x^2/(2nv))| <= 10^(-8).                             (3)
```

The stronger comparison with the exact Gaussian interval integral also has
error at most `10^(-8)` after multiplication by `c_sigma sqrt(n)`.
The notation `2^(10^12)` is an exact integer expression; verification does
not allocate its decimal or binary expansion.

## 3. The sole external analytic approximation

Use the Fourier convention

```
hat f(t) = integral_R f(u) exp(-itu) du,
f(u) = (1/(2pi)) integral_R hat f(t) exp(itu) dt.
```

The classical Beurling--Selberg interval approximation provides real
integrable continuous functions `F_-`, `F_+`, with Fourier transforms
supported in `[-T,T]`, which bound the interval indicator from below and
above and have `L1` defects `2pi/T`. Thus, for an interval of length b,

```
integral |F_+-1_I| = integral |1_I-F_-| = 2pi/T,
||F_+||_1, ||F_-||_1 <= b+2pi/T.                              (4)
```

An inspected statement with precisely this bandwidth and defect is Laura
Shou, *Pointwise Weyl law for graphs from quantized interval maps*,
[arXiv:2110.15301v3, Theorem 4.1, printed page 12](https://arxiv.org/pdf/2110.15301v3).
That paper credits the classical construction and cites J. D. Vaaler,
*Some extremal functions in Fourier analysis*, Bulletin of the AMS 12
(1985), 183--216,
[DOI 10.1090/S0273-0979-1985-15349-2](https://doi.org/10.1090/S0273-0979-1985-15349-2).
Shou includes a `1/(2pi)` normalization in the forward Fourier transform;
rescaling that transform gives the convention above without changing its
support or either spatial `L1` defect. No extremality assertion is needed.

For completeness about endpoints, even if an interval theorem adopts
half-weight indicators at its endpoints, use its majorant for
`[x-epsilon,x+b+epsilon]` and its minorant for
`[x+epsilon,x+b-epsilon]`, with `0<2epsilon<b`. These bound every endpoint
convention for the original interval. The estimates below depend only on
the lengths and ordinary Gaussian integrals. Letting epsilon decrease to
zero proves exactly (1) for each convention. No unproved bound on atom
sizes and no assertion that the random walk has a density are used.

For b=0, apply the positive-length upper bound to
`[x-epsilon,x+epsilon]`. As epsilon decreases to zero, continuity from
above of probability measures gives the mass of `{x}`; the Gaussian
probability and the terms proportional to b vanish. Thus (1) and (2)
hold for the singleton with right side `A_n`. The empty interval is
immediate. This also covers singleton superlevel sets in section 9.

## 4. A Fourier comparison inequality

Let `phi(t)=E exp(itZ)`. Put

```
D_n(T) = integral_(-T)^T |phi(t)^n-exp(-nv t^2/2)| dt.
```

Fourier inversion and (4) imply, for either sign,

```
|E F_+(Z_n)-E F_+(G_n)|,
|E F_-(Z_n)-E F_-(G_n)|
 <= [(b+2pi/T)/(2pi)] D_n(T).
```

Indeed `|hat F(t)|<=||F||_1`, and the compactly supported Fourier transform
is integrable. The density of `G_n` is bounded by
`1/(sigma sqrt(2pi n))`. The Gaussian expectation of each approximation
therefore differs from its Gaussian interval probability by at most this
bound times `2pi/T`. The pointwise sandwich gives

```
sqrt(n) |Pr(Z_n in I)-Pr(G_n in I)|
 <= 2pi/[T sigma sqrt(2pi)]
    + [(b+2pi/T)/(2pi)] sqrt(n) D_n(T).                      (5)
```

The same estimates apply to the enlarged/contracted intervals used for
endpoints, and pass to their limit. They do not depend on x.

## 5. Central frequencies with explicit constants

Take `delta=1/6`. For an independent copy `Z'`, (H) gives
`|t(Z-Z')|<=1` when `|t|<=delta`. The elementary bound
`1-cos u>=u^2/3` on `[-1,1]` gives

```
|phi(t)|^2 = E cos(t(Z-Z')) <= 1-(2/3)v t^2,
|phi(t)| <= exp(-v t^2/3).                                  (6)
```

Taylor's theorem, `E Z=0`, and (H) give

```
|phi(t)-(1-vt^2/2)| <= (5/6)|t|^3,
|exp(-vt^2/2)-(1-vt^2/2)| <= v^2 t^4/8.
```

Here the second bound follows from `0<=exp(-u)-1+u<=u^2/2`
for `u>=0`. Since `v<=3` and `|t|<=delta`,

```
|phi(t)-exp(-vt^2/2)| <= (49/48)|t|^3.
```

For `n>=2`, telescoping the nth powers and using (6) yields

```
|phi(t)^n-exp(-nv t^2/2)|
 <= n(49/48)|t|^3 exp[-v(n-1)t^2/3]
 <= n(49/48)|t|^3 exp(-nv t^2/6).
```

Using `integral_R |t|^3 exp(-ct^2) dt=1/c^2` and `v>=2`,

```
integral_(-delta)^delta |phi(t)^n-exp(-nv t^2/2)| dt
 <= 36(49/48)/(v^2 n)
 <= 147/(16n) < 10/n.                                      (7)
```

## 6. Quantitative separation of the two logarithmic frequencies

For real t write

```
d_2(t)=dist(t log2, 2pi Z),
d_3(t)=dist(t log3, 2pi Z),
d(t)=max(d_2(t),d_3(t)).
```

We prove that, when `n>=1296` and
`delta<=|t|<=T=2 log n`,

```
d(t) >= n^(-1/4).                                          (8)
```

By symmetry assume t>0. Choose nonnegative integers p,q nearest to
`t log2/(2pi)` and `t log3/(2pi)`, respectively. If p=q=0, then
`d(t)>=t log3>=1/6>=n^(-1/4)`, using `log3>1` and `1296=6^4`.

Otherwise unique factorization gives `2^q != 3^p`, including the cases
where only one of p,q is zero. Distinct positive integers differ by at
least one, so integration of `1/u` between them gives

```
|q log2-p log3| >= 1/max(2^q,3^p).
```

The nearest-integer bounds imply

```
max(q log2,p log3)
 <= T log2 log3/(2pi) + (log3)/2.
```

Writing `e_2=t log2-2pi p`, `e_3=t log3-2pi q` shows

```
2pi(q log2-p log3)=e_2 log3-e_3 log2.
```

Consequently

```
d(t) >= [2pi/(sqrt(3) log6)]
        exp[-T log2 log3/(2pi)].                            (9)
```

The elementary inequalities
`log2<7/10`, `1<log3<11/10`, `pi>31/10`, `sqrt(3)<2`,
and `log6<2` show

```
log2 log3/(2pi)<1/8,
2pi/(sqrt(3)log6)>1.
```

Substitute `T=2 log n` into (9) to obtain (8). This argument uses an
explicit integer separation, not an ineffective irrationality or
Diophantine-approximation assertion.

Centering does not change the characteristic-function modulus. The exact
pair expansion and the three atoms in (H) give

```
1-|phi(t)|^2
 = 2 sum_(i<j) p_i p_j[1-cos(t(x_i-x_j))]
 >= 4 p_0 min(p_log2,p_log3)[d_2(t)^2+d_3(t)^2]/pi^2
 >= d(t)^2/(16pi^2).
```

We used `1-cos u>=2 dist(u,2pi Z)^2/pi^2`. Since `pi^2<10`,
`sqrt(1-u)<=exp(-u/2)`, and (8) holds,

```
|phi(t)| <= exp[-d(t)^2/(32pi^2)]
         <= exp[-1/(320 sqrt(n))]
                  (delta<=|t|<=T),
|phi(t)|^n <= exp[-sqrt(n)/320].                            (10)
```

## 7. Complete the Fourier bound

Integration by comparison with the derivative of the Gaussian gives

```
integral_(|t|>delta) exp(-nv t^2/2) dt
 <= 2 exp(-nv delta^2/2)/(nv delta)
 <= 6 exp(-n/36)/n.
```

Combining this with (7), (10), and `T=2 log n` gives

```
D_n(T) <= 10/n + 6 exp(-n/36)/n
                   + 4 log(n) exp[-sqrt(n)/320]
       <= 16/n + 4 log(n) exp[-sqrt(n)/320].                 (11)
```

The smoothing term in (5) is at most `1/log n`, because
`sigma>=sqrt(2)` and `pi<4`. Also `2pi>6` and
`2pi/T=pi/log n<4/log n`. Substitution of (11) into (5), rounding
`16/6` upward to 3 and `4/6` upward to 1, proves (1).

The Gaussian density `g_n` satisfies

```
sup_y |g_n'(y)| = 1/[nv sqrt(2pi e)].
```

Hence replacing its integral over `[x,x+b]` by `b g_n(x)` has error at
most `b^2/[2nv sqrt(2pi e)]`. Multiplying by `sqrt(n)` and using `v>=2`
proves (2). The Gaussian assigns zero mass to endpoints, so this step
introduces no convention dependence.

## 8. The symbolic onset used by the flow proof

We verify the simplification to `2/log n` for `b<=5000`, `n>=2^100`
without representing huge integers. Put `w=log n`. Since `log2>2/3`,
we have `w>=200/3>60`. The right side of (2) is at most

```
1/w + 2^23 exp(-w/2)
    + 5001 w exp(w/2) exp[-exp(w/2)/320].                    (12)
```

Indeed `b+4/w<5001`, and
`3*5001+5000^2/4=6265003<2^23`.

For `w>=60`, `w exp(-w/2)` decreases. The positive exponential series
gives `e^3>16`, and thus `e^30>2^40`. At w=60,

```
2^23 w exp(-w/2) < 60/2^17 < 1/2.
```

The last term of (12), multiplied by w, also decreases for `w>=60`:
its logarithmic derivative is
`2/w+1/2-exp(w/2)/640<0`. At w=60, use that
`u exp(-u/320)` decreases for `u>320`, then `e^30>2^40`, to bound it by

```
5001*60^2*2^40 exp(-2^40/320)
 < 2^65 exp(-2^31)
 < 2^(65-2^31) < 1/2.
```

The two remainder terms in (12) therefore sum to at most `1/w`.
This proves the stated `2/log n` bound, also for (1), whose right side is
smaller. Finally, `c_sigma<5` follows from `v<=3` and `pi<4`. For
`n>=2^(10^12)`,

```
c_sigma * 2/log n < 10/log n
 <= 15/10^12 < 10^(-8),
```

which proves (3) and its Gaussian-integral version. This is a mathematical
onset certificate, not a claim that this many convolution steps were run.

## 9. Kernel forms available to callers

For any nonnegative bounded monotone function f on a finite interval,
extended by zero outside that interval, every positive superlevel set is
an interval. Layer-cake integration of (1) therefore gives, uniformly in
the shift c and with arbitrary consistent endpoint choices,

```
sqrt(n) |E f(c-Z_n)-E f(c-G_n)|
 <= ||f||_infinity A_n + B_n integral_R f(u) du.              (13)
```

The same formula applies to `f(u)=exp(-tau u)1_(u>=0)`, tau>0, by monotone
convergence of its layer-cake representation. Its bound is `A_n+B_n/tau`;
there is no necessary finite tail cutoff at this step. The Gaussian
expectation can in turn be replaced by the flat central density, with

```
|sqrt(n) E[exp(-tau(c-G_n))1_(c-G_n>=0)]
 - 1/(c_sigma tau)|
 <= [c^2/tau+2|c|/tau^2+2/tau^3]/[2nv c_sigma].             (14)
```

To see (14), write the expectation as the integral of
`exp(-tau u) exp[-(c-u)^2/(2nv)]/c_sigma`, and use
`0<=1-exp(-z)<=z` before integrating the three polynomial terms.

The complement-capacity kernel in the predecessor is monotone as required
by (13). For `0<s<1`, let `F(x)=1-(1-x)^s` on `[0,1]`. It is convex,
vanishes at zero, and satisfies `xF'(x)>=F(x)` on `(0,1)`. Therefore,
when alpha<1,

```
d/dy {exp(alpha y) F(c exp(-y))}
 = exp(alpha y)[alpha F(x)-xF'(x)] <= 0,
             x=c exp(-y).
```

Continuity includes the possible endpoint x=1. This explains why no
unquantified step-function approximation is needed to transfer the interval
bound to the finite source and complement windows.

The later flow argument still has to account for its exact mixed-layer
normalizations, target sums, endpoints, geometric tails, and all source,
boundary, and leaf terms. This local-limit lemma alone is not that complete
propagation argument. Neither argument discharges physical realization or
the selected multiplication theorem's inherited assumptions.
