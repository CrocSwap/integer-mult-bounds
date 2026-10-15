# Task card - KB5c: residue class (ii) of F-star, non-3-dichromatic zero digraphs

```text
Task ID / proposed scope key: complex-new-helper-inventory (drawn card, scope changed)
  / fstar-zero-digraph-residue-seede9937f18
  (Kappa-blocker KB5c, authorized explicit open request; chooser OS seed e9937f18f68bb83ac4e780cc2833deb6
   drew track complex-mechanisms with cards complex-new-helper-inventory,
   complex-rank-shape-decoder and p104-side-correction; the draw landed on the
   saturated complex-mechanisms cards, which the assignment names as the recorded
   reason for taking the KB5c request instead.)
Base commit; exact predecessor and dependency heads:
  base main cbda2c010b85d1fb8a66b3b2688ca12d6ca1a040 (priority revision 5; canonical main
  fetched at entry: 63a279f5790872996a13f0e9efdae35818171b48);
  predecessor proofs: https://github.com/CrocSwap/integer-mult-bounds/pull/2717
    head 7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3;
  predecessor residue (i): https://github.com/CrocSwap/integer-mult-bounds/pull/2747
    head 9f725ea012f76aa05924b95891c581106793c069;
  predecessor census: https://github.com/CrocSwap/integer-mult-bounds/pull/2335;
  fixtures: https://github.com/CrocSwap/integer-mult-bounds/pull/2111 (DreamingOfClouds).
Concrete object and question:
  Open problem F-star of research/root-unit-decoder-lemmas section 7 (floor form):
  cert(M) >= floor(2v/3) for every exact 3-total rational decoder M = sum_j p_j q_j^T.
  Residue class attacked: (ii) NON-3-DICHROMATIC ZERO DIGRAPHS - the residue PR 2717
  demoted as "zero digraphs that are not 3-dichromatic (Lemma MP then gives only
  sum_i MAS(Z[C_i]))", left untouched by PR 2747 (class (i) only). Exact question
  (the first open question of PR 2747, which is exactly this class's floor):
  is max over pivot maps c: [v] -> D(t) of sum_i MAS(Z[C_i]) >= floor(2v/3) for every
  rank-3 zero digraph? If yes, Lemma MP proves F-star outright. If no, find the
  smallest decoder where the matched-pivot value drops below floor(2v/3) and decide
  there whether true cert(M) also drops (F-star false) or only the MP route dies.
Scope status: changed (from the drawn complex-mechanisms cards); reason: authorized
  explicit open request KB5c. Pair-collision check before computation (toolkit
  disc-comments --grep on discussions 1317 and 1166 including nested replies,
  2026-10-15 20:05-20:12 UTC) found no live claim on F-star residue (ii) or (iii):
  KB5 (PR 2717) DONE/RELEASED 18:20 UTC, KB5b (residue (i), PR 2747) DONE/RELEASED
  19:50 UTC; agent-64 holds the singleton f(7) L=20 census (KB3b line), untouched here.
Existing restriction being changed (or exact claim being audited):
  Nothing is relaxed. The restriction being addressed is PR 2717's demotion (b):
  "zero digraphs that are not 3-dichromatic (Lemma MP then gives only sum_i MAS(Z[C_i]))"
  and PR 2717's open question 2 (dichromatic numbers of the stored instances' zero
  digraphs). Every new claim carries its exact hypothesis and is labelled
  PROVEN / CHECKED / DEMOTED.
Method; explicit parameter ranges/candidate alphabet:
  Stdlib exact integer/F2 arithmetic. (a) Exact zero-digraph machinery: MAS(Z[S]) for
  all subsets (exact acyclicity DP), exact dichromatic number of Z with and without
  the pivot constraint sets D(t), exact matched-pivot value max_c sum_i MAS(Z[C_i]).
  (b) Calibration on the stored fixtures tied_min (v = 12) and cex_min_1 (v = 19):
  reproduce PR 2717's anchors (tied_min 11/12, cex_min_1 18/19, chain engine 22) and
  PR 2747's anchors (MP/MX 9 and 16), then answer PR 2717's open question 2 on them.
  (c) Smallest-first adversarial search (v ascending from 3) for rank-3 decoders with
  non-3-dichromatic zero digraphs and constrained D(t): entries in {-1,0,1} and
  {-2..2} boxes over p(t), q(t) in Z^3, generators biased to dense mutual-zero
  structure (bidirected triangles/books) and small |D(t)|; exact MP value everywhere,
  exact cert where exhaustive a-enumeration terminates, engine witnesses replayed by
  an independent checker, admissible-B chain cost as the rigorous falsifier criterion.
Nearest overlapping PRs and why this adds something:
  PR 2717 (Aaron Wang) proved SF/MP/RK/AN and named this exact residue; its open
  question 2 (dichromatic numbers of the fixtures' zero digraphs) is computed here.
  PR 2747 (Aaron Wang) closed residue class (i) only and states residue (ii) untouched;
  its open question 1 (the MP floor) is this package's main question. PR 2335
  (Aaron Wang) is the 196-instance census over v = 4..12 entries -2..2; not repeated.
  PR 2111 / PR 2162 (DreamingOfClouds) own the fixtures; cited, not restated.
Optimistic full cost budget; required observable improvement:
  No kappa/supplier budget in play (missing-lemma work). Required observable: either a
  PROVEN lemma with exact hypotheses bounding the matched-pivot value / cert from below
  on the non-3-dichromatic class, or the first explicit instance where the MP value
  falls below floor(2v/3), with the true cert there decided as far as exact methods
  reach and the exact obstruction recorded.
Success evidence; falsification test; time/compute cap:
  Success: PASS markers from verify.py (controls, fixture calibration, dichromatic
  numbers, MP-floor search summary) and written lemma/obstruction text in README.md.
  Falsifier of F-star: an explicit admissible pairing B with
  cost(B) = sum_j rank_F2 B[R_j,A_j] < floor(2v/3), or exact cert < floor(2v/3) where
  exhaustive; a corrupted witness must fail the independent checker. Compute cap:
  one session, single-process stdlib Python, each registered command below 600 s,
  long runs sharded into resumable checkpoints driven by blocking foreground commands.
Predecessor authors; intended artifact and reproduction command:
  F-star / cert(M) / L8 / the proven chain: research/root-unit-decoder-lemmas,
  PR 1590 by DreamingOfClouds (with Claude Opus 5.5 (Anthropic) via Claude Code
  assistance). Fixtures tied_min, cex_min_1, recorded one-copy limits, Lemma SCC/L5:
  DreamingOfClouds, PR 2111 / PR 2162. Lemmas SF/MP/RK/AN, the residue statement and
  the engine design this package adapts: Aaron Wang, PR 2717. Lemma MX and the
  class-(i) closure: Aaron Wang, PR 2747. Census frontier: Aaron Wang, PR 2335.
  Exact cost(tied_min) = 12: Aaron Wang, PR 2379. Exact cost(cex_min_1) = 21:
  Nick Petalas, PR 2206 (each re-verified with gh pr view before citation).
  Artifact: research/fstar-zero-digraph-residue-seede9937f18/. Reproduce:
  python3 -B research/fstar-zero-digraph-residue-seede9937f18/verify.py
  python3 scripts/research_package.py --package research/fstar-zero-digraph-residue-seede9937f18 --check-only
```
