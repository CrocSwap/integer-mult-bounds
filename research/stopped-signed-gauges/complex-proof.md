# Complex deferred readouts on the stopped pair-tree word

This is a conditional composition of the frozen weighted pair-tree word
with the deferred-readout idea of Swapnil Jain / PR97, Paureel's frame geometry,
and icekylinx / PR104's full-rank complex residual interface. It retains the separately frozen stopped-pairtree package as a dependency. The inherited complex Gauss normal
form, copied-center and tensor endpoint proofs remain dependencies. The
finite schedule below has been executed and checked; a separately regenerated
stopped recurrence, precision bridge and three-stock assembly are required.

## 1. Exact scalar contract and center precedence

Let L be the literal 45,266-role word, V the data injection and J the full
rational readout. L consists of ordinary signed shears over characteristic
zero, not XORs on the payload. The frozen graph audit proves JLV=I exactly.
For target triple T the center coefficient on A_i is
`(2-21*[i in T])/42`; the disjoint coefficient is +1/2 and each of the three
pair-star coefficients is -1/2. Write C=JL. All columns C_s are fixed rational
vectors with denominator dividing 42. The exact reverse sweep bounds every
numerator by 24,740 and determines the complete nonzero support without
modular zero assumptions.

The center phase is the closure of the last operations producing the 24
center output roles under actual per-role sequence precedence. It contains
15,791 operations and touches 13,071 roles. Moving this closure first
preserves every original per-role order. A role outside the touched set is
neither read nor written during this phase, and no such role contributes to
a center output. Every center coefficient is nonzero on every target,
so all center copies must be read while every Y_T is at frame zero.

For each selected untouched role s choose a binary subspace sigma_s inside
its first frame A_s, nondegenerate for the ordinary binary dot product, and
inside t_T-perp whenever C_(T,s) is nonzero. For each T, the selected sigma_s
in the actual readout order form a nested chain. The exact chosen inventory
has 14,081 positive sigma_s, total dimension 180,444, maximum dimension 20.
All selected sigma spaces happen to be alternating; the construction and
endpoint argument also permit nonalternating nondegenerate spaces.

## 2. The complete forward local schedule

The initial X_S frame is its triple line, Y_T starts at zero, and the auxiliary
role s starts at sigma_s (zero for all unselected roles). This last statement
is an endpoint gauge, whose physical justification is given below.

1. Read every unselected dirty role out at zero with coefficient -C_(T,s).
   This is an explicitly specified fixed matrix, not an uncharged recursive
   transform. Its 21,298,670 nonzero scalar updates enter the new G0 charge.
2. Inject X only into the source-use roles needed by the center phase. Run
   that phase, raising roles along the original nested frames. Read copies
   of all 24 retained centers into Y at zero. Every rank-23 copy transform
   remains paid; the original role stays in its live frame.
3. In the chosen order, read each selected role at sigma_s with coefficient
   -C_(T,s), raising every affected Y along its verified chain. Each selected
   role still holds its initial dirty value because it was untouched.
4. Inject the remaining source-use roles, run all remaining L operations in
   their original relative order, and scatter ordinary roots at t_T-perp.
5. Raise auxiliary roles to the full local frame and apply the inverse of
   the actual reordered L: reverse its operation order and subtract every
   source. Raise X to full, subtract its source injections and finish every
   auxiliary at full. Y finishes at t_T-perp.

The source-use frames here are still triple lines, so postponing a source
injection does not introduce a new data-frame chain condition. Every
selected source-use role, if any, has sigma contained in that line. Center
source uses are injected before their phase; all others are injected after
both their possible dirty readout and the center copies.

In intrinsic frame coordinates the two dirty-readout groups together equal
-Cz. The actual fresh pass and center/ordinary scatters equal J L(z+Vx).
The inverse restores z+Vx and removal of V restores z. Thus the output is
`y - C z + J L(z+Vx) = y+x` for every dirty z and data y,x. The early center
reads use their completed values and later operations never change those
root roles. This is a linear identity over Q; three full scalar fixtures
check its implementation but are not substituted for the identity.

The schedule checker verifies 434,982 literal forward events, 152,154 actual
geometric edges, all equal-frame scalar additions, all nested nondegenerate
moves, source injection timing, center chronology, and every selected signed
readout coefficient. Orthogonal differences are explicitly checked for the
correct dimension and nondegenerate Gram. It then reverses the complete
signed event word, swaps the data banks and complements every binary frame;
every reversed frame incidence and copied-center event is checked. This is
the opposite local stage, with exactly the same rank histogram.

## 3. Multiplicative endpoint gauges and the sign

For a nondegenerate binary subspace U let C_U be the inherited complex
partial transform. For orthogonal U,V, the quadratic Fourier phases obey
`q_(U+V)=q_U+q_V mod4`, so `C_(U+V)=C_U C_V`. A nested nondegenerate
sigma inside A gives `C_A C_sigma^-1=C_(A minus sigma)`. These statements
hold for alternating spaces as well; an inverse is not silently replaced
by a forward transform.

