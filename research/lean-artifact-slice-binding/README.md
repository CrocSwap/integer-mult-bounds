# Checked artifact slices and named compact columns

This package contributes two unchanged, independently checked Lean 4.21 modules.

- `CheckedArraySlice` checks an entire in-range interval and exact ordered array equality. It derives every original-position element and prefix/fragment/suffix decomposition. The ByteArray specialization preserves empty fragments and endpoints.
- `LocatedCompactEntry` checks a supplied fragment at a supplied offset, parses the same original artifact, and runs the accepted compact fragment/named-dictionary recovery checker. Success derives both parser computations, named column equality, exact compact bytes and the independent column operator with both inverse laws.

A substring occurrence plus named-value equality does not identify the parser's structural field span. Whole-file provenance, digest authentication, parser specification and duplicate-key policy, physical execution and costs remain separate. Restricted completeness keeps the explicit parser/slice/checked-Candidate premises shown in `ACCEPTANCE.json`.

These are generic soundness results. There is no new selected finite census, concrete witness execution, full multiplication theorem or production precision change. The 18 immutable public prerequisites are reused without copying; the complete 20-module order is in `PUBLIC_SOURCE_MANIFEST.json`. Unused ASCII, byte-recovery, complete-object-layout and selected-instance modules are excluded.

Author-checked source context at `feb4dd177862175ea61e27f1cda7c6d124d39b55`: kappa = **836330098538459/500000000000000000 = 0.001672660197076918**. The selected-result source is linked and hashed in the manifest. These generic theorems do not use or change kappa.

`ACCEPTANCE.json` records all 11 clean axiom probes, four complete printed types, warning status and review role. `REPRODUCTION.md` gives a source-hash-checked build in fresh scratch using exact public dependencies. It does not rely on private binaries or receipt files.

Attribution: Lean/Mathlib and Array/List authors; Jeremy Kothe T16/PR514; Rohan Arun PR1094; accepted bank/frame byte, slice, compact and recovery components. James Chang with OpenAI assistance. Apache-2.0.
