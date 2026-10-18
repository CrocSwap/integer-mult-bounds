# Uniform odd-column completions with all nine factors free

This is a quantified theorem in the retained P112 label-pairing model. The
finite premises are checked exactly. The argument over arbitrary complex
parameters and factor changes is written below, not inferred from examples.
The support-classification premise is credited to Arham Tahir's PR1591 and
independently replayed here. The new completion and compensation argument
have a different scope from that single-entry theorem.

## 1. Statement

Use the 120 E8 root lines with norm-two representatives and delete the eight
orthogonal frame lines F. The live set L has 112 elements. The checker uses
doubled integer representatives r_i of squared norm eight, with

    X_ik = (r_i dot f_k)/4,
    X X^T = 2G,
    B_ij = (1 + G_ij) mod 2.

Here X has eight columns, entries 0,+1,-1, and row squared norm four. B is
symmetric of binary rank nine. Its labels span a nondegenerate binary
pairing space Lambda. For complex columns d,t, define

    rho(d,t) = rank_F2 B[supp(d),supp(t)].

Complex coefficients determine supports and are never reduced modulo two.
Every transpose in this proof is ordinary transpose.

Fix v in L, e=e_v, s=X[v,:]^T, and w=Xs-4e. The vector w has exactly the
52 odd neighbors of v as support, with values +2 or -2. In particular,
B[supp(w),{v}]=0. For any lambda in C except zero set

    K_lambda = XX^T + lambda w e^T.                         (1)

Only free entries change: the odd entries of column v are multiplied by
1+lambda, while its diagonal and all other entries stay fixed. Lambda=-1
clears those odd column entries. The completion has rank nine.

**Theorem.** Every exact nine-term factorization K_lambda=DT^T has

    sum rho(D_j,T_j) >= 64,
    sum rho(D_j,T_j)^q >= 8*8^q       for all 0<q<=1.        (2)

Both bounds are sharp for every v and every nonzero complex lambda. If all
nine terms have nonzero projections onto the original eight-coordinate
space on both sides, the sharper bounds are

    sum rho >= 71,
    sum rho^q >= 8*8^q + 7^q.                              (3)

These are also sharp for every allowed parameter. Transposing (1) gives
the corresponding row result. Exactly nine factors and the uniform
52-entry correction are essential scope conditions. Arbitrary amplitudes
on a free column, multiple corrections, more terms, or shared COPY billing
are outside the theorem.

## 2. Finite support classification

For a root/frame label alpha let H_alpha be the binary hyperplane of labels
pairing to zero with alpha. The complete finite check supplies:

1. The canonical P112 geometry agrees, up to explicit root signs/order,
   with the pinned PR845/PR717 geometry, including all binary pairings.
2. For each v and every one of the 511 nonzero label characters h, form
   the integer matrix of X rows with i!=v and h(i)=1. Exactly nine such
   matrices have complex rank seven: the eight frame characters, with
   kernels C e_k, and the character B[:,v], with kernel C s. Every other
   matrix has rank eight. Thus the 57,232 cases comprise 1,008 rank-seven
   and 56,224 rank-eight cases. All nine kernel lines are distinct.
3. The supports of X[:,k] outside v span H_f_k, of dimension eight.
   The support of w spans H_v, also dimension eight. The singleton {v}
   spans one dimension and all live labels span nine.
4. Without deleting v, only the eight frame characters have a nonzero
   kernel; all other 503 character constraints have rank eight.

These premises do not require a Weyl-flat classification. The primary
checker uses fraction-free rational elimination. A separate checker
enumerates frame coordinates directly and uses rank modulo 257, together
with exact integer null vectors in every rank-seven case. A nonzero
modular minor proves the same minor is nonzero over Q and C. The supplied
null vector gives the matching upper bound seven; finite-field rank alone
is never used to assert a complex rank upper bound.

