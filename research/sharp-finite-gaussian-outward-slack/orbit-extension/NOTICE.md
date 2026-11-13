# Provenance and credit

This bounded sweep is a follow-on check in the finite Gaussian-rounding
thread. It uses the same explicit Hadamard operator (H_4/2) and the
paired (W(D_4)) symmetry documented in the R5 package next door, but it
does not load or depend on the R5 matching certificate.

Relevant prior work and attribution:

- CrocSwap/integer-mult-bounds canonical base: commit
  `e54523517d0f03e58352e647c403a5af3e525a57`.
- PR #6509, Ali Romman, head
  `a4173e810c4d34a1d13b9745af123ad0ec6cfed5`,
  `research/conservative-gaussian-rounding/PROOF.md`, Git blob
  `b7047476aaa5e2bb149c92a8a40a9b2ab444ef73`.
- PR #6619, Nick Petalas, head
  `eaa967e7e8aa12cc53ec246a5fc00c5f8873a50b`,
  `research/rational-norm-rounding/PROOF.md`, Git blob
  `ffb873b2749b1590df9267e802aea5af2c2a6eb5`.
- PR #2589, ywz65, the finite-sphere predecessor cited by #6619.
- @CubeJerry, R5 candidate workstream and exact compact (W(D_4)) orbit
  proof that motivated these four bounded probes, published at commit
  9c75d0b4b6e1cfe74694edf52f2f238a741bbaf5. The corresponding local
  proof is
  `../sharp-finite-gaussian-outward-slack/compact-hall/PROOF.md`
  (SHA-256 `c0a9ee164d3a466a4b3996e1075ef7443123ac5e99b0e4e9e05585411352ad21`).
  Its R5 certificate has expanded SHA-256
  `b1fe3d866d2184227f46ec73ec2021c546bba056e98077e657e9205d9db5ad8b`.

The new finite calculations and write-up were prepared with substantial
OpenAI Codex assistance. No claim here replaces the cited predecessor
results or extends them beyond the four enumerated radii.
