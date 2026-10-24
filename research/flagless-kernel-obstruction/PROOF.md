# A coordinate-kernel obstruction for flagless span-six words

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Model and inherited premises

Use the formal abelian model of unpaidmoon's PR4119, with four scalar
roles, eight nonzero rank-one rational 3-by-3 frames A_j and binary
rank-one idempotents N_j. A paid call is

    D_N([A]) = I + ([A]-1) N.

The endpoint is diag([C_0],...,[C_3]); three specified C_i are invertible.
The fourth role is arbitrarily dirty and may have any diagonal monomial
endpoint. Equality is in the full group algebra of the additive rational
matrix group. No clean allocation or extra free address map is allowed.

The rational frame span has dimension six. We take the following reductions
from PR4119, sections 2, 3 and 5, as cited mathematical premises.

1. Cube-relation rank at most one is already excluded.
2. Otherwise the relation lattice has a saturated cube basis r,s, independent
   modulo two. For fixed independent off-diagonal patterns B,C,
   off(N_j) = (r_j mod 2)B + (s_j mod 2)C.
3. If S indexes noncoordinate projectors and T the coordinate projectors,
   r and s vanish on T. Thus all relations are on S, the generated group
   splits as H_S direct-sum Z^T, and dim_Q span{A_j:j in S}=|S|-2.

We also cite waynenilsen's PR1882 theorem: two invertible rational 3-by-3
data targets need at least six calls, with any finite dirty auxiliary
workspace and arbitrary diagonal monomial auxiliary endpoints. It imposes
no lower-triangularity requirement on the two data targets. The present
proof does not replay or independently establish that theorem.

## New obstruction

Suppose the occurring noncoordinate pool has a nonzero common right-kernel
vector v and a nonzero common left-kernel vector w. Put

    U = supp(v) union supp(w).

If |U|>=2, no such eight-call endpoint exists, provided |S|>=3.
Only existence of these vectors is needed; their kernels need not be
exactly one-dimensional. This hypothesis uses the original coordinates.

First apply the group homomorphism setting every T generator to zero.
Each coordinate factor becomes I. The surviving S word is still diagonal,
with endpoint diag([C_i^S]); the decomposition gives
C_i=C_i^S+C_i^T. Every S factor fixes v on the right and w^T on the left.
Therefore the diagonal endpoint does too. In the full group algebra,

    C_i^S = 0 for every i in U.                         (1)

For example, if v_i=1, the i-th coordinate of Dv=v is [C_i^S]=1.
Distinct rational matrices are distinct formal group elements, so C_i^S=0.
The left-kernel argument is identical. Coordinate calls in the original
word need not preserve either kernel. Removing them uses the group split,
not an invariant-subspace claim about the interleaved full word.

Let s=|S| and t=|T|, so s+t=8 and s>=3. Every C_i^S belongs to the
frame span on S. A basis can be selected from its rank-one paid frames,
so rank subadditivity gives

    rank(C_i^S) <= s-2.                                (2)

Let t_i count coordinate calls with projector E_ii. Project instead onto
Z^T, setting every S generator to zero. The coordinate factors commute
and each contributes to exactly one coordinate, hence

    rank(C_i^T) <= t_i,    sum_i t_i=t.                 (3)

At least one of the three data coordinates lies in U. If at least two do,
(1) and invertibility force t>=6, contradicting s>=3. Thus exactly one data
coordinate lies in U. Call it a. Equations (1) and (3) force t_a>=3.
For the other two data coordinates, (2)-(3) give

    3 <= (s-2)+t_i.

Since t>=3, s<=5. Summing the last two inequalities and reserving the
three calls at a gives

    6 <= 2(s-2)+(t-3) = s+1.

Consequently s=5, t=3, t_a=3, and neither other data coordinate has a
T contribution. Both corresponding C_i^S are invertible. But the S word
then realizes two invertible targets in five calls, with the other two
arbitrarily dirty roles ending diagonally. This contradicts PR1882's
six-call theorem. The obstruction follows.

## Application to the exceptional pools

PR4119 leaves 72 flagless noncoordinate pools with three projectors and
two realized off-diagonal patterns. woklerx's earlier PR1846 already
classifies these into coordinate-permutation/transpose orbits of sizes
24 and 48. Those classification and orbit-size results retain their
credit. The new contribution excludes the 48-pool orbit as a possible
eight-call realization. The finite corroboration retains the original
four coordinate axes throughout.

The 48 newly excluded pools are exactly the disjoint coordinate-permutation
orbits of the following triple and its transpose:

    X = 1100/0000/0000/0000, packed 0x0003,
    Y = 0100/0100/0000/0000, packed 0x0022,
    Z = 0000/1011/1011/0000, packed 0x0dd0.

Row strings list column 0 first; packed bit 4i+j is entry (i,j).
For this triple v=e_2+e_3 and w=e_3. Thus |U|=2. Transpose exchanges
the left and right kernels. Each coordinate-permutation orbit has 24
pools, their intersection is empty, and every pool meets the obstruction.
This is a finite certificate attached to the universal scoped argument.

The remaining 24 pools form the coordinate-permutation orbit of
(0x0003,0x0022,0x0550), the representative in PR4119. Their left and
right kernels have the same single-coordinate support. The new hypothesis
fails there. Their eight-call feasibility, and span five, remain open here.

## Evidence boundary

The executable checks the new coordinate orbits, kernel supports, formal
kernel identities and all finite rank-budget allocations. Its formal-word
checks use independent integer exponents, without reducing address frames
modulo two. They corroborate the fixed-vector argument and do not enumerate
rational frame relations or settle arbitrary endpoint feasibility.

The universal exclusion depends on the cited relation-support reduction
and two-target theorem. Their scientific suites are unrun. This result is
neither independent acceptance of those premises nor a proof-kernel theorem.
Native legality, frames, physical costs, precision/tape, stock, compiler,
recursive supplier admission and the full multiplication theorem are outside
scope. No new kappa or selected-frontier change follows.
