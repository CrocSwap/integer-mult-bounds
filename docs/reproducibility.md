# Reproducing the current result

Run commands from the repository root. Numerical verification needs Python
3.11+, a C++17 compiler, Git, and Make; no third-party Python package or network
access is required. The full h28 support check uses about 1.2 GB of memory.

```sh
make verify
```

This rebuilds the retained ternary and complex producers, regenerates the
current and historical certificates and patches, runs the unittest suite,
and checks patch applicability against the pinned manuscript. The new batching
checks are part of this target. On a committed checkout, confirm reproducibility:

```sh
git diff --exit-code -- certificates patches
```

For the new arithmetic alone:

```sh
make batched-certificate batched-patch
```

The output reports `kappa=6149999/50000000000000 > 2^-23`, 29 strict constraints,
seven margins, and the positive final absorption gap. These programs check
exact rational inequalities; the matrix construction and tape-time bounds
also require the written proofs in the [review guide](research/batched-review.md).

## PDF and complete manuscript

```sh
make batched-note
```

This uses pdfLaTeX with AMS, Latin Modern, geometry, hyperref, enumitem,
mathtools, booktabs, and microtype, producing
`artifacts/batched-23-note.pdf`. PDF bytes may differ across TeX environments.
For Tectonic, run from the repository root:

```sh
make batched-note TEX_ENGINE=tectonic
```

The [patch instructions](../PATCHING.md) describe materializing the complete
manuscript. With Tectonic, its three pdfTeX-only metadata commands need
compatibility definitions in a disposable wrapper; the mathematical source
remains unchanged.

## Sources and automation

[SOURCES.json](../SOURCES.json) records the retained PR7 commit and the supplied
archive's hash. [upstream/manifest.json](../upstream/manifest.json) pins the
original manuscript files. `make fetch` optionally retrieves those exact files
and refuses to overwrite modified source.

The existing [GitHub workflow](../.github/workflows/verify.yml) runs `make verify`
and checks regenerated certificates and patches. Local success does not imply
that a hosted workflow has run. Older main-branch witnesses remain available
through their existing targets and version history.
