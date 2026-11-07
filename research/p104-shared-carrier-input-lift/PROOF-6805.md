# Paid retiming and independent-helper retirement

## Claim

Under the five retained framework assumptions, the supplied construction gives
`T(n)=O(n (log n)^(1−κ))` with **κ = 0.00330814**, improving the pending
#6726 claim 0.00330720. This is a proposed conditional result; the independently
selected frontier remains unchanged. Favorable local accounting alone would
not establish this claim: the native identity, actual caller, complete invoice
and parameter qualification are checked separately below.

## Chronology and arbitrary inputs

Indices are zero-based in the pinned native word. Frames 3, 749, 243 and 127
have dimensions 0, 3, 4 and 9, with strictly nested spans `E⊂A⊂F⊂V`.
Source event 14088 is `MOVE(80,749,127,False)`. No event from 12372 through
14087 reads or writes role 80. Advance that move to immediately before old
event 12372 and subdivide it as `749→243→127`, paying ranks one and five.
Skipped events act on other registers, and the two physical chart changes
compose to the original change. Thus the retiming preserves the old endpoint.
The new cut is between those two requests.

Let P be the normalized prefix on valid public inputs, with explicit owned initialization, and S the suffix. Neither is assumed invertible. The exact witness is:

\[
\begin{aligned}
a&=e_{80}^{T}+\tfrac12e_{26}^{T}-\tfrac12e_{368}^{T}
 -\tfrac12e_{95}^{T}+2e_{381}^{T},\\
b&=-2e_{95},\\
c&=2e_{383}^{T}-2e_{372}^{T}-2e_{382}^{T}-2e_{3}^{T},\\
d&=\tfrac12(e_{379}+e_{377}-e_{368}-e_{146}+e_{374}
 -e_{375}-e_{382}+e_{188}+e_{126}).
\end{aligned}
\]

Direct rational replay proves `aP=c`, `Sb=d`, and `ab=cd=1`. The supports
of c and d consist only of independent helpers with entry E and exit V.
All roles in a and b, and pivot p=368, are at F at the cut. These are actual
source identities, not inferences from a pairing rank or sampled inputs.

The retained dyadic basis construction produces G and J with row p of G
equal to c, `Gd=e_p`, row p of J equal to a, and `Jb=e_p`. Therefore
`Q=JPG^-1` has row p equal to `e_p^T`, and `R=GSJ^-1` has column p equal
to `e_p`. G acts among equal-boundary helpers and commutes with the old
normalized endpoint, which is identity on those helpers. Replacing the old
p value at the cut by a fresh independent input z changes only the returned
p value, from the old input to z. All other outputs are preserved.

The emitted word applies `G^-1` at E, the prefix, J at F, then `J^-1` and
the suffix with p renamed to fresh role 771, and the renamed G at V. Old p
returns at F; fresh role 771 starts at F and returns at V. The rank-nine helper
is thereby replaced by independent rank-four and rank-five helpers. The new
input is arbitrary, never presumed zero. All scalar coefficients are legal
dyadics; no broader cross-role SWAP lemma is needed.

All 29 owned labels shift by one to accommodate the public input. The
47 lifetimes and peak 14 are unchanged. Source and candidate have the same
45 nonzero pre-CLEAR observations among 47 clears, with the same owned labels,
charts and zero/nonzero pattern. The erased functionals can change under the
bases; their legality remains conditional on `owned_erasure`. The one COPY
is monitored before overwrite and its destination is zero. Full primary and
independent adjoint replays check all 641,601 candidate endpoint coefficients.

## Strict gain

Writing `H_r=r^t`, the literal per-call deltas are

\[
\Delta P=H_1+H_5-H_6,\qquad
\Delta T=H_4+H_5-H_9.
\]

Hence `Δ(T−P)=H4+H6−H1−H9`. For `f(x)=x^t`, `0<t<1`,

\[
f(4)+f(6)-f(1)-f(9)
=\int_1^4[f'(x)-f'(x+5)]\,dx>0.
\]

Both rank masses remain unchanged. More generally, a legally splittable
helper E→V and a contact-free donor A→V, with nested dimensions e<a<f<v,
give the sufficient economic pattern

\[
(f-e)^t+(v-a)^t-(f-a)^t-(v-e)^t>0.
\]

This compares equal-length increments of a strictly concave function. It pays
the donor subdivision; it does not supply the independent-channel identities
or legal physical frames for any untested application.

The recounted local target profile is
`{1:14,2:8,3:4,4:109,5:17,6:3,7:9,8:40,9:360}` and paid profile is
`{1:2232,2:454,3:490,4:109,5:153,6:7,7:9,8:1}`.

## Physical maps and complete consumer

All 2,940 distinct used native maps, 208 main adapters and 1,128 helper
normalizers are checked by signed Pauli action and exact absolute phase.
The changed pairs `(749,243)`, `(3,243)` and `(243,127)` additionally receive
all 512 explicit Gaussian-column checks each. Phase-only corruptions reject.
Common-frame scalar identities act componentwise, with scalar coefficients
outside tensor powers. Factorwise maps and frame induction give the same
interface at positive tensor widths within the retained native/precision
contracts.

The unchanged #6726 caller is rebuilt with both retirements: 34 main roles,
606 instructions, 18 distinct native stages, 15 thin queries, 12 IDLE events,
six IDLE_ONE events and 100 ordinary normalizations. Independent Laurent-ring
replays check all caller entries. The new native retains precisely the main
interface each LOCAL event consumes. Physical replay checks 7,488 contacts,
53,248 central-square columns and all whole-idle/output phases.

