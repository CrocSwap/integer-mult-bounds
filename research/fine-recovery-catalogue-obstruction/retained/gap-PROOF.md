# The actual cap constructor already funds the production narrow gap

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
**A source-specific all-parameter admission lemma; no new kappa.**

## 1. Precise result and prior boundary

Fix an integer p>=2. The source data satisfy

`theta=e/S in [1/(4p^2),1/p^2]`, `rho=1+theta`,
`alpha` a positive integer, `a=pi alpha^2>=4 log(16p)`.

Here and below log means natural logarithm. Use the literal canonical
`rational-unitary-fft/gaussian_reference.py` class method

`Reference.for_cap(raw,S,e,alpha,B,R,t)`,                    (1)

with dyadic B>=1, 2B<=S, rational R>=1 and integer t>=1. Retain its exact
canonical numerical source cohort. Require the constructor's legal-period
checks `2w<S`, `2W<S+e`; the generated cuts w,W are specified below. Under
the predecessor's certified interval/constructor contracts, (1) returns a
Reference whose **literal rational** field satisfies

`reference.narrow_gap > (1/8-2^-46)/p^2 > 1/(16p^2)`.       (2)

Thus `narrow_inverse_bounds` is present. No extra precision, larger target,
different rounding, altered Reference or post hoc repair is needed. The
result is uniform in the source length, excess, cap, allowed radius and
target. Its gap implication needs no new eventual onset once the named
source inequalities and legal cuts hold.

The outer source uses `alpha=ceil(sqrt((4/pi)log(16p)))`, which satisfies
the lower inequality. Its separate source-prime supply and legal-period
conditions are not established here. Section 5 gives an explicit sufficient
onset for the usual upper-alpha and O(p) precision estimates, and retains
the actual cost of source descriptors and later weight preparation.

This closes the conditional positivity/production-size admission of the
actual cap constructor. It is not a theorem that every manually specified
Reference has this gap. It does not prove the ideal/full-transform identity,
physical delivery, native suppliers, final recovery or an unconditional
multiplication theorem.

### What is already proved

CrocSwap/integer-mult-bounds#4648 (`narrow-row-half-gap`) supplies

`gamma=1-exp(-2a theta)-5exp(-2a)>=1/(8p^2)`                 (3)

under the stated lower-alpha/theta domain, as well as a generic perturbation
budget. It explicitly leaves the actual stored-band precision/rounding
binding open. We credit (3); we do not re-prove or reclaim it.

The canonical `RAW-GAUSSIAN-PROOF.md` §5 defines the actual computed
certificate d and proves that a positive d bounds the true rational narrow
reference row gap. It leaves positivity conditional. Its uniform-cap
construction proves the error bound used below. `GAUSSIAN-PROOF.md` §3 proves
the scalar outward interval width and the conditioning enclosure. These
are exact pinned source premises, not inferred from this finite replay.

`forward-fine-theta-conditioning` studies the different broad inverse
conditioning bound and explicitly excludes the narrow kernel. The nearby
column, Schur and old factorwise-rounding results have different hypotheses.
The new implication is that the **existing normalized conditioning quantity
inside (1)** already forces enough reference accuracy to make its literal
narrow certificate pass. Neither a stronger general Gaussian estimate nor a
new exponential algorithm is claimed.

## 2. The actual allocation is already more than large enough

These are literal expressions in `Reference.for_cap`:

`F*=1+alpha^2 theta(B^2+B+1)`,
`G*=alpha 2^ceil(8F*)`,
`H*=2 qbar(B,1/(alpha^2 rho))`, `Q*=G*^2 H*`,
`E=t+ceil(log2(8(R+1)Q*^2))`.                              (4)

The normalized Gaussian constructor computes qbar from a positive certified
lower interval endpoint l_c for

`exp(-pi/(4c))`, `c=1/(alpha^2 rho)`,

by the exact formula `qbar=B/l_c`. Since `l_c<=exp(-a rho/4)` and rho>=1,

`qbar >= B exp(a rho/4) >= B exp(log(16p)) =16pB`.         (5)

This uses the actual allocated rational quantity, not the norm of an
unknown narrow inverse. F*>=1 and alpha>=1 imply `G*>=2^8 alpha`, hence

`Q* >= (2^8 alpha)^2 * 2 * 16pB
     = 2^21 alpha^2 pB`.                                  (6)

With R>=1, B>=1 and t>=1, the unchanged integer allocation in (4) obeys

`E >= t+46+ceil(log2(p^2))
   >= 47+ceil(log2(p^2))`.                                (7)

