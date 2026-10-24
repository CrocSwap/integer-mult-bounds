# Third-engine check of the coalesced reciprocal budget

The four fixed-profile numerical limits pass an independent rational
interval calculation. With the three-call profile

```text
{1:2913, 2:711, 3:138, 4:36, 5:15, 6:33, 7:30},
```

the extra allowance is 198 rank-one children or 99 rank-two children.
After a stipulated 64 rank-one cleanup, it is 134 rank-one children
or 67 rank-two children. Each maximum has moment strictly below one,
and its next integer count has moment strictly above one.

The check uses dimension 25, 224 productive fields, and the exact
historical saving exponent
`67018507072324140917/40000000000000000000000`. The source commit is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. This is a historical
comparison, not a refreshed selected frontier.

The consumed [budget receipt](../../budget-geometry-20261017/coalesced-reciprocal-budget-20261020/BUDGET.json)
has SHA256
`a24f6b95c5f341817b4f49ce845fa58b83060dc991c9f7772691c0edfcb9ad77`.
The checker imports the independent engine from this lane's freeze
`953690464698b38801b4f2ddf0f56035203a9337214595a557c7d3950e2e6f87`.
It checks all engine files, the historical source pins, and exact
containment within the producer's stated intervals.

This check does not repeat the twelve native-word counts or their
phase review. It takes the stated frozen profile as input. The
64-line cleanup is a separate construction premise. No complete
caller, terminal, host, finite-precision bound, supplier, or kappa
improvement is certified here.

Run `python3 -I -B check_budget.py normal.json` and
`python3 -I -O -B check_budget.py optimized.json`. The expected
status is `PASS_THIRD_ENGINE_COALESCED_BUDGET`. Both receipts must
match.

The budget-geometry lane supplied the profile budget and two exact
evaluators. This lane supplies a third evaluator for the four stated
thresholds. The work used AI assistance. Publication is coordinated
by the parent. Before a PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
