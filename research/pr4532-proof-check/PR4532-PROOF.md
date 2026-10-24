# A sufficient profile criterion for adaptive compiler gates

This note proves a sufficient existence criterion for the adaptive compiler
of zxv's [PR #4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483),
at source head `fb0c208864e6b24e3473318a058aa5b2dbd5764b`. Its new conclusion
is that a moment crossing and strict pointwise mirror capacity imply the
compiler's tail gates. The mirror condition itself supplies the strict
tilted-mean gap and makes the crossing simple. The hypotheses also imply
a fully funded majorant at the crossing exponent, with a logarithmic factor.
The criterion is sufficient; necessity or admission of every favorable
moment profile is not claimed.

The arbitrary-height integer flow, its cancellation identities, and its
shifted-logarithmic majorant are predecessor results, used conditionally
here. Their native and physical implementation premises remain premises.
This note supplies neither a new native profile nor a new multiplication
exponent. The accompanying finite checks illustrate the hypotheses and
reject a tempting weaker criterion; they do not prove the theorem below.

## 1. Profiles and the exact boundary hypothesis

Let nonempty finite histograms `W_k` and `P_r` have positive integer coefficients,
with target ranks `2 <= k <= m`, where `m` is their maximum, and paid ranks
`1 <= r < m`. Define, for every real `t`,

```text
T(t) = sum_k W_k k^t,              P(t) = sum_r P_r r^t,
mu_T(t) = T'(t)/T(t),             mu_P(t) = P'(t)/P(t),
q(t) = T(t)/P(t),                 eta(t) = t m^(t-1).
```

All these moment functions are smooth where used. A native paid position
is still a separate chronological position when another position has the
same rank. The histogram specifies its multiplicity; it does not authorize
pooling unfinished calls or aliasing owners.

Use the finite mirror cells from #4483, section 2. For a pair `(r,k)`, the
exit window is `(1/r,1/k]` when `r>k`, and the inner-source window is
`(1/k,1/r]` when `k>r`. Its coefficient is `P_r W_k (rk)^t`.
Partition at all endpoints, with the indicated endpoint conventions, and
let `E_J(t)` and `S_J(t)` be the respective coefficient sums on cell `J`.
The partition is finite and does not depend on `t`.

The **strict mirror hypothesis at t_*** means there is a number `beta_*`
such that

```text
0 <= beta_* < eta(t_*),
E_J(t_*) <= beta_* S_J(t_*)       for every cell J.        (1)
```

In particular, a cell with zero source coefficient must have zero exit
coefficient. Every coefficient is a positive multiple of a positive
exponential. Thus either a cell's sum is identically zero, or it is positive
for every real exponent. Consequently (1) persists, with a slightly larger
factor, on a sufficiently small interval of exponents. This is a pointwise
mirror condition, not an assertion inferred from finitely sampled flows.

### 1.1 Mirror slack supplies the mean gap and rank-one surplus

Write `S_t(z)` and `E_t(z)` for these piecewise constant coefficient
functions, extended by zero outside their finitely many windows. Their
support lies in a compact interval bounded away from zero. For `k>r`,
the integral of `dz/z` over its source window is `log(k/r)`; for `r>k`,
subtracting the exit window gives that same signed value. Hence

```text
integral_0^infinity [S_t(z)-E_t(z)] dz/z
 = sum_(r,k) P_r W_k (rk)^t log(k/r)
 = P(t) T'(t)-T(t) P'(t)
 = P(t) T(t) [mu_T(t)-mu_P(t)].
```

Whenever `E_t<=beta S_t` pointwise with `beta<1`, the left side is
strictly positive: every paid rank is below `m`, so a pair with target
rank `m` supplies a source window of positive length. Therefore strict
mirror slack implies `mu_T(t)>mu_P(t)`. In particular (1), with
`eta(t_*)<1`, supplies the mean gap at the crossing automatically.

There is also positive rank-one surplus. For `0<t<1`, integrating instead
against `z^(t-2) dz` gives

```text
integral_0^infinity [S_t(z)-E_t(z)] z^(t-2) dz
 = [P(t) T(1)-T(t) P(1)]/(1-t).
```

The same positivity argument applies. At `T(t_*)=P(t_*)`, this implies
`T(1)-P(1)>0`. Thus neither the tilted-mean gap nor positive rank-one
surplus needs an additional hypothesis. These integral identities are
exact finite sums; they do not estimate the distribution of a flow.

## 2. Existence theorem

**Theorem.** Suppose the native profile and the conditional finite compiler
contracts of #4483 apply. Suppose that for some `t_*` in `(0,1)`,

