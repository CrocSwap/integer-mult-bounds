# Task card - KB5e: the chi(Z) >= 4 case of F-star residue (ii)

Task ID / proposed scope key: kappa-blocker KB5e (explicit open request from
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166); chooser draw
seed `73765f295ddd17bbb472f87c2beac209`, track `recursive-interfaces`
(suggestions: centre-path-sharing, connector-alphabet-change,
joint-query-controller). Scope changed from the drawn cards per the assignment.

Base commit: `066766afb181a421eb851b8d73bb0ba71a78a170` (assignment pin).
Predecessor heads at card time (to be re-verified at submission):
PR 2717 `7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3`,
PR 2747 `a2bab9978c8149dc5965558ea9277da07bc750e7`,
PR 2774 `ceaf5acf976cee2f70a680f2d513f12baa634870`,
PR 2869 `153b93c1c0e9ee1c50677ae04d48f1f7f0b1700e`.
Frozen pins of DreamingOfClouds' fixture data (sha256
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` for
`tied_min.json`, `86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`
for `cex_min_1.json`) stay immutable.

Concrete object and question: for exact 3-total rational decoders
`M = sum_{j=1..3} p_j q_j^T` on `v` lines (`M_tt != 0`), the zero digraph
`Z = {(t,s) : t != s, M_ts = 0}` and its dichromatic number `chi(Z)`.
PR 2774 proved both canonical fixtures have `chi(Z) = 3` exactly (unconstrained)
and left open (its open question 2, also PR 2717's open question 2): can a
rank-3 zero digraph have `chi(Z) >= 4` at all? Settle that case: (a) prove it
vacuous or reducible (e.g. `chi(Z) <= 3` forced by rank-3 structure, or
`chi(Z) >= 4` forces anchor/MX coverage of `floor(2v/3)`), or (b) isolate a
minimal `chi(Z) >= 4` fixture and settle F-star on it (exact cert vs
`floor(2v/3)`, D(t)-pivot analysis), or (c) produce an F-star falsifier
(`cert(M) < floor(2v/3)`).

Scope status: changed (authorized explicit open request). The chooser draw
landed on the standard catalogue cards; the assignment names the KB5e request
from discussion 1166 as the recorded reason. Pair-collision check before
computation (toolkit `disc-comments --grep`, discussions 1317 and 1166,
including nested replies, 2026-10-16 ~05:40-05:50 UTC) found no live claim on
this object: the last F-star activity is KB5d's DONE/RELEASED (PR 2869,
2026-10-16 05:38 UTC). Refined overlap re-run on the object's proper names
(zero digraph, dichromatic, chi(Z), pivot constraint, D(t), F-star, cert,
3-total decoder) found only the known predecessors (PRs 2717/2747/2774/2869,
PR 2335 census, PR 2111/2162 fixtures) and unrelated packages.

Existing restriction being addressed: PR 2717's demoted residue (b) "zero
digraphs that are not 3-dichromatic (Lemma MP then gives only
sum_i MAS(Z[C_i]))" after PR 2869 renamed the residue classification to
(i') cancellation lines {t : v2(M_tt) > gamma} plus (ii) zero digraphs. Not a
restriction being relaxed. We keep the maintainer's reviewed distinction
(efficient1700 review of PR 2717/2774): ordinary 3-dichromaticity and
nonempty D(t) lists do NOT imply a D(t)-compatible acyclic partition (retained
rank-2 counterexample `check-2717-pivot-counterexample.json`); unconstrained
chi(Z) and D(t)-compatible dichromaticity are reported as separate quantities.

Method; explicit parameter ranges: exact stdlib integer/F2 arithmetic. Engine
adapted from PR 2717/2747/2774 (Aaron Wang) on DreamingOfClouds' PR 2111 model.
Quantities per instance: Z, chi(Z) exact by subset DP (acyclic-subset DP +
min-partition DP), D(t)-compatible 3-dichromaticity (matched-pivot value
max_c sum_i MAS(Z[C_i]), exhaustive over pivot maps when the product of |D(t)|
admits), anchor reach |S_gamma| and cancellation-line count (Lemma SG,
PR 2869), exact cert(M) by exhaustive a-enumeration + exact b-completion DP
where feasible, engine witness + independent replay otherwise, bounded
admissible-B chain scan as falsifier criterion (chain cost >= cert is proven).
Generators aimed at the chi question: symmetric perpendicularity point sets
(M = P P^T, Z = digons of the orthogonality graph of {p(t)} in Q^3),
one-sided asymmetric sets (M = P Q^T), odd-cycle-seeded and Mycielski-biased
mutual-zero patterns, plus small-integer random boxes. Smallest-first:
v ascending; smallest falsifying instance first; one bounded pivot maximum;
early kill with the exact obstruction recorded.

Nearest overlapping PRs and why this adds something: PR 2774 (Aaron Wang)
computes chi(Z) of the two fixtures (= 3 exactly) and explicitly leaves "can
chi(Z) >= 4 happen at rank 3?" open (its open question 2); this package answers
that question over a declared domain and settles F-star on any fixture found.
PR 2717 (Aaron Wang) names the residue and proves Lemmas SF/MP/RK/AN; PR 2747
(Aaron Wang) proves Lemma MX and closes class (i) on the fixtures; PR 2869
(Aaron Wang) collapses class (iii) and renames the residue. PR 2335 (Aaron
Wang) is the 196-instance falsifier census (v = 4..12), whose generators were
not aimed at chi(Z); its domain is not repeated as a census. The efficient1700
maintainer review (check-2717-pivot-counterexample) constrains every claim
about D(t)-compatible partitions; we do not restate the demoted inferences.

Declared milestone: local module (scoped residue result / obstruction record);
no supplier, no kappa, no frontier change.

Optimistic full cost budget; required observable improvement: no kappa in
play; the price is one bounded deterministic stdlib run (registered verify
below 600 s) plus written analysis.

Unresolved consumer/restoration costs; family expansion decision: none
(missing-lemma work, not a construction); no expansion round follows.

Success evidence; falsification test; time/compute cap: PASS markers from
verify.py plus README analysis: recorded anchors reproduced first (PR 2717:
tied_min 11/12, cex_min_1 18/19, chain 22; PR 2747: MP/MX 9 and 16; PR 2774:
chi(Z) = 3 unconstrained on both fixtures yet non-3-dichromatic under D(t);
PR 2869: reach = anchor_good on both fixtures, 84-instance search 0
falsifiers); then the chi(Z) >= 4 verdict with exact evidence per instance.
Falsifier test: explicit admissible B with sum_j rank_F2 B[R_j,A_j] <
floor(2v/3), or exact cert < floor(2v/3) where exhaustive; corrupted witnesses
must fail the independent checker. Cap: one session, single-process stdlib
Python 3.12, registered verify command below 600 s.

Predecessor authors; intended artifact and reproduction command: F-star,
cert(M), L8 labellings and the proven chain cost >= sum_j r_j >= cert(M):
DreamingOfClouds (with Claude Opus 5.5 (Anthropic) via Claude Code assistance),
PR 1590. Fixtures tied_min/cex_min_1, their recorded one-copy limits 11/18
(CP-SAT, recorded) and the cost-22 pairing: DreamingOfClouds, PR 2111/2162.
Lemmas SF/MP/RK/AN and the residue: Aaron Wang, PR 2717. Lemma MX: Aaron Wang,
PR 2747. Fixture dichromatic structure and the zero-digraph machinery: Aaron
Wang, PR 2774. Lemmas SC/SG, class (iii) collapse, residue rename: Aaron Wang,
PR 2869. Exact cost 12 of tied_min: Aaron Wang, PR 2379; exact cost 21 of
cex_min_1: Nick Petalas, PR 2206. Artifact:
`research/fstar-chi4-zero-digraph-seed73765f29/` (TASK.json, SOURCES.json,
VERIFY.json, verify.py, data/, CERTIFICATE.json, README.md). Reproduce:
`python3 -B research/fstar-chi4-zero-digraph-seed73765f29/verify.py` then
`python3 scripts/research_package.py --package
research/fstar-chi4-zero-digraph-seed73765f29 --check-only`.
