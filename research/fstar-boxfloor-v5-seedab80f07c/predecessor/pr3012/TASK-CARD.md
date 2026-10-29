# Local task card (KB5k) - written before substantial computation

```text
Task ID / proposed scope key: KB5k box-floor / fstar-boxfloor-minimal-seed758ae8fe
  (chooser seed 758ae8fe94f704eed3a4bb471ba333b5, track verifier-engineering,
  drawn cards portable-replay / replay-runtime; explicit-open-request scope change)
Base commit; exact predecessor and dependency heads:
  base 066f57ff795dbe6d0a0ecc11fe742eadcec00c39 (origin/main at worktree creation);
  predecessor PR 2978 head 12eb7b832de9239a314a7cddf6c6033d618cd8f2 (agent-78,
  vendored tree + engine lineage: PR 2963 ee755e682, PR 2936 f0ef06f13,
  PR 2914 3f7781efc); frozen source pins untouched.
Concrete object and question:
  Object: the sub-anchor box value box(M) of exact 3-total rational decoders
  M = sum_{j<=3} p_j q_j^T on v lines (M_tt != 0).
  Question (a): does box(M) >= floor(2v/3) hold for ALL such decoders (the
  surviving box-floor link of the PR 2914/2978 chain)? If not: the minimal
  decoder with box < floor(2v/3), exact both sides, cert reported alongside.
  Then (one bounded pivot): the tau >= 1 restriction of the same floor
  (PR 2978's stated surviving domain), and the structural control of box by
  the tau pattern, the shareable count r_box = |{j : c_j = gamma}| and tied
  totals (the shareable-class vocabulary of PR 2978 Lemma RT).
Scope status: changed (authorized explicit open request from discussion 1166);
  reason: the recorded remainder of PR 2978 (agent-78) - the box-floor route
  plus shareable-class completeness - was assigned to this session; the drawn
  verifier-engineering cards do not match this object.
Existing restriction being changed (or exact claim being audited):
  Audits PR 2978's stated surviving chain link "box >= floor(2v/3) would close
  F-star" as a claim about ALL exact 3-total rational decoders (its own
  counterexample has box = 2 = floor(2v/3) at v = 3, so it did not test the
  floor); and PR 2936's tau >= 1 necessity pin (its tau = 0 demo is v = 2,
  box = 1 = floor(2v/3), also not a floor falsifier).
Method; explicit parameter ranges/candidate alphabet:
  (1) Smallest falsifying instance first: construct exact integer decoders at
  v = 2, 3 with prescribed tau patterns; exact cert/box by the vendored PR 2914
  engine AND an independent section-7/box definition enumeration; int-only.
  (2) Exhaustive combinatorial box census at v = 3 over all Lemma-SG-consistent
  (a0, b0, Z) patterns INCLUDING lines with tau = 0 (PR 2978 job B restricted
  to tau >= 1 per line); box exact per config; min box per tau-pattern class.
  (3) Written lower-bound lemmas (two-line repair; tied-bit matched pivot) and
  their machine checks; then the tau >= 1 pivot at v = 5 (floor 3): bounded
  search for box <= 2 with exact obstruction records per route.
Nearest overlapping PRs and why this adds something:
  PR 2914 (sub-anchor box, Lemmas SB/LB), PR 2936 (Lemma BPP, tau >= 1 needed
  for box = cert), PR 2963 (tied_min v = 11, box weak cell), PR 2978 (Lemma V2,
  Lemma RT + shareable totals, minimal box = cert counterexample v = 3).
  None tests the box FLOOR against decoders with tau = 0 lines, and none states
  a box lower bound in terms of the tau pattern; this package does both.
Declared milestone: local module (scoped obstruction / exact falsifier + exact
  structural bounds; no kappa, no supplier).
Optimistic full cost budget; required observable improvement:
  No kappa claim; the deliverable is the settled floor question. Compute cap:
  combinatorial v = 3 census (seconds), realization and v = 5 pivot bounded
  (minutes), every number replayed exactly.
Unresolved consumer/restoration costs; family expansion decision if continuing:
  Not applicable (no physical construction). Family expansion: none; the
  shareable-class completeness question (PR 2978's 21 patterns) stays open and
  is recorded as the next question unless resolved incidentally.
Success evidence; falsification test; time/compute cap:
  Success: exact minimal falsifier (both sides replayed + independent
  enumeration) or a proof of the floor; every claim labelled PROVEN/CHECKED/
  DEMOTED. Falsification: replay stored witnesses; re-enumerate cert and box
  from the definitions; any v = 3 config with a different exact box refutes the
  census. Cap: registered replay under 600 s; one bounded pivot maximum.
Predecessor authors; intended artifact and reproduction command:
  PR 1590 DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code
  assistance); PR 2111 DreamingOfClouds; PRs 2717/2747/2774/2869/2890/2901/
  2914/2936/2963/2978 Aaron Wang (navinor) - verify each at current ground
  truth before writing. Artifact: research/fstar-boxfloor-minimal-seed758ae8fe/
  with verify.py (python3 -B research/fstar-boxfloor-minimal-seed758ae8fe/verify.py).
```
