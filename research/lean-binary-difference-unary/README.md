# Counted binary difference and unary control

Four exact checked modules implement a reusable preparation path for dyadic exponent alignment. They do not execute Nat subtraction or decode an unbounded integer as a unit-cost operation.

1. BinaryToUnaryControl scans a supplied little-endian binary counter, repeatedly performs explicit finite-bit borrow sweeps, and writes one unary tick for each successful decrement. It writes both markers, returns both heads, clears borrow and consumes the counter to zero.
2. PairedDifferenceArithmetic reuses the seven Boolean adder gates with complemented operand reads and true carry-in. Carry-out derives order, including equality and width zero.
3. MarkedBitDifference executes that scan on a marked paired word, branches on the actual carry, runs the opposite pass on underflow, and physically copies the nonnegative result into a fresh marked one-bit tape. Both source operand tracks remain.
4. PairedDifferenceUnary charges one controller transition into the unary producer and retains the complete three-tape state, direction flag and cleared register frame.

## Derived counts

For paired width w and derived numeric difference d:
- Binary-to-unary: exact first halt d*(2w+6)+2w+8; every-prefix represented cells at most w+d+4.
- Difference/extraction: exact first halt 17w+22 if the first carry is true, otherwise28w+28; every-prefix cells at most2w+4.
- Joined controller: exact sum of those actual times plus one, hence at most d*(2w+6)+30w+37; every-prefix cells at most2w+d+6.

These costs are in numeric magnitude d. Producing d unary cells can require exponential time/space in the encoded width. Fixed finite control and Boolean registers are separate constant space. Bounds include real marker cells and head returns.

## Explicit boundary

The initial exponent words, equal-width paired layout and marked input allocation are supplied. Leading-zero words and width zero are allowed. Work outputs start blank. The binary work counter is zeroed; old scratch/output storage is not restored. Physical allocation/simulation, downstream branch-selected padding/routing and the complete selected recurrence remain open. The later unsigned paid-layout composition is deliberately excluded.

## Reuse and acceptance

Five unchanged prerequisites are fetched from public PR1840, PR1869 and PR1899 at the exact heads in ACCEPTANCE.json. None is duplicated in this package. The four new sources have34 complete standard-only axiom probes and7 printed types. Independent source/API and native terminal reviews passed. The only accepted diagnostic is PairedDifferenceUnary's unnecessarySeqFocus style warning and its note; no sorryAx is accepted. See REPRODUCE.md for exact source checks and serial compile order against existing Lean4.21.0/Mathlib308445 dependencies.

Author: James Chang, Apache-2.0, OpenAI-assisted. Explicit author-checked selected context: kappa =836330098538459/500000000000000000 =0.001672660197076918. This context value is retained without claiming these generic routines close the full multiplication theorem.
