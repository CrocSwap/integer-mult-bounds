# Attribution and assistance

This package is prepared for **@woklerx**, with **substantial OpenAI Codex
assistance**, under the repository's Apache-2.0 license.

The E8 B14 supplier model and label accounting originate in
DreamingOfClouds's [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717).
The exact frame-pair decoder formulation, root-normal support geometry,
and preceding `p<=24` theorem are from themilkman216's
[PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968), retained in
`research/complex-frame-pair-decoders/`. Its README, proof and verifier are
pinned in SOURCES.json and remain unchanged. The simple reflection vectors
follow that credited E8 model. The separate check_sources.py imports the
retained PR968 implementation solely for a model compatibility check.

The primary replay constructs its own root ordering, pairing and finite
dual enumeration. The 26-puncture threshold, explicit witness, rational
completion and finite orbit check are the new contribution. This package
does not claim authorship of the underlying supplier model or preceding
decoder results and does not change the selected bound.

[PR998](https://github.com/CrocSwap/integer-mult-bounds/pull/998), also
prepared for @woklerx with substantial Codex assistance, is prior overlap
context for fixed-reader complex single lifts, not a dependency.
