# Binary common-image full-guard family

This is a counting theorem for complete, equally weighted headers. The proof
covers all dimensions below; the executable domains are finite corroboration.
The complements guarded here are corank one. They are not rank-one first-pivot
requests. No physical header producer or paid caller is supplied.

## Statement

Work over F_2. Fix m >= 2 and 1 <= k <= m. Let u be a nonzero column and
v_1,...,v_k independent ordered covectors, with v_i u = 1. Put
U_i = u v_i and P_i = I - U_i. For G uniform in GL_m(F_2), let E_i mean
that every leading principal minor of G P_i G^{-1} of orders 1,...,m-1
is nonzero. Define

    A_j = 0                              if j < k-1,
    A_j = 2^j product_{r=0}^{k-2}(2^j-2^r) otherwise,

where an empty product is one. Then

    Pr(E_1 and ... and E_k)
      = [sum_{j=0}^{m-1} binom(m-1,j) A_j] / [(2^m-1) A_{m-1}].       (1)

The summand indexed by j counts passing orbit tuples with exactly j zero
coordinates of the transformed u among its first m-1 coordinates. Every
orbit tuple has exactly

    2^{(k-1)(m-k)} |GL_{m-k}(F_2)|                              (2)

complete headers above it, with |GL_0|=1.

The new larger-family case is k >= 3. The k=1 marginal is predecessor
PR4227. The k=2 specialization is the transpose-dual of Nick Petalas's
PR4807 common-covector pair law; neither specialization is claimed as new.

## The tuple orbit and constant header fibers

Write V for the k by m matrix with rows v_i and t for the all-ones column
in F_2^k. Conjugation acts as (u,V) -> (G u,V G^{-1}). It preserves

    u != 0, rank(V)=k, V u=t.                                  (3)

Conversely this action is transitive. The columns t,e_2,...,e_k form a
basis of F_2^k. Choose preimages b_2,...,b_k under V of e_2,...,e_k;
take b_1=u; then extend these columns by a basis of ker(V). Their images
are independent, so the resulting m by m matrix B is invertible and

    B^{-1}u=e_1,    V B=[Q 0],    Q=[t e_2 ... e_k].

For a second tuple use B' in the same way. G=B' B^{-1} sends the first
tuple to the second. Thus every tuple satisfying (3) is reached and
uniform complete headers give a uniform distribution on these tuples.
This conclusion does not apply to a restricted or weighted header set.

In these adapted coordinates a stabilizing matrix has block form

    [ I_k   0 ]
    [  T    H ],

where H is any element of GL_{m-k} and the first column of T is zero
because the matrix fixes e_1. Its other (k-1)(m-k) entries are free.
This proves (2) and the equality of every header fiber by orbit-stabilizer.
At k=m the empty blocks give the same formula with fiber one.

For fixed nonzero u, choose coordinates in which u is the last unit
vector. The condition V u=t fixes the final column of V to t. Let B_0
be its other m-1 columns. Choose an invertible row operation taking t
to the first unit vector. The first row of B_0 is arbitrary, while the
remaining k-1 rows must be independent. There are A_{m-1} possibilities.
Consequently the orbit has size D=(2^m-1)A_{m-1}. Equivalently its
constant fiber is |GL_m|/D, agreeing with (2). Over F_2 a common image
line has a unique nonzero vector u, so no scalar gauge has been counted.

## From all proper minors to coordinate support

For a transformed tuple write u'=G u and V'=V G^{-1}. The rank-one
determinant lemma gives, for each proper order l,

    det((I-u'v'_i)_{1:l,1:l})
       = 1 + sum_{a=1}^l u'_a v'_{i,a}.

In F_2 this determinant is nonzero precisely when the partial sum is
zero. Every proper prefix must vanish. Subtract consecutive prefixes
(the first prefix is already a single product) to obtain

    u'_a v'_{i,a}=0    for every a<m and every i.                 (4)

The full pairing v'_i u'=1 is invariant. Combining it with (4) forces

    u'_m=1,    v'_{i,m}=1 for all i.                             (5)

