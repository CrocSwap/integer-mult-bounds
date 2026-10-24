# The block-three hook has a nonzero error gap

This scoped proof was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## 1. Space and predecessor premise

Let V=C^8 with its standard orthonormal basis indexed by F_2^3. At
digit width five, restrict V^(tensor 5) to the isometrically embedded space

    H = V tensor exterior^4 V.

Exterior basis vectors are normalized antisymmetrizations. Thus H has the
orthonormal basis (x,T), where T is an increasing four-subset of {0,...,7}.
Let N be the coordinate subspace with x in T. Both N and its orthogonal
complement have dimension 280. Write P for the orthogonal projection onto N.
For a single-column matrix g, let rho(g)=g tensor exterior^4(g).

Jacob Alan Sussman's [PR #4628, PROOF sections 1 and 2](https://github.com/CrocSwap/integer-mult-bounds/blob/ee4fd87f064017c23e5a86fc1dcfe0a5237caed3/research/complex-small-m-lower-bounds/PROOF.md)
supplies the hook construction and the paid-call bound

    rank((I-P) rho(C_v) P) <= 80,   v != 0,
    C_v = ((1+i)/2) I + ((1-i)/2) X_v.

That theorem is a cited premise, not a replay target of this package.
Every columnwise monomial map preserves N. Arbitrary linear mixing among
registers, including singular mixing, also preserves the direct sum of their
N spaces. The target on one array is K=C_(e_0) C_(e_1) C_(e_2).

## 2. The new exact spectrum

Define L=(I-P) rho(K)|N. Its squared singular values, with multiplicities, are

    0:56,  1/8:48,  5/8:112,  1:64.                         (1)

Here is an exact finite certificate for (1), generated directly from the
matrix formula. Let h[y,x]=(-1)^popcount(x AND y), so F=h/sqrt(8) is the
normalized eight-point Walsh matrix. Put D_0=diag(1,-i). The two-point
identity C=e^(i*pi/4) D_0 F_2 D_0 gives

    K = e^(3i*pi/4) D F D,    D[x,x]=(-i)^popcount(x).

Both rho(D) factors are diagonal unitary and preserve N and N-perp.
Consequently L has the same singular values as (I-P)rho(F)|N.

In the indicated exterior bases the latter matrix has entries

    h[y,x] det(h[S,T]) / sqrt(32768),
    x in T, y not in S, |T|=|S|=4.                         (2)

Indeed the first tensor factor contributes 1/sqrt(8), and the four-by-four
minor contributes 1/64. Let D_num be the integer numerator in (2).
The verifier constructs all 78,400 entries using the 24-term determinant
formula. Every entry of D_num^t D_num is divisible by 4096. Define

    A = D_num^t D_num / 4096 = 8 L^* L,

where the second equality is up to the harmless diagonal unitary basis
change just described. The verifier checks the exact integer identities

    A(A-I)(A-5I)(A-8I) = 0,
    (tr I, tr A, tr A^2, tr A^3) = (280,1120,6944,46816).   (3)

A is real symmetric. The first identity confines its eigenvalues to
{0,1,5,8}. Their multiplicities solve the four Vandermonde equations
supplied by the traces. The unique solution is (56,48,112,64), proving (1).
This is a computer-assisted finite spectral proof. Floating eigensolvers
and predecessor rank certificates are not used by the verifier.

## 3. From spectrum to approximate completed outputs

Consider any finite linear program with R registers, W designated inputs,
zero initial scratch, and W distinct output registers. It may use arbitrary
complex scalar mixing and columnwise monomial free letters. Each paid letter
is a C_v call. The program can depend on width; only its width-five instance
is needed here. Let M be its joint map from the W data inputs to the W
completed outputs at that width, and suppose it uses s paid calls.

Restrict every data input to N. At an intermediate cut let B be the map
from N^W to the quotient by N in all R registers. Initially rank B=0.
Free steps cannot increase rank B. For a paid letter on register r,
decompose its old content into its N and N-perp components. The image of
the old quotient components has dimension at most rank B. The new leakage
from the N component in register r has dimension at most 80 by section 1.
Subadditivity therefore gives rank B_new <= rank B_old + 80. Projection to
the completed output registers cannot increase rank. Hence

    rank((I-P)^W M|N^W) <= 80s.                             (4)

The intended target leakage is L_W=diag(L,...,L), W copies. Compression
by orthogonal projections and restriction to a subspace do not increase
operator norm. Thus

    ||M - diag(K^(tensor 5),...,K^(tensor 5))||
      >= ||(I-P)^W M|N^W - L_W||.                          (5)

The isometric exterior embedding makes the target restriction rho(K).
For any rank-at-most-k map Q, its kernel meets the space spanned by the
first k+1 right singular vectors of L_W. A unit vector in that intersection
shows ||L_W-Q|| >= sigma_(k+1)(L_W). Truncating the singular expansion
attains equality among unrestricted rank-at-most-k linear maps.

Combining (1), (4) and (5), the squared joint operator error is at least

    1       if             80s <  64W,
    5/8     if   64W <=    80s < 176W,
    1/8     if  176W <=    80s < 224W,
    0       if  224W <=    80s.                            (6)

The endpoints in (6) are inclusive on the left. In particular, error
strictly below 1/sqrt(8) requires s >= ceil(14W/5). Five targets with
thirteen calls have error at least 1/sqrt(8). Fourteen calls merely remove
this rank obstruction; they are not constructed here.

The whole piecewise bound is sharp for the rank relaxation. No optimal
approximate circuit, or attainment within the paid-call game, is asserted.
The theorem uses joint operator error, not a separate error bound for each
input/output block. It concerns exactly linear programs. A nonlinear
rounding process can inject new leakage and needs a separate argument.

## 4. Verification scope and code bounds

The standard-library verifier regenerates (2), checks all entries of (3),
and checks the multiplicity equations. It rejects two explicitly changed
Gram diagonals and four invalid rank-budget inputs. An explicit ordered
list of squared singular values checks the rank/error function for every
rank budget at W=1,...,20, including every endpoint. W=5,s=13 and s=14
are separate obstruction/relaxation controls. These finite controls support
the implementation; section 3 proves the statement for arbitrary W.

All matrix dimensions are fixed at 280. Determinants use 24 permutations,
Gram products use at most 280 terms per entry, and matrix products have at
most 280^3 scalar updates. Functions stay below 60 physical lines. Checks
use explicit exceptions and remain active with Python optimization enabled.
There is no recursion, dynamic code execution or subprocess in the verifier.

Power-of-Ten rule 3 has a Python-runtime deviation: integer arithmetic and
tuples allocate during verification. At most a fixed number of 280-square
matrices is live; the control list has at most 5,600 entries. No size is
read from untrusted input, and the registered process has a 120-second cap.
The workload bounds and normal/optimized replays are the compensating
controls. A fixed-capacity numeric implementation would be needed only if
this certificate were moved to a runtime that prohibits allocation.

The external predecessor theorem is cited at an exact public commit. It
is not imported, vendored, checked by this verifier or represented as a
locally available source-history pin. The retained main-tree prefix README
is provenance for the hook conventions, not a replay dependency. No Lean,
native supplier, compiler, physical precision or multiplication theorem is
verified by this package.
