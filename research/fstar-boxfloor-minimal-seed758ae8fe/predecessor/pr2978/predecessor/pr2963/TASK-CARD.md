# TASK-CARD — KB5i (local task card, written before substantial computation)

Task ID / proposed scope key: kappa-blocker KB5i; scope key for the drawn card
  f383d8fc405ee6982cdd (coverage-law-change), overridden to the explicit open
  request; chooser draw seed 42ff061169763106b201a358b527fd93, track
  recursive-interfaces (draw landed on saturated cards: coverage-law-change,
  centre-path-sharing, connector-alphabet-change).
Base commit; exact predecessor and dependency heads: 991c50d1ea8ddb7cf88c1b4a45c7b409c02d38fb
  (current origin/main at entry, 2026-10-16). Predecessors: PR 2936 head
  f0ef06f13e4de3e50c211c880bdc6891c09620a1 (KB5h, open; the recorded
  remainder this task settles), PR 2914 head 3f7781efccdf10fa61a1e0a6f11c191579b21280
  (KB5g, open; engine + sub-anchor box), PR 2901 head c6e0b150081d46abe8bf5d0320de4311cb55fe95,
  PR 2869 head 153b93c1c0e9ee1c50677ae04d48f1f7f0b1700e (merged),
  PR 2747 head a2bab9978c8149dc5965558ea9277da07bc750e7, PR 2717 head 7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3.
Concrete object and question: (1) the family gap gap_named = cert - named on
  the TWELVE open tied_min v = 11 sub-decoders of PR 2936's record, where named
  is scan-only at Lemma MX construction product 1,977,326,743: compute named
  EXACTLY (DP / symmetry-reduced enumeration over the MX construction space)
  and settle the verdict - does gap_named = 2 exist below v = 12 (minimal
  gap-2 instance drops to v = 11) or is the minimal exact gap-2 instance
  exactly tied_min v = 12? Cross-check: cert reproduces PR 2936's stored
  values. (2) Box-completeness under Lemma BPP: the tau >= 1 general case with
  the projection-parity obstruction as filter - prove cert = box-max (which
  with the box floor closes F-star through the PR 2914 chain) or construct /
  search the minimal tau >= 1 decoder with cert > box-max, concentrated where
  PR 2936's sweep was weak (its 12 gap2-open scans and synthetic families).
  (3) Report the matched-pivot floor status honestly (demoted twice).
Scope status: changed; reason - authorized "explicit open request" scope
  change (discussion 1166, the recorded remainder of PR 2936); the drawn
  cards are saturated/other objects.
Existing restriction being changed (or exact claim being audited): PR 2936's
  recorded obstruction "Lemma MX construction product 1,977,326,743 - named is
  a seeded scan (value 9) and gap_named stays in {0,1,2}" and its open
  question 2 (a DP over the Lemma MX construction space); PR 2914 open
  question 1 (box-completeness at tau >= 1).
Method; explicit parameter ranges/candidate alphabet: exact stdlib integer/F2
  arithmetic on the byte-exact vendored PR 2914 engine. Exact named = max(MP,
  |S_gamma|, MX, CL3) computed by (a) a coarse-assignment DP/DFS over the MX
  per-line options (A / U(a*) / T(c)) with per-line feasibility sets for the
  repair labels, matching mx_eval semantics bit-for-bit (property-tested
  against brute-force product enumeration where the product fits), and (b) the
  CL3 = MP identity at even tau (machine-checked). Domain: exactly the 12
  tied_min v = 11 sub-decoders (labels recorded in PR 2936's
  receipt-tied_min-s11-deep.json); smallest instance first. Box-completeness:
  Lemma BPP parity filter on witness space; synthetic tau >= 1 families
  biased to fixture-density zeros and hard (cert < v) instances.
Nearest overlapping PRs and why this adds something: PR 2936 (the direct
  predecessor; this settles exactly its recorded remainder), PR 2914 (engine,
  box), PR 2901/2747/2717/2869/2890/2774 (lineage). No other work on the 12
  sub-decoders exists at entry (pair-collision check 2026-10-16 12:40-12:43
  UTC on discussions 1317 + 1166 with nested replies; overlap survey
  12:41 UTC complete pagination).
Declared milestone: local module / scoped audit (no kappa, no supplier, no
  frontier change).
Optimistic full cost budget; required observable improvement: no kappa budget
  in play; the price is one bounded deterministic stdlib registered replay
  plus a bounded exact-named run over 12 records (coarse space 3^11 per
  record) and one bounded box-completeness search.
Unresolved consumer/restoration costs; family expansion decision if
  continuing: none (missing-lemma/audit work).
Success evidence; falsification test; time/compute cap: PASS markers from
  verify.py (registered replay reproducing PASS_FG_CALIBRATION
  tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 reach=0/12,8/19 and PR
  2936's census/deep/box-attack lines and PR 2914's 21 exact records gap 0)
  plus exact named values with replayed construction witnesses on all 12
  sub-decoders. Falsification: a named construction witness whose replay value
  differs from the DP optimum refutes the solver; a certified instance with
  cert - named = 2 at v = 11 answers the verdict YES. One bounded pivot
  maximum; early kill with the exact obstruction recorded; registered replay
  under 600 s; heavy runs sharded with receipts.
Predecessor authors; intended artifact and reproduction command: see
  TASK.json predecessor_authors (verified with gh pr view --json author,title
  at writing). Artifact research/fstar-gap2-v11-seed42ff0611/; reproduce with
  python3 -B research/fstar-gap2-v11-seed42ff0611/verify.py then python3
  scripts/research_package.py --package research/fstar-gap2-v11-seed42ff0611 --check-only.
