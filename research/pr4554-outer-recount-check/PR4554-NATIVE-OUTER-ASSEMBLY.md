# A direct native Fourier-to-integer assembly

This is a sufficient assembly theorem with an explicit caller and an explicit missing transform hypothesis. Its multiplication construction uses no Turing-machine algorithm. The independently proved closed Gaussian kernel in NATIVE-STABILITY.md does not, by itself, meet the cyclic Fourier hypothesis below.

## Input and arithmetic

Fix a standard random-access machine with word width w=c_w ceil(log2(n+2)), for a sufficiently large fixed c_w, and add/subtract, Boolean operations, shifts, comparison, indexed memory and word multiplication/division. The input consists of two n-bit nonnegative integers in packed words. Output is their ordinary packed product. Input conversion and output packing operate on O(n/w) words, with a constant number of shifts and masks per digit. A product of two fixed-size multiword scalars costs O(1) instructions: split into half-word digits and use a fixed number of word products and carry updates. No full-input unit-cost product is used.

Choose b=floor(log2(n+2)/8), after a fixed small-input cutoff, and let B=ceil(n/b). Write both inputs in radix 2^b with B digits. Let L be the smallest power of two at least 2B. Thus 2B<=L<4B, and L=Theta(n/log n). All digits and all exact convolution coefficients have O(log n) bits.

## The explicit transform hypothesis

Assume an actual uniform native cyclic Fourier program on L complex entries provides the following contract. For arbitrary complex inputs with real and imaginary parts of magnitude at most L^4 2^(4b), it computes either the unnormalized forward transform or the normalized inverse transform, with absolute output error at most delta, where

    delta = 1/(128 L 2^b),

using O(log n)-bit fixed-point words and total work F(L,n). Its full root construction, address generation, table construction, precision operations and scratch clearing are included in F. A program proof must establish this hypothesis for the full arbitrary-input domain; a kernel identity or nonzero denominator check does not establish it.

## Constructive assembly and proof

Pad the digit arrays by zeros to length L. Apply the forward program to each, multiply corresponding approximate outputs using bounded-word complex arithmetic, and apply the normalized inverse program. Round every final real output to the nearest integer. Compute each pointwise product with absolute error at most delta. This is feasible using O(log n) fractional and integral bits.

The exact forward outputs have modulus at most L 2^b. The difference between an exact product AB and the computed product is at most

    2 L 2^b delta + delta^2 + delta < 1/16.

The normalized inverse Fourier operator has infinity-to-infinity norm at most 1: each row has L entries of modulus 1/L. Thus its exact application to the product errors contributes less than 1/16 per output. The inverse program adds at most delta<1/16. The final real error is therefore less than 1/8, so nearest-integer rounding recovers every exact convolution coefficient. The imaginary part is discarded. The forward approximants, product approximants and inverse inputs all lie within the stated magnitude domain, including fixed rounding margins.

There is no cyclic aliasing because L>=2B. Each coefficient is at most B(2^b-1)^2. A left-to-right radix carry pass uses the recurrence

    s_j = c_j + carry_j,
    digit_j = s_j mod 2^b,
    carry_(j+1) = floor(s_j/2^b).

The carry is at most B 2^b by induction, up to a fixed harmless endpoint constant. Each s_j has O(log n) bits, and shifting/masking and O(1) word additions implement each step. Remaining carries terminate in O(1) additional digits because their size is O(log n). The carry and output packing cost O(L), including zero padding.

Hence the complete native multiplication algorithm has cost

    O(F(L,n) + L),    L=Theta(n/log n).

The input-dependent word width is determined from n; the program and every fixed constant are independent of n. Fixed finitely many small inputs can use grade-school digit multiplication.

## Native saving corollary and its exact scope

If a concrete transform satisfies

    F(L,n) = O(L (log L)^(1-kappa) (loglog(L+4))^C)

for fixed kappa>0 and fixed C, the multiplication cost is

    O(n/(log n)^kappa * (loglog(n+4))^C + n/log n).

For every fixed 0<kappa'<min(kappa,1), this is O(n/(log n)^kappa'). If C=0 and 0<kappa<=1, it is O(n/(log n)^kappa). These are Word RAM bounds and are not new multitape-TM constants. The output lower bound is Omega(n/log n) word stores, so the displayed range is consistent with explicit packed output.

A direct ordinary bounded-word FFT has F=O(L log L), proving the useful O(n) native baseline through this theorem, with no TM base multiplier. The closed rational Gaussian recurrence proved in the companion document is a positive faster *kernel* block. A quantitatively conditioned cyclic lowering, including all root and coefficient preparation, is still needed to replace the baseline by the saved-exponent F above. No new best integer-multiplication exponent is asserted in this packet.

## Credit

Digit convolution and carry recovery, normalized inverse stability, and ordinary FFT multiplication are standard predecessor constructions. The native Gaussian provider used by the companion packet is PR #956 and its attributed lineage. The displayed arbitrary-input contract, quantitative caller tolerance and full native outer cost expose exactly how a proved provider must be integrated; they are informal proofs, not Lean certificates.
