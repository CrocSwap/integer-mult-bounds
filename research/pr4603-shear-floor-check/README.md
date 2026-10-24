# Partial independent check of #4603's query-shear floor

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

Matarener's #4603 (head `caab2b42`) argues that the 15 query-only shears of the p16 controllers cannot be removed by three routes: fusion, lazy central frames, or cheap gather-type native words.

## What is checked here

Three of its statements are checked independently. Nothing is imported from #4603.

1. **Exact identity.** S_x(−Q)·S_y(Q⁻¹) = signed_swap·diag(Q⁻¹, Q)·S_x(Q), with:
   - S_x(a) = [[1, a], [0, 1]] and S_y(b) = [[1, 0], [b, 1]];
   - signed_swap = [[0, −1], [1, 0]].

   This is checked by exact symbolic Laurent-polynomial arithmetic, and the product equals [[0, −Q], [Q⁻¹, 1]]. A wrong-sign control is rejected.
2. **The premise of the window bound,** on main's pinned complex `CONTROLLER.json`:
   - each of the 15 QUERY_SHEAR events on pair j is preceded, since the last LOCAL event on pair j, by **only ADD and IDLE** events;
   - the 15 windows [that LOCAL, the shear] are pairwise disjoint.

   Hence any scheme that pays at least 1 per window pays at least 15, which the controller attains. An inserted SIGNED_SWAP is detected as a control.
3. **The merge bound.** Merging one query's 112 rank-one jobs into 14 rank-eight jobs saves 112 − 14·8^(1−0.0030202) ≈ **0.701 < 1** unit of paid moment, as stated.

## Verify

```text
python3 -B research/pr4603-shear-floor-check/verify.py
```

The check takes about 1 s and uses the standard library only.

## Limitations

**Not re-checked:**

- #4603's fusion-rank statement (part 1);
- the distinct-query-line census;
- the BIT controller's windows (only the complex controller is checked here);
- the parity model's cost rules themselves (this package checks the window premise those rules use).

## Open next questions

- **Fusion composites.** Recompute #4603's Q-coefficient ranks with an independent Laurent-matrix engine, then repeat the window premise for the retained BIT controller. First step: locate the BIT controller's event list among main's records.

Credit: Matarener (Mark) for #4603; 1337isnot1337 / Cinna Davis (#4440, #4470) and zxv for the controllers. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
