# TASK CARD — KB5d: the statement of F-star residue class (iii) "non-dyadic entries"

```text
Task ID / proposed scope key: KB5d (explicit open request; scope change recorded
  in TASK.json) — scope key of the drawn card p104-side-correction
  (c5367b1a1b7bed20db53) retained in TASK.json as the drawn card, with the
  change reason recorded.
Base commit; exact predecessor and dependency heads:
  base 544a7e82810e30cab61c297cb2e2ea86127fe944 (frozen assignment pin);
  predecessors PR 2717 head 7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3
  (re-checked at writing; moved from the 10644c90 head recorded in its DONE
  comment), PR 2747 head a2bab9978c8149dc5965558ea9277da07bc750e7,
  PR 2774 head ceaf5acf976cee2f70a680f2d513f12baa634870 (all three OPEN PRs
  by Aaron Wang at entry 23:25 UTC 2026-10-15; re-checked before submission).
Concrete object and question:
  Open problem F-star of research/root-unit-decoder-lemmas section 7 (merged,
  PR 1590): cert(M) >= floor(2v/3) for every exact 3-total rational decoder
  M = sum_{j<=3} p_j q_j^T. PR 2717 proved Lemma AN (mod-2 anchor,
  cert(M) >= #{t : M_tt odd} under a 2-integral factorization) and named a
  three-part residue; PR 2747 closed class (i) (tied-minimum/isotropic) on the
  fixtures with Lemma MX; PR 2774 handled class (ii) (non-3-dichromatic zero
  digraphs) and recorded class (iii) "non-dyadic entries" as mathematically
  murky. Question: what is the precise scope of Lemma AN/MX with respect to
  entry denominators (entries in Z[1/2] vs odd-denominator Z_(2) vs general
  Q)? Either collapse residue (iii) — prove the existing lemmas cover all
  exact 3-total rational entry classes up to the remaining gap and merge/rename
  the classification — or isolate the TRUE residual obstruction with a precise
  definition and settle it on tied_min / cex_min_1 and a small falsifier search.
Scope status: changed (authorized explicit open request, KB5d); reason for
  change: the assignment names this open request; the chooser draw
  (seed 63d5f999cdfe9e1cd9ddf8083f34a9a8) landed on saturated cards
  (p104-side-correction, complex-rank-shape-decoder, complex-new-helper-inventory).
Existing restriction being changed (or exact claim being audited):
  PR 2717's demoted residue item (c): "for non-dyadic entries (odd primes in
  denominators) the mod-2 anchor does not apply at all" — audited, plus the
  exact scope of Lemma AN's hypothesis ("after per-total powers of two the
  factorization is 2-integral") and Lemma MX's anchor premise.
Method; explicit parameter ranges/candidate alphabet:
  Exact stdlib rational (fractions.Fraction) and F2 arithmetic. (P1) State and
  prove the exact per-total 2-adic content criterion for Lemma AN's
  normalization hypothesis (Lemma SC), a scale-invariant anchor (Lemma SG),
  and the entry-class invariance of (pi, sigma, Z), cert and the chain cost
  (the collapse). (P2) Settle on the canonical fixtures tied_min (v = 12) and
  cex_min_1 (v = 19): entry classes, contents c_j, gamma = min_j c_j, anchor
  reach {t : v_2(M_tt) = gamma}, mixed anchor+pivot Lemma-MX values, with the
  recorded calibration anchors reproduced (PR 2717: tied_min 11/12,
  cex_min_1 18/19, chain 22; PR 2747: MP/MX 9 and 16; PR 2774: chi(Z) = 3
  unconstrained, non-3-dichromatic under D(t)). (P3) smallest-first bounded
  falsifier search over entry classes with even denominators (totals with
  negative 2-content), odd denominators (2-integral non-integer) and mixed
  general-Q entries, v = 3..10, deterministic seeds, exact cert where
  exhaustive a-enumeration terminates, engine witnesses elsewhere, admissible-B
  chain cost as falsifier criterion, early kill at the first falsifier.
Nearest overlapping PRs and why this adds something:
  PR 2717 (Aaron Wang: Lemmas SF/MP/RK/AN and the residue statement; its
  demoted item (c) is the object audited here), PR 2747 (Aaron Wang: Lemma MX,
  class (i) closure), PR 2774 (Aaron Wang: class (ii); records (iii) as
  murky), PR 2335 (Aaron Wang: falsifier census), PR 2111/2162
  (DreamingOfClouds: fixtures, recorded certificate limits), PR 1590
  (DreamingOfClouds: F-star itself). PR 2613 (thakrarsagar) is a same-motif,
  different-object neighbor (a mod-2 2-integral rank floor for a bit register
  model); it does not state the entry-class scope of Lemma AN/MX.
Declared milestone: audit / scoped proof (no kappa, no supplier, no frontier).
Optimistic full cost budget; required observable improvement:
  No kappa or supplier budget in play; the evidence is the written proofs plus
  one bounded stdlib replay below 600 s.
Unresolved consumer/restoration costs; family expansion decision if continuing:
  None (missing-lemma work); no expansion decision needed.
Success evidence; falsification test; time/compute cap:
  PASS markers from verify.py plus README proofs; falsification = an explicit
  admissible pairing B with chain cost below floor(2v/3) (proven chain
  cost >= cert(M)) or exact cert below threshold where exhaustive; corrupted
  witnesses must fail the independent checker; one session, single-process
  stdlib Python 3.12, registered verify below 600 s.
Predecessor authors; intended artifact and reproduction command:
  F-star and cert(M): DreamingOfClouds, PR 1590 (with Claude Opus 5.5
  (Anthropic) via Claude Code assistance). Fixtures and recorded limits:
  DreamingOfClouds, PR 2111 and PR 2162. Lemmas SF/MP/RK/AN, the residue
  statement, the exact-completion engine design: Aaron Wang, PR 2717.
  Lemma MX: Aaron Wang, PR 2747. Class (ii) machinery: Aaron Wang, PR 2774.
  Artifact: research/fstar-entry-class-scope-seed63d5f999/; reproduce with
  python3 -B research/fstar-entry-class-scope-seed63d5f999/verify.py then
  python3.12 scripts/research_package.py --package
  research/fstar-entry-class-scope-seed63d5f999.
```

Pair-collision check before computation (toolkit `disc-comments --grep`,
discussions 1317 and 1166, nested replies included, 2026-10-15 23:24-23:26
UTC): no live claim on residue class (iii) or the entry-class question.
Bounded overlap survey (scripts/find_overlap.py, explicit terms "F-star",
"cert(M)", "3-total decoder", "dyadic", "2-integral", "odd denominator",
"residue class", "non-dyadic", "Lemma AN", "Lemma MX", --refresh,
2026-10-15 23:25-23:27 UTC, complete pagination: 722 open PRs, 1463
discussion records): only the known predecessors and unrelated dyadic
packages; nearest neighbor PR 2613 (different object). A refined re-run is
required before submission.
