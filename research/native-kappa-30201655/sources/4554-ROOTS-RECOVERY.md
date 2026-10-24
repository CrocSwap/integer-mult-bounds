# Native root seeds and exact product recovery

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
Every algorithm here acts directly on bounded words, arrays and arithmetic.
There is no Turing-machine primitive, simulator, conversion or multiplication
black box on an entire variable-length input. Ordinary MUL/DIV on word-sized
operands are allowed, with explicit sufficient width below.

## 1. A generated primitive-root seed with certified precision

For every integer D>=1 and requested p>=1, root_seed.py constructs Gaussian
dyadic coordinates x/2^p,y/2^p satisfying

    max(|x/2^p - cos(2pi/D)|, |y/2^p - sin(2pi/D)|) < 2^-p.

Take P=8(p+16), S=2^P, K=128(p+1). It suffices that every word has at least
2P+20 bits and that D and all array/control addresses fit in one word. Signed
integers are a sign bit and an unsigned magnitude; signed arithmetic expands
to bounded comparisons, ordinary ADD/SUB and word MUL/DIV. This is a uniform
finite loop algorithm, not a stored transcendental constant or root oracle.
For p=Theta(log N) and D<=N^C with fixed C, the sufficient word width remains
Theta(log N). Constants are deliberately conservative.

### Construct pi rather than assuming it

Use Machin's identity pi=16 arctan(1/5)-4 arctan(1/239). Its identity can be
verified without a numerical pi supplier: tan(2 arctan(1/5))=5/12 and
 tan(4 arctan(1/5))=120/119. The tangent subtraction formula then gives
 tan(4 arctan(1/5)-arctan(1/239))=1; the angle is in (0,pi/2), so it is pi/4.

For q=5 and 239, sum the alternating terms

    (-1)^j floor(S / ((2j+1) q^(2j+1)))

while q^(2j+1)<=S. Generate successive powers by multiplication by the fixed
integer q^2. There are at most P+1 terms. Each floored term differs from its
exact scaled term by less than 1, and the alternating remainder after stopping
is at most 1/S. Consequently the constructed integer A obeys

    |A/S - pi| <= 20(P+2)/S.

Every denominator is at most S(2P+3); the next q-power is at most 239^2 S.
These are bounded O(P)-bit integers. Compute the integer angle t=floor(2A/D).
Then 0<=t<=8S and

    |t/S - 2pi/D| <= [40(P+2)+1]/S.

No search for a prime or primitive root is involved.

### Fixed-point complex Taylor evaluation

Start the Taylor term and sum at (S,0). For k=1,...,K, replace the current
term (a,b) by

    (trunc(-b*t/(S*k)), trunc(a*t/(S*k))),

and add it to the sum. Truncation is toward zero, implemented on sign/magnitude
words. Let theta=t/S. Each coordinate's rounding error in term k satisfies
E_k <= (8/k) E_(k-1)+1/S. Expanding this recurrence and using
j!/k!<=1/(k-j)! yields E_k<exp(8)/S<4096/S. Thus the summed rounding error in
each coordinate is at most 4096K/S.

For completeness, exp(8)<4096 follows from the elementary estimate
exp(1)<11/4 and (11/4)^8<4096. The first estimate follows by summing through
1/3! and bounding the tail from 1/4! by (1/24)sum_j 5^-j.

The omitted Taylor tail is at most 2*8^(K+1)/(K+1)!, since the subsequent ratio
is below 1/2. The last K/2+1 factorial factors are each at least 128, so this
is at most 2^(-K/2-3), which is <=32/S for all p>=1. The cosine and sine
functions are 1-Lipschitz on the real line. Combining the angle, rounding and
tail errors gives the explicit coordinate bound

    E_internal <= [40(P+2)+1+4096K+32]/S.

The displayed numerator times 2^(p+1) is strictly less than S. Finally round
the two fixed-point sums to nearest at p fractional bits. This adds at most
2^(-p-1), proving the stated strict 2^-p error.

Term and partial-sum magnitudes are below 2^14 S: the exact absolute Taylor
mass is below exp(8), and the accumulated rounding envelope is smaller than S.
Products with t are below 2^(2P+17), denominators and all Machin intermediates
are smaller still. Thus 2P+20 bits is a sufficient native arithmetic bound.
The implementation charges a conservative

    100(P+1)+40(K+1)

word-operation envelope. Both P and K are O(p), so setup is O(p) word
operations and O(1) live arithmetic words, besides caller storage. It is not
necessary to form factorials or unbounded exact rational denominators.

## 2. Rounding and CRT recover exact convolution coefficients

Let two nonnegative base-beta digit arrays have lengths a,b, beta=2^h>=2.
Every digit is below beta. Their ordinary linear convolution has length
a+b-1 and coefficients

    c_j = sum_(i+k=j) u_i v_k,
    0 <= c_j <= C=min(a,b)(beta-1)^2.

**Rounded numerical route.** If a computed dyadic real value Y_j/2^P satisfies
|Y_j/2^P-c_j|<1/2 for every j, nearest-integer rounding recovers every c_j
exactly. Range-checking 0<=c_j<=C is useful, but does not itself prove the
error premise. The numerical transform must establish that premise from its
actual precision and prefix-norm bounds; it cannot be inferred from good
sample outputs. The recovery loop costs O(a+b) word operations. Its input
integers fit when 2^P(C+1), plus fixed rounding slack, fits in a word.

**Exact modular route.** For distinct certified primes p_1,...,p_s, let
Q=product p_i. If Q>C, the canonical residue in [0,Q) is c_j itself. For
signed coefficients |c_j|<=C, use Q>2C and the representative in (-Q/2,Q/2).

