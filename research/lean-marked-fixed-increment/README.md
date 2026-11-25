# Counted fixed-width marked increment

This package refines the existing fixed-width RippleCounter to the marked one-bit tape used by the public arithmetic/input routines. The actual controller reads or writes one current symbol, moves one head by one cell, executes an entrance and rewind, and returns to the left marker. It reports carry overflow for every input, including an empty word.

For a supplied word of width w, the first halt is exactly 2*carryLength+3, hence at most 2w+3 transitions. Every prefix has at most w+2 represented cells, counting both markers. The actual resulting word satisfies value(updated)+overflow*2^w=value(input)+1. Exact p+1 at unchanged width is equivalent to the explicit condition value(input)+1<2^w. The old flag is overwritten. There is no free high-bit allocation or widening in this package.

The model is a finite marked, sequential tape controller with implicit exterior blank symbols. Input encoding, marked initialization, private allocation, physical multitape/single-tape simulation, dirty-state inversion and a full integer-multiplication bit-cost bound are separate. These results do not supply the complete selected recursive cost family. The later paid-widening and adder compositions are outside this package.

## Reuse and exact changes

- TapeStack.lean is the existing PR64 source with its broad Mathlib.Tactic import narrowed to the exact already-used tactic/finite-instance providers. Every declaration and proof body is unchanged.
- CounterArithmetic.lean is the existing PR64 source with one underflow proof explicitly naming Nat.mul_eq_zero after import narrowing. Every definition, theorem statement and increment proof is unchanged.
- MarkedBinaryIncrement.lean is the new physical marked-layout refinement. It reuses the old updated/overflow/modular arithmetic and carry/rewind algorithm. This is not a claim to have invented binary ripple counting.
- Unchanged RippleCounter is fetched at immutable public commit2d970ab3ca0271cfb2b609dc9aae1b7073b7774d. Public PR1840 supplies the zipper/head API and PR1869 supplies the marked alphabet. None of those five unchanged public modules is vendored here.

See ACCEPTANCE.json for exact source-bound declarations, complete printed signatures, diagnostics and independent review scope; see REPRODUCE.md for isolated commands using existing dependencies. Original attribution is retained in every exact source. New marked refinement: James Chang with OpenAI assistance, Apache-2.0.

Author-checked selected context: kappa=836330098538459/500000000000000000=0.001672660197076918. This context value is not a new numerical enclosure or an unconditional runtime conclusion of this package.
