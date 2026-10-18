# Rank-one and disjoint-support reductions for P112 extra totals

This is a scoped written theorem about exact finite matrix factorizations and
the inherited support-only copy-rank cost. It is not a proof-assistant
formalization or a theorem about unrestricted physical delivery programs.

The real single-lift obstruction is due to **Mihir Srivastava
(@mihir-s-05), PR845**. Its complex extension is due to **@woklerx, PR998**.
Their proofs are retained in
[the real predecessor](../p112-single-lift/PROOF.md) and
[the complex predecessor](../p112-complex-single-lift/PROOF.md).
The P112 model comes from **DreamingOfClouds, PR717**; the coordinate value
64 belongs to **Joel Pulikkan / GamingPuzzled, PR620** and its predecessors.
The present addition is the support-subadditivity reduction for dependent
extra sources or readers, its quotient-space consequence including extra
readers outside the coordinate column space, and the direct summation of
single-lift bounds when the added readers use disjoint coordinate sets.
These reductions do not claim new priority for rank-nullity, rank
subadditivity, or summing bounds on disjoint groups.

## Exact model and inherited premise

Let `X` be the predecessor's real `112 x 8` matrix, with columns `x_j`,
`XX^T = 2G`, and complex column rank eight. All transposes below are
algebraic transposes: no complex conjugation occurs. Let `l_i` and `v_i`
be its fixed binary labels and dual labels. For complex vectors define

    beta(d,s) = rank_F2 (v_i dot l_u)_(i in supp(d), u in supp(s)).

The rank of an empty matrix is zero. This cost depends only on supports;
it is neither complex matrix rank nor an estimate of physical bit width.
The complex predecessor proves that for every `a in C^8` and
`z in C^112`,

    sum_j beta(x_j, x_j - a_j z) + beta(Xa,z) >= 64.          (1)

In particular, `beta(x_j,x_j)=8` for each of the eight coordinates,
and `sum_j beta(x_j,x_j)=64`.

For an integer `k >= 1`, consider any exact factorization on **all**
matrix entries

    XX^T = XT^T + DZ^T,                                     (2)

where `T` has eight columns `t_j` and `D,Z` have `k` columns `d_h,z_h`.
Every entry of `T,D,Z` may be an arbitrary complex number. The first
eight reader columns `x_j` are retained. Its separate-total cost is

    C(T,D,Z) = sum_j beta(x_j,t_j) + sum_h beta(d_h,z_h).     (3)

Zero readers and zero sources are allowed; no column is required to be
in `col_C(X)` at the outset. Write

    q = rank_C([X D]) - rank_C(X).

Equivalently, `q` is the rank of the added readers in the quotient space
`C^112 / col_C(X)`.

**Theorem.** Every factorization (2) satisfies `C(T,D,Z) >= 64` if at
least one of the following holds:

1. `rank_C(Z) <= 1`;
2. `rank_C(D) <= 1`;
3. `q >= k-1`;
4. `D=XA` and the columns `a_h` of `A` have pairwise disjoint
   coordinate supports `J_h = {j : a_jh != 0}`.

Condition 3 implies condition 1 by exactness; it is useful because it
can be checked from the added readers before finding their source columns.
Condition 4 permits independent extra sources and readers. Its supports
refer to coefficients in the retained coordinate basis, not to the
112-component supports of the reader vectors `Xa_h`.

## Support subadditivity

For arbitrary complex vectors `u_h`, scalars `c_h`, and a fixed source
`s`, support containment and binary matrix rank give

    beta(sum_h c_h u_h, s)
        <= sum_(h: c_h != 0) beta(u_h,s).                   (4)

Indeed, the support of the sum is contained in the union of the supports
of the `u_h` with nonzero coefficient. Restricting a matrix to fewer rows
cannot increase rank. The binary matrix on the union of those row sets
is obtained by selecting rows from their vertical concatenation, whose
rank is at most the sum of their ranks. Repeated rows cause no problem.
The same argument using columns proves

    beta(d, sum_h c_h s_h)
        <= sum_(h: c_h != 0) beta(d,s_h).                   (5)

