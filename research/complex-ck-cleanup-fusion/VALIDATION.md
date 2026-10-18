# Validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Local environment: macOS 26.5.2 arm64; Python 3.14.8 and Python 3.11.15.
Verification started at approximately 2026-10-13 04:39 UTC, after the completed
bounded experiment and before submission. The original maximum work budget
was 50 minutes, with completion permitted earlier.

Passed:

- `python3 -B research/complex-ck-cleanup-fusion/verify.py`.
- `python3 -O -B research/complex-ck-cleanup-fusion/verify.py`, with all checks
  still active. Both print `PASS_CK_CLEANUP_RANK_TWO pairs=78 rank=2 columns=312 controls=8`.
- Independent direct-column checker, including optimized Python execution:
  78 pairs, both orientations, 312 columns, 624 exact minor entries.
- Python 3.11.15 optimized replay from a minimal temporary checkout containing
  only this package and the four pinned inputs, at a path containing spaces,
  invoked while the working directory was `/`.
- Recompressing the input with gzip level 1 and a different timestamp preserves
  acceptance. Changing the decompressed input, supplier SPEC bytes, or certificate
  support metadata causes rejection in the temporary checkout.
- `make selected-record-check` passes with the unchanged accepted rational kappa,
  source inventory, and proof-supplement checks.
- Staged whitespace checks and local documentation links pass. The diff contains
  only this package; upstream main still has the recorded base commit.

The package's five semantic controls and three certificate-mutation controls run
on every normal invocation. They distinguish individual commutation blockers
from complete-middle rank obstructions and detect bad minor entries, dual signs,
and coverage. Two additional Codex workers reviewed the same narrowly claimed
scope. One supplied the independent arithmetic implementation; another reported
no mathematical or code blocker for the full-register-space statement. This is
AI-assisted review, not independent human review.

The full repository `make verify`, selected cold supplier regeneration,
global invoice/assembly replay, Lean, and remote Linux CI were not run for this
isolated research addition. No selected construction, generator, production
verifier, or source input changes. The result does not claim a faster
implementation, smaller recursive moment, or larger kappa.

Final overlap review inspected 531 open PRs through #712 and refreshed the pinned
issue query, which remained empty. In particular, #710's new bit-cleanup
conjugation construction is credited in the README and does not establish the
CK rank-two census. #705 concerns determinant obstructions for Clifford register
paths and is a different search class. Exact inspected heads for related work:

| PR | Head |
| --- | --- |
| #271 | `ebc1defe8c13f39f86e5901c3437c1be52886a2b` |
| #411 | `f58d95f2c5da03445e704ea9c72cc55df9e68190` |
| #681 | `80d4edbc2d53f058787cb5c43bd0fc22c7e7fdff` |
| #687 | `82bbb9c3ac34540f196410d137ebc59d9c2c43a9` |
| #696 | `5a3f983715027c4fd83f50bc9001d4b18463bed1` |
| #698 | `ab78f797cffcbeddbb17a7eb069741085ffe3351` |
| #705 | `eeb0cd605415a73b792915aaa9185000f293c84a` |
| #710 | `d97c8d20a8b885271a24c5a4e8446ac7f5697d5c` |

An immediate pre-submission refresh covered 535 open PRs through #716.
#713/#716 concern R420 target-basis compensation; #714 concerns clean product-shear
checkpoints; #715 concerns mixed E8 ports. None studies this fixed CK cleanup
pair domain.
