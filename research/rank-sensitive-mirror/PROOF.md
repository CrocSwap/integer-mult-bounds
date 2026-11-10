# Rank-sensitive complement capacity for the capped mirror flow

This contribution is produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
The capped-flow and normalized recurrence contracts are cited premises. No
native unit realizing the example, physical supplier, new kappa, or complete
multiplication theorem is supplied.

## 1. Premises and the new source charge

Use zxv's arbitrary-height capped flow from PR4436/4483 and Ryanson Jonathan's
corrected PR4459 mirror identity. Dillon Amburgey's PR4532 supplies the
critical-root tail construction and shifted-logarithmic majorant. These results
are used as premises, without auditing or replaying their examples.

The nonempty integer histograms have target ranks `2 <= k <= m=max(k)` and
paid ranks `1 <= r < m`, with multiplicities `W_k` and `P_r`. Let

```text
T(t) = sum_k W_k k^t,       P(t) = sum_r P_r r^t,
0 < t < 1,                 C = floor(n/m).
```

Fix a real ambient scale `Lambda>m`. Restrict to integers `n` for which
`n<=Lambda C`. It suffices that `C >= (m-1)/(Lambda-m)`, since
`n<=mC+m-1`. This is a finite base-range restriction, not a substitution
of `n/m` for the integer cutoff.

The cited mirror identity expresses every inner source through a pair `k>r`
and an integer base product `z`, in the window

```text
C/k < z <= C/r,          source rank s=rkz.
```

Consequently `s>rC>=rn/Lambda`. For the pure power, concavity gives

```text
n^t-(n-s)^t >= t n^(t-1) s >= eta_r(t) s^t,
eta_r(t) := t (r/Lambda)^(1-t).                         (1)
```

The inequality includes `s=n`. Every source rank is at most `n`, by the
inherited flow contract. The usual uniform charge uses only `eta_1`; (1)
retains the paid letter `r` attached to that particular source window.

The same charge works for the shifted-logarithmic function

```text
f(0)=0,    f(x)=A x^theta (c+log x)^p for x>=1,
tau(x)=theta+p/(c+log x),    0<theta<1,    c>=p/(1-theta).
```

Indeed `f` is increasing and concave on `[1,infinity)`, `tau<=1`, and
`f'(x)=tau(x)f(x)/x`. For integer `1<=s<n`, concavity gives
`f(n)-f(n-s)>=tau(n)f(n)s/n`. For `s=n`, use `f(0)=0` and `tau(n)<=1`.
Thus, at `t=tau(n)`,

```text
[f(n)-f(n-s)]/f(n) >= eta_r(t) (s/n)^t.                 (2)
```

This is the new replacement for the uniform source-capacity step. It does
not alter the flow, its paid positions, or the productive boundary.

## 2. Weighted mirror inequality and complete leaf funding

Partition the `y=z/C` axis at the endpoints `1/k,1/r`, using the inherited
half-open windows. Write

```text
E_J(t) = sum_(r>k, J subset (1/r,1/k]) P_r W_k (rk)^t,
S_(J,r)(t) = sum_(k>r, J subset (1/k,1/r]) P_r W_k (rk)^t,
D_J(t) = sum_r eta_r(t) S_(J,r)(t).
```

Suppose a constant `0<=b<1` satisfies

```text
E_J(t) <= b D_J(t) for every elementary cell J.          (3)
```

A zero `D_J` must have zero `E_J`. Let `K_t` be the sum of `eta_r(t)s^t`
over all actual inner sources, with their multiplicities, and let `I_t`
be their ordinary `t`-potential. Integrating (3) against the exact
nonnegative capped base measure gives

```text
B_t <= b K_t,          K_t >= eta I_t,
eta := eta_1(t) in (0,1).                               (4)
```

Here `B_t` is boundary-exit potential. There is no assumed density,
equidistribution, or limit measure. The actual nonlinear complement capacity
dominates `K_t` after the common normalization in (2).

