# Conditional integer-profile envelope for the 8/9 moment tails

This lemma concerns scalar profiles. It neither constructs a receiver nor admits
an algorithm. All 240 H25 targets in the baseline remain hypothetical. The peer
precision lane supplied the robustness extension; root supplied its baseline
bounds and an independent written audit. Their LOCAL hashes and credit are
retained without publishing private receiver or physical-word data.

## Hypotheses and conclusion

Set

```
C=330007/100000000,  t=1-C,  rho=1/1000000000,
c=8, b=9, u=1/5, v=1024,
P0=6611 H1+1236 H2+1530 H3+381 H4+120 H5+8 H8,
T0=84 H4+21 H7+117 H8+954 H9+240 H25.
```

For a finite histogram X write `X_s=sum_r X[r] r^s` and let `B=sum_r T[r]`.
Every rank is a positive integer. A has finite nonnegative **integer**
multiplicities, L is an actual subhistogram of T0, and

```
P=P0+A,  T=T0-L.
```

No new targets, paid deletions or signed netting are allowed. A represents all
gross additions, and L every surrendered target. Define

```
R0=(1-rho)(T0)_t-(P0)_t.
```

Assume the **one strict mixed inequality**

```
A_t+(1-rho)L_t < R0 < 43.
```

The upper bound43 is an explicit conditional premise. Public PR5418's exact
profile model and numerical result supply its motivating source, but this package
does not recompute that price or prove that a future physical ledger fits it.
The conclusion below applies to every A,L satisfying the mathematical hypotheses.

Define

```
alpha=P_t/T_t,
gamma=P_(t+u)/(8^u T_t),
delta=9B/(8^C T_t).
```

Then `T_t>0`, `alpha<1-rho`, `gamma<97/100`, `delta<97/100`, and

```
alpha^1024 + 2gamma^1024 + 2delta^1024 < 1.
```

This is the conditional three-moment envelope. It establishes no physical
endpoint, full compiler/outer admission, precision/stock/tape result, κ gain,
selected-record change or independent human/formal-kernel acceptance.

## 1. Coarse baseline bounds from finite integer certificates

The parameters give `0<C<1/256`, `1/2<t<1` and `t+u>1`. The baseline paid rank
mass is15861. The target rank mass is16005, its count is1416 and its largest
rank is25. All paid ranks are at most5 except eight rank8 jobs, of mass64.

The first five positive binomial terms certify

```
(65/64)^256=(1+1/64)^256
 >sum_(k=0)^4 binom(256,k)/64^k >25.
```

The final comparison is finite integer arithmetic after multiplying by64^4.
Therefore `25^(1/256)<65/64`. For every target rank `1<=r<=25`,

```
r^t=r*r^(-C) >= r*25^(-C) > r*64/65.
```

Summing gives `(T0)_t>16005*64/65=1024320/65`.

Similarly the integer comparison `8*19^5>5*20^5` gives
`(5/8)^(1/5)<19/20`. For paid ranks at most5, use this factor and `r^t<=r`.
For rank8 use `(8/8)^u=1` and `8^t<8`. Thus

```
(P0)_(t+u)/8^u
 =sum_r P0[r] r^t (r/8)^u
 <(19/20)(15861-64)+64
 =(19/20)*15861+64/20=301423/20.
```

These are bounds for this exact baseline. A changed baseline needs a new bound.
No fractional power, logarithm, pricing or transcendental engine is evaluated by
the finite certificate verifier.

## 2. Consequences of the single mixed budget

All terms are nonnegative, hence `A_t<43`. Also
`L_t<43/(1-rho)<44`, since `rho<1/44`. These are consequences of the same
mixed inequality. They are not independently spendable allowances and do not
replace it.

If rank r occurs in A then its multiplicity is at least1, so

```
r^t <= A_t <43.
```

Because r>=1 and t>1/2, `sqrt(r)<=r^t<43`. Therefore

```
r<1849<1944=8*3^5,  (r/8)^(1/5)<3.
```

For nonempty A it follows that

```
A_(t+u)/8^u <3 A_t<129.
```

