# Exact Gram prefix reuse

This optional adapter reuses exact leading principal determinants in the selected R420 bit Gram checker.
The checker first asks for a full determinant, then for each leading principal determinant.
One Bareiss pass supplies those values.
A zero pivot invokes the original pivoted determinant on the full matrix.

**Status: tooling improvement; no new kappa.**
The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected conditional result at that base is `0.001635527380375392`.
This contribution preserves the selected certificate, frozen sources, default commands, and `upstream/`.

## Reproduce

Use Python 3.11 or newer and a full repository checkout.
All dependencies belong to the Python standard library.
The benchmark uses the POSIX `resource` module on macOS or Linux.
No network connection is required.

```sh
python3 -B research/gram-prefix-performance/verify.py
python3 -B research/gram-prefix-performance/test_kernel.py --mutations
python3 -B research/gram-prefix-performance/benchmark.py --pairs 31 --out /tmp/gram-prefix-result.json
```

Use a fresh benchmark output path.
Expected results: 23 passing tests, four detected kernel mutations, and `PASS_GRAM_PREFIX_BENCHMARK`.
The first command prints `PASS_GRAM_PREFIX_VERIFICATION`.
The mutation command reports the passing baseline before the four rejected mutations.

Run either complete checker directly with the same pinned frame fixture:

```sh
python3 -B research/gram-prefix-performance/adapter.py --engine reference
python3 -B research/gram-prefix-performance/adapter.py --engine prefix
python3 -B research/gram-prefix-performance/adapter.py --engine compare --trace --out /tmp/gram-prefix-trace.json
```

All three print:

```text
PASS e8ham Gram: 672 frames checked, all nondegenerate and positive definite; prime witnesses valid; max determinant bits 17; primes [2]; by dim {0: 1, 1: 120, 2: 180, 4: 70, 6: 180, 7: 120, 8: 1}
```

## Exact coverage

The adapter checks source hashes before execution.
It inserts one assignment after the pinned checker imports `prime_witnesses.py`.
That assignment replaces only `pw.det`.
The checker retains every frame, rank, annihilator, prime-witness, residual, and positivity check.
The reference mode uses the original determinant.
The comparison mode compares every requested determinant with that original.

All 3,360 determinant requests on the selected frames agree exactly.
Their ordered matrix/value transcript has SHA-256:

```text
441d68e330a1b8b159fd914ceb2eab302d38eb50c87147ce62a513a02796dbef
```

The fixture contains all 672 exported frames, including frame zero.
The verification command regenerates it from the pinned R420 word through the original exporter.
It compares the full uncompressed payload byte for byte.
Compressed container bytes do not determine mathematical equality.
`SOURCE.json` binds the word, exporter, checker, determinant source, and fixture payload.

The kernel suite includes an independent permutation determinant oracle through dimension five.
It exhausts 530 binary matrices of dimensions one through three.
Seed 88 also gives 240 small signed matrices, 108 positive Gram matrices, and 144 larger matrices through dimension sixteen.
Larger cases use the original determinant and independent determinant identities.
Named cases cover negative pivots, singular leading blocks, singular matrices, large integers, and mutable inputs.

The four kernel mutations corrupt signs, cached minor values, cache keys, or zero-pivot handling.
Each mutation causes assertion failures, without execution errors.
Package controls reject altered dimensions, dependent bases, wrong annihilators, oversized prime residuals, singular Gram matrices, and failed positivity.
The tested rejection arguments agree across all three engines.
Source tampering, disabled checker assertions, and existing output paths also fail.
The retained `--new` frame filter produces matching results in all engines.

[PROOF.md](PROOF.md) gives the integer identity and cache argument.
The proof assumes an exact reference determinant for the fallback.
Finite tests corroborate the implementation; they are not a formal proof of the multiplication theorem.

## Measurements

Each evidence file records 31 alternating fresh-process pairs.
The first runs measure wall time only.
The follow-up runs also measure child user and system CPU time.
Both sets remain in `evidence/`; no samples are removed.
Both engines receive identical exported frames.
Every measured complete process must produce the same output.
Each separate determinant batch follows the actual 3,360 requests captured from the checker.
Every measured batch compares its full result list with the original afterward.
A fresh kernel starts each batch, so no previous batch supplies cached results.

| Python | Run | Full process wall, reference → prefix | Child CPU, reference → prefix | Determinant batch, reference → prefix |
|---|---|---:|---:|---:|
| 3.13 | First | 113.79 → 115.15 ms | Not collected | 19.49 → 9.69 ms (2.01×) |
| 3.13 | CPU follow-up | 161.59 → 148.07 ms | 150.98 → 138.00 ms | 21.61 → 11.11 ms (1.94×) |
| 3.14 | First | 206.13 → 246.14 ms | Not collected | 18.83 → 10.16 ms (1.85×) |
| 3.14 | CPU follow-up | 142.55 → 147.88 ms | 135.07 → 138.29 ms | 15.31 → 8.30 ms (1.84×) |

The determinant batches improve consistently.
Complete-process wall results vary in direction, so no reliable end-to-end wall speedup is claimed.

Complete process timings include adapter startup and source/fixture validation.
The determinant batches exclude imports, input collection, and result comparison.
Filesystem caches are not flushed.
Other applications can affect local timings; these are paired medians, not guaranteed speedups.
The benchmark has no timing threshold and retains every sample.
`wall-only-benchmark.py.txt` preserves the first measurement script.
Its hash matches the earlier receipts; the current script matches the CPU receipts.

These measurements do not include word construction, record export, full supplier replay, or integer multiplication.
No full-frontier speedup follows from this small stage measurement.

## Review map and limits

- `kernel.py`: exact determinant implementation with a bounded prefix cache.
- `adapter.py`: source-pinned execution of the retained checker.
- `test_kernel.py`: independent arithmetic tests and kernel mutations.
- `test_package.py`: full-frame reproduction, equivalence, and package controls.
- `benchmark.py`: reproducible paired measurements with source hashes.
- `evidence/`: raw local measurements and validation receipts.
- `CLAIM.md`: assignment, candidates, and overlap check.
- `NOTICE.md`: predecessor attribution, license, and AI disclosure.

The cache stores at most one requested matrix's leading prefixes.
It uses exact immutable matrix values and does not retain successful checker results.
The public kernel accepts square matrices of built-in integers.
It does not support arbitrary scalar types or concurrent calls on one instance.
The adapter rejects optimized Python because the retained checker uses assertions.
The kernel's arithmetic guards remain active under optimized Python.

The local checks cover only this optional adapter and the pinned Gram stage.
The full `make verify`, supplier cold replay, assembly, and Lean checks are not rerun for this addition.
Dedicated Linux CI is supplied; its remote status remains separate from local results.
All inherited compiler, hosting, precision, tape, and analytic assumptions remain.
Direct activation in a frozen production package requires separate integration and affected source-pin updates.
