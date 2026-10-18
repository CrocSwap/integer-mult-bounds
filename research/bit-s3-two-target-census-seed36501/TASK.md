# Cycle J task card: all two-target maps in the S3 transposition model

- Track: `bit-mechanisms`.
- Accepted OS seed: `36501a8544a63b2f0ecd2e6452836c79`.
- Catalogue card: `bit-new-register-model`, scope key `7084092dd726e7ba1f2f`; priority revision 3, catalogue SHA-256 `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`.
- Exact base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Refined scope key: `7084092dd726e7ba1f2f/S3-transposition-two-target-census/r2/all-36/radius-five`.
- Claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18923720.

## Question and changed premise

For every ordered pair `g,h` in `S3`, what is the minimum number of paid calls
to realize the exact dirty-register map `diag([g],[h])` in `F2[S3]`, using only
the transposition labels `x=(12)` and `y=(23)`? Each call is
`I + ([s]+[1])N`, with `N` a rank-one idempotent over `F2`. The direct bill is
the sum of the two shortest `x,y` word lengths.

Scope status: refined from the catalogue's permitted nonabelian-family
variation. The first bounded target, `diag([xy],[yx])`, had no saving. One
evidence-driven pivot widened that same finite object to its 36 ordered target
pairs, to determine whether the obstruction was target-specific. No further
parameter expansion is in scope.

## Method, full cost and domain

There are six rank-one idempotents in `M2(F2)`, hence twelve paid generators.
The largest separate direct bill is six calls (`xyx` on each register). An
exact breadth-first search enumerates the entire radius-five ball. That is
enough to certify every possible strict saving: all target-pair direct bills
are at most six, so any cheaper word would have length at most five. Direct
words give the exact upper bounds; the search gives each matching lower bound.

Count every paid factor. Free scalar `GL2(F2)` basis changes are included by
normalizing them into arbitrary rank-one idempotents and using augmentation to
force the residual scalar map to identity. Both endpoint registers are
arbitrary dirty data. No extra register, COPY, erasure, clean state, or free
address operation is in the alphabet.

This changes the retained additive rational-frame address group to finite
nonabelian `S3`. There is no established physical supplier implementation, so
the result is a scoped alternative-model bound, not a selected-profile or
`kappa` change.

## Overlap, predecessors and stopping rule

Final pre-submission overlap refresh at 2026-10-14 12:33:47 UTC found no exact
S3 two-target transposition census among 527 completely paginated open PRs and
506 Discussion records, and no matching local task/readme/ledger entry. Nearby distinct work:
PR #1822 uses `Q8` central-commutator pairs; PR #1716 uses a restricted `AGL2`
triple; Discussions #1759 and #1818 use `UT4` and `D16`; PRs #1478/#1573/#1742
and overlap handoff #1792 already address the D8 third-register question.
These differ in group, paid alphabet or target family. Discussion #1167's
recent claims were in other tracks or different objects.

Predecessor: `research/bit-dihedral-commutator/README.md` is pinned as a
provenance input in `SOURCES.json`; it studies a D8 central target, while this
result changes both the group and the target family. No predecessor code is
imported.

Stop after all 36 minima equal their separate direct bills. Do not expand to
more registers, other groups or other paid labels in this cycle.

## Evidence and deliverable

The exact radius-five ball has layers `[1,12,80,466,2345,10760]` and 13,664
distinct products. The 36 pair minima have histogram `{0:1,1:4,2:8,3:10,4:8,5:4,6:1}`,
identical to the separate direct bills. All 36 direct words replay exactly;
the maximum-cost pair `(xyx,xyx)` is absent through length five and has its
six-call direct word. The verifier also checks all 1,885 ordered words through
length three against an independent formal-product implementation, replays all
13,664 canonical paths formally, and rejects each of 108 single-factor
omissions from the direct words.

Deliverable: source-pinned local package and exact certificate. No `kappa` or
supplier adoption is claimed. Prepared with substantial OpenAI Codex assistance.
