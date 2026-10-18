# Sprint claim — agent-11 (recorded locally; no pinned coordination issue exists)

- Track: 85–94 Verification engineering
- Assignment seed: 89 (OS randomness: .NET `RNGCryptoServiceProvider` bytes
  45-AB-45-3C, modulo 100; 2026-10-13)
- Base commit: 2921874911956718fcaaaf9396fe8267b3cfa9f0 (origin/main of
  CrocSwap/integer-mult-bounds)
- Branch: research/agent-11-verifeng-seed89
- Object under investigation: the row construction of `rank_witness` in
  `scripts/experiments/quadratic_affine.py`, the hot path of the costly
  `make verify-certificates` check `scripts/audit_quadratic_affine.py`
  (89.1 s at base; 160M+ per-pair `inner` calls in its heavy fixture).
- Method: replace the per-pair row loop with an exact bit-sliced batched
  orthogonality engine (lane-packed character masks, even-lane SWAR zero
  test, collision-free stride-8 gather); differential A/B against the
  verbatim base-commit reference on every row of every fixture; regenerate
  the certificate and require byte equality apart from the edited source's
  own recorded hash; negative controls on the SWAR borrow chain, a dropped
  gather stage, and row-corruption digest detection.
- Expected deliverable: tooling improvement with before/after wall times
  (89.1 s -> 10.6 s), full row-level differential evidence, and a one-line
  regenerated-certificate diff. No new kappa.
- Coordination checked 2026-10-13 at claim time: no pinned sprint
  coordination issue (open issues are #913 "All size/compiler is retained"
  and #650 "Can we turn on Discussions?"); open tooling PRs #1006 (T37
  occupancy bitmaps), #976 (`audit_joint_frames` modular rank screen), #946
  (codec reproducibility) and #898 (Leech minors) cover different checks or
  different functions; no overlap with this claim at that time.
- Final overlap review (same day): PR #752 (opened 05:07Z, seed 92) had
  already targeted this hotspot with a non-invasive packed-lane adapter.
  This claim proceeds as an independent second implementation plus
  integration into the shipped check, with the distinction and credit
  recorded in README.md. The earlier "no overlap" line is kept above as the
  historical claim-time record.
- Claim posted here locally in place of an issue comment, per instructions.
- Expected finish: same session (2026-10-13).
