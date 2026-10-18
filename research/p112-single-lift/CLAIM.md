# Local sprint claim

- Track: structural decoder research; OS assignment seed **40**, drawn once
  with `System.Security.Cryptography.RandomNumberGenerator.GetInt32(0,100)`.
- Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
- Object: P112 complex E8 decoder, a two-coordinate rank-one lift
  `x*x^T + y*y^T = x*(x-z)^T + y*(y-z)^T + (x+y)*z^T`.
- Hypothesis: a shared correction outside the coordinate column space can
  lower the sum of binary label-pairing ranks below the original 16 for
  these two totals (64 overall). Arbitrary support choices are of interest;
  any finite restriction or incomplete coverage will be explicit.
- Method: exact root/label construction; enumerate or certify compatible
  annihilator conditions on the three source supports. Seed 40 selects the
  starting coordinate pair and deterministic exploration order.
- Expected deliverable: one scoped research note with an exact verifier,
  receipt, negative controls, source pins and attribution; no new kappa
  without a complete paid construction.
- Time budget: about 50 minutes from 2026-10-12 23:41 PDT; expected finish
  2026-10-13 00:31 PDT. Final 25% reserved for verification and handoff.
- Candidate selection: the other candidates were unrestricted overcomplete
  full-E8 tensor decoders (adjacent PR765), and extension-ring decoders
  (crowded by PR703/738/767/785/798/814). This lift targets PR717 D1's
  remaining mixed-beta question, without repeating its gauge walk.
- Coordination: no pinned issue existed at claim time; no separate issue
  opened. Open PR inventory and an all-state P112 search were checked.
- Related work: PR620's coordinate cost64; PR717's eight-term and
  hyperplane-flat evidence and open mixed-beta problem; PR446's copy-tree
  pairing-rank interpretation. Their claims retain their review scope.

Prepared for @mihir-s-05 with substantial OpenAI Codex assistance.


## Scope refinement after the bounded experiment

The exact pair test passed for all 28 coordinate pairs. The same argument
extended to every single lift retaining the original eight reader columns:
arbitrary a in R^8 and z in R^112, exact equality on all matrix entries.
This stays within the claimed shared-correction mechanism. The source
supports need not be in the coordinate column space. The unrestricted
mixed-beta decoder problem is not claimed solved.

The finite domain was exhausted: 511 binary functionals and all 3,272 sign
patterns modulo common sign. For all-eight support, the linear relaxation
has rank 63, so its one-dimensional kernel was also checked for actual
value compatibility; each of the 128 kernels conflicts at 56 ports.
The stopping rule is completed exact coverage, not a time-limited search.

Initial related-work snapshot: 642 open PRs; the only all-state P112 title/
body search hits were #620 and #717. The initial no-pinned-issue check was
repeated immediately before the local claim. This local claim substitutes
for a coordination comment; no unrelated issue receives a message.

## Result and final overlap refresh

Completed a scoped negative result: every real single lift retaining the
eight coordinate reader columns costs at least 64. The package contains
the proof, exact certificate, two independently implemented checkers,
source pins, negative controls and attribution. No new kappa or complete
multiplication proof is claimed.

Result artifact: [research/p112-single-lift](https://github.com/mihir-s-05/integer-mult-bounds/tree/research/seed40-p112-decoder-obstruction/research/p112-single-lift).

The final refresh covered 639 open PRs through #842; PR717 stayed at the
pinned head. All-state P112 searches returned #620/#717, and searches for
single lift / ninth total / rank-one lift found no duplicate. There is
still no pinned coordination issue. Main advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631` with the reviewed #799 frontier;
the new files have no overlap with that integration. The initial base and
all mathematical source pins remain exact. See VALIDATION.json for the
completed replay and corruption controls.
