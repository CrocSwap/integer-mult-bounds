# Complex supplier claim — seed 29

- OS assignment draw: `secrets.randbelow(100)` returned **29** (complex supplier).
- Exact refreshed main base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Started 2026-10-13 04:25 PDT; planned finish by 05:25 PDT, with final 15 minutes reserved for verification and handoff.
- Object: selected PR799 X4 zero-frame compensation panel, from the committed maintainer replay archive. Do not change upstream or the selected frontier.
- Hypothesis: restored target-pair shears with nonunit dyadic multipliers can improve the paid circuit beyond the signed-unit family in PR901.
- Domain: all ordered distinct pairs of the 112 target rows, multiplier `s * 2^e`, `s` in {-1,+1}, `e` in {-2,-1,0,1,2}; seed 29 chooses radius `1 + 29 % 2 = 2` and deterministic tie order. Pay preparation, restoration and every coefficient primitive. Compare nonunit edges to the signed-unit baseline with the same selection algorithm. No general optimality or kappa claim.
- Deliverable: exact finite census and a verified circuit if useful; otherwise a scoped negative result for this explicitly enlarged class. Stop after the complete finite census and one construction pass, with at most one evidence-driven pivot.
- Candidates considered: (1) signed-digit coefficient lowering, already #723/#734/#837/#882; (2) unit target-pair compensation, already #901 and historical #749/#816; (3) nonunit dyadic restored pairs, selected because it changes the search class and prices its extra scale work explicitly.
- Coordination: repository issue search found only open issue #650 (request for Discussions), no sprint coordination issue. Recent open PRs and all-state signed-digit/Horner/coefficient/scaled-compensation searches inspected through #902. Local claim used as instructed. PR901 at `dbe8dc01f8306bd7dab8d861a953b23e5cda6a70` is a directly credited comparator, not an accepted frontier or imported implementation. PR883 modifies the preceding precondition; no combined saving is assumed. PR864 excludes frame-only changes of the unchanged word, not changes to this zero-frame scalar panel.

## Result and handoff

The prespecified 124,320-case screen found all 99,456 nonunit cases losing.
One evidence-driven extension added the +/-3 anchors (174,048 total cases)
and proved the exact price is affine and strictly increasing in both tails.
Thus all nonzero integer exponents are excluded for this specific individually
restored, disjoint target-pair family under inherited binary-Horner costs.
The smallest loss is 20 real primitives per orientation. No new circuit or
kappa is claimed. Full finite coverage and the stopping rule were met; no
further search was run. Two implementations have identical record digests.

The final overlap refresh reached #904; upstream main and the selected record
remain unchanged. No pinned coordination issue was available, so this is the
single local result update. Contribution:
[verified branch](https://github.com/ToikY/integer-mult-bounds/tree/codex/complex-supplier-seed29/research/complex-x4-scaled-pairs).
See README, PROOF, EXPECTED, INDEPENDENT, SOURCES and VALIDATION in that folder.
