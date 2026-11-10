# One nullity-32 class has Schur rank at least 4

**No new kappa.** The selected frontier stays \(781451/250000000\). This note
proves a rank inequality for one affine class in the partial \(\mathbb F_4\)
census of PR #7006. It does not finish that census, and a capped dynamic
program is not a rank bound.

## The class

The class is the solution space of resolution indices \((0,0,0)\), permutation
index \(0\), and thin gaps \(2\) and \(4\), in the enumerator of
`class_witness.c` (the solver from PR #7006 at
`8889385a5bbe64df6f1378047b35d89e1aea355c`). The witness checks all of the
following.

The \(\mathbb F_2\)-nullity is 32. No row is fixed. The 32 free generators
pair as eight components, component \(r\) touching only row \(r\) of \(Z_g\)
and row \(r\) of \(Z_h\). Each free matrix entry depends on exactly one
generator, the same generator appears in the matching entry of \(Z_h\), and
\(Z_h = Z_g + D\) on every solution, where the rows of \(D\), little-endian,
are `54 a8 01 02 01 02 01 02`. In \(2\times 2\) blocks that matrix is

\[
D = \begin{pmatrix} 0 & I & I & I \\ I & 0 & 0 & 0 \\ I & 0 & 0 & 0 \\ I & 0 & 0 & 0 \end{pmatrix}.
\]

The free columns are \(0,1,4,5\) on rows \(0,1,4,5\) and \(2,3,6,7\) on rows
\(2,3,6,7\). The constants on the complementary columns are the identity blocks
below. An \(\mathbb F_4\) point assigns an arbitrary element of
\(\mathbb F_4 = \mathbb F_2[a]/(a^2+a+1)\) to each generator. Because each
free entry has a private generator, those points are exactly the block family
below, for arbitrary \(2\times 2\) blocks over \(\mathbb F_4\). The same
algebra holds over any field of characteristic 2.

## Block form and Schur complements

Write \(I\) for the \(2\times 2\) identity and let \(P,Q,R,S,T,U,V,W\) be
arbitrary \(2\times 2\) matrices. Column blocks are \(x_0,x_1,x_2,x_3\).

\[
Z = \begin{pmatrix}
P & I & I+Q & 0 \\
I & R & 0 & S \\
I+T & 0 & U & 0 \\
0 & V & 0 & W
\end{pmatrix},
\qquad
Z+D = \begin{pmatrix}
P & 0 & Q & I \\
0 & R & 0 & S \\
T & 0 & U & 0 \\
I & V & 0 & W
\end{pmatrix}.
\]

Row operations clear the identity in row block \(0\), column block \(1\) of
\(Z\). The other rows then have a zero in that column block, so the column
operations that clear the rest of row block \(0\) do not change them. The
remaining \(6\times 6\) matrix is

\[
E_Z = \begin{pmatrix}
I+RP & R(I+Q) & S \\
I+T & U & 0 \\
VP & V(I+Q) & W
\end{pmatrix}.
\]

The same elimination at the identity in row block \(0\), column block \(3\) of
\(Z+D\) leaves

\[
E_D = \begin{pmatrix}
SP & R & SQ \\
T & 0 & U \\
I+WP & V & WQ
\end{pmatrix}.
\]

Both eliminations are invertible, so
\(\operatorname{rank}(Z) = 2 + \operatorname{rank}(E_Z)\) and
\(\operatorname{rank}(Z+D) = 2 + \operatorname{rank}(E_D)\). These are the two
Schur complements. The inequality
\(\operatorname{rank}(E_Z)+\operatorname{rank}(E_D) \ge 4\) is exactly
\(\operatorname{rank}(Z)+\operatorname{rank}(Z+D) \ge 8\).

## Theorem

Over every field of characteristic 2, and for every \(2\times 2\) blocks
\(P,Q,R,S,T,U,V,W\),

\[
\operatorname{rank}(E_Z) + \operatorname{rank}(E_D) \ge 4.
\]

The bound is attained.