```text
T(t_*) = P(t_*),                                         (2)
```

and the strict mirror hypothesis (1) holds. Put
`delta_* := mu_T(t_*)-mu_P(t_*)`, which is positive by section 1.1.
Then there exist positive integers `a,b`, an integer `M>1`, positive rational
numbers `s,lambda`,
and a number `epsilon>0`, with `t_*+epsilon<1`, for which all of #4483's
two-tail and ratio-ordering gates hold uniformly on
`[t_*, t_*+epsilon]`.

More precisely, with `g=a+b`, there are constants

```text
0 < U,V < 1,       Q >= 1,       d > 0,
0 <= beta_bar < eta_* := eta(t_*),
```

such that throughout that interval,

```text
u(t) := M^(-s) [T(t+s)/T(t)]^a [P(t+s)/P(t)]^b <= U,
v(t) := M^lambda [T(t-lambda)/P(t)]^g <= V,
T(t+s)/T(t) >= P(t+s)/P(t),
d/dt log q(t) >= d,              q(t) <= Q,
E_J(t) <= beta_bar S_J(t)        for every mirror cell J,
eta(t) >= eta_* > beta_bar.                               (3)
```

There also exist `p,c,A>0` and an integer base cutoff `n0` such that the
normalized rank-one leaf cost of the resulting finite compiler satisfies

```text
L(0)=0,
L(n) <= A n^t_* (c+log n)^p       for every integer n>=1.  (4)
```

The compiler uses elementary evaluation through `n0` and height
`G=g floor(log_M(floor(n/m)))` above `n0`. In particular, for every
`z>t_*`, it has `L(N)<=N^z` at all sufficiently large integer ranks `N`.
This is a statement about normalized leaf counts under the inherited
contracts; productive width and physical constants are not estimated here.
The theorem is existential given its hypotheses. An executable application
must certify the chosen root, or isolate its simple crossing and bound the
needed expressions on a certified interval, before it can extract numerical
constants. No algorithm for an unspecified real parameter is claimed.

### 2.1 Integer height parameters exist

Write `mu_P*=mu_P(t_*)` and `mu_T*=mu_T(t_*)`. Choose an integer `g>=2`
large enough that

```text
(g-1) delta_* / log 2 > 1.
```

The open interval

```text
((g mu_P* + delta_*)/log 2,  g mu_T*/log 2)
```

has length greater than one, so it contains an integer `j`. Its lower
endpoint is positive because `mu_P*>=0` and `delta_*>0`; hence `j>=1`.
Set

```text
a=1,       b=g-1,       M=2^j,       h=(log M)/g.
```

Then both required geometric inequalities are strict:

```text
(a mu_T* + b mu_P*)/g < h < mu_T*.                       (5)
```

This proves existence within integer height parameters. No continuously
chosen height is substituted for an integer compiler.

### 2.2 The two tails and ratio ordering

At the crossing exponent define

```text
phi(s) = -s log M
         +a log[T(t_*+s)/T(t_*)]
         +b log[P(t_*+s)/P(t_*)].
```

We have `phi(0)=0` and, by (5),

```text
phi'(0) = -log M+a mu_T*+b mu_P* < 0.
```

Also define

```text
chi(s) = log[T(t_*+s)/T(t_*)]-log[P(t_*+s)/P(t_*)].
```

Here `chi(0)=0` and `chi'(0)=delta_*>0`. Therefore every sufficiently
small positive `s` satisfies `phi(s)<0` and `chi(s)>0`. Choose such an
`s` rational. It supplies `u(t_*)<1` and strict ratio ordering.

For the root tail, let

```text
psi(lambda) = lambda log M
              +g log[T(t_*-lambda)/P(t_*)].
```

The equality of moments at `t_*` is essential here: it gives `psi(0)=0`.
By (5),

```text
psi'(0) = log M-g mu_T* < 0.
```

Thus some sufficiently small positive rational `lambda` gives
`v(t_*)=exp(psi(lambda))<1`. There is no restriction on the sign of
`t_*-lambda`: all native ranks are positive and these finite moment sums
exist for every real exponent.

Fix these `a,b,M,s,lambda`. All the inequalities just proved are strict
and all their expressions are continuous in `t`. The derivative of
`log q` equals `mu_T-mu_P`, which is positive at `t_*`. There are only
finitely many mirror cells, and their nonzero denominators stay positive.
Choose `beta_bar` strictly between `beta_*` and `eta_*`; shrink an interval
to the right of `t_*` until all its mirror ratios are at most `beta_bar`
and its mean gap is at least some `d>0`. Shrink again as necessary so that
the fixed two tails and ratio ordering remain strict, and so that its
upper endpoint is below one. On this compact interval choose `U,V<1`
above the two tail maxima and finite `Q` above `q`.

