# Minimal source471 preparation and raw-ledger adapter

This focused adapter consumes the current public PR210 source and pinned base-bit files directly. It prepares the actual retimed helper context and recounts its physical paths. It does not run the all-column scalar proof, prime suite, five-stage global lowering, or outer assembly.

## Inputs

`SOURCE_PINS.json` lists 22 exact public files, including original licences and notices:

- eumemic/integer-mult-bounds at `df95878d11190518e45ef9717c9ee05011f88ace`
- CrocSwap/integer-mult-bounds at `8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d`

Supply those source roots with their original relative paths. The supplied `source_inputs/` contains just the listed files for this qualification. Normal pinned upstream checkouts can be used instead. No network access or implicit downloading is performed by the adapter. Python 3.11 or newer with assertions enabled is required; no third-party Python package is used by this focused loader.

## Targeted verification

From this directory:

    python3 -B test_public.py --pr210-root source_inputs/pr210 --base-bit-root source_inputs/base_bit

To print the prepared-source fingerprint:

    python3 -B source_loader.py --pr210-root source_inputs/pr210 --base-bit-root source_inputs/base_bit

To print the independently rebuilt raw ledger:

    python3 -B raw_ledger.py --pr210-root source_inputs/pr210 --base-bit-root source_inputs/base_bit

These commands do not alter inputs or write result files. Redirect output to a new external path if desired. The tests distinguish executable checks from the compact deterministic fixtures `expected_semantics.json` and `expected_ledger.json`.

## Programmatic interface

`source_loader.prepare(pr210_root, base_bit_root)` returns the source preparation namespace. It contains actual `W`, `C`, `schedule`, `borrow`, `terminal`, `regs`, `adj`, `at`, `kpair`, `deliveries`, selections and `SOURCE_TEXT` for the pinned scalar source. The payload replay function is deliberately not loaded or invoked.

The unmodified public joint candidate body is loaded with its base-bit root explicitly rebound. The unmodified current source471 preparation body is then executed, except for the source's historical input-list lines and terminal receipt lookup. Terminal records are reconstructed from pinned source root data and the pinned sink selectors. All input hashes are checked before importing source code.

`raw_ledger.reconstruct(context)` recounts internal, copied-center, original-source and target paths, including actual compensation and terminal chronology. It pays all copied-center calls and independent exterior completions. It neither reads nor rescales a packed historical profile.

The semantic fingerprint binds exact basis rows, original-source/root frames, operation frames, gauge order/read times, aliases, partner mix/delivery chains, retiming, terminal records, all borrowed and independent dirty roles, and target responses. Dynamically allocated frame numbers differ from older preparation code that registered unused historical frames; exact basis/chronology equality is the relevant comparison. No rank-only substitution is made.

## Qualification and exclusions

The one-time development comparison is `check_development_equivalence.py`. It intentionally loads the earlier audited preparation once to compare exact semantics. It is not a runtime dependency and is excluded from the minimal loader package. `equivalence_result.json`, `preparation_result.json`, `raw_ledger_result.json`, and test logs are qualification outputs, not proof inputs.

The minimal loader package consists of source_loader.py, raw_ledger.py, test_public.py, SOURCE_PINS.json, expected_semantics.json, expected_ledger.json, README.md, NOTICE.md, LICENSE and MANIFEST.json, plus the supplied source inputs or equivalent externally supplied pinned roots. Do not include historical search code, whole archived checkouts, or qualification receipts in that runtime closure.

A successful focused run establishes only the preparation/ledger scope above. A complete portable five-stage candidate still needs its global lowering, mathematical witness coverage, finite bills, conditional contract binding and exact assembly connected to these actual source objects.

Assisted with ChatGPT.
