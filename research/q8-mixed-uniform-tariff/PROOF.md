# Uniform tariff for mixed Q8 diagonal targets

Let R = F2[Q8], with quaternion generators i,j and central z=-1=i^2=j^2.
The group elements 1,i,j,k,z,zi,zj,zk are distinct basis elements of R;
in particular [z] is not the scalar -1=1 of F2. We write [g] for the basis
element belonging to g.

## Model and normalization

There are r finite roles, all with arbitrary independent initial data. A paid
operation on one role multiplies it by [i] or [j]. Free operations are scalar
matrices in GL_r(F2). Every nonidentity target role must finish multiplied by
its designated group element, and every other role must finish unchanged.
There are no clean roles, free address maps, COPY, erasure, or higher-rank paid
calls. The proof permits any number of additional restored dirty roles.

Move each free scalar matrix through its adjacent paid operation by conjugation.
The augmentation R -> F2 sends every paid operation to I. Since the diagonal
endpoint also augments to I, the residual scalar matrix is I. Thus any legal
word ending at that endpoint has a normalized factorization

    T = product_(l=1)^n (I + ([g_l]+1) N_l),
    g_l in {i,j}, N_l=u_l v_l^T, u_l,v_l in F2^r, v_l^T u_l=1.

Conversely every binary rank-one idempotent is a scalar conjugate of a
coordinate projector, so this factor language describes exactly the allowed
free mixing. The proofs below are lower bounds even without the idempotence
restriction; idempotence is needed for the operation model and attainment.

Let the diagonal targets lie in {1,i,j,z}, with multiplicities s_i,s_j,t for
i,j,z respectively. Put s=s_i+s_j and w=s+t. Restored roles are the 1 targets.
All ranks in this proof are over F2; no rank over the group algebra is used.

## 1. Full formal endpoint forces two support ranks

Let X be the r-by-n matrix with columns u_l, and Y the n-by-r matrix with rows
v_l^T. Write U=im X and V=row Y. Expand T-I by nonempty ordered subsets of
factors. A term using indices a_1<...<a_m is

    ([g_a1]+1)...([g_am]+1)
    * u_a1 (v_a1^T u_a2)...(v_a(m-1)^T u_am) v_am^T.

This expression is valid in the noncommutative group algebra: its group-algebra
factors remain in their original order, while all scalar matrix entries are
central. Expanding the group-algebra product into its eight basis coefficients,
each resulting binary coefficient matrix has columns in U and rows in V.
Sums preserve both containments. Equivalently, every coefficient matrix of
T-I has image contained in U and row space contained in V.

At the requested endpoint the coefficients of [i], [j], [z] in T-I are the
disjoint coordinate projectors P_i,P_j,P_z. Their column spaces together span
the w active coordinate axes, as do their row spaces. Therefore

    rank X >= w,                    rank Y >= w.                 (1)

This step uses equality in the FULL formal group algebra. Projection onto a
single group coefficient is not asserted to preserve multiplication.

## 2. The first-order quotient constrains each label sum

There is a ring homomorphism

    R -> A = F2[x,y]/(x^2,xy,yx,y^2),
    [i] -> 1+x, [j] -> 1+y, [z] -> 1.

Indeed (1+x)^2=(1+y)^2=1 and all elements 1+a*x+b*y multiply by adding
the pair (a,b); this is the Q8 abelianization followed by its first-order
augmentation quotient. It is not faithful and deliberately kills [z]+1.
All products of two first-order increments vanish in A, so the normalized
factorization gives

    sum_(g_l=i) N_l=P_i,             sum_(g_l=j) N_l=P_j.          (2)

Let n_i,n_j count the two paid labels; partition X and Y by those labels as
X_i,Y_i and X_j,Y_j, preserving each factor's u/v pairing. Equation (2) is
exactly X_iY_i=P_i and X_jY_j=P_j. Sylvester's rank inequality yields

    rank X_i + rank Y_i <= n_i+s_i,
    rank X_j + rank Y_j <= n_j+s_j.                               (3)

For completeness, rank(X_hY_h) is at least rank Y_h minus dim ker X_h,
which equals rank Y_h-(n_h-rank X_h). This proves (3), including n_h=0.

## 3. Exact count and arbitrary positive label prices

Subadditivity of the two label spans, (1), and (3) give

    2w <= rank X + rank Y
       <= rank X_i+rank X_j+rank Y_i+rank Y_j
       <= n_i+n_j+s.

Hence every legal word has n_i+n_j >= 2t+s. Also (2) and rank(P_h)=s_h
imply n_i>=s_i and n_j>=s_j separately. If an i call costs alpha>0 and a j
call costs beta>0, these three inequalities imply

    alpha*n_i + beta*n_j
      >= alpha*s_i + beta*s_j + min(alpha,beta)*(n_i+n_j-s)
      >= alpha*s_i + beta*s_j + 2t*min(alpha,beta).                (4)

All bounds are attained simultaneously: apply i once to each i target, j once
to each j target, and the cheaper generator twice to each z target. Every call
uses the corresponding coordinate projector. Its square is z, the calls on
distinct coordinates commute, and every identity target is untouched. This
works for every finite r>=w, including no extra role, r=0, and w=0.

Thus the exact paid count is 2t+s and the exact tariff is the right side of
(4). The theorem concerns arbitrary positive real label prices; the verifier's
integer price fixtures merely corroborate selected instances.

## Scope and relation to earlier work

PR #2248 already established the finite three-role minima 5 for two z and one
generator, and 6 for three z targets. PR #2047 already established the
one-z/two-generator value 4 for arbitrary finite role counts. Those numerical
values are not claimed as new. The new statement removes the role and target
multiplicity bounds for the whole {1,i,j,z} family, and gives the exact weighted
tariff. The proof combines full coefficient support with first-order label
sums. PR #1573 supplies a related all-register rank-nullity precedent for the
different D8/UT3 commutator problem; the scalar image-span method also appears
in the retained three-identical-target proof. All are credited in README.md.

This is a written proof about the specified formal operation language, not a
machine-checked proof. A faithful regular representation can realize Q8 as
eight-address permutations, but a selected native supplier would still require
its own charged implementation, hosting, precision, and transfer proof. No
such supplier or new multiplication exponent is claimed here.
