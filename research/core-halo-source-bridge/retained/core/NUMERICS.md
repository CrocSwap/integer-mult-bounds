# Numerical and complete-cost interface for the current finite Core

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is the numerical part of the proposed physical join of the current-source
dense interior cohort #6899, the first inverse window #6908 and its complete
union router, and the supplied band action #6909. The Schur identity, generic
residual telescopes and individual provider estimates are inherited. The
contribution is their concrete common-source, actual-radius, precision,
signed-word and complete-cost compatibility. Source binding, literal execution
and controller review are separately required and reported by the integrated
physical package; the numerical interface by itself is not a physical closure.

The primary implementation target is the narrow inverse. Section 8 scopes the
broad compatibility separately. All five selected assumptions and selected
frontier remain unchanged. No new kappa is claimed. Numerical source bodies
are inherited from the canonical commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`; #6899 is pinned at
`61d86cbe25657af55b9463bd3f072b6cbf952638`, #6908 at
`9c6078ff36ae2110e6cc30ff69a9addbf5a47bf2`, #6909 at
`ad6a7bf2213130719e9bf2022d01a30c79638f17`, and the complete union router at
`CubeJerry/integer-mult-bounds@73f3ea9f5773d46113b7d7b1ec21724572de59e1`.
The integrated manifest supplies exact source bytes and their original notices.

## 1. One immutable source and the actual five factors

For each actual coarse context and selected axis take one canonical rational
Reference, an ordinary original-coordinate window, and one admitted interior
partition. The production-source case uses #6899's Partition, invoking the
unchanged Core.load_carve and Core.partition. An explicitly admitted small
partition is distinct from that production carve. It must preserve the source's
original phase, holes, cuts, absolute origin and each interior source_start.

In interior/boundary order the exact original matrix is

\[
 Q=\begin{pmatrix}A&B_0\\C_0&D\end{pmatrix},\qquad
 F=D-C_0A^{-1}B_0.                                         \tag{1}
\]

A is the direct sum of all actual interior blocks, possibly empty. E consists
of J and every I coordinate incident to a nonzero original B0 or C0 entry.
E and J retain increasing original-coordinate order. Source setup checks the
complete partition, exact zero interactions between different interiors, original
band, source gap/norm and the actual compressed bands used by the providers.
The exact Schur coefficients are formed from this Reference, not from an online
approximate interior inverse. The sparse contract requires nonempty J; an empty
sparse substream makes no numerical call.

The five narrow operations in **execution order** are:

| Stage | Exact complete-axis operation | Provider |
| --- | --- | --- |
| 1 | `Dminus=diag(A^-1,I_J)` | #6899 stored interior inverse |
| 2 | `Tlower(u)_J=F^-1(u_J-C0 u_I)`, identity elsewhere | #6908 complete first inverse window and physical union router |
| 3 | `Dplus=diag(A,I_J)` | #6899 interior forward |
| 4 | `Tupper(u)_I=u_I-B0 u_J`, identity on J | #6909 supplied E-matrix `I-N_B` and complete union transport |
| 5 | `Dminus` | #6899 stored interior inverse |

Here N_B has B0 only in I rows and J columns. In matrix multiplication order,
`Dminus Tupper Dplus Tlower Dminus=Q^-1`. Stage 2 must include the original
lower coupling shear at its actual input. F^-1 on the original boundary alone
does not implement it.

This rounded schedule is not claimed to equal Core.execute bit for bit.
The actual global H/D implementation of a dense direct sum can round boundary
coordinates. Sparse stages must receive those actual values. Each error is
compared with the exact local map at the current input, then propagated through
exact later factors. No boundary reset, exact-state radius, commuting rounded
maps or Lipschitz bound for a rounded map is used.

Let the complete field contain T=2^n complex records, with g selected axes and
common side L=2^m. It has K=T/L^g complete contexts. Each exact stage is the
direct sum over K contexts of the tensor product of its g axis factors. Dense
stages operate on the **whole T-record field**. Sparse stages traverse complete
contexts, updating their union records in increasing active-axis order before
restoring the complete field. Different-axis exact maps commute within a fixed
context; this identifies the exact tensor endpoint without commuting rounded
operations. Axis order and the dense/router reversal must be bound explicitly.

## 2. Rational norm certificate and actual input radius

Let h be a common dyadic integer at least one and at least every row sum and
column sum of `|Re entry|+|Im entry|` of all five exact local factor matrices,
over all actual contexts/axes. These are literal rational sums. They dominate
the usual complex row and column norms; current Reference entries are real.
Setup computes them exactly and rounds the maximum upward to a power of two.
Include the elementary broad factors of section 8 when enabled. Therefore

\[
 \|M_{local}\|_2\le h,
 \qquad \|M_{whole\ stage}\|_2\le H:=h^g.                  \tag{2}
\]

This follows from the row/column bound on the Euclidean operator norm and the
tensor/direct-sum norm identities. It is a bound for each complete factor,
including the combined first sparse window, not a bound inferred from A alone.

The actual incoming field x is on grid 2^-P0 and has `||x||_2<=R0=2^r0`.
If it differs from an ideal x0 by e0, the final comparison with the exact Core
at x0 retains the additional term H^5 e0. The present contract first bounds
the local error relative to the exact Core at the actual x.

For tau=2^-t choose

\[
 t_d=t+\lceil\log_2(10H^4)\rceil,\qquad \delta=2^{-t_d},    \tag{3}
\]

and dyadic radii

\[
 R_2\ge(H+1)^5(R_0+1),\qquad
 R_*\ge2(h+1)^{g+1}(R_2+1).                               \tag{4}
\]

Every dense call uses whole-field Euclidean radius R2; each sparse axis call
uses maximum complex-l1 radius R*. If a complete stage has defect at most
delta, its actual radius satisfies `r_next<=H r_current+delta`. Since
delta<=1, (4) covers all five inputs and outputs. During a sparse stage the
same recurrence with local h covers the partial axis applications. The extra
power in R* also covers the broad F micro-step. Finally
`max_i(|Re x_i|+|Im x_i|)<=sqrt(2)||x||_2<=2||x||_2`.
Internal inverse-pass states use their separate completed-residual bounds.
They are not bounded merely by the incoming R*.

Dyadic radii are useful for setup accounting: their full numerator/denominator
description heights are their displayed exponents. Charging only log of the
value of an arbitrary rational radius would not charge its full description.

## 3. Sparse error aggregated over the complete field

Put `V2=2^ceil(n/2)` and choose

\[
 q=t_d+\lceil\log_2(V_2 g h^{g-1})\rceil.                  \tag{5}
\]

Require each sparse local axis call to have complex-l1 defect at most 2^-q
on every coordinate, evaluated at its actual input. Its complete-field residual
then has Euclidean norm at most V2 2^-q. Propagating realized residuals through
exact later axis factors gives

\[
 \|\widehat S(u)-Su\|_2
 \le V_2\sum_{a=1}^g h^{g-a}2^{-q}
 \le V_2g h^{g-1}2^{-q}\le\delta.                          \tag{6}
\]

T and V2 include **all K contexts**. There is no error-budget reset at a new
context key. The union chronology supplies a complete E-line at its current
values. Outside E the map is identity; omitted rows cannot be sources of a
nonzero original coupling because E includes every such source coordinate.
Later sparse windows gather fresh values after the intervening dense stage.

A second exact-suffix expansion for the five stages yields

\[
 \|\widehat C(x)-Cx\|_2
 \le\sum_{j=1}^5 H^{5-j}\delta\le5H^4\delta\le\tau/2.       \tag{7}
\]

For an incoming approximation the bound is H^5 e0+tau/2. Across several axis
groups retain the corresponding actual group norms and error recurrence, or
fund each local target by its downstream exact norm product. The conversions
below are exact, so their defect is zero; an unimplemented conversion does not
receive a free allowance from the factor-two margin.

## 4. Actual sparse admissions and scalar widths

### 4.1 First narrow inverse window

#6908 prepares the C0 shear and the exact Schur F from (1). It executes two
physical bidiagonal passes for the shear and two for F. Its staged rounding is
retained. For eta=2^(1-P), a pass uses exact diagonal-block norm a, preceding-block
norm c, full inverse norm M and

\[
 c_0=ab+2a+1,\quad c_1=b[a(c+1)+1],\quad
 K_{pass}=M(c_0+4Mc_1).                                   \tag{8}
\]

The producer checks `b eta<=1`, `c0 eta<=1`, `M c1 eta<=1/2`. The actual
completed states are bounded by 4MY and the local defect by Kpass eta Y.
For two passes the error is `eta(M2 K1+4M1 K2)Y`.
Let es be this shear error at R*. Its actual F input radius is
`Rs=(1+||C0||_infinity)R*+es`. If ef is the F-solve error at Rs, the complete
local defect is `||F^-1||_infinity es+ef`, checked against 2^-q. The earlier
dense error in both I and J is already part of the input; it is neither erased
nor charged twice inside es.

One all-size sufficient allocation uses
`pbar=max(W+1,ceil(sqrt(1/(16 gap))),1)` and a dyadic block covering the actual
compressed shear/Schur bands, with `2<=b<=4 pbar`:

\[
 P\ge\max(P_0,q+45+16\lceil\log_2\bar p\rceil+
                       \lceil\log_2R_*\rceil),\qquad
 w_I\ge P+52+16\lceil\log_2\bar p\rceil+
                       \lceil\log_2R_*\rceil.              \tag{9}
\]

Increase the width to cover the largest encoded descriptor. The exact finite
producer also checks all input/state/coefficient and residual ranges, including
`Y+(c+b eta)4MY+eta`, against `2^(w_I-P-1)`. A sharper finite allocation is
valid only when these actual source inequalities pass, not because one payload
has a small final output.

### 4.2 Upper negative shear

Supply #6909 with G=I-N_B on E. Check its exact compressed half-band v and
the literal lifted support before coefficient rounding. The lift half-band is
`v_lift=max_{G_ij!=0}|2i-(2j+1)|<=2v+1`; the source preparer checks this actual
support. Choose a dyadic b>=max(2,v_lift). The simpler b>=max(2,2v+1) also
suffices. The proof needs the actual nilpotent lift to be block bidiagonal,
which follows from v_lift<=b; no artificial enlargement is necessary. If s is the
maximum number of nonzero G entries per row and Gamma>=||G||_infinity, its
actual staged return satisfies

\[
 \|\widehat G(u)-Gu\|_*\le(sR_*+6)2^{-P}.                 \tag{10}
\]

Sufficient precision and width are

\[
 P\ge\max(P_0,q+\lceil\log_2(sR_*+6)\rceil+1),\qquad
 w_A\ge P+2+\lceil\log_2(\max(1,\Gamma)(R_*+1))\rceil.     \tag{11}
\]

There are at most three effective truncations per real component in the
nilpotent lift. No one-shot rounding equivalence is assumed. Its stored-state
bound does not replace the larger seven-product operand width w+log2(b)+2,
internal width 2w+4log2(b)+4 or exact returned width 2w+log2(b)+2.

## 5. Dense source accuracy, common grid and paid conversions

Prepare each of the three actual dense programs for target td, radius R2 and
its stated stored direction. If Lambda bounds its exact local interior endpoints,
the actual #6899 source target is at least

\[
 t_s=t_d+\lceil\log_2(8gR_2(\Lambda+1)^{g-1})\rceil.        \tag{12}
\]

The immutable Reference must already meet all resulting RawGaussian/Full
admissions. Increasing arithmetic precision cannot repair insufficient source
accuracy. Replacing the Reference between dense and sparse stages changes (1).
All strengthened source interval precision, original weights, exact inverses,
Full words, genuine idle words, pages and validation are charged as setup.

The unchanged global allocation suffix checks its source telescope against
2^-td/8. Let A be its actual complete prefix product, E its endpoint product,
Dc its diagonal count and bcoef one plus the actual factor-entry bound. Its
arithmetic requirement is

\[
 [8E D_c A^2g b_{coef}^{g-1}R_2+4EA D_cV_2]2^{-P}
 \le2^{-t_d}/4.                                           \tag{13}
\]

Its actual minimum also checks the perturbed-prefix allowance. Choose P at
least P0, all three dense minima, and (9),(11). Invoke the real
`fractional_bits=P` interface, with incoming=P after the initial exact lift.
The source suffix validates its minimum and freezes all internal widths. The
complete dense defect is then strictly below 2^-td as needed in (7).

The dense input width is W0=P+r2+2 where R2=2^r2. Its output is
`Wd=P+ceil(log2(4A(R2+1)))+2`. Factor, cache and product widths remain the
source's own frozen allocations. Choose common sparse w at least W0, all
actually certified sparse widths and descriptor guards; do not mutate a dense
allocation seal. It is sufficient, but unnecessary, to also require w>=all Wd.

The implemented public input already has grid 2^-P: its encoded incoming
precision equals P, so P0=P at this boundary. A caller starting with a coarser
external P0 must first supply an exact numerator shift by P-P0 and signed-width
extension, with its complete O(Tw) scan charged. That initial lift is an explicit
entry requirement; the present controller's converters change signed width at
unchanged P. Before each dense call, check/discard only redundant sign-extension bits into W0; the
actual radius ensures this is exact and the dense consumer still performs its
real squared-radius test. After its return, sign-extend or check/narrow Wd to w.
The five-stage induction in (4), including its actual local defects, bounds
every **completed dense output** by R2. Hence each returned component numerator
has absolute value at most 2^(P+r2), and fits W0 with headroom. This completed
stage bound, not the larger raw-prefix allowance defining Wd, justifies the
shrink when w>=W0. The physical converter still checks every discarded high
bit is redundant sign extension. It discards no low fractional bit. Wd remains
the true provider width throughout its interior work and in the invoice.
Sparse data and pages remain at P,w. All conversions read/write their complete extents and cost
`O(T(w+W0+max Wd))`; old bodies are erased and historical backing retained in
space. Any marker/codec adapter between owners is also a complete paid scan,
not a host decode of a whole field. No conversion rounds downward.

## 6. Complete time, layout and ceiling invoice

Let C_dense(j) be the full #6899 tariff, including its two complete-field
permutations, actual radius squares, every H/diagonal event, Karatsuba products,
controls, native constructor, setup and cleanup. Let C_route denote the actual
support route with precision w+g and support k, and C_union(c,s) the complete
transport, catalogue and numerical tariff for context c and sparse stage s.
A safe complete invoice is

\[
 \sum_{j\in\{1,3,5\}}C_{dense}(j)
 +\sum_{s\in\{2,4\}}
   [2C_{route}(n,w+g,k,w)+\sum_{c=1}^K C_{union}(c,s)]
 +C_{convert}+C_{assembly}.                                \tag{14}
\]

The extra sparse routes put the original field into complete-context order
and restore it. An enclosing controller may prove a smaller bill by actually
keeping compatible packed order throughout. Identity permutation in one finite
fixture does not remove the all-size charge. Assembly includes complete copies,
encoded context traversal, bank selection and every ABI adapter.

**Three global dense cohorts are essential to this favorable rate.** The
retained physical dense theorem expressly needs n=Theta(P) for its accelerated
H tariff. Separate local-context dense calls have n_local=g log2 L=o(p), while
the requested accuracy may require P=Theta(p). They cannot inherit that rate
without another theorem. They retain the unsimplified provider cost instead.
A K=1 small fixture establishes execution at its actual dimensions only.

For m nonempty complete complex E-lines, a=|E|, j=|J|, the exact inverse
matrix-call count is

\[
 Q_I=[2(2\lceil a/b\rceil-1)+2(2\lceil j/b\rceil-1)]
                          \lceil2m/b\rceil.                \tag{15}
\]

One supplied forward action on k rows has

\[
 Q_A=2(2\lceil2k/b\rceil-1)\lceil2m/b\rceil.              \tag{16}
\]

Each matrix call uses exactly 7^log2(b) scalar children. The 2k in (16) is
the actual zero/source lift; 2m is the real/imaginary pairing. All transposes,
extraction/return, zero writes, page scans, source comparisons, padding,
additions, protected returns and erasures remain priced. Scalar arguments have
width w+log2(b)+2, never the width of a packed tensor.

The sparse source instantiates FftWord(base_bits=4096), with retained theorem
`M(u)=O(u log^2(u+2))`, including unamortized twiddle setup. It uses the
corrected #3709 normalized product. Pending #6895 at
`85e0534b3a86dc0237f368ff0e5fb646fe4744ec` already gives the arbitrary-input
numerical source implication. The source-compatibility receipt compares all
seven of its numerical files with the actual sparse FftWord nested ring archive
by Git blob and SHA256. Inherit that audited numerical implication only for
the byte-identical source closure; no new numerical audit is claimed here.
Count, WordProduct, codecs, live-operand, owner and complete-cost premises remain.
The exact comparison is recorded in
[NORMALIZED-SOURCE-COMPATIBILITY.json](NORMALIZED-SOURCE-COMPATIBILITY.json).
This scalar differs from dense #6899's Karatsuba.

With omega=log2(7) and Lambda7=1+log2(b)+ceil(log2(w+2)), retain

\[
 Q\,O\{b^\omega[M(w+\log_2b+2)
                 +(2w+4\log_2b+4)\Lambda_7^3]\}             \tag{17}
\]

plus the full movement terms of the union and action providers. If an action
uses global RHS count, retain its log(2k+2m+2) descriptor term. In the intended
regime it is O(n)=O(p) and is absorbed by w=Theta(p), not called O(log p).
A local b-column adapter uses the smaller descriptor only if actually executed.

### 6.1 Least checked blocks fund the row ceilings

Choose the least dyadic inverse block covering max(2,v_N,v_F), using the actual
checked bands. Matrices have dimensions at most a, so b<=4a; the ordinary band
also gives b<=4pbar as required in (9). For a forward action choose the least
dyadic block covering max(2,v_lift). Since v_lift<=2k-1 and k<=a, again b<=4a, including
the a=1,b=2 case. No arbitrary-partition boundary density is inferred here.

Expanding (15)--(17) bounds arithmetic by a constant times

\[
 [am b^{\omega-2}+(a+m)b^{\omega-1}+b^\omega]
 [M(w+\log b)+O((w+\log b)\Lambda_7^3)].                    \tag{18}
\]

The m b^(omega-1) term is at most 4am b^(omega-2). Remaining
`a b^(omega-1)+b^omega` terms are genuine per-substream remainders. At most
g squared nonempty round/axis substreams occur per context. Their full cost
is charged before context absorption. Oversized user blocks retain the full
ceiling bill without this simplification; empty substreams make no call.

## 7. Compatible conservative family; no new bound claim

Use the admitted #6899 family beta=39/40, xi=15/16, epsilon=1-10^-30,
g=Theta(p^beta), d=Theta(p^epsilon),
`L=2^ceil(400 log2 p)`, `Bint=2^floor(xi log2 p)`.
The complete field has n=Theta(p), original-axis address width
ell_original=O(p^(1-epsilon)), and balanced groups between g and 2g axes.
No independently padded small final group is used.

Retain the actual source accuracy/carve regime: physical
W=O(sqrt(p) polylog p), gap>=1/(16p^2), and enlarged boundary density
`a/L=O(W/Bint polylog p)`. Finite admitted small partitions do not prove
this density or the production source regime. The source conditioning gives
polynomial local factor row norms; column norms are at most L times them,
also polynomial. Thus log h=O(log p), log H=O(g log p)=o(p).
With target, incoming precision and log R0 all O(p), (3)--(5) give
td,q,log R2,log R*=O(p). Equations (9),(11)--(13) and the retained raw-prefix
analysis give P,w,U=O(p). The raw-prefix condition is exactly
beta+2xi-2=17/20<1. The larger offline original-weight precision remains setup
height, not an online scalar width. An initial grid Omega(p) gives w=Theta(p).

The complete uniform preparation/remainder envelope per delivered context is

\[
 2^{O(\ell_{original})}\operatorname{poly}(p).                \tag{19}
\]

It includes all g source keys, exact matrix/Schur formation, interval and
original-coordinate generation, radius-description heights, all three dense
source words, real page preparation, coefficient code, every catalogue traversal,
g-squared ceiling remainders and disposal or retained source/cache backing.
Constants must be uniform over contexts. Multiply by **K** for the complete
field. Since

\[
 \log_2(L^g)=\Theta(p^\beta\log p),\quad
 \log_2(2^{O(\ell_{original})}\operatorname{poly}(p))
       =O(p^{1-\epsilon}+\log p),\quad 1-\epsilon<\beta,
\]

the complete term is o(Tw). No cross-context cache or omitted K is needed.
Time absorption does not erase retained source objects or old physical backing
from the space invoice. Native constructor charges remain positive inherited
admissions, even when their fixed source constant is astronomical.

With V=Theta(Tp), use the incidence identity
`sum_(r,f) a_f m_(r,f)=sum_f a_f L^(g-1)` in each context. The two sparse
windows, the exact scalar FFT tariff, b=O(W) and density give over O(d/g) groups

\[
 O(Vd W^{\omega-1}/B_{int}\operatorname{polylog}p)
 +O(V[d/g+dW/B_{int}]\operatorname{polylog}p),               \tag{20}
\]

besides the absorbed complete setup and remainder. Lift constants and every
inner scalar product are already included. Since 7^16<2^45, the sparse
arithmetic power above V is strictly below

\[
 \epsilon+(45/16-1)/2-15/16=\epsilon-1/32.                 \tag{21}
\]

Use only the historical physical rates actually retained by #6899:
alpha=99827101/100000000 and eta=332353/332929. Dense and support-route powers
are respectively epsilon-(1-alpha)beta<.99831423475 and
epsilon-(1-eta)beta<.998313153856. Three dense calls, the four additionally
charged sparse layout routes and exact conversions preserve these powers up
to fixed logs/constants. Actual route reserve/free-block and stock guards
remain admissions; outside them retain its unsimplified tariff.
The exact comparison 3^5<2^8 bounds dense scalar power by
epsilon-beta+3/5<.625; scans/conversions have epsilon-beta<.025.
Thus the complete sparse arithmetic is subordinate to the inherited dense
maximum. Substituting Karatsuba into the sparse service instead destroys
this favorable comparison, as the checker demonstrates.

This is no identification of alpha or eta with a current .0034 BIT rate and
no new kappa. Halo, CRT, final recovery, production native construction and all
five selected assumptions remain outside the asserted closure.

## 8. Broad compatibility, separately scoped

For the same broad Q, exact execution order is
`Dplus ; E_+B ; Dminus ; (E_+C diag(I,F)) ; Dplus`.
F is applied, never inverted. The lower macro maps
`(u_I,u_J)` to `(u_I,C0 u_I+F u_J)`.
It can use two paid #6909 transactions: extract J/apply F in J order/restore J,
then apply the original +C0 shear in E order. This avoids an unproved band
claim for F embedded back into E. Each matrix uses its actual checked band;
the maximum of their least dyadic blocks still has b<=4a and source b=O(W).

Include both micro-factors and the macro in h. Allocate each micro-call at
`q_micro=q+ceil(log2(2(h+1)))`. Their combined complex-l1 defect is at most
`(h+1)2^-q_micro<=2^-(q+1)`, at actual intermediate radius covered by (4).
Equations (2)--(7) then apply. The extra target guard is O(log p), and the
additional action has its complete (16)--(18) bill. The broad source's own
`E_M Qideal<=1/2` and polynomial inverse-interior allowances remain explicit.
This compatibility statement is not an assertion that broad execution ran.

## 9. Evidence and open next questions

The check_budget.py verifier has been executed normally and with -O.
Its identical receipts contain 108 exact allocations,
4916 complete inverse/lifted-forward ceiling cases, six algebraic factor cases,
six rejecting admission/conversion controls and explicit omitted-volume,
per-context-reset, wrong-scalar, boundary-reset and Schur-only counterexamples.
Those matrix cases are explicitly algebraic controls. No assertion is used as a
required failure gate.

The separately executed check_source_join.py uses two actual immutable
References `(15,1,alpha,2,3,192)` for alpha=2,3, two complete contexts, two axes
and side L=4. All four actual interiors have length two and nonzero off-diagonal
entries. The adapter reverses the router's high-coordinate-first source order
for the unchanged dense source's low-coordinate-first convention. Each of the
three dense calls executes all 851 emitted H/diagonal events, including genuine
idle words, on the actual preceding result. The common grid is P=777 and the
recorded common width is 1091. Sparse values follow the retained staged
per-column functions in increasing router-axis order. The original complete Q
matrices, independently inverted and tensored, supply the final target.

Both normal and -O executions pass the five actual-input defects and their
complete propagated allowance. They reject unreversed source axes, swapped
source contexts and a one-ulp discontinuity at a sparse service boundary.
These are **semantic** replays; retained host value functions do not count as
physical tape execution. The fixture uses explicitly validated admitted
partitions and does not establish the production carve or its asymptotic rate.
Its observed dense all-boundary drift counts are zero; the all-size proof still
allows nonzero drift and requires every subsequent stage to receive actual
returned values.

The independent check_allocation.py additionally reconstructs the source
admissions in prepared_join.py before any payload is supplied. It uses its own
pivoted matrix inverse for the original-Q factors and the four padded
bidiagonal pass norms, and recomputes the staged errors, perturbed solve radius,
all scalar-state and residual bounds, literal forward lift support, complete
V2, dense coefficient/rounding constants and internal widths. Normal and -O
receipts agree on the actual small allocation P=242,w=264,W0=253,Wd=362,
an incoming grid of 320 that forces P=320, and a two-context/two-axis nonidentity
interior allocation P=752,w=779,W0=767,Wd=1078. These are admissions, with no
physical execution claimed. Four controls reject an insufficient h, a grid
below the incoming precision, an insufficient scalar carrier, and insufficient
immutable Reference accuracy despite 192 stored entry bits.

independent_numerics.py forms the final target by independently pivoting the
original complete Q on each actual context/axis. It does not import a producer
Schur builder, rounded page solver, physical controller or author oracle. A
joined fixture must expose all five actual inputs and outputs; exact converters
must preserve values across adjacent stages. This detects a boundary reset even
when the resulting difference fits a loose final error tolerance.

The completed small physical receipt uses Reference `(7,1,2,1,3,64)`, original
origin 2, L=2, I={1}, K=g=1, common P=242 and w=264. Its complete original Q is
nonidentity, while its scalar interior A is exactly 1. All three dense calls
execute 63 actual H/diagonal events each; the two sparse calls are real physical
children. The independent check_physical_result.py regenerates the Reference,
the original Q and both full dense source certificates, then checks all five
externally observed transitions at their actual inputs and the final result
against an independent direct inverse of Q. The normal and -O observers agree
on the successful complete physical receipt, including its signed-width
conversions and source allowances. They do not rerun the physical controller.
In addition, they compare every returned physical word bit for bit with a
separate interpreter of all emitted dense H/diagonal events and the staged
sparse schedule. staged_oracle.py recomputes quantized diagonal blocks by its
own pivoted inverse and applies each residual and product truncation at its
actual boundary, including coefficient pre-rounding in the forward lift. It
imports no producer page builder or rounded sparse observer. No interpreter
output is supplied to the physical execution.
All three observed dense boundary drift counts are zero. The receipt's cleanup
and ownership checks are separate physical evidence, supplied by its producer
and controller review.

This small admitted partition supplies complete execution evidence and does not
establish nonidentity interior physical performance, the production carve or
the asymptotic rate. The nonidentity interior evidence above is semantic. The
complete original-coordinate wrapper and its nonidentity layouts require their
own registered execution/review evidence. Retained native/Count/WordProduct,
codec, ownership and complete-cost premises and all five selected assumptions
remain explicit.
Subsequent questions are attachment to actual halo delivery and independent
closure of retained native/physical lifecycle/cost contracts, keeping #6895's
completed numerical source implication. Finite agreement, generic telescopes
and increased precision alone do not answer those questions.
