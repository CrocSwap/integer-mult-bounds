# Exact relative power-tariff threshold for the frozen PR6375 bill

This proof concerns the **difference between two complete formal invoices**.
It does not establish a new multiplication exponent or native/physical
applicability. The exact local words, common caller, complete paid and
productive profiles, all carrier trips and all six productive debits were
independently extracted in the preserved
[PROFILE-PROOF.md](PROFILE-PROOF.md), with receipts
[PROFILES.json](PROFILES.json) and [ORACLE-PROFILES.json](ORACLE-PROFILES.json).
This continuation adds the whole-domain sign proof and a rational enclosure
of its one interior power-exponent threshold.

## 1. Source-bound statement

Keep candidate PR6375 head
`247b5c319b9f58fe9ee61dbf80697f8a9a429831` and its retained PR6372 baseline
at originating head `b556600ffe14be72406b03a47c661f3c7f1aff06` fixed.
The candidate WORD blob is `b1cfd03abe9128cf5a3908fbd82652e5e8a2e292`,
the retained baseline WORD blob is
`0af79e58172f85c302c35b193205c0b185b09393`, and the common controller blob
is `1f2e375b24aba5fb25580dfea7fab7a2049f3eb8`.
[SOURCE-PINS.json](SOURCE-PINS.json) authenticates the exact source bytes.
No conclusion here transfers automatically to another head or caller.

For the power tariff `H_r=r^s`, let

`M(s)=sum_r (T_r-P_r) r^s`

be the declared complete productive-minus-paid moment. The independently
extracted local differences are

`Delta P = 6H_1-3H_3+3H_4-3H_5`,
`Delta T = 6H_8-6H_9`.

All nineteen LOCAL copies are charged and all common queries, paired whole
idles and main diagonal targets remain in both complete profiles. Therefore

`M_new(s)-M_old(s)=19g(s)`,

`g(s)=-6+3*3^s-3*4^s+3*5^s+6*8^s-6*9^s`.

**Theorem.** There is exactly one number `sigma` in `(0,1)` with
`g(sigma)=0`. For `0<s<sigma` the candidate has strictly smaller formal
margin than its baseline; for `sigma<s<1` it has strictly larger formal
margin. At `s=1` the margins are equal. The factor19 is positive, so the
same sign classification holds for the complete invoice difference.

This is a relative comparison. A positive difference does not by itself
prove that either complete margin is positive, that the underlying supplier
is physically realized, or that a claimed kappa is admitted. The author's
separate proof of uniqueness of the complete raw-kappa crossing below its cap
was already present and is not claimed as a newly resolved gap.

## 2. Derive the proper-integral factorization

Normalize `f(s)=g(s)/3`. Its coefficients `c_r` are:

| r | 1 | 3 | 4 | 5 | 8 | 9 |
|---:|---:|---:|---:|---:|---:|---:|
| c_r | -2 | 1 | -1 | 1 | 2 | -2 |

They satisfy `sum c_r=-1` and `sum r*c_r=0`. In particular,
`sum c_r(r-1)=1`.

For any real `s` and any `r>=1`, integrate the second derivative of
`x^s` twice on the finite interval `[1,r]`:

`r^s-1-s(r-1)`
`= integral_1^r integral_1^t s(s-1)x^(s-2) dx dt`
`= s(s-1) integral_1^r (r-x)x^(s-2) dx`.

Every integrand is continuous there. Interchanging this finite double
integral is legitimate; no behavior at zero or infinity is involved.
Multiplying by the six coefficients and summing gives

`f(s)=(s-1)[1+sI(s)]`,

`I(s)=integral_1^9 K(x)x^(s-2) dx`,
`K(x)=sum_r c_r (r-x)_+`.

Here `(r-x)_+=max(r-x,0)`. Deriving the sum interval by interval yields:

| Interval | K(x) |
|---|---|
| [1,3] | 2-x |
| [3,4] | -1 |
| [4,5] | 3-x |
| [5,8] | -2 |
| [8,9] | 2x-18 |

For example, on `[1,3]` the rank1 term vanishes, the remaining first
moment is2 and their total coefficient is1, giving `2-x`. At each
successive rank remove exactly that rank's term. Endpoint values agree,
so this is one continuous piecewise-linear kernel. It is positive on
`(1,2)`, zero at2, and negative on `(2,9)`.

The integral is proper and finite. On every compact interval of real `s`,
`x^(s-2)` and its derivatives in `s` are uniformly bounded on `[1,9]`.
Thus `I` is continuously differentiable there and differentiation under
this integral is justified. The finite kernel breakpoints do not affect it.

