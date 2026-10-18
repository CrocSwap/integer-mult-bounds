# Whole-template cost ceilings for native odd-size star observations

The known paired odd-size decoder escapes the even-size COPY obstruction,
but for every odd `k>=5` its literal odd-degree proper-star observations
cannot improve the campaign-start selected bound in the inherited odd-stage
template with at least five stages. Even granting arbitrarily efficient
shared native helpers, free scalar work and restoration, and favorable
unsplit frame climbs, its bit saving satisfies

```text
c < 107/66606 = 0.0016064618803110831...
```

This is below the pinned campaign-start selected value
`1661634653669567/10^18`. The result rejects a specified observation and
compiler class. A separately stated conditional three-stage extension also
excludes odd `k>=7`. Three stages at `k=5`, arbitrary recoded observations,
and later copies whose innovations have smaller frames remain outside these
bounds. No new κ or physically admissible supplier is claimed.

## 1. Observation and compiler hypotheses

Use the full paired k-port family for odd `k>=5` on p original coordinate
pairs, with `v=2^k binom(p,k)` independent scalar sources and rational
incidence labels `chi_S` in dimension `h=2p`. The proposed decoder acquires
every star of each odd degree `1,3,...,k-2` once per local invocation as a
**native observation**: its COPY frame contains every source label in that
star's support. Target corrections at intersection one are granted free.

Preparation may use arbitrarily shared and efficient monotone helpers. Their
scalar work, dirt compensation, restoration and finite compilation charges
are granted zero for this upper bound. However, the required native copies
still pay their frame dimensions. The native condition matters: if a later
literal star is synthesized using earlier copied observations, its innovation
may have a smaller frame than its full source support. Such COPY-assisted
recoding is not covered by the frame lower bound below.

Conditionally retain the inherited odd-stage source/target endpoint schedule
and whole-call hosting accounting, with

```text
L=2K+1 >= 5,    a=h-1=2p-1,    m=1+La,
```

and T replicas. Source and target frame climbs have total rank a in every
local invocation. Whole-call hosting replaces idle ranks by helper residual
widths and the remaining idle complement. Additional whole banks add one
full address dimension m of rank mass for each new live family, leaving the
rank deficit unchanged. These are explicit compiler hypotheses, checked
against the pinned predecessor sources in Section 6. A different compiler
or different endpoint accounting is outside the theorem.

The scalar identity itself is inherited binomial incidence algebra. For
odd k, summing the odd proper stars contained in T evaluates to
`sum_(odd l<k) binom(j,l)` on a source with `j=|S intersect T|`. This is one
at `j=1,k` and zero elsewhere: the full odd sum is `2^(j-1)` for `j>=1`,
and the omitted top term changes the value at `j=k`. Thus these observations
give the target indicator plus the whole intersection-one class. This note
contributes the uniform cost ceiling for the stated physical class, not
that identity or a new construction of its helper word.

## 2. Native COPY rank

For `p>k`, a literal l-star with `1<=l<k` has rational support-label rank
exactly `2(p-l)`. To prove this, fix its defining face J and write its
source labels as `chi_J+chi_A`, with A a signed `(k-l)`-port on the `p-l`
residual pairs. Differences of these labels span the sum-zero subspace of
the residual coordinates. Sign flips give within-pair differences, and
single-pair substitutions give differences between distinct pairs, since
`0<k-l<p-l`. One source label adds the final independent direction.

Conversely, all coordinates in J have the same value, their opposite
coordinates vanish, and the residual-coordinate sum is `k-l` times that
value. This gives the matching dimension upper bound. Keeping only the
required degree `k-2` observations gives

```text
rho = C/v >= [2^(k-2) binom(p,k-2) * 2(p-k+2)]
             / [2^k binom(p,k)]
          = k(k-1)/[2(p-k+1)]
          >= 10/(p-4),    odd k>=5, p>k.             (1)
```

At `p=k`, the degree `k-2` observations alone are nonzero and number
`2^(k-2) binom(k,2)`. Rank at least one per required native copy gives
`C/v>=k(k-1)/8>1`, already excluding positive rank deficit.

As a worked case, at `k=5,p>5`, point and three-coordinate stars give the
more precise native COPY bound

```text
C >= 4p(p-1) + 16(p-3) binom(p,3),
rho >= 10/(p-4) + 15/[(p-2)(p-3)(p-4)].
```

