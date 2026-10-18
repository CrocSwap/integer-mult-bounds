# Exact packed verification of the historical dyadic central factor

This opt-in tooling contribution checks the same **6,760,000 integer product
entries** as `scripts/experiments/complex_centers.py::verify_factor` at h=26.
It packs complete coefficient rows into exact Python integers. The original
structural checks, scalar-charge checks, and returned receipt are retained.
The complete historical audit is also rerun and compared byte for byte with
`certificates/dyadic-central-factor.json`, including the unchanged side circuit,
phase/frame checks, restoration interfaces, operation invoice and rational
inequalities. Default verifiers and all existing files remain unchanged.

**Tooling improvement; no new kappa or construction.** The selected conditional
result at base `47481c89fd30a43f8f882eb4b391e89c29273fd0` is PR890's
`1661957774647029/10^18`. The older `2^-31` and `3.6e-8` strings in the reproduced
receipt describe its historical checkpoint, not the accepted frontier.

Three alternating fresh-process pairs on macOS arm64 / Python 3.14.6 measured
median complete-audit wall time **5.629786 s → 3.489217 s (1.613481×)**.
Factor-only runs, including source admission, factor generation and receipt
comparison, measured **2.185536 s → 0.119217 s (18.332397×)**. Each engine used
the same pinned input in a new interpreter. These are local descriptive
measurements, not a runtime guarantee or a speed threshold; raw samples and
implementation hashes are in `BENCHMARK.json`. Preliminary timings during
orientation are excluded.

## Reproduce

From the repository root, with Python 3.11+ and its standard library:

```sh
python3 -I -B research/central-factor-packed/verify.py
```

Expected: `status` is `PASS_CENTRAL_FACTOR_PACKED`, scope is
`complete_historical_audit`, `coefficients_checked` is `6760000`, and
`receipt_sha256` is
`ffae0f0a22863718e3134a924592dcf4b05e919223323ba536c587c592bfe6a1`.
The printed duration varies. This receipt is byte-identical to the original
full audit; the benchmark/result wrapper is a new, explicitly separate record.

```sh
python3 -I -B research/central-factor-packed/test_packed.py
python3 -I -O -B research/central-factor-packed/test_packed.py
python3 -I -B research/central-factor-packed/verify.py --engine baseline
python3 -I -B research/central-factor-packed/benchmark.py --pairs 3 \
  --output /tmp/central-factor-benchmark.json
```

Use a fresh output path. Full audit replay deliberately rejects `-O`, since
some inherited side/phase assertions require it to be absent. The packed
verifier and its differential tests use explicit failure checks and are also
tested under `-O`. `--factor-only` restricts a timing run to factor generation,
factor verification and receipt comparison; it is not a complete audit.

## Why the packing checks every coefficient

The supplied sparse gather column for triple T is v(T). The validator requires
each coordinate at most once, with weight -1 or +1. The supplied scatter row
u(S) consists of h exact integers. For all S,T the obligation is

```
a(S,T) = sum_i u(S)[i] v(T)[i] = |S intersect T| - 1 = e(S,T).
```

Let `M = max_S sum_i abs(u(S)[i])`, using 0 for an empty family. Then
`abs(a(S,T)) <= M`; since S and T are triples, `abs(e(S,T)) <= 2`.
Choose `b = (M+2).bit_length()` and `B = 2**b`. Thus

```
abs(a(S,T) - e(S,T)) <= M+2 < B.
```

Number all triples T_j in their original order. The verifier constructs

```
V_i = sum_j v(T_j)[i] B**j
I_i = sum_{j: i in T_j} B**j
O   = sum_j B**j
```

and compares `sum_i u(S)[i] V_i` with `sum_{i in S} I_i - O` for **every** S.
Both are exact signed integers. Their difference is
`sum_j d_j B**j` with `abs(d_j) < B`. If this sum is zero, reduction modulo B
implies `d_0 = 0`; dividing by B and repeating proves every `d_j = 0`.
Conversely, coefficient equality plainly gives packed equality. This is an
injective encoding on the possible difference vectors, not a probabilistic
fingerprint. Signed digits need not be normalized or extracted.

The radix comes from the *supplied* scatter rows, including invalid large
weights; it does not assume that the scalar-charge check will later pass.
The expected row comes solely from the triple incidence relation. The actual
row uses every supplied factor entry; it does not assume the generator's
formula, a particular basis, or any source symmetry. At h=26 the published
factor needs five bits per position. No machine-word overflow is possible.

The bounded-radix argument is a written mathematical argument. Neither it nor
the finite tests is a formal proof of the complete multiplication theorem.

## Coverage and negative controls

- Complete original-verifier comparisons at h=8,10,12,18,26, plus the original
  verifier's empty small domains. Equivalent coordinate permutations, sparse
  term orderings and sign changes are accepted.
- All **1,344** allowed single scatter-entry replacements at h=8; every one
  of its **231** sparse gather terms sign-flipped and separately deleted:
  **1,806** rejected corrupt factors, with the original rejection reason.
- Seed-93 cases with signed magnitudes from the `2**2` through `2**199` domain,
  first/last positions,
  malformed dimensions/types, duplicated/out-of-range coordinates, and a
  correct product with an inadmissible scalar charge.
- A swapped-column factor has unchanged row sums. It passes a deliberately
  faulty radix-1 kernel and is rejected by the proper radix, demonstrating
  sensitivity to an information-losing optimization.
- Original four central-factor/dirty-interface tests run against each engine.
  Source, adapter, fixture, upstream, missing-file, incomplete-receipt,
  optimized-replay and existing-output controls fail explicitly. No verifier
  input is mutated or acceptance cached.

The test domain is finite and recorded; no search or impossibility theorem is
claimed. The experiment stops after the listed cases and three alternating
fresh-process benchmark pairs for each scope.

## Pins, integration and limitations

`SOURCES.json` pins 43 inherited source, test, proof, fixture and upstream files
to the exact base, plus the adapter implementation. All inherited pins were
compared with that base's Git blobs. It includes the original upstream commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Source admission happens before
imports; the replay also rejects an unlisted imported repository script.

The adapter replaces only the `verify_factor` reference inside the historical
audit for the duration of that invocation, then restores it. No certificate is
regenerated in place. Source pins and the complete expected receipt must be
updated deliberately if a maintainer wants to support a changed source.
These files establish reproducibility and content binding, not proof that
some third party executed the checks or trust in a maliciously rewritten
manifest and program.

This package does not accelerate the PR890 supplier/controller replay, change
the selected frontier, or discharge its all-size/compiler, common-label,
mutable-source, hosting, precision/tape, analytic or bit H1-H5 assumptions.
The full repository suite and selected cold replay are outside this isolated
historical adapter's measured coverage. See `VALIDATION.md` and `BENCHMARK.json`
for actual verification and timings, `CLAIM.md` for selection/overlap, and
`NOTICE.md` for source and technique credit.
