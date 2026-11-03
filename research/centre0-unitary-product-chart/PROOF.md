# Unitary common chart, and the sharp boundary for the fixed output

Prepared by ToikY with substantial OpenAI Codex assistance and separate AI
implementation/static review. Apache-2.0. This is a scoped written algebraic
construction with exact bounded evidence, not human or proof-kernel acceptance.

## Statement and the changed contract

Let G be the literal rational112x112 centre0 matrix defined below, following
Chris R/Clear1nsight PR5101 and Brian/JoyboyBrian PR5130. For every integer
N>=112 put A=G direct-sum I_(N-112), B=G^T direct-sum I_(N-112), and
H_N=C[y]/(y^N+1) in its Euclidean coefficient coordinates. Define

    lambda=937+12sqrt(6097), h=lambda^-1=937-12sqrt(6097),
    r=sqrt(lambda)=sqrt(469)+6sqrt(13)>1.

**Changed-output theorem.** There are algebraic complex-linear unitary S,C
such that, for all x,z in H_N,

    (S A S^-1 x)(S B S^-1 z)=C(xz).                         (1)

Thus ||S||_2=||S^-1||_2=||C||_2=||C^-1||_2=1, independent of N. The
conjugated native endpoints still have norm r and condition number lambda.

**Fixed-output theorem.** If an invertible complex S instead satisfies (1)
with the additional requirement C=S B S^-1, then

    cond_2(S)>=r, ||C||_2=||C^-1||_2=lambda,
    cond_2(C)=lambda^2.                                    (2)

The lower bound on cond_2(S) is attained. These are different output
conventions: the unitary construction does not realize the predecessor's
fixed output for free or contradict (2).

Nick Petalas PR6667 already constructs a common complex chart with fixed
output S B S^-1, supplies the seven-plane weighted-swap basis, and asks for
conditioning/physical realization. PR5130's broader complex-chart question
allows an arbitrary invertible output. The addition here is the source-bound
unitary changed-output construction and the sharp fixed-output conditioning
boundary. Orthogonal normalization, two-involution reduction, product isotopy
and Fourier unitarity are classical; no global literature-priority claim is
made. Gaussian-rational restrictions and all predecessor credit remain.

## Literal matrix and inherited planes

Read the exact pinned R.json and corrected derivation, including its selected
set J and literal F_actual. R has eight rows r_i^T of length112. Put K=R^T/4,
let P_J agree with K on the rows in J and vanish elsewhere, and set U=K-12P_J
with columns u_i. The actual matrix is

    G=I-sum_(i=1..7)u_i r_i^T.                             (3)

The finite check constructs all12544 entries from R/J and compares them to
the frozen literal matrix; no predecessor scientific program is executed.
It checks the exact source identities

    R R^T=56I_8, R U=2I_8, U^T U=(67/2)I_8.

Consequently the seven planes V_i=span(u_i,r_i), i=1,...,7, are mutually
orthogonal, each with Gram matrix [[67/2,2],[2,56]] and determinant1872>0.
Their common orthogonal complement Z has dimension98. G and G^T fix Z
pointwise, and both are involutions. On each (u_i,r_i) plane their matrices
are [[-1,-56],[0,1]] and [[1,0],[-67/2,-1]]. All this plane structure is
inherited from6667 and source data, not a new native or invoice audit.

Let t=-(1+h)/56 and retain the source vectors

    v_i=u_i+t r_i, w_i=h u_i+t r_i.

The inherited action identities are

    Gv_i=w_i, Gw_i=v_i, G^Tv_i=lambda w_i, G^Tw_i=h v_i.    (4)

Since h^2-1874h+1=0, (1+h)^2=1876h. Direct Gram calculation gives

    v_i dot w_i=(67/2)h-(1+h)^2/56=0,
    ||w_i||^2=h||v_i||^2,
    n=||v_i||^2=(234/7)(1+h)>0.                          (5)

Distinct planes remain orthogonal. The vectors are nonzero because their
coordinate determinant t(1-h) is nonzero. Choose a rational orthogonal basis
z_1,...,z_98 of Z, with positive squared norms d_j. The checker supplies one
literal such basis and checks every pairwise inner product and both actual
matrix actions; orthogonality/nonzero norms certify its rank and span.

Normalize each column positively to obtain a real orthogonal matrix Q:

    Q=(v_1/sqrt(n), r w_1/sqrt(n), ...,
       v_7/sqrt(n), r w_7/sqrt(n), z_1/sqrt(d_1), ...).

Here r=1/sqrt(h)>0. The complement normalization may adjoin additional
algebraic square roots. We do NOT retain6667's smaller coefficient-field
claim Q(sqrt6097,zeta_(2N)); our construction allows these explicit positive
radicals, sqrt(N), and the evaluation roots. They form a finite algebraic
extension. No dyadic/Gaussian-rational or cheap-coefficient implementation is
asserted. Padding Q by identity yields Q_N for every N>=112.

## Balanced endpoint matrices and the unitary chart

In these orthonormal coordinates (4)--(5) become, on each pair,

    L=Q_N^T A Q_N=[[0,r],[1/r,0]],
    M=Q_N^T B Q_N=[[0,1/r],[r,0]],                         (6)