The weaker uniform inequality (1) is sufficient for the cost ceiling.

## 3. A favorable full rank moment

The inherited schedule has `W_0=(L-1)vT` data families and rank deficit

```text
D = T[(L-1)v-LC].                                   (2)
```

The following derivation also checks the mass behind that expression.
For each local invocation, grant each source and target climb as one
unsplit child of rank a. At `0<c<1`, splitting a climb only increases the
sum of child ranks to the power `1-c`.

The actual inherited idle schedule contributes, for each `j=1,...,K-1`,
`4vT` children of rank `2aj` and `2vT` children of rank a. Including all
L local invocations, an optimistic source/idle profile is therefore

```text
rank a:    2vT[L+(K-1)] = 6KvT children,
rank 2aj:  4vT children, for j=1,...,K-1.             (3)
```

Its rank mass is `La(L-1)vT`. Adding the `LTC` required native COPY mass
makes the total `mW_0-D`, as asserted in (2).

For whole-call hosting, an idle rank r is replaced by helper climb pieces
whose total widths are `w_1,...,w_t`, and a residual idle rank
`r-sum_i w_i`. All pieces are nonnegative and sum to r. Since

```text
sum_i r_i^(1-c) >= (sum_i r_i)^(1-c),    0<c<1,
```

this refinement cannot improve the moment relative to the unsplit profile.
It also cannot reduce its first logarithmic derivative: for pieces summing
to r,

```text
sum_i r_i log(m/r_i) - r log(m/r)
    = sum_i r_i log(r/r_i) >= 0.
```

Extra whole banks may increase the actual family count `W_actual` beyond
`W_0`. Each adds mass m per family, so the actual mass remains
`m W_actual-D`. Their logarithmic derivative is nonnegative. This explicitly
accounts for the denominator change: the argument below uses the actual
mass and actual family count, not a comparison that silently fixes W.
All other positive work only worsens the favorable profile.

## 4. A uniform ceiling without a parameter search

Let B denote `sum_r r H(r) log(m/r)` for the source/idle profile (3),
ignoring the positive derivative from native COPY terms. In the actual
normalized moment, `exp(cz)>=1+cz` gives

```text
moment(c) >= 1-D/(m W_actual) + c B/(m W_actual).
```

Consequently any strict saving with `0<c<1` requires `c<D/B`. As `m/a>L`,
profile (3) gives

```text
B > (L-1)vT a F(K),
F(K) = 3 log(2K+1)
       +(4/K) sum_(j=1..K-1) j log[(2K+1)/(2j)].      (4)
```

For every `K>=2`,

```text
F(K) > 6.6606.                                      (5)
```

No monotonicity assumption is needed. At `K=2`, use
`F(2)=3 log5+2 log(5/2)>6.6606`. For `K=3`, keep the `j=2` term to get
`3 log7+(8/3)log(7/4)>7.3299`. For `K=4`, keep `j=3` to get
`3 log9+3log(3/2)>7.8078`. For `K>=5`, use
`3log(2K+1)>=3log11>7.1934`. Each exceeds the common lower bound required
below.

If `p<=14`, equation (1) gives `rho>=1`, hence `D<0`. Otherwise, weakening
both the numerator and the COPY bound in a favorable direction yields

```text
c < (1-rho)/[(2p-1)*6.6606]
  <= (p-14)/[(p-4)(2p-1)*6.6606].                   (6)
```

The quadratic `214p^2-10963p+140428` is strictly positive for every real p:
its leading coefficient is positive and its discriminant is `-18999`.
For `p>14`, this is exactly the inequality

```text
(p-14)/[(p-4)(2p-1)] < 107/10000.
```

Thus

```text
c < 107/66606 < 1661634653669567/10^18.              (7)
```

The bit saving must exceed the assembled κ in the inherited assembly.
Therefore this class cannot improve even the campaign-start selected bound.
The bit half also remains subject to the complex and outer assembly; none
of those costs is removed by this argument.

The displayed logarithm lower bounds have exact rational certificates.
For rational `x>1`, set `z=(x-1)/(x+1)`. The positive series gives

```text
log x > 2 sum_(j=0..99) z^(2j+1)/(2j+1).
```

Using this finite rational sum verifies all four lower bounds above. The
quadratic discriminant and comparison (7) are integer/rational identities.
They were independently checked with standard-library `Fraction` arithmetic;
no floating-point estimate is needed for the ceiling. The numerical decimal
is for orientation only.

