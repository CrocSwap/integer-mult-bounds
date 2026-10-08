# Reproducing the current result

Run from the repository root with Python 3.11+, a C++17 compiler supporting
unsigned 128-bit integers (GCC or Clang), Git, and Make. No third-party
Python package or network access is required.

```sh
make copied-centers-verify
```

The incremental target:

- Matches the unchanged positive-label bit producers at h25 and h23 to
  the previously verified partial-swap certificate.
- Recomputes all 47 rational corner pivots and verifies all 315 symbolic
  zero-minor partitions using 630 exact integer-rank calculations.
- Regenerates the new h28, d19 mixed-center complex producer, checking its
  scalar supports, center coefficients, binary frames, matching and histogram.
- Applies the copied-center histogram replacement, reconstructs both complete
  child lists and checks both strict moments, the semantic precision guard,
  product row stock, seven margins and 47 strict assembly constraints.

The copied-center scheduling and simultaneous rational-basis arguments are
written proofs. The finite checks establish their selected arithmetic inputs.
Unchanged historical producers and suites are skipped. Intermediate graphs
and compiled tools are temporary; `--work-dir PATH` retains them if needed:

```sh
python3 scripts/copied_centers_producer.py --work-dir /tmp/copied-centers-producers
```

For arithmetic alone, use `make copied-centers-certificate`. `make verify`
also runs inherited checks, including the previous structured-bulk target.

## Proof and dependencies

The proof is supplied as [LaTeX source](../notes/copied-centers-note.tex).
No PDF is generated for this submission. The selected
[two-stage and corner sources](../references/copied-centers/README.md) and
[semantic/analytic sources](../references/semantic-bulk/README.md) retain
original licenses, notices and hash manifests.

[SOURCES.json](../SOURCES.json) pins the archive, parent and contribution
sources. Raw graphs, alternatives, terminal-eligibility experiments and
recursive copies of predecessor archives remain outside the submission.
The [historical manuscript patch](../PATCHING.md) retains the #10 result.
