# Sources and attribution

- unpaidmoon, with substantial Cursor Grok assistance as stated in the source:
  [PR #7223](https://github.com/CrocSwap/integer-mult-bounds/pull/7223),
  head `7a17378d02117c956ca76b8106f35b15aa34c0dc`.
  The [proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/7a17378d02117c956ca76b8106f35b15aa34c0dc/research/nonidempotent-middle-factor-1100/PROOF.md)
  gives the all-dimension coefficient criterion BC=0 and the named rank-one
  classification. Its Git blob is `ed66217bb9168670c76a245c86d96f3d8bc4af13`.
  The [README](https://github.com/unpaidmoon/integer-mult-bounds/blob/7a17378d02117c956ca76b8106f35b15aa34c0dc/research/nonidempotent-middle-factor-1100/README.md)
  gives the scope and next questions, blob `eff4b18ab892b2b75a309e679ac77a298dd462b3`.
  These files were read. The 296-element accepted-list fingerprint is checked
  by a new raw-product census. The full predecessor suite was not run.
- unpaidmoon, with substantial Cursor Grok assistance:
  [PR #7040](https://github.com/CrocSwap/integer-mult-bounds/pull/7040),
  head `2bac9bfafe5fa009bce2141c07b703c977b18456`.
  The [proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/2bac9bfafe5fa009bce2141c07b703c977b18456/research/rank1-idempotent-triple-1100/PROOF.md),
  blob `902037a612824c9a460a64f38666668607577336`, supplies the orthogonal
  idempotent restriction/extension bijection and earlier counts 58 and 177.
  Its proof, README and verifier were read; its pair census was not rerun.
- Retained lineage, credited by these sources: the E11 slice and orthogonal
  identity in [PR #7027](https://github.com/CrocSwap/integer-mult-bounds/pull/7027),
  Ali Romman's paired-star coordinates in
  [PR #5747](https://github.com/CrocSwap/integer-mult-bounds/pull/5747), and the
  T-commuting obstruction in [PR #6956](https://github.com/CrocSwap/integer-mult-bounds/pull/6956).
  Those packages are not dependencies of this verifier and were not replayed.

The coefficient criterion and the named 296-matrix result are prior work.
The new contribution is the kernel parameterization, all-rank count and rank
distribution, and the higher-rank idempotence split. Gaussian subspace counts,
complement counts and rank-nullity are standard linear algebra, not new claims.

No predecessor code or file is copied. The sources and this new package use
Apache-2.0. Prepared by Ali Romman with substantial OpenAI Codex assistance.
No independent human or formal-kernel review is claimed.
