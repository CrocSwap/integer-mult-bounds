# Credit and source boundary

Ali Romman prepared this package with substantial OpenAI Codex assistance.
New work is Apache-2.0. Independent human and formal-kernel review are
unclaimed. No predecessor package is needed at runtime.

CubeJerry supplied the intersecting diagonal-dependency argument and the
sharp dimension-three total bound in
[PR #6838](https://github.com/CrocSwap/integer-mult-bounds/pull/6838),
[exact proof](https://github.com/CubeJerry/integer-mult-bounds/blob/f177c4f27e63dfa2e886033bb6a4e2dcd91f40b6/research/bit-zero-edge-image-bound/PROOF.md).
The new proof extends the coordinate-column method to every diagonal
relation at once.

unpaidmoon supplied the normal/column triple classification, the sharp
dimension-four bound in
[PR #7139](https://github.com/CrocSwap/integer-mult-bounds/pull/7139),
[exact proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/007869ccdc22ee591b5a88d99a35f02511bffbee/research/no-edge-dim4-image-at-most-six/PROOF.md),
and the seven-image construction in
[PR #7237](https://github.com/CrocSwap/integer-mult-bounds/pull/7237) and
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281),
[exact source](https://github.com/unpaidmoon/integer-mult-bounds/blob/0cd5324c41490b856d0e94daa8b011683fc153f6/research/no-edge-dim5-fresh-link/PROOF.md).
The seven-image witness is rechecked as prior sharpness evidence.

Nick Petalas supplied the binary fiber lemma in
[PR #5921](https://github.com/CrocSwap/integer-mult-bounds/pull/5921),
as credited in the exact proofs of PR #6838 and PR #7139. A short proof is
included here. The new total bound does not require the fiber lemma; it is
used for the irreducible equality boundary and complete sharp pools.

Ali Romman's image-basis theorem in
[PR #7686](https://github.com/CrocSwap/integer-mult-bounds/pull/7686),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/9da06cbe0b888293cbb249cb29eef0f37addaa4f/research/no-edge-image-basis-bound/PROOF.md),
and extraction counterexample in
[PR #7688](https://github.com/CrocSwap/integer-mult-bounds/pull/7688),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/d9aba79eaed566640353efcb0a27b0d5649f705a/research/no-edge-basis-extraction-failure/PROOF.md),
supplied the immediate scope question. Their exact verifiers supply the
reused binary matrix, span, lift, orbit and subspace-enumeration primitives:
[PR #7686 verifier](https://github.com/aliromman/integer-mult-bounds/blob/9da06cbe0b888293cbb249cb29eef0f37addaa4f/research/no-edge-image-basis-bound/verify.py),
[PR #7688 verifier](https://github.com/aliromman/integer-mult-bounds/blob/d9aba79eaed566640353efcb0a27b0d5649f705a/research/no-edge-basis-extraction-failure/verify.py).

The disjoint-circuit structure, the sharp total bound for every k, and the
general irreducible consequence are the new result. Earlier examples,
dimension-specific bounds and normal-form classifications retain their
source credit.
