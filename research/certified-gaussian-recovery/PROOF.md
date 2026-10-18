# Certified Gaussian resampling through exact integer recovery

## 1. Result and its boundary

This package executes the Gaussian numerical path requested in PR2298's
second open question. It independently implements the periodic Gaussian
expansion, nearest-coordinate selection, inverse correction, normalized
power-of-two Fourier transforms, retained frequency permutations, two
forward source transforms, pointwise multiplication, the opposite source
transform, inverse CRT order, integer decoding and carry propagation.

**Finite uniform theorem.** At the three source/target pairs `(5,8)`,
`(7,16)`, `(13,32)`, Gaussian parameter `alpha=5`, output precision `p=256`
and enclosure precision `Q=448`, the supplied certificate and algorithm
multiply every pair of nonnegative integers of at most **14,592 bits**.
The caller uses radix `2^64`, supplies exact `2n`-bit output for a declared
width `1 <= n <= 14592`, and certifies a coefficient recovery error strictly
below `2^-49`. The certificate is uniform over the input digits. The
executed examples are corroborating tests, not an enumeration of all inputs.

The more general conditional statement is useful: for any configuration
accepted by `uniform_certificate`, the same caller is correct throughout
the returned input domain. All acceptance inequalities are rational.
The proof below justifies the finite certificates and the computation.
It is a written proof with executable certificates, not a proof-assistant
formalization or independent human review.

This is a dense reference implementation. It uses indexed Python arrays,
arbitrary-precision integer arithmetic, and a conventional radix-two FFT.
It does not implement the fast Gaussian chirp algorithm, the selected
recursive butterfly supplier, their physical multitape schedules, the
long polynomial-record representation, or their asymptotic cost bounds.
The small boxes satisfy the original one-dimensional Gaussian lemma;
they are not claimed to be instances beyond the enormous eventual cutoff
of PR2298's outer parameter recipe. No new kappa or all-size faster
integer-multiplication theorem follows from this artifact.

## 2. The exact maps being enclosed

Let `2 <= s < t` be coprime, with `t` a power of two. Put
`sigma=t/s`, `theta=sigma-1`,

    q_j = floor(tj/s + 1/2),       beta_j = tj/s - q_j.

Then `-1/2 <= beta_j < 1/2`, periodically modulo `s`. Define

    (S u)_k = alpha^-1 sum_(j in Z)
                exp(-pi (j-sk/t)^2/alpha^2) u_(j mod s),

    D_jj = exp(pi alpha^2 beta_j^2),

    E_j,(j+h mod s) += exp(-pi alpha^2 X_(j,h)), h != 0,
    X_(j,h) = (sigma h + beta_j)^2 - beta_(j+h)^2.

Here `N=I+E=C T D` in the notation of the retained source07 proof;
`C` selects positions `q_j`. **Nonzero multiples of s occur in E**, even
though their matrix entries are diagonal. Periodic indexing does not
delete those summands.

The two contraction matrices used by the code are

    A = S/2,
    D' = 2^(-(2 alpha^2-2)) D,
    B = D' N^-1/2.

Selection `C` is performed before applying the `s` by `s` matrix `B`.
For normalized negative-sign Fourier transform `F_t`, the Gaussian
source operator is

    G = 2^(2 alpha^2) B C P_t F_t A,
    (P_t z)_k = z_(-s k mod t).

The intended source operator is `U=P_s F_s`, with
`(P_s z)_j=z_(t j mod s)`. These are Harvey--van der Hoeven's Gaussian
maps and the retained source07 permutation convention; their invention
is not part of this contribution.

The code checks the original domain `p>100`, `alpha>=2`, `alpha^2<p`,
`theta>p/alpha^4` and `t<2^p`. All three retained pairs satisfy it.
Their source product is `S_total=5*7*13=455`.

## 3. Outward arithmetic and the infinite tails

An `Interval(lo,hi,Q)` represents the closed real interval
`[lo/2^Q,hi/2^Q]`. Additions and negations are exact. Multiplication
takes the minimum and maximum of all four endpoint products and rounds
outward with integer floor and ceiling. Positive reciprocals reverse
endpoints and also round outward. No machine floating-point operation
participates in acceptance.

