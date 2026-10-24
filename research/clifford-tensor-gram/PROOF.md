# A finite and stable tensor test for dyadic Clifford programs

The [continuation](ADVANCES.md) reduces the number of tested widths,
improves 14/15 to 75/76, proves the sharp one-axis cutoff, and supplies
a compact native implementation. This note retains the original proof.

## Result

Let R = Z[i,1/2], let D = 2^n, and let C_n be the unitary matrices in
M_D(R) that normalize the n-axis Pauli group. Keep their exact global phase.
This class includes the source Gaussian gate

    C_v = (1+i)I/2 + (1-i)X_v/2,

its inverse, quadratic phase gates, affine binary permutations and the
source Hadamard gate. It is larger than the monomial subgroup.

Consider two finite scalar register programs. Each role has an independent
arbitrary input in (C^D)^(tensor f). Instructions can add a scalar multiple
of one role to another, scale a role, exchange roles, or apply U^(tensor f)
for U in C_n. Queries can add c U^(tensor f) v_s to v_d. Self queries are
permitted. Both programs and their scalar coefficients are fixed as f varies.
Every input and return role is part of the contract.

**Theorem.** The complete endpoints agree for every positive integer f if
and only if they agree for f = 1,...,8n+4. There is no program-length or
support-size term in this cutoff. This is not a claim that these widths are
minimal, or that dense tensor matrices can be tested at low cost.

There is a stronger quantitative statement. In one endpoint entry, combine
equal exact native matrices and write the residual as

    A_f = sum_(g in S) c_g g^(tensor f),

where the matrices in S are distinct. Set

    M = sum_g |c_g|^2,
    E_f = D^(-f) ||A_f||_HS^2.

Then

    max_(1 <= f <= 8n+4) E_f >= (14/15) M.                 (1)

The proof gives explicit rational weights b_f such that

    sum_(f=1)^(8n+4) b_f E_f = M.                        (2)

Each E_f can be computed from base-dimension pair traces. It does not require
a tensor matrix. A nonzero E_f gives an exact nonzero tensor entry by a finite
sequence of conditional norm tests. The executable uses Q(i); the theorem
allows arbitrary complex scalar coefficients.

This result changes an infinite algebraic obligation into a finite test for
this native class. It does not supply a native layout, a physical cost bound,
rounding, stock, a recursive supplier, or a change to the complete kappa.

## 1. The exact trace alphabet

Use Hermitian Paulis P_v, labelled by v in F_2^(2n), as an orthogonal basis
of M_D(C). A Clifford U acts by

    U P_v U* = epsilon(v) P_(S v),

where S is symplectic and each epsilon(v) is 1 or -1. On the fixed space
L = ker(S-I), the signs form an additive character. Indeed, multiplication
P_u P_v = gamma(u,v) P_(u+v), followed by conjugation, cancels the same
nonzero gamma on both sides and gives epsilon(u+v)=epsilon(u)epsilon(v).

The trace of conjugation on all matrices is |tr U|^2. The Pauli basis gives
the same trace as sum_(v in L) epsilon(v). A nontrivial sign character sums
to zero; the trivial character sums to |L|. Thus

    |tr U|^2 is zero or 2^d, with 0 <= d <= 2n.           (3)

We also need the phase of this trace. C_n is a finite group. Its conjugation
action on the finite Pauli group has finite image. Its kernel consists of
scalar matrices: commuting with all Z generators forces a diagonal matrix,
and commuting with all X generators makes that diagonal constant. A scalar
in R with absolute value one is in {1,i,-1,-i}. To see this, write it as
(a+bi)/2^k. Unique factorization in Z[i], with 2=-i(1+i)^2, shows that a
Gaussian rational with denominator a power of two and norm one is a unit.
The kernel therefore has four elements.

Every U has finite order. Its eigenvalues are roots of unity, so its trace
is an algebraic integer. The trace is also in Q(i). The ring of integers of
Q(i) is Z[i], so tr U is a Gaussian integer. Factoring its norm in (3) now
shows

    tr U in {0} union {i^k (1+i)^d : 0 <= k < 4,
                                          0 <= d <= 2n}. (4)