Finally,

```text
eta'(t) = m^(t-1)(1+t log m) > 0    for t>0.
```

Hence `eta(t)>=eta_*` on the interval. This proves every assertion in (3).
Integrating the mean-gap inequality from the exact crossing gives

```text
q(t) >= exp[d(t-t_*)]     for t in [t_*,t_*+epsilon].      (6)
```

For `t>t_*` within this interval, in particular, `T(t)>P(t)`.

### 2.3 Funding the majorant at the crossing exponent

This step applies #4483's shifted-log construction. It also identifies the
precise endpoint change to that source: its displayed guard
`T(t0)>P(t0)` can be replaced here by `T(t_*)=P(t_*)`, because the power
used by every finite-rank induction step is strictly above `t_*`.
Equation (6) supplies the same lower bound needed in its equation (19).
No geometric sum is evaluated with a zero moment gap.

Put

```text
R = (1-eta_*)/(eta_*-beta_bar) > 0.
```

Choose a positive rational `p` large enough that

```text
exp(d p a/log M)-1 > R,                                  (7)
```

and choose `c>0` with `c>=p/(1-t_*)`. For integer `ell>=1` define

```text
K_ell = d p (a ell+1) /
        [c+log m+(ell+1)log M+log 2],

F_ell = (1-U^ell)(exp(K_ell)-1)-Q M^lambda V^ell.
```

The fraction in `K_ell` is increasing: its derivative, apart from a
positive denominator and the factor `d p`, is

```text
a(c+log m+log 2)+(a-1)log M > 0.
```

Both other tail factors improve as `ell` increases. Thus `F_ell` is
nondecreasing, and

```text
lim_(ell->infinity) F_ell = exp(d p a/log M)-1 > R.
```

Choose an integer `ell0>=1` with `F_ell0>=R`, large enough also that, for
`n0=m M^ell0`,

```text
tau(n0) := t_*+p/(c+log n0) <= t_*+epsilon.               (8)
```

Such a choice exists by the strict limit and because `tau(n0)` decreases
to `t_*`. The cutoff is an actual positive integer. Use elementary
evaluation at every `n<=n0`.

For `n>n0`, put `C_n=floor(n/m)`, `ell=floor(log_M C_n)`, and
`t=tau(n)=t_*+p/(c+log n)`. Then `ell>=ell0` and
`t_*<t<=t_*+epsilon`, so all of (3) applies with `T(t)>P(t)`.
Also

```text
n < m(M^(ell+1)+1),
log n < log m+(ell+1)log M+log 2.
```

Consequently (6) gives `q(t)^(a ell+1)>=exp(K_ell)`. The exact source
cancellation and the two Chernoff bounds in #4483, equations (7)--(9),
therefore give

```text
A_t := (T(t)-P(t)) H_t - R_t
     >= D_ell(t) P(t)^(G+1),

D_ell(t) = (1-u(t)^ell)(q(t)^(a ell+1)-1)
            -q(t) M^lambda v(t)^ell
          >= F_ell >= F_ell0 >= R.                     (9)
```

Here `H_t` is unit column potential and `R_t` is root-source potential;
`A_t` and `R_t` are unrelated to the normalization `A` and constant `R`.
Write `I_t,B_t,F_t` for inner sources, boundary exits, and leaf exits.
The same predecessor identities are

```text
I_t=B_t+F_t+A_t,      B_t<=beta_bar I_t,
F_t<=P(t)^(G+1).
```

The function `(1-eta)/(eta-beta_bar)` decreases for
`beta_bar<eta<1`. Since `eta(t)>=eta_*`, (9) implies

```text
(eta(t)-beta_bar) A_t >= (1-eta(t)) F_t.
```

Combining this with `(1-beta_bar)I_t<=F_t+A_t` yields

```text
B_t+F_t <= eta(t) I_t.                                  (10)
```

In particular `A_t>0`, so the inner source potential and total source
count are positive. This supplies a nonempty flow in the certified range;
a separate paid-rank-one assumption is unnecessary for this theorem.

Set

```text
A = n0^(1-t_*)/(c+log n0)^p,
f(0)=0,       f(x)=A x^t_* (c+log x)^p for x>=1.
```

For `x>=1`, its local tangent exponent is
`tau(x)=t_*+p/(c+log x)<=1`, and