Let \(L_0(x_0,x_2) = Tx_0 + Ux_2\) and
\(L_1(x_0,x_2) = (I+T)x_0 + Ux_2\), and write \(p = \operatorname{rank}(L_1)\),
\(q = \operatorname{rank}(L_0)\). Then \(L_1 + L_0\) recovers \(x_0\), so the
kernel of \((x_0,x_2) \mapsto (L_0,L_1)\) is \(\{x_0 = 0,\ Ux_2 = 0\}\). That
map has rank \(2 + \operatorname{rank}(U)\), and therefore
\(p+q \ge 2 + \operatorname{rank}(U)\). Also \(p \le \operatorname{rank}(E_Z)\)
and \(q \le \operatorname{rank}(E_D)\), since \(L_1\) and \(L_0\) are the
middle block rows with \(x_1 = x_3 = 0\). Ranks of a \(2\times 4\) matrix are
at most 2, so \(p+q \ge 2\).

**Case A.** If \(p+q \ge 4\), the Schur sum is at least 4.

**Case B.** Suppose \(p+q = 3\) and \(\operatorname{rank}(U) = 1\). Then
\(\{p,q\} = \{1,2\}\).

*B1, \(q = 2\) and \(p = 1\).* If \(\operatorname{rank}(E_D) \ge 3\), then
\(\operatorname{rank}(E_Z) \ge 1\) finishes the sum. If
\(\operatorname{rank}(E_D) = 2\), its row space equals the row space of
\(d_2 = [T\ 0\ U]\). That block row has a zero in column \(x_1\), so \(R = 0\)
and \(V = 0\). On \(\ker L_0\), one has \(L_1(x_0,x_2) = x_0\). The restriction
is nonzero: otherwise \(\ker L_0 = \{0\} \times \ker U\), of dimension
\(2 - \operatorname{rank}(U) = 1\), while \(\dim\ker L_0 = 4-2 = 2\). Thus some
kernel vector has \(x_0 \ne 0\). Every row of \(E_D\) is a combination of the
rows of \(d_2\), and \(d_2\) vanishes on that kernel vector with \(x_1 = 0\), so
the bottom output \(p_3 = (I+WP)x_0 + WQx_2\) vanishes there. If \(W = 0\),
then \(p_3 = x_0 \ne 0\). Hence \(W \ne 0\).

Now \(z_2 = [I+T\ U\ 0]\) has rank \(p = 1\), so some column supported on
\((x_0,x_2)\) has nonzero middle block. Its bottom block is zero because
\(V = 0\). The column \(x_3 \cdot v\) with \(Wv \ne 0\) is
\((Sv,\ 0,\ Wv)\). These two columns of \(E_Z\) are independent, so
\(\operatorname{rank}(E_Z) \ge 2\).

*B2, \(p = 2\) and \(q = 1\).* If \(\operatorname{rank}(E_Z) \ge 3\), then
\(\operatorname{rank}(E_D) \ge 1\) finishes the sum. If
\(\operatorname{rank}(E_Z) = 2\), its row space equals the row space of
\(z_2 = [I+T\ U\ 0]\). That block row has a zero in column \(x_3\), so
\(S = 0\) and \(W = 0\). The bottom block row of \(E_D\) is then
\([I\ V\ 0]\), which has rank 2.

**Case C.** Suppose \(p+q = 3\) and \(U = 0\). Then
\(\operatorname{rank}(T) + \operatorname{rank}(I+T) = 3\).

*C1, \(\operatorname{rank}(T) = 2\) and \(\operatorname{rank}(I+T) = 1\).*
The block row \(d_2 = [T\ 0\ 0]\) is an invertible pivot on \(x_0\), and its
\(x_2\) block is zero, so clearing \(x_0\) does not change the \(x_1\) or
\(x_2\) blocks of the other rows. Thus
\(\operatorname{rank}(E_D) = 2 + \operatorname{rank}(N_D)\) with
\(N_D = \begin{pmatrix} R & SQ \\ V & WQ \end{pmatrix}\).
If \(\operatorname{rank}(N_D) \ge 1\), then \(\operatorname{rank}(E_D) \ge 3\)
and \(\operatorname{rank}(E_Z) \ge 1\). If \(\operatorname{rank}(N_D) = 0\),
then \(R = V = 0\). In \(E_Z\), take \(v \ne 0\) in \(\ker(I+T)\) and \(w\)
with \((I+T)w \ne 0\). The columns \(x_0\cdot v = (v,0,0)\) and
\(x_0\cdot w = (w,(I+T)w,0)\) are independent, so
\(\operatorname{rank}(E_Z) \ge 2\).

