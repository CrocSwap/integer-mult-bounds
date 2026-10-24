# Repeated native codes through reduced degree 32

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## Result and scope

Use the 112 signed normalizers and the matrix A in the pinned
[coded caller](https://github.com/CrocSwap/integer-mult-bounds/tree/1ec1119972c9aefe42525172d07b332fcff81cb4/research/coded-native-caller).
There is one common binary coordinate e. There are two private blocks of
eight coordinates each. A stage uses its original nine-coordinate map on
the common coordinate and its private block, and fixes the other block.

Let C_s(f) have owner blocks

    C_s(f)[i,j] = A[i,j] (K_s,i^-1 K_s,j)^(tensor f),

and put P_s(f) = (I - C_s(f))/14. The predecessor proves that A = I - 14 P
for an orthogonal rank-eight owner projection P. The signed K are real
orthogonal matrices, so each P_s(f) is an orthogonal projection.

Consider a polynomial in P_0 and P_1 with scalar coefficients that do not
depend on f. Use P_s^2 = P_s to reduce each word. Suppose its nonconstant
part is nonzero and every reduced word has length at most 32.

**Theorem.** The resulting operator B_f has a native owner path with nonzero
coefficient whose binary map moves e. Consequently, for some finite constant
r that depends on B but not on f, an exact scalar/monomial decoder for
Q_f^-1 B_f Q_f needs

    g >= max(0, 2 f - 3 r)

scalar ADDs. Here Q_f is the tensor power of the central one-column
Gaussian. COPY, CLEAR, SCALE, arbitrary monomial address maps, independent
input owners and owned scratch are allowed. The linear schedule must not
depend on the input values.

**Corollary.** The theorem applies to every nonempty reduced product of
C_0(f) and C_1(f) with at most 32 alternating power blocks and with arbitrary
nonzero integer exponents. It also applies to its inverse. Adjacent powers
of the same stage must first be combined. A pair C_s C_s^-1 is the identity
and is not excluded.

This is a source-specific, certificate-assisted theorem. It is not an
all-length result, a statement about three stages, a paid-Gaussian lower
bound, or a lower bound for a new caller with retained correlated inputs.
It does not supply a cheaper native circuit or a new kappa bound.

## 1. A finite witness for all polynomial coefficients

Only this section uses a finite calculation. Work at f = 1, on 112 owner
fields with 2^17 address entries each. Let v be the unit vector at owner 0
and address e. Let E project onto all 112 entries at address e.

For each length n = 1,...,32, there are two alternating projection words,
one for each starting stage. There are 64 words in total. For each such
word w, define

    z_w = (I - E) w(P_0, P_1) v.

The calculation proves that these 64 vectors are linearly independent.
This is stronger than checking a finite list of candidate coefficients.
Every nonzero linear combination of these words moves some component of
v away from address e. The constant word has zero projection under I-E.

Here is the complete small certificate for that large vector calculation.
Let w_n be either alternating word of length n, and let

    t_n = E w_n v,       m_n = <v, w_n v>.

The operator that swaps the two private blocks exchanges P_0 and P_1. It
fixes v and every vector in the image of E. Therefore t_n and m_n do not
depend on the starting stage. The first component of t_n is m_n.

Each P_s is self-adjoint. For words a and b, form the concatenation of
reverse(a) and b, and replace every run of equal stage labels by one label.
Let its length be d(a,b). Then the Gram matrix is

    G[a,b] = m_d(a,b) - <t_length(a), t_length(b)>.

Thus 65 vectors t_0,...,t_64, each with 112 entries, determine all 4,096
Gram entries. The stored moments use the integer operators 56 P_s and the
prime modulus 65,521. Divide moment n by 56^n modulo that prime before
forming G. The denominator is invertible.

The exact certificate is

    det(G) = 52006 mod 65521.

This nonzero residue proves that the rational Gram determinant is nonzero.
It follows that the 64 rational vectors are independent over the rationals,
the reals and the complex numbers. The finite certificate therefore proves
the assertion for every choice of polynomial coefficients in the stated
degree range.

## 2. Two exact implementations

The source supplies a 112-by-8 integer mode matrix U. Its entries are 0,
1 and -1. The source checks prove, entry by entry,

    U^T U = 56 I,       U U^T = 4 (I - A) = 56 P.

The C++ replay first applies each owner's signed K map, then applies
U U^T, then applies each inverse signed K. It uses integer additions and
modular reductions. All intermediate sums fit in signed 32-bit integers:
each mode has 56 nonzero entries, and each residue is at most 65,520.

The separate dense replay does not use U. It constructs 28 P = 2(I-A)
from CODE.json. It reconstructs each native permutation with literal row
dot products and applies the source's sign at the output address. It then
uses the dense owner matrix. After n steps its moment is multiplied by
2^n to match the saved 56 P normalization.

The dense implementation uses binary64 for its matrix products. This is
exact arithmetic in this calculation: the factors are integers, the
coefficients are 0, 1, -1 or 2, and every partial sum has absolute value
below 2^24. Binary64 represents all these products and sums exactly. The
code checks the sum bound before the replay and checks integral outputs
before each modular reduction. It does not use a floating-point rank test.

Both implementations reproduce all 7,280 stored entries. Modular Gaussian
elimination and a separate fraction-free integer Bareiss calculation give
the same determinant residue. These are separate implementations, not an
independent human review or a proof-kernel check.

## 3. From the finite witness to a moving native path

Fix an allowed polynomial B. Expand its owner blocks as finite sums of
signed native maps. A map is a binary linear permutation with a linear
sign character. Group equal maps and add their coefficients. This gives

    B_f[i,j] = sum_M b_M M^(tensor f).

The coefficients b_M do not depend on f. The owner coefficients are used
once; they are not tensor powered. Products of the one-column maps do
tensor correctly.

Section 1 gives (I-E) B_1 v != 0. Therefore at least one owner block with
input owner 0 has a term M_0 with b_M0 != 0 whose binary part sends e to
a vector different from e. This implication does not infer a tensor
identity from a one-column sample. The sample witnesses a nonzero
coefficient in a finite native-map expansion whose all-f tensor meaning
is already fixed by the source.

## 4. Isolate that path at arbitrary tensor width

Put N_M = Q^-1 M Q for one column. If the binary part of M moves e,
the predecessor's four-point formula gives exactly four nonzero entries
in each row and column of N_M. The two binary vectors e and M e are
independent. The signs of M do not remove any of those four entries.

All distinct native maps in the chosen block are nonproportional. In fact,
every native map fixes the zero address with sign +1, so proportional
maps would have proportionality constant 1 and would be equal. Conjugation
by Q preserves this property.

For every competing map M != M_0, there is a linear functional on
one-column matrix entries which vanishes on N_M and is nonzero on N_M0.
The functional needs at most two matrix entries: choose two coordinates
which distinguish their entry ratios, or one entry which is zero in the
competitor and nonzero in N_M0.

Use one separate tensor column for each of these functionals. If there
are r competitors, their tensor product kills every competing term and
leaves a nonzero scalar multiple of

    N_M0^(tensor (f-r)).

It has 4^(f-r) nonzero entries per row when f >= r. Expanding the r
functionals uses at most 2^r restrictions of rows and columns of the full
decoder. A linear scalar/monomial word with g ADDs has row support at
most 2^g, including arbitrary owned workspace. The sum of these
restrictions has row support at most 2^(g+r). Hence

    4^(f-r) <= 2^(g+r),

which gives g >= 2f-3r. For f < r the nonnegative lower bound is enough.
The constant r can be large. No small numerical ADD bound for a specific
repeated caller is claimed.

This contraction argument extends the path-isolation method in
[PR #5408](https://github.com/CrocSwap/integer-mult-bounds/pull/5408) and its
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/256126eeb1607c0bf52996c3d90490f2b786b94a/research/fresh-stage-code-separation/PROOF.md).
Its fresh-stage path uniqueness is not assumed here. The Gram witness
supplies a surviving moving path even when the two stages repeat.

## 5. Arbitrary integer powers

Since C_s = I - 14 P_s and P_s is a projection,

    C_s^a = I + ((-13)^a - 1) P_s

for every integer a. The coefficient of P_s is nonzero whenever a != 0.
Expand a reduced alternating product with m power blocks. Its unique
degree-m word has coefficient equal to the product of those m nonzero
coefficients. Terms which omit a factor have reduced degree less than m.
Thus the nonconstant reduced polynomial is nonzero. If m <= 32, the
theorem applies. Reversal and negation of the exponents prove the claim
for the inverse decoder as well.

## Decision and open boundary

The experiment changed the fresh-stage premise. For these exact source
codes, short reuse does not give the required scalar terminal decoder.
Increasing the degree bound alone is not a new construction direction.

A route outside this result must change a stated premise, for example the
normalizers, the number of stages, the shared coordinate space, the paid
decoder interface, or the requirement to decode arbitrary terminal inputs.
Such a route still needs its actual source, complete cost and target bill,
restoration, compiler, precision and outer calculation. No such bill is
supplied by this obstruction, and the selected kappa remains unchanged.
