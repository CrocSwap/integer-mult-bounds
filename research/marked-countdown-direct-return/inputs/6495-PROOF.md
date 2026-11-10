# Cached borrow termination and the exact saving

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

Use the exact Tape and Counter ABI pinned in SOURCES.json. A tape read returns
its current symbol and increments the read meter. It neither changes the tape
nor moves its head. The caller supplies a positive canonical Counter, with its
head at the first binary digit. Its private tape has a LEFT delimiter, a
little-endian binary numeral, a RIGHT delimiter and blank exterior. The finite
control flag `finished` is false. No concurrent writer changes that tape.

The inherited decrement changes a current value x to x-1, shortens the top
marker when necessary, sets `finished` at zero and restores the head. The
constructor and `close` operation are retained literally. Their algorithms and
correctness retain Jose Manuel / PR2697 and the retained library's credit.

## One-step equivalence

Write k for the number of trailing zero digits in x. Positivity and canonical
encoding ensure k is finite and that the next digit is ONE. In the inherited
program, the condition `while tape.read() == ZERO` reads those k zero digits
and then reads the terminating ONE. Each visited zero is changed to ONE. After
the condition fails, `need(tape.read() == ONE, ...)` reads that same ONE again.
There is no intervening write or head move.

The new program retains the symbol read by the condition in the finite variable
`digit`. It tests `digit != ONE` without performing another tape read. This
variable has only the fixed tape-symbol alphabet as its range. It contains no
numerical count, address, bit length or ripple length.

All subsequent writes, moves, tests and the final rewind are identical. Thus
one valid decrement has exactly the same tape contents, head and `finished`
flag, the same write count and the same unit-move count, and exactly one fewer
read. This includes k=0, a power of two, and x=1. The invalid-terminator and
already-finished rejection conditions remain. A valid decrement traverses at
most the current encoded digit width before finding its terminator.

Induction applies the same statement to every subsequent decrement. From an
initial N, the complete countdown performs exactly N decrements. Constructor
and disposal do identical work on identical states, so the complete saving is
exactly N reads, with zero change in writes or movement. At N=0 it is zero.

## Complete countdown invoice

Arham Tahir / PR2877 supplies the original complete constructor, normalization,
N-decrement and disposal invoice for d input digits, including input-word
reads and head restoration. For d >= max(2, bit_length(N)), it is

```
15N + 14d - 5 popcount(N) + 36,  N > 0,
14d + 40,                     N = 0.
```

Its invoice is a cited predecessor result, not a new audit deliverable. The
proved exact trace saving gives the new complete invoice

```
14N + 14d - 5 popcount(N) + 36,  N > 0,
14d + 40,                     N = 0.
```

The stronger conclusion that each operation category changes by `(N,0,0)`
does not depend on that closed-form predecessor invoice.

## Exact saving in the retained sign caller

Consider the unchanged sign-address algorithm with modulus M>=2, B>=1 outer
rows, and S>=1 suffix bits per atom. Use the new decrement in every Counter
reached by that call. This substitution changes no constructor, branch,
cardinality, numerical primitive, payload operation or counter inventory.

The following table counts decrements, not merely Counter allocations.

| Counter use | Total decrements |
| --- | ---: |
| Outer row loop | B |
| Two forward-skip block loops per row | 2B(M-2) |
| Their suffix loops | 2B(M-2)S |
| Nonzero-atom loop | B(M-1) |
| Two backward suffix loops between nonzero atoms | 2B(M-2)S |
| Payload copy suffix loops when S>1 | BMS |

At S=1, the literal copy routine uses its one-bit branch and allocates no
suffix counter. At M=2, the zero forward skips still construct and close
zero counters, which save no decrement reads. Hence the exact complete-call
saving in reads is

```
D(M,B,S) = B [3M-4 + 4(M-2)S + M S 1_{S>1}].
```

Writes and moves are unchanged. This is positive throughout the declared
parameter domain. In particular, the new implementation saves 443 reads at
(M,B,S)=(65,1,1), and 7,230 at (65,3,7). Both are executed fixtures. All
constructor, cleanup, source and numerical traffic is retained in the measured
complete interval, so these savings are not a per-decrement microbenchmark
extrapolated to an unexecuted caller.

## Evidence and limits

The verifier checks every intermediate canonical state for 387 count/padding
fixtures and 24,768 decrements. It meters old and new private tapes separately.
It then executes both complete sign calls on 30 shape fixtures, records every
output's source coordinate, verifies the literal output bits, checks all closed
counter tapes and numerical temporary returns, and compares the complete
read/write/move deltas with D. Runtime numerical inspection is forbidden.
Provenance tracking and post-execution integer decoding are verifier observations.

The written induction is the all-parameter argument. The finite cases alone
are not its proof. This is an exact logical-tape improvement, not a wall-clock
speedup, optimal transducer, machine compiler, full H2 proof, admitted supplier,
new kappa or complete multiplication theorem. No selected frontier changes.
