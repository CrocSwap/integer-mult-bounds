# SW4: read-set exchange on 4 entering-copy pairs

- **Input.** P6k3, sha a38bb414.
- **Output.** sha f35a852b. Strict PASS at κ 0.001659645685315104, which is +3.267e-7 over P6k3 and equal to the ideal.
- **Width.** W 3782 is unchanged, as are start_extra, helper_final, cleanup and the helper numbering.
- **Rebuild.** `python build_sw4.py INPUT OUT [SW4-RECIPE.json]`. It is a deterministic apply of the 16 explicit moves, with 4 pinned controls: C0 (identity), N1 (keeping the pre-read is rejected), N2 (a partial exchange is rejected) and N3 (a wrong-sign pre-read is rejected).

## Move
For each pair (h,r) in {(461,25), (581,89), (591,415), (603,431)}, where h = E_h + r after h's copy gate:
- every post-copy target read of h becomes a read of r, and that target's entrance pre-read of h is deleted;
- every target read of r becomes a read of h, with the pre-read add(t,h,−c) inserted after h's last pre-read, while h = E_h.

The B-end state of every register is unchanged (checked mod p).

## How exhaustive the search was
These 4 are the only positives within an exactly defined family.
- **Copy pair.** h is an entering helper whose first B write is add(h,r,1/1) from a non-target r, and whose only earlier B gates are single target pre-reads. NP has 107 such pairs.
- **Candidates.** Every nonempty subset of one pair's movable reads (target reads of h or r between the copy and the next write of h or r), with all other pairs left unchanged. That is 602 candidates over the 54 pairs that have reads.
- **Outcome.** 564 are frame-illegal. The 38 legal ones are all full single-pair exchanges, and only these 4 are positive. Their gains are additive.

**What is not covered.** Cross-pair combinations of partial moves were not enumerated. Without a decomposition proof (moves can shrink as well as grow target frames), the result is exhaustive only within this single-pair family.