## 3. Establish the first endpoint without decimal logarithms

Differentiate the finite sum at zero:

`f'(0)=log3-log4+log5+2log8-2log9=log(80/27)`.

Differentiating the derived factorization at zero gives

`I(0)=1-f'(0)=1-log(80/27)`.

For `z>1`, the elementary bound

`log z > 2(z-1)/(z+1)`

follows because the difference is zero at1 and its derivative is
`(z-1)^2/[z(z+1)^2]>0`. Apply it to2 and40/27:

`log(80/27)=log2+log(40/27)`
`> 2/3+26/67 = 212/201 > 1`.

Hence `I(0)<0`. This is a strict exact inequality, not a sampled
logarithm approximation.

## 4. A single kernel sign change forces strict decrease

For `s>0`, compare the integral to its value at zero:

`I(s)-2^s I(0)`
`= integral_1^9 K(x)x^-2 [x^s-2^s] dx < 0`.

On `(1,2)` the kernel is positive and the bracket negative; on `(2,9)`
the signs reverse. The product is strictly negative on sets of positive
measure. Therefore `I(s)<2^s I(0)<0`. Together with the previous section,
`I(s)<0` for every `s>=0`.

Similarly,

`I'(s)-log2*I(s)`
`= integral_1^9 K(x)x^(s-2) log(x/2) dx < 0`.

Again both sides of2 contribute strict negative sign. Since `log2>0`
and `I(s)<0`, this implies `I'(s)<log2*I(s)<0` for `s>=0`.

Set `L(s)=1+sI(s)`. Then

`L'(s)=I(s)+sI'(s)<0` for every `s>=0`,

including zero, where `L'(0)=I(0)<0`. Thus `L` is strictly decreasing
on `[0,infinity)`, and `L(0)=1`.

## 5. The other endpoint and the complete sign classification

From `f(s)=(s-1)L(s)`, differentiation at1 gives `L(1)=f'(1)`.
The literal finite sum yields

`f'(1)=40log2-33log3+5log5`
`=log(2^40*5^5/3^33)<0`.

The strict comparison is an exact integer one:

`2^40*5^5 = 3435973836800000`,
`3^33 = 5559060566555523`,
`3^33-2^40*5^5 = 2123086729755523 > 0`.

Continuity, `L(0)>0`, `L(1)<0` and strict decrease give exactly one
zero `sigma` in `(0,1)`. Since `s-1<0` throughout that interval,
the identity `g(s)=3(s-1)L(s)` reverses the sign of `L`:

- `0<s<sigma`: `L(s)>0`, so `g(s)<0`;
- `sigma<s<1`: `L(s)<0`, so `g(s)>0`;
- `g(1)=0`, by the exact zero first rank moment.

There are no other zeros in `(0,1)`. The endpoint at1 is separate from
the interior threshold; `f'(1)<0` also shows that this endpoint zero is
simple. At the interior zero,
`g'(sigma)=3(sigma-1)L'(sigma)>0`, because both factors are negative;
thus that zero is simple as well. No numerical grid or general root-count
black box is needed for this source-specific conclusion.

## 6. Rational isolation by two exact arithmetic methods

The exact isolating interval is

`11712509413/13421772800 < sigma < 5856254707/6710886400`.

The upper endpoint has the same denominator after multiplying its numerator
by2, so the interval width is exactly `1/13421772800 < 1/10^10`.
Both arithmetic implementations independently enclose the signed gain at
these two fixed rational points. Their full rational intervals lie strictly
inside the following common, simpler outward bounds:

| Point | Strict certified bounds on local g |
|---|---|
| `11712509413/13421772800` | `-8/10^11 < g < -7/10^11` |
| `5856254707/6710886400` | `1/10^11 < g < 2/10^11` |

The complete gain is19 times each interval. These are rational inequalities,
not rounded decimal estimates. The theorem above proves there is exactly
one interior root, so strict opposite signs at these endpoints rigorously
isolate that root. The finite sign evaluations by themselves would not
exclude further roots elsewhere.

### Logarithm and positive exponential series

[verify_tariff.py](verify_tariff.py) authenticates the fourteen preserved
scientific files, reads both exact complete-profile receipts and derives
their common coefficient difference before evaluating it. It imports no
profile producer, author price engine or other arithmetic checker.

For each positive rank `r`, choose `e` with `2^e<=r<2^(e+1)`, and use

`log r = e log2 + 2 atanh((r-2^e)/(r+2^e))`.

