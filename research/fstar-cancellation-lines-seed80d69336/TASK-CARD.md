# Task card (local, written before substantial computation)

Task ID / proposed scope key: drawn card `replay-runtime` (scope key
`b1dd41940c60d240b47a`, chooser track `verifier-engineering`, OS seed
`80d6933678e809418135a00a66e8ea0c`); scope CHANGED to kappa-blocker **KB5f**,
the cancellation-line residue (i-prime) of open problem F-star, per the
assignment's authorized "explicit open request" (discussion 1166). Package
scope key: `kb5f-cancellation-lines`.

Base commit; exact predecessor and dependency heads: base main
`38746ad3f6ffebcc0275e286b1dbb733d7c696dd` (canonical main at assignment; to be
refreshed before submission). Predecessors, authors verified against current
ground truth with `gh pr view --json author,title` on 2026-10-16 (all five by
Aaron Wang (navinor), with help from opencode):

- [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) —
  Lemmas SF/MP/RK/AN and the residue; branch `research/agent-63-fstar-proof-3096ed3f`,
  head `7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3` (OPEN).
- [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) —
  Lemma MX (mixed anchor-repair-pivot), tied-residue closure; branch
  `research/agent-65-fstar-tied-residue-dcc97691`, head
  `a2bab9978c8149dc5965558ea9277da07bc750e7` (OPEN).
- [PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) —
  zero digraphs, matched-pivot floor; branch `research/agent-66-fstar-zerodigraph-e9937f18`,
  head `ceaf5acf976cee2f70a680f2d513f12baa634870` (OPEN).
- [PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869) —
  Lemmas SC/SG, residue rename to (i-prime) cancellation lines + (ii) zero
  digraphs; branch `research/agent-67-fstar-residue-iii-kb5d-8a3f`, head
  `153b93c1c0e9ee1c50677ae04d48f1f7f0b1700e` (MERGED 2026-10-16T07:32:07Z).
- [PR 2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890) —
  chi(Z) >= 4 narrowing; branch `research/agent-69-kb5e-chi4-73765f29`, head
  `08a44355403604c346f8d907811edce992382cc4` (OPEN).

