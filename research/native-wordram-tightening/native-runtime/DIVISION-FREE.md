# Remove unit-cost division from the native transfer

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## Sufficient theorem

A w-bit unsigned integer division with nonzero divisor can be implemented on a native Word RAM with additions, subtractions, Boolean operations, comparisons, both primitive logical left and right shifts, and low-word multiplication, using O(log w) operations and a constant number of scratch words. Both quotient and remainder are exact. There is no Turing-machine simulation, unbounded-word multiplication, precomputed exponential table, floating point or leading-zero instruction. This is a concrete application of classical reciprocal/Newton division; no priority is claimed for that method.

For w >= 2 and 0 <= n < 2^w, 1 <= d < 2^w, find the highest nonzero bit of d by binary search with shifts and comparisons. Put s = w - 1 - floor(log2 d), dn = d*2^s, so a = dn/2^w lies in [1/2,1). Let B = 2^(4w), A = dn*2^(3w), X0 = B, and k = ceil(log2(4w)). Evaluate exactly, k times,

    X_next = floor((2*B^2*X - A*X^2)/B^2).

The division in this display is only a shift by 8w on a constant-limb integer. In particular it is not the division primitive being removed. Return

    t = floor(n*2^s*Xk / 2^(5w)),
    if n - t*d >= d, increment t,
    remainder = n - t*d.

The final denominator is again a power of 2. Signed division uses magnitudes and the source's specified sign/rounding convention, with one conditional adjustment for floor division. If the source model defines division by zero as zero, an explicit d = 0 branch returns zero; it does not run Newton. The w = 1 cases are a fixed finite table.

## Universal proof

Write x_i = X_i/B and e_i = 1 - a*x_i. Exact Newton would replace x by x*(2-a*x). The displayed integer formula rounds this value downward by less than 1/B. Starting with x0 = 1, induction gives 1 <= x_i <= 1/a, and 0 <= e_i <= 1/2: the exact Newton map lies between x_i and 1/a, rounding cannot pass below the integer X_i, and e_next <= e_i^2 + 1/B <= 1/4 + 1/B <= 1/2.

Set z_i = 2^(-2^i). We claim e_i <= z_i + i/B. The initial inequality holds. When e_i <= z_i, squaring gives the next inequality directly. Otherwise e_i + z_i <= 1, so e_i^2 - z_i^2 <= e_i - z_i <= i/B; the rounding term adds at most 1/B. Thus

    e_k <= 2^(-2^k) + k/B
        <= (k+1)*2^(-4w) <= 2^(-2w).

Here 2^k >= 4w and k <= 2w for every w >= 2, with 2w+1 <= 2^(2w). The real number before the final floor is exactly (n/d)*(1-e_k). It underestimates n/d by at most n*e_k < 2^(-w) < 1. Consequently t is either floor(n/d) or one less. The final comparison chooses the exact quotient, with 0 <= remainder < d. This proves correctness for every admissible input.

## Exact native cost and storage

All intermediates have O(w) bits: B has 4w+1 bits, X <= 2B, and the largest Newton numerator/product has at most 12w+O(1) bits. Store them in a fixed number of limbs, not in a unit-cost unbounded integer. Addition, subtraction, comparison and shifts on a fixed limb count use O(1) native instructions. A full product of two w-bit words is obtained by splitting them into half-word pieces and using a fixed number of low-word products, additions and carry operations. For odd widths, use smaller pieces so each piece product fits; the number remains fixed. Grade-school multiplication on the fixed limb count is therefore O(1) native instructions. Constructing the single-bit constants B and B^2 uses fixed limb initialization; no register must contain 2^w itself.

Binary search for the leading bit costs O(log w). The k Newton updates cost O(log w); the final correction is O(1). Scratch can be placed in a separate bounded arena and the unrelated dirty memory is untouched. This strengthens the generic two-shift Word RAM used by the native assembly. It does not delete DIV from the literal Lax13 instruction set: that separate machine has primitive left shift but derives right shift using division. The two-shift model is stated explicitly and no unsupported Lax13 lowering is claimed. This is an informal algorithm and complexity proof. check_division.py uses exact Python integers to test the identities and is not itself an instruction-level implementation of the fixed-limb backend.

For division of operands occupying at most a fixed c words, apply the same construction at conceptual width c*w, with a fixed number of actual w-bit limbs. The cost remains O(log w). This covers the retained native caller's constant-limb signed fixed-point arithmetic. Offline polynomial-sized rational constructors may instead retain binary long division implemented by shifts and subtractions; their polynomial setup remains n^o(1).

## Composition with the actual nine-row native invoice

The inherited native algorithms in PR #4630 and #4635 use bounded-word MUL/DIV. Replace every online DIV by the construction above, keeping all other operations and the actual source Gaussian/provider contracts. If a row has bound O(T*p^(1-saving)*polylog(p)), w = O(p), this adds at most another O(log p) factor. Every saving is strictly larger than the target kappa in NATIVE-TRANSFER.md. For fixed positive eta, any fixed power of log p is O(p^eta); spend at most half the smallest proved margin on all these factors. Thus the complete bound remains

    O(n / (log n)^kappa),

now without a division instruction. This preserves, rather than increases, the numerical kappa established by the new source-bound transfer. It is a stronger instruction-set conclusion. The inherited all-fiber, compiler, precision, analytic and recovery premises remain explicit; this proof does not discharge them.

## Attribution and evidence

The reciprocal-division literature includes Torbjorn Granlund and Peter L. Montgomery, Division by Invariant Integers using Multiplication, PLDI 1994, https://doi.org/10.1145/178243.178249 and https://gmplib.org/~tege/divcnst-pldi94.pdf; Niels Moller and Torbjorn Granlund, Improved Division by Invariant Integers, https://gmplib.org/~tege/division-paper.pdf. Those papers address efficient reciprocal-based sequences; this document supplies its own conservative all-divisor Newton error proof and binds its O(log w) tariff to the current native rows. Credit the native and mathematical predecessor owners listed in README.md. No claim that this classical method has never appeared elsewhere in the repository is made.

The finite check exhausts all numerator/divisor pairs for widths 2 through 8 and tests deterministic wide cases through 512 bits, checks the one-correction invariant, rejects malformed bounds, and demonstrates failures when correction is omitted. The all-input result is the proof above, not an inference from these tests.
