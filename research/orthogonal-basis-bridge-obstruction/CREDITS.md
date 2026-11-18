# Sources and credit

Ali Romman prepared this proof and verifier with substantial OpenAI
Codex assistance. New work is Apache-2.0. Independent human and
formal-kernel review are unclaimed.

- Ali Romman's [PR #7694](https://github.com/CrocSwap/integer-mult-bounds/pull/7694),
  head `96b8b22f5925c4cf4514ed27575f465ebc95e51a`, supplies the prior
  all-k extremal edge-core word obstruction and the full ambient
  bridge-deletion argument. Read its
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/96b8b22f5925c4cf4514ed27575f465ebc95e51a/research/extremal-core-word-obstruction/PROOF.md).
  Binary matrix, polynomial, type-order and Laurent routines are
  adapted from its [verifier](https://github.com/aliromman/integer-mult-bounds/blob/96b8b22f5925c4cf4514ed27575f465ebc95e51a/research/extremal-core-word-obstruction/verify.py).
- CubeJerry's [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
  head `685457252b51b9c7932ece363365bdf0b12c9c31`, supplies the original
  five-core associated-graded and bridge-chronology proof:
  [exact word proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/FIVE-CORE-WORD.md).
  Its [Laurent checker](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/independent_five_word.py)
  is the original source of the adapted recurrence. The source notice
  states that the work was prepared for @CubeJerry with substantial
  OpenAI assistance. This adaptation is not an independent review.
- The no-edge seven-image corollary uses Ali Romman's
  [PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691),
  head `69e70b1426c32b19da8334930815800a2c95ffca`,
  [exact classification](https://github.com/aliromman/integer-mult-bounds/blob/69e70b1426c32b19da8334930815800a2c95ffca/research/no-edge-dim5-extremal-classification/PROOF.md),
  and [PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690),
  head `b725be51349cce4e0a262c76233838992042dd62`,
  [exact image bound](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/PROOF.md).
  The classification retains unpaidmoon's normal-triple and positive
  link credit and Nick Petalas's nonsymmetric-link credit. Those
  constructions and their pool geometry are prior work.

The new result concerns arbitrary even old bases, including coordinate
old calls. It uses the exact diagonal-intersection partition, a
basis-independent idempotence obstruction in the star quotient, and
physical target-multiplicity matching. The Boolean-algebra partition
itself is an elementary algebraic fact, not a new priority claim.

No external file is read at runtime. SOURCES.json binds the main
selected record and task catalogue as provenance. The corollary's
mathematical dependencies are linked at exact public commits; their
whole package replays are not part of this verifier.
