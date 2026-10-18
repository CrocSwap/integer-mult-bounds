# H6 banked-invoice source and threshold audit

**Prepared for Andrey Mas through ChatGPT.** Model and geometry: Dominik
Scholz / PR606 and its NOTICE. H6 interpretation and six quoted thresholds:
DreamingOfClouds / PR1590, with Claude Opus 5.5 via Claude Code. New work here
is the bounded arithmetic audit and its proof, not a new pricing model.
See `NOTICE.md` for the complete attribution boundary and `SOURCES.md` for
references [S1]–[S8].

## 1. Claim and result

For the twelve inputs below, the largest nonnegative integer helper count
whose **returned invoice lower scaled κ endpoint, divided by 10^18, strictly
exceeds the specified exact target** is the stated R. The source
`threshold(..., bad=False)` returns the same integer in each case. The proof
certifies R and R+1 and excludes every greater count by analytic monotonicity
of the true pressure root. It does not assume monotonicity of floating
nomination or of rounded endpoint output.

| Exact comparison target | L = 3 | L = 5 | L = 7 |
|---|---:|---:|---:|
| Author's rounded PR890: 0.001661957775 | **80,558** | **89,683** | **80,753** |
| Retained PR890: 0.001661957774647029 | **80,558** | **89,683** | **80,753** |
| Pinned selected record: 0.001672660197076918 | **79,880** | **88,765** | **79,778** |
| Author's quoted open-PR1424: 0.001676855229071321 | **79,617** | **88,409** | **79,399** |

All six originally quoted integers reproduce. The selected-target allowances
are smaller than the rounded-PR890 allowances by 678, 918, and 975 helpers,
respectively. The two PR890 inputs remain distinct even though their integer
answers coincide. The longer PR1424 title endpoint is not substituted for
the last row. PR1424 is a comparison target, not the pinned selected result.

Every comparison is exact. In fact, at each R+1 the **upper** scaled endpoint
is already below its target. No boundary tie remains unresolved in these
twelve cases. These are conditional invoice allowances only; no new κ,
compensation construction, or supplier admission follows.

## 2. Frozen inputs and source binding

The only stages are L in {3,5,7}. The inputs are n=30960, h=17,
`hist={17:256,15:560}`, data path `[16]`, helper path `[1,7,8,1]`,
`virtual=False`, and `bad=False`. The unchanged factor is the supplied
K=(t^3−4t)/48, of rank 816. Its geometry and full-rank compensation receipt
are inherited inputs, not independently reconstructed geometry in this study.
The center bill is exactly

\[
 C=17\cdot256+15\cdot560=12752.
\]

The four full source files were authenticated against the provided SHA-256
values before importing PR606. Their paths, byte counts, hashes, and public
URLs appear in `SOURCES.md` and `EVIDENCE.json`. No upstream file was changed.
Only the narrow invoice/threshold import closure was evaluated. Neither
`banked.run()` nor `costs.source_check()` was called; no unavailable historical
data were required.

The source's `costs.FRONTIER` is exactly 0.001612719427075359, the historical
PR592 comparison. It is a fifth value, **excluded** from the twelve cases.
The retained PR890 and pinned selected targets were also read in their
respective public JSON `kappa` fields [S5,S6]. Their construction chains and
complete source manifests were not replayed here.

## 3. Paid stock, children, and rank mass

Set d=h−1=16 and

\[
 m=16L+1,\qquad W_0=(L-1)n,\qquad D=W_0-LC,
 \qquad q=\lfloor m/17\rfloor,\quad p=m-17q.
\]

Here D is a scalar deficit, not a matrix. To avoid confusing the packing
integer q with an exponent, the pressure exponent below is always α.

| L | m | W0 | D | q | helper pad p | child cap | actual largest child |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 49 | 61920 | 23664 | 2 | 15 | 34 | 17 |
| 5 | 81 | 123840 | 60080 | 4 | 13 | 57 | 32 |
| 7 | 113 | 185760 | 96496 | 6 | 11 | 79 | 64 |

The cap is `isqrt((m*m−1)//2)`, so an integer child rank r at or below the
cap satisfies the strict guard m²>2r². A term is recorded as (mass M, base
b=m/r). The base has active data mass 2nL·16 at rank 16 and center masses
L·17·256 and L·15·560 at ranks 17 and 15. The retained idle-rank lists are

```
L3: []
L5: [32, 32, 16]
L7: [64, 32, 16, 32, 64, 16]
```