`pi_interval` uses Machin's identity and alternating rational arctangent
series, stopping with their next-term remainders below `2^(-Q-16)`.
It combines those rational endpoints before converting to the dyadic
grid. For `exp(-x)`, `x>=0`, reduce by powers of two to `0<=y<=1/8`.
The positive exponential series through degree `m` has omitted tail at
most `2/(8^(m+1)(m+1)!)`. Add that tail, take a positive reciprocal,
and square back. If `x>=Q`, the enclosure `[0,2^-Q]` follows from `e>2`.
Each step encloses the exact exponential, including the reduction and
rounding errors. A different positive rational Taylor calculation checks
the implementation at twelve test points.

Phase evaluation reduces a rational angle by the nearest quarter turn,
so the remaining angle has magnitude at most `pi/4<4/5`. Alternating
sine and cosine series have next-term remainders bounded using `4/5`;
these are added before rotating by the exact quarter turn. This supplies
independent enclosures of the power-of-two FFT phases and the odd-order
Fourier matrix used for certification.

For expansion, choose the integral radius
`R=alpha*(floor(sqrt(Q+16))+2)` and retain indices from
`floor(sk/t)-R` through `ceil(sk/t)+R`. We check

    3 R^2/alpha^2 > Q+16,
    3(2R+1)/alpha^2 >= 1.

Since `pi>3` and `e>2`, each omitted side is bounded by a geometric
series of ratio at most `1/2`. The two tails together are below
`4*2^(-Q-16)<2^-Q`, even before the factor `1/(2 alpha)` of A.
Adding one working-grid unit to each matrix entry is therefore a safe
entrywise enclosure of its omitted positive terms.

For the correction, for every nonzero integer `h`,

    X_(j,h) >= (sigma |h|-1/2)^2-1/4
              = sigma^2 h^2-sigma |h|
             >= sigma theta h^2.

Set `a=3 alpha^2 sigma theta`. Choose an integral cutoff `H` satisfying
`a H^2>Q+16` and `a(2H+1)>=1`, and retain every `0<|h|<=H`.
The same geometric argument bounds the omitted positive row tail below
one grid unit. The implementation adds one unit to each entry. This
overcount remains safe even when several shifts share a residue.

These tail statements cover the infinite sums, not only their sampled
terms. The code's cutoff inequalities are checked exactly.

## 4. Inverse correction and complete operator certificates

Let `eta` be the largest outward upper row sum of the enclosed positive
matrix E. The code requires `eta<1/2`. Thus N is invertible, and for

    J_K = I-E+E^2-...+(-E)^(K-1),

the operator-norm error satisfies

    ||N^-1-J_K||_infinity <= eta^K/(1-eta).

This is the inverse error, including the factor `1/(1-eta)`, rather than
only the Neumann residual. The code chooses K to make it below
`2^(-Q+24)`, evaluates the polynomial by outward interval Horner
arithmetic, then widens every entry by the full inverse-error bound.
Multiplying by D'/2 encloses B. Explicit outward row sums certify
`||A||_infinity<1` and `||B||_infinity<1` for each configuration.

For every basis input, `exact_column` applies the *Gaussian* factorization,
with its enclosed infinite sums and enclosed inverse. `direct_column`
separately encloses the entries

    U_kj = exp(-2 pi i t k j/s)/s.

For each row we sum upper bounds for the absolute real and imaginary
parts of every entry of `G-U`. Let the maximum row sum be delta. Because
complex modulus is bounded by the sum of the component magnitudes,

    ||G-U||_infinity <= delta.

This is a bound for **every complex vector in the unit sup-norm ball**,
not only for the basis vectors. No assertion of exact equality is inferred
from interval overlap. The retained three bounds are respectively
`delta<2^-392`, `delta<2^-391`, `delta<2^-389`.

