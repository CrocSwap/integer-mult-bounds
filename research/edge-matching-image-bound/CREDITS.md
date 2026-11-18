# Sources and credit

Ali Romman prepared this proof and verifier with substantial OpenAI
Codex assistance. New work is Apache-2.0. No independent human or
formal proof-kernel review is claimed.

- Ali Romman's [PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690),
  head `b725be51349cce4e0a262c76233838992042dd62`, supplies the disjoint
  diagonal-relation proof, restated here with the unit-free restriction
  removed. The [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/PROOF.md)
  credits CubeJerry's earlier support argument and unpaidmoon's
  normal/column blocks. Matrix, basis, lift, orbit and subspace routines
  are reused from its [verifier](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/verify.py).
- Ali Romman's [PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691),
  head `69e70b1426c32b19da8334930815800a2c95ffca`, supplies the
  column-support invariant lemma, restated with proof. Read its
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/69e70b1426c32b19da8334930815800a2c95ffca/research/no-edge-dim5-extremal-classification/PROOF.md).
- CubeJerry's [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
  head `685457252b51b9c7932ece363365bdf0b12c9c31`, supplies the general
  edge-quotient bound, the exact five-projector two-edge example and its
  irreducible normal form. Read its [exact proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/PROOF.md).
  The author notice states that the work was prepared for @CubeJerry
  with substantial OpenAI assistance. It credits Nick Petalas's
  [PR #5921](https://github.com/CrocSwap/integer-mult-bounds/pull/5921)
  for the binary fiber theorem. That fiber argument is proved again
  here. The five-projector witness is checked without changing its masks.
- Nick Petalas's [PR #6785](https://github.com/CrocSwap/integer-mult-bounds/pull/6785),
  head `5dbf2c05220bea53d84b510efe5910c4cec8f182`, proves the one-edge,
  pattern-three irreducible bound four. This is a prior special case,
  not a new result here. The source notice gives the author name:
  [exact proof](https://github.com/petalas/integer-mult-bounds/blob/5dbf2c05220bea53d84b510efe5910c4cec8f182/research/one-edge-pattern-reducibility/PROOF.md).
- CubeJerry's [PR #6838](https://github.com/CrocSwap/integer-mult-bounds/pull/6838)
  already proves the universal pattern-three total bound six. Its
  [exact proof](https://github.com/CubeJerry/integer-mult-bounds/blob/f177c4f27e63dfa2e886033bb6a4e2dcd91f40b6/research/bit-zero-edge-image-bound/PROOF.md)
  is context, not an executable dependency.

The new result is the all-width edge-matching refinement, its total
equality exclusion for irreducible complete pools, and sharp all-k
total and irreducible maxima. The earlier no-edge theorem and each
known three-dimensional example retain their original credit.

No external source file is read at runtime. Mathematical arguments
needed for the new result are included in PROOF.md. The two entries
in SOURCES.json bind the selected state and task catalogue on main;
they are provenance records, not proof premises.
