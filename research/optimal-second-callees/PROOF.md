# All optimal second callees in the fixed ordinary wrapper

This proof is produced by Nick Petalas. Apache-2.0.

Jerry Chen / CubeJerry's [PR2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950),
Theorem 2 of `research/weighted-wrapper-contract/README.md`, supplies the
optimal agreement value and the attainer Q=P. The new result here is the
complete equality classification and its scalar finite-field count. The
predecessor's optimum, source execution and census are not audited here.

## 1. Exact model and statement

Let V be an n-dimensional vector space over any field F, n>=1. Let P and
Q be invertible F-linear maps V to V. For a callee define

    F_P(H,D) = (P D, P^-1 H).

Execute these six operations in chronological order:

    D -= H; F_P; D += H; F_Q; D = -D; D += H.

Call their endpoint W_(P,Q), and let J(H,D)=(D,H). All inputs are arbitrary.
There is no restriction to a convenient subspace of the two input banks.
Put

    E = W_(P,Q) - J,     A = P^2-I,     R = Q-P,     s = rank A.

Choose any inner inverse G of A, meaning A G A=A. Such a G exists over every
field, including when A is singular. The choice need not commute with A or P.

**Theorem.** Q attains the minimum possible error rank s if and only if

    im R is contained in im A,
    ker A is contained in ker R,
    R G R = 0.                                             (1)

The last condition is independent of the choice of G when the first two
hold. Over a finite field F_q, this is exactly the condition for Q to attain
PR2950's maximum q^(2n-s) correct input pairs. Q must still be invertible;
conditions (1) by themselves do not imply that requirement.

Equivalently, let K=ker A and U=V/K. The map A induces an isomorphism
Abar: U to im A. Under the first two conditions, R induces Rbar: U to im A.
The endomorphism S=Abar^-1 Rbar of U must satisfy S^2=0. Thus all optimal
second maps have the complete parameterization

    Q = P + Abar S pi,    S in End(U), S^2=0, Q invertible,  (2)

where pi: V to U is the quotient map. This describes an attaining set, not
an implementation of any of its elements.

## 2. Reduce the literal error to one block matrix

Set x=D-H. Direct execution of the six operations gives

    H' = Q P^-1 H + Q P x,
    D' = H' - Q^-1 P x.

If e1=H'-D and e2=D'-H, then

    e1 = R(P^-1 H+P x) + A x,
    Q(e2-e1) = R x.

Both changes of coordinates

    (H,D) to (x,y), y=P^-1 H+P x,
    (e1,e2) to (e1,Q(e2-e1))

are invertible. Therefore E has the same rank as

    M = [ A R ]
        [ R 0 ].                                           (3)

This calculation preserves the order of noncommuting P,Q. It uses no
symmetry, diagonalizability or characteristic assumption. The A submatrix
shows rank M>=s; R=0 attains s. This short observation records the already
credited optimum while preparing its new equality case.

## 3. Characterize equality

If rank M=s, adjoining R to A horizontally or vertically cannot increase
rank. These are exactly the image and kernel containments in (1).

Choose invertible L,T with L A T=D_s=diag(I_s,0). Apply L to both block
rows and T to both block columns in (3). Write B=L R T. The two
containments say exactly

    B = [ B0 0 ]
        [ 0  0 ],

where B0 is s by s. After deleting the zero rows and columns, the block
matrix becomes

    [ I_s B0 ]
    [ B0  0  ].

Subtract B0 times the first block row from the second, then eliminate the
upper-right block by a block-column operation. This gives diagonal blocks
I_s and -B0^2. Hence

    rank M = s + rank(B0^2)                                (4)

under the two containments. In particular equality holds exactly when B0^2=0.

For any G satisfying A G A=A, put G'=T^-1 G L^-1. Its leading s by s block
is I_s because D_s G' D_s=D_s. Consequently

    L R G R T = B G' B = diag(B0^2,0).

This proves (1), its independence of G and both directions of the theorem.
For (2), the identity pi G Abar=I_U follows from A G A=A and injectivity
of Abar. Thus R G R=Abar S^2 pi. Surjectivity of pi and injectivity of
Abar give the stated square-zero equivalence. If F=F_q, rank-nullity on
the 2n-dimensional input space counts the agreements as q^(2n-rank E).

The case A=0 is included. Its image containment forces R=0, so an
involutory first map has a unique optimal second map, namely P itself.

## 4. Count every optimal second map for a scalar first map

**Corollary.** Let F=F_q and P=lambda I, with lambda nonzero and
lambda^2 different from 1. Every optimal second map is uniquely

    Q = lambda I + R,    R^2=0.

There are exactly

    sum_(r=0)^floor(n/2) [n choose r]_q [n-r choose r]_q |GL_r(F_q)|   (5)

such second maps. The summand is the exact count with rank(Q-P)=r.
Here [a choose b]_q counts b-dimensional subspaces of F_q^a and
|GL_0(F_q)|=1. Every one agrees with interchange on q^n input pairs.

*Proof.* A=(lambda^2-1)I is invertible, so the first two conditions in
(1) are automatic and the third is R^2=0. Such a Q is invertible with
inverse lambda^-1 I-lambda^-2 R. For square-zero R of rank r, choose
its image I of dimension r and its kernel K of dimension n-r, with
I contained in K. Then choose the isomorphism V/K to I induced by R.
Conversely each such choice gives exactly one R. The numbers of choices
are [n choose r]_q, [n-r choose n-2r]_q=[n-r choose r]_q and |GL_r|.
The inclusion forces r<=floor(n/2), proving (5). Rank A=n gives the
agreement count. This flag-counting argument is standard linear algebra;
its application to all optimal wrapper callees is the scoped new consequence.

At n=2, (5) is 1+(q+1)(q-1)=q^2. In particular P=2I over F5 has
exactly 25 optimal second maps, although PR2950 gives P as one attainer.
One different attainer is Q=[[2,1],[0,2]]. It agrees on 25 of 625 input
pairs, the same maximum as Q=P. None of these calls fixes the failed
wrapper on every input. No claim of exact interchange follows from optimal
agreement.

Invertibility in (2) cannot be dropped for a nonscalar P. Over F5 take

    P = [2 0],   A = 3I,   R = [4 1],   Q = [1 1].
        [0 3]                  [4 1]       [4 4]

All three conditions (1) hold, but Q is singular. This is an excluded
parameter, since F_Q is undefined. Finite tests explicitly retain this control.

## 5. Limits

The theorem is a written all-dimension, all-field linear algebra proof.
The verifier corroborates declared finite prime-field domains; it is not
a proof-kernel formalization. General finite abelian groups and nonlinear
callees are outside the equality classification. Callees are exact endpoint
oracles. Their implementation, normalization, frames, restoration, hosting,
precision, tape costs and supplier admission remain unproved here. The
selected conditional frontier and the multiplication theorem are unaffected.
