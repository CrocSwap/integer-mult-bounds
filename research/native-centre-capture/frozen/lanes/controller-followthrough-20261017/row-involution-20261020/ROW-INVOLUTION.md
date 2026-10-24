# A rank-sixteen involution from sixteen row replacements

This packet constructs an exact dyadic involution on the 112 actual data
ports. It changes only sixteen rows of the pinned response. It also gives
its transpose, scalar programs, and the sixteen final query rows. It does
not claim a complete supplier or a terminal decoder.

## General row completion

Work over a commutative ring in which 2 is a unit. Let

\[
E=I+UV,\qquad U\in R^{n\times r},\quad V\in R^{r\times n}.
\]

Select \(r\) rows \(P\), and let \(R\) also denote the complementary index
set when it occurs as a subscript. Assume the square minor \(V_P\) has an
inverse over the ring. Keep \(U_R\), and set

\[
\widetilde U_P=V_P^{-1}(-2I-V_RU_R),\qquad
A=I+\widetilde U V.
\]

Then \(V\widetilde U=-2I\). Thus

\[
A^2
=I+\widetilde U(2I+V\widetilde U)V
=I.
\]

All rows outside \(P\) still equal the corresponding rows of \(E\).
The change has rank \(r\) over any field of characteristic other than
2. Indeed, \(V\widetilde U=-2I\) makes both factors full rank. The
determinant identity gives \(\det A=(-1)^r\). The space
\(\operatorname{im}\widetilde U\) is the \(-1\) eigenspace, and
\(\ker V\) is the \(+1\) eigenspace.

More generally, replace \(-2I\) by \(K-I\), for an arbitrary \(r\)-square
matrix \(K\). This gives

\[
V A=K V,\qquad \det A=\det K.
\]

If \(K\) is a unit, then

\[
A^{-1}=I-\widetilde U K^{-1}V.
\]

The construction is unique within the stated factor family: \(V\), the
rows \(U_R\), and the desired matrix \(V\widetilde U\) determine
\(\widetilde U_P\). This is not a uniqueness claim for all possible row
completions.

## Actual signed blocks

The pinned native response has eight signed blocks of size six and
eight blocks of size eight. In the pair chart, each block is

\[
E_k=I-dd^{T},\qquad d_i\in\{1,-1\}.
\]

Choose one pivot \(p\) with \(d_p=1\). The completion is

\[
A_k=I+\bigl((k-2)e_p-d\bigr)d^{T}.
\]

Since \(d^{T}((k-2)e_p-d)=-2\), this is an involution. In pivot and
complement order it is

\[
A_k=
\begin{pmatrix}
k-2 &(k-3)d_R^{T}\\
-d_R&I-d_Rd_R^{T}
\end{pmatrix}.
\]

All nonpivot rows are unchanged. In \(A_k^T\), all nonpivot columns are
unchanged. Its nonpivot row support is the old support. Only its pivot
column coefficients change: multiply the old coefficients by
\(-(k-3)\), which is \(-3\) or \(-5\). The sixteen pivot diagonal
entries are the only nonzero diagonal entries.

The actual pivot order is

```text
0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23.
```

The first eight ports form four complete physical pair blocks. Thus
the pair matrix \(H\) preserves the pivot set and its complement.
On the large component \(H^T H=2I\); on the small component \(H=I\).
These components do not mix. Consequently

\[
(H^{-1}A_{\rm mode}H)^T
=H^{-1}A_{\rm mode}^{T}H.
\]

The physical matrix \(A\) therefore preserves the 96 ordinary response
rows. Its transpose preserves the 96 ordinary columns. The checker
constructs \(A\) once from the general \(U,V,V_P\) formula and once
from the signed block formula. The results agree exactly.

For the complete 112-port matrix,

\[
A^2=(A^T)^2=I,\quad
\operatorname{rank}(A-I)=16,\quad
\det A=1,\quad
\operatorname{tr}A=80.
\]

All coefficients are dyadic. No inverse by 3, 5, or 7 is needed.

## Query code and scalar programs

Retain the normalized row code from the source packet:

\[
C=\begin{pmatrix}I&B\\0&I\end{pmatrix},\qquad
V_P^{-1}V=[I,B].
\]

The completed response has the exact form

\[
C A C^{-1}
=\begin{pmatrix}-I&0\\ U_RV_P&I\end{pmatrix}.
\]

This is a lower triangular code. The lower block is present and must
not be discarded.

The packet gives two scalar implementations of \(A\). A direct
physical implementation uses \(C\), a lower shear, pivot signs, and
\(C^{-1}\). It costs 5,600 real scalar primitives. A shorter word
first applies the actual pair code. In each block, it executes:

1. Add \(d_R^Tx_R\) to \(x_p\).
2. Subtract \(d_Rx_p\) from \(x_R\).
3. Negate \(x_p\).
4. Subtract the updated \(d_R^Tx_R\) from \(x_p\).

It then applies the inverse pair code. This word costs 3,276 scalar
primitives. Transpose each gate and reverse the order to obtain a
word for \(A^T\) at the same price. Both words use the existing data
fields only. They require a common admissible frame for their scalar
operations.

The final selected-target queries have arbitrary target baselines:

\[
Y_P\mathrel{+}=A[P,*]X,\qquad
Y_P\mathrel{+}=A^T[P,*]X.
\]

Their literal prices are 2,960 and 1,984 scalar primitives,
respectively. Their sources must all be in the same completed FULL
frame as the selected targets. The programs contain only dyadic
ADDs and power-of-two SCALEs. They use no extra fields.

## Native application and scope

The earlier row-replacement service removes the selected target
paths, advances the sixteen selected targets by full rank-nine
children, and adds the selected response rows after all source
fields reach FULL. The 96 other target paths remain in place.

For \(A\), those retained response rows are unchanged. For \(A^T\),
their off-diagonal support is unchanged in the actual mode chart.
The transfer weights on the pivot columns must be changed as
specified above. These facts supply exact inputs to the separate
native emitter. This packet does not replace its native replay.

The intended hybrid forward output has selected FULL fields and
96 ordinary hole fields. A formal transpose does not by itself
restore the original raw output contract. A backward service and
any conversion to the raw contract require separate complete
words, phase checks, and costs. In particular, \(A^{-1}=A\) is an
algebraic fact, not an automatic composition rule for the mixed
native frames.

The construction removes the old odd centre eigenvalues from the
response. It does not prove that the actual responses at different
supplier stages are equal, or that the final raw phase can be
removed at no cost.

## Source and validation

The checker pins the previous row-capture checker and payload, the
complete rank-sixteen native response, and the actual pair flags.
The source paths and hashes are in `ROW-INVOLUTION.json`.

Run:

```sh
python3 check_row_involution.py
python3 -O check_row_involution.py --output run-optimized
```

Both runs produce `PASS_EXACT_ROW_INVOLUTION` and byte-identical
payloads and receipts. The checks include the two independent
matrix constructions, both involution identities, exact
displacement rank, all 112 matrix columns, all 224 query columns
with arbitrary baselines, transpose support, and both scalar
programs. No complete supplier cost or kappa improvement is
claimed.

This work uses the row-capture construction and native clique
response from the coordinated centre-information campaign.
AI agents developed the algebra, programs, and checks. Independent
review is pending at this freeze and will use a separate packet.
