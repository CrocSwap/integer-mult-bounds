# Fixed rational recovery without word multiplication or division

## Exact useful result and scope

Fix integers p and d with d > 0. On a Word RAM with bounded-word addition,
subtraction, comparisons, AND, OR, XOR, NOT and both logical shifts, prescribed
rounding of p x / d can be computed in O(log(2 + w)) instructions using O(1)
words, for signed inputs whose magnitude has w bits. The constants depend on
p and d, which are fixed independently of w. The computation uses no word
multiplication, division, remainder, leading-zero-count or table lookup oracle.
The algorithm below handles every positive w; signs use a separate bit and
magnitude word. It supports floor, truncation toward zero and nearest ties to
even. For each fixed denominator, the same compiled program serves all widths.
A valid caller may supply w as metadata; alternatively the standard zero-on-
overshift semantics finds w by doubling and binary search in O(log(2 + w))
operations. The executable supplies w explicitly and rejects out-of-range shifts
inside the scientific division routine.

This reduces the basic-arithmetic fallback in Dugongue's PR #4885 from
O(N w) to O(N log(2 + w)) for its fixed-polynomial resonant recovery program,
under the explicitly stated both-shifts instruction set. It supplies no new
multiplication kappa and does not recover the channel's missing complement.
It is an asymptotic upper bound, not a measured speedup for practical widths.

The existing Problem 1.8 Lean RAM has right shift as a derived operation using
its division primitive. Therefore the division-free instruction set here is
NOT claimed as a literal subset compilation of that exact Lean machine.
Its fixed-width shift and division specifications are semantic precedents;
this contribution has no new Lean kernel audit.

## Bit-plane invariant

Let 0 <= x < 2^w and d >= 2. Put b = ceil(log2(d + 1)), implemented as the
ordinary bit length of d. For each address position i, maintain a lane value
r_i in [0,d). Store its b binary digits in b ordinary w-bit words: bit i of
word R_j is bit j of r_i. The w lanes share these b words; this is NOT an
ultraword or an array of w separate word registers. All lane operations use
only ordinary w-bit Boolean operations. A binary ripple circuit across the
b bit planes adds two lane values independently, using a bit-plane carry.
An extra carry plane permits exact values below 2d without machine-word
overflow. Compare with the fixed binary digits of d, then conditionally
subtract d in every selected lane. This computes all lane sums modulo d
in O(b) word operations and O(b) words, including carry and borrow fields.
There is no carry between lanes: every Boolean operation acts on matching
bit positions, and carries move between planes, not adjacent word bits.

Multiplication of every lane value by a scalar a in [0,d) uses b binary
shift-and-add stages, with each lane doubling/addition reduced modulo d.
It costs O(b^2) word operations. Here this is a construction from Boolean
operations, not a primitive word multiplication. The loop uses only the b
bits of a. To square the scalar weights themselves, ordinary scalar modular
addition avoids overflow as follows: for u,v < d, set gap = d - v; return
u - gap if u >= gap, and u + v otherwise. The latter branch is below d.
A b-step binary product of scalar weights therefore uses O(b) instructions
and never forms the potentially overflowing u + v in the former branch.

Start with length l = 1 and r_i = bit_i(x). At every stage maintain

    r_i = (sum_{j=0}^{l-1} bit_{i+j}(x) 2^j) mod d,

where bits at positions >= w are zero. Set a_l = 2^l mod d. The simultaneous
updates are

    r_i <- (r_i + a_l r_{i+l}) mod d,
    a_l <- a_l^2 mod d,
    l <- 2 l.

A logical right shift of each bit-plane word by l supplies all r_{i+l}.
Old planes remain available until the entire new collection is finished.
The displayed invariant follows by splitting the 2l-bit block into lower
and upper halves. After ceil(log2 w) stages, every lane contains

    r_i = floor(x / 2^i) mod d.

The quotient bit at position i is exactly

    [2 r_{i+1} + bit_i(x) >= d].

Indeed this is the next quotient bit in ordinary high-to-low long division.
The b+1 planes for the expression are obtained without addition: the lowest
plane is x and the upper planes are the previous remainder planes shifted
right by one. A bit-plane comparison with d emits the ENTIRE quotient word.
The remainder is lane zero, extracted from the b planes in O(b) operations.
Thus the quotient and remainder are exact, not reciprocal approximations.

If d has more than w bits, x < d gives quotient zero and remainder x directly.
This exceptional branch uses the fixed denominator's bit length and does not
load a truncated denominator into a word. If the denominator fits, the scalar
weight arithmetic above stays below d, even when d is near 2^w. All data word
values and actual shift counts in the executable are checked. Setup, loop
control and fixed-constant bit inspection add O(b log(2+w)) instructions;
the recorded Boolean/arithmetic count is bounded by

    100 (b + 1)^2 (ceil(log2 w) + 1).

This is a conservative bound on the emulated data operations, not a cycle-
accurate count for a compiled processor or an exact tariff for a prior ABI.
For fixed d it is O(log(2+w)). Temporary planes occupy O(b) words, a constant
independent of w. Every original input word remains unchanged.

## Signed rounding and fixed numerators

