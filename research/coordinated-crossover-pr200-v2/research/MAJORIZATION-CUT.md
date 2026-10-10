# Global extremal-frame majorization cuts

2026-10-09. Pure mathematics and checked-integer C++ discovery, no Lean certificate, no all-column/prime closure, no new published kappa.

## Sufficient theorem

Let a legal finite physical compiler word have one frame F_i at each operation, fixed source/gauge/root/alias/target boundaries, and paid directed chain edges i -> j. Every edge has F_i subset F_j. Let f be increasing and concave on permitted nonnegative rank gaps, with f(0)=0. Construct ANY second legal schedule M_i with F_i subset M_i for every mutable i and identical fixed boundaries. Assume every M_i is nondegenerate and contains the required exact value span.

There is a linear-size explicit minimum-cut majorant for selecting F_i or M_i independently at each operation. A strict reduction of its objective is a sufficient certificate of a strict reduction of the actual complete paid rank objective. All stock, endpoints, source/target legality, chronological aliases and total rank mass remain unchanged. This is a legal-neighborhood optimization theorem; it does not claim global optimality or an all-size multiplication theorem.

For an edge with both endpoints mutable, write d_i=dim(M_i)-dim(F_i), d_j=dim(M_j)-dim(F_j), r=dim(F_j)-dim(F_i). The 00,01,11 cases always nest, and have costs E00=f(r), E01=f(r+d_j), E11=f(r+d_j-d_i). The 10 case nests precisely when M_i subset F_j; if legal, E10=f(r-d_i).

Define unary contributions u_i=E11-E01 and u_j=E01-E00. The affine objective E00+u_i*x_i+u_j*x_j agrees with every 00,01,11 cost. If 10 is illegal add a hard arc i -> j, prohibiting x_i=1,x_j=0. If 10 is legal its affine price is E00+E11-E01. Concavity implies E00+E11 >= E01+E10: these are two inner points versus two outer points with equal sum. Thus the affine price majorizes the true 10 cost. Both implications follow without requiring equal subspaces or a common join direction. For fixed boundaries retain the exact one-variable cost; no hard arc is needed where an endpoint contains both alternatives.

Sum over ALL actual physical and target-chain edges, including terminal pivot movements. Positive unary u becomes i -> sink; negative unary becomes source -> i with the usual constant offset. Use a hard capacity strictly greater than the sum of absolute unary capacities. The unchanged all-zero assignment is feasible and has the baseline objective. Consequently a minimizing cut with negative surrogate delta has actual delta at most that negative number. This proves sufficiency. Concavity defects are explicitly bounded, so the surrogate can also quantify how far it is from the best schedule in its binary neighborhood; this is useful for dropping an unproductive route, not a research result by itself.

A contraction schedule L_i subset F_i reduces to this theorem by replacing each frame with its ordinary annihilator, reversing every paid edge and exchanging F,L accordingly. Dimensions change from k to h-k, so every paid rank gap is exactly preserved. Nondegeneracy and required-value containment are verified on the original physical frames, not presumed from the annihilator representation.

## Concrete second schedules

The greatest feasible candidate is reconstructed backwards: M_i is the intersection of every successor frame, including all literal endpoint caps. The required values and current F_i stay contained because the initial word is legal. If a candidate frame is degenerate, freeze that operation at its current frame and restart backwards propagation. Since each failed round freezes at least one operation, the process terminates in at most N rounds with a legal schedule; in the observed PR200 input no freeze was necessary.

The least candidate is reconstructed forwards: L_i is the span of its exact required source-label value vectors and every predecessor frame, including literal source/gauge/target boundaries. This is a subspace of the current legal F_i. Freeze a degenerate candidate at F_i and continue forwards; successors still remain within their current frames. Again the observed PR200 input needed no freeze. Both candidates are explicit finite constructions rather than assumed transformation gadgets.

## C++ implementation and actual results

- `greatest.cpp` is the complete loader, exact fraction-free integer basis/kernel operations, checked signed-128 multiplication/subtraction, canonical interning, full physical/target graph reconstruction, nondegeneracy predicate for G=I-J/9, Dinic nomination and literal histogram recount.
- Input is the unchanged PR200 a1175449f34d39ff933d9d8ab23ced1f32b290ec word plus the already admitted 302-frame checkpoint. Staged immutable JSON and executable are on F:/proof/research/beyond-nlogn-20261009/threshold/frames. No Python was executed for this lane.
- Current graph: 41,288 operation nodes, 126,520 paid edges, rank mass 405,456. The stage factor3 is not part of this graph-level histogram.
- Complete greatest schedule changes14,487 operations and worsens entropy867200.2563234223 -> 898639.1065801512. Rejected as a whole.
- Its majorant cut chooses48 operations and improves entropy to867140.3594551166. Exact histogram delta {0:-24,2:+96,4:-72,10:-48,12:+48}. Surrogate delta -45.67759759837121, actual entropy delta -59.8968683057. This is a candidate beyond prior common-direction cuts, not a threshold-scale improvement.
- On that checkpoint the full least schedule worsens entropy to897647.8189150952. Rejected as a whole.
- Its majorant cut chooses1410 operations and reaches entropy866438.7403496904. Final cumulative1458 operation changes relative to the 302 checkpoint. Rank mass still405456. Total graph entropy improvement761.5159737319. There are zero degenerate freezes.
- `greatest-summary.json` contains every full exact histogram and surrogate decision ledger. `greatest-bases.json` contains the explicit integer rational bases for all1458 additional operations relative to the 302 checkpoint; it is NOT a standalone public-relative replacement file. Compose with the original302 witness before any full replay.

Every changed basis is independently reduced and every literal physical/target edge is rechecked for containment; all source/gauge/root/alias/read/terminal identities remain fixed. This does NOT replace the untouched original all-formal-column and all-used-frame prime certificate. New bases need that admission before publication or kappa pricing as a record. No such closure is claimed in this lane.

## Threshold assessment and route selection

The new graph entropy reduction is too small for the requested kappa >= .0007. At baseline normalized delta1936, approximately48 additional useful rank-deficit units would be threshold-scale at approximately unchanged entropy. The copied-center loss528 is therefore a higher-leverage target than continuing tiny frame cuts. Parent is pursuing a concrete hybrid264 missing-port and center dirty-completion route. This lane stops expensive frame cuts and preserves all exact witnesses and the generic sufficient construction for reuse.

## Retrieval and literature provenance

Prior exact cut contracts and proofs were read from the whole-subspace mincut notes, the rank-moment-to-exponent notes, PR200 frame continuation and actual public integer geometry checker. The canonical tree search found Mathlib `Analysis/SpecialFunctions/Log/NegMulLog.lean` (`strictConcaveOn_negMulLog`) and existing Problem18ProductAwareCost/Calculus majorization mechanisms; these are source retrieval, no new imports or Lean certification. The ordinary directed minimum-cut method and concavity/majorization are classical. This particular variable-frame majorant applies those methods to the compiler's complete physical/target ledger. Publication novelty is not established.