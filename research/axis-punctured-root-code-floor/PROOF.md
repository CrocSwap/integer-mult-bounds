# Dense root-code floor with any subset of axes

This scoped proof was produced by Nick Petalas. The coefficient field K has
characteristic other than two. Binary support ranks are always over F2.
Ordinary transpose is used throughout.

## Statement

Let n>=4 and A be any subset of {0,...,n-1}, with k=|A|. Let R have rows

    e_i+e_j, e_i-e_j       for every i<j,
    s_i e_i               for i in A, with s_i nonzero in K.

The fixed integer geometry declares distinct axes orthogonal, an axis
orthogonal to an edge exactly when it is outside that edge, opposite signs
of an edge orthogonal, and two different edges orthogonal exactly when
they are disjoint. Define B to have unit diagonal and ones at precisely
those off-diagonal orthogonal pairs. Its definition does not gain extra
zeros or ones after reduction in K. Thus B is the retained principal
submatrix of the full dense Bn/Cn pairing.

For any finite exact root-code Gram expansion

    R R^T = sum_(j=1)^m (R x_j)(R y_j)^T,

remove terms with a zero factor and charge term j its binary rectangle rank

    c_j = rank_F2 B[supp(R x_j), supp(R y_j)].

Then sum c_j >= n(n-1)+k. Coordinate factors attain equality. Every optimum
has exactly n nonzero terms. In particular, deleting arbitrary axis lines
while keeping all signed edges cannot make the cost smaller than the
number of retained lines.

The cases k=0 and k=n are the previously established full Dn and Bn/Cn
floors. The new result is the intermediate-axis family 0<k<n. Arbitrary
nonzero axis scalings change no support or binary pairing.

## Cited ingredients

The following are used as prior lemmas, rather than re-established results.

1. **Signed-edge tariff.** ywz65's [PR2719](https://github.com/CrocSwap/integer-mult-bounds/pull/2719),
   [retained proof](../dn-unrestricted-root-code-floor/README.md), gives the
   full dense Dn support classification over every such K. If n is even,
   every nonzero pair costs n-1 on the signed-edge submatrix. If n is odd,
   its costs are n when neither factor is an axis, n-1 when exactly one is
   an axis or they are on the same axis, and n-2 for two distinct axes.
2. **Cross-star minor.** ywz65's [PR2582](https://github.com/CrocSwap/integer-mult-bounds/pull/2582),
   [proof](../bc-dense-root-code-floor/PROOF.md), proves that the binary
   rectangle between any two complete axis stars is an invertible n-by-n
   matrix. An axis star consists of its axis and one supported sign on
   each incident edge. The sign choices do not affect the pairing.

DreamingOfClouds's PR2228/PR2277 retain priority for the root-code floor
method and the one-extra coupling argument. PR2719 supplies its all-n
application. Aaron Wang's PR2272/PR2518 and ywz65's PR2536 retain their
root-generator, finite-screen and different fixed-coordinate pairing work.

## Retained axes force additional charged terms

The signed edges span K^n, since 2 is invertible. Consequently exactness is
equivalent to

    X Y^T = sum x_j y_j^T = I_n,

where X and Y have columns x_j and y_j. In particular m>=n. All nonzero
vectors have nonzero root-code factors.

Call a term marked when both x_j restricted to A and y_j restricted to A
are nonzero. Restricting the last identity to its A-by-A block gives

    I_k = sum_(marked j) (x_j|A)(y_j|A)^T.

Rank subadditivity therefore forces at least k marked terms. This is a
rank argument, not merely k separate nonzero diagonal entries; one term
can contribute to several diagonal entries without supplying their rank.

Each marked term costs at least n. Indeed choose a retained axis i with
x_ji nonzero, and a retained axis h with y_jh nonzero. The axis entries
are supported. For every t!=i at least one of x_ji+x_jt and x_ji-x_jt is
nonzero; otherwise 2x_ji=0. The analogous fact holds on the other side.
Thus both supports contain complete axis stars. The cited cross-star
minor is a submatrix of the actual punctured rectangle. Its rank n is
retained because none of its two axes or signed edges was deleted.

Write e for the number of marked terms, so e>=k. Restricting any actual
rectangle to the signed edges also retains the cited Dn lower bound.

## All finite numbers of terms

For even n, every term costs at least n-1 and each marked term costs at
least n. Hence

    sum c_j >= m(n-1)+e >= n(n-1)+k.

If m>n, this inequality is strict.

For odd n, n>=5. Call a term cheap when x_j and y_j are nonzero multiples
of distinct coordinate vectors. The cited Dn tariff implies that an
unmarked noncheap term costs at least n-1, a cheap term costs at least
n-2, and a marked term costs at least n. A cheap term is never marked
unless both of its distinct axes are retained, in which case the marked
bound n applies instead. In the estimates below it is safe to subtract
the count c of all cheap terms, including any marked cheap terms:

    sum c_j >= m(n-1)-c+e.                         (1)

For m=n, Y^T X=I_n follows from XY^T=I_n. Thus y_j^T x_j=1 for every j,
which excludes every cheap term. Equation (1) proves the desired floor.

For m=n+1, the credited one-extra coupling argument bounds c by two.
Here is its application, included to specify every hypothesis. H=Y^T X
is an idempotent of rank n. Therefore I-H=u v^T for nonzero vectors u,v,
with v^T u=1. A cheap index j has H_jj=0, so u_j v_j=1. For distinct
cheap indices j,l, H_jl=-u_j v_l is nonzero. Write the cheap factors as
x_j=alpha_j e_(a_j), y_j=beta_j e_(b_j), with a_j!=b_j. Then H_jl!=0
forces b_j=a_l. Three cheap indices j,l,t would force
a_l=b_j=a_t and a_j=b_l=a_t, hence a_j=a_l=b_j, a contradiction.
Thus (1) gives

    sum c_j >= (n+1)(n-1)-2+k
             = n(n-1)+k+(n-3) > n(n-1)+k.

For m>=n+2 use the universal signed-edge floor n-2 and charge two more
for each marked term:

    sum c_j >= m(n-2)+2e
             >= (n+2)(n-2)+2k
             = n(n-1)+k+(n+k-4) > n(n-1)+k.

The last strict inequality uses n>=5 and k>=0. These three cases exhaust
all finite m, without assuming a bounded coefficient alphabet or m<=n+1.

## Attainment and scope

Take x_j=y_j=e_j, j=0,...,n-1. The support for j contains the two signs
on each of its n-1 incident edges, and its own axis precisely when j is
retained. After removing identical sign rows and columns, its pairing
rectangle is I_(n-1+[j in A]). The exact Gram expansion therefore costs

    sum_j (n-1+[j in A]) = n(n-1)+k.

This proves attainment and, with the strict inequalities above, the
exactly-n-terms statement. It is an algebraic separate-term rank invoice.
Sparse pairings, deleted signed edges, non-root-code factors, different
targets and characteristic two are outside the theorem. No physical
frames, access, dirty restoration, compiler, precision or recursive
supplier budget is supplied. These costs remain unknown, rather than
being set to zero. No new multiplication theorem or kappa follows.