with identities on all other coordinates. Let Pi swap each of the seven
active coordinate pairs and fix the complement/padding. Rowwise products
of the two nonzero weights equal1. Hence for every a,b in C^N,

    (L a) .* (M b)=Pi(a .* b).                           (7)

The singular values in each block are r,1/r; therefore both native endpoint
norms equal r and their condition numbers equal r^2=lambda. Identity on
the remaining coordinates changes neither extremum. Unit condition numbers
for the surrounding charts do not make these native endpoints norm one.

Let rho_j=exp((2j+1)pi i/N), and let E_N evaluate polynomials at rho_j.
For coefficient indices k,l, geometric summation gives

    sum_j conjugate(rho_j^k)rho_j^l=N if k=l, and0 otherwise.

Thus E_N^*E_N=NI and F_N=E_N/sqrt(N) is unitary. Evaluation carries the
negacyclic product to coordinatewise multiplication. Put

    S=F_N^* Q_N^T=sqrt(N) E_N^-1 Q_N^T,
    C=F_N^* Pi F_N=E_N^-1 Pi E_N.                        (8)

Both are unitary. In evaluation coordinates conjugation gives L,M and
output Pi. Applying E_N to (1) therefore reduces it to (7), proving (1)
for all complex inputs and every N>=112. The common scalar sqrt(N) in S
cancels from the conjugated endpoints; it is nevertheless essential when
stating the chart's Euclidean norm. The same identity holds for a product
normalized by any common scalar, by output linearity.

For exact finite identity checks a large compositum of square roots is
unnecessary. The balanced unnormalized basis T=(v_i,rw_i,z_j) differs from
Q only by a diagonal matrix that is scalar on each active pair and arbitrary
on the fixed complement. Those scalings commute with L,M and Pi. Thus the
conjugated operators in (6)--(8) can be checked before column normalization;
the exact Gram certificate separately establishes the complex unitarity.
Finite-field product checks are algebraic corroboration, not finite-field
proofs of a positive Euclidean norm.

## Why the fixed output cannot be unitary

We first give the necessary split-product lemma, rather than assuming an
isotopy classification. Suppose invertible L,M,T over C obey

    (La).* (Mb)=T(a.*b) for every a,b.

For output row i, the cross coefficient L_ij M_ik is zero whenever j!=k.
Choose a nonzero entry in that row of M. Every entry of the row of L except
the matching column must vanish. Since the row of L is also nonzero, the
row of M then has the same single supported column. Invertibility forces
these columns to form a common permutation. Thus L=D_a Pi, M=D_b Pi,
T=D_(ab) Pi, with all diagonal weights nonzero.

If T=M, each a_i b_i=b_i implies a_i=1, so L=Pi is an unweighted
permutation, with norm one. In the original problem the split coordinates
are obtained through E_N S; its condition number equals that of S because
E_N is a scalar times a unitary matrix. Consequently

    ||G direct-sum I||_2
       =||(E_N S)^-1 Pi(E_N S)||_2<=cond_2(S).

Equation (6) gives ||G direct-sum I||_2=r, proving the lower bound.

There is a stronger exact output restriction. A^2=I forces Pi^2=I. With
M=D_b Pi, the product LM=Pi D_b Pi is diagonal. It is similar to AB,
whose eigenvalues are lambda seven times, h seven times and1 otherwise.
These positive real values are therefore the multiset of diagonal weights
b_i. A weighted permutation has singular values |b_i|; hence its norm and
inverse norm are both lambda. Conjugation by scaled-unitary E_N preserves
these norms, proving the output assertions in (2), not merely lower bounds.

Finally let D_0 have entries(r,1) on each active pair and1 on the complement.
Take S_fixed=F_N^* D_0^-1 Q_N^T. Then cond_2(S_fixed)=r, and

    D_0^-1 L D_0=Pi,
    D_0^-1 M D_0=diag(h,lambda) Pi

on each pair. Their row products give the latter matrix itself as output,
so the fixed-output identity holds and the chart lower bound is attained.
This also makes the two contracts and their different output operators
explicit. Reusing the old fixed output with the new unitary S would fail.

## Evidence and obligations

The written proof carries the all-N/all-input quantifiers. Finite exact
source-matrix, Gram, action, split-basis-product and negacyclic fixtures and
their actual controls are listed in VALIDATION.md; no float eigensolver or
finite enumeration substitutes for the proof. The source operator is pinned;
the entire native archive, producer, normalizers and paid invoice are not
independently replayed here.

The changed output must be accepted or converted by an actual consumer,
with all coefficient delivery, access, restoration and other costs paid.
Unitary endpoint maps alone do not price an arithmetic implementation, bound
every intermediate rounded operation, erase intrinsic bilinear amplification,
or supply a finite-grid precision contract. Physical native/compiler/tape,
precision/stock/storage, independent targets and complete recursive/outer
admission remain open. All five selected assumptions remain; no new kappa,
frontier change, complete multiplication theorem or human/kernel acceptance
is claimed. Exact credit and open next questions are retained separately.