Run unsigned division on abs(x), retaining its original sign. Write magnitude
abs(x) = d q + r, 0 <= r < d. Truncation returns sign(x) q. Floor returns q
for nonnegative x, and -q - [r != 0] for negative x. Nearest ties to even
increments q when r > floor(d/2), or when d is even, r = d/2 and q is odd;
then restore the sign. This never forms 2r, so there is no boundary overflow.
When d does not fit a word, the half-denominator threshold either fits and
can be stored as a fixed constant, or exceeds the entire magnitude range
and the comparison is always false. These are fixed-width comparisons,
not an uncharged multiword division. The output has a sign bit and magnitude;
no signed two's-complement overflow convention is silently assumed.

For fixed p, form abs(p) abs(x) by its fixed binary shift-and-add expansion.
Use W = max(w + bit_length(abs(p)) + 1, bit_length(d) + 1, 3) working bits;
this adds only a constant number of guard bits for fixed p,d. Every shifted
summand and partial sum fits W bits, as checked by the emulator. Apply the
unsigned scan and the selected rounding with sign(x) XOR sign(p).
This proves the stated fixed-rational theorem. If a machine ABI fixes its
physical word width before the payload precision, reserve these constant
guard bits in that ABI; do not store a W-bit temporary in a w-bit word.
Alternatively a constant number of physical limbs implements the same
construction at constant instruction overhead, with logical shifts across
that constant limb count explicitly charged.

## Application to the resonant pseudoinverse

PR #4885 proves a fixed rational monomial program for every width, including

    A^dagger = (1/16) R(C) A*,   C = A* A / 16,
    R(x) = -(q(x) - q(0)) / (x q(0)),   q(0) = -40131624960.

The literal denominator has 2-adic factorization

    40131624960 = 2^19 * 76545.

The scalar scan may use the full fixed denominator, or shift the power-of-two
part with explicitly tracked discarded remainder for prescribed rounding.
The executable tests the full denominator; it does not omit those discarded
bits. All numerator heights, polynomial degrees and the number of monomial
passes are fixed constants. Each pass visits N scalar entries and preserves
the arbitrary retained input in an owned buffer. Therefore its prescribed
rounded fixed-rational operations cost O(N log(2+w)), with the same constant
number of full-size buffers plus O(1) scalar scratch words. Clearing those
scratch words costs O(1); buffer initialization and clearing are O(N) passes.
The source requirement 2^W >= c N must include guard words, retained input,
three owned Horner buffers and constant plane scratch. Rounding and original
source precision budgets remain those of #4885; this lemma changes the cost
of implementing their specified scalar rounding, not the algebraic projector
or its inverse-norm bound. It does not claim an unrounded rational computation
in bounded precision. Every rounded scalar step still incurs the explicitly
chosen local error already accounted for by the fixed-degree stability bound.

## Precedents and review limits

The general associative scan method is classical: Guy E. Blelloch, Prefix Sums
and Their Applications, CMU-CS-90-190 (1990), and its 1993 chapter. This use of
bit-plane modular prefix blocks is an application of that method, with an
explicit quotient-emission identity and bounded-word invoice. No broad novelty
claim for parallel constant division or Boolean arithmetic is made. Torbjorn
Granlund and Peter L. Montgomery, Division by Invariant Integers Using
Multiplication, PLDI 1994, supplies the important distinct multiplication-
assisted constant-division context; it is not used as an uncharged primitive.
PR #4713's Newton reciprocal implementation also uses word multiplication;
this theorem's restricted instruction-set scope is different.

The shared MathProof source tree was consulted for fixed word shifts and
long-division semantics, specifically shiftLeftMany_fixed,
shiftRightMany_fixed and divBits_fixed in
Mathproof.Meta.Problem18RAMLax51ProofsRamToTMWordOperations20261001,
and the instruction set in Problem18RAMLax13Ram20261001. These inspected
source files and DAG search matches were not freshly kernel checked. The
current theorem is an informal mathematical proof plus executable exact
word emulation. No independently reviewed full multiplication theorem,
selected-frontier admission, hosted CI or new kappa is claimed.

## Open next question

Instantiate this implementation inside a named source-compatible consumer
whose full paid profile already beats the current bound. Begin with the
actual precision/error tariff and both-shifts physical ABI, then price owned
buffers and every pass. The scalar implementation is now supplied; the missing
productive channel complement and favorable complete recurrence remain separate.

Primary references consulted:

- [Guy E. Blelloch, Prefix Sums and Their Applications](https://www.cs.cmu.edu/~guyb/papers/Ble93.pdf), especially the definition of associative scan and the logarithmic-depth construction.
- [CMU-CS-90-190 record](https://www.cs.cmu.edu/afs/cs.cmu.edu/project/scandal/public/papers/CMU-CS-90-190.html).
- [Granlund and Montgomery, PLDI 1994](https://doi.org/10.1145/178243.178249), multiplication-assisted invariant division; full publisher text was not accessible in this session, so no internal theorem from it is used as a proof premise.

A fixed program still needs address space for its constant register allocation.
Require 2^W >= c_d for the b-plane scalar workspace, and 2^W >= c N + c_d
for the array application. The fixed-rational wrapper already reserves
W >= bit_length(d) + 1; if a particular compiled register allocation requires
more constant address headroom, increase W by that fixed additive constant.
The all-width executable scalar identities are not a claim that arbitrarily
many temporaries fit a two-cell w = 1 memory. Constant guard widening and the
stated address condition are part of the native ABI.
