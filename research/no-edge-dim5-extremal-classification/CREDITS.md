# Credit and source boundary

Ali Romman prepared this package with substantial OpenAI Codex assistance.
New work is Apache-2.0. Independent human and formal-kernel review are
unclaimed. There is no external runtime package dependency.

The structural reduction uses Ali Romman's disjoint-circuit theorem in
[PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/PROOF.md).
The small binary matrix, span, lift and orbit routines are reused from its
[exact verifier](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/verify.py).
That source retains credit to CubeJerry for the earlier intersecting-support
method and to Nick Petalas for the binary fiber lemma.

unpaidmoon supplied the three-coordinate normal-form lemma in
[PR #6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921),
[exact proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/6020400853abc110134804fad04b695adc360bcd/research/no-edge-irreducible-image/PROOF.md),
and the two-block construction and open classification question in
[PR #7237](https://github.com/CrocSwap/integer-mult-bounds/pull/7237) and
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281),
[exact source](https://github.com/unpaidmoon/integer-mult-bounds/blob/0cd5324c41490b856d0e94daa8b011683fc153f6/research/no-edge-dim5-fresh-link/PROOF.md).

Nick Petalas supplied the nonsymmetric link in
[PR #7648](https://github.com/CrocSwap/integer-mult-bounds/pull/7648),
[exact source](https://github.com/petalas/integer-mult-bounds/blob/f967555200c111925d48a46b65b124432a762b65/research/no-edge-asymmetric-block-link/README.md).
Ali Romman supplied the fixed-block fresh-factor classification in
[PR #7676](https://github.com/CrocSwap/integer-mult-bounds/pull/7676),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/943c355c233649f77f018e6247e5456584ef715e/research/two-block-fresh-link-classification/PROOF.md).
Its complete-pool proof is restated here with credit.

The irreducible-image-basis classification in
[PR #7686](https://github.com/CrocSwap/integer-mult-bounds/pull/7686) and the
general extraction counterexample in
[PR #7688](https://github.com/CrocSwap/integer-mult-bounds/pull/7688) mark the
scope that this result extends. The new contribution excludes the other
complete-pool geometries and the zero fresh-covector boundary. The existing
positive links, their fixed-coordinate counts and the normal-form lemma
are not new results here.
