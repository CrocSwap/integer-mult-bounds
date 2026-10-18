# Sprint claim and handoff

Initial claim: [D#1163, comment 18911678](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911678).
Submitted: [PR #1398](https://github.com/CrocSwap/integer-mult-bounds/pull/1398); DONE update: [D#1163, comment 18911841](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911841).

- Track / OS seed: complex supplier / 37.
- Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Exact object: PR1263 frozen k8 scalar word, helper L284, eligible index 53; first helper after PR1259's seed-37 interval `[37,53)`.
- Method: exact all-integer one-coordinate temporal gauge on every incident ADD in both orientations; include entry, transition, and restoration scales; compare against the best constant additional exponent.
- Result: -78 real / -156 complex primitives per orientation, paid profile unchanged, all 712 formal columns exact.
- Limits: no other helper search, schedule composition, native/hosted admission, or κ claim.
- Reproduction: `python3.12 scripts/research_package.py --package research/k8-l284-temporal-seed37`.
