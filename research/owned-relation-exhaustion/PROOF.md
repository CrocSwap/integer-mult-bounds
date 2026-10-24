# Signed invoice order and the fixed centre-exchange ceiling

## 1. The reusable order certificate

Let d_r=(P'_r-P_r)-(T'_r-T_r), with finite positive integer rank support and signed
integer coefficients. Put K(k)=Σ_r d_r min(r,k). For an increasing concave tariff
f with f(0)=0 and largest rank R, write s_j=f(j)-f(j-1). Direct telescoping gives

    Σ_r d_r f(r) = s_R K(R) + Σ_{k=1}^{R-1} (s_k-s_{k+1}) K(k).

All coefficients are nonnegative. Thus nonnegative K means no improvement in
paid-minus-target cost; nonpositive K means no worsening. Conversely, each
min(r,k) is an allowed tariff, so these signs characterize the whole tariff
class. K is linear between support breakpoints, including the segment from zero
to the first breakpoint. Checking just the reported knots is sufficient.

For f(r)=r^t, 0<t<1, s_R>0 and every curvature coefficient is positive. A nonzero
one-sided K therefore gives a strict sign. If every K vanishes, d vanishes.
Unequal rank mass is allowed; K(R) explicitly carries its linear contribution.
This is classical concave order, not a new theorem. mightyOil's retained T16
audit supplies the closely related equal-mass predecessor implementation.

Two useful controls have equal rank mass but opposite strict signs:

* H4→2H2 gives d_2=2,d_4=-1, K(2)=2,K(4)=0: uniformly worse.
* Remove paid H1+H8 and target H9: d_1=d_8=-1,d_9=1, K(1)=K(8)=-1,K(9)=0:
  uniformly better. For powers, the margin gain is g(C)=1+8^(1-C)-9^(1-C)>0.

## 2. Exact current-source inventory and exchange family

The retained final #4610 word has 3,298 paid events per orientation, including
exactly eight H8 centre events and no other H8 paid events. The retained p16/a7
controller has sixteen backward and two forward local invocations: 144 original
centre slots. `source_invoice()` separately rebuilds the complete paid histogram
and targets from this word and controller, including copied queries, whole idles,
all helper endpoints and main diagonal outputs. It agrees exactly with the
final source invoice. Its rank surplus is 752.

Define the following restricted optimistic family, for integers 0≤k≤144:

    P(k) = P(0) - k H1 - k H8
    T(k) = T(0) - k H9.

There is at most one exchange per original centre slot and **all other recursive
charges and target credits remain fixed**. Giving every exchange free preparation,
storage, copying and completion only favors it. A scalar basis choice or schedule
cannot create a 145th original centre slot within this definition. No assumption
is made that all 144 exchanges have a physical realization.

The margin is M_k(C)=Σ_r(T_r(k)-P_r(k))r^(1-C). By strict concavity,
M_k(C)=M_0(C)+k g(C), with g(C)>0 for 0<C<1. Therefore M_144 dominates this entire
family. The raw-root brackets proved by directed rational intervals are:

| Exchanges | Complete raw crossing |
|---|---|
| 0 | (.00302177587077, .00302177587078) |
| 16, #5377 bill | (.00302238736347, .00302238736348) |
| 128, #5383/#5387 bill | (.00302667476807, .00302667476808) |
| 144, optimistic whole-family maximum | (.00302728824993, .00302728824994) |

Consequently the remaining **raw** gain above the 128-exchange crossing is less
than .00000061348187. Even the all-144 margin at C=.0034 is below -91.8985594569.
The #5387 claimed endpoint .003026674765 is within .00000000000308 of the
128-exchange raw upper bracket. These are ceilings on this recursive invoice,
not supplier admissions or a claim that every compiler achieves its raw root.

`budget.py` proves strict decrease on [0,.01] by bounding the derivative
Σ_r(P_r-T_r)log(r)r^(1-C) throughout that interval, not just at sample points.
Each root has strictly positive and negative directed margins at its bracket
endpoints. A 1,024-cell directed interval cover proves M_144<0 on [.01,1]. For
each cell [a,b], it bounds targets at a and paid terms at b, using monotonicity
of every power term. The largest upper bound is below -1,134. Thus there is no
later positive window; the brackets give global raw ceilings for 0<C<1 in the
stated family. Other k are dominated by 144.

Every endpoint is rational. Logarithms use range reduction to [1,2] and the
positive atanh series with an explicit geometric tail; exponentials use Taylor
series, a geometric tail and repeated squaring. Integer endpoints round
outwards at scale 10^50. Exact integral and square-root cases calibrate the
implementation. This is an independently written arithmetic engine, not reuse
of the predecessor's pricing code. The classical interval formulas are shared.

## 3. Independent fixed-eight formal-row census

The eight entry relations and their first physical realization are Ali Romman's
#5383. Exact rational row reduction gives pivots
225,227,229,230,241,245,257,288. Substitution leaves the 224 main inputs and all
nonpivot helper inputs independent. The census walks every source event in
both orientations, checks its frame progression and paid rank, and follows
the retained scalar-row convention: paid inclusion changes the frame, while
native warp symbols act on the row and cancel only adjacent inverse pairs.

At every boundary it records a nonzero row's exact physical frame identifier
and rational projective normal form. Every historical row is retained without
charging slots or enforcing liveness. This favors possible snapshot reuse.
Before each paid job it checks whether the row is zero or proportional to any
earlier row already in that job's output frame. Since the source event list is
finite and every boundary is visited, the census is exhaustive in this grammar.

| Orientation / entry contract | Paid jobs | Zero rows | Proportional single-snapshot matches |
|---|---:|---:|---:|
| Forward / original inputs | 3,298 | 0 | 0 |
| Backward / exact eight relations | 3,298 | 8 | 8 |

All eight nonzero matches are precisely the previously supplied centre
witnesses, each unique with factor +1. All zero jobs are the supplied later
climbs. Relations of the same span give the same quotient regardless of basis.
Wrong relation sign, a dropped actual ADD and a wrong snapshot sign fail.

This is a **formal-row** absence result, not a proof of physical operator
inequality. Concrete native operators obey further identities; this traversal
uses only the retained free reduction. It also excludes arbitrary linear
combinations of saved rows, changed scalar programs, extra entry relations,
new preparations, alternate frame equivalences and different caller boundaries.
It does not itself verify the physical construction's phase or erasure ABI.

## 4. Scope and reopening conditions

The budget and census have different scopes. The exchange ceiling allows any
basis or schedule that keeps exactly the declared complete invoice family; the
census fixes the eight relations and unchanged source event history, regardless
of whether a proposed edit has that invoice. Neither implies that all productive
helper ideas are exhausted. Removing different ranks, surrendering different
targets, using scalar combinations or native relations, changing contact heights,
or changing the controller requires a fresh complete signed bill and proof.
The selected construction and its five framework assumptions are unchanged.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
