# Compensation rank closes the two-product branch

This is a scoped, computer-assisted algebraic proof. Its finite premises are
recomputed by two exact implementations; the quantified argument below is
written mathematics, not a proof-assistant formalization.

## Statement and model

Use PR717/PR845's P112 geometry, with its eight deleted orthogonal frame lines,
112 live root lines, coordinate matrix X, and symmetric binary matrix

    XX^T = 2G,  X^T X = 56I,  B_ij = (1 + G_ij) mod 2.

Fix x = X[:,4] and y = X[:,6], using zero-based coordinate indices. For complex
column vectors a,b define the separate-total COPY charge

    beta(a,b) = rank_F2 B[supp(a), supp(b)].

Let u,v be nonzero complex vectors with U=supp(u), V=supp(v), and B[U,V]=0.
Thus uv^T is a free rectangular correction in this model: it vanishes on
every constrained entry and beta(u,v)=0. For any M in GL(3,C), set

    D = [x,y,u] M,     S = [x,y,v] M^(-T).

Transpose is ordinary, not conjugate. The other six coordinate terms stay
unchanged. Then DS^T = xx^T + yy^T + uv^T, so this is a valid masked identity.

**Theorem.** If r_j = beta(D[:,j],S[:,j]), then

    r_1+r_2+r_3 >= 16,
    r_1^t+r_2^t+r_3^t >= 2*8^t     for every real 0<t<=1.

Consequently the complete eight-coordinate decoder has COPY sum at least 64
and separate COPY power bill at least 8*8^t. These bounds are attained at
M=I. There is no support-size restriction on the nonzero free rectangle.

The new result is the **exactly-two projected-product branch**. Cinna Davis's
PR1373 proves the three-product branch for this same pair. We credit that
argument and independently replay its finite premise to obtain the stated
full-GL3 corollary without assuming a pending certificate's correctness.

## Exhaustive finite premises

For a nonzero normal a in C^2, write C(a)=supp(a_1*x+a_2*y). Since X has entries
0,+1,-1, the following five representatives exhaust every possible support:

    (1,0), (0,1), (1,1), (1,-1), (1,2).

Indeed a cancellation with both coefficients and both row entries nonzero
requires a_2/a_1=+1 or -1. Every other nonzero complex ratio has the same
support as (1,2). No coefficient sampling is used in this reduction.

The certificate establishes:

1. The row space L of B has dimension nine, and its 112 rows are distinct and
   nonzero. Also X^T X=56I and all 12,544 entries satisfy the displayed identities.
   Each of the eight individual coordinate terms has COPY rank eight.
2. For the five C(a), the row-span dimensions are (8,8,9,9,9). The minimum
   positive weights of binary linear functionals restricted to those row
   sets are (24,24,12,12,24), respectively.
3. For all 25 ordered normal-support pairs, rank B[C(a),C(b)]>=8.
4. Put E(a,j)={i in C(a): B_ij=1}. For all five-by-five support pairs and all
   112 ports j, rank B[E(a,j),C(b)]>=7: 2,800 ranks in total.
5. For all support pairs and all 5,824 ordered pairs (i,j) with B_ij=0,
   rank B[E(a,j),E(b,i)] >= 4+nnz(a)+nnz(b)>=6. This is PR1373's credited
   premise, replayed across all 145,600 records, including its exact minima.

For item 2, the primary checker enumerates every nonzero word in the
nine-dimensional row space of B. Because B is symmetric, these are precisely
the values of all nonzero linear functionals on L, evaluated on its spanning
list of rows. The independent checker instead enumerates all 511 nine-bit
functionals on the source's dual labels. Both obtain identical histograms.
Zero restrictions on an eight-dimensional support are excluded only when
taking the *positive* minimum.

Deleting at most three rows from any C(a) preserves its entire row span.
Otherwise some linear functional would vanish on the remaining rows but not
on the original span, giving a positive restricted weight at most three,
contrary to item 2. This also preserves every further column restriction of
that row span. The independent checker exhibits actual span loss at each of
the five stated erasure distances, so the distance calculation has a boundary
control as well as a lower-bound check.

## Why only two branches exist

Let q_j and p_j be the first two entries of columns j of M and M^(-T).
The top-left block of M(M^(-T))^T=I gives

    sum_j q_j p_j^T = I_2.

At least two of these outer products are nonzero. Thus there are exactly two
or exactly three. Over C, a zero outer product means q_j=0 or p_j=0.

In the two-product case, permute the three terms so that the zero product is
third. If necessary transpose the entire factorization, exchanging u and v
and replacing M by M^(-T), so that q_3=0. Symmetry of B preserves every charge.
Invertibility now gives the block form

           [ C   0 ]
    M  =   [ d^T e ],      C in GL(2,C), e != 0.

