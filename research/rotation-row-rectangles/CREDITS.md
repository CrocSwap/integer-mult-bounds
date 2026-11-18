# Credit and source boundaries

Prepared by Ali Romman with substantial OpenAI Codex assistance in research,
implementation, verification and writing. New work is Apache-2.0.

- Ali Romman's [PR #7734](https://github.com/CrocSwap/integer-mult-bounds/pull/7734)
  supplied the [closed descent](https://github.com/aliromman/integer-mult-bounds/blob/57bb6efed1be1dda9eb1a0f622ec2773bc8b0047/research/rotation-switch-closed-descent/PROOF.md)
  and [point query](https://github.com/aliromman/integer-mult-bounds/blob/57bb6efed1be1dda9eb1a0f622ec2773bc8b0047/research/rotation-switch-closed-descent/query.py).
  Its proof, query and credit file are retained unchanged.
- Nick Petalas supplied the endpoint formulas and child recurrence in
  [PR #7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504).
  The [source proof](https://github.com/petalas/integer-mult-bounds/blob/7efb9a84277ec31abe2a934aeef8c8a70548aa5b/research/canonical-rotation-switch-query/PROOF.md)
  is an inherited mathematical premise. The new rectangle description is
  a consequence of those endpoints and the closed descent.
- Cinna Davis supplied the [canonical compiler](https://github.com/CrocSwap/integer-mult-bounds/blob/337d04939571a637aeab54a0f58f54fde811663a/research/unconditional-batched-crt/check_batched_crt.py)
  in [PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100).
  It is retained unchanged as the finite table oracle, together with its
  NOTICE. The proposed complete unconditional construction is not a premise.

Related work has different contracts. Jerry Chen's
[PR #7593](https://github.com/CrocSwap/integer-mult-bounds/pull/7593) and
Ali Romman's [PR #7735](https://github.com/CrocSwap/integer-mult-bounds/pull/7735)
supply physical point queries. Nick Petalas's
[PR #6629](https://github.com/CrocSwap/integer-mult-bounds/pull/6629) changes
the routing choices to compact Waksman rows. His
[PR #4876](https://github.com/CrocSwap/integer-mult-bounds/pull/4876) gives a
minimum swap count for full dyadic rotations. This package keeps the exact
canonical padded table and does not claim those physical or global optima.

The six retained files have source commits, Git blobs and SHA256 hashes
in `SOURCE-PINS.json`. `SOURCES.json` binds only the base catalogue and
selected record as provenance. No unmerged source ancestry is asserted.
The base license is retained. Source authors keep all credit in their notices.
The canonical table is a separate finite oracle; the point query shares the
proof's predecessor. These checks are not independent human review.
