# Sources and credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
New work is Apache-2.0. Independent human and formal-kernel review are
unclaimed. The algebraic oracle is adapted source methodology, not blind
or independent scientific review.

- Ali Romman's [PR #7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696),
  [proof](https://github.com/aliromman/integer-mult-bounds/blob/d7be8d9131a948ea1d25833e96906ea3da979764/research/gaussian-exact-sum-global-optimum/PROOF.md)
  and [ring code](https://github.com/aliromman/integer-mult-bounds/blob/d7be8d9131a948ea1d25833e96906ea3da979764/research/gaussian-exact-sum-global-optimum/verify.py),
  supplies the global Hall lower bound and individual-ring matching.
  The new kernel adapts that matching and removes variable division.
  That source retains Nick Petalas's first forward exact-sum witness,
  CubeJerry/Jerry Chen's half-grid and annular geometry, and the earlier
  Gaussian-pair credit. The lower theorem is not a new result here.
- Ali Romman's [PR #6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509),
  [proof](https://github.com/aliromman/integer-mult-bounds/blob/a4173e810c4d34a1d13b9745af123ad0ec6cfed5/research/conservative-gaussian-rounding/PROOF.md),
  [port interface](https://github.com/aliromman/integer-mult-bounds/blob/a4173e810c4d34a1d13b9745af123ad0ec6cfed5/research/conservative-gaussian-rounding/ports.py),
  [retained code](https://github.com/aliromman/integer-mult-bounds/blob/a4173e810c4d34a1d13b9745af123ad0ec6cfed5/research/conservative-gaussian-rounding/inputs/rounded.py)
  and [oracle source](https://github.com/aliromman/integer-mult-bounds/blob/a4173e810c4d34a1d13b9745af123ad0ec6cfed5/research/conservative-gaussian-rounding/verify.py),
  supplies the exact backend interface, stage structure, requests and
  coordinate-error/width analysis. oracle.py follows its rational
  convolution and literal three-bit monomial formulas. Exact copied
  files keep their notices and are authenticated by ORIGINS.json.
- JoyboyBrian's [PR #5485](https://github.com/CrocSwap/integer-mult-bounds/pull/5485)
  and [PR #4743](https://github.com/CrocSwap/integer-mult-bounds/pull/4743)
  supply the actual port and error-channel lineage, as recorded in the
  retained [notice](predecessor/NOTICE). Generic reversible rounding,
  phase covariance, fiber sums and dirty cleanup are prior work.
  The notice retains Tekalign, Arham Tahir, Nick Petalas, Cinna Davis
  and the earlier native/compiler attribution.
- CubeJerry's [PR #6758](https://github.com/CrocSwap/integer-mult-bounds/pull/6758),
  [pinned source](https://github.com/CubeJerry/integer-mult-bounds/blob/362b20bc934500bc503e850059f0d34daa5dcae3/research/four-axis-phase-covariant-grid/README.md),
  is related prior phase restoration and port binding for a different
  four-axis quotient map. No code or precision gain is transferred from it.

The new result selects the one-pair matching by sum parity. It attains
the sharp radial budget with phase, conjugate-inverse, translation and
swap covariance, then proves the complete retained-port radial envelopes.
The copied sources are unchanged. Their retained proof is a dependency,
not a claim of independent reproving or first port implementation.
