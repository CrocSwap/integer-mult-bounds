# A uniform dyadic section with a changed output contract

Let A be exactly the 256-term target coefficient in JoyboyBrian's PR #4797,
with each actual monomial evaluated columnwise as g_f = g tensor ... tensor g.
Scalar coefficients are retained outside this tensor power. All fourth-root
phases, including the actual central word iI, are retained.

## Theorem

The 30-term signed-double-coset recipe in SECTION.json emits a fixed sum B
of 1,920 free monomials with coefficients in (1/2048) Z. For every positive
integer f,

    A_f B_f A_f = A_f,        ||B_f||_2 <= 113/32.

Consequently E_f = B_f A_f is an idempotent with exactly the kernel of A_f.
It retains all information in the source channel: A_f x = A_f y if and only
if E_f x = E_f y. For every attainable observation z, B_f z is a representative
with A_f(B_f z)=z. The original observation can remain intact.

E is not required to be the orthogonal projection. The literal width-two
oracle supplies a non-Hermitian entry witness. Thus this changes the output
contract of PR #4980; it does not contradict that theorem's necessary primes
3,5,7 for the canonical orthogonal input projection. No choice of independent
canonical Gaussian jobs, complete target, or paid saving follows from a section.

## Exact finite certificate

The actual source has equal coefficients on g and (-I)g. This is checked for
every source term. Therefore A_f=0 at odd f. For even f, work in the finite
monomial algebra quotient by precisely [-I]=[I]. Normalization subtracts either
zero or two from all eight phase exponents so that the first is zero or one.
It does not discard iI. Multiplication is actual monomial composition followed
by this normalization, so it is associative and respects all even evaluations.

In this quotient the paired coefficients of A are +/-1/8. Let a be the
lexicographically first quotient monomial, explicitly retained as the recipe
anchor. Define C = 8 a^-1 A. C has 128 distinct coefficients +/-1.

The verifier derives the full signed left and right stabilizers of C:

    L = {(l,s): l C=s C},       R = {(r,t): C r=t C},

where s,t are +/-1. Their sizes are 32 and 16. This computation is complete:
if c0 is any support word, a stabilizer must send c0 to another support word,
so its candidate lies in support(C) c0^-1 on the left, or c0^-1 support(C)
on the right. Every candidate is tested against the entire coefficient table.

For a recipe representative g, form

    T_g = sum_(r,t in R; l,s in L) t s [r g l].

Equal words are collected. The certificate checks that their nonzero absolute
multiplicities are one common positive integer m_g. Put U_g=T_g/m_g; U_g
has coefficients +/-1. With the 30 integer numerators n_g in SECTION.json, set

    D = (1/16384) sum_g n_g U_g.

The emitted D has 1,920 terms, numerators bounded by eight, and the verifier
checks the complete integer identity

    C (16384 D) C = 16384 C.

Both convolutions are coefficientwise, with no modular rank, floating point,
sampled tensor width or discovery solver in this certificate. The intermediate
table (16384 D)C has 5,408 terms; the final table has exactly the 128 prescribed
terms and their prescribed integer coefficients. It follows that C D C=C.

Define the actual decoder B=8 D a^-1. It follows, in the stated order, that

    A B A = (a C/8) (8 D a^-1) (a C/8)
          = a C D C /8 = a C/8 = A.

Every emitted monomial is independently checked to have invertible affine
binary permutation and a mod-four phase polynomial of degree at most two,
with even quadratic terms. This is the constructive free alphabet used by
the source: affine address maps, coordinate S phases and conjugate parity-S
implement the even quadratic terms. No general monomial is silently granted
free. The even evaluation homomorphism proves the identity at every even f.
At odd f it holds because A_f=0, irrespective of the chosen lifts of B.

Since B's 1,920 reduced coefficients have common denominator 2048 and integer
numerators with absolute sum 7,232, their l1 norm is 7,232/2048=113/32.
Each g_f is unitary, proving the uniform bound. Finally E^2=B(ABA)=BA=E.
If A x=0 then E x=0; if E x=0 then A x=A E x=0. These implications give
the kernel equality and exact information equivalence without a rank formula.

