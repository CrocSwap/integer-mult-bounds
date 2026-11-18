# Sources and credit

Ali Romman prepared this proof and verifier with substantial OpenAI
Codex assistance. New work is Apache-2.0. No independent human or
formal-kernel review is claimed.

- Ali Romman's [PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692),
  head `c2870a38841f515db7203a0761cd77f014f7fb7a`, supplies the all-width
  matching bounds and the all-k attaining family. Its
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md)
  is the mathematical dependency used to force the edge count and
  preserve the image under completion. Matrix, basis, lift, orbit and
  subspace routines are reused from its
  [verifier](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/verify.py).
  That package credits the disjoint-relation and support arguments in
  [PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690)
  and [PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691),
  and their retained predecessor lineage.
- CubeJerry's [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
  head `685457252b51b9c7932ece363365bdf0b12c9c31`, supplies the prior
  five-dimensional two-edge restricted normal form and its common
  cross-block argument. The source notice states that it was prepared
  for @CubeJerry with substantial OpenAI assistance. Read its
  [exact proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/PROOF.md).
  The proof also credits Nick Petalas's
  [PR #5921](https://github.com/CrocSwap/integer-mult-bounds/pull/5921)
  for the binary fiber theorem. The present edge lifts are the same
  two-member fibers, not a new construction.

The new result forces the edge count and disjointness at every k,
classifies the full ambient link, and proves that an arbitrary
extremal irreducible collection is automatically complete. The pure
matrix-unit graph criterion supplies the boundary case. The k=3
restricted normal form and the all-k positive family retain their
original credit.

No external source file is read at runtime. SOURCES.json binds the
selected state and task catalogue on main as provenance. Those
records are not mathematical premises. The matching proof is linked
at its exact public commit; full predecessor package replays are not
part of this verifier.