The reduced argument `z` lies in `[0,1/3]`; log2 uses `z=1/3`.
After48 positive terms
`2 sum_(j=0)^47 z^(2j+1)/(2j+1)`, the remaining tail is nonnegative
and at most `2z^97/[97(1-z^2)]`: every omitted denominator is at least97,
and the remaining powers are geometric. This gives rational logarithm
bounds, rounded outward on the `10^-40` grid.

For `x=s log r`, divide its entire interval by16 and require its upper
endpoint to be at most1/4. At a nonnegative argument `y`, the exponential
polynomial through degree24 is a lower bound. If `t25=y^25/25!`, every
successive tail ratio is at most `y/26`, so an upper bound is that
polynomial plus `t25/(1-y/26)`. Evaluate the lower polynomial at the
lower argument and the upper bound at the upper argument. Four interval
squarings recover bounds on `exp(x)=r^s`; monotonicity on nonnegative
numbers and outward grid rounding preserve them after every square.
The final power bounds are rounded outward on the `10^-30` grid.

Each positive gain coefficient uses the lower power bound for the lower
gain and the upper for the upper gain; negative coefficients exchange
those choices. Thus cancellation cannot turn pointwise power approximations
into unsupported signed bounds. The fixed-point certificate is
[RELATIVE-RESULT.json](RELATIVE-RESULT.json).

### Independent generalized-binomial quotient

[oracle_tariff.py](oracle_tariff.py) uses the same frozen source profiles
as authenticated data, but no logarithm/exponential evaluator or peer
implementation. For `0<s<1` and `r>1`, put

`x=(r-1)/(r+1)`, so `r^s=(1+x)^s/(1-x)^s`.

On this source support `0<x<=4/5`. The positive binomial magnitudes obey
`b1=sx` and `b_(k+1)=b_k x(k-s)/(k+1)`. Their ratio lies strictly
between zero andx, so they decrease. The numerator is
`1+b1-b2+b3-...`, whose alternating remainder is bounded by the next
term. The denominator is `1-b1-b2-b3-...`, whose omitted positive
tail magnitude is at most `b_(N+1)/(1-x)`.

The oracle bounds192 terms with an outward `10^-40` rational grid at
each positive recurrence step. Because192 is even, the numerator's
remaining signed tail is nonnegative and at most the next-term upper
bound. The denominator's lower endpoint subtracts both the upper partial
sum and the geometric tail upper bound; its upper endpoint subtracts the
lower partial sum. After checking the denominator lower bound is positive,
the power interval is the numerator lower bound divided by the denominator
upper bound through the numerator upper bound divided by the denominator
lower bound. Final outward `10^-30` rounding and signed coefficient
selection give an independent rational gain enclosure. Rank1 is exactly1.
The certificate is [RELATIVE-ORACLE.json](RELATIVE-ORACLE.json).

The two methods share source data and the analytic theorem, not their power
evaluation algorithms. Both use fixed bracket endpoints in registered
verification. No decimal bisection or sample grid is a dependency of the
certificate. Source-claimed-power and square-root examples are relative
bill comparisons only, not admitted kappa or positive-complete-margin claims.

## 7. Scope and predecessor credit

The preserved profile proof states the declared nested-frame MOVE tariff,
productive helper endpoint contract and fixed caller rank interface. This
proof uses those premises; it does not establish the new arbitrary-input
lift response maps, scalar/native endpoint equality, actual caller contact
semantics, native phases/all columns/all widths, owned erasure, complete
ordinary funding, compiler or outer admission. All five retained framework
assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, `analytic_recovery`. The selected frontier is unchanged.

DreamingOfClouds with Claude Opus5.5 assistance supplies PR6375, its
reported separate exact row/ownership audit and its approximate tariff
sensitivity observation. Ali Romman supplies the PR6372/6353/6349/6348
source and caller line, building on DreamingOfClouds PR6314. Preserve
Cinna Davis's productive controller/thin-query interface, Jacob Alan
Sussman's productive recursion, zxv and Cao Yifan's interval/compiler
work and the complete native/helper/BIT/analytic attribution in
[sources/NOTICE](sources/NOTICE). PR6359 and PR6376 retain their distinct
finite invoice and scalar endpoint audit credit.

Taylor's integral remainder, positive-kernel comparisons, logarithm
inequalities and single-crossing arguments are classical methods. The
repository's general-rank root-budget and exact interval tools, PR5174's
designed rank-exchange thresholds and PR5772's different P104 chart-tariff
switches are prior context. This contribution claims the exact matched-source
application and rigorous relative-tariff classification, not a new general
analytic method. New audit/proof work is by ToikY with substantial OpenAI
Codex assistance; same-session agent review is not independent human or
formal-kernel acceptance.
