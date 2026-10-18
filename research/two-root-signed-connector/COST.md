# Complete declared cost model

The algebraic construction admits arbitrary exact Q/C linear children.
The executable cost fixture specializes those children to products of integer matrices.
It does not implement a selected complex supplier or establish a physical speedup.

## Ports, preparation, and storage

The new schedule reserves eleven mutable rows of length L: three sources,
three outputs, two roots, and three recursive scratch rows.
The compact predecessor schedules reserve ten rows and omit the second root.
All mutable rows start arbitrarily; every source, root, and recursive scratch row restores.
The 27 integer coefficient matrices follow the mutable rows, in row-major order.
Their production, transport, and initial placement cost P; the comparison must retain any difference in P.
No coefficient matrix or intermediate vector is copied during execution.

The machine additionally owns three numeric registers, initially zero and zero on return.
These are explicit clean scalar workspace, not borrowed dirty rows.
It clears all three at entry and after each primitive instruction.
Input admission scans every supplied tape word and returns the data head to zero.
It checks integer values and declared magnitude bounds; its per-word price includes these checks.
The caller supplies distinct, contiguous rows in the declared layout.
Any host allocation, layout conversion, or restoration adapter costs an additional H_host.
The Python emulator is a semantic implementation of this model, not a bit-level reversible machine.

Program instructions use 16 bits: opcode 2, factor/scalar field 5, source 4,
target 4, and sign 1. The fixture uses 308 instructions for the old word and
306 for both the scaled and new words. Thus program sizes are 4928, 4896,
and 4896 bits. The two-root program has 300 factor and six root instructions.
The scaled word has 304 factor and two scaling instructions.
The decoder rejects aliases, missing rows, reserved opcodes, and invalid factors.
The controller carries the program counter, row/column counters, current head
address, requested address, and fixed row/coefficient bases: O(log L) bits
in addition to its fixed program. These controller bits are owned workspace.
Their initialization and return cost belongs to the entry/exit tariff K.
There is no recursion stack at execution time: the literal program includes
every recursive child and inverse. Constructing and encoding that program
costs E; static publication of a word does not make E a free input operation.

## Exact integer width

Suppose every initial data entry has magnitude at most D and every matrix
coefficient has magnitude at most H, with integer L>=1, D>=0, H>=0.
Define

```text
G = 1 + L max(1,H),
B = 3^6 max(1,D) G^308,
w = bit_length(2B) + 1.
```

A factor shear replaces one row by that row plus a signed dense product.
If all data entries have magnitude at most K, every partial target sum has
magnitude at most `(1+LH)K <= GK`; each temporary product has magnitude at
most `HK <= GK`. A root shear grows the maximum by at most three.
Root doubling grows it by at most two; halving cannot increase it.
All three words and their inverses contain at most 308 factor instructions
and at most six such scalar instructions. Induction over these instructions
therefore bounds every data entry and temporary product by B.
This bound is conservative and applies uniformly to all inputs in the domain.

For a common representation, store every data value as its doubled numerator.
Store coefficient values as ordinary integers. This gives one fractional bit.
The new and fourteen-query words preserve even numerators throughout.
The scaled word has exactly one halving followed by its doubling.
Before that halving every numerator is even. Between these operations all
factor updates are integer-linear, so every stored numerator remains integral.
The doubling restores integral root values; no truncating division occurs.
The same reasoning applies to the literal inverse, whose only halving also
precedes its doubling. The emulator rejects a nonexact division.
Signed w-bit integers cover all doubled data numerators, coefficients,
temporary products, and sums. Overflow causes rejection; it never wraps.
For inversion of a previously computed output, choose D for that actual
input, or provide a larger common bound for both calls.

The candidate's declared tape and numeric-register capacity is
`(11L + 27L^2 + 3)w` bits, plus its 4896 program bits and controller.
The compact scaled comparator needs `(10L + 27L^2 + 3)w` bits with the same
program size. The extra Lw bits remain a real cost.
Widths for arbitrary rational or complex coefficients require a different
representation and precision analysis; the integer fixture does not supply it.

## Operations and controller tariff

Each dense term loads its coefficient and source into two numeric registers,
multiplies them, loads the target into the third, adds or subtracts, and stores.
Root passes load the source and target, optionally double the source register,
add or subtract, and store. Scaling passes load, shift exactly, and store.
Signs select addition versus subtraction; no separate uncharged negation occurs.
LOAD overwrites an owned register; CLEAR returns it to zero.
The data head returns to zero after every instruction.

Let F,R,S be the numbers of factor, root, and scaling instructions and n=F+R+S.
The controller uses two nested length-L loops for F and one loop for R or S.
Here is its complete symbolic tariff, alongside the data-operation counts
in `two_root_invoice.json`:

