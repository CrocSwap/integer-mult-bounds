# Recovered binary certificates and byte entrypoints

This source set contains four reusable, kernel-checked Lean modules. Independent source/API and terminal reviews checked their 15 axiom probes and seven complete printed theorem types. The exact sources and those observed results are recorded in `PUBLIC_SOURCE_MANIFEST.json`.

## What the four modules establish

- `RecoveredProviderChart`: finite lookup recovers the coordinate permutation and inverse table from packed columns plus update/form vectors. Executed round-trip and scalar checks produce a binary chart certificate. Completeness is restricted to one involutive rank-one update after a coordinate permutation, not arbitrary invertible matrices.
- `RecoveredJsonProviderEntry`: decodes an actual named dictionary field, recovers its certificate, generates auxiliary canonical JSON internally, and derives the independent column operator and both inverses. Execution takes no inverse table, permutation or auxiliary certificate input.
- `ByteJsonGlobalCall`: applies the installed UTF-8 and JSON parser to the original byte array, then checks the calls-array count/index and complete owners/assignment data. Success exposes the original parser equations and ordered arbitrary-payload output.
- `ByteRecoveredProviderEntry`: feeds the same parsed dictionary into the recovered entrypoint. Successful byte execution derives the exact parser/recovery/named-field equations and both operator inverses.

The chart statements quantify over arbitrary natural dimension, including the empty finite dimension. They assert no efficient bound uniform in that dimension. Calls/owners statements also quantify over family, row and call counts and payload universes. Soundness uses actual checker success. Completeness retains the stated restricted factorization class and exact input-correspondence equations; it does not claim success on selected files.

## Exact public dependencies

The four new sources total 30,860 bytes. Thirteen unchanged research prerequisites are imported from:

- [PR1831](https://github.com/CrocSwap/integer-mult-bounds/pull/1831), exact head `542f914ca0e5df4026341d08c84385cb1a71cfdf`: shared strict `SelectedSourceSyntax`.
- [PR1879](https://github.com/CrocSwap/integer-mult-bounds/pull/1879), exact head `981afe759f7dd206188b1c1a62250c6425bcd76a`: eight generic parser/index/permutation/gather/chart modules.
- [PR1927](https://github.com/CrocSwap/integer-mult-bounds/pull/1927), exact head `a5838afac3a2d69d802c2440cbfa7d160ca0b218`: four actual-JSON format adapters.

The manifest gives every immutable public path, byte count and SHA-256. Those prerequisites are referenced, not duplicated in this source set. Thin selected L450 applications and canonical owner exports are excluded. See `REPRODUCTION.md` for the isolated 17-module source closure and check order.

## Scope and remaining obligations

Byte success is relative to `String.fromUTF8?` and `Lean.Json.parse` as installed executable functions. It does not prove those implementations against Unicode or JSON standards, prescribe lexical integer spelling, reject duplicate object keys, prove a serializer/parser round trip, validate an artifact digest or authenticate a dictionary key. No actual selected artifact has been checked by this package.

The binary address operator and its inverses do not supply complex phases, affine shifts, physical chart direction, memory allocation, primitive execution, precision or runtime/bit-cost bounds. Parser errors remain distinct in `parseBytes`; the Option consumers return `none` for either error. No new JSON grammar, selected literal census or closed finite decision is introduced.

At the explicit author-checked context kappa = 836330098538459/500000000000000000 = 0.001672660197076918, these generic theorems do not use or change kappa and do not prove the full multiplication theorem.

## Attribution

Lean UTF-8/JSON parser and Mathlib authors; Jeremy Kothe's T16/PR514 and inherited PR484/507 lineage; Rohan Arun's PR1094 source-format lineage; and the accepted strict parser, permutation, gather, chart and recovery components are credited in the unchanged sources. Prepared by James Chang with OpenAI assistance under Apache-2.0. Preparation-time source comments are preserved; the additive manifest records completed acceptance.
