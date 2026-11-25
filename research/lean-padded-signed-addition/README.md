# Paid signed layout and seven-tape addition

This package contains six accepted generic Lean 4.21 modules. They extend the
public paired/marked XOR head primitives in PR1840 and the counted adder/padding
machines in PR1869, without copying those four public source modules.

## Exact implemented result

Two source words are finite low-bit-first Boolean lists with separately supplied
sign bits. Two unary controls specify independent nonnegative shifts dx and dy.
Seven tapes hold the original source words, both unary controls, two generated
padded words and the final sum. Source/control words are initially marked;
three output workspaces start empty. The finite controller executes both padding
runs, two charged switches, actual sign extension/pair copying and marker/sign-row
writes, a third charged switch, then the marked ripple adder. All seven tapes are
retained and counted. All final heads return to their specified markers.

For LA=dx+length(xs), LB=dy+length(ys), M=max(LA,LB), the actual first halt is
19M+7(LA+LB)+89 transitions. Every prefix has at most 2(LA+LB)+M+16 represented
tape cells. The actual output word represents
2^dx*signedValue(xs,sx) + 2^dy*signedValue(ys,sy).
Both extra sign columns are written and executed; empty words and zero shifts
are included. There is no supplied endpoint equation or uniform running-time
hypothesis.

The actual entrance volume V is measured from all seven tape fields and equals
LA+LB+8. The executed trace gives time at most 26V and represented cells at most 3V
at every prefix. The fixed Boolean registers, sign bits and finite control are
additional constant storage. These counts are for the stated finite-alphabet
multitape model, with one bounded symbol/register/head transition as one step.

## Remaining boundary

The caller supplies marked source words, signs, unary controls and blank disjoint
workspace. Converting selected Cell numerators/exponents to this encoding,
computing binary exponent differences and producing unary controls, restoring
arbitrary overwritten scratch/output, physical address allocation and any
single-tape simulation are separate obligations. The coefficient 26 is derived
for this prepared routine; it is not the selected program's missing uniform C.
Other selected events, recursive payload partition, complete physical execution
and the all-size multiplication bit-cost theorem remain open.

## Modules and retained public inputs

Public dependencies are immutable PR1840 head
3f1b0641d5866f9d0b6cdd8e46db416fed6c5645 and PR1869 head
65ab016b4a464e3f5e2dd26c1bb0ae477e1ebce8. Fetch them into caller scratch using
REPRODUCE.md; they are not vendored here. Compile in the recorded order:

1. Public PairedBitXorScan and MarkedBitXorScan
2. Public SequentialBitAddition and MarkedZeroPadding
3. SignedWordAlignment and MarkedBitAddition
4. MarkedPairLayout, MarkedLayoutAddition, PaddedSignedAddition
5. PaddedAdditionLinearInvoice

The six new sources have 41 complete axiom probes and 10 full type checks.
All observed axioms belong to Lean's standard propext, Classical.choice and
Quot.sound set, and the accepted checks have no diagnostics. ACCEPTANCE.json
records the exact source hashes, independent reviewer roles, public prerequisite
pins and the scope of each accepted result. Reproduction commands are provided
in REPRODUCE.md for an existing aligned Lean/Mathlib installation.

Historical source comments saying uncompiled are preserved byte-for-byte;
the source-bound acceptance summary records the later checks. No compiled
object binaries or internal execution artifacts are included.

## Attribution and selected context

James Chang, Apache-2.0, with OpenAI assistance. Reuses the accepted analytic
padding/alignment work, machine marked-adder and public PR1840 tape primitives.
The author-checked selected context is
kappa = 836330098538459/500000000000000000 = 0.001672660197076918,
with certificate SHA256
1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045.
These generic machines introduce no new selected exponent or unconditional
multiplier claim.
