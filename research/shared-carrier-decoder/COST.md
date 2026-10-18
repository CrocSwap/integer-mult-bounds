# Complete local invoice

The baseline and candidate have the same 111 source streams, 111 target
streams, and 452 dirty helper streams. Each stream has `M` complex values.
The executed finite case has `M=512`. Every copy and adapter keeps the full
stream, including all control and spectator values.

## Recursive children

Every transition is lowered to one rank-r C child with two native monomial
adapters. No positive-rank transition is omitted.

| Role or operation | Coordinate baseline | One replacement |
|---|---|---|
| 111 sources, line to FULL | 111 H8 | 111 H8 |
| Use helpers, zero to line to query to FULL | 444(2 H1+H7) | 441(2 H1+H7) |
| Eight centres, zero to query to FULL | 8(H8+H1) | 8(H8+H1) |
| COPY transforms | 8 H8 | 7 H8+H7 |
| Targets | 111 H8 | 56 H8+55(H1+H7) |
| Unused dirty helpers | 0 | **3 H9** |
| Total | 896 H1+444 H7+238 H8 | 945 H1+497 H7+182 H8+3 H9 |

The difference is the sum of three paid changes:
`55(H1+H7-H8)` for target splits, `3(H9-2H1-H7)` for the inactive helpers,
and `H7-H8` for the changed COPY. It is therefore
`49 H1+53 H7-56 H8+3 H9`. Rank mass falls from 5908 to
5907, while the number of recursive children rises from 1578 to 1627.

Under a common child price `r(m/r)^b`, the recursive difference is

```text
(m/8)^b [49*8^b + 371*(8/7)^b - 448 + 27*(8/9)^b].
```

For `0 <= b <= 1/256`, the exact integer checks

```text
1009^256 > 8*1000^256,
7*1001^256 > 8*1000^256
```

bound the square bracket above by

```text
49*(1009/1000) + 371*(1001/1000) - 448 + 27 = -47/250.
```

This proves a strict recursive-moment improvement on the whole interval. It
includes the selected complex value
`416181814685169713943/250000000000000000000000` at the pinned base. The
formula is conditional on that child price. It does not construct an all-size
embedding or change the selected supplier.

## Scalar, adapter, and temporary work

| Scalar stage | Coordinate baseline | One replacement |
|---|---:|---:|
| Gather old helpers | 444 | 441 |
| Compensate old centre output | 444 | 507 |
| Remove old helper gather | 444 | 441 |
| Read sources | 444 | 441 |
| Gather updated helpers | 444 | 441 |
| Read transformed copies | 444 | 507 |
| Restore centres | 444 | 441 |
| Restore use helpers | 444 | 441 |
| AXPYs per address | 3552 | 3660 |

Each AXPY charges one complex scalar addition. An AXPY coefficient of absolute
value 1/2 or 1/4 also charges one dyadic scalar multiplication. Their counts
are 888 and 1014. Negative signs are included in the scalar operations.
The candidate therefore pays **108 extra AXPYs and 126 extra dyadic scalar
multiplications per address**.

Each native monomial adapter contains a permutation P, a quadratic phase D,
an XOR translation X, and a global phase. The emitted word retains identity
instances and charges them too. Each of these four types occurs 3156 times
in the baseline and 3254 times in the candidate. The increase is 98 scans
per type, or 392 adapter scans in total. The literal finite interpreter also
executes 5908 and 5907 coordinate C factors, respectively.

In the forward orientation each word charges eight complete-stream copy
assignments, eight erasures, and all scatter reads in the AXPY table. In the
inverse transpose, replace those eight assignments with eight zero scans
and add eight centre-injection AXPYs. The recursive profile and all adapter
counts are the same. These orientation costs do not cancel from the invoice;
only their difference between the matched modules is zero.

There are 674 original complex streams and one sequential temporary stream.
Thus there are at most `675 M` live complex values in the physical word.
The finite interpreter applies permutations by cycles and C and X gates by
pairs. Scalar arithmetic uses a fixed number of complex registers. Its fixed
permutation cycles and phase tables contain address data only. The checker
also stores proof data, exact integer numerators, and expected outputs; that
checker memory is not a claim about supplier workspace.

## A finite route bound and the host boundary

The invoice concerns the emitted complex-arithmetic word. It is not a count of
Python big-integer operations in the checker. Integer normalization and expected
output construction are verification work.

The invoice counts all required arithmetic and address operations. It does
not treat an arbitrary address permutation as a free sequential tape scan.
At nine address bits, a direct P address circuit uses at most 256 Boolean
operations per value: its nine dot products need 81 ANDs and 72 XORs, with
space in the bound for packing the output bits. A D phase needs at most 144
Boolean operations: 54 for the nine linear terms modulo four, 71 for the
quadratic parity, and one final XOR. X and a global unit phase use bounded address or scalar work.
These are fixed finite costs. A recursive child retains its full input volume.

Here is a conservative route implementation for the finite word. Put the 675
complex streams consecutively. A requested cell read or write can move the
head at most `2*675*M` complex-cell positions. An AXPY uses at most three cell
accesses per value. Each P, D, X, global-phase scan, or coordinate C factor
uses at most two per value. A copy assignment uses two, and an erasure uses
one. If `A` is the AXPY count, `B` is the sum of the four adapter scan counts,
and `R` is the rank mass, the forward access count is at most

```text
M K,  where K = 3A + 2B + 2R + 24.
```

The resulting route bound is `2*675*K*M^2` complex-cell moves. The inverse
transpose adds at most 16 accesses per address. For bit cells, multiply cell
width and charge the address counters. Exact integer arithmetic also has its
usual bit cost. No linear tape-time bound follows from this deliberately
simple route.

A future host must supply and charge its complete-row routing interface,
external endpoint adapters, remaining side corrections, recursion storage,
precision control, and owner schedule. Those objects are not silently set to
zero here. They are outside the advertised finite decoder interface.
Consequently this result is a new exact local physical module with a smaller
paid recursive moment, not a measured speedup or an improved kappa.