Frozen source pins (byte-identical vendored copies, sha256 verified
2026-10-16): `tied_min.json`
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93`,
`cex_min_1.json`
`86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`,
`cex_min_1.B22.json`
`15f5039069a175831f92c4ffe023a23a6f6e6bd6665f0ca2c2734bbe672b51ef`,
`cex_min_1.witness.json`
`153f4d2e8dc262f547a91f2daff9724cab88beb4d45c399497efc68a8ed2c933`.

Concrete object and question: exact 3-total rational decoders
`M = sum_{j<=3} p_j q_j^T` on `v` lines with nonzero diagonal (F-star:
`cert(M) >= floor(2v/3)`; `research/root-unit-decoder-lemmas` section 7, OPEN).
Residue (i-prime) = the cancellation lines `C = {t : v_2(M_tt) > gamma}` with
`gamma = min_j c_j` the global content floor (PR 2869 Lemmas SC/SG): exactly the
lines no mod-2 anchor of any normalization can mark. Question (CORE): when more
than `floor(v/3)` lines are cancellation lines (anchor short of threshold), do
AN+SG+MP/RK/MX and repair/ordering still certify `floor(2v/3)`, or what is the
true residual obstruction? Plus (CORRECTIVE) the PR 2717 dyadic-corollary
normalization gap found by PR 2869.

Scope status: **changed**; reason: authorized explicit open request (assignment
KB5f, discussion 1166), recorded per the assignment; the draw landed on
verifier-engineering cards `replay-runtime`/`portable-replay`, not this object.
Pair-collision check before computation: `disc-comments --grep` on discussions
1317 and 1166 (nested replies included), 2026-10-16 07:50-07:55 UTC: no live
CLAIM on cancellation lines or the dyadic-corollary fix; KB5d/KB5e/KB3d threads
are DONE/RELEASED and cover other objects. Entry overlap survey
(`find_overlap.py`, explicit terms, complete pagination, 07:50-07:51 UTC) found
only the known F-star lineage (PRs 2717/2747/2774/2869/2890, PR 2335 census,
PR 2111/2162 fixtures) and unrelated packages.

Existing restriction being changed (or exact claim being audited): none
relaxed. Audited: PR 2717's corollary sentence "F-star holds for dyadic decoders
with at most one-third even diagonals" (normalization gap as literally stated:
dyadic entries do not imply the 2-integrality Lemma AN assumes; corrected via
PR 2869's Lemma SC/SG gamma/S_gamma formulation). Extended: PR 2747's Lemma MX
two block orders (its open question 2, insertion-finite mixing) on the
cancellation-line axis.

Method; explicit parameter ranges/candidate alphabet: exact stdlib integer/F2
arithmetic. (a) Reproduce every recorded anchor first (PR 2717 tied_min 11/12,
cex_min_1 18/19, chain 22; PR 2747 MP/MX 9 and 16 over 4096/6144 pivot maps; PR
2869 reach = anchor_good 0/12 and 8/19; PR 2890 PASS_FC4_CALIBRATION). (b)
PROVEN lemmas: tie-parity classification of cancellation lines (tau(t) =
number of content-minimal totals at t; cancellation iff tau even; tau = 2 lines
carry two tied totals inside D(t); |D(t)| = 1 lines are pivot-forced) and
insertion-finite mixing (Lemma CL3: an anchor line is placeable at a cut of the
pivot order iff no pivot-order path forces an R(x)-vertex before an L(x)-vertex;
jointly insertable anchor lines add to sum_i MAS(Z[C_i])). (c) CHECKED
settlement of tied_min (12/12 cancellation lines) and cex_min_1 (11/19) through
the full ladder: anchor, repairs, pivots, insertion-mixed, engine cert. (d)
Smallest-first falsifier search, v = 3..12, k = 1..v cancellation lines exactly,
deterministic generators (integer generic, tied-pair, negative-content dyadic,
adversarial-MP dense-zero), falsifier criterion: exact cert < floor(2v/3) where
exhaustive a-enumeration terminates, or an explicit admissible B with chain cost
< floor(2v/3); certified instances carry replayed L8 witnesses.

Nearest overlapping PRs and why this adds something: PR 2747 (its open
questions 1-2 are this object's repair/ordering core; it witnessed MP on 42 tied
instances and recorded the 6144/6144 mixed-route obstruction on cex_min_1, but
did not implement the insertion criterion or search the 1..v cancellation-line
axis); PR 2869 (named the residue and the anchor-count axis; its open question 1
asks exactly for anchor+repairs vs threshold on tied-heavy decoders); PR 2717
(tied-minima obstruction named, engine design); PR 2890 (chi(Z) machinery; a
different residue). This package adds the tie-parity lemma, the insertion-finite
mixing lemma with its exact criterion, the fixture settlement of the mixed route
beyond the two block orders, the cancellation-line-axis falsifier search, and
the corrective dyadic-corollary text.

Declared milestone: local module (missing-lemma/audit work; no kappa).

Optimistic full cost budget; required observable improvement: no kappa or
supplier budget in play. Price: one bounded deterministic stdlib run (registered
verify below 600 s) plus written analysis.

Unresolved consumer/restoration costs; family expansion decision if continuing:
none; this is residue mathematics on F-star, not a supplier claim.

Success evidence; falsification test; time/compute cap: PASS markers from
verify.py (controls, calibration, correction-gap reproduction, insertion
analysis, cancellation search) plus README claims labelled PROVEN/CHECKED/
DEMOTED; falsification test as in (d); one session, single-process stdlib
Python, registered verify command below 600 s, one bounded pivot maximum.

Predecessor authors; intended artifact and reproduction command: see head list
above (F-star object and fixtures: DreamingOfClouds (Claude Opus 5.5 (Anthropic)
via Claude Code assistance) in PR 1590/2111/2162; lemmas and residue: Aaron
Wang (navinor), with help from opencode, in PRs 2717/2747/2774/2869/2890).
Artifact: `research/fstar-cancellation-lines-seed80d69336/` (TASK.json,
SOURCES.json pins, VERIFY.json, verify.py, data/ byte-identical fixture copies,
CERTIFICATE.json written by verify.py, README.md). Reproduce:
`python3 -B research/fstar-cancellation-lines-seed80d69336/verify.py` then
`python3 scripts/research_package.py --package research/fstar-cancellation-lines-seed80d69336 --check-only`.
