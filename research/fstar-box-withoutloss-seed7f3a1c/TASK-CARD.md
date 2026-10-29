# Local task card (KB5j) — written before substantial computation

```text
Task ID / proposed scope key: KB5j / fstar-box-withoutloss (scope key of the drawn
  card bit-new-register-model: 7084092dd726e7ba1f2f; scope CHANGED, see below)
Base commit; exact predecessor and dependency heads:
  base 0614abaef427f123d9b844f85a759e64ee3ab29c (origin/main at worktree creation,
  2026-10-16); predecessors PR 2963 head ee755e682b3b30d493e764d3be50003b13b69b4a,
  PR 2936 head f0ef06f13e4de3e50c211c880bdc6891c09620a1, PR 2914 head
  3f7781efccdf10fa61a1e0a6f11c191579b21280 (vendored byte-exact, pins asserted).
Concrete object and question:
  Open problem F-star (research/root-unit-decoder-lemmas section 7, PR 1590):
  cert(M) >= floor(2v/3) for exact 3-total rational decoders. Object here is the
  LAST named blocker of the family-gap line (PR 2963's exact statement):
  Lemma BPP's WITHOUT-LOSS QUESTION at tau >= 1 - may one assume, without loss,
  that an attaining L8 witness satisfies Lemma BPP conditions (i)+(ii) (odd tied
  overlap per kept line, even off-anchor shared parity on forward zero arcs),
  i.e. is box(M) = cert(M) for every exact 3-total decoder with tau(t) >= 1
  everywhere (box-completeness)?
Scope status: changed; reason for refinement or change:
  Authorized "explicit open request" scope change (assignment records this reason):
  the drawn cards (bit-new-register-model / bit-helper-contract, chooser seed
  0194e0b2ffbe43b4e67165afcf5ee6cd, track bit-mechanisms) are not this object;
  discussion 1166 carries the explicit open request "Lemma BPP's without-loss
  question remains the exact blocker" (PR 2963 body), which this assignment takes.
Existing restriction being changed (or exact claim being audited):
  Audit/settle PR 2914 open question 1 + PR 2936 open question 1 as narrowed by
  PR 2963: box-completeness for tau >= 1 (Lemma SB (iii) PROVEN excludes tau = 0).
Method; explicit parameter ranges/candidate alphabet:
  (1) Classify the escape mechanism of PR 2963's 21 escaping witnesses (v = 3..5
  fixture sub-decoders) exactly; (2) prove or refute the line-by-line re-pairing
  (repair) lemma - smallest instance first: v = 2 (case analysis on anchor data),
  then v = 3 exhaustive label-space checks and a smallest-first decoder search
  (exact cert vs exact box, both sides certified by replayed witnesses or exact
  enumeration; int-only arithmetic); (3) if neither falls, isolate the precise
  parity condition that blocks repair with a minimal demo.
Nearest overlapping PRs and why this adds something:
  PR 2914 (box, Lemmas SB/LB), PR 2936 (Lemma BPP, tau >= 1 necessary, v = 7..11
  census), PR 2963 (tied_min v = 11 exact, box weak cell closed, BPP strictness
  at tau = 0). None settles the without-loss question; this is its named blocker.
Declared milestone: local module (scoped lemma/obstruction package; no kappa).
Optimistic full cost budget; required observable improvement:
  No kappa claim; milestone is a PROVEN lemma, a minimal counterexample, or an
  exact isolated obstruction. Compute cap: about 25 minutes of heavy search in
  blocking chunks with receipts; exactness over speed (never scan-and-trust).
Unresolved consumer/restoration costs; family expansion decision if continuing:
  Not applicable at this milestone; F-star closure remains conditional on the
  chain cost >= cert and the box floor (PR 2914), whose hypotheses must be
  re-verified link by link if box-completeness falls.
Success evidence; falsification test; time/compute cap:
  Success: (a) PROVEN box-completeness at tau >= 1 (written proof + machine
  checks), or (b) minimal tau >= 1 decoder with cert > box-max, both sides exact
  with replayed witnesses, or (c) exact obstruction to the repair/projection
  lemma with a minimal demo and one stated condition. Falsification test of any
  proof: smallest v = 2/v = 3 instances enumerated from the definition; corrupted
  witness rejection controls. Time cap: one bounded pivot maximum.
Predecessor authors; intended artifact and reproduction command:
  PR 1590 DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code
  assistance); PR 2111 DreamingOfClouds; PR 2717/2747/2774/2869/2890/2901/2914/
  2936/2963 Aaron Wang (navinor) - all verified with gh pr view --json author,title
  at current ground truth. Artifact: research/fstar-box-withoutloss-seed7f3a1c/
  with verify.py (python3 -B verify.py).
```

Entry checks recorded: chooser draw (seed `0194e0b2ffbe43b4e67165afcf5ee6cd`,
track `bit-mechanisms`, cards `bit-new-register-model` / `bit-helper-contract`) —
saturated for this object, the recorded reason for taking the assigned explicit
open request. Pair-collision checks (toolkit `disc-comments --grep`, discussions
1317 + 1166, nested replies) at entry found no live claim on this object; the
last family-gap activity is KB5i's FINDING/DONE/RELEASED (PR 2963, 2026-10-16
14:36:56 UTC), which this assignment extends. Entry overlap survey
(`find_overlap.py`, object proper names and synonyms, `--refresh`, complete
pagination: 240 open PRs, 1660 discussion records, 14:44-14:45 UTC) found only
the known F-star lineage and unrelated traffic. Recorded anchors reproduced from
pristine predecessor copies before computation (`PASS_FG_CALIBRATION
tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 reach=0/12,8/19`;
`PASS_KB5I_NAMED records=12 named-exact=12 named=9x12 gap2-proven=12`;
`PASS_KB5I_BOXREPLAY in-box=12/12`; `PASS_BOX_SEARCH bpp-strict-tau0=yes
bpp-strict-tau1=no tau-ge1=60 hard=0 box-violations=0`; PR 2936 tau = 0 demo
cert = 2 > box = 1 asserted value-by-value).
