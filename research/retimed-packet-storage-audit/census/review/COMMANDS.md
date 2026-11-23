# Commands and review boundary

Track 79 started 2026-11-23 at approximately 08:04 UTC. The requested scope was
the Gaussian owner census in `work-storage/wave2-stock/OWNER-CENSUS.md`, with
author files preserved. The prior Lean result and earlier reviews were frozen.

Read the census, its binding manifest and proof context, then the exact
`transport`, `retimed_supplier`, `raw48`, `spool`, `compact_columns`, `periodic`,
`positive`, `strong_complex`, `tagged_sources`, `mixed_caller` and `closed_caller`
implementations. A separate bootstrap probe authenticated those eleven runtime
modules and reconstructed the graph/layout; its output is `BOOTSTRAP-READ.json`.
No source code was edited outside this review directory.

The complete independent check command is:

```bash
cd /workspace/scratch/5b0914ccc34e/work-compiler/census-review
python3 -B review_check.py
```

It passed with exit code zero and marker
`PASS_INDEPENDENT_OWNER_CENSUS_REVIEW_CHECKS`. `RESULT.json` includes the checker
hash, frozen proof hash, source hashes, finite coverage and mutation outcomes.
The final version adds an executed free-first mutation, actual `Job.select`
partition checks, and the exact installed mass-exponent binding. The prior run
was superseded by this final receipt.

The script does not execute the author's `census_raw.py`, `census_primitives.py`,
`census_schedule.py` or `verify_census.py`. It reconstructs source syntax and
compares source events with an independently sorted lifetime model. It does not
invoke production-size calendars or validate the analytic mass enclosure.

Final file hashes are recorded in `REVIEW-RECEIPT.json`. Source boundary hashes
must remain equal to `READ-BOUNDARY.json` / `FINAL-BOUNDARY.json`; source changes
invalidate this exact-byte review.
