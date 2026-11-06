# Sharp inverse envelope with a column cap

This proof was produced by Nick Petalas. Apache-2.0.

## Theorem

Fix an integer n>=1, an integer m>=2 and a real number 0<rho<1. Let E range
over all complex n by n matrices satisfying

    sum_j |E_ij| <= rho,     sum_i |E_ij| <= m rho.

There is no prescribed support, symmetry, positivity or sparsity assumption.
Put d_1=0 and d_i=ceil(log_m i) for i>=2. Then the exact maximum is

    max_E ||(I-E)^-1||_1 = F(n,m,rho)
                           = (sum_(i=1)^n rho^d_i)/(1-rho).             (1)

The induced 1-norm is the largest absolute column sum. Every inverse exists.
A nonnegative matrix with one nonzero entry in each row attains the maximum.
The theorem is an abstract conditioning result. It supplies no claim that an
emitted Gaussian matrix has the additional column cap.

## Reduction to nonnegative columns

Set B_ij=|E_ij|. The row bound gives ||B||_infinity<=rho<1, so both Neumann
series converge absolutely. Termwise triangle inequalities give

    |(I-E)^-1| <= (I-B)^-1

entry by entry. Thus it is enough to bound every column
h=(I-B)^-1 e_j. This column is nonnegative and satisfies

    h=e_j+B h.                                                        (2)

Its largest entry is at j. Indeed h_j>=1. If a largest entry M occurred
at i!=j, then (2) would give M<=rho M, impossible for M>0. In particular
the root can be included in every set of k largest coordinates.

Order the coordinates decreasingly as v_1>=...>=v_n>=0, with root j first.
Write S_k=sum_(i=1)^k v_i and S_0=0. For a set A of k largest coordinates,
summing (2) gives

    S_k = 1 + sum_l a_l h_l,   a_l=sum_(i in A) B_il.

The column and row caps imply, respectively,

    0<=a_l<=m rho,     sum_l a_l<=k rho.

For nonnegative decreasing v, these constraints maximize the last weighted
sum by placing m rho on each of the largest floor(k/m) entries and the
remaining mass on the next entry. This elementary transport inequality
follows by moving mass from a smaller coordinate to any larger coordinate
whose cap is not full. Each move weakly increases the objective. Filling
the permitted total mass cannot decrease it.

Consequently, for q=floor(k/m) and r=k-mq,

    S_k <= 1+rho [m S_q+r v_(q+1)]
         = 1+rho [(m-r)S_q+r S_(q+1)].                                (3)

When r=0 the last term is absent. Here q<n, since m>=2 and k<=n, so the
displayed coordinate is defined. No row concentration assumption was made.

## Solving the partial-sum inequalities

Define b_i=rho^d_i/(1-rho), and T_k=sum_(i=1)^k b_i, with T_0=0.
These numbers are positive and nonincreasing. They obey

    b_1=1+rho b_1,
    b_i=rho b_(ceil(i/m))    for i>=2.                                (4)

For the second equality, an index i lies in the shell
m^(d-1)<i<=m^d precisely when ceil(i/m) lies in the preceding shell.
The case 2<=i<=m has parent 1. This proves (4), including exact powers of m.

There are m occurrences of each parent among the first mq indices and r
occurrences of parent q+1 among the remaining r indices. Summing (4) gives

    T_k=1+rho [(m-r)T_q+r T_(q+1)].                                   (5)

For k=1, (2) gives S_1<=1+rho S_1 and hence S_1<=T_1=1/(1-rho).
For every k>1, each partial-sum index on the right side of (3) with a
nonzero coefficient is strictly less than k. If q=0 the only such index
is 1; if q>=1, q<k, and r>0 implies q+1<k because m>=2.
Induction on k, using nonnegative coefficients in (3) and equality (5),
therefore proves S_k<=T_k for all k. Taking k=n bounds every inverse
column by F(n,m,rho). The complex comparison proves the same bound for E.

## Attainment

Use indices 1,...,n and put

    E_(i,ceil(i/m))=rho,    every other entry zero.                    (6)

Each row sums to rho. At most m rows have any particular parent, so each
column sums to at most m rho. The first row is the self-loop E_11=rho.
All other edges go to a smaller index. Equations (4) give

    (I-E)b=e_1.

The row contraction already proves invertibility, so b is exactly the first
inverse column. It sums to F(n,m,rho), establishing attainment and (1).
This construction also attains all the partial-sum inequalities at once.
The self-loop consumes one of the first column's m available row positions;
the first nonroot shell consequently has m-1 vertices.

## Exact critical family and comparison

At n=m^h, h>=0, the shells have sizes 1 and (m-1)m^(d-1) for 1<=d<=h.
Thus (1) becomes

    F(m^h,m,rho) = [1+(m-1)rho sum_(t=0)^(h-1) (m rho)^t]/(1-rho),     (7)

with an empty sum when h=0. In particular the column-cap-one case
rho=1/m has the exact value

    F(m^h,m,1/m)=h+m/(m-1).                                          (8)

At rho=1/2 and m=2, this is h+2. For n=8 the sharp value is 5, versus 9
in the full-support row-only class of PR5255. For n=64 it is 8, versus 65.
The comparison changes the admitted class by adding the column cap. It
does not improve the correct row-only theorem within its original class.

The smallest strict case is n=3,m=2,rho=1/2. The attaining matrix and column
are

    E = [[1/2,0,0], [1/2,0,0], [0,1/2,0]],
    (I-E)^-1 e_1 = (2,1,1/2),      F=7/2.

The row-only star has column (2,1,1) and norm 4, but its first column sum
in E is 3/2. It violates the added column cap of 1. If m>=n the cap is
redundant, and (1) returns [1+(n-1)rho]/(1-rho), as it should.

## Credit and scope

Ali Romman's PR5255 proves the row-only graph-support inverse envelope and
asks whether a column budget can exclude directed concentration. Its
full-support specialization is the comparison in this proof. Cinna Davis
PR4100 supplies the Gaussian conditioning context; James Reed PR4282 supplies
periodic sections. Ali Romman PR5306 treats unequal row budgets, and Nick
Petalas PR5859 treats missing diagonals. Those different restrictions and
their results retain their credit. None is replayed as this contribution.
ToikY PR4209 proves Schur closure when both caps equal the same number below
one. Here the asymmetric column cap m rho may be one or greater.

Neumann comparison, finite transport inequalities and partial-sum induction
are classical tools. No general literature-priority claim is made. The new
result is the exact simultaneous-cap envelope, including its attaining
routing matrix and its critical finite-dimensional logarithmic value.

Arbitrary nonintegral column-to-row ratios, prescribed sparse supports,
unequal row budgets, Gaussian source binding, physical preparation, error
grids, tapes, native operations, compiler, owned erasure, analytic recovery
and the complete supplier invoice remain outside this result. The selected
frontier and its five framework assumptions are unchanged. This is a scoped
proof with finite corroboration, not a complete multiplication theorem.
