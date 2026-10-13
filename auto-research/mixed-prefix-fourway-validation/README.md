# Four-provider cold replay evidence

The frozen source manifest is `6a804eb28134da69813960e231ae9609d6786b3452d46f8936d03766a2dc2407`.

| Environment | Full cold time | Top-level stages | Result |
|---|---:|---:|---|
| macOS arm64, Python 3.14.8, zlib 1.2.12 | 541.075 s | 30 | PASS |
| Linux aarch64, Python 3.12.3, zlib 1.3 | 607.330 s | 30 | PASS |

Each run starts from an absent output directory and rebuilds the complete
pinned PR572/PR568 dependency chain before the new providers and whole-owner
allocation. No retained provider proof outputs are reused in either final run.
The result is `kappa=0.001600848528154892`; both `RESULT.json` files are
byte-identical with SHA-256 `eaa75361679536e5b68ea72a7a91e0f8e4dcf1a900d545d346d99ca6089a79e9`.

`CROSS-PLATFORM.json` compares all seven proof-content identities for each
of the four providers and every numerical/semantic invoice field. It names
the raw-reference fields omitted from the invoice comparison. Those references
are validated against actual files during each run. Compressed containers,
timings, absolute paths and derived raw-reference hashes are environment-specific.

Both environments retain root and nested receipt chains, named proof artifacts,
logs, local omission and phase checks, owner/invoice audits and all admission
controls. Every run passes 16 owner mutations, 109 assembly mutations, four
phase timing accept/reject pairs, four actual recompressions, 36 proof-content
mutations and 36 reference/metadata mutations. Source files are unchanged after
execution; `SOURCE-VALIDATION.json` records all 273 original Git-blob comparisons.
GitHub CI is a separate execution and is not implied by these receipts.

## Preliminary correction

The initial v1 run on each platform completed the pinned parent replay but
failed at a root packaging path: it looked for `PROMOTION.json` in
`eight-cold-word` instead of `eight-multicold-word`. The corrected source receipt
is byte-identical to the earlier PR569 receipt. No mathematical check failed.
A diagnostic continuation with the completed Mac parent then passed all
remaining stages; it is identified as retained-parent evidence, not a cold run.
V2 fixes both receipt paths and explicitly rejects optimized Python before
creating output. Both final full runs above were restarted from absent output
directories. The mathematical construction, owner allocation and rate did not
change. The v1 source inventory, failed Mac log and diagnostic log are retained
in `preliminary/`.

## Repository baseline

The unchanged baseline is `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`.
`BASELINE-REUSE.json` identifies byte-identical evidence already published in
PR572 at `0c3a7d1b0d99dbc6a1cc5ec1675ddd74aa959586`. All 18 top-level `make verify`
groups passed across its initial and resumed runs, including `gen4-bank-verify`.
The first invocation passed twelve groups, then exited 2 because Apple clang
rejected `-fopenmp`. After validating a run-owned libomp compiler wrapper with
four workers, the failed group and five remaining groups passed. No source or
assertion changed. This is reused baseline evidence, not a new aggregate run.

The construction remains conditional on the assumptions listed in the source
README and PROOF. These receipts establish finite admission, not a complete
multiplication theorem, a practical speedup, or kappa = 1.

The full diff has nine trailing-blank-line warnings, all confined to pinned
vendored sources. Newly authored code, workflow and validation documentation
pass the whitespace check; original vendored bytes remain intact.
