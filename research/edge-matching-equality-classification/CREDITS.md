# Sources and credit

Prepared by Ali Romman (@aliromman) with substantial OpenAI Codex assistance.
New work is Apache-2.0. No independent human or formal-kernel review is claimed.

The consumed disjoint-relation and matching theorem is Ali Romman's
[PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md).
Binary matrix, pattern-lifting, matching and orbit primitives are adapted
from its [checker](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/verify.py).
The pair blocks, all-pair fresh links and general image bound are prior work.

Ali Romman's [PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/69e70b1426c32b19da8334930815800a2c95ffca/research/no-edge-dim5-extremal-classification/PROOF.md),
supplies the complete-coset column argument and the two-triple equality
classification. It credits unpaidmoon's [PR #6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921) for the normal-triple lemma
and [PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281) for the two-block fresh-link construction. Those finite blocks
and that special classification are retained results. The present checker
repeats the normal-triple step, then checks the new mixed equality domains.

The exceptional lower-attainment case uses Ali Romman's three-copy pool lemma
in [PR #7688](https://github.com/CrocSwap/integer-mult-bounds/pull/7688),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/d9aba79eaed566640353efcb0a27b0d5649f705a/research/no-edge-basis-extraction-failure/PROOF.md).
The new three-projector instance is separate from that source's cycle family.

Jerry Chen (@CubeJerry), Nick Petalas (@petalas) and @unpaidmoon supplied the earlier
matrix-unit fiber, three-relation, no-edge and normal-block results credited
in the consumed proofs. Nick Petalas's [PR #7648](https://github.com/CrocSwap/integer-mult-bounds/pull/7648) supplied asymmetric fresh
block links. The universal maximal edge-pool classification in Ali Romman's
[PR #7693](https://github.com/CrocSwap/integer-mult-bounds/pull/7693) is the
all-pair end of the present first-equality family. These are predecessor
results, not new claims here.

The relevant word obstruction is Ali Romman's
[PR #7695](https://github.com/CrocSwap/integer-mult-bounds/pull/7695),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/996c002d82420141c19797e4e3b699ed88aee330/research/orthogonal-basis-bridge-obstruction/PROOF.md).
This geometry result does not bypass its relation-lattice premises or supply
a scalar word. The G20 source proposals [PR #5679](https://github.com/CrocSwap/integer-mult-bounds/pull/5679) and [PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708) were read for
orientation; their component savings are not changed or reused as bounds.

The contribution is the general equality classification, its parity condition,
the sharp improved odd-difference bound, the attaining families and the two
complete small-block exclusions. It does not claim that finite checks alone
prove an unrestricted multiplication theorem.
