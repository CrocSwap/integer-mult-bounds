# Invariance of one fixed scalar code

Let E be a complex subspace of C^W. Let P be its orthogonal projection.
Let V be finite-dimensional. Set D=diag(A_1,...,A_W), with operators A_i
on V. Join distinct coordinates i,j when P_ij is nonzero. Then

```text
D(E tensor V) is contained in E tensor V
if and only if A_i=A_j on each graph component.
```

To prove necessity, expand the A_i in a basis B_alpha of their linear
span. Linear independence of B_alpha implies that each scalar diagonal
matrix diag(c_i,alpha) preserves E. For a finite diagonal matrix, each
spectral projection is a polynomial in that matrix. These orthogonal
projections preserve E, so the matrix also preserves E perpendicular.
It commutes with P. Hence (c_i,alpha-c_j,alpha)P_ij=0, which forces the
operator equality on every edge. For sufficiency, the same entry equation
gives [P tensor I,D]=0. The A_i need not be invertible or normal.

For the pinned real query matrix R, R R^T=56I. Thus the projection onto
ker R is I-R^T R/56. Its graph is connected on all 112 ports. A block of
independent port operators preserves this one fixed code only when all
112 completed operators agree. Equal native ranks do not meet this test.

This theorem does not exclude changing the code between calls or using a
joint operator on several arrays. The code (u,v,u+v) also shows why full
coordinate projections alone do not prevent compression: a common operator
needs two independent native inputs, followed by scalar reconstruction.
That count does not grant a free overwrite of arbitrary borrowed contents.

The [original note](frozen/lanes/source-domain/CODE-INTERFACE.md) is unchanged.
The [independent review](REVIEW.md) adopts this criterion and its stated
112-port application. Its later gauge discussion remains source context;
that discussion is already covered by the fixed-word gauge package.
No complete kappa calculation changes.
