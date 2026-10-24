# TI_SP-inspired Levi-adaptive native gauges

The concrete connection from MathProof's TI_SP proof is the combination of **support-restricted substitution** and the **Levi homomorphism** A ↦ diag(A,A^−T). It suggests changing a gauge while processing different active coefficient groups, then deriving the backward program as its inverse dual. This package implements that idea: **666 → 616 scalar allowance per orientation**, with no extra fields and no new recursive calls. It also reduces the worst backward additive scalar-defect factor from 4,879 to 4,871 in the explicit logical-noise model of #4510.

The TI_SP proof's Levi embedding is classical, as its own attribution says. The class equality itself is not an algorithmic speedup. The source-bound adaptive schedule and cost theorem below are the contribution; no absence-of-prior-art claim is made.

| Four native windows | Original | #4502/#4505 | New |
|---|---:|---:|---:|
| 1 × 38 row | 418 | 358 | 316 |
| First 3 × 2 repeated-input block | 52 | 42 | 42 |
| Second 3 × 2 repeated-input block | 52 | 42 | 42 |
| 16 × 11 sparse block | 244 | 224 | 216 |
| Total per orientation | 766 | 666 | 616 |

The new row compiler is optimal within a precisely stated family: each original nonzero ADD is executed once, sources are unchanged, only the target is scaled by powers of two, and ADD order is free. It is not optimal among all arithmetic circuits. The two 42-cost borrowed adapters are inherited and explicitly credited.

## Complete native and error checks

| Complete THREE-base word | Original | #4505 | New |
|---|---:|---:|---:|
| Forward scalar allowance | 158,120 | 158,020 | 157,970 |
| Backward scalar allowance | 158,168 | 158,068 | 158,018 |
| Forward uniform logical ADD/SCALE defect factor | 1,328 | 1,328 | 1,328 |
| Backward uniform logical ADD/SCALE defect factor | 4,879 | 4,879 | 4,871 |

Both full native programs pass the retained independent literal and prefix loops on all 632 arbitrary persistent inputs plus the original arbitrary owned C input. All 408 helpers are restored in logical coordinates, C exits zero, the paid profile/rank mass are unchanged, and the exact ideal prefix maxima remain `(457,32,32,32)` forward and `(169,5,21,64)` backward for row ℓ₁, coefficient, numerator and denominator. Actual field count is unchanged; the symplectic doubling is a proof device, not allocated runtime workspace or two orientations computed for free.

Suffix factors assume bounded additive defects of an entire logical field, isometric free warps, exact initial inputs and exact other modeled event classes. They are not a physical rounded-precision theorem or mantissa-bit guarantee. **No new κ is claimed.**

```sh
python3 -I -O -B research/levi-adaptive-gauges/verify.py
python3 scripts/research_package.py --package research/levi-adaptive-gauges
python3 -I -O -B research/levi-adaptive-gauges/emit.py --output /tmp/levi-native.json
```

NATIVE.json is the complete generated forward/backward word. RESULT.json contains adaptive intervals, all source-bound replacement rules, complete native receipts and per-output suffix ledgers. emit.py requires a fresh output path. PRECEDENTS.json binds the exact inspected TI_SP source hash and retrieved DAG declarations; no fresh Lean audit is claimed. Standard-library Python only; Windows tested, Linux execution unavailable.

## Open next questions

1. Bind the improved suffix ledger to actual physical rounding and rank-dependent recursive defect contracts, including annotation/coordinate-conversion errors. This is the first step toward a rounded-induction contribution; the current local scalar saving does not change the paid recurrence by itself.
2. Extend the interval theorem to coupled source/target gauge paths only after specifying complete restoration, scalar charges and both dual interfaces. First compare against this exact restricted optimum; a symplectic lift alone does not make a coordinate change free.
