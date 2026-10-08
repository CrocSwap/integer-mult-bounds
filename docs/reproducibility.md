# Reproducing the current result

Run from the repository root with Python 3.11+, a C++17 compiler, Git, and Make.
No third-party Python package or network access is required for verification.
The inherited full h28 support check uses about 1.2 GB of memory.

```sh
make verify
```

This retains the #10 checks and additionally regenerates the selected
`(25,23,57)` scalar graphs, original carrier dependencies, positive labels,
final carrier matches and full rank histograms. The complex h28 histogram is
reconstructed from its retained producer. The new rational certificate
rebuilds the recursive width multiset, checks both moments and the precision
guard, and evaluates all 29 strict constraints and seven assembly margins.
Basis checks cover the prescribed coordinate compatibility and both A5 trees.
The remaining generic-minor and interface arguments are in the proof.

All large intermediate graph and label files are temporary. To retain them:

```sh
python3 scripts/partial_swap_producer.py --work-dir /tmp/partial-swap-producers
```

The portable producer sources are in `scripts/partial_swap/`. They adapt the
retained paired-exclusion and shared-point circuits with base threshold two,
aligned point ordering, retained totals, and dependency-preserving labels.
The selected data in `certificates/partial-swap-input.json` are compared with
regeneration; they are not accepted as the sole producer justification.

For exact arithmetic alone:

```sh
make partial-swap-certificate
```

The output certificate uses exact rational numbers. Rounded decimal values in
the prose are explanatory. On a committed checkout, generated artifacts can
be checked with `git diff --exit-code -- certificates patches`.

## Proof PDF

```sh
make partial-swap-note
# Alternatively:
make partial-swap-note TEX_ENGINE=tectonic
```

The target produces `artifacts/partial-swap-note.pdf`. The default engine is
pdfLaTeX. PDF bytes can differ across TeX environments. The standalone note is
the current proof; the [combined manuscript patch](../PATCHING.md) and its
generator remain the inherited #10 result.

## Provenance

[SOURCES.json](../SOURCES.json) records the handoff archive hash, #10 parent,
and retained source pins. The original archive and exploratory alternatives
are kept outside this submission. Existing copyright notices and the Gaussian
scaling correction are preserved. The GitHub workflow runs `make verify` and
checks certificate/patch reproducibility.
