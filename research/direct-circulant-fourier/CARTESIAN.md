# Two physical roots from a Cartesian multiplier list

The input is an explicit list of r≥1 nonzero Gaussian-rational multipliers λₖ and a positive target h. A value such as 3/5+4i/5 can occur without an angle description. The output is a dyadic first column c, an exact rational unit g, and a certified positive rational margin μ for C=circ(c). They satisfy

    (C+C*)/2 > μ I,
    ||gC²−U||₂ < 2^(−h),

where U is the circulant with that input Fourier multiplier list. Identity padding preserves arbitrary values on the other wires. The source compiler from [the padded circuit proof](ROOT-CIRCUIT.md) applies to C with the returned μ. Its issued gate error is additional to the error displayed here. The computation uses only fixed input coefficients on its private tapes. [Producer](cartesian_spectrum.py) · [Physical check](check_cartesian.py)

Set b=min(1, minₖ max(|Re λₖ|,|Im λₖ|)) and B=max(1, maxₖ(|Re λₖ|+|Im λₖ|)). For every k, b≤√|λₖ|≤B. Define

    a = b/(6r),
    τ = min(2^(−h)/(2B+1), a/4)/(4r).

Use the source unit-phase routine with error at most min(1/(32r),τ/B). Each returned phase is exactly unit and Gaussian rational. [Phase routine and proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/rational-unitary-fft/PROOF.md)

## An exact cut without angle comparisons

Generate the 4r candidate cuts with this routine at angles 2πj/(4r). Distinct true grid values have distance at least 2 sin(π/(4r))≥1/r. The rational candidates therefore have pairwise distance at least 15/(16r). Each true phase λₖ/|λₖ| can exclude at most one rational candidate at distance less than d=1/(3r). At least one candidate c* survives all r exclusions.

There is an exact rational test for survival. Write v=Re(λₖ conj(c*)). The squared distance of the two unit values is 2−2v/|λₖ|. When v≤0 it is at least d². Otherwise compare v² and (1−d²/2)² |λₖ|². Both sides of the unsquared comparison are positive. Take the first c* with distance at least d for every k. Put γ=−conj(c*) and g=conj(γ). These scalars have exactly unit modulus. The principal square root sₖ of γλₖ has

    Re sₖ = √|λₖ| · |1+γλₖ/|λₖ|| / 2 ≥ a.

The algorithm has a single-valued branch on every selected multiplier. Repeated input phases, negative real multipliers and candidates at a test boundary are permitted. The correction g is exact. It acts only on the logical block.

## Rational square roots and a certified column

For each w=γλₖ, set p=ceil(log₂(32B²/(τa³))) and u=2^(−p). Integer square root gives a dyadic lower approximation to √q with absolute error less than u for any nonnegative rational q. The formula is floor(sqrt(floor(2^(2p)q)))/2^p. Apply it first to |w|², obtaining ℓ≤|w|. Apply it again to max(0,(ℓ+Re w)/2), obtaining x. Round Im(w)/(2x) to the p-grid for y. The code checks x≥a/2 and |(x+iy)²−w|≤aτ.

To prove these checks always hold, let s=A+iD be the exact principal square root. We have a≤A≤B, |D|≤B, and A²=(|w|+Re w)/2. The first lower approximation changes the argument of the second square root by at most u/2. Taking the positive square root changes its value by at most u/(2A), from the difference of squares. Its final rounding contributes at most u. Thus 0≤A−x≤2u/a and x≥a/2. The imaginary error is at most u/2+|D|(A−x)/x≤u/2+4Bu/a². It follows that |x+iy−s|≤7Bu/a²≤1. Multiplication by |x+iy+s|≤2B+1≤3B gives a residual at most 21B²u/a²≤aτ. Conversely, the checked residual proves that the stored root is within τ of s, since |x+iy+s|≥A≥a.

For column j average the r stored roots against the certified phases at angles 2πjk/r. Their unit moduli keep the root error per summand below τ, while the phase error contributes at most B(τ/B). Round this average once to a dyadic grid with step at most τ. The Euclidean error per column entry is at most 3τ. If R is the true root circulant, the row and column sums give

    e = ||C−R||₂ ≤ 3rτ < min(2^(−h)/(2B+1), a/4).

It follows that Re C ≥ (a−e)I > (a/2)I, and the adapter checks this last strict inequality over the actual dyadic column at μ=a/2. The unit correction and the two products give ||gC²−U||₂≤(2B+e)e<2^(−h). These bounds control every input vector by multiplication by its norm. All width choices in the coefficient construction are O(h+log r+log B+log(1/b)). Finite sums of r rational terms can require O(r) times this width. The comparison and synthesis loops use O(r²) rational operations, in addition to the retained phase computations. Exact Hermitian elimination uses O(r³) rational operations and polynomial-bit Schur minors. Private preparation, bit cost and tape storage are polynomial in r, h and the total input description. A rational λₖ can have a large denominator with small numerical magnitude. Its input height and the time to read it are included here.

The physical replay compiles the Cartesian list (1,−1,−2,3/5+4i/5) on four of eight wires. The selected rotation has both components nonzero. It applies two issued gate programs and the exact logical-block correction, then compares against a separate Gaussian-rational four-point Fourier reference. A control omits the rotation correction. Two scalar tests cover a near-zero nonreal multiplier and a negative real multiplier. Inputs with a zero symbol or an empty table are rejected.
