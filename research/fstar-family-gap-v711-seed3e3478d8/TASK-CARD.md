# Task card - KB5h: the remaining search space of F-star's family gap

```text
Task ID / proposed scope key: kappa-blocker KB5h (explicit open request from
  discussion 1166); drawn card was supplier-boundary-audit (chooser seed
  3e3478d8db3f113c6d56f586419795de, track adversarial-audit) - scope
  changed, reason recorded in TASK.json.
Base commit; exact predecessor and dependency heads:
  base 5a0dc2c0f4685b02bef7776bc196c7c1231cbac1 (current origin/main at
  entry, fetched and pinned 2026-10-16 10:45 UTC, unchanged at the
  pre-computation refresh); predecessor engine extracted byte-exactly from
  PR 2914 head 3f7781efccdf10fa61a1e0a6f11c191579b21280 with the shared
  toolkit pr-tree-extract (SHA-256 pins in predecessor/PREDECESSOR-PINS.json,
  verified at every replay).
Concrete object and question: the EXACT REMAINING SEARCH SPACE of open
  problem F-star's family-gap question as recorded by PR 2914 (agent-72):
  (1) enumerate v = 7..11 (the recorded unenumerated range) with the
  falsifier criterion armed, looking for the FIRST gap-2-or-more instance
  below v = 12 and any threshold counterexample; (2) attack box-completeness
  (cert = box-max for tau >= 1 at general v): prove it or find the minimal
  instance where cert > box-max; (3) report the matched-pivot floor status
  honestly (PR 2914 DEMOTED route (a): MP is strictly weaker than cert on the
  fixtures, 9<11, 16<18).
Scope status: changed (authorized explicit open request; the chooser draw
  landed on the adversarial-audit cards supplier-boundary-audit /
  selected-stock-envelope / uniform-transfer-audit, none of which is this
  object).
Existing restriction being changed (or exact claim being audited): PR 2914's
  recorded remaining gap ('prove the sub-anchor box complete ... or prove the
  matched-pivot floor ... both remain OPEN here') and its recorded compute
  obstruction ('sizes v = 7..11 of both fixtures ... were not enumerated
  (compute cap)').
Method; explicit parameter ranges/candidate alphabet: exact stdlib
  integer/F2 arithmetic on the vendored PR 2914 engine. Smallest instance
  first: sub-decoders M[S,S] of both canonical fixtures at v = 7..11
  (complete at tied_min v = 9..11; deterministic strides recorded per cell),
  cheap rungs on every record (exhaustive MP at v <= 11, named_lo, threshold
  and falsifier screens, seeded bounded witness hill-climbs with independent
  replay), deep rungs on 113 flagged/potential records (exact named via
  exhaustive Lemma MX + CL3 construction spaces with a raised 3M cap; exact
  cert/box by exhaustive a-enumeration where products allow; ceiling
  exactness via replayed size-v witnesses), a named-settlement pass on every
  scan record whose product fits 3M (the one bounded pivot), the
  box-completeness attack (explicit tau = 0 v = 2 demonstration, Lemma BPP
  projection parity, 126-instance synthetic sweep with exact cert vs exact
  box), and a registered replay verify.py (58.5 s observed).
Nearest overlapping PRs and why this adds something: PR 2914 (Aaron Wang -
  the sub-anchor box, Lemmas SB/LB, the v = 3..6 census, the recorded
  remaining gap; its engine is vendored byte-exactly and credited); PR 2901
  (Aaron Wang - family-gap definition and record); PR 2747 (Aaron Wang -
  Lemma MX, exhaustive MP/MX values); PR 2717 (Aaron Wang - Lemmas
  SF/MP/RK/AN and the exact-completion engine); PR 2869 (Aaron Wang -
  SC/SG); PR 2774 / PR 2890 (Aaron Wang - other residue classes); PR 2111
  (DreamingOfClouds - fixtures and the recorded certificate limits 11/18);
  PR 1590 (DreamingOfClouds - F-star, cert(M), the proven chain). No other
  work on this object existed at entry or at the pre-computation overlap
  re-run (2026-10-16 10:45 and 11:21 UTC, complete pagination).
Declared milestone: local module / scoped obstruction (labelled lemma and
  precisely scoped census verdicts; no kappa, no supplier).
Optimistic full cost budget; required observable improvement: no kappa or
  supplier budget in play; one bounded deterministic registered stdlib run
  below 600 s plus sharded resumable checkpoint runs with receipts; required
  observable: either box-completeness proved (plus its floor), or the exact
  remaining search space recorded with the minimal gap-2-or-more instance
  and the box status pinned.
Unresolved consumer/restoration costs; family expansion decision if
  continuing: none (missing-lemma/audit work, no construction round).
Success evidence; falsification test; time/compute cap: PASS markers from
  verify.py plus README analysis labelled PROVEN / CHECKED / DEMOTED;
  falsification test = exact cert < floor(2v/3) where exhaustive, or an
  explicit admissible B with chain cost below threshold; for
  box-completeness any cert > box-max instance on tau >= 1 lines; corrupted
  witnesses must fail the independent replay checker. Stop at the first
  falsifier or confirmed box counterexample with the exact obstruction
  recorded, else at the declared domain with the exact residual recorded.
  One bounded pivot maximum. Compute cap: one session, single-process stdlib
  Python, registered verify below 600 s; heavy runs sharded into resumable
  checkpoint jobs with periodic receipts.
Predecessor authors; intended artifact and reproduction command: see
  SOURCES.json / TASK.json predecessor_authors; artifact
  research/fstar-family-gap-v711-seed3e3478d8/; reproduce with
  python3 -B research/fstar-family-gap-v711-seed3e3478d8/verify.py then
  python3 scripts/research_package.py --package
  research/fstar-family-gap-v711-seed3e3478d8 --check-only.
```

Pair-collision check at entry (before computation): toolkit
`disc-comments --grep` on discussions 1317 and 1166 including nested replies,
2026-10-16 10:45-10:47 UTC, and the refined pre-computation re-run 11:21 UTC
with the object's proper names ("box-completeness", "sub-anchor box",
"family gap", "named certificate", "form_r", "cert", "matched pivot",
"F-star", "3-total decoder"). No live claim on this object; the only F-star
family activity in the last hours is KB5g's FINDING/DONE/RELEASED (PR 2914,
2026-10-16 10:40:51 UTC), which this assignment explicitly extends.

Entry overlap survey: `scripts/find_overlap.py` with explicit object terms
and synonyms, `--refresh`, complete pagination (494 then 496 open PRs, 1588
then 1597 discussions, 2026-10-16 10:45 and 11:21 UTC): only the known
F-star lineage (PRs 2717/2747/2774/2869/2890/2901/2914, the entry-class
package `research/fstar-entry-class-scope-seed63d5f999`, the 196-instance
census `research/fstar-cert-census-seed298df375`) and unrelated board
traffic.