```text
f'(x)=f(x) tau(x)/x,
f''(x)/f(x)=x^(-2)[tau(x)(tau(x)-1)-p/(c+log x)^2]<=0.
```

Moreover `(f(x)/x)'<=0` and `f(n0)=n0`. Thus every elementary base
rank `1<=n<=n0` satisfies `L(n)=n<=f(n)`.

For positive integer exit rank `e<=n`, `log(1+y)<=y` gives

```text
f(e)/f(n) <= (e/n)^tau(n).                               (11)
```

For an inner source rank `s>n/m`, concavity gives

```text
f(n)-f(n-s) >= tau(n) f(n) s/n
              >= eta(tau(n)) f(n) (s/n)^tau(n).          (12)
```

When `s=n`, the first inequality follows from `tau(n)<=1` and `f(0)=0`;
otherwise its arguments lie in `[1,n]`. Root sources may be smaller than
`n/m`, but their complement capacities remain nonnegative because `f` is
increasing. The zero-rank complement has zero cost.

Equation (10), with (11)--(12), bounds the complete exit charge by the
inner-source capacity. Hence `f` satisfies the complete recurrence

```text
sum_s S_s f(n-s)+sum_e E_e f(e) <= (sum_s S_s) f(n).
```

Every recursive rank is strictly below `n`, all counts are finite, and
the source count is positive. Strong induction proves (4). Finally,

```text
log A+p log(c+log N) <= (z-t_*) log N
```

holds for every sufficiently large `N` whenever `z>t_*`; its left-hand
growth is logarithmic in `log N`, while the right-hand growth is linear
in `log N`. This proves the last assertion of the theorem. QED.

## 3. Exact feasibility criterion for the two tail gates

The following lemma characterizes just the tail and ratio-ordering gates
at a fixed exponent. It neither supplies the mirror hypothesis nor admits
a native implementation. It helps distinguish the root hypothesis above
from the stronger inequality required away from a root.

Fix `t` with `q(t)=T(t)/P(t)>=1`, and for `lambda>0` define

```text
H(lambda) = [log P(t)-log T(t-lambda)]/lambda.
```

**Lemma.** Positive integers `a,b`, an integer `M>1`, and positive rational
`s,lambda` satisfying

```text
M^(-s) [T(t+s)/T(t)]^a [P(t+s)/P(t)]^b < 1,
M^lambda [T(t-lambda)/P(t)]^(a+b) < 1,
T(t+s)/T(t) >= P(t+s)/P(t)
```

exist if and only if there is a real `lambda>0` such that

```text
H(lambda)>mu_P(t),
```

or, equivalently,

```text
T(t-lambda) exp(lambda mu_P(t)) < P(t).                   (13)
```

**Necessity.** Put `g=a+b`, `alpha=a/g`, and `h=(log M)/g`.
The root-tail gate gives `h<H(lambda)`. Convexity of `log T` gives

```text
H(lambda) <= mu_T(t)-log(q(t))/lambda <= mu_T(t).
```

Convexity of both logarithmic moment functions bounds the mixed-tail
logarithm below by

```text
s g [alpha mu_T(t)+(1-alpha)mu_P(t)-h].
```

Its negativity therefore requires
`h>alpha mu_T(t)+(1-alpha)mu_P(t)`. If `mu_T(t)<=mu_P(t)`, this would
contradict `h<H(lambda)<=mu_T(t)`. Hence `mu_T(t)>mu_P(t)`, and the
weighted mean is strictly above `mu_P(t)`. Thus `H(lambda)>mu_P(t)`.
The ratio-ordering gate is not needed for this direction.

**Sufficiency.** Suppose (13) holds. Strictness and continuity allow
`lambda` to be chosen rational. The preceding convexity bound implies
`delta:=mu_T(t)-mu_P(t)>0`. Choose an integer `g>=2` large enough that
the interval

```text
((g mu_P(t)+delta)/log 2,  g H(lambda)/log 2)
```

has length greater than one, and choose an integer `j` strictly inside it.
Since `mu_P(t)>=0`, its lower endpoint is positive, so `j>=1`.
Set `a=1`, `b=g-1`, `M=2^j`. Then

```text
mu_P(t)+delta/g < h=(log M)/g < H(lambda).
```

The upper inequality gives the root-tail gate. As in section 2.2, the
derivative at `s=0` of the mixed-tail logarithm is negative, while the
derivative of the logarithmic forward-ratio difference is `delta>0`.
All sufficiently small positive `s` therefore give both the mixed-tail
gate and strict forward-ratio ordering. Choose one rational. QED.

