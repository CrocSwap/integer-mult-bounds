# Counted bit addition and paid zero padding

Author-checked context: kappa = 836330098538459/500000000000000000 =
0.001672660197076918. These generic implementations change no numerical bound.

Accepted exact sources:
- SequentialBitAddition: signed ripple arithmetic, two explicitly executed
  sign columns, first halt11n+10, returned head, unchanged inputs, seven scratch
  register clears and constant represented tape footprint. Its controller uses
  the stated boundary-observing three-track model.
- MarkedZeroPadding: three explicit symbol-marked tapes, first halt6(d+n)+14,
  output marker/zero/copy writes into blank workspace, returned heads, preserved
  data/unary-control inputs and cleared scratch. Every prefix occupies at most
  2(d+n)+6 represented tape cells, plus one Boolean register and finite control.
  Exact output extent is d+n+2 cells. Both zero-size cases are covered.

The padding controller does not use an unbounded shift, Nat arithmetic or a
zipper-boundary sensor. Its supplied unary control and input-marker format
still need implementation from the caller's exponent representation. The adder
and padding have different entrance layouts: a charged zip/sign-column builder
is required before their sequential physical composition can be claimed. The
new marked-adder refinement and signed-alignment work are outside this accepted
publication boundary.

No arbitrary old scratch/output restoration, selected allocator/encoding,
whole-program bit-cost supplier, all-size multiplier or final multiplication
exponent is established. The bit-length budgets for selected reference traces
are separate prerequisites for choosing these machines' widths.

## Source reconstruction

Use Lean4.21.0 and Mathlib308445d7985027f538e281e18df29ca16ede2ba3.
Reuse, without copying into this package, the two exact public modules in
research/lean-paired-bit-xor-machines at PR1840 head
3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:
PairedBitXorScan33a93351 and MarkedBitXorScanf28dbd4d.
Build those public prerequisites first. Then compile SequentialBitAddition
before MarkedZeroPadding with their output directories on LEAN_PATH and the
pinned Mathlib package path. Keep all printed axiom/type diagnostics. The
accepted native evidence is retained; this proposal performs no relocated
replay and makes no claim about a future CI result.

## Attribution

James Chang, OpenAI-assisted, Apache-2.0. Elementary full-adder and signed-word
identities are standard arithmetic. The existing paired/marked tape definition
and Lean/Mathlib sources retain their original attribution. The contribution
claimed here is the specific executable finite-alphabet refinement with proved
transition counts, complete stated state behavior and represented footprint.
No first-ever or optimality claim is made.
