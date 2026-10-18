# Publication preparation and receipt provenance

The scientific source baseline remains
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. The integration base checked during
publication preparation is `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`.
All 24 paths in `INPUT-PINS.json` have the same committed raw bytes at that
integration base and the pinned baseline; their decompressed payload pins also
match. The #626/R492 fixture was selected at the historical baseline. This
package makes no claim to replace or audit the current selected frontier.

## Receipt path normalization

An exact copy of all 65 original package files and a SHA-256 inventory were
preserved locally outside the repository before preparation. The public receipts
replace personal checkout-directory prefixes with `<REPOSITORY_ROOT>` and the
original external evidence-directory prefix with `<LOCAL_EVIDENCE_DIR>`.

Twenty execution-provenance fields in twelve JSON files were normalized:

- `cwd` in each of the nine per-case `COMMAND.json` receipts;
- each of the eight `/command/cwd` values in `SOURCE-REVERTS.json`;
- `/argv/2` and `/cwd` in `astra-run-command.json`;
- `/run_command_receipt` in `astra-receipt-review.json`.

The last reference names the original local receipt; its packaged copy is
[`evidence/astra-run-command.json`](evidence/astra-run-command.json).
[`evidence/PUBLICATION-NORMALIZATION.json`](evidence/PUBLICATION-NORMALIZATION.json)
records each affected JSON pointer and each file's original and published hash.
The original private prefixes are not included there.

All preexisting hash values inside receipts remain unchanged. In particular,
the historical `comparison` and `receipt_hashes` values in
`astra-receipt-review.json` identify the original raw execution receipts.
`MANIFEST.json` supplies hashes for the current published package. Neither
`run.py` nor `independent.py`, either input-pin inventory, source patches,
stdout/stderr, emitted artifacts, mathematical results, or timestamps were
changed by normalization. Generic temporary output paths and Python/platform
details are retained as execution provenance.

## Additional publication validation

After reviewing the harness, independent checker, pinned emitter and witness
loader, the publication reviewer executed:

```sh
python3 -B research/k492-emitter-independent-controls/run.py --out /tmp/k492-emitter-publication-review-20261013
```

On 2026-10-13, 19:14:22–19:15:01 UTC, CPython 3.13.2 completed with exit 0 in
38.96 seconds and printed `PASS_COMPLETE_EIGHT_EMITTER_SITE_SLICE`. Both verifier
source files retained their reviewed SHA-256 values. All 24 pinned input blobs
were then checked against the integration commit above and matched exactly.
The raw validation receipts remain outside the submitted package.

The complete baseline `HOSTED.json` equals the retained #626 receipt. Five source
controls fail at their required line and exception class, two emit artifacts
rejected by the independent geometry checks, and the changed-label control
passes. Eighteen semantic corruptions are rejected after digest refresh; the
cosmetic and actual recompression positive controls pass.

`BASELINE.json`, `RESULT.json`, `SEMANTIC-CONTROLS.json` and `INPUT-PINS.json` from
this additional run are byte-identical to the retained package receipts.
Every non-command field in `SOURCE-REVERTS.json` is identical. Its command fields
differ only in execution metadata: paths, timing and path-dependent stderr hashes.
The unchanged `RESULT.json` SHA-256 is
`2ece1e706252c810df6e8a73d09dd66ae6c9b2b940c83049a7c7767aec6856e9`.

This is an additional finite replay and publication check, not a new mathematical
claim, cold provider rebuild, full theorem audit or human peer review. The scope
limits and source attributions in `README.md` and `REVIEW.md` continue to apply.
