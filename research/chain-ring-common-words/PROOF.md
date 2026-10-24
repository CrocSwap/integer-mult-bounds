# Three factors for singular matrix targets over truncated polynomial rings

Prepared for Cinna Davis / 1337isnot1337 with substantial OpenAI Codex
assistance. Apache-2.0. This is a scoped formal-alphabet proof.

Let K be any field, S=K[t]/(t^d) with d>=1, and
R=product_i M_{m_i}(K[t]/(t^{d_i})), a nonempty finite product.
On two roles the allowed paid factors are I+u y^T, with u in R^2 and
**y in K^2**. Common GL2(K) maps may be free. Singular paid factors are
allowed. There are no scratch roles.

**Theorem.** Every target M in M2(R), including zero and singular targets,
has a three-factor word with fixed right vectors e1,e2,e1. The word uses no
free endpoint maps. The bound is sharp, already for singular targets over
M2(F2[t]/(t^d)) at every d>=1. For a single scalar component S, every target
has cost at most two if free base-field maps are allowed.

The scalar two-factor statement is an application of Nick Petalas's #4276
criterion. The three-factor absorption skeleton is the one in JoyboyBrian's
#5156, extending Nick Petalas's #4805. The new ingredient is a completion
through arbitrary nilpotency for possibly singular top block rows, followed
by #4749's semilocal unit-completion step. Classical Smith elimination and
stable range one are not claimed as new. The claim concerns this particular
restricted-right-vector alphabet and coefficient algebra, not a native
recursive supplier.

## 1. Complete a singular rectangular row over S

Write a single-component target in m by m blocks as
M=[[A,B],[C,D]], and L=[A B]. Valuation elimination gives invertible matrices
P in GL_m(S), Q in GL_{2m}(S), and s_1,...,s_m in S such that

    P L Q = [diag(s_1,...,s_m)  0].

Here each nonzero s_i is a power of t, and zero s_i are allowed. For
completeness, select a nonzero entry of least t-valuation in the remaining
rectangle. Swap it into the pivot position and multiply its row by a unit
to make the pivot t^v. Every remaining entry is divisible by t^v. Row
subtractions clear its column, and column subtractions clear its row.
All operations are invertible even when t^v is a zero divisor: division is
only the choice of a coefficient h with t^v h equal to the entry being
cleared. Recurse on the smaller rectangle. If it is zero, stop and fill the
remaining diagonal with zeros. This proves the displayed decomposition
without assuming any singular pivot is invertible.

Set

    a = P^{-1} diag(s_i),       [X Y] = [I_m 0] Q^{-1}.

Then [A B]=a[X Y], and [X Y] has a right inverse: it consists of the first
m rows of an invertible 2m by 2m matrix. In particular its reduction modulo
t is a surjective map K^{2m}->K^m. Unlike a itself, this completed row is
unimodular. It also covers [A B]=0 by taking a=0 and [X Y]=[I 0].

## 2. A unit pivot for the completed row

There is an F in M_m(S) such that E=X-YF is invertible. Indeed F can be
chosen with all entries in the constant field K. Write X0,Y0 for residues
modulo t, so im X0 + im Y0 = K^m.

Choose U complementary to ker X0 in the domain. The restriction of X0 to
U identifies U with im X0. The dimension of ker X0 equals the dimension of
K^m/im X0. Choose vectors whose Y0 images form a basis of that quotient,
and define F0 to map a basis of ker X0 to those vectors, and U to zero.
Then X0-Y0F0 maps U isomorphically to im X0 and maps ker X0
isomorphically to the quotient. It is therefore invertible over K.
Lift F0 as the constant matrix F. A matrix over S is invertible exactly
when its residue is invertible. One proof lifts the residue inverse and
uses the finite geometric series for the resulting matrix in t M_m(S),
whose d-th power is zero. Thus E is invertible.

This is the stable-range-one step used for invertible targets in #4749.
The singular target M is never inverted. Only its completed row is used.
The block coefficient F is algebra-valued, despite its scalar entries
being constant in this construction. It need not be a scalar multiple of
I_m, so declaring F to be a free GL2(K) chart would be incorrect.

## 3. The complete endpoint and common word

