# Skip zero row updates in the exact cyclic-inverse replay

This optional adapter speeds up Ali Romman's incorporated PR621 verifier by
skipping elimination updates whose coefficient is exactly zero. The full
eight-case output remains byte-identical to the predecessor's `EXPECTED.json`.
This is a tooling improvement with no new kappa or mathematical construction.

The only arithmetic change is in `eliminate`, immediately after reading the
coefficient for a non-pivot row:

```python
value = a[row][col]
if value == k.zero:
    continue
```

The original implementation and all its callers remain unchanged on disk.
`replay.py` checks the predecessor's SHA256 and exactly one insertion site,
then applies these two statements in memory before running the original CLI.
The historical review binds the original source bytes, so editing that package
would invalidate its provenance. Default repository verification is unchanged.

## Reproduce

Use Python 3.11 or later and the standard library. The benchmark uses POSIX
child CPU accounting and supports macOS and Linux.

```sh
python3 -I -B research/cyclic-zero-elimination/verify.py --output /tmp/cyclic-zero-result.json
```

Use a fresh output path. Expected terminal result:
`PASS_CYCLIC_ZERO_ELIMINATION`. The JSON records all fourteen full replay
timings, source hashes, interpreter, platform, and control results. Every
replay must match the pinned predecessor receipt before its timing is accepted.
There is no machine-dependent speed threshold in the correctness checks.

To run just the faster replay, including all inherited checks:

```sh
python3 -I -B research/cyclic-zero-elimination/replay.py --output /tmp/cyclic-fast.json
```

The output must match `research/prime-power-cyclic-inverse/EXPECTED.json`
byte for byte. Both entrypoints retain their checks under `-O`.

## Why the guard preserves the check

`Field` represents each element as a fixed-length tuple of exact rational
coefficients reduced modulo the cyclotomic polynomial. Equality with `k.zero`
is exact. For a zero elimination coefficient, every omitted operation has
the form `a[row][j] = a[row][j] - 0 * a[col][j]`. If a boundary is present,
its omitted update is `b[row] = b[row] - 0 * b[col]`. Each leaves its value
unchanged. The skipped block contains no validation or inversion.

The guard leaves pivot search, row swaps and their determinant sign, pivot
inversion, nonzero elimination, singular detection, and solution checks in
place. Both original callers run: the Sylvester system with its Bezout
boundary and the singular unit-root control without a boundary.

No input cases or series terms are removed. All eight shipped cases still
check tail products, integral coefficients, residue identities, determinant,
Bezout identity, norm, and conjugate-reversal squared moduli. Each retains its
unit-root and missing-conjugation negative controls. These are finite checks,
not a formal proof of the all-prime-power theorem or integer multiplication.

## Evidence

Seven pairs run sequentially in alternating order. Each member is a fresh
isolated Python process on the same eight inputs. The guarded timing includes
loading, hashing, and compiling the adapter. Within each recorded series,
no priming run or timing sample is discarded. Times include the entire process,
not just elimination.

| Local interpreter | Reference wall median | Guarded wall median | Reference CPU median | Guarded CPU median |
| --- | ---: | ---: | ---: | ---: |
| CPython 3.13.16 | 3.709 s | 3.156 s | 3.149 s | 2.374 s |
| CPython 3.14.8 | 4.205 s | 2.649 s | 3.212 s | 2.371 s |

Both runs were on macOS 26.5.2, arm64. Child CPU medians fell by 24.6% and
26.2%, respectively. Wall time is noisier: one Python 3.14 pair was slower
with the guard. No universal speedup or complete frontier replay speedup is
claimed. Raw samples are retained in [RESULT-python313.json](RESULT-python313.json)
and [RESULT-python314.json](RESULT-python314.json).

Before these series, a baseline-only smoke run took 2.7844 seconds. A separate
feasibility pair using `python -c` measured 3.2008 seconds before the guard and
2.8955 seconds after it, with identical receipts. Those preliminary runs use
different launch conditions and are not included in the table's medians.

The focused checks cover 36 matrix/mode combinations at orders 3, 4, and 5.
They include sparse, dense, row-swapped, and singular matrices, non-rational
entries, both boundary modes, direct determinant formulas, direct substitution
of solutions, and input preservation. Seed 94 selects the extra boundary
`(zeta_q^94, 94)`. The identity solve uses 12 field multiplications before the
guard and 7 after it, so disabling the guard fails the work-reduction check.
Changing the source bytes is rejected. Inverting the guard or skipping all
rows makes the inherited identity check fail.

All 28 measured full replays matched the expected receipt. Additional isolated,
optimized runs from `/tmp` matched on Python 3.11 and 3.14. A separate Codex
agent reviewed the change and ran the 36 focused checks under optimized Python.
This is AI-assisted review, not independent human review.

The original source, expected receipt, selected frontier, and `upstream/` are
unchanged. The full `make verify`, cold frontier replay, and optional SymPy
engine were not rerun for this adapter. The affected standard-library replay
was run in full; no production integration is claimed.

## Pins, attribution, and scope

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCE.json](SOURCE.json) pins the PR621 source and exact receipt. The original
package's [notice](../prime-power-cyclic-inverse/NOTICE.md) and
[source record](../prime-power-cyclic-inverse/SOURCE.json) retain its kernel,
proof, and classical-source attribution. The algebra and verifier are Ali
Romman's predecessor work. The only proposed arithmetic change is the guard.

Scott Woolsey Biggart's pending PR668 uses CRT and a different implementation
to extend resultant coverage through order 27. It is related work, not a
dependency or duplicated search. This contribution keeps the predecessor's
eight-case domain and rational-field method. It does not settle efficient
preparation, rounding, restoration, fixed-tape implementation, or the inherited
analytic interfaces.

Adapter and experiment contributed by [thakrarsagar](https://github.com/thakrarsagar)
with substantial OpenAI Codex assistance, including a separate AI review.
Licensed under the repository's Apache-2.0 license.
