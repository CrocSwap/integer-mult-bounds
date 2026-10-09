# Generated numerical results

This file is generated from `certificate.json` and compared during verification.

The conditional saving is **kappa = 305534205135809/500000000000000000 = 0.000611068410271618**.
This exceeds PR168 by 0.23464917 percent; the comparison concerns the asymptotic exponent saving, not measured runtime.

| Quantity | Certified value |
|---|---:|
| Bit coarse saving | 0.000611792602908216 |
| Paid ordinary bit saving | 0.000611442043188922772764 |
| Complex saving | 0.000613954254891227 |
| Actual transfer saving | 0.000611442043188922772764 |
| Active supplier | bit |
| Changed bit operation frames | 2196 |
| Bit persistent stock | 25772 |
| Bit rank deficit | 1936 |
| Largest bit child | 60 |
| Complete fallback children per edge | 124842 |

The transfer uses `a = min(actual_bit_saving, (1-beta)*complex_saving - weakening)`.
Both the ordinary supplier and the strict complex leaf inequality are checked.
Every one of the 47 constraints and seven margins is strict; the next final grid point fails.

## Matched comparisons

| Construction and bill, with the same refined wrapper | kappa |
|---|---:|
| PR168 fixed word and rounded fallback | 0.000609860726957640 |
| PR168 fixed word and exact fallback bounds | 0.000609860728621245 |
| Selected checked word and exact fallback bounds | 0.000611068410271618 |

All finite frame, prime and scalar checks are separate from the inherited all-size interfaces. Those interfaces remain assumptions.
