# Key-only compact dictionary certificates

Author-checked source context: **κ = 836330098538459/500000000000000000 = 0.001672660197076918**, as recorded in [the selected result at the preserved author-checked source revision](https://github.com/CrocSwap/integer-mult-bounds/blob/299eb8effe080183313757ac36e76c1b98ed9fae/certificates/selected-result.json). These generic results do not use or change κ and do not prove the full multiplication theorem.

## What this adds

- `HexObjectLayout` constructs an ordered flat-object byte layout. It checks actual nonempty lowercase-hex key bytes and their distinctness, and derives the selected payload's prefix, offset, suffix and exact slice from the complete layout. Arbitrary payloads in this generic module alone do not assert JSON validity.
- `CheckedCompactObject` restricts every payload to the accepted bounded compact Nat-column encoder. It executes key checks, equality against **every original artifact byte**, actual parser/recovery, and complete selected-column equality. The selected slice follows from the complete layout rather than a supplied containment assumption.
- `KeyOnlyCompactObject` accepts original bytes and an ordered key list, with a natural selected index and restricted binary update/form. It parses the actual bytes and strictly decodes **all column values internally**, preserving key order and every named lookup. It then invokes the unchanged complete-layout checker on the same bytes. Actual success derives the independent column operator and both inverse identities.

All three sources are kernel-checked and independently source/API/terminal reviewed: 17 complete axiom probes and six complete printed types are recorded in `ACCEPTANCE.json`. Observed axioms are only `propext`, `Quot.sound` and `Classical.choice`; no diagnostic or admitted proof is accepted. Historical preparation comments are retained byte-for-byte, with this additive acceptance record supplying their later status.

## Coverage and limits

The statements cover arbitrary binary dimension and finite field lists. Finite executable checks validate the supplied data; no selected-file census or successful ACTUAL-SIGMAS artifact run is claimed. Empty layouts are allowed by the layout module, but a successful selected-entry execution necessarily has an in-range entry.

Soundness is conditional on actual execution success. Completeness retains original whole-artifact and fragment parser equations, actual per-field decoding, full-layout equality/key policy and the restricted single-transvection/permutation Candidate check. Mere invertibility is insufficient for that restricted certificate class. No target operator equality is assumed.

The key order remains an explicit checked witness. The complete byte equality and unique hex key policy identify a restricted serializer position; they do not prove the installed parser's internal source spans or pre-collapse trace. File identity, digest authentication, general JSON round trips, runtime extern refinement, complex phases, physical charts/execution and costs remain separate.

## Sources and reuse

`PUBLIC_SOURCE_MANIFEST.json` pins exactly three new sources and twenty public prerequisites. Source files are hand-authored generic Lean modules, copied unchanged from accepted bytes. There is no generated table, omitted source-generation script or literal census. The derived values are produced by the executable definitions themselves: `decodeFields` obtains columns from actual named lookups; `fields` builds compact payloads; `prefixBytes` computes the selected offset. The prospective build recipe is in `REPRODUCTION.md` and does not claim a publication-time rerun.

The unit reuses [PR1978](https://github.com/CrocSwap/integer-mult-bounds/pull/1978) at `cfd9f916c2e3402cc1d65c63235f3f7241233b3c`, [PR1961](https://github.com/CrocSwap/integer-mult-bounds/pull/1961) at `3bb423ee93c8d8707b7b521e88132e3dfb5799fc`, and the exact earlier heads in the manifest. No prerequisite source is duplicated here. `OVERLAP.md` provides a bounded comparison, without claiming global novelty.

Credits: James Chang with OpenAI assistance; Lean/Mathlib authors; Jeremy Kothe T16/PR514; Rohan Arun PR1094; and the accepted strict-decoder, slice, compact-column and restricted-certificate components. Existing source attributions and Apache-2.0 notices are preserved.

Scoped later continuity: coordinator/integration observations at `e2e2b43cdb2085075c174c3ecb1cff8d2911aa20` match the same five critical scientific inputs. This package preserves its directly author-checked `299eb8ef` context; it does not claim an independent local read or full donor audit of that later revision.
