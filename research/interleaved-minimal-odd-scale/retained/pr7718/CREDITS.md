# Credit and retained sources

Ali Romman prepared this physical scale substitution with substantial
OpenAI Codex assistance in research, implementation, verification and
writing. New work is Apache-2.0. This is author checking with reused
engines, not blind, independent human or formal-kernel review.

The source is [PR #7717](https://github.com/CrocSwap/integer-mult-bounds/pull/7717),
head `586f4f81a8bd09a65a8e6d0bfff57a0fec8925e8`.
Its [complete application](https://github.com/aliromman/integer-mult-bounds/blob/586f4f81a8bd09a65a8e6d0bfff57a0fec8925e8/research/quotient-split-physical-application/PROOF.md)
and [receipt](https://github.com/aliromman/integer-mult-bounds/blob/586f4f81a8bd09a65a8e6d0bfff57a0fec8925e8/research/quotient-split-physical-application/results/application.json)
supply the fixed graph, interface, original scale and full bill.
The interface reader, physical and signed caller engines are retained
without changes. Their source notices are copied byte for byte.

Gareth Davidson / bitplane supplied the coefficient-grid criterion and
basis-witness method in [PR #866](https://github.com/CrocSwap/integer-mult-bounds/pull/866),
[pinned precision proof](https://github.com/bitplane/integer-mult-bounds/blob/5ae580bf68516f1cbe3b2dd3cb646be55170288f/research/dyadic-fractional-grid/README.md).
Ali Romman's [PR #7680](https://github.com/CrocSwap/integer-mult-bounds/pull/7680),
[pinned grid proof](https://github.com/aliromman/integer-mult-bounds/blob/533cdca9225d1c0af1ae8d3b79cb527f59afaf0f/research/banked-native-minimum-grid/PROOF.md)
and [checker](https://github.com/aliromman/integer-mult-bounds/blob/533cdca9225d1c0af1ae8d3b79cb527f59afaf0f/research/banked-native-minimum-grid/verify.py)
supply the integer-gcd and separate Fraction audit structure adapted here.
The criterion and normalized minimum are prior work.

The [common-root proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/odd-native-common-grid/PROOF.md)
and [notice](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/odd-native-common-grid/NOTICE.md)
supply the per-call odd clearing and nested precision argument. Preserve
icekylinx's odd-clearing credit, the fixed-root work of Ross Richardson,
zxv and Jacob Alan Sussman, and the credited source authors. The note was
prepared for CubeJerry with OpenAI assistance; it is not human acceptance.

DreamingOfClouds supplied the literal split witnesses with Claude Opus 5.5
assistance. Clear1nsight supplied the banked physical realization and split
method. Ali Romman supplied the restrictions and composition. SYLforge
supplied the word and signed caller. Rohan Arun, Jerry Chen / CubeJerry,
Douglas Colkitt, mightyOil and the retained contributors supplied the
framework and predecessor methods. The shared-wire notice retains the
operator-engine lineage and unpaidmoon's phase-convention credit.

SOURCE-PINS.json records exact source commits, paths, Git blobs and hashes.
All copies are under source/ or credits/ except the root license. The one
external interpreter is pinned to current main in SOURCES.json. No pending
source history is required for replay, and no source checker is patched.
