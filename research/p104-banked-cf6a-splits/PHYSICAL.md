# Physical accounting

All coefficients fit in 13 bits.

The recursive row-denominator bound changes from #7708's `2025 × 2²⁰` to `2,083,725 × 2²⁰`. The new odd factor `1029 = 3 · 7³` comes from the split coefficients. It is the same odd grid that #7697 uses for its chart-595 split. Native entrance and exit conversions scale by the new odd factor.

The paid edge count and every paid route are unchanged: 6,121 rows per native.

The public width rises from 1,501 to 1,504, adding three fresh helper owners per native invocation. Under #7708's home count `2n + k + 5`, the private homes go from 9,128 to 9,134 per native.

Nonzero local terms rise from 177,531 to 179,874 per native, from the input encoding, the injections and the output decoding. Under the #7682 service formulas, our recount gives:

| Per native | #7708 | This circuit |
| --- | ---: | ---: |
| Reset services | 1,517,724 | 1,536,516 |
| Selected transfer legs | 413,036 | 417,740 |

The same recount reproduces #7708's published 413,036 transfer legs exactly. Its reset count, 1,517,724, is within 2 of the published 1,517,726 because the home formulas differ by two homes.

Scalar services rise by 2,343 × 32 per native.

All of these charges are finite constants absorbed in the funded compiler margin of the selected finite-template substitution, as in #7697 and #7708.