In particular `2^-E<=2^-47/p^2`. No growth assumption on t or R was needed.
The global narrow inverse was never assumed to exist in deriving (5)-(7),
so the argument is not a circular use of its own conditioning certificate.
The relevant lower bound follows directly from the positive scalar enclosure
already constructed for the normalized cap allowance.

## 3. Literal cutoffs, tails and outward certificate precision

Set A=alpha^2 rho^2. The same function chooses

`w=ceil(sqrt((E+5)/(3alpha^2)))`,
`W=max(ceil(A),ceil(sqrt(A(E+5)/3)),2w+2)`,
`b_E=E+3+ceil(log2(2max(w,W)+1))`.                         (8)

It computes square-root ceilings by integer arithmetic and rejects illegal
period cuts. The unchanged uniform-cap source theorem supplies

`E_N=reference.errors['narrow']<=2^-E`, `b_E>=E+3`.          (9)

Specifically, E_N is the actual rational geometric tail plus
`(2w+1)2^-b_E`. This is not an unnamed per-entry precision constant or a
floating estimate. The original function checks the rational bound before
returning. Its proof bounds both tails and coefficient row/column allowances
for the actual cutoffs (8). We consume that constructor theorem unchanged.

The literal `Reference` constructor uses working precision

`J=2(b_E+ceil(8alpha^2 rho^2)+16)+32 >= 2b_E+64`            (10)

for its adjacent and distant exponential enclosures. The predecessor proves
that an exponential enclosure at J>=16 has width at most

`omega(J)=512 J^2 2^-J`.                                  (11)

For every integer b>=8 and J>=2b+64,

`omega(J)<=2^-b`.                                         (12)

Here is a direct all-integer check of (12). J^2 2^-J decreases for J>=3,
so it suffices to put J=2b+64. After cancellation the assertion is
`512(2b+64)^2<=2^(b+64)`. At b=8 it is
`512*80^2<=2^72`. Increasing b multiplies its left side by
`((2b+66)/(2b+64))^2<2`, while the right side doubles. This proves (12)
for all b>=8, not just the verifier's finite range.

Because a true exponential lies inside its outward enclosure, the excess
of its upper endpoint over the true value is at most the enclosure width.
Write those two nonnegative excesses as eta_adj and eta_dist. From (9)-(12),

`eta_adj+5eta_dist+E_N
 <=6*2^-b_E+2^-E
 <=(7/4)2^-E
 <2*2^-E <=2^-46/p^2`.                                   (13)

There is no exact-floor/separation requirement in this argument. It concerns
the actual rational endpoints returned by the existing interval method.

## 4. The literal certificate clears the production threshold

The actual constructor sets

`d=1-adjacent_hi-5*distant_hi-E_N`.

Subtract the explicitly funded excess (13) from the credited ideal
majorant gap (3). This gives exactly (2). The branch that computes
`narrow_inverse_bounds` is therefore taken on every source admitted by
Section 1; its positivity is no longer a separate hypothesis for this
particular constructor.

By the existing same-reference theorem, d bounds the row gap of the actual
rational narrow H, including original period crossings and identity holes.
Its principal restrictions inherit that gap. Thus the source's existing
inverse-infinity bound is at most16p^2, and the least dyadic normalizer
obeys `u<=ceil(log2(16p^2))`. The usual dimension-independent column/inverse
estimates continue to use their actual physical bandwidth. We do not
replace a row estimate by a column estimate or improve an assembled kappa.

This consequence applies when the common Reference supplied to every Core
and halo window is generated once by (1). A caller cannot create independently
rerounded References and invoke this lemma to identify their overlaps. A
manually constructed reference with the same theta/alpha but small entry
precision can fail; the replay contains an actual negative certificate of
that kind. Small alpha or theta outside the domain can also make (1)'s
certificate negative even though the cap constructor itself returns normally.

## 5. Explicit production onset, widths and complete setup cost

Now use the source's actual alpha ceiling, cap
`B=2^floor((15/16)log2 p)`, fine theta, and admitted radius/target with
`t+log2 R=O(p)`. Rational descriptors are supplied with polynomial bit height;
in the physical caller the radius can be a dyadic bound with O(p)-bit
description. A numerical value close to1 does not excuse an arbitrarily
long rational descriptor.

A convenient sufficient onset for the following estimates is `p>=2^200`.
Let L=log(16p). Then L>100, and alpha<=sqrt(4L/pi)+1 gives

`4L<=a<=4L+4sqrt(pi L)+pi<4L+8sqrt(L)+4<=5L`.