## 5. A conditional three-stage extension for odd k>=7

The pinned compiler implements `L>=5`. This section is a conditional
extension of its rank schedule to `L=3`, not an assertion that it emits a
legal three-stage physical supplier. Retain the same endpoint and complete
bank accounting. Now `K=1`, there are no idle intervals, and formula (3)
consists only of the six source/target climbs per port. Formula (4) remains
valid with `F(1)=3log3>3.2958`; for `K>=2` the stronger previous bound applies.

For every odd `k>=7`, the highest required degree gives

```text
rho >= k(k-1)/[2(p-k+1)] >= 21/(p-6),    p>k.
```

The `p=k` boundary was already excluded. Positive deficit now requires
`p>27`. The same favorable argument gives

```text
c < (p-27)/[(p-6)(2p-1)*3.2958].
```

The quadratic `106p^2-10689p+270318` has discriminant `-360111` and is
positive everywhere. Therefore

```text
(p-27)/[(p-6)(2p-1)] < 53/10000,
c < 53/32958 = 0.001608107288063596...
              < 1661634653669567/10^18.
```

The logarithm series from Section 4 certifies `3log3>3.2958` exactly;
the discriminant and final comparison are rational checks. This excludes
odd `k>=7` even in that favorable three-stage extension. It leaves
`k=5,L=3` and the paired-triple case open in the stated cost model.

## 6. Scope, predecessors and immutable sources

The compiler and hosting trace is pinned to main commit
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. The same pinned selected
certificate supplies the comparison value in (7); it is a historical
campaign-start reference, not a claim that the selected frontier is frozen.
Any later increase of that bound remains above this ceiling.

The odd-stage kernel is DreamingOfClouds' generalization of earlier
chafreaky, Zhihao Chen and eumemic integration. The whole-call hosting
mechanism is inherited from DaysSky and subsequent hosting refinements.
The paired-cube geometry and scalar decoder are credited to icekylinx and
eumemic, and the general binomial expansion is already recorded in
[`single-intersection.md`](../../docs/research/single-intersection.md).
The older bounded unshared three-tensor-stage screen in
[`network-screens.md`](../../docs/research/network-screens.md) is a different
cost class. This note uses the inherited shared odd-stage idle schedule and
its full moment instead of repeating that screen.

Concurrent [PR #958 by Ross Richardson](https://github.com/CrocSwap/integer-mult-bounds/pull/958),
at head `28d68c88f0184835d8c8a7266ab8d0dad3f18a8a`, studies the five-port
**point-star-only** decoder. It needs readable corrections at overlaps one
and three and uses the quadratic pairing `2(j-1)(j-3)` to realize both
zero classes. Its separate-star copy trees and active-frame rank witnesses
give a distinct cost ceiling. Here the extra three-star observations at
`k=5` cancel the overlap-three terms, so the stated readability hypothesis
is only overlap one and the labels are the original incidence vectors.
Neither note's geometry or accounting bound is silently applied to the
other. The comparison is based on the actual proof at the pinned PR head.

| Pinned source | Git blob |
| --- | --- |
| `certificates/selected-result.json` | `1f107b55a2f045fa66d9c35d658b3b79549f5ba6` |
| `research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py` | `3df12bd632f1fdba825ced57110a1fee82eb2857` |
| `research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py` | `8864ca9b942a3507171edca0cf6cbaaf10fcf434` |
| `research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/idle-axis-hosting/hosting_core.py` | `68b536daa9e6546c0aa046934bf840aaa3c3fde3` |
| `docs/research/single-intersection.md` | `7cdf4555e9f9e043debbfe1e3a49fa201234d710` |
| `docs/research/network-screens.md` | `bc69870f7cfa30752ee898719055db6a8b6903f7` |

This is not an end-to-end supplier replay or a general lower bound on
odd-k decoding. The genuine remaining alternatives include three-stage
odd-five helper/bank designs, the paired-triple case, a cheaper native
recoded observation family, and COPY-assisted innovations. They require
their own frame histories and
complete invoices. The even-size result in
[COPY-OBSTRUCTION.md](COPY-OBSTRUCTION.md) covers a different, wider
observation class through its odd integral diagonal; that certificate is
unavailable for the present intersection-one odd-k geometry.

Prepared by Sam Sung with substantial OpenAI Codex assistance; Apache-2.0.
