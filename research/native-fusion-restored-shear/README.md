# A completed shear boundary for the native fused BIT query

Research note and exact verification; **no new κ**.

For the unipotent ADDRESS permutation `h` in Karl Appel / applecrusher's
PR #521, this packet completes the DATA shear
`(x,y,z) -> (x XOR y XOR h(y), y, z)` under three explicit workspace contracts:

| Implementation | Recursive children | Persistent full private rows | Workspace endpoint |
|---|---:|---:|---|
| Query the DATA target | 2 | 0 | Every unrelated dirty row preserved |
| Query only private storage with triangular XOR charts | 4 | 1 | Arbitrary private contents restored |
| Owned disposable storage, with paid copy and clear | 1 | 1 | Private row returned to zero |

Each query has one ordinary ADDRESS-interchange child and six paid affine
events. The first program uses two XOR scans; the second five; the third
two XOR scans, one source-copy scan and one clear. Evaluator scratch,
complete spectators, routing, coefficient preparation and head returns
remain charged in the [typed cost recurrences](PROOF.md#6-complete-typed-costs-and-workspace).

The two-query minimum is proved in the fixed-`h`, arbitrary-dirty-row XOR
model. The four-query minimum has the narrower private-only restriction.
Neither lower bound covers arbitrary alternate ADDRESS primitives.
The one-query implementation relies on ownership that permits overwriting
the private input; it is not a dirty-restoration implementation.

Run from the repository root, with Python 3.10+ and no installed packages:

```sh
python3 -I -B research/native-fusion-restored-shear/check.py --check
```

Expected first line: `PASS_RESTORED_SHEAR_INTERFACES`. The next lines give
the exact enumeration and control counts. The checker reads local packet
files and writes nothing with `--check`.
For focused checks use, for example, `--check -k endpoints`.
To intentionally regenerate the evidence use `--write-results`.

The [proof](PROOF.md) includes the full two-query factorization
classification, the private-only restriction, literal programs, and every
local recursive child. The replay covers 60,880 signed projector pairs,
4,681 native-chart words, exact rational ADDRESS identities, and dirty BIT
columns on full/shorter prime-power orbits. This is not a formal verification
of the multiplication theorem or a cold replay of the selected supplier.
An independently implemented sparse-set replay also covers every address
in `(Z/3)^6`, with 2,916 basis inputs per program and 17,496 endpoint/inverse
cases. It is included in the same command.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`; assignment seed **57**,
recursive-interfaces track. The base selected conditional κ remains
`51110230636731/31250000000000000`; the selected certificate and `upstream/`
are unchanged. All work is isolated to this directory.

The new value is a completed resource/endpoint comparison and a sharp scoped
query classification. The ADDRESS lowering and unfinished-module identity
come from [PR #521](https://github.com/CrocSwap/integer-mult-bounds/pull/521)
at `a190fdb39f31647fc6f651625353710624627348`, which was unreviewed in the base
ledger. The algebra uses predecessor scalar-projector methods, credited in
[NOTICE.md](NOTICE.md). This work does not approve the rest of that PR.
Source URLs and SHA-256 pins are in [SOURCES.json](SOURCES.json).

Open obligations: place a completed shear inside an actual supplier,
authorize its DATA query or disposable storage, price the resulting whole
profile, handle arbitrary widths, and discharge the inherited all-size and
tape interfaces. No saving is inferred merely from the local counts.

Submitted by @commdata2338 with substantial AI assistance (OpenAI Codex,
GPT-6-Astra; packaged with Claude Code); no independent human review is
claimed.
