# Exact degree pruning for signed-sparse coefficient replay

Tooling improvement, **no new κ**. Replace the `4^h` complete Cartesian scan
in `coefficient_terms` with an ordered depth-first traversal that rejects a
prefix as soon as `r + 2s > q - 1`. Every suffix has nonnegative degree, so
no completion of such a prefix could survive the original filter. The
binomial parity test and feature-weight guard are unchanged. Visiting children
in `0, pp, np, pn` order preserves the complete ordered output, including
multiplicity; this is not a sample or a search for new constructions.

## Reproduce

From a full Git checkout containing the base commit, with Python 3.11+:

```sh
python3 -B research/signed-sparse-pruning/reproduce.py
```

Expected: `PASS 13 ordered streams; full historical certificate unchanged; 10
regression tests`. The command verifies the baseline source SHA256, compares
all valid power-of-two pairs `2 <= q <= h <= 8`, runs both implementations of
the complete historical audit, compares its proof-relevant payload to the
committed certificate, and runs the old and new regression tests. Only
`source_sha256` is excluded from certificate equivalence; all mathematical
fields, controls and scan rows are retained. Use `--output /tmp/result.json`
to save fresh measurements; timings are observational, never pass thresholds.
No external Python dependencies are needed. Git is needed to load the pinned
baseline; fetch the base commit first if using a shallow checkout.

## Evidence and limits

[RESULT.json](RESULT.json) records seven alternating-order measurements for
each identical input, exact ordered-stream digests, interpreter/platform and
source pins. At h=8, measured enumeration median speedups were **574x** for
q=2, **52x** for q=4 and **3.08x** for q=8 (9, 205 and 7,423 emitted terms).
The absolute baseline time is only around 10–16 milliseconds per h=8 stream.
The standard historical audit uses smaller controls and spends time elsewhere:
its measured median speedup was **0.982x**, i.e. no demonstrated end-to-end
speedup. This is a focused enumeration optimization, not a claim to accelerate
the selected frontier's cold replay.

The new Cartesian-reference test uses a separate direct mask construction.
Two negative controls remove a mixed term or duplicate the constant; both
fail the existing full factor identity check. The h>8 expansion guard remains
active. All 10 signed-sparse tests also pass under `python3 -O`.
The existing positive-side tests and generator cover its import of the same
module. Regenerated signed-sparse and positive-side certificates change only
the affected source digest. The unrelated repository-wide `make verify` and
selected frontier cold replay are not needed for this scoped historical
helper change and were not run.

The historical factor construction and unresolved side-circuit budget remain
as described in [signed-sparse-core.md](../../docs/research/signed-sparse-core.md).
No side construction, stronger bound, selected-frontier change, all-size formal
proof, or discharge of inherited multiplication assumptions is supplied.

## Pins, attribution and coordination

- Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
- Baseline helper SHA256:
  `21da8e1de5ab6ac8479183326c2000313d24b47cc5be2f46b4fe6ac3cd59779f`.
- Historical source integration: Douglas R. Colkitt,
  `d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`; the existing factor construction,
  audit and test suite receive all mathematical predecessor credit.
- Contribution: anudeepadi, with substantial OpenAI Codex AI assistance in
  implementation, testing and documentation. Apache-2.0, as in this repository.
- [Local claim](CLAIM.md): seed 92, verification engineering; no pinned sprint
  issue existed. The checked open tooling PRs concern other objects, including
  #824 (stage-pair), #778 (single-intersection), #752 (quadratic-affine), and
  #736 (cyclic inverse). This work does not depend on those pending changes.
