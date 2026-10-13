Apache-2.0 (see `LICENSE`). Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.

The Lean sources in `HyperplaneEnd/` are new. They generalize the Lemma A package `../e8-lemma-a-lean` and the Lemma G
package `../e8-lemma-g-lean` (both by DreamingOfClouds, prepared with Claude Opus 5.5 via Claude Code), which they use
unchanged through Lake path dependencies. Their extended labels, wrapper reading and realization theorems are those
packages' work; this package only lets the terminal frame of an entering helper be any frame `U`, keys the wrappers by
`(E, U)`, and instantiates Lemma A.

Lemma A formalizes the realization part of Lemma A of PR #484 (DreamingOfClouds), which PR #484 adopted from PR #458 §3
(chafreaky), with PR #471/#500's footprint rule (Dugongue, rohanarun), PR #505's asynchronous borrowing (Dugongue) and
PR #442's stream model (DaysSky). The event semantics are PR #425's conjugation lemma (jacklightChen / Zhihao Chen). The
nested-children factorization `T_U T_E⁻¹ = L (C ⊗ I) R` is from `notes/general-clifford-frames.tex`. Lean conventions
follow the `formal/lean` pin on main and #487/#488 (jamesyc).

`HyperplaneEnd/Clifford.lean` and `HyperplaneEnd/Exact.lean` prove hypothesis (N) for the HPE words' `(E, U)` pairs. Their
gate semantics, `canonical_frame` (`basis_extend`, `inv`, the quadratic form) and `parity`/`mv`/`qvalue` are ports of
`clifford_exact.py` (as vendored in `research/split-centres-global`, icekylinx); `monomial_op` and the `"E:U"` recipe
data are from the HPE wrapper tool `adapters_local.py` (DreamingOfClouds, following PR #458, chafreaky). The packed
kernel check is new; the balanced-split/packed-`Nat` approach to kernel-only checking follows the LeanRoadmap probe.