Allocate 3,536 main fields and eighteen disjoint blocks of 564 arbitrary
native helpers: 13,688 productive fields. The 29 owned labels and one reused
thin-query scratch field are separate and uncredited. The eighteen additional
helper inputs are not shared. Their complete boundary normalizer count is
20,304, an increase of 36.

| Rank | Productive T | Paid P |
|---:|---:|---:|
| 1 | 356 | 41,736 |
| 2 | 144 | 8,172 |
| 3 | 72 | 8,820 |
| 4 | 1,962 | 1,962 |
| 5 | 306 | 2,754 |
| 6 | 54 | 126 |
| 7 | 162 | 162 |
| 8 | 720 | 226 |
| 9 | 6,688 | 0 |
| 16 | 0 | 1,664 |
| 17 | 1,664 | 0 |
| 32 | 208 | 1,040 |
| 33 | 832 | 0 |
| 40 | 0 | 208 |
| 41 | 208 | 0 |
| 73 | 208 | 0 |
| 145 | 104 | 0 |

There are 66,870 paid requests, paid rank mass 178,080 and surplus 760.
The signed improvement over the identical #6726 caller is exactly eighteen
times the local gain. Native scalar allowance rises by 384 to 138,374.
Including every charged request, normalizer, main adapter, lifetime, fixed
route rate and caller scalar gate gives 5,533,374 units per native call,
below 10⁷, and a complete ordinary upper envelope 535,415,008 below 10⁹.
The route/precision rates remain framework contracts; all multiplicities
and coefficient heights are freshly checked.

Both canonical-job boundaries are charged using the explicit decomposition
from the pinned #6763 audit. A scattered set of r axes is sent to the first r
axes by pairing selected indices outside that set with missing indices inside
it. These two-axis exchanges form an actual involutive permutation. Main jobs
also receive both nine-axis q-basis changes and their required translations;
whole idles receive both canonicalizing maps; thin queries receive both q-basis
maps and their inverse-Gaussian phase translation. The actual inventory is:

| Fixed elementary map | Count |
|---|---:|
| Main input/output two-axis exchanges | 144,768 |
| Main input/output q-basis maps | 6,656 |
| Main endpoint translations | 3,328 |
| Whole-idle input/output two-axis exchanges | 127,296 |
| Thin-query input/output q-basis maps | 3,120 |
| Thin-query translations | 1,560 |

Thus 286,728 maps are charged at 1,000 units each. The complete envelope is
`18·10^7 + 68,570,112 + 24,960 + 91,936 + 286,728,000 = 535,415,008`.
The fixed-map rate is applied to each at-most-nine-axis map separately;
native contacts satisfy their separate 17-axis bound. It is not applied once
to an arbitrary 153-axis transformation. Input adapters on fresh fields are
scheduled before their first use; output adapters on retired fields can be
deferred to the final output boundary, preserving the checked retention.
This closes the additional routing bill identified in the earlier physical
audit. It replaces the predecessor driver's partial 252,223,008 estimate;
the complete bill still fits the unchanged 10^9 budget used by the compiler.

For coordinate sup norms, the charged scalar macros have elementary
majorants, monomial routes have norm one, and a rank-r Gaussian is bounded
by `2^(rf)`. The conservative envelope `2^(10^9+178080f)` therefore controls
every prefix, suffix and subinterval. COPY is physically an ADD into owned
zero; approximate residual errors still propagate as ADD errors, rather than
being discarded by its ideal overwrite notation. INIT/CLEAR retain their
explicit owned-erasure premise. Summing propagated defects gives finite
precision choices under the inherited implementation contract. Storage counts
all productive fields and disjoint owned/query slots, plus movement scratch
under the retained tape contract. Fixed descriptor/precision constants are
absorbed at fresh outer thresholds using strict exponent gaps, not presumed
absorbed at the displayed finite supplier threshold.

## Exact qualification

Two separately implemented rational interval engines certify opposite signs
at 0.0033081451891 and 0.0033081451892 and a positive margin at tested saving
0.003308145. A rational derivative upper bound is negative through the retained
BIT cap. The claim 0.00330814 is strictly lower; the compiler gap is
`g=(0.003308145−0.00330814)/7=1/1,400,000,000`.
The next eight-decimal value 0.00330815 already exceeds this fixed invoice's
certified raw crossing.

Strictification uses power 1920, cutoff/floor 11/12, offset 1/7, reserve
10⁻²⁷ and decay 31/32. Fresh moments verify alpha, gamma and completion-delta
bounds, counting all 13,688 targets. Exact normalized contraction is below
one and `11^64<12^63`. The compiler checks shifted exits, complement capacity
and initial range using theta 63/64, logarithm power 2100 and maximum target
rank 145. It finds an explicit finite `N=2^H` by integer inequalities and
checks the adjacent grid point; this enormous word is not materialized.

The retained BIT construction supplies saving 17/5000, strictly above the
tested complex saving, with its stock and ordinary savings inequalities
recounted. Set complex-uniform saving `κ+6g`, `b=κ+5g`, `a=κ+4g`, `q=κ+3g`,
epsilon `1−g`, beta `1−3g`, `r0=g/10`, and stop/layout/d all g. All 54 strict
and four functional outer inequalities pass. An insufficient BIT budget
rejects. Exact fractions, margins and threshold are in `RESULT.json`.

## Qualification and credit

The finite identities and inequalities support the proposed conditional
construction. They do not independently verify the full rounded multiplier,
eliminate analytic/precision assumptions, establish admission of pending
predecessors, or certify optimality. The five named assumptions remain.
Separate AI-assisted review provides implementation diversity, not human
or proof-kernel acceptance. Credit is retained as listed in the README and
original source notices; this extension is by @CubeJerry with OpenAI assistance.
