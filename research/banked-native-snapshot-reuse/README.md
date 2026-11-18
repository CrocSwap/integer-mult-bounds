# Reuse the current banked circuit's private snapshots

The pinned final forward DAG of [PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674) needs 2425 snapshot banks under its fixed row order and the stated distinct-snapshot contract. A live cut of that size proves the minimum for this model. With one shared paid-row accumulator and four scalar scratch fields, **2430 private homes** suffice instead of 15290. Sixteen disjoint occurrences reserve 38880 instead of 244640. Other physical backing remains additional.

[Proof and physical limits](PROOF.md) · [All 9144 allocation entries and peak witness](ALLOCATION.json) · [Exact receipt](RESULT.json) · [Verifier](verify.py) · [Source inventory](PREDECESSOR.json) · [Task and open questions](TASK.json)

All 8533666 coefficient products and 1501 public endpoints pass an owner-aware exact scalar replay. Closed intervals, per-slot checks and a separate live-count sweep agree. Six controls reject unsafe ownership, capacity, inventory and arithmetic changes. The number of logical lifetimes is still 15290; all 30580 initialization/retirement services remain charged per native occurrence. The full source reset allowance stays 11816384 per raw caller. The result changes storage placement and retention time; it does not claim new kappa, a faster machine or a general space minimum.

## Reproduce

Use CPython 3.12 and the standard library. The source graph constructor is imported from authenticated retained bytes. No network or Git access is used by the verifier.

```sh
python3.12 -I -W error -B research/banked-native-snapshot-reuse/verify.py
python3.12 -I -W error -B -O research/banked-native-snapshot-reuse/verify.py
python3.12 -B scripts/research_package.py --package research/banked-native-snapshot-reuse
```

Expected status: `PASS_BANKED_NATIVE_SNAPSHOT_REUSE`. The registered normal and optimized commands each have a 120-second bound. The current base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, card `supplier-boundary-audit`. The scoped [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19703844) takes the source's explicit storage review request. The source scientific head is fixed. A later role-230 banked construction has a different graph and is not covered.

The source's full physical precision proof, physical Clifford suite, signed caller, selected cold replay, Lean and Docker were not rerun. The field allocation inherits the source's physical primitives and all five selected assumptions. Independent human or formal-kernel review is unclaimed. The interval method and source graph are prior work; the source-bound allocation and its ownership/cost certificate are the new result.

## Open next questions

Can a changed legal row order reduce the pool? First retain the same donor-chart, child-return and output-installation rules, then produce a new complete allocation and cost certificate. The present cut is not a lower bound for that changed order.

Can one concrete compiled tape occurrence realize the pool with its actual views and suspended backing? First bind every home, guard, guide and child workspace to its packed extent. This package supplies the field-level schedule, not that full lowering. [Structured next questions](TASK.json)

Prepared by Ali Romman with substantial OpenAI Codex assistance. Credit the graph and private-bank realization to [PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674), its native parent to SYLforge in [PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669), and the prior sources named in the [retained notices](predecessor/NOTICE) and [original parent credit](predecessor/source/7669-CREDITS.md). These files retain their exact original bytes. New work is Apache-2.0.
