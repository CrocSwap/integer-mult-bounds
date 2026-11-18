# Credit and source boundary

Ali Romman prepared this package with substantial OpenAI Codex assistance.
New work is Apache-2.0. Independent human and formal-kernel review are
unclaimed.

The question follows the scope boundary of Ali Romman's
[PR #7686](https://github.com/CrocSwap/integer-mult-bounds/pull/7686),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/9da06cbe0b888293cbb249cb29eef0f37addaa4f/research/no-edge-image-basis-bound/PROOF.md).
The binary matrix, span, orbit and four-trial lift primitives are reused
from its [exact verifier](https://github.com/aliromman/integer-mult-bounds/blob/9da06cbe0b888293cbb249cb29eef0f37addaa4f/research/no-edge-image-basis-bound/verify.py).
They are included here, with no runtime dependency on that package.

unpaidmoon supplied the earlier cyclic complete-pool example in
[PR #6962](https://github.com/CrocSwap/integer-mult-bounds/pull/6962),
[exact proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/46dbf04cae1140f33bd6a12fa6967a54f8d2c417/research/pattern-dim4-irreducible-image/PROOF.md).
That example is an irreducible basis. It is related context for the present
failure of basis extraction. No source code from that package is reused.

The source record of PR #7686 credits Nick Petalas for the earlier
pattern-fiber lemma and unpaidmoon for the normal-form and two-block pool
results. Those results motivate the restricted pattern-dimension-five
question. They are not reproved or extended to larger dependent-image pools
by the present counterexample.

The cycle plus one extra projector, the exact three-copy pool embedding and
the all-dimension extraction counterexample are the new result here.
