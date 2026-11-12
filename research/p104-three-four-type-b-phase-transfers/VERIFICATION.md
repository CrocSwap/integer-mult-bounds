# Verification and source pins

[PROVENANCE.json](PROVENANCE.json) binds the source commits, exact Git blobs
and SHA-256 values for the caller, price helpers and predecessor engines.
The exact caller's uncompressed bytes are SHA-256
`255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.
The preceding two-transfer price is a generated receipt pinned by #7323's
public hash manifest. The #7334 independent admission and full signed
invoice readback are included as immutable campaign receipts. The package
reproduces the new exclusions and uses that prior admitted comparator.

[LOCAL-PINS.json](LOCAL-PINS.json) pins the package inputs, engines and
receipt manifest by path. [receipts/SHA256.json](receipts/SHA256.json)
pins the deterministic plaintext outputs. Use `--out fresh-receipts`
to materialize `PRICE.json`, `KEYS.json`, `MODULAR.json`, `EXACT.json`
and `COMPARE.json` without prior temporary state or network access.

Both original science runners used CPython 3.12.14 with assertions.
The primary gate took 0.29 s and the independent exact gate took 0.49 s.
The independent moved-root gate took 0.42 s and reproduced its exact
receipt. Both were bounded by 35 runner seconds with 32 seconds
cooperative. The independent engine retains genuine cancellation controls
at four, six and eight clocks and compares mutated dense probes to literal
rational recurrence. The modular engine checks cancellation, a changed
reflection, and the required basis fallback after a passing dense probe.
The package rejects a caller with an added byte before reporting any
exact endpoint receipt.

No nonunit-body, full Laurent, changed native, compiler, precision, tape
or outer candidate replay was required after all keys failed the first
necessary gate. The five inherited assumptions and the selected record
are separate from the finite endpoint exclusion.
