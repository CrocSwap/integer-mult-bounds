# Independent check of #4623's idle-mass bookkeeping and tangent bounds

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

dillona's #4623 (head `fd5d3be1`) deletes the whole-idle stages and bounds what this can save. Its BUDGET.md says that:

- the complex p16 main output mass falls from 177,408 to 35,840, with the idle mass cancelled exactly;
- tangent bounds A(t) and B_J(t) are negative at C = .006 (complex) and C = .007 (BIT).

Nothing is imported from #4623.

## Results

- **Masses.** From main's pinned `joint-helper-lattice/CONTROLLER.json`, the main target mass is **177,408** and the idle paid mass is **141,568**. Their difference, **35,840**, equals #4623's determinant formula M_p = 2v[p + b(p+2)] with v = 112, b = 8 and p = 16.
- **Tangent bounds.** The engine is 40-digit Decimal, with h(t) = local helper moment − local paid moment:
  - complex: PR4470's lists, v = 112, b = 8;
  - BIT: 439 H8 helpers against the PR589 local paid list, v = 111, b = 7.

  The results match #4623's printed values to every digit, and all are negative:

| inventory | C | A(t) | B_J(t) |
|---|---|---|---|
| complex | .006 | −2.6366097978 | −132.6282065738 |
| BIT | .007 | −3.5731057049 | −133.1717283853 |

- **Monotone extension (separator premise).** The equal-rank signed terms of h are positive only above the separator (complex: ranks 7, 8 and 9 above 6; BIT: rank 8 above 7.5) and negative only below it. The Jensen base 1 + b + 2b/p lies above the separator and the rank-one thin queries lie below it. So J_p(t)/separator^t increases in t, and the exclusion extends to every larger saving, as #4623 states.

## Verify

```text
python3 -B research/pr4623-budget-check/verify.py
```

The check takes under 1 s and uses the standard library only.

## Limitations

**Not checked:** the repeated-evaluation and decoder barriers, and the precision lemma.

## Open next questions

- **Decoder barrier.** Check #4623's copied-input decoder rank p − 1 independently. First step: rebuild the per-port query matrix for p = 2 and 3 exactly.

Credit: dillona (Dillon) for #4623; Cinna Davis and the #4440/#4470/BIT lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
