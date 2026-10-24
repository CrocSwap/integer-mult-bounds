# Independent check of #4583: a serialized header for the PR4100 sparse-union schedule

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

mihir-s-05's #4583 (head `8d259a89`) gives a fixed-width per-microbox header for #4100's sparse-union schedule:

`H = 2gh + g + 2⌈log₂(g+1)⌉ + 2` bits, with `h = ⌈log₂ L⌉`.

At #4100's core side `L = 2^⌈400 log₂ p⌉` and `β = 1 − 3/10^30`, it shows `H ≤ 810 p^β log₂ p = o(p)` for `g ≤ p^β`, with an explicit cutoff `p ≥ 2^(40·10^30)` beyond which `H < p/32` (or `< p/16` with doubled `g`). This package checks it with a separately written codec and exact integer arithmetic. Nothing is imported from #4583's `header.py` or `verify.py`.

## Results

All checked claims are confirmed.

1. **Codec.** I built it from #4583's field table: marker `01`, coordinates, membership flags, boundary ordinals, flag count and tag, all big-endian.
   - **Round trips.** 2,888 of them, over random contexts for `g ≤ 5` and `L ≤ 16`, plus every boundary subset of a small domain. Every encoded width equals `H`.
   - **Active headers.** 2,094 checks: the `(r+1)`st set flag gives the active axis, a record is kept iff its count exceeds `r+1`, and the active ordinal recovers the boundary point.
   - **Corruptions.** All 3,600 corrupted headers (bad markers, inconsistent counts) are rejected.
2. **Width chain.** 6,448 cases, for integer `p` (2–69, powers of two up to `2^40`, and two non-powers) and `g ≤ 2000`.
   - `h = ⌈400 log₂ p⌉` is computed exactly as `(p^400 − 1).bit_length()`.
   - `H ≤ 2gh + 5g` holds (`b ≤ g`).
   - `H ≤ 810·g·t_lo` holds, where `t_lo = (h−1)/400 < log₂ p`, so `H < 810 g log₂ p`.
3. **Cutoff and binding.**
   - `δ = 1 − β = 3/10^30` matches both `β` and the `group_headers` slack in the pinned #4100 ledger (`composition-controls.json`), and `L = 2^⌈400 log₂ p⌉` matches `GAUSSIAN.md`.
   - `δ·t0 = 120` at `t0 = 40·10^30`, and `810·t0 < 2^115` and `1620·t0 < 2^116`, so `H/p < 1/32` and `< 1/16` there.
   - The tail is monotone, since `δ·t·ln 2 > 1` for `t ≥ t0` (using `ln 2 > 1/2`).

## Verify

```text
python3 -B research/pr4583-header-check/verify.py
```

This runs in under 1 s with the standard library only.

## Limitations

- **Not covered.** #4583's adaptation of #4327's tape simulator, and the reader-cost accounting (`O(H polylog p)`), which is an asymptotic argument in #4583.
- **Codec.** The codec checked here is the reference format. Whether #4100 serialises headers this way is outside both PRs.

## Open next questions

- None new from these checks. The producer and global-context tape obligations that #4583 names remain open.

Credit: mihir-s-05 (#4583); the #4100, #4327 and #4376 union-schedule lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
