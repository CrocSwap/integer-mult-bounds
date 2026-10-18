# Local sprint claim

No pinned sprint coordination issue existed on 2026-10-13 (the only open issue was #650), so the claim is recorded here.

- Track: 20–39, complex supplier. Seed **28**, drawn from the operating system's CSPRNG with Node.js `crypto.randomInt(1, 61)` at 2026-10-13T07:45:49Z (range 1–60 as instructed for this run).
- Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631` (selected κ = 0.001661634653669567, #799 with #589 on #555; the complex side binds).
- Object: the frame schedule of the selected complex word, PR799's X4 word (content `1e1d99ba…`), all A, B and early-cleanup gates.
- Method: complete F₂ frame intervals, local-polytope LP and symbolic exact duals (the #557 method), with a standard-library verifier and two pinned moment engines.
- Expected deliverable: a constructed frame improvement if the LP found one, otherwise a scoped exclusion at the next 10⁻²⁴ tick.
- Expected finish: same day.

## Candidates considered

1. **Residual low-end capacity on X4.** For each helper ending at FULL, join the end-of-B frames over its inverse-row and dirt-column cones (the two cone conditions of `audit_local.py`). Result: all 216 fresh and 162 entering FULL-ending helpers have a 9-dimensional join, so no new low end exists without a scalar change. This matches the p6n note's "2 a-type units" estimate, which concerns new premix directions rather than the fixed program. Not packaged.
2. **Joint entrance-promotion and frame search.** Every entering helper's first gate sits exactly at its entrance frame, so any promotion must raise a partner's frame. Pricing a promotion needs the owner-packing model, because freed width changes the idle profile (#850 covers only the current inventory). A rough packing-free bound, pricing all idle mass as rank-51 children, gains about 11.6 moment units (×mW) from repacking alone, roughly 17 times the X4 step (0.67), so it decides nothing. Not pursued.
3. **Exact frame-assignment optimality of X4 (chosen).** #815 covers PR699's SW4 word with floating-point solvers and fixed tail frames, and #776 covers #626's words. The #799 review keeps the X4 frame-optimality report as a search report. No open PR claimed X4 when this work started (snapshot through #857).

Overlap was refreshed again before submission; see the pull request description.
