# Portable exact arithmetic

Python 3 standard library only. No producer, external service, dependency install or upstream baseline execution is required. Keep this directory layout and filenames intact.

Generate the deterministic mathematical certificate from the selected complete profile and paid scalar bill:

```sh
python3 certificate.py --profile PATH/complex-profile.json --scalar-bill PATH/READOUT_COST.json --certificate PATH/certificate.json --record
```

Verify exact regeneration by omitting `--record`. The generator checks the copied upstream sources against SHA256 and Git blob pins, canonicalizes the supplied mathematical profile, rejects floats recursively, recomputes both rational moment enclosures, all 47 inequalities, seven margins, three row stocks, semantic constants, cutoffs and the fixed-profile next-grid exclusion. It also recomputes the stopped coarse-bit supplier with both enclosures.

Run the source-adaptation and selected mutation checks:

```sh
python3 validate.py --certificate PATH/certificate.json --receipt PATH/validation.json
```

For the independent prepackage witness, add `--reference-certificate PATH/independent-prepackage-certificate.json`. The validator compares all controlling mathematical fields, including both full moment records, the complete assembly and cutoffs. Its receipt is deterministic and float-free. Normal Python assertion execution is required; optimized mode is rejected.

`references/pr100/refine.py` is a pinned source document. Only its three exact arithmetic function bodies are selected through AST; its application and foreign producer entry points are never imported or executed. `REFERENCE_PINS.json` retains original repositories, commits, file paths and Git blobs. The full original notices remain in copied source files.

Raw discovery timings and source metadata are excluded from the mathematical certificate. Only the raw profile/bill SHA256 values enter it. Retain physical generation, both-orientation scalar/frame audits, proofs, Lean input/source/compiler receipts, raw metadata, and their source manifest separately. This arithmetic layer does not replace those obligations or claim a global optimum or practical speedup.
