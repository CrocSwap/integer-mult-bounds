# PROOF-NOTE-FRAMES-X4: chafreaky's #741 frames and JointXF's joint exchange (X4)

Two construction steps on top of research/gauge44-promo-p6k4sw's SW4 word P6k4sw4 (`d232183f…`).

## 1. #741's eight B frames (`construction/frames/`)
The eight B-gate frame raises are by **chafreaky**, [#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741)
(`research/complex-sw4-frame8`, commit e516b146). `FRAME-RECIPE-sw4.json` is byte-identical to #741's
`data/FRAME-RECIPE.json` (a2c7ca4d…). CompetitorMine ported #741's builder and controls; only package paths are adapted.
The step applies the frames with BlockInvert's `build_promotion.apply` and checks:
- the scalar program of A, cut, B, precondition and cleanup is unchanged;
- start and end frames are unchanged;
- the profile, the widths and the output word `e7804702…` are pinned;
- 3 pin controls are rejected;
- #741's 10 focused native controls are rejected (8 frames emptied, a changed read coefficient, paid-profile tampering);
- the per-end layer-end controls reject 95;
- the native chain matches its pins.

The rebuilt locals equal G44Pack's F741 locals except the `seconds` field in CLIFFORD-REVIEW.
This step reproduces #741's word. The final word is built by step 2, which contains these frames.

## 2. Joint exchange X4 (`construction/jx/`, JointXF)
There are four disjoint instances of BRoute's sw4 read-set exchange rule. Each one exchanges *two* copy pairs that
share targets: (448, 472), (458, 592), (470, 604) and (482, 614), with face registers 235, 267, 58, 427, 26, 443, 18
and 50. #741's eight frames sit on top. The 16 moved reads keep their original stored dim-6 frames: they are
monotone-repaired rather than refitted to the plain join. The recipe `RECIPE-X4.json` is explicit:
- 32 replaced gates, 16 deleted gates and 16 inserted gates, each with its old gate asserted;
- #741's 8 frames, listed with their source;
- 16 explicit frames at the moved reads, each asserted equal to the recomputed frame.

The builder `build_jx.py` uses only the standard library. It checks:
- target frames lie inside u_t^⊥;
- tails and ends;
- exactness of the whole B segment's rational linear map against the input (a Fraction replay);
- the recomputed paid profile and the output sha `1e1d99ba…`.

Effect against #741's word: the profile goes {1:2556, 2:334, 3:430, 4:194, 5:56, 8:8} → {1:2548, 2:338, 3:430,
4:194, 5:56, 8:8}. The width inventory is unchanged, and each instance gives +1.0798e-7 at ideal, exactly additive.

**Controls**, each pinned in the recipe and rerun by `reproduce_jx.py`:

| control | outcome |
|---|---|
| C0 identity | returns the input `d232183f` |
| C1 #741 only | `e7804702`, #741's word (ties step 1 to step 2) |
| M1 one pair (448) with frames retained | `5fb6fb2e`, neutral (profile = #741) |
| N1 pre-read dropped | rejected: exactness rows [132, 135] |
| N2 pre-read with wrong sign | rejected: exactness rows [132, 135] |
| N3 plain-join refit of the moved reads | `7241cd59`, strictly worse |
| N4 a raise made dim-7 at B855 | rejected: cap at (1302, 174) |

N3 and M1 are pinned-outcome controls (a specific different word), not rejections. They show the gain needs both the
target-sharing pair and the retained frames.

**Other checks (JointXF):**
- `audit_local` PASS;
- native chain PASS;
- FrameCoal's global frame optimiser reaches the same profile on this move set, so X4 is frame-optimal for these moves;
- SW4Extend found the same word independently.