*C2, \(\operatorname{rank}(I+T) = 2\) and \(\operatorname{rank}(T) = 1\).*
Now \(z_2 = [I+T\ 0\ 0]\) is an invertible pivot on \(x_0\), and
\(\operatorname{rank}(E_Z) = 2 + \operatorname{rank}(N_Z)\) with
\(N_Z = \begin{pmatrix} R(I+Q) & S \\ V(I+Q) & W \end{pmatrix}\).
If \(\operatorname{rank}(N_Z) \ge 1\), then \(\operatorname{rank}(E_Z) \ge 3\)
and \(\operatorname{rank}(E_D) \ge 1\). If \(\operatorname{rank}(N_Z) = 0\),
then \(S = W = 0\), so the bottom block row of \(E_D\) is \([I\ V\ 0]\) and
\(\operatorname{rank}(E_D) \ge 2\).

**Case D.** Suppose \(p+q = 2\). Then \(U = 0\) and
\(\operatorname{rank}(T)+\operatorname{rank}(I+T) = 2\).

*D1, \(T = 0\).* Then \(z_2 = [I\ 0\ 0]\), so
\(\operatorname{rank}(E_Z) = 2 + \operatorname{rank}(N_Z)\) with \(N_Z\) as in
C2. The middle block row of \(E_D\) is zero, and the other two block rows form

\[
E_D' = \begin{pmatrix} SP & R & SQ \\ I+WP & V & WQ \end{pmatrix}.
\]

