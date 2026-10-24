# Independent derivation of the selected-row service

This derivation precedes the review of the emitted word. It gives the
map that the word must implement. It does not certify that word.

Let V have r independent rows. Let P be an ordered set of r ports,
and let V_P be the square submatrix on those columns. Assume V_P is
invertible. Put W=V_P^{-1}V. Then W_P=I.

Define C to have rows W on P and identity rows on the other ports.
If B=W-pi_P, where pi_P selects P, then

\[
C=I+\iota_P B,\qquad B\iota_P=0,\qquad
C^{-1}=I-\iota_P B.
\]

Here iota_P inserts r coordinates at P. Thus C is a shear. Its
determinant is one. If W is dyadic, both C and its inverse are dyadic.
Every addition uses an unchanged coordinate outside P. No extra field
or zero-input assumption is needed. Reversing the literal additions
gives the inverse.

The row code is independent of the basis used for the row space of V.
Replacing V by A V, for any invertible A, leaves W unchanged.

For the present response E, direct normalization of the pinned V gives
eight rows of support 21 and eight rows of support 8. The first rows
have pivot coefficient 1 and twenty coefficients of magnitude 1/2.
The other rows have pivot coefficient 1 and seven coefficients 1.
The precode therefore has 216 complex additions, at 2048 old real
scalar units under the retained scalar invoice.

These rows are left eigenvectors:

\[
WE=\Lambda W,\qquad
\Lambda=\operatorname{diag}(-5I_8,-7I_8).
\]

Therefore the selected rows of CE are exactly Lambda W. Their direct
late additions cost 3696 old real scalar units. These are separate
costs; they do not include the retained core or the new native children.

## Physical operation

Use Q for the diagonal family of positive input line operators,
q=Q^{-1}, and F for the common full operator. The raw forward word has
physical contract

\[
(Qx,y)\longmapsto(Fx,Fq(y+Ex)).
\]

Suppose the exact event list permits all operations on the selected
target fields to be removed. Every retained operation must have no
read from those fields. The source subsystem and the other targets
must retain their original event lists.

Apply C to current input Y while all target fields have the I frame.
Apply F to each selected target. Run the retained source and ordinary
target operations. After all source fields have reached F, add
the selected rows of CE from those source fields to the selected
targets. The physical result is

\[
X'=Fx,\qquad
Y'_P=F[C(y+Ex)]_P,\qquad
Y'_R=F[q(y+Ex)]_R.
\]

Scalar coefficients commute with the common F in the final query.
No step commutes C or E through Q. In particular, the precode acts
on the physical current-I target values. It does not act on a
changed logical frame.

Write T for the output operator that is F on P and Fq on R.
Then the full target contract is T C(y+Ex), since C is identity
on the rows in R. This is an invertible output representation.
Its entry into a later word, inverse, final decode, and recursive
hosting require their own implementation and cost.

## Required literal checks

The review must check the selected set and every removed event.
It must reject a retained read of a removed target. It must check
the exact full-frame recipe, including its global phase, and all
inherited native records. It must check that every source has
reached the same F frame before the final query.

The complete word must pass every arbitrary input column. The
unchanged helper fields must retain their arbitrary values.
The native and scalar invoice must include the precode, all retained
events, the sixteen full children, and the late query.

No PR, push, commit, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