Multiplication by a nonzero complex scalar does not change support.
These statements concern ranks over `F2`; complex coefficients are used
only to determine supports. They do not require positivity, bounded
coefficients, or the vectors to belong to `col_C(X)`.

## Collapse of rank-one sources

If `rank_C(Z)=0`, all `z_h` vanish. Equation (2) becomes
`X(T^T-X^T)=0`; injectivity of `X` gives `T=X`. The eight retained terms
alone cost 64 and every added term costs zero.

Otherwise `rank_C(Z)=1`, so there are a nonzero vector `z` and scalars
`c_h` with `z_h=c_h z`. Put `d=sum_h c_h d_h`. The identity becomes

    XX^T = XT^T + d z^T.                                   (6)

By (4),

    beta(d,z) <= sum_h beta(d_h,z_h).                       (7)

For `c_h=0` both the original added term and its cost are zero; such
indices are simply omitted from (4).

Reducing each column of (6) modulo `col_C(X)` gives
`[d] z_i=0` for every index `i`. Since `z` is nonzero, this forces
`d in col_C(X)`. Write `d=Xa`, uniquely. Substitution into (6) and
injectivity of `X` give

    T^T = X^T - a z^T,  or equivalently  t_j=x_j-a_j z.

Applying (1) and then (7) proves

    C(T,D,Z) >= sum_j beta(x_j,x_j-a_j z)+beta(Xa,z) >= 64.

This includes `d=0`. Individual `d_h` may lie outside `col_C(X)`;
their quotient components can cancel in the combination `d`. The proof
requires only the combined reader to belong to the coordinate column
space and therefore does not discard that possibility.

## Collapse of rank-one readers

If `rank_C(D)=0`, equation (2) again gives `T=X`, so the cost is 64.
Otherwise choose a nonzero `d` and scalars `c_h` such that `d_h=c_h d`.
Put `z=sum_h c_h z_h`. Equation (6) holds, and (5) gives

    beta(d,z) <= sum_h beta(d_h,z_h).                       (8)

If `z=0`, exactness gives `T=X`; the nonnegative added costs cannot
lower 64. If `z!=0`, the same quotient and injectivity argument used
above gives `d=Xa` and `t_j=x_j-a_j z`. Equation (1) and inequality
(8) prove the required bound. No assumption on the rank of `Z` was
used in this case.

## Quotient rank forces source dependence

Let `pi: C^112 -> C^112 / col_C(X)` be the quotient map. Applying it
to the columns of (2) gives

    (pi D) Z^T = 0.                                        (9)

View `pi D` as a linear map with domain `C^k`. It has rank `q` and
kernel dimension `k-q`. Equation (9) places the image of `Z^T` in
that kernel. Hence, for every exact factorization (2),

    rank_C(Z) = rank_C(Z^T) <= k-q.                         (10)

If `q>=k-1`, inequality (10) yields `rank_C(Z)<=1`, which is the
already proved first case. If `q=k`, all sources are zero. If `k=1`,
the condition `q>=k-1` is automatic and recovers the inherited
nine-term conclusion. The theorem has no `k=0` hypothesis; with no
added terms, injectivity directly gives `T=X` and cost 64.

The numerical lower bound is sharp for the whole stated class: taking
`T=X` and `Z=0` gives cost 64. This does not assert that every individual
quotient-rank stratum attains 64.

## Disjoint coordinate supports separate into single lifts

Suppose `D=XA`, and write `a_h` for column `h` of `A`. Injectivity of
`X` in (2) gives

    T=X-ZA^T,  so  t_j=x_j-sum_h a_jh z_h.                 (11)

Assume the sets `J_h={j:a_jh!=0}` are pairwise disjoint. If `j` belongs
to `J_h`, it belongs to no other such set, and therefore
`t_j=x_j-a_jh z_h`. If `j` lies outside their union `J`, then `t_j=x_j`.
Consequently the exact cost separates as

    C(T,D,Z)
      = 8(8-|J|)
        + sum_h [sum_(j in J_h) beta(x_j,x_j-a_jh z_h)
                 + beta(Xa_h,z_h)].                       (12)