Let `F_t` be leaf-exit potential and `A_t` the net occupation surplus after
root sources. The cited exact cancellation is

```text
I_t = B_t + F_t + A_t.
```

The new sufficient funding implication is

```text
A_t >= 0 and (1-b) eta A_t >= (1-eta) F_t
       imply B_t+F_t <= K_t.                            (5)
```

To prove it, suppose `K_t<B_t+F_t`. Then cancellation and (4) imply
`K_t>=eta I_t>eta(K_t+A_t)`, hence
`(1-eta)K_t>eta A_t`. Also (4) gives
`F_t>K_t-B_t>=(1-b)K_t`. Multiplying these inequalities contradicts
the hypothesis of (5). This proof uses no division by `F_t` and covers
zero leaf or boundary mass. With (2), exit charge is therefore funded by
the actual inner-source complement capacity. Root complement capacities
are nonnegative and remain available.

In particular, the inherited bounds

```text
F_t <= P(t)^(G+1),      A_t >= Q_ell(t) P(t)^(G+1)
```

are sufficient whenever

```text
Q_ell(t) >= (1-eta)/((1-b)eta).                          (6)
```

Leaves have not been dropped. Condition (6) replaces the uniform mirror
threshold; it does not assert that a favorable mirror test alone funds a flow.

Allowing `Lambda>m` to be chosen makes this a weaker sufficient mirror test.
Indeed, if the old uniform ratio is `beta<t m^(t-1)`, choose `Lambda`
sufficiently close to `m` that `beta<eta_1(t)`. Since every `r>=1`,
`D_J>=eta_1 S_J`, so (3) holds with `b=beta/eta_1<1`. The example below
proves that the converse fails. No inclusion is asserted for an arbitrary
fixed, excessively large value of `Lambda`.

## 3. Critical-root corollary

Assume the same finite-flow and normalized recurrence contracts as PR4532.
Suppose, for some `theta in (0,1)`,

```text
T(theta)=P(theta),
mu_T(theta)>mu_P(theta),
E_J(theta)<=b_* D_J(theta) for every J, with b_*<1.       (7)
```

Then there exist positive `A,c,p` and an integer base cutoff `n0` such that
the conditional normalized leaf recurrence has

```text
L(0)=0,        L(n)<=A n^theta(c+log n)^p for all n>=1.  (8)
```

The following specifies exactly which predecessor steps are used and which
capacity step changes. The moment crossing and positive mean gap give positive
integers `a,b_h`, an integer height base `M>1`, and positive rational tail
parameters `s_0,lambda` as in PR4532 section 2.1--2.2. The mixed and root
tail factors are strictly below one, and forward ratio ordering holds.
This tail argument uses the mean gap, not mirror capacity.

Every nonzero `D_J(t)` is positive and continuous near `theta`; identically
zero source cells have no exit under (7). Choose `b_bar` strictly between
`b_*` and one. On a sufficiently short right interval at `theta`, (3)
holds with `b_bar`, both tails are bounded by constants `U,V<1`, and
`d(log(T/P))/dt>=d>0`. Also

```text
eta_1'(t) = Lambda^(t-1)(1+t log Lambda)>0,
eta_1(t)>=eta_*:=eta_1(theta)>0.
```

The inherited shifted-logarithmic occupation estimate is

```text
Q_ell(tau(n)) >=
(1-U^ell)(exp(K_ell)-1)-Q M^lambda V^ell,
K_ell = d p(a ell+1)/(c+log m+(ell+1)log M+log 2),
```

where `Q` is a finite upper bound for `T/P` on that interval. This is the
same occupation/root-tail estimate, not a new invoice or tail inequality.
Its right side increases to `exp(dpa/log M)-1` as `ell` increases. Choose
`p` so that this limit exceeds

```text
(1-eta_*)/((1-b_bar)eta_*).
```

