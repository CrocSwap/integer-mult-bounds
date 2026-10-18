# Local coordination claim

- Track: `recursive-interfaces`; task `persistent-boundary`; OS seed `65562f37d3a7a48fc2f959e36d6e638c`; catalogue priority revision 3; exact base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Scope: two distinct root-echo types in the pinned order-four PR1391 macro interface. Type A has 3 children and source-reader sequence `[0,1,2]`; type B has 7 children and sequence `[2,1,0,2,1,0,2]`. Both use the same arbitrary dirty source and output.
- Question: Can canonical A then B be replaced by a canonical joint ten-child echo with exactly the composed dirty map, while charging the second wrapper and all frame transitions?
- Changed assumption: child count and source-reader sequence vary between the two consecutive calls; the closest prior `z4-persistent-pair-seed57` result covers two identical 5-child calls and explicitly excludes heterogeneous calls.
- Optimistic invoice: separate 3+7 estimate 2,080 ADD/NEG primitives; joint ten-child estimate 1,904, for a target saving of 176. Check the full map, both call wrappers, inverse bodies, read/write invoice and prefix row-L1 before claiming a result.
- Method/domain: exact 4-state phase dynamic program plus exhaustive `4^3`, `4^7` and `4^10` path checks; all 56 dirty coordinates.
- Related work: `z4-persistent-pair-seed57`, `z4-paired-frame-restoration-seed56`, `research/cyclic-output-restoration`, and `research/mutable-source-persistent-connector`. The fresh cached overlap scan found no active matching heterogeneous Z4 pair. Discussion #1516 concerns centre-path hosting and is a different lever; its claim expiry is past.
- Claim expiry: 2026-10-14 09:55 UTC.
- Posting: GitHub GraphQL remains rate-limited. The local claim and the 09:00 UTC overlap snapshot are retained under the repository fallback procedure.

## Status update

The exact construction and 56-coordinate map checks pass. Separate 3+7 calls cost 2,080 ADD/NEG primitives; the joint ten-child word costs 1,904 and saves 176 (11/130), while peak row-L1 rises from 36 to 42. The result remains local until package validation and final overlap refresh are complete.

## Status update

The exact construction completed and passed: separate A then B and the joint ten-child word have the same full 56-coordinate integer map. The separate invoice is 2,080 ADD/NEG primitives; the joint invoice is 1,904, saving 176 (11/130). Read counts fall 3,968 to 3,624 and writes 2,080 to 1,904. Prefix row-L1 rises from 36 to 42. Local verification command and package metadata validation passed; final overlap and submission remain.

## Posted claim

The refined claim is live at [Discussion #1163 comment 18920329](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18920329). It records the exact A/B maps, 3+7 domain, 176-primitive optimistic saving, overlap context and 09:55 UTC expiry.

## Final overlap refresh

Complete PR and Discussion pagination was refreshed at 2026-10-14 09:16 UTC (438 PRs, 400 Discussions). No matching active heterogeneous Z4 3+7 scope appeared. The posted claim remains at [Discussion #1163 comment 18920329](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18920329).