With F=[x,y], put f_j=(FC)[:,j], g_j=(FC^(-T))[:,j], and w=FC^(-T)d. The three
terms, ignoring reciprocal nonzero column scalings, are

    (f_1+d_1*u) g_1^T,
    (f_2+d_2*u) g_2^T,
    u (v-w)^T.

Each f_j and g_j is a nonzero two-coordinate normal. The last term is the
compensation term and must be included in the bill.

## Compensation rank controls support size

Suppose d!=0. Since F has column rank two, w!=0; put W=supp(w). On columns outside V,
v-w=-w; on columns inside V, every row indexed by U is zero in B. Therefore

    r_3 = rank B[U,supp(v-w)] = rank B[U,W].                    (1)

This is equality of column spans after ignoring zero columns, not an
assumption that supp(v-w)=supp(w).

Let L_U be the span of the rows of B indexed by U, as a subspace of L. The
coordinate-restriction map pi:L -> F2^W has rank at least eight by
item 2 and symmetry of B, so its kernel has dimension at most one. Equation
(1) says dim pi(L_U)=r_3. Rank-nullity gives

    dim L_U <= r_3+1,     |U| <= 2^(r_3+1)-1.                 (2)

The second inequality uses the distinct, nonzero row property. In particular,
if r_3<=1, then |U|<=3. Removing U from C(f_j) therefore preserves its full
row span. Outside U, f_j+d_j*u=f_j, so monotonicity of rank and item 3 imply
r_1,r_2>=8. This proves both desired bills in this case.

If r_3>=2, choose any port k in the nonempty V. Every row in U has B_ik=0,
so E(f_j,k) lies outside U and survives in supp(f_j+d_j*u). The right factor
is g_j without a rectangle correction. Item 4 gives r_1,r_2>=7. Thus the
rank vector dominates (7,7,2) componentwise, proving the sum bound.

If d=0 instead, both original mixed terms are unchanged, item 3 gives
r_1,r_2>=8, and the third term is the free correction with rank zero. This
completes every two-product case, including the transposed branch.

## The power bill

For 0<t<=1, z -> z^t is increasing and concave on nonnegative reals. The
identity

    (7,7,2) = (3/4)(8,8,0) + (1/8)(8,0,8) + (1/8)(0,8,8)

and coordinatewise concavity imply 2*7^t+2^t >= 2*8^t. This completes the
two-product power bound; the r_3<=1 and d=0 cases already have two ranks >=8.
The same assertion is false at t=2, as the checked control 102<128 shows.

For three active products, choose any i in U and j in V. The uncorrected
left and right normals survive on E(q_k,j) and E(p_k,i), respectively, since
these sets are outside U and V. Item 5 gives all three ranks at least six,
as in PR1373. Hence

    (3*6^t)/(2*8^t) = (3/2)(3/4)^t >= 9/8 > 1.

The total rank sum is at least 18 in that branch. Adding the six unchanged
rank-eight terms establishes the full theorem. At fixed width m, common
multiplicity and normalization, multiplication by m^(-t) preserves the power
comparison. Taking t=1-a yields the separate COPY moment screen for 0<=a<1.

## Sharpness, failure controls, and limits

At M=I the replacement ranks are (8,8,0), attaining the full cost 64 and
the full power baseline. The singleton free rectangle in the certificate
also gives a rank-nine masked completion: each singleton vector e_i is
outside col(X), since X^T X=56I and the squared norm of row i is four, so the
projection of e_i onto col(X) has i-th entry 4/56 != 1. Both [X,e_i] and
[X,e_j] have rank nine, and their product has rank nine.

The literal cancellation fixture uses u=-x on the zero-pairing neighbors of
canonical port 46, v=e_46, C=I, d=(1,0), e=1. The ranks are (7,8,7). Omitting
the compensation term falsely reports 48+7+8=63; its complete bill is 70.
Deleting the term also fails the full matrix identity. Other controls check
nonfree and zero rectangles, singular factor changes, ordinary versus
conjugate transpose, and the required power range.

All helper preparation, source access, factor mixing, frame changes, copies
other than these charged terms, restoration, hosting and child management
were optimistically assigned zero *additional* cost for this rejection
screen. A nonnegative added expense cannot improve this fixed separate-COPY
comparison. This does not bound a whole supplier with changed widths,
normalization, sharing rules or compensating savings elsewhere.

The result covers this pair (4,6), nonzero rank-one free corrections, and
three-term invertible mixing, with six coordinate terms fixed. It does not
cover other coordinate pairs, three or more mixed coordinates, multiple free
rectangles, arbitrary nine-term factorizations, other punctures, shared-copy
accounting or zero-factor boundary families. No physical supplier, new kappa,
full compiler/hosting/precision/analytic result or formal multiplication
theorem follows. The algebraic objective is explicit; its physical
interpretation retains the separate-total, drop-free copy-tree assumptions.
