# Fixed-coordinate F4 caller bound

This is a scoped cost bound. It supplies no new kappa or native word.

## Model

Use the 24 real rays in `WITNESS.json`: four coordinate rays, twelve
two-coordinate sign rays, and eight four-coordinate sign rays. Choose the
representative whose first nonzero coordinate is positive. Sort the vectors
in lexicographic order. Their Gram matrix has a four-term coordinate
decomposition. Both factors of term j have support

    A_j = {i : ray i has nonzero coordinate j}.

Let B be any 24 by 24 binary fitting matrix. Its diagonal is one, and
B[i,k]=0 when i differs from k and the real inner product of rays i and k
is nonzero. Entries at orthogonal pairs can be zero or one. B need not be
symmetric. Each coordinate term is a separate query with rank

    rho_j = rank_F2 B[A_j,A_j].

Assume ambient rank h>=7. Put w=h-1 and H(r)=r^t, where
t=1-0.00310045. The declared path caller has p>=1 pairs and a prefix split
0<=a<=p-1. Its optimistic local paid cost is

    48 H(w) + sum_j H(rho_j).

There are p+2 full calls, 48 final targets of rank 1+w(p+2), and 24(p-1)
rank-one thin queries. The two path segments have lengths a and p-1-a.
For each k in 2,...,a+1 and 2,...,p-a, they contribute 48 targets of rank
1+wk and 48 paid idle requests of rank wk. Empty sums are zero.

The net side-circuit cost, after all productive helper credit, is assumed
nonnegative at this t. Set that cost and all other added fees to zero for
the optimistic comparison. The theorem applies only to callers whose
complete bill is no better than this declared bill. It does not establish
that every F4 implementation has this bill.

## Four forced minors

For coordinates 0,1,2,3, use these five-element index sets:

    (9,10,11,14,16), (4,5,6,11,13),
    (1,2,4,12,18), (0,1,5,10,17).

Each set lies in its coordinate support. Every two distinct rays in each
set have nonzero real inner product. The fitting rule therefore forces its
principal binary submatrix to be I5. Thus rho_j>=5 for all four terms,
for every fitting B. This argument does not require an exhaustive search
over B. Since t>0, each separate query costs at least H(5).

## All caller sizes

Define d_w(k)=H(1+wk)-H(wk). The target-minus-paid margin is at most

    M(p,a,w) = 48 H(1+w(p+2)) - (p+2)[48 H(w)+4 H(5)]
               -24(p-1)
               +48 sum_{k=2}^{a+1} d_w(k)
               +48 sum_{k=2}^{p-a} d_w(k).

Since 0<t<1, d_w(k) decreases with k. Moving one term from the longer
segment to the shorter segment cannot decrease the margin. A balanced
split a=floor((p-1)/2) therefore maximizes M over all prefix splits.

The margin decreases with w. For N=p+2, the derivative of
H(1+wN)-N H(w) is

    Nt[(1+wN)^(t-1)-w^(t-1)] < 0.

The derivative of d_w(k) is

    kt[(1+wk)^(t-1)-(wk)^(t-1)] < 0.

It is therefore sufficient to use w=6. Exact outward rational intervals
check all 5,050 splits for 1<=p<=100. A separate histogram calculation
checks the 100 balanced cases. The greatest balanced upper bound occurs
at p=15 and is less than -6.677788560603989040569623266403.

For real p>=100, bound each d_6(k) in the sums by H(13)-H(12). For integer
p, there are p-1 such terms. Extend the resulting upper bound to real p:

    U(p) = 48 H(1+6(p+2)) - (p+2)[48 H(6)+4 H(5)]
           -24(p-1)+48(p-1)[H(13)-H(12)].

The exact interval checks give U(100)<-74.533259289680662016821454843357
and U'(100)<-1.376842160393419293079707531672. Also

    U''(p) = 1728 t(t-1)(1+6(p+2))^(t-2) < 0.

Thus U stays negative for p>=100. Together with the finite checks and the
two monotonicity arguments, this proves M(p,a,w)<0 for every declared
p,a,w. The fixed coordinate model cannot fund saving 0.00310045 under
these invoice assumptions.

## Boundaries of the result

The theorem fixes the four coordinate factors and separate queries. It
does not cover other bases or rectangular decoders, h<=6, a negative net
helper bill, shared query delivery, or a different caller. The numerical
saving is a historical comparison point, not a current selected frontier.
No monotonicity in the saving itself is claimed. The result does not set a
global ceiling on kappa. The universal steps are written mathematics with
finite exact corroboration, not proof-kernel or independent human review.
