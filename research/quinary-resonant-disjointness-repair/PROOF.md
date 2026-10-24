# Repeated-root disjointness repair in characteristic five

## Statement and source boundary

Let F be any field of characteristic five. For h=4k with k≥1, let A_h be
indexed by the nonempty proper subsets of [h], with entry1 exactly when
the two subsets are disjoint. This is the same literal source matrix as
Ali Romman's PR4962 and Nick Petalas's PR5173, now in the repeated-root
coefficient characteristic. Put B_h=I−A_h.

Define nonnegative integers c_(h,j),1≤j≤5, by c_(0,1)=1 and all other
initial entries zero. The update replaces each block label j as follows:

    1 → 2;  2 → 1+3;  3 → 2+4;  4 → 3+5;  5 → 5+5.       (1)

Multiplicity is additive, and all c are ordinary integers, not residues.
Let b_h=sum_j c_(h,j).

**Theorem.** For every h=4k≥4,

    rank_F(B_h)=2^h−1−b_h.                              (2)

Exactly this many additive scalar rank-one terms are necessary and
sufficient to repair A_h to the identity. For example h=4 gives c=(2,0,3,0,1)
and rank9; h=8 gives c=(13,0,21,0,36) and rank185.

The theorem covers the entire resonant family h≡0 mod4. Other dimensions,
nonadditive repairs, physical quinary costs and selected κ are not claimed.
The separate even-characteristic-three problem in Discussion5194 is not
part of this work. Its semisimple proof cannot replace the Jordan analysis here.

## 1. The repeated-root tensor

Include the empty and full subsets. The full disjointness matrix is
T_h=K^⊗h, K=[[1,1],[1,0]]. Over F5,

    K=3I+N,   N=[[3,1],[1,2]],   N²=0,   N≠0.

Consequently U=K/3 is similar to the unipotent block J2=I+N2, where N2
has a single1 above its diagonal. Similarity can be exhibited over F5:
with columns (3,1)^T,(1,0)^T, the matrix S has determinant−1 and
S^-1 N S=N2; rescale the second column by3 to obtain S' with
S'^-1 (N/3) S'=N2. Thus U^⊗h is similar to J2^⊗h over every F.

Since U^5=I, at h divisible by4 we have 3^h=1 and

    T_h=U^⊗h,   T_h^5=I,   M_h:=I−T_h satisfies M_h^5=0. (3)

Unlike the characteristic-three cases, the full operator is nonsemisimple.

## 2. Complete finite Jordan rule and induction

For 1≤j≤5 write Jj=I+Nj, Nj the j-by-j upper shift. The nilpotent part
of J2⊗Jj is the explicit 2j-by-2j matrix

    L_j = [[Nj, I+Nj],[0,Nj]].

For each r≥1 its power is

    L_j^r = [[Nj^r, r Nj^(r−1)(I+Nj)],[0,Nj^r]],       (4)

by block multiplication; coefficients are reduced modulo5. In particular
L_j^5=0. Direct reduction of these five explicitly specified matrices gives
ranks of powers r=1,...,5:

| j | ranks | resulting Jordan sizes |
|---|---|---|
|1|1,0,0,0,0|2|
|2|2,1,0,0,0|1,3|
|3|4,2,1,0,0|2,4|
|4|6,4,2,1,0|3,5|
|5|8,6,4,2,0|5,5|

This is a fixed finite algebra certificate: entries are given by (4), and
exact elimination over F5 checks all25 ranks independently of h. A separate
kernel enumeration on the smallest cases and rank-nullity differences
corroborate it. Rank of a matrix over the prime subfield is unchanged under
field extension, so the table holds over every F. The ranks of all powers
of a nilpotent matrix determine its Jordan sizes: the number of blocks of
size at least r is rank(L^(r−1))−rank(L^r). This proves (1), not just a
numerical pattern at a few large dimensions.

Start with the one-dimensional identity J1 at h=0. Tensoring once more
by J2 applies this complete table separately to every Jordan block.
Induction proves that c_(h,j) counts the actual blocks of U^⊗h for every h.
The ordinary-integer dimension invariant sum_j j c_(h,j)=2^h follows from
(1). At h divisible by4, (3) therefore implies

    nullity(M_h)=b_h,   rank(M_h)=2^h−b_h.             (5)

## 3. The endpoint witness

Let e0 be the empty-subset coordinate and P=M_h^4. As M_h^5=0, P M_h=0.
In characteristic five, (I−T)^4=I+T+T²+T³+T⁴. The needed local powers are

    K^0=I, K^1=[[1,1],[1,0]], K²=[[2,1],[1,1]],
    K³=[[3,2],[2,1]], K⁴=[[0,3],[3,2]].

At an interior subset of size r,1≤r≤h−1, the coordinate of P e0 is

    1+2^(h−r)+3^(h−r)2^r = 1+3^r+4^r,

because h is divisible by4. For r≡0,1,2,3 mod4 these are respectively
3,3,1,2 in F5, all nonzero. In particular P e0≠0, and e0 is not in the
image of M_h. This explicit witness is the endpoint fact absent from a
mere eigenvalue or rank count.

## 4. Exact deletion of empty and full subsets

In the order empty, proper nonempty, full, direct disjointness gives

    M_h(x0,z,xF)=(-1^T z−xF, −x0*1+B_h z, −x0+xF).  (6)

If B_h z=0, then M_h(0,z,0)=−(1^T z)e0. Apply P. The nonzero witness
of §3 forces 1^T z=0. As B_h is symmetric, its image is the orthogonal
complement of its kernel for the nondegenerate standard bilinear pairing.
Thus the all-ones vector belongs to its image. Choose w with B_h w=1.
By (6), M_h(1,w,1)=−(1^T w+1)e0. Applying P again gives 1^T w=−1,
so (1,w,1) lies in ker M_h.

Every kernel vector of M_h has xF=x0 by its last coordinate. Those with
x0=0 are exactly (0,z,0) with z in ker B_h, using the established sum-zero
condition. The vector (1,w,1) supplies precisely one additional independent
kernel direction. Therefore

    nullity(M_h)=nullity(B_h)+1,
    rank(M_h)=rank(B_h)+1.

Together with (5) this proves (2) over every characteristic-five field.

## 5. Additive correction cost and limits

If sum_(j=1)^ell u_j v_j^T=I−A_h, rank subadditivity gives
ell≥rank(B_h). Conversely a rank factorization over F writes B_h as the
sum of exactly rank(B_h) nonzero scalar rank-one matrices. This proves the
stated exact algebraic correction count. It supplies no permission to reuse
the binary physical ledger or to treat coefficient preparation/restoration
as free in a physical construction.

The universal result rests on the five finite Jordan rules followed by
induction and the all-h endpoint witness. Literal h4/h8 controls corroborate
source indexing but do not establish its quantifier. No Lean, large census,
physical supplier, full multiplication theorem or selected-frontier change
is part of this package.

## Open next questions and credit

Analyze the nonresonant characteristic-five dimensions with their own
endpoint restriction; this theorem does not claim their rank. Any physical
quinary repair requires an explicit caller and complete preparation,
routing, precision, dirty-return and tape invoice before expansion.

Ali Romman PR4962 supplies the binary tensor/deletion predecessor; Nick
Petalas PR5173 supplies the distinct ternary inverse; mikey1201 PR172 and
icekylinx/#144 retain the source endpoint/compiler lineage. Jordan tensor
classification and rank factorization retain their classical attribution.
Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
This is a written proof with a fixed exact algebra certificate, not human or
formal proof-kernel approval.