The production transform uses the Gaussian factorization, not the direct
odd Fourier matrix. The latter supplies a finite operator certificate
and contributes delta to the error budget. Consequently correctness of
these finite runs does not need to assume the exact Gaussian/Fourier
identity: its independently bounded residual is explicitly charged.
This does not replace the all-size mathematical identity or its proof.

## 5. Actual rounding and a uniform bound

Between completed numerical stages, each component is an integer multiple
of `h=2^-p`. For a real enclosure `[l,u]`, extraction uses zero if it
contains zero, rounds `l` toward zero if it is positive, and rounds `u`
toward zero if it is negative. Therefore the extracted component has
magnitude no larger than **any** exact component in the interval.
For complex values this preserves a known disk bound. Its component
error is at most `h+(u-l)`. The code also records the tighter actual
distance to the interval endpoints.

Apply this rule after A and B, and after every normalized radix-two
butterfly. Each butterfly is a contraction in the sup norm. Its phase
is enclosed rigorously; the phase value is not assumed exactly
representable. The FFT is actually executed by these butterflies.
Both signs are implemented by exact input/output conjugation.

Here are the uniform local estimates used by `certify_operator`.
Let `L=2^Q`. For a real matrix with n columns, let `w` be the largest
row sum of its interval widths in integer grid units. Multiplication
by an exact p-grid component of magnitude at most one adds at most
two units to an interval width. The sum of real and imaginary widths
is at most `(2w+4n)/L`. Hence extraction error is bounded by

    e_matrix = 2h+(2w+4n)/L.

For a butterfly, let `v` be the sum of its phase's two component widths.
Complex multiplication, exact addition, division by two and outward
rounding give a sum of output widths at most `(v+8)/L`. Thus its
extraction error is at most `2h+(v+8)/L`. Take the maximum at each
FFT level and sum the levels to get `e_FFT`.

Since A, B and the exact normalized FFT are contractions, and the final
scale is exact, the returned source-transform error relative to U is

    E_line = 2^(2 alpha^2) (e_A+e_FFT+e_B) + delta.

All three retained lines have `E_line<2^-202`. The runtime derives a
usually tighter data-dependent error and checks it against this uniform
bound. It checks disk membership explicitly. The rescaled output is
guaranteed to stay in the disk on the quarter-disk inputs and margins
used below; we do not claim that the exit check always succeeds on
arbitrary boundary points of the full unit disk.

For a tensor product, complete one axis at a time. Each exact source-axis
operator U is a contraction, so errors add over axes. They are not
multiplied by the internal Gaussian scale again. Put
`E=sum E_line<3*2^-202`; the code checks the exact rational value.

## 6. Permutations, products and integer recovery

Map the index j of a digit polynomial to the CRT coordinate
`(j mod s_1,...,j mod s_d)`. This is a bijection for pairwise coprime
source lengths. Scale each nonnegative radix-`2^b` digit by `2^(-b-2)`.
The input components are exact p-grid points and have modulus below 1/4.
Forward tensor transforms have modulus below `.25+E<.26`.

Let F be the tensor of normalized negative Fourier transforms and let
R multiply the frequency index of each axis by its corresponding t.
The forward endpoint is `U=R F`; the opposite endpoint is `U+=R F+`.
For these permutations,

    F+ R = R^-1 F+,
    (R a)(R b)=R(ab).

Thus `U+((Uu)(Uv))=F+((Fu)(Fv))=(u*v)/S_total^2`. Both factors of
`S_total` are necessary. This identity follows from the ordinary finite
Fourier orthogonality relations on the product group; CRT converts its
convolution to the cyclic coefficient convolution of length S_total.

The code multiplies the computed pointwise Gaussian integer pairs,
then extracts p-grid values with a uniform local error
`e_product<=2h+8/2^Q`. It does not use whole-input integer multiplication
or a direct convolution to produce its answer. For disk-bounded inputs
and computed values,

    |ab-AB| <= |a| |b-B| + |B| |a-A| <= E_forward_1+E_forward_2.

The product input to the opposite call has modulus below `.26^2`.
Every subsequent source-axis call remains strictly inside the disk.
The complete normalized convolution error is at most

    3E + e_product.

