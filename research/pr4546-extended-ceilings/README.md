# #4546's zero shear headroom: recomputed, extended to six-shear words and to all 128 eligible windows

**Task:** independent-moment. **Base:** canonical main `f626db5c`. **No new κ.**

Clear1nsight's #4546 (head `55b8d34c`) certifies **zero optimistic headroom** at C = 0.00302015 in the first twelve #4470 phase-B receiver windows. The candidates are every word of at most **four** unit shears on the same three persistent fields, with the same exact endpoint and fixed entrance/exit frames. Its open question asks to change the length cap before reopening the domain.

This package recomputes #4546 with separately written code and **extends the cap to five and six shears**. Nothing is imported from #4546. The windows are extracted by this package's own code from the canonical #4470 constructor in main (`research/joint-helper-lattice/native_joint.py`, run isolated on its pinned inputs). #4546's `RESULT.json` (blob `f2f41100`) is vendored only for cross-checking.

## Results

1. **Reproduction at length ≤ 4.** All twelve windows match #4546 exactly:
   - index, roles, coefficients, phase, start/exit dimensions and old paid profile;
   - 22,621 words with 84 endpoint matches each;
   - relaxed-profile counts of 1, or 4 for windows 10575 and 10579;
   - a best optimistic gain of exactly 0.
2. **Lengths 5 and 6.** These add 248,832 and 2,985,984 words, with matches found by meet in the middle over exact integer matrices. Every window then has 272 matching words (≤ 5) and **3,812** (≤ 6), and every one is admitted by the dimension screen. **The relaxed-profile set is unchanged in every window, and the best optimistic gain stays exactly 0.**

| window | old paid | relaxed profiles (≤4 / ≤5 / ≤6) | best gain |
|---|---|---|---|
| 10554, 10555 | {2:1} | 1 / 1 / 1 | 0 |
| 10557, 10560, 10561, 10563 | {1:3} | 1 / 1 / 1 | 0 |
| 10558 | {1:2} | 1 / 1 / 1 | 0 |
| 10564 | {1:1} | 1 / 1 / 1 | 0 |
| 10575, 10579 | {1:1, 2:1, 3:1} | 4 / 4 / 4 | 0 |
| 10577, 10581 | {1:2, 2:1} | 1 / 1 / 1 | 0 |

3. **All 128 eligible windows.** #4546 tested only the first twelve, so this extension covers all 128 eligible adjacent pairs: 123 in phase B and 5 in cleanup_tail. **Every one has an optimistic ceiling of exactly 0 at both length ≤ 4 and length ≤ 6.** At length ≤ 6, 93 windows have one relaxed profile and the others have 2–9, none of which improves on the incumbent.

4. **#4543's receiver-sharing rewrite on all 128 windows.** #4543 replaces `a += ca·x; b += cb·x` with `a += s·b; b += cb·x; a −= s·b`, `s = −ca·cb`, and tests twelve windows. On all 128, the endpoint identity holds. In **96 windows** (91 in phase B, 5 in cleanup_tail) the relaxation admits the incumbent profile and nothing better. In the other **32 phase-B windows the rewrite is infeasible**: `b`'s entrance frame is not contained in `a`'s exit frame, so the first gate `a += s·b` has no admissible common frame. Since the relaxation contains every actual path, this is a sound impossibility, not just an optimistic bound. **With exact geometry**, an exhaustive search over actual nested subspaces, the receiver-sharing word realises the incumbent profile **exactly** in all 96 feasible windows, including #4543's twelve, and nothing better. This confirms #4543's construction claim and extends it to every feasible window.

5. **Nonunit coefficients, all 128 windows.** This allows shears `y_i += c·y_j` with `c ∈ {±1, ±2}` up to length 6 (37,076 endpoint-matching words per sign case), and with `c ∈ {±1, ±2, ±3}` up to length 5 (8,386 per sign case). **Every ceiling is still exactly 0.** The coefficients' scalar-height cost is not charged, which only favours the rewrites, so this zero is still a sound negative.

