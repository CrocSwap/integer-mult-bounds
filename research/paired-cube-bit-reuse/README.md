# Exact obstruction to fixed-gauge bit reuse

The proposed compensated-reuse experiment has **no legal handoffs into the
currently selected bit gauges**, in either checked snapshot. The obstruction
is geometric and applies before compensation-read deadlines are considered.
It should prevent spending optimizer effort on an empty matching graph.

| Checked snapshot | Logical auxiliary roles | Non-root donor roles | Gauge roles | Excluded donor/gauge pairs |
|---|---:|---:|---:|---:|
| PR164, `4391a60bb26f75ea47a4c55c508c88a036b5a2b8`, with its selected 1,464 frame descents | 23,368 | 13,224 | 5,720 | 75,641,280 |
| PR168, `98c115b53742b6613ad630de4d493f37b0119da7`, retained bit word | 22,252 | 12,108 | 5,720 | 69,257,760 |

Both snapshots have 220 distinct selected gauge spaces, all of dimension 20,
and 1,760 source incidence vectors in dimension 24. For every one of the
387,200 gauge/source combinations, the checker finds an explicit integer
annihilator row with a nonzero pairing. Thus no selected gauge contains any
source incidence line.

For every non-root donor, the checker separately exhibits a source incidence
line in its terminal operation frame. If that donor frame were contained in
a selected gauge, its exhibited line would also be contained there, contrary
to the first check. This proves that the entire compatibility graph is empty;
it is not a random sample, dimension-only filter, or failure of a particular
greedy matching algorithm.

## Reproduction

From the PR168-based repository checkout, the local certificate needs no
other checkout:

```sh
python research/paired-cube-bit-reuse/check_obstruction.py --check
```

To reproduce the separate historical PR164 record, provide an unmodified
PR164 source checkout at `SOURCE164`:

```sh
python research/paired-cube-bit-reuse/check_obstruction.py --source164 SOURCE164 --check
```

The equivalent explicit commands, useful when checking a different source
checkout, are:

```sh
python research/paired-cube-bit-reuse/check_obstruction.py \
  --source SOURCE164 \
  --plan SOURCE164/research/paired-cube-bit-descent/descent.json \
  --out research/paired-cube-bit-reuse/pr164-obstruction.json --check

python research/paired-cube-bit-reuse/check_obstruction.py \
  --source SOURCE168 \
  --out research/paired-cube-bit-reuse/pr168-obstruction.json --check
```

Omit `--check` to write a fresh certificate. The certificates include the
source commit, Git blob identities, SHA-256 hashes of all inputs, the checker
hash, and hashes of every deterministically enumerated integer witness.
Each source input is required to match its recorded commit. Both shipped
certificates reproduced byte for byte. The commands require only Python's
standard library and Git and reject optimized Python execution.
The `--check` mode uses the commit pinned in the saved record, so subsequent
commits adding this package do not invalidate an unchanged source snapshot.

The integration API is
`certificate(source: Path, plan: Path | None = None, source_commit: str | None = None)`.
For the local pinned result, call it with this repository path and
`source_commit="98c115b53742b6613ad630de4d493f37b0119da7"`; JSON-normalize the
returned dictionary before comparing with `pr168-obstruction.json` because
the in-memory dimension histogram uses integer keys.

Before proving the obstruction, the script runs the source's independent
exact frame, scalar-decoder, geometry, chain, and ledger checks. The optional
frame plan is checked for full conservative source containment,
nondegeneracy over the rationals, and nested actual role chains. This is not
a new local-ring prime-exclusion certificate or a new formal-word replay.
The negative controls replace a selected gauge by the full space and erase
a donor's source-support frame; both must be rejected.

## Consequence for further optimization

Moment-weighted matching on these frozen bit gauges cannot improve the
profile. Neither valid donor-frame ascents nor conservative-support descents
remove the obstruction: the donor still contains a source incidence line.
Shrinking one of the selected gauges also cannot help.

A useful reuse search must first change the gauge spaces or the surrounding
target-read schedule and demonstrate a nonempty compatibility graph. Those
changes require their own scalar restoration, target-chain, local-ring,
fallback, and moment checks. This result does not rule out that larger
compiler search, multi-stage schemes with different invariants, or other
physical-frame improvements. It claims no new saving, global optimality,
or all-size multiplication theorem.
