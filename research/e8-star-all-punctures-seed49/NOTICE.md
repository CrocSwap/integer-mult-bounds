# Notice, Attribution, and AI Assistance Disclosure

## License

This package (`research/e8-star-all-punctures-seed49/`) is licensed under the **Apache License, Version 2.0**, matching the upstream `CrocSwap/integer-mult-bounds` repository.

## Predecessor Attribution

This work builds directly on and retains byte-identical copies of predecessor artifacts in `sources/` (verified by SHA-256 and Git blob SHA-1 in `SOURCES.json`):

1. **Chi Zhao** (`@chizhao`, PR #631, commit `fb893b5ee1317c2da3b297e6fe78eca0857d1a76`):
   - Retained files: `sources/pr631/README.md`, `sources/pr631/verify.py`.
   - Established the $120$ positive $E_8$ root lines, the $9$-dimensional binary reader code $C \subset \mathbb{F}_2^{120}$, the $256$ standard parabolic flats, the single-reader puncture thresholds $\delta_d$, and the exclusion of star ratio $< 63/111$ for $0 \le p \le 35$.
2. **Philipp** (`@mightyOil`, PR #875, commit `7f334e4c749fd83d03feb6c1de4e4cda9534c9dc`, `research/e8-rank5-boundary`):
   - Retained file: `sources/pr875/README.md`.
   - Established the two-reader support-union bound $|\operatorname{supp}(c_a) \cup \operatorname{supp}(c_b)| \ge 84$ resolving the $p = 36$ rank-5 boundary.
3. **Ross Richardson** (`@RossRichardson`, PR #939, commit `3a8ec54d62fb8824c658dc7ed356f99423cac8cf`, merged as `c9b187382b2d370e21e866fa4070a7bfceaf86ad`, `research/e8-joint-reader-bound`):
   - Retained files: `sources/pr939/README.md`, `sources/pr939/PROOF.md`.
   - Generalized the pairwise joint-reader capacity inequality $M_a + M_b \ge 84 - p$ to $0 \le p \le 55$ and identified the $p = 56$ binary label dimension-loss boundary.

## Disclosure of Substantial AI Assistance

This research note, mathematical proof, primary verifier (`verify.py`), independent checker (`independent_check.py`), package test suite (`test_package.py`), and certificate (`CERTIFICATE.json`) were prepared by `@3xcalibur-tech` with substantial AI assistance from **Antigravity (Google DeepMind / Gemini)**.