The same statement holds for U*V. In particular, no arbitrary rational
unit-circle phase may be admitted. For example (3+4i)I/5 is unitary and
normalizes Paulis, but is outside the dyadic hypothesis.

Finally tr(U*V)=D holds exactly when U=V. All eigenvalues of U*V have absolute
value one. Equality in their sum being the positive real number D forces
every eigenvalue to be one; a unitary matrix with those eigenvalues is I.

## 2. An explicit polynomial that selects the identity

Let z = tr U / D. In addition to zero and the four scalar values 1,i,-1,-i,
every possible z satisfies

    z^4 = (-1)^j 4^(-j),  for some 1 <= j <= 2n.

Define the rational polynomial

    q_n(z) = z(1+z+z^2+z^3)/4
             * product_(j=1)^(2n)
                 (z^4 - (-1)^j 4^(-j))/(1 - (-1)^j 4^(-j)).       (5)

It has zero constant term, degree 8n+4, and q_n(1)=1. It vanishes at every
other value in the trace alphabet. Therefore, for exact matrices U,V in C_n,

    q_n(tr(U*V)/D) = 1 if U=V, and 0 otherwise.            (6)

Write q_n(z)=sum_f b_f z^f. The triangle inequality for polynomial
coefficient norms gives a dimension-independent bound. The first factor
has coefficient norm one. Each odd-j factor has nonnegative coefficients
whose sum is one. The norm of the even factor j=2k is

    (1+16^(-k))/(1-16^(-k)).

For nonnegative a,b with a+b<1,

    [(1+a)/(1-a)] [(1+b)/(1-b)]
        = (1+t)/(1-t), where t=(a+b)/(1+ab) <= a+b.

Induction and sum_(k>=1) 16^(-k)=1/15 show

    sum_f |b_f| <= product_(k=1)^n (1+16^(-k))/(1-16^(-k)) < 8/7. (7)

For n=0 the norm is one and the same strict bound holds. Also sum_f b_f=1.
It follows that the sum of the positive coefficients is less than 15/14.

## 3. The Gram identity and stable separation

The Hilbert-Schmidt inner product is multiplicative under tensor products.
Thus

    E_f = sum_(g,h in S) conjugate(c_g)c_h (tr(g^* h)/D)^f,         (8)

where g* denotes the adjoint, so the trace argument is g* h. Apply (6) to
(8) and sum against b_f. All terms with g != h vanish and the diagonal
terms give M. This proves (2).

Each E_f is a nonnegative real number. Terms with b_f<0 can be removed from
the right side of (2) when taking an upper bound. Hence

    M <= (sum_(b_f>0) b_f) max_f E_f < (15/14) max_f E_f

when M>0. The weaker non-strict form (1) also covers M=0. If the first 8n+4
residual matrices vanish, (2) forces M=0. Every exact coefficient c_g is then
zero, so A_f vanishes at every positive width. The reverse implication is
immediate. Apply this argument to each input/output entry to obtain the full
dirty-register theorem.

This proof uses only pair traces and a rational polynomial. It does not need
an irreducible character table or a census of C_n. Burnside-Brauer supplies
a related classical tensor-generation argument; (5)-(8) give the explicit
native cutoff, quantitative bound and computational certificate used here.

## 4. Extract a tensor entry without a tensor matrix

Suppose E_f>0. For one output coordinate x and input coordinate y in the
first tensor factor, put c'_g=c_g g[x,y]. The remaining tensor operator is
sum_g c'_g g^(tensor (f-1)). Its normalized squared norm is obtained from
the same pair-trace matrix by (8). The sum of these conditional norms over
the D^2 choices of (x,y) is D E_f. At least one choice is positive, and a
maximizing choice is at least E_f/D.

Repeat until no tensor factors remain. The final scalar is exactly the
chosen entry of A_f. It is nonzero and its squared absolute value is at
least E_f/D^f. Start at a width attaining the maximum in (1) to obtain

    |entry|^2 >= (14/15) M D^(-f).                         (9)

The independent witness checker uses a separate signed-word interpreter,
multiplies the base matrices in their literal order, and computes this one
entry as a product of base entries. It does not use traces, the cutoff,
the interpolation polynomial, or the producer's register compiler.

## 5. Cost, input validation and trust