Each idle occurrence has mass 2nr at its actual rank r. All listed idle ranks
already obey their stage's cap; no splitting is needed. This is the actual
`banked.base` accounting, with no added free idle-hosting credit. In
particular, it is not an unannounced substitution of a different idle model
elsewhere in `costs.py`. Summing the base terms gives mW0−D exactly.

One ordinary helper follows nested increments 1,7,8,1, totaling 17. Its four
path terms have masses L,7L,8L,L at the corresponding ranks. The paid pad
term has mass Lp/q at rank p. Therefore the total mass per helper is

\[
 L(1+7+8+1)+Lp/q=17L+Lp/q=Lm/q.
\]

Adding R such helpers adds stock LR/q, **as well as** their path and pad
children. Thus

\[
 W_R=W_0+LR/q,\qquad
 \sum M=mW_0-D+RLm/q=mW_R-D.
\]

This is the complete rank-mass identity for this frozen invoice. Adding
children without their banked stock, or stock without residual/pad children,
is not the same model. Omitting the pad fails the identity. The two rank-one
entries are both present; one helper is not one scalar term or copy.

The physical interpretation is conditional on [S1]: a helper is a restored
physical local register role, with the specified path, banked across
separately invoked replicas. Replicate by a multiple T of q, pack TR
width-17 residual slots into TR/q full banks at each stage, and pay each
bank's remaining rank p. The slots must be disjoint. Fractional reported
stock is a normalization of that integral replicated accounting, not a
fractional physical register.

The ordinary zero-entrance assumption explains why this particular bank
wrapper has no virtual-entrance spectators. It does not waive spectators
needed by an eventual compensation implementation. Numerically checking
that the four increments sum to 17 does not prove gate legality, physical
loading, arbitrary-dirt restoration, or the existence of those paths.

## 4. Pressure model and maximality proof

For a child of mass M and base b=m/r, define its pressure at α≥0 by

\[
 M(b^\alpha-1).
\]

Let P0,L(α) be the sum for the base terms. A unit helper contributes

\[
 H_L(\alpha)=L\left[
 2(m^\alpha-1)
 +7((m/7)^\alpha-1)
 +8((m/8)^\alpha-1)
 +\frac p q((m/p)^\alpha-1)\right].
\]

The two rank-one increments explain the coefficient 2. All actual bases
exceed 1; masses are nonnegative, with positive base mass. Therefore

\[
 P_{L,R}(\alpha)=P_{0,L}(\alpha)+R H_L(\alpha)
\]

is continuous and strictly increasing in α, starts at zero, and tends to
infinity. Since D>0, there is a unique positive root αR of P=D. Its nominal
κ is κR=αR/(1+αR). For α>0, HL(α)>0. If R2>R1 then
P(L,R2,αR1)>D, hence αR2<αR1 and κR2<κR1. This proves strict decrease of the
**true** root for all finite nonnegative helper counts, not merely at
sampled integers.

For a target τ in (0,1), put a=τ/(1−τ). Then

\[
 \kappa_R>\tau\quad\Longleftrightarrow\quad P_{L,R}(a)<D.
\]

The exact real helper boundary is

\[
 x_L(\tau)=\frac{D-P_{0,L}(a)}{H_L(a)}.
\]

All twelve cases have positive numerator. With outward bounds P0−≤P0≤P0+
and 0<H−≤H≤H+, define

\[
 x_-=(D-P_{0,+})/H_+,\qquad
 x_+=(D-P_{0,-})/H_-.
\]

The checker proves **R<x−≤x+<R+1** in every case. It also directly proves
P(L,R,a)<D<P(L,R+1,a) by rational outward pressure bounds. Thus the exact
pressure comparison has maximum R, with no equality ambiguity.

For the specified *invoice* criterion, an additional fact is required:
its rounded lower endpoint at R must itself exceed τ. That fact is checked
separately. At R+1 the returned rounded upper endpoint is below τ, proving
κR+1<τ. True-root monotonicity then excludes every R′≥R+1, independently of
how the floating nomination or its rounded output behaves at R′. Any
successfully returned certified lower endpoint is below its true root.
Consequently R is the largest integer for the requested invoice criterion,
without needing to certify monotonicity of the floating program or search
a huge integer interval. No claim is needed that `invoice` returns a usable
bracket for arbitrarily large R.

## 5. Exact scaling and the distinction from threshold()

The source first makes a floating nomination, then takes an integer z on
the 10^-15 α grid. Its certified bracket is

\[
 a_-=(z-2)/10^{15},\qquad a_+=(z+3)/10^{15},
\]

with exact outward sign checks P+(a−)<D<P−(a+). The returned integers are