## Independent literal checks

independent_tensor.py uses packed column actions, independently reconstructs
the signed stabilizers and recipe, and applies the resulting actual words
without a sign quotient when evaluating tensors. It checks every one of the
64 width-two input columns of ABA=A and E^2=E, and a non-Hermitian entry of E.
It verifies literal cancellation at odd widths one and three. A dense dirty
Gaussian-integer input of length 4,096 checks the actual width-four ABA identity.
These are independent implementation checks, not the universal proof: the
full finite-algebra identity above is the reason the result holds at all widths.

## Arithmetic and complete obligation ledger

For N=8^f components the displayed decoder uses 1,920 monomial applications
and at most 1,920 scaled accumulation passes in the inherited linear-array
interface. Every coefficient is an integer of absolute value at most eight,
divided by 2048. Its integer numerator needs at most two additions/subtractions
and three fixed shifts; its denominator is an exact eleven-bit dyadic shift.
Retain one read-only observation array and use one owned zero accumulator and
one owned temporary monomial array; initializations and erasures are real
linear scans. This is an explicit logical buffer plan, not a physical tape
compiler or a claim that source address applications have unit physical cost.

If real and imaginary parts of the input lie in 2^-P Z and are bounded by M,
every term and every partial sum can be kept exactly in 2^-(P+11) Z.
Every emitted scalar has only one nonzero real or imaginary part; hence the
same bound 113 M/32 < 4M applies componentwise to partial sums. Two extra
integer magnitude bits suffice, apart from the chosen sign representation.
The input lattice widening and integer growth are independent of f. Stored
input errors bounded componentwise by epsilon are amplified by at most
113 epsilon/32 in each real/imaginary component. No rounding need occur
inside the decoder at the stated widened grid.

| Obligation | Status |
|---|---|
| Exact fixed-word section, all tensor widths, all phases | Proved by full coefficient identity |
| Same accessible information, changed oblique representative | Proved by kernel equality |
| Extra paid Gaussian children in this formal linear decoder | Zero |
| Dyadic scalars, 1,920 logical monomial/accumulation passes | Constructively bounded |
| Exact input/output grid, uniform magnitude and error factors | Proved above |
| Logical read-only input plus two owned buffers; initialize/erase scans | Constructively specified |
| Legal physical reads, routing, tape head motion, precise time invoice | Unknown |
| Returning arbitrary original owners in a completed paid producer/consumer | Unknown |
| Encoding useful canonical independent Gaussian jobs in this image | Unknown |
| Missing complementary target coordinates and eventual buffer funding | Unknown |
| Source-uniform native compiler, stock, outer contracts and new kappa | Unknown |

The opportunity is removal of odd scalar divisions from this changed recovery
module. Its 1,920 passes may be too expensive in a completed consumer. This
does not justify a downstream optimization campaign while that consumer and
complete invoice remain missing. The family decision is NARROW to this section.

## Discovery and credit

Discovery used the signed-stabilizer double-coset corner of the finite even
group: 164 nonzero source-corner basis elements and an exact linear system of
rank 51. Rational elimination gave the 30 dyadic recipe coefficients. The
discovery system is not needed or trusted by replay; the final integer identity
directly certifies the resulting section. No random seed or rank extrapolation
is a premise. Nick Petalas's PR #4825 dyadic width-four minor was an existing
positive control, not a new contribution of this package.

Credit JoyboyBrian #4797 for the resonant channel, Dugongue #4885 for its
all-width rank/projector and explicit rational recovery, JoyboyBrian #4980 for
the orthogonal scalar criterion and explicit oblique open question; retain
Yiyang/Lyy-iiis #4710, lee-phys #4688, Jacob Alan Sussman #4628 with eumemic
and Swapnil Jain and the source lineage. Prepared for JoyboyBrian with substantial
OpenAI Codex assistance. Exact automatic checks are not independent human or
proof-assistant acceptance. Apache-2.0.
