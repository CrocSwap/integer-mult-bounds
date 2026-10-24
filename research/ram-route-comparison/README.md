# Comparing native Word RAM with the TM route on equal footing

The present evidence supports a native research backend, not an exclusive switch justified by a proved computational advantage.

The decisive comparison is on the SAME Word RAM, packed input/output, exact product contract, charged setup and word width C log n. The optimized TM route is not one RAM instruction per tape step. PR #4541 constructs logarithmic-window batching with total cost

    O((T(n)+n+m)/log(n+2) + (n+2)^(1/16)*log(n+2)).

For multiplication with m <= 2n and the retained conditional TM bound T(n)=O(n*(log n)^(1-kappa)), this already gives O(n/(log n)^kappa) RAM operations. The additive setup and IO terms are absorbed for the present fixed kappa below 1. Its instruction model does not require word MUL or DIV. PR #4552 independently checks its parameters and packed macro simulation; that finite review does not establish all antecedent multiplication assumptions. PR #4553 separately covers packed codecs.

Our latest native result also gives O(n/(log n)^0.0030217758), under its explicitly retained native/analytic premises. Thus the +4e-10 number improves the previously reported NATIVE backend in PR #4635; it is not a stronger Word RAM complexity guarantee than transferring the same latest TM bound. The native construction avoids the TM simulator, which is architectural independence rather than an established speedup. Its DIV-free variant does not change this comparison.

A useful next success would be a strictly stronger complete native upper bound on that common model, or a complete implementation showing a measured advantage under a specified workload and hardware. A smaller proved upper bound is a stronger guarantee; it does not alone prove the old algorithm has a slower actual runtime. Neither source presently supplies a complete practical implementation or a claimed usable cutoff.

## Positive adoption result

PORTFOLIO-THEOREM.md constructs a uniform native-first portfolio that alternates the two correct RAM algorithms in disjoint contexts, charges each route's setup, and returns the first completed exact product. Its cost is O(min(t_native,t_packed)+n/w), with constant dispatch/arena overhead. Consequently an experimental native backend can be adopted while retaining the better runtime of the two up to constant overhead. This is a universal sufficient construction, not an impossibility result or an invented speed advantage. Correctness requires the stated correctness contracts of both candidates; racing an unproved implementation does not certify its answer.

The literature worker's SWITCH-DECISION.md supplies the comparison table, exact meaning of a positive exponent gap, and a full-product benchmark protocol. The packed-simulation theorem and independent small-machine checks, when present alongside this report, are supplementary operational evidence. No fresh Lean kernel proof, complete multiplier, actual comparative benchmark or new kappa is claimed by this decision document.

## Evidence and predecessor credit

Primary project sources: https://github.com/CrocSwap/integer-mult-bounds/pull/4541 , https://github.com/CrocSwap/integer-mult-bounds/pull/4552 and https://github.com/CrocSwap/integer-mult-bounds/pull/4553 . The actual native proof is pinned in the preceding native-wordram-tightening package. Exact-head source reads and their limits are recorded by the comparison workers; public API refresh was rate-limited. No selected frontier, canonical DAG, proof module, predecessor package or uploaded branch has been changed.

Credit Dugongue's #4541/#4630/#4635 native and transfer work, Ryanson Jonathan/pinterbanget's #4552/#4553 checks, Hopcroft/Paul/Valiant's classical logarithmic simulation, Fuerer's machine-model analysis, the Lax/Problem 1.8 compiler lineage, Cao Yifan's #4610 source profile, Cinna Davis and retained supplier/compiler/analytic contributors, and all credited source owners. Prepared for Dugongue with substantial OpenAI Codex assistance: one lead and three comparison/review workers. Classical dovetailing and logarithmic simulation are credited precedents, not novelty claims.

## Reproduction

Run `python3 -I -O -B research/ram-route-comparison/verify.py` from the repository root, or run verify.py from a Git-free package copy. Python 3.12 standard library only; no network or Windows dependency. The proof documents establish informal universal constructions; finite checks address parameters and packed window execution. No new kappa or practical speedup is claimed.

The frozen native proof and arithmetic receipt are in native/, with their local source commit and hashes in SCIENTIFIC-SOURCES.json. This is source evidence for the compared conditional claim, not an independently rerun native compiler or proof of its inherited universal premises. The portfolio may retain a TM-derived branch during validation; it is not the final TM-free architecture requested for a native production backend.

## Open next questions

The next useful result is a complete improved native bound after all costs, or an implemented full-product comparison with declared setup/reuse policy and hardware. Begin with the actual dominant provider/controller invoice and literal ownership/precision ports; neither a generic table theorem nor an isolated native kernel supplies that missing gain. Independently review the supplied universal simulation/portfolio proofs before relying on this report as accepted mathematics.