\[
 s_- =\lfloor10^{18}a_-/(1+a_-)\rfloor,\qquad
 s_+ =\lceil10^{18}a_+/(1+a_+)\rceil.
\]

For τ=u/v, the task's strict test is the integer inequality

\[
 v\,s_->10^{18}u.
\]

It is not a float comparison, and equality fails. It is also not the same
predicate as P(τ/(1−τ))<D. The latter compares the true pressure root; the
former loses some headroom to the certified bracket and scaling.

The supplied certificate additionally proves
P+(z/10^15)<D<P−((z+1)/10^15). Thus each recorded z is exactly the floor of
10^15 times the true root. The rational verifier does not trust or execute
floating nomination. It checks this grid cell and reconstructs the source's
wider bracket and both scaled endpoints exactly. A different platform's
source nomination is not silently accepted if it produces a different
receipt; `audit.py` reports such a mismatch, while the rational certificate
remains independently checkable.

The source `threshold()` floors the two bounds x− and x+ and requires equal
floors. In general, for strict R<x, the largest integer is ceil(x)−1, not
unconditionally floor(x). An exact integer tie requires separate treatment;
an interval that straddles an integer is unresolved. Clamping a negative
floor to zero also does not prove zero helpers are feasible. In these twelve
cases none of those caveats is active: the verified open inequalities
R<x−≤x+<R+1 make `threshold()`'s returned floor correct for the exact-pressure
criterion. Agreement with the rounded invoice criterion is then proved by
the distinct endpoint checks, not presumed.

A concrete rejection control uses the first row's own lower endpoint as a
synthetic τ. The invoice strict comparison is false by equality, while the
true pressure-root comparison is certified true. This is a same-row
semantics control, not a thirteenth scientific comparison. Additional
controls reject an exact tie and a straddled real-boundary interval rather
than silently flooring them into an asserted strict allowance.

## 6. Why the numerical certificates are rigorous

For rational b≥1, the logarithm engine writes b=2^e u with 1≤u<2 and uses
z=(u−1)/(u+1). The first 24 positive terms of

\[
 \log u=2\sum_{j\ge0}\frac{z^{2j+1}}{2j+1}
\]

form a lower bound. The remaining tail is at most
2 z^(49)/(49(1−z²)). The same bound at u=2 encloses log 2; adding e copies
encloses log b. Lower/upper outward rounding to denominator 10^40 preserves
both inequalities.

For 0≤x−≤x+<1, the degree-12 Taylor polynomial for exp(x−) is a lower bound.
At x+, the next term is x+^13/13!, and the subsequent term ratios are at
most x+/14. Adding the geometric majorant
(x+^13/13!)/(1−x+/14) is an upper bound. All exponent/log arguments used by
the certificate satisfy these hypotheses. A second outward rounding to
10^40 again preserves the inequalities. Multiplication by nonnegative
masses and summation preserve the pressure enclosures. No floating number
is used as an acceptance sign in this reasoning.

The complete intervals and margins are in `EVIDENCE.json`. There are 24
boundary invoice records across twelve cases, representing 18 distinct
(L,R) pairs because the two PR890 targets share their counts. This is not
sampling: the finite checks certify the stated exact inputs, and the
analytic monotonicity argument covers every greater integer helper count.

## 7. Physical meaning and remaining obligations

A positive allowance is conditional on the exact base terms and helper
path. It is not a fully paid compensation profile. The original response
explicitly leaves unpaid the K encoder beyond the base terms, compensation
chronology and arbitrary-dirt restoration, including frame-zero
precompensation and the stated target cap-15/FULL restriction, spectators or
padding beyond `helper_pad`, and sharing between compensation and other
stages [S4]. These remain obligations in this audit. The four numeric
invoice files do not contain the scalar word or target frame history needed
to certify them. No cap-15 loading/chronology theorem is inferred merely
from the width-15 center histogram.

The stated helper path and the single `[16]` data climb must themselves be
realizable under those constraints; total rank alone does not prove either
path is available. Sharing is not credited here, nor is a cost for sharing
invented. A construction with different paths, stock reuse, or coverage must
receive its own complete invoice; this is not a universal helper-count
obstruction for changed models.

The quotient 30960/R is a **budget ratio**, using the supplied full-rank
compensation demand. It is not measured throughput or a proved amount of
rank that a physical helper can load, deliver, or restore. For example,
30960/80558=15480/40279≈0.384319, whereas the pinned-selected L3 allowance
has ratio 30960/79880=774/1997≈0.387581. Neither figure supplies the missing
helper-capacity/loading lemma. The sampled Walsh identities and that lemma
are outside this task.

