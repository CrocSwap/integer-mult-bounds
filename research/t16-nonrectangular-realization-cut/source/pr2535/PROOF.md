# Necessary mixed-width, multiple-call cuts

The object is one PR2169 class: bins with a common capacity and common set A
of allowed calls. Its width alphabet is (4,5,7,8,9). X_p counts bins of pattern
p, where p_w is the number of helpers of width w in that bin. Y_tw counts
helpers assigned to call t and width w in that class. A realization assigns
the helpers to bins, with at most one helper in each bin at each call.
All multiplicities are nonnegative integers. This is the retained owner's
class relaxation, not a new physical model or global packing optimum.

For every width subset U and call subset T, the necessary inequality is

    sum(t in T, w in U) Y_tw <= sum_p X_p min(|T|, sum(w in U) p_w).       (1)

Proof: a bin of pattern p can contribute at most |T| helpers to T by the
one-helper-per-call condition, and at most sum_U p_w helpers of these widths.
Sum this minimum over bins. This elementary capacity/Hall inequality is
standard; the contribution here is its explicit source-bound separation and
a strict mixed-width gap in the pinned search's implemented constraints.

For fixed U and k=|T|, the right side is independent of T. The largest left
side is the sum of the k largest call loads L_t=sum_U Y_tw. Therefore sorting
the call loads and checking each prefix is an exact separator for the entire
family (1). Ties can use any deterministic order. With five widths there are
31 nonempty U. For n calls and P represented patterns, the implementation
uses O(P log P + 31*(n log n + n P)) arithmetic operations. Missing/zero pattern
variables have coefficient min(k,sum_U p_w) too when inserting a cut in an
optimizer; the JSON lists coefficients only for patterns present in its input.

This does not assert sufficiency for the colored realization problem, and
does not solve the source MIP. No-violation output only certifies this family.
Global demands, exact idle profile, family and physical endpoint audits,
pricing and selected admission remain separate obligations.

## Strictness against both implemented families

Use the actual capacity-16 class 9 of mindiff_cls1.py, allowed calls 0..8,
224 bins, with two nonempty patterns and 222 empty bins:

    bin 0: two width 4 helpers, one width 8 helper (capacity16)
    bin 1: one width 8 helper                    (capacity8)

Call 0 and call 1 each request one width 4 and one width 8 helper; other calls
request none. Counts and capacity balance. All full per-call width-subset
Hall inequalities in glob.py pass: one bin sees width 4, two see width 8 or
their union. The optional single-width Gale-Ryser-style constraints also
pass. Width4's only nontrivial j=2 inequality is 2<=min(1,1)+min(1,1);
width 8 has no multiplicity above1. This verifies the stronger full Hall+GR
system, and hence the weaker single/all-width Hall system in mindiff_cls1.

But U={4,8},T={0,1} gives 4<=min(2,3)+min(2,1)=3, impossible. This proves a
strict strengthening on the class-level domain; it is not claimed to match
the source's global idle target or to have arisen in a source optimizer run.

Keep the same patterns and move call 1's width 8 helper to call 2. Then assign
bin 0 to (call0,width 4),(call 1,width 4),(call 2,width 8), and bin 1 to(call0,width 8).
The verifier checks this concrete legal placement. Hence rejecting the bad
flow need not ban its patterns: (1) depends on flows as well as pattern counts.

## Reported source failure and its limited inference

PR2169 SEARCH.json reports eleven four-width 4 bins in class 9, with only four
width 4 helpers outside calls{5,6,8}. Each such bin needs at least one helper
outside those three calls, so outside demand must be at least 11, a deficit 7.
Equivalently, subtract (1) for U={4},T={5,6,8} from width balance; the lower
bound is sum_p X_p max(p_4-3,0). Other patterns can only increase this bound.

The producer already diagnosed this failure. The c1 stage1 artifact is not
retained, so this package checks the stated conditional implication, not a
replay of that missing candidate. Source BAN forbids a whole pattern in
subsequent heuristic searches. A conditional inequality can instead keep
that pattern when enough distinct calls are supplied. The source's reported
1002 relocation lower bound was computed before BAN; this work neither
invalidates nor independently certifies that solver bound. Its final 1415-
relocation concrete map is unaffected.

## Evidence and scope

The selected and PR2169 maps each reconstruct 69120 helpers over 32256 bins,
144 classes and 144 calls. Their class aggregates pass all 182652 prefix
checks per map. This is a necessary-constraint check, not a replacement for
their native auditors. Window order, active-pair exclusion and phase ranks
are reconstructed from source-pinned events, PLAN and DATA-PHASES.

An independent literal call-subset loop agrees with the sorted separator
for all 2995 aggregate schedules from 19683 three-bin/three-call A/B/empty
placements and balanced one-helper perturbations: 14989 comparisons,
5928 violations. Every concrete placement is accepted. This finite check
supports implementation correctness; the elementary argument proves (1)
at every size. Receipt, source and parser controls are separate from it.

This is an exact strengthening of one search relaxation. There is no new
owner map, objective improvement, physical compiler, supplier, packing
optimum, empirical speedup, or new kappa claim.