6. **Nonadjacent pairs.** These are pairs `a += ca·x … b += cb·x` with unit coefficients, separated by at least one operation, none of which touches `a`, `b` or `x`, so the pair can be rewritten in place. My extraction finds 88 of them.
   - **87 pairs.** The relaxation already gives ceiling 0 through length 6.
   - **One pair** (positions 11334 and 11344, gap 9). The relaxation is **not tight**: it allows a cheaper dimension profile, `{2:5, 3:1}` against the incumbent `{1:3, 2:2, 3:2}`, with optimistic gain about 0.0026, for 186 words of length ≤ 6, including the original two-shear word. An **exact search over actual nested subspaces**, which enforces joint incidence across gates, finds **no positive gain** for any of those 186 words. The incumbent contact frames, of dimensions 4 and 6, are already geometrically optimal.

7. **Single-contact retiming, whole word.** Across every phase, every two-operand scalar contact of #4470's word (16,089 contacts) already sits at a cost-minimising contact dimension, given its operands' current frames and next-contact frames. Every intermediate dimension is realisable by a nested subspace, so this local-optimality check is exact. The phase breakdown is zero_frame_precondition 5,908, full_frame_cleanup 4,637, A 3,557, B 1,791 and cleanup_tail 196.

8. **Two-contact joint retiming, whole word.** This retimes pairs of consecutive contacts of one field jointly, with different partner fields: 26,092 pairs. The dimension relaxation gives no gain for 26,042 of them. It suggests a gain of about 0.0016 for 50 pairs, but an exact search over actual nested subspaces finds **no gain for any of the 50**.

9. **Agreement with #4581's all-length certificate.** mihir-s-05's #4581 (head `b154350f`, `RESULT.json` vendored, blob `3fec4b9b`, SHA256-pinned) proves the all-length floor with a different relaxation: a DAG over dimensions and a source-dependence mask. **In all 128 windows, its all-length terminal profile set is identical to this package's length-≤6 relaxed profile set**, computed by different code with a per-word forward-span/backward-intersection relaxation. Its capped-rank majorization certificate (`Σmin(r,k)` for `k ≤ 9`, equal mass) is rechecked here with my own integers. The telescoping identity that turns it into every concave price is checked exactly on 200 random rank-price tables. So length 6 already attains every all-length relaxed profile here, and the two relaxations corroborate each other. mihir-s-05's two further all-length certificates, #4582 and #4587 (their `RESULT.json` files are vendored and SHA256-pinned), give **the same sets in all 128 windows**, so four separately implemented computations agree exactly.

**Why it does not move.** In this relaxation, every contact frame lies between the forward sum of the operands' current lower bounds and the backward intersection of their exits. For these windows those bounds already pin each field's admissible rank steps. For example, in the `{1:3}` windows a field climbing `0 → 2` has every contact capped at an exit intersection of dimension 1. Longer words only add contacts under the same caps, so they cannot merge the two rank-1 payments. This explains the observed invariance but is **not** proved here for all lengths; the checked statement is lengths ≤ 6.

**Model** (re-implemented from #4546's README):
- each shear acts in one common binary frame, and frames only grow along a field's path;
- forward mandatory spans and backward permissible intersections bound every contact;
- integer contact dimensions are enumerated, and every positive gap, exit gaps included, is charged;
- ranks are priced `r^(1−C)` with certified rational enclosures.

The relaxation contains every actual monotone path, so a zero ceiling rules out gains from any word in the class.

## Verify

```text
python3 -B research/pr4546-extended-ceilings/verify.py
```

This runs in about 3 s with the standard library only.

## Limitations

- **Coverage.** All 128 eligible adjacent windows and 88 nonadjacent pairs are covered, with coefficients up to 3 in absolute value (adjacent windows) and unit coefficients (nonadjacent), the same three fields and fixed boundaries.
- **Lengths.** This package checks lengths ≤ 6. The all-length statement for the 128 adjacent windows is #4581's theorem, with which these sets agree exactly. Nonadjacent pairs, nonunit coefficients beyond the checked alphabets, and retiming neighbourhoods remain finite checks here.
- **Overlap.** Individual window results must not be summed across overlapping windows.

## Open next questions

- Prove the length-independence: show that the relaxed-profile set of a window is determined by its start and exit frames. First step: characterise the reachable contact dimensions from the pairwise exit intersections and start sums alone.
- Change the model further: owned-field allowances or extra fields. Length up to 6, coefficients up to ±3 and nonadjacent pairs are now closed. The exact-geometry search here shows the relaxation can be loose, so any positive relaxed lead in a new model should be rechecked with it.

Credit: Clear1nsight (#4546), Cinna Davis (#4470), and zxv's receiver-sharing and helper work. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
