# Credit and exact sources

Prepared by Ali Romman with substantial OpenAI Codex assistance in research,
implementation, verification and writing. New work is Apache-2.0.

- Nick Petalas supplied the canonical endpoint formulas and child recurrence
  in [PR #7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504).
  The [source proof](https://github.com/petalas/integer-mult-bounds/blob/7efb9a84277ec31abe2a934aeef8c8a70548aa5b/research/canonical-rotation-switch-query/PROOF.md)
  and [query](https://github.com/petalas/integer-mult-bounds/blob/7efb9a84277ec31abe2a934aeef8c8a70548aa5b/research/canonical-rotation-switch-query/rotation_query.py)
  are retained unchanged. The source README retains its related-work credit.
- Cinna Davis supplied the deterministic compiler in
  [PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100).
  The [canonical source](https://github.com/CrocSwap/integer-mult-bounds/blob/337d04939571a637aeab54a0f58f54fde811663a/research/unconditional-batched-crt/check_batched_crt.py)
  is called unchanged for finite table comparisons. Its NOTICE is retained.
  The full unconditional construction is not an accepted premise here.
- Jerry Chen supplied the fourteen-tape implementation in
  [PR #7593](https://github.com/CrocSwap/integer-mult-bounds/pull/7593),
  head `56335a406469fad85e88ff72820d506d8bea6f63`. It is related physical
  work, not a consumed executable or a claimed automatic speedup.

The new contribution is the two-length closed descent, direct query and
matching bit-probe lower bound. The endpoint formulas retain their source
credit. The canonical compiler is a separate finite oracle; the recurrence
comparison shares the mathematical predecessor. Neither is an independent
human review.

`SOURCE-PINS.json` binds six retained files byte for byte. `SOURCES.json`
binds the base catalogue and selected record as provenance. No unmerged
source ancestry is asserted. The base license is retained. All predecessor
authors named in the retained notices keep their credit.