If A is empty its numerator is zero and the strict129 bound still holds.
Integer multiplicity is essential: arbitrarily small fractional weights can
hide arbitrarily large ranks at bounded raw moment. Negative weights or paid
deletions can likewise conceal larger gross additions. Those domains are excluded.

The rank estimate alone is not an ambient certificate. In particular `r<1849`
does not imply145-axis geometry or the existence of canonical whole-job adapters.
No conclusion about a complete physical program follows from that coarse scalar
bound, even when a stronger rank estimate might be available separately.

## 3. Exact rational tail margins

Since T=T0-L,

```
T_t >1024320/65-44=1021460/65>0.
```

The baseline and addition bounds give

```
gamma <(301423/20+129)/(1021460/65)
       =19760195/20429200 <97/100.
```

The cross-multiplied strict margin is exactly

```
97*20429200-100*19760195=5612900>0.
```

Because L is a subhistogram, `B<=1416`. Since C>0, `8^C>1`; consequently

```
delta <1416*9/(1021460/65)
       =828360/1021460 <97/100,
97*1021460-100*828360=16245620>0.
```

Finally the original mixed inequality gives

```
(1-rho)T_t-P_t =R0-A_t-(1-rho)L_t>0.
```

Divide by the proved positive T_t to obtain `alpha<1-rho`.

## 4. Bernoulli and the complete scalar envelope

For 0<rho<1, Bernoulli's inequality applied to
`(1-rho)^(-1024)=(1+rho/(1-rho))^1024` gives

```
alpha^1024 <(1-rho)^1024 <1/(1+1024rho).
```

The first three binomial terms prove

```
(100/97)^32=(1+3/97)^32
 >1+96/97+496*9/97^2>2.
```

Thus `(97/100)^1024<2^(-32)`, since1024=32*32. Combining the bounds,

```
alpha^1024+2gamma^1024+2delta^1024
 <1/(1+1024rho)+4/2^32 <1.
```

The last inequality is equivalent to
`rho>1/[256*(2^32-4)]=1/1099511626752`, and holds for rho=10^(-9).
The verifier checks the exact rational positive gap without evaluating any
unknown profile moment or fractional power.

## 5. Honest accounting, quantification and remaining joins

The universal coverage is the written argument above, not finite enumeration.
The executable checks its finite constants, model restrictions and meaningful
countercontrols. For example, A=42H1 and L=H4 meet the separate loose bounds
A_t<43 and L_t<44, but

```
A_t+(1-rho)L_t >42+2(1-rho)>43,
```

since t>1/2. Thus those separate bounds cannot supply the mixed hypothesis.
This is a real integer-ledger countercontrol, not a hypothetical fractional job.

If a later version adds eight H1 jobs, they spend this same allowance. Write
`A_total=8H1+A_future`, or equivalently use P1=P0+8H1 and R1=R0-8; reconstruct
total A before invoking this lemma. There is no fresh43 allowance on top.

A future actual ledger must still establish its complete P/T binding, the one
strict mixed inequality and independently earned canonical productive targets.
All240 H25 remain hypothetical here. No ambient, owned-entry/return, restoration,
ordinary movement/cost, norm/error, semantic constant, stock, fixed-tape,
chronological splitting/completion, compiler, outer or recovery admission is
supplied. This scalar lemma cannot certify the target κ>=.0033 objective.

## Credit

Peer precision owns the integer-profile robustness extension. Root supplied the
baseline elementary derivation and independent written audit. Their LOCAL hashes
are retained as credit references only. Public PR5418 supplies the explicit P0/T0
model and motivating upper-bound result, separate from canonical ancestry.
Retain the construction/resource owners and Dillon, Ali Romman, Cao Yifan,
Cinna Davis, zxv, Jacob Alan Sussman, Dugongue, Chris R / Clear1nsight and all
native/helper/compiler/precision/analytic/recovery predecessors. New rational
certificate checking and publication packaging by Chris R / Clear1nsight with
substantial OpenAI Codex assistance; Apache-2.0. No construction priority,
independent human approval or formal-kernel proof is claimed.
