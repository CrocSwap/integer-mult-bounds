# Sprint claim

- Track: independent verification; fresh OS-random seed **81**, drawn with
  `secrets.randbelow(100)` on 2026-10-13.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60` (freshly fetched main).
- Object: the selected #626 cold-helper pair `E = []`,
  `U = [268, 140, 45, 30]`, width 4; helper register 442 in both providers.
  This is recipe `0:429` in CK and `0:413` in JP8. Among each provider's 14
  lexicographically sorted rank-4 cold recipes, seed `81 % 14 = 11` selects it.
- Method: independent closed matrix-entry formulas over Gaussian integers,
  checking every one of the 512 basis inputs and all 512 output coordinates.
  No imports from the Clifford tableau/compiler or existing state evaluator.
- Deliverable: pinned instance, exact full-operator check, meaningful wrong
  phase/geometry/monomial controls, and a proof of the kernel formula's scope.
  No new kappa and no full formal multiplication theorem.
- Claim time: 2026-10-13 04:25 UTC; expected finish: 04:50 UTC.
  Final quarter reserved for verification and handoff.
- Three candidates: prime-power cyclic inverse identity (already two engines,
  plus #668/#666), entering-helper wrapper (literal proofs in #593 and #581),
  and this rank-4 cold wrapper. The third has no selected literal Lean theorem
  and benefits from a different all-basis matrix-entry implementation.
- Overlap: #662 accelerates the existing tableau/zero-state checker and compares
  circuit-prefix states; this is an independent closed-kernel calculation.
  #680 studies fixed register words, not this supplier wrapper. #675 audits
  owner boundaries. Current negative results and review scope remain intact.
- No pinned coordination issue exists; Discussions remains disabled and #650
  asks for a channel. This local claim avoids opening a reservation issue.

Joshua Snider (`jsnider3`), with substantial OpenAI Codex assistance. Apache-2.0.

## Evidence-driven scope refinement — 04:30 UTC

PR #702 at `27db45ac6befa99d6c06be920a93845023e81937` appeared at
04:26:49 UTC while this work was in progress. It covers all 14 cold frames
using direct matrix entries, including this pair. The initial one-pair replay
here passed, but would duplicate that method. The single pivot keeps the same
helper and replaces the deliverable with an affine-support certificate and
coefficient-wise quadratic-phase identity over 13 Boolean variables. This
independently corroborates #702 by symbolic algebra rather than a second
all-column enumerator. No #702 implementation or result is imported.

## Result — 2026-10-13 04:39 UTC

Submitted [PR #712](https://github.com/CrocSwap/integer-mult-bounds/pull/712).
The affine support map is bijective and the quadratic phase residual vanishes
at all 92 coefficient positions. Thirteen rejection controls pass; five test
groups include direct checks of all six phase components on all 8,192 Boolean
assignments. Normal and optimized isolated runs from a separate committed-files-only
worktree reproduce the exact saved certificate. Selected-record and whitespace
checks passed. No new kappa or full theorem is claimed.

Final overlap refresh through #711 found #702 as the related amplitude audit,
credited for its broader frame coverage. The symbolic method is distinct and
upstream main remains at the recorded base. No pinned sprint issue exists, so
this is the local result update and handoff link. The source contribution is
commit `634026a`; this follow-up changes only the claim's handoff record.
