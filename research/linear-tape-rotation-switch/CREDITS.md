# Credit and source boundaries

Prepared by Ali Romman with substantial OpenAI Codex assistance in research,
implementation, verification and writing. New work is Apache-2.0.

- Jerry Chen supplied the physical ABI, builder primitives, primary hardware
  and quadratic graph in [PR #7593](https://github.com/CrocSwap/integer-mult-bounds/pull/7593).
  The [program source](https://github.com/CubeJerry/integer-mult-bounds/blob/56335a406469fad85e88ff72820d506d8bea6f63/research/literal-canonical-rotation-switch/switch.py),
  [hardware](https://github.com/CubeJerry/integer-mult-bounds/blob/56335a406469fad85e88ff72820d506d8bea6f63/research/literal-canonical-rotation-switch/hardware.py)
  and [proof](https://github.com/CubeJerry/integer-mult-bounds/blob/56335a406469fad85e88ff72820d506d8bea6f63/research/literal-canonical-rotation-switch/PROOF.md)
  are retained unchanged. Initialization in the new emitter adapts this
  source. Its Builder and cleanup are called without mutation. The old
  complete graph is replayed on the same 544 service fixtures.
- Ali Romman's [PR #7734](https://github.com/CrocSwap/integer-mult-bounds/pull/7734)
  supplied the [closed descent proof](https://github.com/aliromman/integer-mult-bounds/blob/57bb6efed1be1dda9eb1a0f622ec2773bc8b0047/research/rotation-switch-closed-descent/PROOF.md)
  and [arithmetic oracle](https://github.com/aliromman/integer-mult-bounds/blob/57bb6efed1be1dda9eb1a0f622ec2773bc8b0047/research/rotation-switch-closed-descent/query.py).
  Nick Petalas's [PR #7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504)
  supplied the endpoint and child formulas. These are predecessor results.
- Cinna Davis's [PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100)
  supplied the [canonical network compiler](https://github.com/CrocSwap/integer-mult-bounds/blob/337d04939571a637aeab54a0f58f54fde811663a/research/unconditional-batched-crt/check_batched_crt.py).
  Its unchanged finite function supplies expected table bits. Its full
  unconditional claim is not an accepted premise here.

The new contribution is the physical closed-descent program, canonical
countdown and carry-scan lowering, linear complete service bill, and
separate sparse instruction interpretation. No predecessor formula or
physical ABI is claimed anew. Shared code and mathematical premises are
explicit; separate interpretation is not independent human acceptance.

`SOURCE-PINS.json` records eleven retained files. The source notices and
license are unchanged, including ToikY, JoyboyBrian, Douglas Colkitt and
their predecessor lineages. `SOURCES.json` binds only base provenance.
No unmerged ancestry or full historical replay is asserted.
