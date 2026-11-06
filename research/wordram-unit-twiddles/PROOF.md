# A two-instruction unit-twiddle refinement

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Contract and cited inputs

Use David Ganz / Dugongue's bounded multiplier from PR #5466, retained at
`research/wordram-ntt-kernel/`. Its literal 64-bit Word RAM semantics, exact
NTT schedule, all-input multiplication theorem and range invariant are cited
inputs. They are not re-proved or audited here. In particular, at every
transform butterfly the multiplicand b is an integer in [0,65537), ZERO
contains zero, the threshold cells 20+i contain p*2^i for p=65537, and the
twiddle cell contains the requested residue. Inputs have 1..256 hexadecimal
digits. The generated transform size n is a power of two at most 512.

The new result concerns the exact emitted program, including its complete
memory, scratch values, branch targets and instruction count. No selected
supplier admission, asymptotic saving or proof-kernel verification follows.

## Local full-state equivalence

At a constant-one twiddle, the original 49-instruction macro is

```text
mul VALUE, b, one_cell
for i = 15,...,0:
    sub TEMP, VALUE, threshold_i
    bltz TEMP, after_copy_i
    add VALUE, TEMP, ZERO
```

The loop is notation for a completely unrolled instruction list. Every
subtraction has signed value b-p*2^i < 0, with absolute value below 2^32.
There is no signed overflow. Therefore every branch is taken and every copy
is skipped. At exit VALUE=b and TEMP=b-p modulo 2^64. All other cells have
their incoming values. This macro executes exactly 1+2*16=33 instructions.

Replace it by these two literal instructions:

```text
add VALUE, b, ZERO
sub TEMP, VALUE, threshold_0
```

The exit memory is identical at every address, including TEMP. The replacement
uses the same write addresses and preserves arbitrary incoming dirt elsewhere.
It saves exactly 47 static instructions and 31 executed instructions. This
identity holds for every b in the admitted residue interval; it does not
require any particular original values in VALUE or TEMP. It also explains
why the second replacement instruction is retained.

## Binding replacements and relocating control flow

The source files are authenticated before importing the producer. The
transformer accepts only the direct-address instruction subset emitted by
that producer, with forward branches and a terminal accept. It identifies a
unit cell by its complete write inventory: one `one` initialization and one
final `sub cell,cell,cell`, with no intervening writes. For the pinned
producer these initializations execute before use; its conditional skips
only omit modular-reduction/carry updates, not literal initialization.

Only a `mul` into the retained VALUE cell with such a unit operand qualifies.
The transformer checks every instruction and branch target in the following
49-instruction macro, checks the unit's lifetime and excludes data aliasing
with VALUE, TEMP, ZERO or a threshold cell. Its structural gates alone are
not a soundness theorem for arbitrary
programs: coefficient bounds, setup and executed initialization remain the
cited producer premises. Corrupt source bytes are rejected before assembly.

Partition the original instruction list into replacement blocks and singleton
unchanged instructions. Map each block entry to its new instruction index.
Every surviving branch must target such an entry; a branch into the interior
of a removed macro is rejected. Translate all surviving labels by this map.
The removed internal branches have exactly the local behavior proved above.

Induction over executed blocks now gives equal complete memory at corresponding
entries. Unchanged conditional branches take the same outcome because they
read equal values. Replacement blocks reach equal memory at their mapped exit.
Thus both programs reach accept with identical complete memory, including all
operand, output, scratch, temporary and exterior addresses. All setup, literal
synthesis, carry normalization, final clearing and halt instructions remain
charged. The new program is a direct-address literal program in the same ISA.

## Exact uniform savings

At a radix-two transform stage of width 2^l there are n/2^l blocks. Each has
one unit twiddle, at its first butterfly. There are no others: the stage root
has exact order 2^l and its used exponents range from zero through 2^(l-1)-1.
Consequently one transform has

```text
sum_(l=1..log2 n) n/2^l = n-1
```

unit-twiddle butterflies, including the empty sum at n=1. The two forward
transforms and the inverse transform give 3(n-1) replacements. All execute on
every admitted input. Pointwise products and inverse normalization use other
output cells and are unchanged. Hence the exact static and dynamic savings are

```text
static saving   = 141(n-1),
executed saving =  93(n-1).
```

This proves a uniform all-input refinement of each admitted fixed template,
conditional on the cited original multiplication/range theorem. The finite
certificate independently enumerates the replacement sites of nine balanced
templates; it is not an enumeration of every operand or every length pair.

At n=512 the emitted program has 1,533 replacement sites. Its static length
is 435,650 rather than 507,701, a decrease of 72,051. Every admitted input to
that template saves 47,523 executed instructions. These are exact ISA counts,
not elapsed-time measurements. No unrestricted optimality is claimed.

## Evidence and limits

The verifier compares complete local memory for all 65,537 residues and dirty
VALUE/TEMP/exterior initial values. It then executes the refined templates on
36 complete dirty-memory fixtures and checks both full-memory equivalence
and direct integer multiplication of the new outputs. The former execution
is the transformation specification, not a deliverable re-verification of
the predecessor's mathematical theorem. Structural controls corrupt a
threshold, a macro branch, an exterior branch entry, the data operand and
terminal control flow. Explicit guards remain enabled under Python -O.

The universal implication rests on this block simulation and the cited
producer invariants. Finite executions corroborate it. We do not claim an
independent human review, complete machine formalization, physical selected
consumer, selected cold replay, or new kappa. Other constant-specialization,
liveness and cleanup changes are outside this first improvement.
