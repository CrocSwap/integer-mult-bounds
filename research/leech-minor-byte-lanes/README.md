# Exact byte lanes for historical Leech minors

**Verification tooling; no new kappa or new negative result.** This opt-in
adapter accelerates the five Leech minors in the historical affine-vector
audit. It reconstructs every recorded matrix entry and retains the original
Golay inventory, vector norms, rational spans, exact binary elimination,
admission checks and nine-screen certificate. The other four polynomial-code
screens run unchanged. The original checker and its default command remain
available.

Reproduce with standard-library Python 3.11+ from the repository:

```sh
python3 -I -B research/leech-minor-byte-lanes/verify.py
python3 -I -B research/leech-minor-byte-lanes/test_lanes.py -v
```

The first command compares **5,927 complete rows / 7,531,037 matrix entries**
against the pinned pairwise implementation, compares both full certificates
byte for byte with the committed certificate, and checks `EXPECTED.json`.
Its final line is:

```text
PASS_LEECH_BYTE_LANES all_frozen_rows_equal=true cases=5
```

To use just the accelerator, provide a fresh output path:

```sh
python3 -I -B research/leech-minor-byte-lanes/replay.py --output /tmp/leech-certificate.json
```

The output is the complete original certificate; the stdout receipt explicitly
identifies the executed geometry source. The certificate's original source
hashes still refer to the unchanged files on disk. They do **not** identify the
adapter: `EXPECTED.json` pins the transformed geometry, while `BENCHMARK.json`
records hashes of the adapter, wrapper, benchmark and input pin manifest.
Neither entry point overwrites an existing output file. Optimized Python is
rejected so no inherited assertion can be disabled.

## Exact arithmetic

Let columns be vectors `v_j` with coordinates in `[-4,4]`. For each coordinate
`k`, pack two nonnegative base-256 integers, with column `j` in byte `j`:

```
P_k = sum_j (v_j[k] + 4) 256^j
M_k = sum_j (4 - v_j[k]) 256^j
```

For a row vector `u`, calculate

```
S_u = sum_(u[k]>0) u[k] P_k + sum_(u[k]<0) (-u[k]) M_k.
```

Byte `j` is exactly `dot(u,v_j) + 4 ||u||_1`. Every summand is nonnegative and
the final byte is at most `8 ||u||_1`. The adapter admits only `||u||_1 <= 31`,
giving a bound of 248, strictly below 256; every partial sum also fits. There
are no carries between columns and no signed borrowing. Original Leech rows
have l1 norms 8, 16 or 26, so this bound includes every allowed historical row.

The adapter decodes all bytes, compares each with `shift + 4 ||u||_1`, and
explicitly includes the diagonal. Thus it returns precisely
`C[i,j] = (i == j or dot(v_i,v_j) == shift)`, in the original column order.
No floating-point arithmetic, modular-rank surrogate, sampled comparison,
zero-byte bit trick or omitted row is used. Invalid lane domains fail before
packing. The extra packed coordinate arrays occupy approximately `48 * m`
bytes of integer payload for an `m`-column, 24-coordinate sample, plus Python
object overhead; the existing vector inventory and binary rows are retained.

## Source admission and coverage

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. `PINS.json` records SHA256
for all 41 consumed predecessor sources, fixtures, expected certificate,
original tests, historical note and retained upstream inputs. The geometry
source has SHA256
`756778eeca27f490adc7354a122dc50c40375156259991469c47a90949118ea1`.
The wrapper checks the pins before importing the audit. It requires one exact
match for the old row-construction block and replaces only that block in a
separate namespace. The original functions outside that block and all caller
checks remain. The alternative cannot silently activate after source drift.

| Shift | Signed family | Rows | Columns |
| ---: | :---: | ---: | ---: |
| 0 | no | 683 | 715 |
| -16 | yes | 1,311 | 1,343 |
| -8 | yes | 1,311 | 1,343 |
| 8 | yes | 1,311 | 1,343 |
| 16 | yes | 1,311 | 1,343 |

All row hashes remain unchanged. The full certificate SHA256 is
`f72787ebf4a991e32705c7fb7ef7ad559a9964b27c0f91d1b5a034c05027cfb0`.

Supplemental controls use assignment seed **86** and cover all 81 two-coordinate
vectors in `[-4,4]^2` for every integer shift from -32 through 32; 192 shuffled
signed Leech vectors from all three generator families at seven shifts; zero
lanes, the maximum admitted lane, and mandatory diagonals. Controls detect
wrong signs, wrong shifts, omitted diagonals, reversed columns, dependent
rows, faulty-kernel output, invalid inputs, changed or missing pinned files,
incomplete receipts, disabled assertions and attempted output reuse. Column
reversal demonstrates why a matching rank alone is insufficient. The three
unchanged predecessor tests are also run against both implementations.

## Benchmark

Run the same complete nine-screen audit in alternating fresh processes:

```sh
python3 -I -B research/leech-minor-byte-lanes/benchmark.py --rounds 3 --output /tmp/leech-benchmark.json
```

Every timed process includes interpreter startup, imports, source admission,
all nine witnesses and their checks, exact complete-certificate comparison and
output. The runner checks every resulting file again. Timing is descriptive;
no speed threshold controls mathematical acceptance. Raw measurements and
the tested adapter hashes are retained in `BENCHMARK.json`.

The initial instrumented profile attributed 42.3 of 49.7 seconds to Leech
minor replay. Instrumented figures are diagnostic, not benchmark samples. A
preliminary timing run overlapped supplemental testing and is excluded from
the retained comparison. See `VALIDATION.md` for final measurements and limits.

## Mathematical scope and credit

These are the same five specified central matrices rejected by Douglas R.
Colkitt's historical audit, and the same four polynomial-code screens. The
rank lower bounds rule out positive deficit only for those stated full
relations in the historical compiler. This does not reopen the search,
exclude arbitrary supported matrices or subfamilies, improve a supplier, or
raise the selected conditional kappa. The selected #799/#589 result remains
0.001661634653669567 with its inherited all-size, realization, hosting,
precision/tape and analytic assumptions. This is finite verification, not a
formal proof of the multiplication theorem.

Credit and immutable predecessor pins are in `NOTICE.md`; selection and overlap
checks are in `CLAIM.md`. The technique follows the related integer-lane idea
of Curtis Dransfield's #752, here applied to signed real Leech minors with
direct byte decoding. No pending PR code is imported. This package is by
Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance, under
Apache-2.0. No independent human review is claimed.