At an exact crossing `q(t)=1`, `H(lambda)` tends to `mu_T(t)` as
`lambda` decreases to zero. A positive mean gap consequently guarantees
(13), recovering the existence step of section 2. At `q(t)>1`, a
positive mean gap alone does not imply (13). The strict surplus `T(t)>P(t)`
required by a recurrence at its actual exponent remains a separate condition;
the lemma concerns only the displayed tail and ordering inequalities.

## 4. Why fixed-exponent mean separation alone does not suffice

The moment equality at `t_*` cannot simply be dropped from the gate-existence
argument. Consider the valid rank histograms

```text
targets: W_4=4, W_64=17;       paid: P_1=4, P_16=1;
t=1/2,       m=64.
```

Then

```text
T(t)=144>P(t)=8,
mu_T(t)=(26/9)log 4 > mu_P(t)=log 4.
```

This profile also passes strict pointwise mirror capacity. Its only exit
window is `(1/16,1/4]`, from the pair `(r,k)=(16,4)`, with coefficient
`4 sqrt(64)=32`. Throughout this window the pair `(1,64)` supplies inner
coefficient `4*17*sqrt(64)=544`. The remaining cells have no exits. Hence
the exact largest mirror ratio is `beta=32/544=1/17`, while
`eta(t)=(1/2)/sqrt(64)=1/16`.

Nevertheless no choice of positive integers `a,b`, `M>1`, and positive
`s,lambda` satisfies both tail gates. Convexity of both logarithmic moment
functions gives, with `g=a+b`,

```text
log u >= s[-log M+a mu_T(t)+b mu_P(t)].
```

Thus `u<1` forces `h:=(log M)/g>log 4`. The rank-4 target term alone gives

```text
T(t-lambda) >= 4*4^(1/2-lambda) = 8*4^(-lambda).
```

It follows that

```text
v^(1/g)=exp(h lambda) T(t-lambda)/P(t)
        >=exp(lambda[h-log 4]) >1,
```

a contradiction. The obstruction concerns these simultaneous Chernoff
gates, not existence of every possible compiler. Equivalently, the rank-4
term ensures `T(t-lambda) exp(lambda mu_P(t))>=8=P(t)` for every
`lambda>0`, so the exact criterion (13) fails. For every `x>=0`,
`4*4^x>=4` and `17*64^x>16^x`, so this profile has no moment crossing in
`(0,1)`. It is outside the theorem's hypotheses despite passing the other
three fixed-exponent tests, and does not challenge #4483's certified
examples. This strengthened example was supplied by the separate
author-side proof audit for this contribution.

## 5. Scope, evidence and credit

The theorem inherits #4483's all-column arbitrary-input correctness,
disjoint productive owners, literal chronological paid interface, and
permitted and priced whole-job adapters, including input maps. Native
centers and scratch must remain owned until their words restore and erase
them. No input cloning, field aliasing, omitted complement, unpaid move,
or pooling of unfinished calls is introduced here. Integer widths must
still clear every actual chronological batch. Existence of a finite word
and its normalized recurrence gives no numerical productive-width bound
or physical, precision, fixed-tape, stock, analytic-transfer, or recovery
constant. Those obligations remain inherited and unresolved by this note.

The new implication is a sufficient profile criterion for the adaptive
gates and the explicit allowance of the exact crossing as the endpoint of
the funded majorant. The finite compiler is Jacob Alan Sussman's work;
the overlapping integer flow and adaptive/shifted-log argument are zxv's
#4436 and #4483; the corrected mirror-window method is Ryanson Jonathan's
#4459. The related finite-flow, leaf, width and accounting investigations
retain their own contributions and limitations. Their native construction
lineage, including Cinna Davis and the original retained sources, is
unchanged. Prepared for Dillon with substantial OpenAI Codex assistance.
The proof is an author-side mathematical argument, not a formal-kernel
proof or independent human review. Apache-2.0.

## Open next questions

1. Is a weaker, distribution-dependent boundary condition sufficient when
   the pointwise mirror factor reaches source capacity? The first step is
   to retain the exact capped base measure on the offending windows. That
   requires a new bound; this proof uses strict uniform pointwise slack.
2. Can profiles with a favorable moment but no simple crossing satisfying
   the mirror condition use a different height or majorant? The exact
   counterexample above shows why mean separation alone cannot establish
   the present two-tail gates. It does not rule out another compiler.
3. Can the resulting chronological words be emitted with complete native
   physical and precision constants? Start with one small changed-height
   forest and its actual batch widths. The inherited native contracts and
   complete paid implementation remain the blocking obligations.
