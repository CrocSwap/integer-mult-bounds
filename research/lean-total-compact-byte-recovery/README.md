# Total compact-byte decoding and L450 operator recovery

Five unchanged, independently accepted Lean 4.21.0 sources connect compact decimal bytes to bounded ordered columns and the existing independently defined column operator. The selected application recovers the previously bound original 907-byte L450 fragment and proves both inverse directions on every address, without a logical JSON-parser premise.

Author-checked context: κ = 836330098538459/500000000000000000 = 0.001672660197076918, at selected main revision 299eb8effe080183313757ac36e76c1b98ed9fae. The generic theorems do not use or change κ. This package does not prove the full multiplication theorem.

## Executed decoder and proved endpoints

`DecimalReprValuation` proves that a total decimal accumulator evaluates the installed logical `Nat.repr` back to its original natural number. It also proves representation injectivity. The accumulator by itself is not a rejecting lexer.

`TotalCompactColumnDecoder` runs logical UTF-8 decoding, checks the outer brackets, splits the interior in order at commas, evaluates the tokens, and executes an equality comparison of the complete original bytes against the existing canonical encoding. The equality comparison supplies strict acceptance even for arbitrary candidate tokens. Leading zeros, whitespace, alternate spellings and other noncanonical input are rejected. Its exact endpoints are:

- `decodeNatArray bytes = some xs ↔ bytes = CompactNatColumnFragment.encode xs`
- `decodePacked n bytes = some cols ↔ bytes = CompactNatColumnFragment.payload cols`

These are all-list/all-dimension statements. Empty arrays, repeated entries, original order, exact length and packed-column bounds are retained. Canonical completeness follows from the accepted decimal/UTF-8 facts and the official list split/intercalate theorem.

`TotalCompactProviderRecovery` executes that bounded decoder and then the unchanged restricted provider recovery. Its executable inputs are original bytes and update/form vectors. It returns the decoded columns together with the recovered checked certificate. Successful execution derives the exact canonical byte identity, original column function, supplied vectors, equality with the independent column operator, and both all-address inverse laws. Completeness is restricted to the existing checked single-transvection/permutation class.

`Current1094L450TotalDecoder` and `Current1094L450TotalRecovery` apply these generic results to the accepted original 907-byte literal. They reuse the exact published byte-to-payload equality and existing selected scalar certificate. No new literal, scalar census, large finite decision or runtime diagnostic is needed. The final inverse theorem refers to the old independent `Current1094L450OrderedChart.sourceLinear`.

## Acceptance and boundaries

`ACCEPTANCE.json` records all 14 exact axiom probes, all ten complete printed types, source/object hashes and independent reviewer roles. The five source hashes are accepted with no diagnostics. Some immutable source comments still describe acceptance as separate or a predecessor as required; the source-bound status entries explicitly supersede that preparation wording without editing the accepted code.

The new logical path does not call `Lean.Json.parse`. It does not prove the old opaque parser's equation, general JSON compatibility, or equivalence with the old `validateFragment`. The exact canonical byte policy is intentionally narrower than general JSON. Logical standard-library facts also leave compiler/runtime extern refinement separate.

The selected literal's external archive/member/slice provenance is reused from PR2371. This package proves the new decoder and recovery results for that exact literal; it does not authenticate a file supplier or prove the fragment's structural location in an original whole dictionary. `ARTIFACT_BOUNDARY.md` states the precise inherited identity and remaining boundary. Complex phases, physical allocation/execution and paid costs are separate.

## Reproduction and reuse

The five new sources total 24,208 bytes. The accepted research closure contains 103 modules: these five and 98 unchanged immutable public prerequisites. None of those prerequisites is copied here. All 94 prior prerequisite mappings are reused unchanged, with four already-public byte/ASCII suppliers added. The inherited import-only source recipe remains explicit.

`PUBLIC_SOURCE_MANIFEST.json` gives exact public revisions, paths, hashes, imports and topological order. `REPRODUCTION.md` provides prospective hash-checked bounded serial commands, including the existing official `Mathlib.Data.List.SplitOn` provider. Preparation ran no compiler, parser diagnostic, archive extraction or census. Dependency installation or recovery requires separate authorization.

Credits: Jeremy Kothe for T16/PR514 compact sigma encoding; Rohan Arun for PR1094; James Chang with OpenAI assistance for the paired bank/frame Lean work; Lean, Batteries and Mathlib contributors. Existing attribution and Apache-2.0 source declarations are preserved.
