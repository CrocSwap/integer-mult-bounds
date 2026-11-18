# Sources and credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
New work is Apache-2.0. Independent human and formal-kernel review are
unclaimed. The verifier follows the earlier half-grid conventions and
integer comparison method; it is not a blind review of those sources.

- CubeJerry / Jerry Chen's [PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570),
  [exact proof](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md),
  supplies the half-grid reduction and the sharp square-to-swap theorem.
  Its global annular construction and attaining four-cycle supply the
  upper bound for the weaker fourth-power class here. They are not new.
  The full proof was read; its full package replay was not run.
- Ali Romman's [PR #7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696),
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/d7be8d9131a948ea1d25833e96906ea3da979764/research/gaussian-exact-sum-global-optimum/PROOF.md),
  supplies the sharp unconstrained exact-sum value, the individual-ring
  matching, square boundary costs and sharpness geometry. The new proof
  forces every optimal map into those ring choices. The code adapts its
  coordinate conventions and integer radical comparisons; the exhaustive
  matching and orbit classifier are new.
- Ali Romman's [PR #7698](https://github.com/CrocSwap/integer-mult-bounds/pull/7698),
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/f821eb5ea909e5c56118c5042f7740d87f0355b2/research/phase-covariant-radial-ports/PROOF.md),
  motivates the question through its failed fourth-power identity at the
  optimum. Its phase/port construction is not replayed or changed here.

The new lower proof assumes neither square-to-swap nor quarter-turn
symmetry. Its finite-capacity and cycle classification yield the general
finite-order gap and the exact weaker fourth-power lower bound.
The sources retain Nick Petalas's forward exact-sum question and first
finite witness, Ali Romman's next witness and ideal pair, and the earlier
Gaussian/native/compiler credit. No prior finite witness, generic matching
method, half-grid transform or upper construction is claimed as new.

[PR #7572](https://github.com/CrocSwap/integer-mult-bounds/pull/7572) concerns
affine translation periods. That is a different condition from F^m=id;
it was checked for overlap and is not a mathematical dependency here.