Why this classifies arbitrary complex normals: if the binary support of
Xa+c e is proper, a nonzero binary character annihilates it. Away from v,
the corresponding X rows must annihilate a. For a!=0, premise 2 forces
a to lie in one of the nine displayed complex lines. Two independent
binary annihilators would require two distinct such kernel lines to
contain a, which is impossible. Thus every factor with a!=0 has binary
support dimension at least eight. This argument covers complex isotropic
a as well; it does not assume that a nonzero complex vector has nonzero
Euclidean square.

More precisely, nonzero columns Xa+c e have the following classes:

| Class | Coefficients | Binary support |
|---|---|---|
| Z | a=0, c!=0 | singleton v |
| E_k | a=t e_k, t!=0; arbitrary c if s_k!=0, otherwise c=0 | H_f_k |
| V | a=t s, c=-4t, t!=0 | H_v; the unique line Cw |
| F | all remaining a!=0 cases | all of Lambda |

For E_k, adding the v label preserves the hyperplane exactly when s_k!=0.
For the s direction, the v entry is 4t+c. Since B_vv=1, it must vanish to
stay in H_v. The checks verify these statements through actual supports.

The complete pairing table, checked at all 112 v, is

| Left/right | E_l | V | Z | F |
|---|---:|---:|---:|---:|
| E_k | 8 | 7 if s_k!=0, otherwise 8 | 1 | 8 |
| V | 7 if s_l!=0, otherwise 8 | 8 | 0 | 8 |
| Z | 1 | 0 | 1 | 1 |
| F | 8 | 8 | 1 | 9 |

In particular, a term with both coordinate projections nonzero costs at
least seven, and cost seven requires one factor on the single line Cw.
A pure singleton can pair with w at cost **zero**. This is the important
difference from PR1591's distinct odd-anchor setting; its nonzero
singleton-side lemma cannot be carried over to the same-anchor space.

For unshifted nonzero columns Xa, only E_k and F are possible, by premise
4. Any pair of unshifted columns therefore costs at least eight.

## 3. Forced factor spaces and at most one cost-seven term

Let C=[X,e]. Deleting v leaves X of rank eight, so e is outside col(X)
and C has rank nine. Equation (1) becomes

    K_lambda = C H C^T,
    H = [ I_8   lambda*s ],
        [  0    -4lambda ],
    H^(-1) = [ I_8       s/4          ],
             [  0     -1/(4lambda)    ].                  (4)

The determinant of H is -4lambda, so K_lambda has rank nine. Every
nine-term factorization consequently has D=C M, T=C N with M,N invertible
and MN^T=H. Writing its coefficient columns as (a_j,c_j),(b_j,d_j) gives

    sum a_j b_j^T = I_8,       N^T H^(-1) M = I_9.         (5)

Call a term mixed when both a_j and b_j are nonzero. The first identity
forces at least eight mixed terms. There are thus eight or nine. A full
factor basis can contain at most one column on each fixed one-dimensional
line, including Z and V.

Put k=(s,-4), the coefficient vector of w. Since s^T s=4, (4) gives

    H^(-1) k = (0,1/lambda),
    k^T H^(-1) k = -4/lambda != 0.                        (6)

If V occurs on the left at term i and on the right at a distinct term j,
the corresponding off-diagonal entry of the second identity in (5) is a
nonzero multiple of (6), a contradiction. If they occur at the same
term, its V/V cost is eight. The pairing table now implies that **at most
one mixed term can cost seven**. Every other mixed term costs at least
eight. This uses the actual nonsymmetric completion matrix H, rather than
assuming that the projected nine coefficient columns are dual bases.

With nine mixed terms this proves (3) immediately. With eight mixed terms,
the remaining term has a pure Z side and costs either zero or one. If it
costs one, its whole rank profile dominates

    (1,7,8,8,8,8,8,8,8).                                 (7)

Its COPY sum is at least 64. For 0<q<=1, subadditivity gives
1+7^q >= 8^q, proving (2) for this branch.

