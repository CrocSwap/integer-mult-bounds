# Helper 757 receives the change in helper 1255

The source is PR7604 head `ba2638c5a6e2b9a1c0c559a41811e5d41a591f41`.
All event indices below are zero-based in that source word. The complete caller
is the unchanged PR7113 signed 17-call construction. Current main at intake is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.

## Exact identity and legal contacts

Let `x` and `y` be the values of 757 and 1255 before event 33518. Both are in
chart 3. Let `u` be the value of 902 at event 38582, and let `v` be the value of
owned field 1557 at event 42710. No instruction changes 902 before its later
read at 38585. No instruction changes 1557 before its later read at 42714.

The only writes to 1255 between 33518 and 42716 are
`1255 -= 902` at 38582 and `1255 -= (2/3)*1557` at 42710.
Its MOVEs are `3→595` at 38295 and `595→603` at 42712. Thus its later value is

`y_late = y - u - (2/3)*v`.

The old 757 enters 595 at 38584, subtracts the same `u` at 38585 and the same
`(2/3)*v` at 42714, then enters 603 at 42716. No instruction reads 757 after
33517 and before 42717. Its required exit value is `x - u - (2/3)*v`.

The new word does this:

1. Before 33518, apply `757 -= 1255` in chart 3.
2. Remove the old MOVE at 38584 and incoming ADDs at 38585 and 42714.
3. Replace 42716 by `MOVE 757 3→603`, then `757 += 1255` in chart 603.

The result is `(x-y)+y_late = x-u-(2/3)*v`. The donor 1255 does not change.
All its intermediate reads therefore keep their original values. The first
later read of 757, at 42717, sees the original value. Every other instruction
keeps its original relative order. The early subtraction must occur after
33517, which reads 757 into 1143; the checker rejects crossing this boundary.

This argument treats `x`, `y`, `u` and `v` as arbitrary values. It does not
assume that a dirty public input is zero. It introduces no COPY, INIT, CLEAR,
owned field, lifetime or paid donor route. The old 1557 CLEAR remains at its
original chart and retains its actual erased row. The helper target and both
public endpoint charts remain unchanged.

## Physical action

Charts 3, 595 and 603 have dimensions 0, 1 and 2, with strictly nested spans.
The old paid maps compose as `F603 * F595^-1 * F595 * F3^-1`.
The new map is `F603 * F3^-1`, with rank 2. Ordinary ADDs occur only when both
operands have the same chart, so the scalar identity transfers to the physical
word. The exact Gaussian interpreter checks all 512 forward columns and all
512 adjoint columns, including absolute phase. Wrong-source and global-phase
controls reject. The complete application also rebuilds all 38 affected
lineage pairs and all 3,040 catalogue maps, with 104 main boundary pairs.

## Complete cost and κ

The native delta is `P1 -= 2, P2 += 1`. Across 17 calls it is
`P1 -= 34, P2 += 17`. The complete paid count falls from 110,383 to 110,366.
All 22,461 productive fields remain. The target-minus-paid rank surplus stays
1,424. At `0 < C < 1`, the exact moment improvement is

`17 * (2 - 2^(1-C)) > 0`.

Two independent directed engines certify the full old and new invoices.
One uses integer square roots and dyadic products; the other uses directed
logarithm and exponential series. Both reject the old invoice at the new
claim. Both enclose the new crossing in
`(0.0036504442447168877, 0.0036504442447168879)`.
The public claim `0.0036504442446` exceeds PR7604's certified upper bound
`0.0036502223358273` by `0.0000002219087727`.

For `F(C) = sum_r (T_r-P_r) r^(1-C)`, the directed derivative upper bound is
negative throughout `[0, 0.00376669]`. Therefore the crossing is unique on
that inherited BIT interval. This is a ceiling for the fixed complete invoice;
it is not a ceiling for changed words, stock or callers.

The fresh signed application supports the stronger claim
`0.003650444244716`. Its ordinary bound is **782,699,212 < 10^9**. The exact
native grid remains `1125 * 2^25`, and the complete precision factor remains
**2430**. The finite tape charges 298,502 monomial map slots, at most
25,451,474,528 elementary records, and 43,923,200 scalar services. The complete
caller has 13,600 physical native contacts. All 54 strict and four functional
outer predicates pass, including the public claim and its positive slack.

## Coverage and limits

The forward and reverse exact interpreters agree on all 1,569 final rows and
all 74 erased rows. They compare against PR7604, including every arbitrary
public input, helper identity, actual COPY-zero condition, owned path, live
peak and endpoint chart. Four changed-word controls reject the omitted early
subtraction, omitted late addition, omitted paid MOVE and crossed earlier read.

The discovery screen first found no nominee among 1,033 current receive-only
pairs with stock fixed at the two cuts, including a free-scale extension.
A changed screen allowed actual timed stock from the source chart before the
fused MOVE and from the destination chart before the next read. It produced
one modular nominee, this 757/1255 construction; the exact solution has three
terms and scale 1. The other cases were not all proved impossible over the
rationals. No general optimality follows. The finite search is local research
evidence; the published verifier proves the explicit construction directly.

The five inherited assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The source-bound finite
application has not materialized the full multiplier or discharged these
assumptions. No independent human or formal-kernel approval is claimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Retain the
credits in README.md, NOTICE and every frozen source.