Conversely (4) and (5) make every proper leading minor equal to one.
This proves an equivalence for all proper guards, not a first-pivot proxy.
The normalization and rank assumptions in (3) are essential.

## Counting the passing tuples

Suppose exactly j of u'_1,...,u'_{m-1} are zero. Its last coordinate is
one by (5). At every other proper coordinate, (4) forces the entire
column of V' to zero. At the j zero coordinates of u', that column is
free; the final column is t. The rank condition is therefore precisely
that these j columns, together with t, span F_2^k. Modulo the line of t,
the j columns must span a (k-1)-dimensional quotient.

An invertible row operation taking t to the first unit vector leaves
2^j free choices in the first row and requires a full-row-rank
(k-1) by j matrix below it. Choosing its independent rows in order
gives product_{r=0}^{k-2}(2^j-2^r), and none exist if j<k-1. Hence
there are exactly A_j choices. There are binom(m-1,j) choices of the
zero-coordinate positions in u'. Summing gives the numerator in (1),
and dividing by the full orbit size D proves the theorem.

For k=1 the numerator is 3^{m-1}, recovering the credited marginal

    s_m = 3^{m-1}/[(2^m-1)2^{m-1}].

For k=2, A_j=4^j-2^j and the numerator is 5^{m-1}-3^{m-1}; thus

    J_{m,2}=(5^{m-1}-3^{m-1})/
            [(2^m-1)(2^m-2)2^{m-2}],

the binary PR4807 pair formula after transposition. Transposition
preserves all leading principal determinants, so this is prior coverage.
No all-(m,k) correlation-sign theorem is asserted here.

## Six common-image kernels at m=7

Take u=e_7 and v_i=e_7^T+e_i^T for 1<=i<=6. The covectors are independent
because their first six coordinates are the six different unit rows.
Each v_i u=1, so U_i has rank one and U_i^2=U_i. The six kernels are
distinct and have the same image. For i!=j,

    U_i U_j=U_j,    U_j U_i=U_i,

so they do not commute and are not pairwise orthogonal. All six requests
have corank-one complements. With G=I_7 every proper leading block of
P_i is identity, so all 36 required minors equal one.

For the probability under every uniform complete header, only j=5 and
j=6 contribute. The support counts (including binomial factors) are

    [0,0,0,0,0,1919877120,40317419520].

Thus N=42237296640, D=5120312279040, and

    J_{7,6}=22/2667 > (729/8128)^6 = s_7^6.

For a simple exact inequality, 22/2667>1/128, while 729/8128<1/8,
so s_7^6<1/8^6<1/128. Each individual event still has the same
marginal s_7. Sharing changes the joint distribution, not the single
uniform-GL corank-one full-guard marginal.

This exhibits all six common-image kernels. It does not settle a narrower
reading of PR6515 Q2 involving exactly one coupled pair and four otherwise
orthogonal kernels. Nor does it identify PR4240's rank-one first-pivot
predicate with the complementary full-guard predicate used here.

## Evidence and scope

The primary literally conjugates the complements and checks every proper
minor for every GL_2, GL_3 and GL_4 header. Its 20,334 complete actual
header-code/passing-mask records include orbit coverage and constant-fiber
checks for every k in those dimensions. A separate engine uses column-rank
and zero-support dynamic programming for the 135 frozen (m,k) pairs through
m=16, plus literal quotient-span states at (7,6). After both blind firsts,
its separately written literal-matrix census compares every submitted small
header record as data. These finite checks corroborate, and do not replace,
the all-dimension argument above. There is no GL_7 or predecessor spectrum
run. AI static review is recorded separately from execution and from human
or proof-kernel acceptance.

The direct released request is Nick Petalas's PR6694 README question 3.
The binary prefix criterion and orthogonal-family context are predecessors
PR4275 and PR6515; their orthogonal spectra are not reused or contradicted.
PR4807 explicitly excludes larger families, rather than requesting this law.
Arbitrary nonorthogonal mixtures, odd fields, restricted headers and physical
selection/emission/dispatch/restoration/stock/precision/caller costs remain
outside this theorem. No supplier, recursive invoice, kappa or selected
frontier change follows from a complete-header counting probability.
