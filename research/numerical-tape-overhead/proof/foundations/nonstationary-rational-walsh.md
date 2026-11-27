# Varying-arity rational Walsh execution on fixed tapes

Status: **proved numerical component; independently reviewed by C** in
[REVIEW-NONSTATIONARY-RATIONAL-WALSH.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/route-c/REVIEW-NONSTATIONARY-RATIONAL-WALSH.md). The exact-interchange
premise is stated in section 1 and is supplied separately by B's
[adaptive-interchange.md](adaptive-interchange.md), itself reviewed by C. This note does not claim that
premise from a recurrence alone, and does not by itself prove an integer
multiplication bound.

Source pins: programme `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math
`3344da59991ed94f9ba711217b29c1d760badfa6`. Read source sections are Fourier
`kernel.tex`, `binary.tex` and tape `walsh.tex`, `permutations.tex`, plus
the source uniform precision mechanism. Predecessor dependencies are
[pairwise-newton-division.md](pairwise-newton-division.md), [growing-arity-circuit-candidate.md](growing-arity-circuit-candidate.md),
[polynomial-auxiliary-cost-audit.md](polynomial-auxiliary-cost-audit.md), and this session's independently
reviewed [compact-rational-walsh.md](compact-rational-walsh.md). The predecessor varying-arity result
was in an arithmetic/indexing model. This note supplies a different arity
choice, physical cost recurrence and complete numerical-space/precision
interface under the stated exact interchanger.

All logarithms are base two. Write

    F(x)=(x^2 log(2+x))^(1/3),   x>=1,
    J(u)=sqrt(1+u) 2^[C_I F(log(2+u))].                 (NW1)

Absolute effective constants may be enlarged in the proof. They never
depend on the input length, a locally chosen arity or a spectral key.

## 1. Exact-interchange premise and theorem

**Interface I-var.** One fixed finite-alphabet multitape machine exactly
interchanges two equal-width binary address fields of width u, with
arbitrary positive prefix, gap and suffix ranges, in at most C_I V J(u)
steps and C_I V visited cells. Here V is the incoming bit volume. Field
encodings, actual template construction, all range padding, descriptor
work and any choice of internal arity are included. The returned stream
has exactly the original volume and format. No numerical interpretation
of the bits is imposed.

The conclusion below can instead take a fixed absolute polynomial in
log(V+2) as an additive setup/workspace term in I-var. In the numerical
application all active arrays have exponentially many records, so section
7 absorbs that term explicitly. A multiplicative space coefficient growing
with u or an internal arity is **not** this interface.

**Theorem NW.** Assume I-var. Fix positive constants c,L,D. Let N=2^k and
specify s<=c k/log(2+k) address positions. There is one deterministic fixed
multitape machine for their normalized Walsh layer, and its adjoint, with

    time <= C N k sqrt(1+k) 2^[C F(log(2+k))],
    visited cells <= C N k.                             (NW2)

The input and output real and imaginary components have fractional and
signed integer widths equal to absolute multiples of k. For input norm
at most 2^(Lk), absolute Euclidean error is at most 2^(-Dk). The constants
depend only on c,L,D and the fixed constructive interfaces. Actual
generation, coefficient preparation and all intermediate precision are
included. The bounded initial k range is handled by an explicit direct
algorithm.

The numerical format and visited-space coefficient do not change with
the local arity. The exponent F(log k) concerns the tape overhead, not
the algebraic circuit's finer predecessor bound.

## 2. Quantitative binary templates

For every sufficiently large odd m, the explicit source binary label
family has

    u=ceil(log m), v=ceil(log(u+2)),
    L_F=2 ceil(sqrt(u/v)),
    q_F=2^ceil(2+2u/L_F), D_F<=1+L_F q_F,
    A_m=2(m+D_F-1).

Integer square-root comparisons implement these choices. The predecessor
audit supplies the exact pencil bound

    R_m<=10(1+L_F q_F)(1+log q_F)^L_F,
    log R_m <= C_B sqrt(log(m+2) log log(m+4)).          (NW3)

One may use the exact upper dimension D_F=1+L_F q_F by adjoining orthogonal
unit directions to the nondegenerate binary Gram quotient. All label
vectors and their pairings remain unchanged. The source paired-basis and
free-endpoint arguments still apply, now with this larger auxiliary space.
This optional padding makes the finite integer arity tests independent of
an enormous explicit Gram elimination; it preserves all displayed bounds.

For a fixed effective initial threshold, q_F^L_F<=m^3 and D_F<=m, so
2m<=A_m<=4m. The rational pairwise-shift predictor has degree at most
7sqrt(m), power-of-two seed count W0=O(m), and two check-conversion phases
of one eighth of the parent volume. Finite unrolling to
h=ceil(log(m)/4) gives an exact normalized template with

    W_m=W0 q_F^L_F 8^h,      W_m is a power of two,
    sigma_m/W_m <= C sqrt(m)(R_m+1),
    W_m, sigma_m, local instruction count <= m^K.       (NW4)

One absolute K also bounds actual finite generation, matrix dimensions,
rational coefficient heights and ordinary scalar-control costs. The
on-demand construction in [compact-rational-walsh.md](compact-rational-walsh.md) removes the optional
2^m spectral and 2^(4m) column tables from the predecessor audit. Every
spectral coefficient is calculated from its O(m)-bit query key.

The full-rate row program accepts every independent numerical row. A
completed child is a normalized unitary Walsh transform; source binary
normalization removes all f-dependent powers of two from the external
rational coefficient list. An odd-width one-bit butterfly is handled
separately using 1/sqrt(2).

## 3. A uniform local numerical payload schedule

The binary Fourier pencil has a simpler constant-array schedule than the
scalar low-rank interchange pencil. Retain original inputs and final
output accumulators. Process rectangles one at a time.

For a free rectangle, copy and apply its first shared partial transforms
to the current source subset. This subset contains at most all input
rows. Keep those transformed sources across every query j. For each j,
perform the source's monomial representative maps and row arithmetic,
and add to a destination subset accumulator. That subset also contains
at most all rows. Only after all j apply the shared final partial
transforms and add to the ordinary-layout output. Release all current
rectangle scratch. This is exactly the source sharing order, so no axis
call is repeated for each j.

For a charged rectangle, retain only its common sum, scalar work arrays
and the current destination accumulator. Its separately billed query
kernel is executed in the source order. A dense polynomial-size row map
can scan each input/output row pair in succession, retaining immutable
input and one output region. Repeated scans are polynomial(m) ordinary
work, with a fixed number of regions.

The two-array Newton predictor, check maps, correction and finite
one-eighth contraction also use a fixed number of full arrays. At a
contraction child park only a constant multiple of the parent volume;
different phases reuse their regions. Thus each local numerical template
uses

    C V + polynomial(m,k)                               (NW5)

visited cells outside an active child, with C absolute. Here V is actual
encoded numerical bit volume, and k is the unchanged global address-width
and precision parameter. The number of tapes is fixed. In particular,
the template does not retain all rectangle incidence arrays at once.

This schedule follows the source endpoint algebra and the predecessor
uniform-array diagnostic, now with physical scans included. Every row
role has polynomial(m) size. Extracting a selected role across arbitrary
prefixes, reversing the extraction and rewinding can each be charged a
complete V-bit scan. The module widths here are polynomial(m), unlike
the exact characteristic-two full-rate cyclic module.

## 4. Physical local cost and rational arithmetic

The proof of source `permutations.tex` uses the interchanger only as a
complete field swap. Replace its width-u cost by J(u). The eight guarded
rotations, exceptional-set sorting and restoration then give

    C V(1+J(u))(1+log(2+k)) + polynomial(k)              (NW6)

for one packed-XOR primitive, with O(V)+polynomial(k) visited cells. The
guard is G=C0 ceil(log(2+k)) for one absolute C0. The controls and rank
computations have fixed polynomial degree in k: all local m below satisfy
m<=k, and their explicit descriptions are polynomial in m. Choosing C0
after this fixed degree pays for exceptional records and offset setup.
No guard coefficient depending on m remains necessary. Short slots use
direct bit operations. An arbitrary permutation of the k address bits
uses the source bounded number of such primitives, at u<=k.

Binary elimination implements each column matrix of the source Fourier
template in polynomial(m) slot additions and exchanges. Their slot width
is no larger than the current active width a. Since J is increasing,
all physical nonrecursive address work is at most

    V m^K (1+J(a))(1+log(2+k)) + polynomial(m,k).         (NW7)

The rational coefficients have numerator and denominator at most m^K bits.
For each numerical record its complete O(k)-bit address may be read and
rewound; the record itself has Theta(k) encoded bits. Computing the
column parities, all shifted counts, the actual nonzero-gap defect set,
its Vandermonde inverse and a requested rational coefficient costs
polynomial(m) control work plus polynomial(m) times k address work. It
uses no all-key lookup table.

For a rational with B<=m^K-bit numerator/denominator, bounded-remainder
long division prepares p fractional bits in O(B^2+pB) steps. At p=C0 k
and B<=k, this is polynomial(m) times k, since the divisor remains B bits
throughout. The source fixed O(k log(2+k)) short multiplier then applies
the prepared coefficient. Repeating this for every scalar operation
fits (NW7), after increasing K. It does not require a k-bit divisor at
every record. Coefficient errors are included in section 8.

## 5. Varying arity and exact spectator batches

For even active width a above a fixed threshold, put

    x=ceil(log(a+2)),
    v_x=ceil(log(x+2)),
    y=least positive integer with y^3>=x^2 v_x,
    m=2^y-1.                                           (NW8)

This m is odd. All quantities use integer bit lengths, cubing and binary
search, with no real root oracle. For large a,

    F(x)<=y<=2F(x),   y=o(x),   m=a^o(1).               (NW9)

Choose f to be the largest even integer at most a/A_m. Run the normalized
template on the Af selected bits, and handle the even remaining
a-A_m f<2A_m bits with direct four-point butterflies. If f=0 or the
fixed parameter guards fail, use the bounded direct base. The direct
remainder cost is polynomial(m) times V log(2+k), already in (NW7).
There is no need to express a in a fixed base or to re-pad after each
level.

The root has q=2^(k-s) complete spectator rows after moving the selected
positions to a contiguous block. At every descent the leading row count
divides by exactly W_m. The child still has the same independent inactive
address bits and all complete spectator ranges; only its chosen f-bit
slot is active.

Along a path with active widths a_i and arities m_i,

    f_i<=a_i/A_(m_i),
    sum_i log m_i <= sum_i log A_(m_i) <= log a_0.       (NW10)

Therefore (NW4) gives

    product_i W_(m_i) <= a_0^K.                         (NW11)

Every W_m is a power of two. For sufficiently large global k,
k-s>=k/2>=K log(2+k), so q is already divisible by the full product in
(NW11). Every leading split is exact. No additional numerical spectator
padding, hidden volume growth or variable tape count is needed. The
product and all row-count descriptors have polynomial(k) bits and work.
All nodes at the same numerical depth use the same a_i and m_i; different
spatial positions of a selected child slot do not alter its width.

## 6. Solving the physical recurrence

Divide time by the numerical bit volume V. Up to the absolute-degree
setup terms treated below, the actual recurrence is

    T_k(a) <= m^K(1+J(a))(1+log(2+k))
                  +(sigma_m/W_m) T_k(f).               (NW12)

The child volume is V/W_m, not V. The sharing invoice in (NW4) is unchanged
by the serial ordinary-work schedule of section 3.

Write psi(y)=sqrt(y log(y+2)). From (NW3)--(NW4), after enlarging an
absolute C_B,

    (sigma_m/W_m) sqrt(f/a) <= 2^[C_B psi(y)].           (NW13)

The function F has derivative

    F'(t)=F(t)/3 [2/t+1/((t+2) ln(t+2))].

For large x and d in [y/2,2y], with y as in (NW8), integration over
[x-d,x] gives

    F(x)-F(x-d) >= (d/2) x^(-1/3) log(x+2)^(1/3)
                 >= c psi(y)                          (NW14)

for an absolute c>0. For example a sufficiently enlarged fixed base
permits c=1/32. Indeed y is comparable to
x^(2/3)log(x+2)^(1/3), whereas log(y+2)<=log(x+2) for large x. The child
quantity x_f=ceil(log(f+2)) satisfies x_f<=x-y+O(1); hence its decrement
has at least y/2, and a larger decrement only improves the inequality.

Also m^K<=2^(2K F(x)). Thus the local toll divided by sqrt(a) is at most

    C 2^[(C_I+2K+1)F(x)] (1+log(2+k)).                 (NW15)

Choose a single absolute C_* exceeding C_I+2K+3 and 32(C_B+3). Equations
(NW13)--(NW15), with an enlarged fixed base if necessary, imply by
induction

    T_k(a) <= C_* sqrt(1+a) 2^[C_* F(log(a+2))]
                                      (1+log(2+k)).    (NW16)

For precision in the rounded argument one may first use
F(ceil(log(a+2))) in the induction. Its difference from F(log(a+2))
is bounded by an absolute constant, which is absorbed into C_*.
The recursive part uses at most one quarter of the proposed bound,
and the local toll uses at most one half. Bounded widths use direct
butterflies. This proves the recurrence claim with no depth-dependent
constant and no substitution of O_m(1) into a varying family.

The two initial/final bit-position permutations cost
O(V J(k) log(2+k)); the odd one-bit butterfly costs O(V log(2+k)).
Both fit (NW2). The extra log(2+k) factor in (NW16) contributes only
O(log log k) to the exponent and is absorbed by F(log(2+k)).

## 7. Actual setup, node count and visited cells

Each template has at most m^K array operations, child calls and descriptor
instructions. Equation (NW10) bounds their product along a path by a
fixed polynomial in a_0. There are at most log(a_0+2) numerical levels,
so the entire expanded numerical call tree and its finite repair
subprograms have polynomial(k) array steps, with an absolute degree.
Rebuilding a template at every node, even if unnecessary, therefore
costs polynomial(k) time and workspace. No table of size 2^m is rebuilt.

The number of visited descriptors along a path is polynomial(k). Every
numerical array has at least its complete root spectator count divided
by the product in (NW11), possibly further divided by polynomial(k)
finite-repair factors. Its record count is consequently at least
2^(k/2)/polynomial(k). Thus every fixed polynomial(k) setup and word
workspace term is absorbed in a constant multiple of any active numerical
volume beyond one effective global threshold. One can charge all such
terms at the root instead, since their total is polynomial(k)<<N k.

The local payload coefficient in (NW5) is absolute. A numerical spatial
child has at most half its parent's volume because W_m>=2. A finite
repair child has one eighth. Exact interchanger calls have their own
uniform linear-space guarantee I-var. Sequential children, subsequent
rectangles and direct remainders reuse marked regions. The parked arrays
therefore form a geometric sum along the actual nested depth-first
execution, bounded by C N k with C absolute. Polynomial descriptor/word
areas are also reused, so this is a bound on cells ever visited.

The finite parameter constructor is explicit and has polynomial(m) work.
The local base is an effectively chosen fixed threshold. In particular,
all inequalities can be enforced by enlarging a fixed x0 until the
elementary estimates F(x)=o(x), (NW14), the predecessor binary guards
and m^K<=a^(1/8) hold for x>=x0; their displayed monotone bounds give
a finite constructive choice. No per-input unbounded search or arbitrary
machine-dependent absorption exponent is used.

## 8. Uniform O(k) numerical precision

The rational height proof and source normalizations remain valid at every
m. A deliberately coarse bound for the logarithm of the product of
one-node norm bounds is m^K, after increasing the same absolute K.
Completed normalized child transforms are unitary and completed exact
address changes are permutations. Their internal binary scratch is not
a numerical array on which rounding occurs.

Along a numerical path, the total logarithmic amplification is at most

    sum_i m_i^K <= (1+log k) 2^[2K F(log(k+2)+1)]
                  = k^o(1).                            (NW17)

For an input-to-intermediate estimate use the path to that intermediate;
for propagation from an additive fault to a later array use the paths
to their first common ancestor. This at most doubles (NW17). Completed
intervening pieces or calls are unitary. Consequently, after a fixed
global threshold, every propagation logarithm is below k/10, and every
coefficient height B_m<=m^K is below k/10. Bounded parameters are included
by enlarging the threshold and format constants.

Every array has at most C N numerical entries, with C absolute by
section 7, and there are polynomial(k) array operations. For input norm
2^(Lk), ideal intermediate norms are below 2^((L+1)k). Approximate each
rational coefficient to absolute error 2^(-p), prepare 1/sqrt(2) by
certified dyadic bisection once, and round after numerical arithmetic to
the same mesh. The per-array rounding contribution is at most
C sqrt(N)2^(-p). The coefficient perturbations contribute at most
polynomial(k)2^(-p) times the current numerical norm; their polynomial
matrix multiplicity is already in the explicit node count.

Freeze the actual faults and propagate them through the ideal linear
circuit. Equations (NW17) and the polynomial operation count show that
p=C0 k, for one absolute C0 depending only on c,L,D and the fixed
construction, makes the total error at every array at most 2^(-Dk).
Induction justifies the assumed intermediate norm bound and signed
integer widths C1 k. Temporary exact coefficient products and sums use
O(k) bits, apart from the separately paid polynomial(k) control scratch.
The bounded-divisor preparation of section 4 meets this same format.

This completes the conditional numerical theorem. The layer is
self-adjoint, so the same construction and estimates supply its adjoint.
