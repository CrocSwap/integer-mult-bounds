# Sprint claim and handoff

Initial claim: [D#1163, comment 18911884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911884).
Submitted: [PR #1406](https://github.com/CrocSwap/integer-mult-bounds/pull/1406); DONE update: [D#1163, comment 18911948](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911948).

- Track / seed: structural decoder / OS seed 43.
- Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Object: `research/format-limits` C.6 P112 asymmetric two-target unit at `e=line 0`, `d0=line 77`; relaxed lines 74 and 77, sinks 378 and 389.
- Method: standard-library exact rational support replay over all 12,544 entries and direct F2 rank elimination; mutate sink and omit a shared source as controls.
- Result: window rank 9, COPY 65, 24 shared sources, corrections 28+28 versus 52+52.
- Limit: one finite witness audit only; no full decoder, supplier, or kappa claim.