The supplied CRT constructor checks each prime by literal trial division and
constructs inverses of preceding products by modular repeated squaring with
exponent p_i-2. Primality and inverse work is charged setup. Trial division
costs O(sum sqrt(p_i)) word operations; modular inversion costs
O(sum log p_i). This is a constructive positive algorithm, but these setup
costs are not asserted to fit a fast FFT bound. A fast application must provide
its own fully costed modulus construction or choose the numerical route above.

For each coefficient maintain its reconstructed x in [0,M), initially x=0,
M=1. The precomputed next modulus data give

    t = ((r_i - (x mod p_i)) mod p_i) * inv(M mod p_i) mod p_i,
    x <- x + M*t,   M <- M*p_i.

Compute the subtraction as r_i+p_i-(x mod p_i), then reduce; it is nonnegative.
Induction proves all processed congruences and 0<=x<M. At the end uniqueness
proves exact recovery. The cost is O(s) native word operations per coefficient,
with no per-coefficient root/inverse search. It suffices that Q, 2Q, every
p_i^2 and all actual buffer indices, with constant arithmetic slack, fit in
a word. If Q is polynomial in input length and s is fixed, this is a genuine
logarithmic-word O(a+b) recovery stage. No such conclusion is made if Q grows
beyond the declared word width.

## 3. Linear native carry propagation and exact product

Append c_(a+b-1)=0. Set carry=0. For j=0,...,a+b-1 perform

    t = c_j + carry;
    digit_j = t AND (beta-1);
    carry = t >> h.

If carry<=min(a,b)(beta-1), then

    t <= min(a,b) beta(beta-1),

and the next carry obeys the same bound. Thus this quantity, together with
buffer addresses, is a sufficient word bound. No large input-sized integer
is ever multiplied by the algorithm.

The induction invariant is

    sum_(j<i) digit_j beta^j + beta^i carry_i
      = sum_(j<i) c_j beta^j.

At completion the right side is the exact product of the two original digit
arrays. That product is below beta^(a+b), so after a+b emitted digits the carry
is zero. The output digits therefore represent the exact integer product.
Each iteration takes a constant number of native operations, for O(a+b) time
and O(1) arithmetic scratch. Separate source/result arrays give an immediate
frame/preservation property; ordinary streaming array stores are sufficient.

If the original inputs had exactly n bits and their limb arrays are padded to
ceil(n/h) words, the output may contain high zero limbs. The bound product<2^(2n)
justifies removing them and masking any partial top output limb in O(a+b)
time; adding zeros to an MSB-first representation would be a different action.

## 4. Direct native multiplication assembly

Take h=Theta(log n), so each input has L=Theta(n/log n) digits. A directly
implemented approximate DFT/NTT convolution on N=Theta(L) entries, with its
own paid roots, normalization, bounded-word arithmetic and error<1/2, combines
with the recovery above in O(L) additional word operations. The numerical
root seed costs O(log n) when its requested precision is Theta(log n).

Thus a direct O(N log N) word-operation convolution gives a direct O(n)
Word RAM integer multiplication algorithm. If a fully implemented stronger
native convolution has cost O(N log^(1-kappa) N), then the same explicit
assembly gives O(n/log^kappa n) word operations. The latter sentence is a
sufficient composition theorem, not an assertion that this packet supplies
that stronger convolution. It does not use a TM black box anywhere.

## 5. Evidence, library reuse and next questions

`root_seed.py` checks 80 seeds, p=1,...,128 and orders through 2^40+87, against
a separate high-precision Decimal implementation. Its transcendental reference
is validation-only and is not called by the native constructor. An undersized
word rejects; the exact order-four result is checked.

`recover.py` checks 960 products, 10,752 CRT coefficients and 10,752 rounded
coefficients, including extremal digit arrays, unequal lengths, signed CRT,
composite/duplicate moduli, an invalid carry input and an actual half-unit
rounding corruption. These are finite tests, not universal proof certificates.

The existing Problem 1.8 sources provide directly relevant precedents:
`MpLimbs20261007.lv_dig`, `dig_add_high`, `addCode` and `add_run` establish
literal limb representation and carries in bounded IMP; `Frame` describes
preserved arrays and IO. `Problem18IMPPrimeInverse20261001.inverseRoutine_run`
constructs literal modular inversion from a prime/nonzero residue and charges
84*size(p)+34 bounded instructions. Their source was inspected, not freshly
kernel-audited here. This packet uses these as precedents, not as claims that
the newly supplied Python/Word RAM algorithms have been formalized.

The federated DAG search for Machin also found the existing source-only
`FamousTheorems.machin_formula` public-catalog record and a Gerver-sofa
certificate declaration; neither hit was re-elaborated or imported. Actual
inspected project precedents include Dugongue's PR #3877,
`research/gaussian-expansion-headroom/PROOF.md`, whose interval backend is
credited to Mason Hale and whose retained lineage includes Jose Manuel's
physical chirp/Gaussian work. It already uses Machin arctangent remainders and
outward Taylor enclosures. The registered OpenAI preprint
*The maximum number of mutually unbiased bases in dimension six*
(2026-09-24), `build/sections/rounding.tex`, already writes the tangent proof
and explicit alternating arctangent tail. These are method precedents, not
freshly checked proofs or new claims of invention. Our new component is the
explicit bounded-word seed algorithm, global precision envelope and its
integration contract. The sources and exact inspected hashes are recorded.

Concrete next tasks are to bind the recovery threshold to the actual native
transform's row-norm/error proof, emit the signed fixed-point/root routines in
the actual RamStd/IMP language, and audit their chosen word/arena width. A fast
prime-based variant additionally needs a fast fully paid prime/root supplier.
None of those requirements is hidden inside the executable root constructor.