Choose `c>=p/(1-theta)`, then a sufficiently large integer `ell0` so that
the occupation estimate exceeds this threshold, `tau(n)` lies in the
certified right interval, and `n<=Lambda floor(n/m)` above the base cutoff.
All these demands are finite. Increasing `ell0` preserves them. Put
`n0=m M^ell0` and use elementary evaluation through `n0`.

For `n>n0`, set `ell=floor(log_M floor(n/m))`, so `ell>=ell0`.
The occupation estimate, monotonicity of `eta_1`, and (6) fund all exits
by the source capacities (2). The inherited exit comparison
`f(e)/f(n)<=(e/n)^tau(n)` applies unchanged. Choosing
`A=n0^(1-theta)/(c+log n0)^p` funds the elementary base range since `f/x`
is decreasing. Every recursive rank is strictly below `n`, so induction
proves (8). No predecessor native premise has been discharged.

The mean gap is an explicit hypothesis in this corollary. The weighted
condition is not used to infer it. This avoids transferring PR4532's
unweighted integral argument to a different mirror inequality.

## 4. Exact integer-histogram separation

Take the abstract histograms

```text
W_16=1, W_64=2;      P_1=2, P_4=6, P_36=1;
theta=1/2, m=64,    Lambda=289/4, sqrt(Lambda)=17/2.
```

Both moments at `theta` are exactly 20. Their tilted-log mean difference is

```text
mu_T-mu_P = (19 log 2-3 log 3)/5 > 0,
```

since `2^19>3^3`. The only cell with exits is `(1/36,1/16]`. On it,

```text
E=24,       S_(J,1)=32,       S_(J,4)=192,
E/S = 24/224 = 3/28 > 1/16.
```

Thus PR4532's uniform mirror hypothesis fails, even with its more favorable
ambient constant `m=64`. For the new charge,

```text
eta_1=1/17,     eta_4=2/17,
D_J=32/17+384/17=416/17,
E/D_J=51/52<1.
```

All other cells have zero exit coefficient. The floor guard holds uniformly
for `C>=8`, since `64C+63 <= (289/4)C`. In particular `n>=512` suffices.
The local mirror calculation uses exactly the cap and costs declared in
sections 1--2.

There is also an exact two-tail positive control. Choose `a=b_h=1`,
`M=1024`, `s_0=lambda=1/2`. Then

```text
T(1)=144, P(1)=62, T(0)=3,
u=1024^(-1/2)(144/20)(62/20)=279/400<1,
v=1024^(1/2)(3/20)^2=18/25<1,
144/20 > 62/20.
```

The corollary therefore applies to this abstract recurrence at exponent
`1/2`. This is not a native supplier with saving `1/2`. No native word
realizing these histograms has been given.

At the exact exponent, (6)'s threshold is 832. The algebraic values
`B=51,F=1,A=832,I=884,K=52` attain every constraint in (4)--(6) and give
`K=B+F`. The shifted-log proof uses a strictly larger bound on a right
interval. The number 832 is not a claimed sufficient compiler height.

## 5. Verification boundary

The standalone verifier computes only this new toy profile and the new
capacity/funding implications. It uses exact rational and integer arithmetic.
It enumerates the toy's capped base measures in two ways and checks actual
nonlinear square-root complement capacities at 49 finite rank/height fixtures.
Those checks corroborate (1)--(6); (8) rests on the written argument and cited
flow/tail premises. No p7/p16 or selected native replay is performed.

The contribution only replaces a sufficient complement-capacity test. It
does not solve the full distribution-dependent mirror question in PR4532,
prove an actual profile's physical costs, or discharge any of the selected
record's five inherited assumptions. Arbitrary-input native correctness,
ownership/restoration, chronological batch widths, adapters, movement,
precision, stock, tape execution, analytic transfer and exact recovery remain
separate obligations. Independent human and formal proof-kernel review are
unclaimed.