The last inequality holds at L=100 and increases thereafter. Using pi>3
and p>=16 gives `alpha^2<2L<=4log2 p`. Also

`F*-1<=12 log2(p) p^-1/8 <=192 p^-1/16 <=1`.              (14)

The elementary maximum of `log2(p)/p^(1/16)` is
`16/(exp(1) log(2))<16`, using exp(1)>2 and log(2)>1/2. Finally
`(2^200)^(1/16)>192`, so the last step in (14) holds at the stated onset.
Thus `G*<=2^16 alpha` there.

For completeness the same actual conditioning enclosure also has a simple
upper qbar bound. Its precision rule certifies width at most
`2^(-a_c-2)`, where `a_c=ceil(2/c)`, while the true positive exponential is
at least `2^-a_c`. Hence `l_c>=3/4 exp(-pi/(4c))` and
`qbar<= (4/3)B exp(a rho/4)`. Since rho<=5/4 and a<=5L,

`qbar <= (4/3)B(16p)^2`.

For p>=16, `4log2 p<=p`, so the preceding alpha bound gives `alpha^2<=p`.
Together with B<=p^(15/16) and (14), this yields the deliberately loose bound
`Q*<=2^43 p^4`. In (4)
this gives the explicit sufficient upper allocation

`E<=t+ceil(log2 R)+90+8ceil(log2 p)`.                      (15)

In particular E=O(p) without increasing the existing target. Equations (8)
then give the source's established

`w=O(sqrt(p/log p))`, `W=O(sqrt(p log p)+log p)`,
`b_E=O(p)`, `J=O(p)`.

The cap constructor does not enumerate the original S or S+e coordinates.
Its normalized Gaussian constructor may scan up to B candidate cutoffs;
each interval/rational operation has polynomial cost in the actual descriptor
and precision heights. A safe unamortized constructor tariff is
`B poly(p)` in this production family, with the declared source-description
read, parsing, interval arithmetic, allocation, comparison and disposal
included. More generally retain the actual B and descriptor/working heights;
O(log R) alone is not a representation-size bound. The theorem does not
reprice a later full matrix/Schur/compiler preparation by this constructor
tariff.

The same constructor records full-cell weight precision

`P_weight=ceil(2alpha^2/theta)+b_E+7=O(p^2 log p+p)`.

Those larger weights remain offline setup, with actual later generation,
tables, caches and retained backing charged by the original source/physical
caller. The kernel precision adds `ceil(8alpha^2 w)+4=O(sqrt(p log p))` bits,
preserving O(p). This lemma neither lowers those widths nor declares the
original source field, context delivery or coefficient pages free.

The strict period checks remain explicit. Their eventual satisfaction uses
the caller's original-axis size and the usual source-prime construction; we
do not infer it from the small fixtures or from (2). A complete caller may
retain its ordinary small-parameter fallback. The gap inequality itself
already holds for every p>=2 whose stated constructor/geometry domain holds.

## 6. Executed checks and limitations

The checker authenticates 14 canonical scientific inputs plus the frozen
task-card provenance. It executes the complete, unchanged canonical
`Reference.for_cap`, including the actual normalized Gaussian constructor,
interval cutoffs and literal rational gap. The checker executes the complete
unchanged constructor rather than an extracted allocation formula; its
existing AST parsing/compilation remains charged.

The 37 cases cover p in {2,3,7,19,73,74,257,1024,65536}, near both fine-theta
endpoints, cap 1 and the actual dyadic p^(15/16) cap, with extra rational/large
radius and target cases. The largest target period is 2^37 and largest cap
2^15. These are metadata/constructor cases: no 2^37-entry field or huge
full-cell weight is generated. Empty original entry/weight/kernel caches and
the absent hole listing are checked explicitly. The actual alpha ceiling is
certified with independent rational log/pi bounds.

A separately implemented direct positive Taylor/remainder oracle, inverted
after its exact rational calculation, corroborates the literal certificate's
two exponential terms. It imports no retained interval backend. The complete
source allocations and all resulting certificate hashes are recorded. The
505 finite integer checks support the interval-budget induction; the proof
of that induction is separate. Six controls distinguish low entry precision,
bad alpha, bad theta, invalid cap, illegal cuts and inadequate input radius.

The universal argument still cites the prior ideal-majorant and outward
interval/constructor theorems. This is source-specific assumption reduction,
not independent human or proof-kernel acceptance of every cited source.
All five selected framework assumptions, global source integration and final
multiplication recovery are not collectively discharged by this result.