| Charge | Count |
|---|---:|
| Instruction bit reads | 16n |
| Instruction tape bit moves, including final return | 32n−2 |
| Complete instruction decodes, including validity branches | n |
| Address calculation and SEEK setup | 3FL² + 2RL + SL + n |
| Loop counter resets | n + FL |
| Loop tests | F(L+1)² + (R+S)(L+1) |
| Loop increments | F(L²+L) + (R+S)L |
| Numeric register clears | 3(n+1) |
| Admission reads | N = mutable_rows·L + 27L² |
| Admission head movement, first cell at zero | 2(N−1) |

The instruction head visits bits zero through 16n−1 once and returns to zero.
A complete decode contains eight masks/shifts and two sign arithmetic
operations, plus range/alias checks and opcode dispatch. The decode tariff
includes all of these; do not charge the displayed subcounts twice.
SEEK setup includes evaluating its affine address expression, distance,
direction, and termination setup. Each head-step price includes updating
the head address and its walk control. No unit-cost arbitrary-distance jump
is assumed. Loop tariffs include their counter work and branch control.
The emulator checks literal data traces against the first invoice; controller
counts come from the stated loop structure, not an independently traced CPU.

At address width `a = bit_length(N)`, let each class have its full nonnegative
price at widths a,w. Loads and stores charge word access and register transfer;
ADD/SUB, MUL, SHIFT, and CLEAR charge their full scalar bit costs.
Then sum each count times its class price and add

```text
P + E + K + H_host.
```

This is the complete invoice of the declared model, with preparation and
entry/exit charges exposed. It is not a numerical claim about unspecified
hardware. A comparison must use common adequate widths and identical tariffs,
or account for their differences explicitly. In particular, fewer arithmetic
operations do not imply lower arbitrary weighted cost or less storage.

## What improves and what does not

Against the compact scaled word, factor multiplications fall by `4L²`.
Target loads/stores fall by `4L²−4L`, additions by `4L²−6L`, and source reads
fall by `4L²−6L`. Both schedules use `2L` scalar shifts and 306 instructions.
At L=1 some of these counts increase; no pointwise dominance is claimed.
Including its admission scan, the new word's data-head movement difference is

```text
−8L^4 + 148L^3 + 12L^2 + 478L.
```

It changes sign between L=18 and L=19, as proved in README.md.
At L=19 its value is −14022; at L=3 it is +4890.
Admission reads increase by L and storage increases by L words at common width.
The complete weighted inequality, including the extra storage/host charge,
decides whether a particular implementation benefits.
The selected supplier has no identified admissible instance of this connector.
No multiplication exponent follows from this fixture.

## Independent checks and limits

The machine checks all three literal schedules at L=1,2,3,4 on three integer
fixtures each, and their inverses. It compares the results with direct product
evaluation that never traverses the recursive echo word.
The data trace matches the separate invoice; a closed summation formula
separately checks head movement. These are different models, written with
AI assistance in the same project; no external human review is claimed.
Five machine controls reject a reserved opcode, a factor alias, insufficient
width, nonexact halving, and a missing row.
The all-input algebraic and width arguments are written proofs, not an
exhaustive finite test or proof-assistant formalization.

## Derivation of the tape polynomial

For one dense factor instruction, write the coefficient address as
`c_ab = RL + fL² + aL + b`, source address `s_ab = pL+b`, and target
address `t_ab = qL+a`, for `0<=a,b<L` and distinct p,q<R.
Every coefficient address exceeds every mutable-row address.
The head visits `(c_ab,s_ab,t_ab)` in lexicographic order and returns to zero.
Summing distances, including the initial visit and final return, gives

```text
2 sum(c_ab) - sum(s_ab) - sum(t_ab) + sum(|s_ab-t_ab|)
    + 2((q+1)L-1).
```

The individual sums are

```text
sum(c_ab) = RL³ + fL⁴ + (L⁴-L²)/2,
sum(s_ab) = pL³ + (L³-L²)/2,
sum(t_ab) = qL³ + (L³-L²)/2,
sum(|s_ab-t_ab|) = |p-q|L³.
```

The last identity holds because p and q label disjoint rows; the terms b−a
cancel. Substitution yields the factor formula in README.md.
For a descending root pass p>q, successive source visits differ from the
previous target by `(p-q)L+1`; each source-to-target move costs `(p-q)L`.
Including the first visit and last return gives
`2(p-q)L²+2(q+1)L−2`. Setting p=7,q=6 gives the stated root formula.
Scanning one row and returning costs `2((q+1)L−1)`.
Adding these formulas over the literal words produces the displayed
polynomial coefficients without simulating the individual tape visits.
