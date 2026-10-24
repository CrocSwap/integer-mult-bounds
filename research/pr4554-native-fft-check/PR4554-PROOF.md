# Native bounded-word integer multiplication

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## The theorem and its model

For every n ≥ 1 and two nonnegative integers of at most n bits, the algorithm in
native_fft.py computes their exact packed product on a uniform Word RAM in O(n)
word operations and O(n/log(n+2)) words of memory. The program uses add/subtract,
comparison, shifts, masks, indexed memory and multiplication/division of bounded
words. Its word width is a sufficiently large fixed constant times log(n+2).
The input/output consists of packed radix digits; converting conventional packed
binary words to/from these digits takes O(n/log(n+2)) operations.

This is an informal algorithmic theorem accompanied by a portable executable
bounded-word model, not an emitted machine program or a Lean theorem. Linear
Word RAM FFT multiplication is classical: see Fürer, 2014, Theorem 4.1(a),
https://arxiv.org/abs/1402.1811. Our contribution is a self-contained, paid,
source-bound native implementation and the explicit precision, error and assembly
interfaces needed to remove the prior TM multiplication subroutine. O(n) is not
claimed as a new record, or as a higher κ.

## Fully specified construction

Set ell = bitlength(n+2), b = max(1,floor(ell/8)), β = 2^b,
L = ceil(n/b), N the least power of two at least 2L, F = 24ell+64 and S = 2^F.
Use a single global magnitude-word width w = 16(F+16)+20; signed values have a
separate sign bit. These are fixed formulas, with w = Θ(log(n+2)). The large
constant simplifies this proof; it is not a claim of practical speed.

The packed ABI supplies L radix-β digits per operand, with unused high input
bits zero. Pad each to N. Construct exp(2πi/N) to coordinate error < 1/S using
root_seed.py: Machin's formula and bounded Taylor arithmetic, not a root oracle.
ROOTS-RECOVERY.md proves its universal precision, word bound and O(F) cost.
Generate the first N/2 twiddles by successive rounded complex products.

Perform two ordinary iterative radix-two forward FFTs, multiply their entries,
perform the unnormalized inverse FFT, then divide by N. Each real scalar product
is taken exactly within the common word and the complex product is rounded back
to the S grid. Forward twiddles are conjugates of the positive-angle table;
inverse twiddles use that table directly. Additions are exact at the common grid.
Round the real inverse coefficients to integers and carry in radix β.

## Discharging numerical premises

Let δ = 1/S. A seed's complex error is < 2δ, and one rounded complex product
has error < 2δ. If a_j is the error in the j-th stored power, then

    a_(j+1) ≤ (1+2δ)a_j + 4δ,    a_0 = 0.

Since Nδ < 1/16, summing this geometric recurrence gives a_j ≤ 8jδ ≤ 16Nδ.
Every twiddle therefore has coordinate error at most 16N/S, including the
conjugated table. Local fixed-grid product errors are less than 2/S per
coordinate; floor division instead of nearest rounding still satisfies this
bound. The independent proof in FFT-ERROR.md now applies. It proves final
complex error at most 216N^6β²/S, below the looser envelope

    2^28 N^8(F+1)^2β^4/S < 2^(-10ell-6) ≤ 2^-26 < 1/4.

The separate integer division by N has its own grid-rounding error included in
that estimate. Thus every rounded real coefficient is the correct integer;
the imaginary coordinate is within 1/4 of zero. The runtime separation tests
always succeed for valid input. They are checks of a proved property, rather
than a substitute for a closeness-to-the-right-integer proof.

N ≥ 2L prevents cyclic aliasing. Each coefficient lies between 0 and
L(β−1)². Carry propagation uses s_j = c_j + carry_j, output digit s_j mod β
and carry_(j+1) = floor(s_j/β). Inductively carry_j ≤ L(β−1), so every carry
operation has O(log n) bits. After 2L digits the carry is zero. Product size
< 2^(2n) proves that trimmed output digits and unused high bits are zero.
This includes n = 1 and all finite small cases without a separate FFT convention.

## One common bounded-word model

FFT-ERROR.md bounds inverse intermediate complex magnitudes by 6N^6β². Raw
scalar product magnitudes, including sums of two such products, need at most
2F + 6ceil(log2 N) + 2b + 8 bits. The root routine needs at most
16(F+16)+20 bits, which dominates this FFT bound for every ell ≥ 2 since
ceil(log2 N) < ell+2 and b ≤ ell. Address, loop and carry words fit too.
The runtime rejects any stored arithmetic magnitude reaching 2^w.
Its bound-checking interpreter uses arbitrary-precision Python integers only
to emulate those bounded words. No runtime operation multiplies the n-bit
operands as integers. Python's independent x*y appears only in the test oracle.
The physical word constant is chosen before execution from the bit budget n;
subroutines do not silently switch to larger private words.

## Complete cost

Root setup costs O(F) operations. Its internal precision 8(F+16) and its
128(F+1) Taylor iterations remain O(log n). Twiddle setup costs O(N) rounded
complex word products. Bit reversal costs O(N): the number of inner bit flips
summed over the whole index loop is less than 2N. There are log2 N stages,
N/2 butterflies per stage, with a constant number of scalar operations, address
updates, loads and stores per butterfly. Three transforms cost O(N log N).
Pointwise products, validation of padding, rounding, carries, allocation,
packing and final output cost O(N). The counted arithmetic ledger is exposed
by the executable; it is not a literal emitted-instruction trace.

For ell ≥ 16, b ≥ ell/16, so N < 4ceil(n/b) ≤ 64n/ell + 4 and log2 N ≤ ell+2.
Consequently N log N = O(n). The finite remaining lengths are absorbed in a
fixed constant. All setup costs are paid; no input-independent preprocessing
is excluded. Storage is O(N) words, plus O(1) root-generation words.

## Use in the faster route

This construction is a native implementation for every record multiplication
in a future Fourier/resampling compiler. NATIVE-OUTER-ASSEMBLY.md proves the
quantitative caller and full multiplication cost if a faster cyclic transform
is actually supplied. NATIVE-STABILITY.md proves a bounded-word rational
Gaussian kernel and safe shear divisions; PHASE-TABLES.md proves paid native
phase queries. Those positive results do not silently supply the missing cyclic
conditioning bound. No existing TM instruction table, TM simulation or TM
multiplier is used by this construction.