For s distinct residual operators supplied as D-by-D matrices, all pair
traces cost O(s^2 D^2) exact scalar operations. Equal traces can be collected
into at most 8n+5 buckets, including zero. The full norm sequence then costs
O(n^2+s^2) further scalar operations after the pair traces, apart from
coefficient storage. Coefficient bit sizes are not bounded by this count.

The direct entry extractor uses O(f D^2 s^2 log(f+1)) scalar operations in the
worst case, with base matrices and their Gram matrix in memory. The logarithm
accounts for repeated squaring of pair traces. It never allocates
a D^f-by-D^f matrix. Word support can grow exponentially during compilation;
the program compiler is not asserted to be polynomial in instruction count.
The base dimension D itself is exponential in n. No practical full-supplier
speedup is inferred from these bounds.

The frontend checks every supplied matrix for dyadic entries, unitarity and
Pauli normalization on all 2n generators. The last check is sufficient:
the generators generate the Pauli group, and invertible conjugation gives
an injective map of that finite group into itself. Products and adjoints
remain in C_n. Exact matrix keys include global phase. Scalar coefficients
remain outside tensor powers. The checker does not move a scalar phase
from an operator into a coefficient.

The actual source kernel uses precisely the gates in the first section.
Its C formula has eigenvalues 1 and i. Its Hadamard convention is S C S,
so H^2=iI, not I. The retained source bytes and the independent column
formula are checked in verify.py. These checks bind the algebraic grammar;
they do not run a complete native supplier or its physical implementation.

The proof is written mathematics. Python, the compiler, the frozen Gaussian
arithmetic and the native-source transcription remain trusted. The direct
tensor, signed-word and source-column checks test different implications.
They are not an independent human review or a proof-assistant theorem.

## 6. A finite test that misses a real failure

The one-axis source C and S gates generate a group G of 96 exact matrices.
There are at most 24 signed images of an ordered anticommuting Pauli pair,
and at most four scalar lifts of each image. Thus this group is the complete
one-axis dyadic normalizer, not just a proper subgroup used for calibration.
Let one dirty target receive

    y <- y + (1/96) sum_(g in G) g^(tensor f) x.

The source x is unchanged. The average is an orthogonal projector, so its
trace equals its rank. Complete exact enumeration gives rank zero at widths
1 through 7 and rank 15 at width 8. The all-zero input/output tuple has
entry 5/24 at width 8. Thus seven full small-width checks can all accept
a false all-width identity. The registered example and literal witness
checker reproduce this counterexample without building its tensor matrix.

## 7. Scope and credit

The program must have fixed scalar coefficients and a fixed native word as
width changes. This theorem does not cover a different program at each f,
arbitrary continuous phases, nonunitary scaled operators, non-Clifford gates,
positive characteristic, nonlinear leaves or physical aliasing. A caller
with restricted clean inputs needs its own input contract. Rounded equality
is not exact equality. No complete multiplication theorem or kappa changes.

The finite-group algebra viewpoint is prior work. The repository's
projection-recursion-check already uses positive-width Burnside-Brauer
separation, following Jacob Alan Sussman's engine model. The free-word
tensor audit of Cinna Davis's programs and the certificates by zxv and
Krzysztof Wojt retain their separate contributions. Chris R's retained-helper
and passive-query proofs already use finite Clifford alphabets and tensor
Gram separation. For fixed scalar coefficients, this package supplies the
explicit filter and dimension-independent stability constant above. It does
not replace their statements about width-dependent coefficients. The
concurrent PR #5369 targets the smaller
affine-quadratic monomial class with four selected widths. This package does
not claim its result. README.md links these related sources.

Classical provenance: Burnside and Brauer's tensor-generation theorem, as
reviewed by Benjamin Steinberg in
[On the Burnside-Brauer-Steinberg theorem](https://arxiv.org/abs/1409.7632),
the Pauli conjugation basis, Gaussian-integer factorization, polynomial
interpolation and Gram identities. No global mathematical priority is
claimed. The new package provides the explicit dyadic-Clifford trace
filter, stable bound, complete program frontend, compressed failure
certificate and source-bound checks. The exact source and credit map is
in README.md and SOURCES.json.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
