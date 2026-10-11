# Serialization audit review informed by PR444

Source: [PR444](https://github.com/CrocSwap/integer-mult-bounds/pull/444), head `8c4242ea61c67827fe62b07b2edc093d7ddfa631`; audit blob `b256e112b0d51dd3ffb34eb3e1516084a8965485`, SHA256 `e770305d5b23967bf0fcd3757c9b04587b28931ae1ed30e9bc9e6f53d5e86218`. Attribution: chafreaky with OpenAI Codex, Apache-2.0.

PR444 contributes useful checks: exact immutable template fields, full unchanged call metadata and local instructions, normalized schedule equality, fourteen ownership/window mutations, and a fresh streamed hash after helper owners change. We adapted these checks to our separately admitted signed75 T64 supplier in a future-only audit; the published frozen package is unchanged.

A concrete isolated-checker gap motivated the adaptation. Our earlier joint assignment/profile checker accepts a template whose private centre reserve changes from 9 to 8 after its template digest is correctly rebound. That checker focuses on assignments/profile and never reads the reserve field. FIELD-GAP.json reproduces the observation. This does not show that the full frozen package admits an incorrect primitive: its source manifest and unchanged local signed/private-work checks provide separate constraints. The new immutable-field guard rejects the same mutation.

The instruction hash covers the serialized renamed local-call stream. It does not emit or hash every idle, bridge, final exchange, sigma-chart, or selector primitive. A separate canonical schedule digest and immutable-field check bind those serialized descriptors. This distinction should accompany any `emitted_program_sha256` label: a hash of abstract descriptors is useful conformance evidence, while exact expanded primitive realization and its counted compiler invoice remain additional conditional obligations.

This is a constructive project review artifact, not feedback sent to the upstream authors. The source-bound rational sigma, local signed J decoder/dirt, and global hosted invoice gates remain separate; native F2 cancellation alone does not admit an integer lift.
