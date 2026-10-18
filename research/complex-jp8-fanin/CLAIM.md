# Complex supplier claim, seed 27

- Assignment: OS randomness returned 27 on 2026-10-13 at 04:52 UTC.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Track: complex supplier. Seed parity selects JP8; the distinct object is its backward common-target coefficient runs.
- Hypothesis: forming a signed source sum in one private stream, then using reverse Horner to accumulate its common dyadic multiple, reduces the fully charged cost of backward JP8 additions. The stream must be cleared at the block boundary and every live register must retain its exact map.
- Method: exhaust all maximal contiguous additions with the same target and non-unit coefficient magnitude in the pinned backward program. Price source accumulation, Horner preparation, signed target update and both clears before emitting a replacement. Keep only strictly cheaper blocks. Check exact rational maps and prefix bounds.
- Deliverable: one finite circuit research package, source pins, reproducible verifier, exact cost certificate, negative controls and scoped proof. No new kappa claim.
- Expected finish: 2026-10-13 05:42 UTC, 11:12 IST. Reserve the final quarter for verification and handoff.

Three candidate tasks were considered: further single-coefficient recoding, CK fixed-boundary frame optimization, and backward JP8 common-target coefficient batching. The first two overlap #723/#696 and #698. The third changes the sharing direction and needs a separate workspace and prefix argument from #722, whose backward scan found no common-source run.

No pinned coordination issue exists; the only open issue is #650 about Discussions. This local claim follows an open-PR review through #725. Related #681, #696, #719, #722 and #723 were inspected. Delegated work stays within this common-target batching experiment.

Acceptance requires a positive fully priced saving, exact maps including arbitrary private inputs, charged restoration, preserved source access, an explicit prefix bound, deterministic evidence and meaningful rejection controls. The selected certificate, supplier sources, global accounting, upstream directory and unrelated artifacts stay unchanged.

During optimistic pricing, the initial two-stream recipe was simplified to one stream. Halve the signed source sum first, then scan numerator bits from least to most significant, accumulating into the target at each set bit and doubling the work stream between bits. This is the transpose direction of binary Horner sharing. It needs no added private register and explicitly credits the related forward construction in #722.

Prepared for Sagar Thakrar, @thakrarsagar, with substantial OpenAI Codex assistance. Apache-2.0.

## Result

Completed and submitted as [PR #751](https://github.com/CrocSwap/integer-mult-bounds/pull/751).
All 999 backward cleanup batches, covering 3,022 additions, preserve their
exact maps and save 19,688 real primitives with one existing private stream.
The full backward prefix remains 101 bits. Main replay, twelve controls,
the separate 5,020-column block checker and selected-record check pass.
The contribution is a finite circuit research construction with no new kappa;
production integration and inherited global obligations remain open.