PR606's 48,780 allowance is not interchangeable: [S1] uses its full-width
center scenario, center bill 13,872, source path `[16]`, target path
`[1,7,8]`, L5, and a historical +20% target. No threshold for that different
scenario was recomputed or silently substituted here. We do not establish
a ≥5% improvement over the current priority target, a fully paid local
profile, native/global supplier admission, or any new exponent.

## 8. Original source gap and later clarification

The original response [S4] does not define the 1.538× ceiling calculation;
it also says the pricing, structure, and Walsh scripts were unpublished.
At that source cutoff it would be wrong to describe reconstruction from
PR606 as replay of the author's unpublished implementation, or to invent
an interpretation of the ceiling.

A later reply, observed during this audit, supplies the exact supplement
commit `b496aed769dd724cd1ff6b921cade626562be27b` [S8]. Its price script
explicitly distinguishes its original float comparison from a Fraction
comparison and defines the ceiling as the ratio of the two printed
zero-helper values in PR606 COSTS.txt: E8² full Pauli 0.006945535353 divided
by E8 root reference 0.004515128332. This is the author's later definition,
not an invented throughput ratio, and not a newly certified physical gain.
The original-response gap is therefore documented, while the later source
availability is not misreported as still missing.

That script's main program includes a longer PR1424 target and two
comparison modes. It was read, not run or imported. The present results
come from the authenticated PR606 invoice and the independent narrow
reconstruction for exactly the twelve task cases. The supplement's
structure/Walsh programs and saved output were not verified. Its adjacent
boundary test is not by itself a proof of global monotonicity; Section 4
supplies the needed mathematical argument for this bounded audit.

## 9. What was and was not verified

`audit.py` binds the complete four-file import closure, compares every base
and helper term with the reconstruction, calls the source `threshold()` at
all twelve targets and `invoice()` at R and R+1, and checks exact receipt
equality. `verify_certificate.py` checks the mathematical certificate using
rational arithmetic without importing the original source or using float
nomination. Both have explicit exception-based guards that remain active
under Python `-O`.

The controls cover source-byte corruption, omitted pads, mismatched stock
and children, over-cap children with the mass unchanged, silent target
substitution, false counts/endpoints/grid cells, missing cases, forbidden
additional stages, interval domain errors, and strict-boundary semantics.
The actual executions and deterministic-output checks are recorded in
`RUN_LOG.txt`. Python 3.13.5 was used; Python 3.12 execution was not performed.
No independent human review, formal proof, geometry census, construction
search, external publication, installation, or frontier update is claimed.

## Appendix: exact endpoint witnesses

The following integers have scale 10^18. For every line,
`lower(R)/10^18 > exact target > upper(R+1)/10^18`.
The complete lower/upper pairs and exact pressure margins are also provided
in the JSON certificate.

| Target | L | R | lower(R) | upper(R) | lower(R+1) | upper(R+1) |
|---|---:|---:|---:|---:|---:|---:|
| author_PR890 | 3 | 80558 | 1661964956043699 | 1661964956048683 | 1661949271827939 | 1661949271832924 |
| author_PR890 | 5 | 89683 | 1661961473768445 | 1661961473773429 | 1661949885203049 | 1661949885208033 |
| author_PR890 | 7 | 80753 | 1661965395044844 | 1661965395049828 | 1661954492995919 | 1661954493000904 |
| retained_PR890 | 3 | 80558 | 1661964956043699 | 1661964956048683 | 1661949271827939 | 1661949271832924 |
| retained_PR890 | 5 | 89683 | 1661961473768445 | 1661961473773429 | 1661949885203049 | 1661949885208033 |
| retained_PR890 | 7 | 80753 | 1661965395044844 | 1661965395049828 | 1661954492995919 | 1661954493000904 |
| selected_pinned | 3 | 79880 | 1672667447516726 | 1672667447521710 | 1672651560609143 | 1672651560614127 |
| selected_pinned | 5 | 88765 | 1672668412934956 | 1672668412939941 | 1672656674515531 | 1672656674520515 |
| selected_pinned | 7 | 79778 | 1672663423502237 | 1672663423507221 | 1672652380569229 | 1672652380574214 |
| author_PR1424 | 3 | 79617 | 1676856209287933 | 1676856209292917 | 1676840242697020 | 1676840242702004 |
| author_PR1424 | 5 | 88409 | 1676857789885697 | 1676857789890681 | 1676845992570138 | 1676845992575122 |
| author_PR1424 | 7 | 79399 | 1676859227320794 | 1676859227325778 | 1676848128885528 | 1676848128890513 |