Undo digit scaling and normalization by the exact integer factor

    L_recover = S_total^2 * 2^(2b+4).

The finite uniform certificate checks

    radius = L_recover * (3E+e_product) < 2^-49 < 1/2

at `b=64`, `S_total=455`. This inequality, not agreement with an expected
product, authorizes recovery. For every coefficient, the caller computes
the smallest and largest integers in its real enclosure, requires them
to coincide and be nonnegative, and requires the imaginary enclosure to
contain zero. Only then does it select that integer.

At most 228 digits are admitted because `2*228-1=455`; therefore there
is no cyclic wrap for any product. This gives `228*64=14592` input bits.
The inverse CRT ordering is applied before the carry scan. In radix
`B0=2^b`, the scan updates

    digit_j = (coefficient_j+carry_j) mod B0,
    carry_(j+1) = floor((coefficient_j+carry_j)/B0).

The usual positional-value invariant proves that the drained output is
the product. The input-width bound implies it fits in 2n bits; leading
zeroes are emitted to reach that exact width. Zero inputs are included.

## 7. Execution, controls and full reference cost

The retained replay checks all 243 entries of the three Gaussian source
operators, 30 rounded complex-vector runs in both signs, and 289 complete
integer products. The latter perform 10,548 actual Gaussian line calls
and 9,155 pointwise products, then check every decoded coefficient by
an independently written schoolbook convolution and every binary output
against Python's integer multiplication. Those reference calculations
occur only in `verify.py`, after recovery.

The fixtures include zero, maximal digits, long carries, leading zeroes,
deterministic nonuniform inputs, and 1D/2D/3D boxes. A separate
`p=128,Q=320,alpha=4` certificate and 288-bit product exercise a second
precision setting. Runtime does not contribute to the retained receipt.

The operator controls remove the target permutation, use an incorrect
selector or remove one rescaling bit. At `(5,8)` the inverse-correction
omission also exceeds the p-bit budget. At the wider gaps that correction
can lie below that budget; its omission is deliberately **not** counted
as a failure there. An independent `(s,t,alpha)=(2,3,2)` coefficient
fixture separates the nonzero periodic winding terms; it tests the
infinite-sum definition and is not asserted to satisfy the full p>100
caller domain. Full recovery controls omit one S_total, alter maps,
reduce precision, or violate the no-wrap, theta, and interval guards.

The reference invoice includes initialization and all preprocessing:
expansion uses O(t R) enclosed Gaussian terms; correction uses O(s H)
terms; dense Neumann preparation uses O(K s^3) interval operations;
the independent operator certification uses O(s t^2+s^3) interval
operations plus phase preparation. Each executed line then uses
O(st+s^2+t log t) interval operations, plus every p-grid extraction and
the exact rescale. An axis performs S_total/s such lines per transform;
there are three transforms, S_total pointwise products, CRT input/output
passes and a full carry scan. Integer-operation bit costs are additional.

No preparation, source access, correction, or inverse scale is treated
as a free oracle. This invoice intentionally does **not** assert the
fast scalar-map or fixed-tape bounds of the research construction.

## 8. Attribution and remaining work

Harvey and van der Hoeven supply the Gaussian maps and analytic lineage.
OpenAI's retained sections 07/08 supply the permutation and normalization
conventions. Jose Manuel's PR2298 supplies the immediate executable
handoff and the conservative outer composition; his PR2234/2287 supply
the proposed completed callees, which this implementation does not run.
The PR371, PR684, PR902 and PR1430 lineage separately motivates explicit
rounding, parameter-domain, inverse-tail and rounded-Neumann accounting.

The new work is the independent enclosed implementation and its full
finite uniform composition/decoding certificate. Next, the dense A/B
backend can serve as an oracle for a genuinely sequential fast Gaussian
backend, and the conventional FFT can serve as an oracle for the selected
completed layer. Replacing either requires its own full cost and domain
proof. Those replacements, all-size parameter generation, formalization
and independent review remain open.