## 4. The zero-cost compensation branches

The remaining term can cost zero only if it is V/Z or Z/V. Removing it
from K leaves a matrix of rank exactly eight: it is a sum of eight terms,
and removing one rank-one term from rank nine cannot lower rank below
eight. Its coefficient matrix in the independent basis C is singular.

**Right singleton.** Write the removed term as kappa w e^T, with kappa!=0.
The residual coefficient determinant is

    det(H-kappa*k*e_9^T) = -4(lambda-kappa).

It vanishes only when kappa=lambda, leaving exactly XX^T. The remaining
eight left and right factor spaces must be col(X). Every term therefore
costs at least eight by the unshifted classification. The free term has
not been discarded from the argument; its forced coefficient is what
makes this reduction valid.

**Left singleton.** Write the removed term as kappa e w^T. The residual
coefficient matrix is

    [ I_8       lambda*s      ],
    [ -kappa*s^T  -4lambda+4kappa ],

whose determinant, using s^T s=4, is

    4[kappa*(1+lambda)-lambda].                            (8)

For lambda=-1, (8) is the nonzero constant four, so this branch cannot
occur. Otherwise kappa=lambda/(1+lambda), and the residual factors as

    (X-kappa*e*s^T)(X+lambda*e*s^T)^T = L XX^T R,

where L and R are diagonal, equal to one away from v, with

    L_vv=1/(1+lambda),       R_vv=1+lambda.

Both are nonzero. The eight remaining factor spaces are col(LX) and
col(RX). Multiplication by these diagonal matrices preserves each
column's support. Their term costs are therefore those of unshifted
root-linear columns and are at least eight. This proves (2) in the last
branch, including nonreal lambda with ordinary transpose.

## 5. Attainment and equality profiles

The eight coordinate terms plus lambda w e^T have ranks
(8,8,8,8,8,8,8,8,0), proving sharpness of (2) for every parameter.

To attain (3), choose p with s_p!=0. Starting from D=[X,w], T=[X,lambda e],
replace the two pairs at p and 9 by

    D_p=X_p+w,     T_p=X_p,
    D_9=w,         T_9=lambda e-X_p.

Their outer products have the same sum. The new D_p has full binary span,
T_p is E_p, and D_9/T_9 is V/E_p. All nine pairs are mixed, with ranks
(7,8,8,8,8,8,8,8,8), up to order. The classification proves this for every
nonzero lambda, not merely the shipped fixtures.

The paid-compensation profile (7) is attained at lambda=-1. Let B_0 be
I_8 with column p replaced by s; its determinant is s_p=+1 or -1. Set
A_0=B_0^(-T). Then

    D=[X A_0, e],
    T=[X B_0-e*(B_0^T s)^T, 4e]

is a factorization of K_(-1) with ranks (7,8,8,8,8,8,8,8,1), up to order.
Omitting its final term appears to leave COPY63 but removes four from
the constrained (v,v) entry. The independent integer checker verifies
this at three different v, without using the Gaussian fixture engine.

At q=1 the only equality **rank profiles** are eight eights and a zero,
or seven eights, a seven and a one. For 0<q<1, strict subadditivity in
(7) leaves only eight eights and a zero. This is a statement about rank
multisets, not a classification of all attaining factor bases.

## 6. Relation to a completed supplier budget

The theorem counts every one of the nine separate COPY terms and their
full powers. At unchanged multiplicity, width and normalization, multiplying
these inequalities by the common positive normalization preserves them.
Even granting zero extra preparation, frame changes, helper reservation,
source/target access, restoration, hosting and precision/tape expenses,
this family cannot reduce the COPY component or improve its rank shape.

It does not establish that those ancillary costs vanish, price a complete
physical supplier, or exclude savings in other parts of a network. Changes
to normalization, shared COPY implementations or the surrounding frame path
need their own completed invoice. No selected contraction or kappa follows.
