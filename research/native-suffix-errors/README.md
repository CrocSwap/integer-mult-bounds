# Suffix-weighted logical error certificates for the complete native word

This continues [#4505](https://github.com/CrocSwap/integer-mult-bounds/pull/4505)'s explicit missing suffix-sensitivity task. It computes exact free-word responses to an additive logical defect after **every scalar, warp, climb and center event** in both complete original and rewritten THREE-base native words. The output is a proved sufficient perturbation bound with explicit per-output/per-event-class coefficients. It is **not a new κ or the full rounded recursive induction**.

## Concrete sufficient guarantee

Assume each entire-field ADD and SCALE introduces an additive defect of norm at most δ in the retained logical chart model; other event classes are exact, initial data are exact, and free warp operators act isometrically in the chosen norm. Then every one of the 632 persistent output errors has norm at most:

| Word | Original | #4505 rewrite | Extra logical defect bits sufficient for target 2^−b |
|---|---:|---:|---:|
| Forward | 1,328 δ | 1,328 δ | 11: δ ≤ 2^−(b+11) |
| Backward | 4,879 δ | 4,879 δ | 13: δ ≤ 2^−(b+13) |

Thus the 100-unit scalar saving of #4505 preserves these worst-output error coefficients. The bit statement concerns the absolute defect of an **entire logical field**, not a floating-point mantissa or a per-coordinate rounding quantum. Actual physical/recursive implementations must supply those contracts separately.

The certificate supports unequal defects: each output has a rational weighted sum over ADD, SCALE, CLEAR, COPY (where present), warp and each paid rank class. The API requires an explicit nonnegative budget for **every** present class; a missing unknown is rejected instead of treated as zero. Initial persistent input error at most E₀ adds at most 2 E₀. PROOF.md also supplies a quantitative feedback-absorption corollary for caller-provided recursive defect contracts.

Worst-case equality does not mean coordinatewise nonregression. The rewrite changes 33 forward and 90 backward row bounds; individual bounds rise by at most 2 and 12, respectively. The complete rational row ledger is retained. For ADD-only noise with all other classes exact, the backward class maximum changes from 4,308 to 4,300; this does not assume SCALE is exact in a real implementation.

## Replay

```sh
python3 -I -O -B research/native-suffix-errors/verify.py
python3 scripts/research_package.py --package research/native-suffix-errors
```

The verifier authenticates main inputs, regenerates #4505's guarded rewrite, checks the complete reverse-response endpoint on all 633 initial variables, and checks sampled complete suffixes against independent forward error injection. It also checks 720 all-event impulse responses from 30 small programs in both orientations, including noncommuting warp words, clear, copy, negative scalars and cancellation. Exact class budgets and malformed-budget controls are included.

`RESULT.json.results.rewritten.forward` and `.backward` each contain the per-output rows. `suffix.py.bound_from_rows(receipt, defects)` returns their exact worst weighted bound. Use a verified/recomputed receipt; the function is an evaluator, not an authenticator of arbitrary caller-supplied certificates.

Standard-library Python; Windows tested. No Linux execution was available. The shared canonical DAG and selected frontier remain unchanged.

## Open next questions

1. Bind physical rounding and recursive-callee defects to the precise post-event logical norm used here, including dimensions, normalization and conversion errors. Supply explicit budgets for all classes; this package does not declare unknown implementation errors zero.
2. Use the row ledger with actual rank-dependent recursive error contracts and the feedback theorem in PROOF.md to close the rounded induction. Ideal adapter/residual_adapter annotations have no modeled state update or noise here; any physical error they introduce needs an explicit conversion into supported injection sites or a separately extended model.
