# Sprint assignment and overlap record

- OS random integer: `3423301012`.
- Assignment seed: `52` (`3423301012 mod 60`); structural decoder track.
- Exact base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Narrow question: independently replay the `d0=76` P112 asymmetric two-sink
  witness in `research/format-limits` C.6, including all matrix entries, COPY
  ranks, and correction supports.
- Method: a standard-library implementation of the E8/Hamming line geometry,
  exact rational row construction, and bit-packed `F_2` elimination; no SAT
  search. Seed 52 chooses `d0=76` from the predecessor's three cases
  `{75,76,77}` by the middle-index rule (`52 mod 3 = 1`).
- Expected artifact: an independently runnable verifier, exact certificate,
  scope note, source pins, and negative controls. No new supplier or κ claim.
- Expected finish in the posted claim: 2026-10-13 23:35 UTC; claim expiry:
  2026-10-14 00:56 UTC.
- Claim posted to the pinned coordination discussion:
  https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18910869

## Candidate tasks considered

1. **Selected:** independently check the off-pattern P112 asymmetric unit in
   C.6, fixing the seed-selected `d0=76` pencil. The fresh overlap helper
   reported zero direct matches across all 818 open PRs and 68 discussions
   for the exact witness/audit terms. This is not a novelty certificate: the
   local C.6 source is the predecessor being checked.
2. **Declined for overlap:** lower the P112 co-star/root-star COPY threshold
   under support trims. Same-day open work includes PRs #1320, #1323 and #1325,
   with claims/discussions #1267, #1301 and #1330 on adjacent pieces.
3. **Declined for overlap:** classify masked rank-eight complex decoders over
   all P104 frame-pair punctures. The recent claim in discussion #1275 and PR
   #1292 cover that object; PR #1212 also covers a neighbouring rank-eight
   decoder rigidity question.

The overlap helper used complete paginated snapshots (818 open PRs, 68
discussions; no warnings). It searches titles, bodies, comments, local package
readmes/task metadata and the PR ledger, but not arbitrary code diffs or every
closed PR. The direct PR inventory and these local predecessors were also
checked by name. Recheck live metadata before submission.
