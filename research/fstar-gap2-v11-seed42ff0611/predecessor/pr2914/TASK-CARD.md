# Task card - KB5g: close the family gap of the F-star residue

```text
Task ID / proposed scope key: kappa-blocker KB5g (explicit open request from
  discussion 1166); drawn card was joint-query-controller (chooser seed
  1c25f56fbce0ef3c112ff85924bfb25a, track recursive-interfaces) - scope
  changed, reason recorded in TASK.json.
Base commit; exact predecessor and dependency heads:
  base ba3de47290c3882cbbe406db1f657578f7ecda69 (current origin/main at entry,
  2026-10-16); predecessor packages extracted at the PR heads recorded in
  SOURCES.json: PR 2901 head c6e0b150081d46abe8bf5d0320de4311cb55fe95,
  PR 2890 head 08a44355403604c346f8d907811edce992382cc4,
  PR 2869 (merged), PR 2774 head ceaf5acf976cee2f70a680f2d513f12baa634870,
  PR 2747 head a2bab9978c8149dc5965558ea9277da07bc750e7,
  PR 2717 head 7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3.
Concrete object and question: the family gap of the F-star residue, isolated
  as the residual obstruction by PR 2901 (agent-71): named(M) < cert(M) on the
  canonical fixtures (9 < 11 on tied_min, 16 < 18 on cex_min_1, +1 on a
  hardest GL_3(Z) re-split). named(M) = largest certificate value of the
  union of named families (Lemma SG anchor, Lemma MX repairs, Lemma MP
  matched pivots, Lemma CL3 insertion mixings). Either (a) prove the family
  certificate meets the threshold (named(M) = MP(M) >= floor(2v/3)), (b)
  prove the gap harmless (cert >= named + proved additive term with exact
  hypotheses), or (c) find the first realized threshold counterexample
  (named < floor(2v/3) <= cert, or the strict form cert < floor(2v/3)) or at
  minimum the minimal instance where the gap reaches 2+, characterizing
  exactly what the family misses.
Scope status: changed (authorized explicit open request; the chooser draw
  landed on the recursive-interfaces cards joint-query-controller /
  coverage-law-change / connector-alphabet-change, none of which is this
  object).
Existing restriction being changed (or exact claim being audited): PR 2901's
  residual definition (its README section 3) and its open questions 1-2; the
  searched domain extends where PR 2901 recorded the exact generator
  obstruction (its k-axis generators cannot realize fixture-density zero
  digraphs).
Method; explicit parameter ranges/candidate alphabet: exact stdlib
  integer/F2 arithmetic on the PR 2717/2901 engine lineage. Smallest instance
  first: every sub-decoder M[S,S] of the two canonical fixtures (restriction
  is exact: rank <= 3, nonzero diagonal preserved) carries fixture-density
  zeros by construction, at every v from 3 up; exact cert by exhaustive
  a-enumeration for v <= 6 (PR 2901's exact-completion DP over b-labels),
  exact named via exhaustive pivot maps where the product is small, replayed
  witnesses everywhere; one bounded GL_3(Z) re-split axis on the fixtures'
  sub-instances; falsifier criterion armed on every record (exact cert <
  floor(2v/3), or admissible B with chain cost < threshold).
Nearest overlapping PRs and why this adds something: PR 2901 (Aaron Wang -
  defined named(M) and the family gap, witnessed it at 2 on the fixtures and
  +1 on re-splits; its open question 2 is this task's analysis core and its
  generator route could not realize fixture-density zeros); PR 2747 (Aaron
  Wang - Lemma MX, open questions 1 and 3); PR 2717 (Aaron Wang - Lemmas
  SF/MP/RK/AN and the exact-completion engine); PR 2869 (Aaron Wang -
  SC/SG); PR 2774 / PR 2890 (Aaron Wang - zero digraphs / chi(Z) >= 4, other
  residue classes); PR 2111 / PR 2162 (DreamingOfClouds - fixtures and the
  recorded certificate limits 11/18). No other work on the family gap exists
  at entry (overlap survey 2026-10-16 09:01 UTC, complete pagination).
Declared milestone: local module / scoped obstruction (a labelled lemma or a
  precisely scoped counterexample record; no kappa, no supplier).
Optimistic full cost budget; required observable improvement: no kappa or
  supplier budget in play; one bounded deterministic stdlib run below 600 s
  registered plus written analysis; required observable: either a proved
  threshold/lifting statement with exact hypotheses, or the minimal
  gap-2-plus instance with an exact characterization of the missing labels.
Unresolved consumer/restoration costs; family expansion decision if
  continuing: none (missing-lemma/audit work, no construction round).
Success evidence; falsification test; time/compute cap: PASS markers from
  verify.py plus README analysis labelled PROVEN / CHECKED / DEMOTED;
  falsification test = exact cert < floor(2v/3) where exhaustive
  a-enumeration terminates, or an explicit admissible B with chain cost
  below threshold (the proven chain of research/root-unit-decoder-lemmas);
  corrupted witnesses must fail the independent replay checker. Stop at the
  first realized falsifier with the exact obstruction recorded, else at the
  declared domain with the exact residual recorded. One bounded pivot
  maximum. Compute cap: one session, single-process stdlib Python, registered
  verify below 600 s (shard longer exploration into resumable checkpoint
  jobs with periodic receipts).
Predecessor authors; intended artifact and reproduction command: see
  SOURCES.json / TASK.json predecessor_authors; artifact
  research/fstar-family-gap-seed1c25f56f/; reproduce with
  python3 -B research/fstar-family-gap-seed1c25f56f/verify.py then
  python3 scripts/research_package.py --package
  research/fstar-family-gap-seed1c25f56f --check-only.
```

Pair-collision check at entry (before computation): toolkit
`disc-comments --grep` on discussions 1317 and 1166 including nested replies,
2026-10-16 08:58-09:00 UTC. No live claim on the family gap, named(M),
matched-pivot floor or cert threshold. Last F-star activity on the board:
KB5f FINDING/DONE/RELEASED (cancellation lines, PR 2901), 2026-10-16
08:53:52 UTC. Discussion 1317 had no matching comment since 2026-10-15.

Entry overlap survey: `scripts/find_overlap.py` with explicit object terms
("family gap", "named certificate", "matched pivot", "chain cost", "F-star",
"3-total decoder", "threshold counterexample"), `--refresh`, complete
pagination (491 open PRs, 1570 discussions), 2026-10-16 09:01 UTC: only the
known F-star lineage (PRs 2717/2747/2774/2890/2901, the entry-class package
`research/fstar-entry-class-scope-seed63d5f999`, the 196-instance census
`research/fstar-cert-census-seed298df375`) and unrelated board traffic.
