# Index changed paths once for replay selection

The registered replay planner now groups changed paths by package once.
It retains the complete matrix, reason lists, manifest hashes and input checks.
No verifier coverage is removed. There is no persistent cache.

At base `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, the all-tracked case
contains 115,770 paths and 3,072 registered manifests. The previous planner
tests every path against every package prefix. A profile measured 356,105,974
`startswith` calls. The package-file generator used 113.300 of 119.537
instrumented seconds. An earlier cold Git download was stopped; it is not a
completed benchmark. The completed profile used materialized manifests.

## Exact selection argument

Each manifest is `research/<package>/VERIFY.json`. A changed path starts with
`research/<package>/` exactly when its first two slash-separated components
are `research` and `<package>`, and a third component exists. Split at most
twice. Group the original strings without path normalization. Process sorted
strings, so each group's order equals the previous sorted prefix result.
Removed paths, nested paths, Unicode and line breaks keep their exact spelling.
A sibling such as `research/alpha-extra.txt` is not inside `research/alpha`.

This replaces a package-count times changed-path-count scan with one sort and
one grouping pass. It uses additional linear storage for path references.
Declared-input validation, sparse manifest authentication, symlink rejection,
shared-control selection and publication order are unchanged. The existing
stable-checkout requirement still applies. A plan is not a mathematical check.

## Measured evidence

[The full receipt](replay-path-index-benchmark.json) records all three alternating
samples, source hashes, platform, interpreter and complete-plan hashes. Every
result row, cause list and manifest hash was equal in every comparison.

| Input case | Selected packages | Median before | Median after |
|---|---:|---:|---:|
| All tracked paths | 3,072 | 47.135 s | 2.433 s |
| Shared runner path | 3,072 | 1.735 s | 1.719 s |
| Selected package result path | 17 | 1.822 s | 1.827 s |
| Root README path | 1 | 1.703 s | 1.720 s |

The all-tracked median ratio is 19.37 on macOS arm64 and CPython 3.14.7.
The receipt calls the root README case `unrelated`; one package declares that
file as an input, and that package remains selected. Small-diff timings are
approximately unchanged. This is a local planner measurement. It is not a
whole-replay, hosted-CI or multiplication-runtime measurement.

Run from a stable checkout with Git, full baseline history and Python 3.10+:

```sh
python3 -B scripts/benchmark_research_plan.py --baseline ff3cc58e370d0f678e529246f8c73e8094e18fcf
```

The command compares complete plans and fails on any difference. Sparse
checkouts can need normal Git downloads for omitted manifest blobs. Materialize
the manifests before timing when a download-free comparison is required.
The expected counts above belong to the recorded base, not every later commit.

## Checks and limits

All 37 tests in these five modules pass on CPython 3.12.13 and 3.14.7:

```sh
python3 -B -m unittest discover -s tests -p 'test_research_plan_explanations.py' -v
python3 -B -m unittest discover -s tests -p 'test_research_replay_selection.py' -v
python3 -B -m unittest discover -s tests -p 'test_research_sparse_planning.py' -v
python3 -B -m unittest discover -s tests -p 'test_research_input_paths.py' -v
python3 -B -m unittest discover -s tests -p 'test_research_matrix_batches.py' -v
python3 -I -O -B tests/test_research_plan_explanations.py
```

The last command also passes all seven focused groups on Python 3.12. The new
real-Git case covers exact package boundaries, nested Unicode paths, a newline
path, rename deletion and an unmatched sibling file. Existing controls retain
invalid-input, sparse drift, inventory failure, removed-input and matrix limits.
Selected source-binding orientation passes. No package verifier, historical
supplier replay, full test suite or native Windows run was performed.
The selected kappa remains `60403/20000000`.

## Coordination and credit

This refines the `replay-runtime` card, priority revision 7, picker nonce
`03c019e9d2a2a285915b6e03f0dff26e`. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5305)
records the question and stopping test. The final overlap check covered 357
open PRs, 4,569 Discussion records and all 7,091 tracked local README/TASK
notes, with no reported omissions. Arbitrary diffs and unpublished work remain
outside that check. Canonical main still matched the base before submission.

Douglas Colkitt supplied the replay planner and source validation. Charles
Bethin supplied the retained invalidation tests. Tekalign supplied the retained
plan explanation and sparse discovery work; its Arham-Tahir64 sparse-reference
lineage remains credited. The earlier
[source-read batching](https://github.com/CrocSwap/integer-mult-bounds/pull/1595)
and [inventory rejection](https://github.com/CrocSwap/integer-mult-bounds/pull/2958)
solve different stages. Their checks are retained. Ali Romman, with substantial
OpenAI Codex assistance in code, measurement, review and documentation.
Apache-2.0. No independent human review is claimed.

## Open next questions

Measure the same complete plan on the hosted Linux/Python 3.12 environment.
Use the pinned base and record all timing samples and exact plan equality.
This tests host portability of the measured gain; it requires that runner
environment. No additional optimization is justified by this local result alone.
