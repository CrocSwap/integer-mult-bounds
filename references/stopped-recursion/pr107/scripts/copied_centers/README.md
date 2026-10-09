# Copied retained-center incremental verification

Run from the repository root:

```sh
python3 scripts/copied_centers_producer.py --output /tmp/copied-centers-producers.json
```

This command compares the reused positive-label bit25/23 producer records
with their already validated `partial-swap-input.json` provenance. It does
not regenerate those DAGs or matchings. Research terminal-eligibility fields
are excluded from the curated selected inputs.

The new work regenerates only the complex `(h,d)=(28,19)` mixed-center
producer, using the existing `structured_bulk.complex` implementation and
deterministic complex matcher. Exact support, scalar coefficient, frame,
and nondegeneracy checks are inherited. The complete matched record must
equal `copied-centers-complex-input.json`.

`corners.py` recomputes all 47 nonzero rational pivots and their contiguous
runs at `(25,23)`. It covers every candidate entry to the right of each pivot
and checks all 315 saved zero-minor partitions by 630 independent integer
rank computations. It does not repeat matroid-intersection search. The
resulting data profile is 11 singletons and blocks 21, 15, 481. This proves
the finite local corner assertions; their simultaneous basis transfer is
the separate written construction.

`physical.copied_histogram(record)` applies precisely `H[1] += h`,
`H[h] -= h`, leaving the copied rank-`h-1` calls and all other classes
unchanged. It verifies both old and new rank masses and fixed role counts.
It returns the complete changed histogram, rank mass and saved rank for
each selected producer.

All intermediate DAGs, labels and the matcher executable are temporary
unless `--work-dir` is supplied. Standard-library Python and C++17 suffice;
no archived binary or new dependency download is required. Assertions must
remain enabled.

Corner methods are by Rohan Arun (PR31, Apache-2.0, recorded OpenAI Codex
assistance), parameterized by Dominik Scholz (PR33, Apache-2.0, recorded
Anthropic Claude Opus 5.5 and OpenAI GPT-6 Astra/Codex assistance). The
selected specialization, copied-center scheduling and this incremental
integration are by icekylinx with OpenAI GPT-6 Astra/Codex assistance.
The copied-stream interface retains Aurel Prosz (Paureel)'s credit. Exact
source pins appear in `corners.py`; complete inherited licenses and notices
are retained in repository `LICENSE`, `NOTICE` and `SOURCES.json`.