Let H be the rank-h active tensor subspace in one local network and E=H-perp,
so the complete selected-axis transform is F=C_H C_E. Embed sigma in H.
For the first auxiliary bank choose the formal source label S=C_sigma and
sink label T=F C_sigma. These are labels defining the logical interpretation
of arbitrary physical inputs; no dense preprocessing is performed. The
local path begins at sigma and ends at H, hence its product is
`C_H C_sigma^-1`. Its final exterior is
`T C_H^-1 = C_E C_sigma = C_(E+sigma)`,
a single nondegenerate residual of rank m-h+dim(sigma). The full physical
endpoint is exactly `T S^-1=F` on every arbitrary input. Equivalently the
local path and exterior compose to F. No input-invariance assumption is
used: any physical input a has the unique intrinsic value C_sigma^-1 a.

For the second auxiliary bank retain the translated source C_E and sink
F C_E from the copied-center construction. The reflected local path starts
at zero and ends at H minus sigma, so its final global label is
`C_(I-sigma)=F C_sigma^-1`. The final exterior is therefore
`(F C_E)(F C_sigma^-1)^-1 = C_E C_sigma`,
again the same rank m-h+dim(sigma). Its complete source-to-sink quotient is
still F. All intermediate reflected labels remain the retained translated
labels, and all signed scalar coefficients are negated in reverse order.

The first-stage sink must be **F C_sigma**. Replacing it by the literal
complementary transform `C_(I-sigma)=F C_sigma^-1` while keeping source
C_sigma leaves a spurious `C_sigma^-2`. The all-address controls include a
noncoordinate odd line and a noncoordinate alternating plane; the wrong
complementary sink fails on 8 Fourier addresses and gauging only one endpoint
fails on 20 across the two cases. The selected alternating gauges happen to
have C_sigma=C_sigma^-1; the proof does not rely on that special coincidence.

The data sources and terminal frames are unchanged. Hence both interstage
data connectors, the inverse rank-one correction, and the inherited Z/sign
normalization of the tensor triple line are unchanged and remain paid. In
particular the endpoint copy uses C_U^-1, not C_U. No new claim is made by
replacing that signed phase identity with a dimension calculation.

## 4. Actual complete paid inventory

The forward local auxiliary rank mass is
`24*45266 -180444 =905940`.
The two local data chains have mass `2*2024*23=93104` and copied centers have
mass `24*23=552`. The actual histogram of these three classes is exported
separately by the literal checker, not inferred from their totals. Both axis
stages multiply it by 2v. Every original auxiliary contributes one exterior
of width `552+dim(sigma_s)` in each stage. Add the unchanged `2N` data macros
of width529 and `N` endpoint copies of width1. The resulting histogram agrees
exactly with the independent first-frame substitution/target-chain screen.
Its total rank is `W*576-N+L=110261771840`, W=191429920, L=2234496.
The largest child is now **572**, not552, and its exact halving degree is100.

Each scalar coefficient has denominator dividing42 and numerator bounded
by24,740. Charging64 to every literal event and explicit grouped readout
bounds its coefficient height, row-norm growth and fixed copy work. Expanding
and conservatively double-counting center scatters and fixed wrappers gives
`g=64*(434982+21298670+2*24*2024+8*24+8)=1397184256`,
`G0=N+2v*(g+2h)=5655806159168`.
This deliberately generous fresh bound must replace the old G0 everywhere
in the semantic/precision recurrence. The root-dyadic reachable-state proof
for the common odd21 grid is unchanged in form: each fixed rational update
adds at most one odd21 factor, completed tensor children add none, and the
new larger G0 and depth bound pay the whole unfinished chain.

## 5. Reproducible evidence and limits

Scripts and receipts in this package:

- complex_profile.py / complex-axis.json: reconstruct the literal word from
  fresh graph and matching files, derive exact signed covectors and sigma
  chains, and regenerate the complete rank inventory and fresh scalar charge.
- gauge_check.py / gauge-audit.json: full local frame chronology, reflected
  opposite word, per-class histograms and signed dirty fixtures.
- endpoint_check.py / endpoint-audit.json: exact Fourier phase/rank controls
  with odd and alternating gauges and rejecting endpoint mutations.

No pickle or supplied sigma witness is trusted. The producer derives all
sigmas from the fresh literal word, and the default acceptance check compares
regenerated deterministic evidence to the frozen receipts. Word fingerprints
hash the canonical uncompressed JSON, so gzip header differences between
Python versions do not affect mathematical provenance. The arithmetic
checker separately recomputes both exact moments and the full bridge.

No losing chronology is repaired by a free frame shrink. In particular an
attempt to read a center copy after positive target moves is rejected by its
required zero-frame chronology. Omitting the deferred dirty readout changes
the full scalar map. The currently verified local construction still relies
on the retained all-size complex normal form, copied-center/tensor endpoint
and streaming interfaces. Exact numerical recurrence/bridge/assembly checks
are separate evidence. No all-size theorem or new published result is claimed
solely from the geometry screen or its exploratory floating exponent.
