# Cycle 12 scope and pivot record

- Accepted OS seed: `ff568c3e5cf8605fe719bcb7533b22f8`.
- Track: `bit-mechanisms`.
- Priority revision: 3.
- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

## First screen, released

The first refined scope was the two-role S4 target `diag([w],[w^-1])` for a
4-cycle and adjacent-transposition alphabet. The natural permutation
representation immediately gave target rank six and rank-one effect per paid
call, forcing six calls and matching its direct bill. Exact meet-in-the-middle
also returned no word in lengths zero through five. No package or PR was
proposed. The scope was released at [Discussion #1166 comment 18924236](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18924236).

## One evidence-driven pivot

The second scope was claimed in [Discussion #1166 comment 18924259](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18924259), then clarified against merged PR #1443 in comment 18924309. It uses the D8 noncentral order-four pair `diag([r],[r^-1])` on
two dirty roles. Here the regular representation only forces three calls,
while the direct bill is four, so a genuine saving remained possible. Exact
search exhausted lengths zero through three and found no saving. The package
records this scoped negative result and its direct four-call control.

The pivot followed the prescribed stop screen: the first scope had no
headroom, so it was released before packaging; no further pivot was made.
