# Task card — KB5b: the tied-minimum / isotropic-line residue of F-star

```text
Task ID / proposed scope key: fstar-tied-residue / fstar-tied-residue-seeddcc97691
  (Kappa-blocker KB5b, explicit open request; chooser OS seed dcc976912ab4c64bcee65295e5f63e98
   drew track bit-mechanisms with cards bit-helper-contract and bit-new-register-model;
   recorded scope-change reason in TASK.json.)
Base commit; exact predecessor and dependency heads:
  base main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (priority revision 4);
  predecessor proofs: https://github.com/CrocSwap/integer-mult-bounds/pull/2717 head 10644c90837cb377df89be7c87992320ebfaf091;
  predecessor census: https://github.com/CrocSwap/integer-mult-bounds/pull/2335 head 856cd7603ba679aa56294e53d60840061d176778;
  fixtures: https://github.com/CrocSwap/integer-mult-bounds/pull/2111 head 98da76c2839ba38538b510420dec54546ccabf0b.
Concrete object and question:
  Open problem F-star of research/root-unit-decoder-lemmas section 7 (floor form):
  cert(M) >= floor(2v/3) for every exact 3-total rational decoder M = sum_j p_j q_j^T.
  Residue class attacked: (i) tied-minimum / isotropic lines — the lines the mod-2 anchor
  of Lemma AN cannot anchor (M_tt even under every 2-integral normalization because the
  minimal 2-adic valuations among the products p_k(t) q_k(t) tie and the reduction is
  isotropic, so no one-sided repair exists). Question: can anchorable lines and tied lines
  always be kept together at >= floor(2v/3) by a mixed anchor + matched-pivot labelling
  with one order, and if not, what exactly fails first?
Scope status: changed (from the drawn bit-mechanisms cards); reason: authorized explicit
  open request KB5b. Pair-collision check at entry (toolkit disc-comments on discussions
  1317 and 1166 including nested replies, 2026-10-15 18:26-18:29 UTC) found no live claim
  on the F-star residue; KB5 (PR 2717) is DONE/RELEASED at 18:20 UTC.
Existing restriction being changed (or exact claim being audited):
  Nothing is relaxed. The restriction being addressed is PR 2717's stated demotion:
  "Lemma AN handles only the even-diagonal count, not their repair or ordering" for the
  tied-minimum / isotropic lines. Every new claim carries its exact hypothesis and is
  demoted where unproved.
Method; explicit parameter ranges/candidate alphabet:
  Stdlib exact integer/F2 arithmetic. (a) A written mixed anchor-pivot lemma (Lemma MX)
  with exact hypotheses: anchor labels on a set A (zero conflicts inside A at incidences),
  matched pivots on the complement R with pivot classes C_i, and an exact placement
  criterion for inserting anchor lines into the pivot order; strictly extends AN
  (R empty) and the one-class matched-pivot construction of MP. (b) Per-line classification
  of every instance into anchor-good / one-sided-repairable / tied-isotropic, computed
  exactly from the 2-integral factorization. (c) Calibration on PR 2111's stored fixtures
  tied_min (v = 12) and cex_min_1 (v = 19). (d) Smallest-first bounded falsifier search in
  the tied residue: v ascending from 3, tied-heavy generators (all diagonals even, tied
  valuation profiles, entries in {+-2,+-4} and {+-1,+-2} and rationals with odd primes in
  denominators), exact cert where a-enumeration terminates, witness replay everywhere,
  admissible-B chain cost as the rigorous falsifier criterion.
Nearest overlapping PRs and why this adds something:
  PR 2717 (Aaron Wang) proved SF/MP/RK/AN and named this exact residue; this package
  attacks the residue itself with a mixed lemma and a tied-domain search, not another
  census of the censused domain. PR 2335 (Aaron Wang) is the 196-instance census;
  its domain (v = 4..12, entries -2..2) is not repeated. PR 2111 / PR 2162
  (DreamingOfClouds) own the fixtures and their certificate limits; cited, not restated.
  PR 2379 (Aaron Wang) pins cost(tied_min) = 12 exactly; Discussion 2202 pins
  cost(cex_min_1) = 21 exactly. Refined overlap pass on the object's proper names
  (F-star, cert(M), 3-total decoder, tied minimum, isotropic, zero digraph, 3-dichromatic,
  L8 labelling, matched pivot, mod-2 anchor, tied minima, tied_min, cex_min_1,
  root-unit decoder, 2-adic, one-sided repair) at 2026-10-15 18:27-18:42 UTC, complete
  pagination both passes, found no other work on this residue.
Optimistic full cost budget; required observable improvement:
  No kappa/supplier budget in play (missing-lemma work). Required observable: a PROVEN
  lemma whose hypotheses strictly include AN's and MP's and which certifies >= floor(2v/3)
  on instances where either alone is short, or an exact obstruction showing why the mixed
  route fails at the smallest instance where it fails.
Success evidence; falsification test; time/compute cap:
  Success: PASS markers from verify.py (controls, fixture calibration, MX bound vs
  threshold per instance, search summary) and a written proof of Lemma MX in README.md.
  Falsification test: an explicit admissible pairing B with sum_j rank_F2 B[R_j,A_j] <
  floor(2v/3) refutes F-star on that instance (chain is proven); a corrupted witness must
  fail the independent checker. Compute cap: one session, single-process stdlib Python,
  each registered command below 600 s.
Predecessor authors; intended artifact and reproduction command:
  F-star / cert(M) / L8 / the proven chain: research/root-unit-decoder-lemmas (Douglas
  Colkitt with OpenAI Codex assistance lineage). Fixtures tied_min, cex_min_1 and their
  recorded one-copy limits: DreamingOfClouds, PR 2111 / PR 2162. Lemma residue statement
  and engine design this package's engine adapts: Aaron Wang, PR 2717. Census frontier:
  Aaron Wang, PR 2335. Exact cost(tied_min) = 12: Aaron Wang, PR 2379. Exact
  cost(cex_min_1) = 21: Discussion 2202 (author credited in README after verification).
  Artifact: research/fstar-tied-residue-seeddcc97691/. Reproduce:
  python3 -B research/fstar-tied-residue-seeddcc97691/verify.py
  python3 scripts/research_package.py --package research/fstar-tied-residue-seeddcc97691 --check-only
```
