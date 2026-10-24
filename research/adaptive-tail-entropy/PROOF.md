# A sharp range-and-mean screen for the two tail gates

## Contract and cited premise

Let finite nonempty target and paid histograms have positive coefficients,
with target ranks `2<=k<=m` and paid ranks `1<=r<m`. Fix `0<t<1` and set

```text
T(t)=sum W_k k^t,       P(t)=sum P_r r^t,
q=T(t)/P(t)>=1,
mu_T=T'(t)/T(t),        mu_P=P'(t)/P(t).
```

The analytic bounds below also hold for positive real histogram weights.
Gate implications apply to histograms covered by the cited contract.

We use Dillon Amburgey's #4532, PROOF.md section 3, as a cited premise.
The following three gates admit positive integers a,b, an integer M>1
and positive rational s,lambda if and only if some real lambda>0 has
`F(lambda)<1`:

```text
u=M^(-s) [T(t+s)/T(t)]^a [P(t+s)/P(t)]^b <1,
v=M^lambda [T(t-lambda)/P(t)]^(a+b) <1,
T(t+s)/T(t) >= P(t+s)/P(t),
F(lambda)=T(t-lambda) exp(lambda mu_P)/P(t).
```

The source proves the integer-height and rational-parameter existence
implication. It is not an audit target here. This note computes a new
explicit screen for F and its equality case. Mirror capacity, recurrence
funding and native implementation are outside that equivalence.

## The theorem

Give `X=log k` probability `W_k k^t/T(t)`. Write

```text
A=min log k, B=max log k, R=B-A,
Z=(X-A)/R,   p=E[Z]=(mu_T-A)/R,   x=(mu_P-A)/R.
```

First suppose the target has at least two distinct ranks. Then R>0,
`0<p<1`, and `F(lambda)=q E exp[-lambda R(Z-x)]`.

1. If `mu_P<A`, the gates are feasible.
2. If `mu_P=A`, they are feasible exactly when
   `W_kmin kmin^t < P(t)`.
3. If `A<mu_P<mu_T`, define
   `D(x||p)=x log(x/p)+(1-x)log((1-x)/(1-p))`.
   If `log q<D(x||p)`, the gates are feasible. They are also feasible at
   equality if any target rank lies strictly between the two extremes.
   For targets supported on the two extremes only, the exact condition is
   `log q<D(x||p)`. Equality fails.
4. If `mu_P>=mu_T`, the gates are infeasible.

For a one-rank target `k0`, feasibility is exactly `mu_P<log k0`.
No upper bound on q is needed in that case, except the assumed q>=1.

The interior-regime sufficient bound is sharp among positive finite laws
with the same range and target mean: the two-endpoint law attains its
bound, so above or at that threshold these statistics alone cannot
guarantee feasibility. At equality, knowing that interior mass exists
does supply additional information. For integer histograms, this sharpness
assertion applies whenever the corresponding endpoint statistics can be
realized. The integer boundary example below provides one such realization.

## Proof

If `mu_P<A`, then
`F(lambda)<=q exp[-lambda(A-mu_P)]`, which tends to zero. If `mu_P=A`,
F decreases strictly to `q Pr(X=A)`, and every finite value is larger than
that limit. This proves cases 1 and 2.

For `0<x<p`, put h=lambda R. Strict convexity on `[0,1]` gives

```text
exp[-h(z-x)] <= (1-z) exp(hx)+z exp[-h(1-x)].
```

For h>0 equality holds exactly at z=0 or z=1. Taking expectations gives

```text
F(lambda) <= q [(1-p) exp(hx)+p exp(-h(1-x))].       (1)
```

Differentiate the bracket. Its unique minimizing positive h is

```text
h*=log[p(1-x)/(x(1-p))]>0.
```

Substitution gives the minimum

```text
(p/x)^x ((1-p)/(1-x))^(1-x) = exp[-D(x||p)].         (2)
```

If `q exp(-D)<1`, (1) evaluated at h* supplies a strict passing point.
If this product equals one and some interior rank has positive mass,
strict convexity makes (1) strict at that same point. The source's premise
then supplies integer height and rational tail parameters. There is no
claim that h*/R is rational; the passing inequality is open.

For a two-endpoint law, (1) is an equality for every h, and (2) is its
actual minimum. Thus strict inequality is necessary and sufficient.
This also proves the stated sharpness from range and mean alone.

Finally Jensen's inequality gives
`F(lambda)>=q exp[lambda(mu_P-mu_T)]>=1` if `mu_P>=mu_T`.
For a single target rank the exact expression is
`F(lambda)=q exp[lambda(mu_P-log k0)]`, proving the final case.

These arguments address real lambda. The cited equivalence supplies the
required rational and integer compiler parameters wherever a strict
passing point exists. QED.

## Exact new histogram boundary

Take `W_4=1, W_256=32, P_16=c` and t=1/2. For integers `1<=c<=128`,
q=514/(4c)>=1. The normalized log ranks are 0 and 1 with p=512/514,
and `x=(log16-log4)/(log256-log4)=1/3<p`.

Writing `y=4^lambda>1`, the unnormalized scalar criterion is

```text
T(t-lambda) exp(lambda mu_P) = 2y+512/y^2.
```

Its derivative vanishes exactly at y=8; it decreases below 8 and
increases above 8. The exact minimum is 24, at lambda=3/2.
Equivalently the entropy calculation gives
`q exp[-D(1/3||256/257)]=6/c`.
The strict gate condition is therefore c>6, proving the claimed integer
transition. All c<=6 fail, including the equality case c=6.

For c=7 choose a=1,b=31,M=2^132,s=1/2,lambda=3/2. Since

```text
T(1)/T(1/2)=(4+32*256)/514=4098/257,
P(1)/P(1/2)=16/4=4,
T(-1)=1/4+32/256=3/8,
```

direct substitution in the original gates gives

```text
u=2^-66 (4098/257) 4^31=2049/2056<1,
v=2^198 (3/224)^32=64*(6/7)^32<1.
```

The latter strict inequality is the exact integer inequality
`64*6^32<7^32`, checked by the verifier. The forward ratio also strictly
exceeds 4. This is a literal gate witness, not just a scalar sufficient test.

For c=7 and every nonnegative exponent z, `32*256^z>7*16^z`.
Thus T(z)>P(z), so this passing fixture has no nonnegative moment
crossing. This observation does not imply full recurrence funding.

## Mirror failure and claim correction

The only exit window is `(1/16,1/4]`, supplied by the pair (16,4),
with coefficient `8c`. The only inner-source window is `(1/256,1/16]`,
from (16,256), with coefficient `2048c`. They are disjoint. On the
exit window the source coefficient is zero, so no finite mirror factor
covers it. The coefficient ratio 1/256 does not establish coverage.

The advance CLAIM predicted mirror slack for this fixture. That
prediction was wrong and was explicitly corrected in the permitted
[progress update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147154).
The delivered claim is tail/ordering feasibility only. The entropy theorem
does not assume mirror coverage. No full compiler admission was obtained.

## Scope and credit

Native realizability, full mirror/recurrence funding, chronological
batching, ownership/restoration, adapters, precision/tape costs, stock,
analytic transfer and exact recovery remain open. No selected frontier
or frozen predecessor is changed.

The exact scalar equivalence is Dillon Amburgey's #4532 contribution.
The compiler/gate lineage is zxv #4436/#4483, Jacob Alan Sussman and
Ryanson Jonathan #4459, together with the native and outer contributors
credited there. The entropy optimization is a classical method. The
new scoped screen, strict boundary application and exact histogram
transition were produced by Nick Petalas. Apache-2.0.