If \(\operatorname{rank}(N_Z) = 0\), then \(S = W = 0\), so \(E_D'\) contains
\(I\) and has rank at least 2. If \(\operatorname{rank}(E_D') = 0\), then
\(R = V = 0\), \(SP = SQ = WQ = 0\) and \(I+WP = 0\). Thus \(WP = I\), so \(W\)
and \(P\) are invertible, \(Q = 0\) and \(S = 0\). Then
\(N_Z = \begin{pmatrix} 0 & 0 \\ 0 & W \end{pmatrix}\) has rank 2. If neither
rank is zero, both are at least 1. Hence
\(\operatorname{rank}(N_Z)+\operatorname{rank}(E_D') \ge 2\).

*D2, \(T = I\).* This is the only invertible \(T\) with
\(\operatorname{rank}(I+T) = 0\). The middle block row of \(E_Z\) vanishes, so
\(\operatorname{rank}(E_Z)\) is the rank of the \(4\times 6\) matrix

\[
E_Z' = \begin{pmatrix} I+RP & R(I+Q) & S \\ VP & V(I+Q) & W \end{pmatrix}
= [CP + E,\ C(I+Q),\ B],
\]

where \(C = \begin{pmatrix} R \\ V \end{pmatrix}\),
\(B = \begin{pmatrix} S \\ W \end{pmatrix}\) and
\(E = \begin{pmatrix} I \\ 0 \end{pmatrix}\). The block row \(d_2 = [I\ 0\ 0]\)
gives \(\operatorname{rank}(E_D) = 2 + \operatorname{rank}(N_D)\) with
\(N_D = [C,\ BQ]\). If \(\operatorname{rank}(E_Z') = 0\), then \(B = 0\),
\(C(I+Q) = 0\) and \(CP = E\), so \(\operatorname{rank}(C) = 2\) and
\(\operatorname{rank}(N_D) = 2\). If \(\operatorname{rank}(N_D) = 0\), then
\(C = 0\) and \(E_Z'\) contains \(E\), of rank 2. Otherwise both ranks are at
least 1.

*D3, \(\operatorname{rank}(T) = \operatorname{rank}(I+T) = 1\).* Then
\(\det(T) = \det(I+T) = 0\). For a \(2\times 2\) matrix in characteristic 2,
\(\det(I+T) = 1 + \operatorname{tr}(T) + \det(T)\), so
\(\operatorname{tr}(T) = 1\). Cayley–Hamilton gives \(T^2 = T\). The
eigenvalues are \(0\) and \(1\), both in the prime field, and both eigenspaces
have dimension 1. Choose one basis of every copy of the coordinate plane so
that \(T\) becomes \(E_{11} = \begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix}\).
Conjugating every block by the same invertible matrix preserves \(I\), \(0\),
the block positions and both Schur ranks, and it runs through every other
tuple of blocks. It is enough to prove the claim for \(T = E_{11}\) and
\(U = 0\).

Here \(I+T = \begin{pmatrix} 0 & 0 \\ 0 & 1 \end{pmatrix}\). If
\(x_0 = (a,c)\), the second output coordinate of the middle block row of
\(E_Z\) equals \(c\), and that scalar row is zero in every other column. The
first output coordinate of that block row is identically zero. Clearing \(c\)
does not change any other entry, so
\(\operatorname{rank}(E_Z) = 1 + \operatorname{rank}(\varphi_Z)\), where
\(\varphi_Z\) is the remaining map on \((a,x_2,x_3)\):

\[
\varphi_Z = a(e_{\mathrm{top}} + CP e_0) + C(I+Q)x_2 + Bx_3,
\qquad e_{\mathrm{top}} = (e_0, 0).
\]

The middle block row of \(E_D\) is \((a, 0)\). The scalar pivot on \(a\) is
zero off that column, so
\(\operatorname{rank}(E_D) = 1 + \operatorname{rank}(\varphi_D)\) with

\[
\varphi_D = c(e_{\mathrm{bot}} + BP e_1) + Cx_1 + BQx_2,
\qquad e_{\mathrm{bot}} = (0, e_1).
\]

If \(\operatorname{rank}(\varphi_Z) = 0\), then \(B = 0\) and
\(R(Pe_0) = e_0\), \(V(Pe_0) = 0\). Hence
\(\varphi_D(c,x_1) = (Rx_1,\ Vx_1 + ce_1)\) hits both \((0,e_1)\) and
\((e_0,0)\), and \(\operatorname{rank}(\varphi_D) \ge 2\). If
\(\operatorname{rank}(\varphi_D) = 0\), then \(C = 0\) and \(W(Pe_1) = e_1\).
Hence \(\varphi_Z(a,x_3) = (ae_0 + Sx_3,\ Wx_3)\) hits both \((e_0,0)\) and
\((SPe_1, e_1)\), and \(\operatorname{rank}(\varphi_Z) \ge 2\). If neither rank
is zero, both are at least 1. Therefore
\(\operatorname{rank}(\varphi_Z)+\operatorname{rank}(\varphi_D) \ge 2\).

These cases cover every pair with \(p+q \ge 2\). The Schur sum is at least 4,
and the two matrix ranks sum to at least 8.

## Sharpness

All eight blocks zero: \(\operatorname{rank}(E_Z) = \operatorname{rank}(E_D) = 2\),
and the matrix ranks are \(4\) and \(4\).

\(P = Q = R = T = I\) and \(S = U = V = W = 0\): \(E_Z = 0\),
\(\operatorname{rank}(E_D) = 4\), and the matrix ranks are \(2\) and \(6\).

\(T = E_{11}\) and every other block zero:
\(\operatorname{rank}(E_Z) = \operatorname{rank}(E_D) = 2\).

All three points belong to the block family. The first two have entries in
\(\mathbb F_2\). A sum of \(4\) is attained, and it is not a matrix rank sum
below 8.

## What the dynamic program sees

On this class the enumerator of PR #7006 returns \(-3\). Each component is one
row of \(Z\) and the matching row of \(Z+D\), so after three components the
partial rank sum is at most 6. Nothing is pruned before the stored frontier
reaches \(2^{20}\). The return value \(-3\) means the frontier filled. It is
not a lower bound, and it does not exhibit a point of Schur rank below 4.
The case analysis covers every point of the family, including the points the
enumerator does not finish.

Exchanging the two thin maps exchanges \(Z\) and \(Z+D\). The Schur sum is the
same. That ordered swap is a different signature of the same matrices; the
witness names only the orientation above. The other nullity-32 masks are not
claimed.