Apply the inherited complex single-lift inequality (1) separately to
each pair `(a_h,z_h)`. Its `8-|J_h|` unaffected coordinate terms each
cost eight, so subtracting them gives

    sum_(j in J_h) beta(x_j,x_j-a_jh z_h)+beta(Xa_h,z_h)
      >= 64-8(8-|J_h|) = 8|J_h|.                          (13)

Since disjointness gives `|J|=sum_h |J_h|`, substituting (13) in (12)
proves `C(T,D,Z)>=64`.

Empty `J_h` cause no exception: then `a_h=0`, `Xa_h=0`, and the
corresponding bracket in (12) is zero, irrespective of `z_h`. Zero
sources also cause no exception, because (1) includes them. There is
no dependence, reality, magnitude, or sign requirement on the nonzero
coefficients or sources. For `k>8`, at most eight of the disjoint sets
can be nonempty; the same argument handles all remaining zero readers.

## Consequence for exactly two added totals

Take `k=2`, allowing zero columns as before. If either added reader
lies outside `col_C(X)`, then `q>=1=k-1`. Consequently the cost is at
least 64. Off-column readers are not forbidden as algebraic
factorizations: they may cancel in the quotient when their sources
are dependent. That cancellation cannot lower the cost, because the
dependent-source collapse does not increase it.

Therefore any exact ten-term factorization (2) with cost **strictly
less than 64** must satisfy all of

    d_1,d_2 in col_C(X),
    rank_C(D)=2,
    rank_C(Z)=2.                                           (14)

This is a necessary condition, not existence of such a factorization.
The first line follows because otherwise condition 3 applies. The
second and third lines follow from conditions 2 and 1, since matrices
with two columns have rank at most two.

There is then a unique `8 x 2` complex matrix `A` with `D=XA`;
injectivity of `X` implies `rank_C(A)=2` and

    T=X-ZA^T,
    XX^T=X(X-ZA^T)^T+(XA)Z^T.                              (15)

Since a strict saving cannot satisfy condition 4, the coordinate
supports of these two columns must also intersect:

    supp(a_1) intersect supp(a_2) != empty.                 (16)

Thus the remaining two-total question can be confined to full-rank
`A` and `Z` in (15), with overlapping coordinate supports for the
columns of `A` and arbitrary complex entries. The overlap in (16)
is a necessary condition, not evidence of a saving: it says that
at least one retained coordinate source is affected by both added
totals. Cost is not invariant under arbitrary mixing of their two
columns: such mixing can change individual supports and beta costs.
Nonzero rescalings and permutations alone preserve cost.

## Scope and remaining obligations

The result does **not** prove a bound for the remaining case (15)
with `rank_C(A)=rank_C(Z)=2` and overlapping column supports of `A`.
For `k>=3`, an off-column reader alone need not give `q>=k-1`; no
such stronger claim follows from (10).
Nor is a general complex-to-real support transfer for multiple totals
claimed. The inherited complex extension is used only through the
single-lift inequality, either after collapse or separately for each
disjoint coordinate group.

The result assumes exact equality on all entries and retention of
the eight coordinate readers. It does not cover masked equality
with free correction terms, arbitrary reader changes, other
geometries, or interacting/nonlinear copy programs. Independent
nonzero rescalings of the retained coordinate readers can be absorbed
into their source columns without changing supports, but arbitrary
mixing cannot.

Before applying this lower bound, preparation, source access, frame
changes, cleanup/restoration, hosting and recursive-child work are
all optimistically granted zero additional cost. Even under that
relaxation, the covered cases cannot lower the separate-total
copy-rank sum. Savings in other cost components or rank distribution
at equal sum are not excluded. The physical interpretation still
inherits **DreamingOfClouds' PR446** separate-total copy-tree
assumptions; no physical compiler, all-size multiplication theorem,
new supplier, kappa, or runtime improvement is supplied here.

The general complex-parameter proof is the written argument above.
Finite exact fixtures can check identities, quotient ranks and the
claimed failure modes; they are not an exhaustive search of complex
parameters and do not replace that proof or the pinned predecessor
premises. Substantial OpenAI Codex assistance was used; delegated AI
review is not independent human review.