Define

    b = (C-D F) E^{-1},       delta = D-bY.

Direct multiplication, preserving block order, gives

    M = [[a,0],[b,I]] [[I,Y],[0,delta]] [[E,0],[F,I]].       (1)

The top row is a[E+YF,Y]=a[X,Y]=[A,B]. The lower-left block is
bE+DF=C, and the lower-right is bY+delta=D. All four blocks are accounted
for; no output is discarded or assumed zero. The three factors have the
forms

    I+(a-I,b)^T e1^T,
    I+(Y,delta-I)^T e2^T,
    I+(E-I,F)^T e1^T.

Apply (1) separately to every component of R and assemble the coefficient
tuples. Every component uses exactly the same ordered right vectors.
Thus the product algebra needs just three R-valued factors; no component
has its own free endpoint map. Execution on column data uses the rightmost
factor first. Equation (1) is an algebraic product in the indicated order.

## 4. Single scalar chain ring: two factors and exact cost

For M=[[a,b],[c,d]] over S, its first-row entries generate comparable
principal ideals. Swap the two input columns, if needed, so b=a q for
some q in S. If a=b=0, use q=0. Then

    M H = [[a,0],[c,1]] [[1,q],[0,d-cq]],

where H is either I or the scalar swap. The two factors have allowed
right rows e1,e2, and H^{-1}=H is free. This is #4276's criterion with
only a column permutation needed. No division by a nonunit is asserted.

The exact scalar cost is zero when M is a constant invertible matrix;
it is one otherwise when Mx=w for some nonzero x,w in K^2; and it is two
in every remaining case. The one-factor test is inherited from #4276:
a paid factor fixes a nonzero constant vector in the kernel of its right
row. Conversely, if Mx=w, choose T in GL2(K) with Tw=x; then MT-I kills
w, so its two columns have K-span dimension at most one and it is an
allowed rank-one update. This does not count a singular constant matrix
as free. Zero has exact cost two.

## 5. A singular sharp example at every nilpotency depth

Let C0=[[0,1],[1,1]], X=E00, Y=E10 over F2, and

    M0 = [[X,Y],[C0 X,C0 Y]]
       = [[1,0,0,0], [0,0,1,0], [0,0,1,0], [1,0,1,0]].

Its ordinary rank is two. For every nonzero scalar row phi=(r,s),
rI+sC0 is invertible, because z^2+z+1 is irreducible over F2. Therefore
[phi_1 I phi_2 I] M0 has rank two. For every nonzero scalar column
v=(u,v), the matrix uX+vY has rank one. Consequently every one of the nine
row/column choices in #4276 Corollary C has ranks two and one respectively,
and its exact two-factor criterion fails. The three-factor word above
attains cost three.

View the same constant M0 over M2(F2[t]/(t^d)). A word of at most two
factors would reduce modulo t to a word of at most two for M0 over M2(F2),
which was excluded. Formula (1) gives three, proving exact cost three at
every d. This is an explicit application of the predecessor rank criterion;
three-factor sharpness over matrix algebras is prior work.

## Scope, limitations and next decision

PR5156 treats products of full matrix algebras. The present proof supplies
its requested singular radical extension for the stated matrix chain
rings, without restricting nilpotency depth. PR4749 already handles
invertible targets over arbitrary semilocal algebras; the addition here is
singular endpoints. The multigenerator square-zero counterexamples of
#4745/#4776 remain valid. Their coefficient algebras are not chain rings,
and the rectangular completion in section1 need not exist there. Nothing
here classifies all finite-dimensional algebras or all singular endpoints.

For characteristic p and cyclic group order p^h, the standard identity
K[C_{p^h}]=K[t]/(t^{p^h}), t=g-1, puts cyclic modular group-algebra
coefficients in scope. This is an algebraic observation only. A native
rank-one call does not grant arbitrary u in R^2 for free.

The alphabet permits data-discarding updates. Coefficient preparation,
reversible recovery of overwritten inputs, physical routing, ownership,
stock, precision and a complete recursive invoice are unknown. The result
has no new kappa or supplier-admission claim. Independent human and
proof-kernel review are unclaimed. Bounded replay corroborates the written
proof; it does not prove its universal quantifiers by enumeration.
