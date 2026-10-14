# Compact natural-column fragments and named dictionary entries

Three reusable Lean modules connect compact natural-column fragment bytes to an existing named dictionary entry and establish their exact ASCII/one-byte UTF-8 representation. The statements are dimension-parametric and introduce no selected table census.

## Accepted source scope

- **CompactNatColumnFragment** executes the existing byte parser and ordered bounded-column decoder, then compares every original byte against the compact encoding of the decoded columns. Success derives the original UTF-8/parser/AST equations, exact bytes, length `n`, and every column bound `< 2^n`.
- **CompactFragmentDictionary** validates the fragment, runs the unchanged restricted provider recovery on a supplied dictionary AST/key, and checks equality of the complete ordered column lists. Success identifies the parsed fragment AST with that named entry and derives the independent binary column operator and both inverse identities.
- **CompactNatColumnAscii** proves that arbitrary natural-number representations contain decimal digits only, that the compact array adds only brackets and commas, and that those characters take exactly one UTF-8 byte each in their original order. Its general string lemma requires only an ASCII hypothesis; the compact-array application derives that hypothesis.

The three unchanged accepted sources total **20,894 bytes**, with **16 axiom probes and six complete printed types**. All observed axioms are among `propext`, `Classical.choice`, and `Quot.sound`; there are no diagnostics in the accepted outputs. The ASCII proof has five ordinary closed `decide` sites for the fixed ten-digit alphabet, three punctuation constants and positivity of base ten. There are no `decide +kernel` sites or selected-data decisions.

The exact sources, hashes, imports, complete observed probes and printed types are in `PUBLIC_SOURCE_MANIFEST.json`. Original comments, attribution and historical preparation labels remain unchanged; the manifest records acceptance of these exact final versions. Failed earlier proof elaborations were rejected, and only the repaired clean versions appear here.

## Public prerequisites, without copying

The minimal research-source closure is **19 modules**: these three sources and 16 unchanged public prerequisites. Import the prerequisites from their exact public heads:

- [PR1831](https://github.com/CrocSwap/integer-mult-bounds/pull/1831), `542f914ca0e5df4026341d08c84385cb1a71cfdf`: shared strict syntax
- [PR1879](https://github.com/CrocSwap/integer-mult-bounds/pull/1879), `981afe759f7dd206188b1c1a62250c6425bcd76a`: eight strict parser, table, binary chart and JSON interpreter components
- [PR1927](https://github.com/CrocSwap/integer-mult-bounds/pull/1927), `a5838afac3a2d69d802c2440cbfa7d160ca0b218`: four actual-JSON adapters
- [PR1950](https://github.com/CrocSwap/integer-mult-bounds/pull/1950), `d5aa485468f31fbcac3758ee63284c07da426cde`: `RecoveredProviderChart`, `RecoveredJsonProviderEntry`, and `ByteJsonGlobalCall`

The fourth PR1950 module, `ByteRecoveredProviderEntry`, is unused by this closure. The separate checked-slice witness and selected L450 applications are excluded. File paths, SHA-256 identities and the exact topological order are in the manifest. `REPRODUCTION.md` describes a fresh-reader check using an already prepared Lean 4.21.0 / Mathlib environment.

## Exact remaining premises and limits

The compact validator's completeness theorem still requires the explicit equation that the actual parser returns the canonical column AST on the compact payload. The ASCII and one-byte UTF-8 theorems do not prove that JSON parser equation, a numeral-value parsing theorem or a general decode/encode round trip.

The dictionary join consumes a dictionary AST. It proves semantic identity at its named field, but does not establish that the fragment bytes physically occur within a particular dictionary file, identify a byte offset as that field's source span, or authenticate a digest key. No actual selected-file success is claimed. Pre-collapse duplicate-key history, lexical normalization and equivalence of Python and Lean serialization remain separate.

Recovery retains its restricted class: a coordinate permutation followed by one involutive rank-one binary update, with the checked scalar conditions. Invertibility alone does not imply completeness. The operator is over the finite binary address space, including dimension zero; this does not supply complex phases, a physical chart direction, a physical executor, precision or cost bounds. Logical representation proofs also do not verify the compiler/runtime extern implementations.

## Author-checked context and attribution

Author-checked kappa is **836330098538459/500000000000000000 = 0.001672660197076918**. These generic results do not use or change kappa and do not prove the full integer-multiplication theorem.

Credits are preserved for Lean's Nat/String/UTF-8/JSON and Mathlib authors; Jeremy Kothe's T16/PR514 compact sigma payload and inherited PR484/507 geometry; Rohan Arun's PR1094 source-format lineage; and the accepted strict parser, column, chart, recovery and fragment components. James Chang with OpenAI assistance. Apache-2.0.
