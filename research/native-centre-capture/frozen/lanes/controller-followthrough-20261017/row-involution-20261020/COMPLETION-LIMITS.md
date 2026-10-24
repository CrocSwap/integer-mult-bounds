# Limits and two consequences of the row completion

This addendum uses the immutable `ROW-INVOLUTION.json` source with hash
`a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b`.
It does not change the earlier freeze.

## Rank clarification

In the general theorem in `ROW-INVOLUTION.md`, the sentence “The change
has rank \(r\)” means
\(\operatorname{rank}(A-I)=r\). It does not mean that
\(\operatorname{rank}(A-E)=r\) for every source. For the actual source,
the two ranks are both 16. The addendum checks the second rank
separately.

## Sixteen row changes are necessary

Let \(E\) be the actual pinned 112-port response. Allow arbitrary new
values in a set of its rows, including new coefficients across the
old component boundary. Require the resulting matrix to be a unit
over \(\mathbb Z[1/2]\).

At least sixteen rows must change: eight in the large 48-port
component and eight in the small 64-port component.

The large component is similar, by a dyadic unit, to eight signed
blocks \(I-dd^T\) of size six. Modulo 5, each block has exactly one
left-null direction. Thus its left nullspace has dimension eight.
The small component has eight blocks \(I-dd^T\) of size eight.
Modulo 7, its left nullspace also has dimension eight. The exact
physical matrix ranks are 40 modulo 5 on the large component and
56 modulo 7 on the small component.

Suppose fewer than eight large rows change. The eight-dimensional
old left nullspace contains a nonzero vector whose coefficients
at all these changed rows are zero. Extend that vector by zero
on the small component. It still annihilates the new matrix
modulo 5: its coefficients vanish on every modified large row,
and its coefficients on all small rows are zero. The new matrix
cannot be a dyadic unit. The same argument modulo 7 applies to
the small rows. This proof does not restrict the coefficients in
the modified rows.

The sixteen-row involution attains this lower bound. This is an
exact lower bound for row replacement of this fixed response.
It does not apply to changes in columns, native transfer
weights outside the selected rows, odd-denominator arithmetic,
or a different initial response.

## Uniqueness at displacement rank sixteen

The retained ordinary factor \(U_R\) has rank sixteen. The checker
verifies this rank over the rationals.

Let \(A'\) be an involution that has the same 96 ordinary rows as
\(E\), and suppose \(\operatorname{rank}(A'-I)=16\). Its retained
ordinary displacement rows are \(U_RV\), which have rank sixteen.
They therefore span the full row space of \(A'-I\). This row
space is the row space of \(V\), so there is a unique matrix
\(U'\) such that

\[
A'=I+U'V,\qquad U'_R=U_R.
\]

Both \(U'\) and \(V\) have rank sixteen. The involution identity
then gives

\[
0=U'(2I+VU')V,\qquad VU'=-2I.
\]

Since \(V_P\) has an inverse, this forces

\[
U'_P=V_P^{-1}(-2I-V_RU_R).
\]

Thus \(A'=A\), the frozen row involution. This stronger uniqueness
statement uses the actual rank of \(U_R\). It is not a claim about
other pivot sets or involutions with larger displacement rank.

## A symmetric unit with a cheaper selected query

Let \(\Pi_P\) be the diagonal projector on the sixteen pivots. The
actual normalized row code satisfies

\[
S=CA=E-\Pi_P=C^TDC,\qquad D=I-2\Pi_P.
\]

In one signed block, with \(b=d_R^T\),

\[
S=
\begin{pmatrix}
-1&-b\\
-b^T&I-b^Tb
\end{pmatrix},
\qquad
S^{-1}=
\begin{pmatrix}
k-2&-b\\
-b^T&I
\end{pmatrix}.
\]

The complete physical response is symmetric and dyadic. It has
determinant one. Its displacement from the identity has rank 32,
which is larger than the rank of \(A-I\).

The selected query is

\[
Y_P\mathrel{+}=S[P,*]X=-V_P^{-1}VX.
\]

It costs 1,904 scalar primitives on the existing common-frame
fields. This is a different response from the selected rows of
\(A\), whose query costs 2,960. There is no pricing discrepancy.

A scalar word for \(S\) applies the actual pair code, the signed
block capture, the pivot signs, the transposed capture, and the
inverse pair code. It costs 2,508 scalar primitives. Its literal
inverse has the same price. Both words use no extra fields.

Only the selected diagonal entries differ from the old response.
This supplies another input for the row-replacement native
emitter. The inverse has ordinary diagonal entries, so the
existing off-diagonal native grammar does not automatically
implement it. No native inverse or complete caller is claimed.

## The diagonal metric of the involution

In each signed block, define

\[
M_{pp}=k-3,\qquad M_{ii}=-1\quad(i\ne p).
\]

Then \(A=I+Md\,d^T\), and

\[
A^T=M^{-1}AM,\qquad A^TM^{-1}A=M^{-1}.
\]

The physical pair code preserves this diagonal matrix: its
selected pairs have the same value 3 on both ports, and its
ordinary pairs have value \(-1\) on both ports. The small
selected values are 5.

For any diagonal unitary phase \(Z\) on the selected ports,
put \(L=ZA\). Since \(M\) commutes with \(Z\),

\[
L^*=M^{-1}L^{-1}M.
\]

This is an exact operator identity. The inverse metric contains
\(1/3\) and \(1/5\), so it is not a dyadic unit. A caller that uses
these factors must prove the required divisibility of its live
values and include the scalar cost. This addendum does not
provide that caller.

## Validation

Run:

```sh
python3 check_completion_limits.py
python3 -O check_completion_limits.py --output limits-optimized
```

Both runs produce `PASS_ROW_COMPLETION_LIMITS` and byte-identical
payloads and receipts. The checks use exact rational and finite
field arithmetic. They verify both modular ranks, the ordinary
factor rank, both symmetric inverse orders, all literal scalar
words, the arbitrary-baseline selected query, and the metric
identities. Native emission, phase admission at a caller cut,
and complete supplier pricing remain separate.

The coordinated independent review supplied the stronger
uniqueness argument and checked the nullspace lower-bound
argument. The bridge and native review workers supplied
independent forms of the symmetric completion. This packet
records the exact combined statement and producer checks.
AI assistance was used throughout.
