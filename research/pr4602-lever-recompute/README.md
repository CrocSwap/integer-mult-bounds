# Independent recomputation of #4602's lever re-pricing

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

Matarener's #4602 (head `0dadb877`) recomputes the #1240 one-at-a-time ideal lever budgets on the current complete invoices: #4470's complex invoice and the retained query-thinned BIT invoice. It finds the root of Σ_T n·r^(1−C) = Σ_P n·r^(1−C) with exact interval arithmetic.

## What is checked here

The values are recomputed independently. Nothing is imported from #4602.

- **Complex invoice.** Rebuilt from main's pinned `joint-helper-lattice/CONTROLLER.json`, using PR4470's local paid list. The 8 H8 jobs per call are the owned centre.
- **BIT invoice.** Read from main's pinned `query-thinned-controllers/RESULT.json`: targets, paid, whole-idle and 15 × 111 thin queries.
- **Roots.** Each root comes from a 40-digit Decimal bisection. This engine differs from #4602's outward-rounded log/exp series.

| quantity | complex | BIT | #4602 |
|---|---|---|---|
| baseline raw root | 0.0030201659 | 0.0034642489 | 0.0030202 / 0.0034642 |
| paid-moment share: idle / local / shears / centre | 59.0% / 39.8% / 0.71% / 0.48% | 56.4% / 42.8% / 0.77% / — | 59/40/0.7/0.5 and 56/43/0.8 |
| centre free | 0.0076503 | — | 0.00765 |
| centre shared by two calls | 0.0053347 | — | 0.00533 |
| query shears free | 0.0099146 | 0.0113100 | 0.0099 / 0.0113 |
| two unpaid coordinates per idle family | 0.0282012 | 0.0318657 | 0.0282 / 0.0319 |
| free idle stages | 0.317 | 0.323 | > 1/6 |

- **Agreement.** Every recomputed value matches #4602 to the digits it reports.
- **Semantic control.** Substituting #4610's changed local list moves the complex baseline off 0.0030202.

## Verify

```text
python3 -B research/pr4602-lever-recompute/verify.py
```

The check takes about 2 s and uses the standard library only.

## Limitations

- **Two rows not recomputed:** the rank-16 local-children and rank-one pairing levers. They depend on #4602's merge rule.
- **Outer rows not recomputed:** strictification and the BIT ordinary conversion.
- **Root uniqueness** is not certified here, as in #4602.

## Open next questions

- **The remaining lever rows.** Recompute them once the local-job merge rule is fixed explicitly.

Credit: Matarener (Mark) for #4602; 1337isnot1337 and Cinna Davis (#4440, #4470), zxv (#4359) and the #1240 lever table authors. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
