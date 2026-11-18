# Credit and source identity

Nick Petalas produced the specialized half-sum circuit, proof and verifier
in [PR #7721](https://github.com/CrocSwap/integer-mult-bounds/pull/7721).
The [source README](https://github.com/petalas/integer-mult-bounds/blob/8f6279527c4362e2638737c90fa18c3cfec724fa/research/half-sum-clear-circuit/README.md)
states this credit and asks for a physical tape layout and bill. Its six
scientific files are copied without change from published head
8f6279527c4362e2638737c90fa18c3cfec724fa. SOURCE-PINS.json gives their Git
blobs and SHA-256 values. The source's shared-CI edits are not reused.

SYLforge supplied the source word in
[PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669), and the
row identification, complete XOR/diagnostic interface and general circuit in
[PR #7687](https://github.com/CrocSwap/integer-mult-bounds/pull/7687).
Read the [source interface](https://github.com/SYLforge/integer-mult-bounds/blob/e5ba67dfd6237a1a3acf4d67098d3242adee8229/research/clean-rational-clear-witness/README.md).
Those native and arithmetic results remain inherited. This package claims
only the emitted tape execution, endpoint check and execution/stock bound.

[PR #3233](https://github.com/CrocSwap/integer-mult-bounds/pull/3233) prices a
different pooled high-field ADD and leaves a full finite-control bill open.
No code or constant from that package is used. The selected
[application review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)
already gives a conservative scalar grammar. Its admission does not transfer
to this successor row or stored-program service.

Ripple arithmetic, reversible compute/copy/uncompute and multi-tape machine
simulation are standard methods. Credit the retained native and compiler
authors for the source context. Original notices remain in retained/source;
retained/LICENSE preserves the Apache-2.0 license from the repository base.

Prepared by Ali Romman with substantial OpenAI Codex assistance in research,
implementation, verification and writing. Apache-2.0. This is source-aware
author checking, not independent human or formal acceptance.
