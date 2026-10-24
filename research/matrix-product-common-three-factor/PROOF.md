# One common ABA word for every finite product of full matrix algebras

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a written formal-alphabet theorem, not a physical supplier theorem.

Let K be a field and R=product_{i=1}^k M_{m_i}(K), with finite k>=1 and
m_i>=1. Scalars embed diagonally in every component. On two roles a paid
factor is I+u y^T, u in R^2 and y in K^2. Common GL2(K) maps may be free,
but the construction below uses NONE. No auxiliary roles are introduced.
Targets may be singular, zero, or invertible, independently in each component.

**Theorem.** Every M in M2(R) is the product of three paid factors with the
SAME ordered right vectors e1,e2,e1 in every component. Thus every finite
tuple of singular targets over (M2(F2))^k satisfies the claimed three-call
contract. There is no component-count obstruction to this bound.

The input lemma is Nick Petalas PR4805, exact head
fbf2bd033f2d3ae1605a3cad690e1fc2fbf477e7,
research/matrix-algebra-three-factor/PROOF.md, sections 'A classical subspace
lemma' and 'Lifting the complement to a graph'. That source chooses free
block swaps before applying the lemma. We eliminate the component-dependent
swaps by a row-space completion and absorb its generally singular map into
one paid factor. We retain the lemma's credit; classical basis extension is
not claimed as new. PR4780 already supplies a common ABA word for pure field
products. PR4749 covers invertible semilocal targets; neither settles the
singular noncommutative product endpoint stated here.

## 1. Complete the top row without charging a free algebra-valued map

First consider a single component M=[[A,B],[C,D]], each block m by m.
The row space of [A B] has dimension r0<=m in K^(2m). Extend a basis of that
space to m independent rows, forming T=[X Y] of rank m. Every original row
has unique coordinates in these rows, so a matrix a in M_m(K) satisfies

    [A B] = a [X Y].

There is no need for a to be invertible. Define

    N = [[X,Y],[C,D]],     M = diag(a,I_m) N.

This equality is only an intermediate algebraic identity: diag(a,I) is NOT
assumed free or independently charged. It will be absorbed below. If the
original top row is zero, take any m independent rows for T and a=0. The
same construction includes M=0 without using an inverse of a.

## 2. The predecessor graph lemma applies in this fixed chart

Write W=im N, V=im [Y;D], and let pi be projection to the first output
K^m. Since T has rank m, pi(W)=K^m. Thus Z=W intersect ker pi has dimension
rank(N)-m. The first block column of N has at most m independent columns,
so rank(N)<=m+dim V. Consequently dim Z<=dim V.

PR4805's classical subspace lemma gives a complement U of V inside W with
U intersect Z=0. Since U is contained in W, this also means U intersect
ker pi=0. The proof works over every field, including F2; its union-of-two-
proper-subspaces step requires no generic/random field choice.

As in the cited graph lemma, N^{-1}(U) surjects onto the quotient of the
input space by its second coordinate block: subtracting a vector in that
block changes N's image by V, and W=U+V. Choose a linear section. Its image
is the graph of -F for some m by m matrix F. Therefore

    [X-YF; C-DF]

has image in U. Injectivity of pi on U gives
ker(X-YF) subset ker(C-DF). Extend the resulting linear map from im(X-YF)
to K^m to obtain b satisfying C-DF=b(X-YF). Set E=X-YF and d=D-bY. Then

    N = [[I,0],[b,I]] [[I,Y],[0,d]] [[E,0],[F,I]].

This is the predecessor multiplication in the original fixed chart; there
are no residual row swaps, column swaps or endpoint GL2 maps. The dimension
inequality was proved directly, rather than invoking the predecessor's
chart-selection procedure.

## 3. Absorption and simultaneous component assembly

Multiply the preceding identity on the left by diag(a,I). The full target
is exactly

    M = [[a,0],[b,I]] [[I,Y],[0,d]] [[E,0],[F,I]].       (1)

The first factor equals I+(a-I,b)^T e1^T, even if a is singular or zero.
The second equals I+(Y,d-I)^T e2^T; the third equals
I+(E-I,F)^T e1^T. All three are legal. Column-data execution applies the
rightmost factor first; equation (1) is algebraic product order.

Apply this construction separately to each component. Assemble a,b,Y,d,E,F
as tuples in R. Since each component uses the same right-vector sequence,
these tuples give exactly three R-valued paid factors. This uses neither
component-specific free scalar maps nor free internal-coordinate changes.
The full two-role endpoint, including every off-diagonal block, is equation
(1). No independent-component work is silently declared free.

## 4. Cost and scope

This is an upper bound of three formal paid updates, uniform in k. It does
not say that every endpoint needs three: zero and many singular endpoints
need fewer. Exact lower costs are governed by PR4276's inherited one/two-
factor criteria applied over the PRODUCT algebra with common scalar charts.
For example PR4780's binary six-component scalar rank-one tuple has cost
three, not more than three. Embed its scalar entries as scalar I2 matrices:
the common two-factor rank criterion remains the identical scalar condition,
so this gives a singular tuple in the primary (M2(F2))^k domain with exact
cost three. The new upper construction supplies the matching word.

Finite executions test an explicitly bounded domain and corroborate the
proof. They do not establish the all-field or arbitrary-k statement by
extrapolation. The constructive proof establishes that statement. Native
preparation of arbitrary matrix coefficients, overwritten-data recovery,
physical ownership/routing/cleanup, precision, stock and a recursive supplier
invoice remain unknown. There is no new kappa or selected-frontier change,
and no independent human or kernel proof acceptance is claimed.

## Open next questions

Can the same uniform skeleton be lifted through a singular radical extension
of a product of matrix algebras? Residue factorization alone need not lift
singular equations. Begin with a named square-zero extension and a complete
endpoint, preserving PR4776's existing radical obstructions. A physical
application separately needs a real producer/consumer and a fully charged
coefficient/overwrite/restoration bill before further construction expansion.
