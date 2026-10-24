# A sharp lower bound for monomial native ADDRESS words

Use the native model from PR521 at
`a190fdb39f31647fc6f651625353710624627348`. There are r productive
binary DATA roles and m rational ADDRESS difference coordinates. A
query is `H_N(g)=I+N tensor (g-1)` in `Mat_r(F_2[G])`, where G is the
rational ADDRESS group and N is a binary rank-one idempotent. The
target is `I_r tensor (-I_m)`. Every DATA role must reach that target
on arbitrary input. There is no uncompleted private role.

The complete all-size ADDRESS identity gives the formal group-algebra
identity. To see why, separate its finite set of distinct rational maps
by a rational vector outside their pairwise equality subspaces. An odd
allowed prime that avoids the finite denominator and collision data
retains distinct images. Distinct VALUE bits then separate the formal
coefficients. An identity on one small ADDRESS grid is not sufficient.
The native lift Phi is injective and preserves products, so the same
argument applies to the lifted maps.

## A valid representation in characteristic two

Assume that every g is a rational monomial matrix: each row and column
has one nonzero entry. Let `R=F_2[e]/(e^2)`. Map each positive nonzero
entry to 1 and each negative entry to `1+e`, and leave zero entries zero.
Call the resulting monomial matrix rho(g). This is a group homomorphism.
Each entry of a monomial matrix product has one nonzero product term,
and `sign(xy)=sign(x)sign(y)`. The equation `(1+e)^2=1` preserves the
negative-sign involution. There is no map from binary coefficients to
the rational field in this construction. Both the coefficient field and
R have characteristic two.

The homomorphism extends linearly from `F_2[G]` to `Mat_m(R)`.
It sends the complete target to `(1+e)I_(rm)`.

## Every query difference has one outer-product factor

If a nonidentity rational monomial g has `rank_Q(g-I)=1`, it is one of
two types:

- One coordinate is scaled by a nonzero rational number different from 1.
- Two coordinates are exchanged with reciprocal weights, and every
  other coordinate is fixed.

For the classification, a cycle of length l in the underlying permutation
has kernel dimension at most one in `g-I`, hence rank at least `l-1`.
Different cycles use disjoint coordinates. A cycle of length at least
three, two nontrivial cycles, or a changed spectator scale gives rank
at least two. A two-cycle has rank one precisely when its weights
multiply to 1.

A positive coordinate scale maps to identity. A negative coordinate
scale has difference `e e_i e_i^T`. For a reciprocal exchange, both
weights have the same sign. Its difference on the two coordinates is

    [1 1; 1 1] = (1,1)^T (1,1),

or

    [1 1+e; 1+e 1] = (1,1+e)^T (1,1+e).

Thus `rho(g)-I=u v^T` over R, or it is zero. Since N has a binary
rank-one factorization, `N tensor (rho(g)-I)` also has one outer-product
factor over R.

Every nonzero query difference in this representation comes from a
negative-determinant monomial map. Positive coordinate scales contribute
zero. Reciprocal exchanges have determinant -1.

## The target requires at least rm factors

For a product P of k represented queries, telescope `P-I`. Each summand
is a query difference multiplied by the preceding or following product.
It still has one outer-product factor. Hence a successful word gives

    e I_d = B C,       d=rm,

where B has d rows and k columns, and C has k rows and d columns. Write
`B=B0+e B1` and `C=C0+e C1`, with binary matrices. The two coefficients
give

    B0 C0=0,          B0 C1+B1 C0=I_d.

The second equation gives

    d <= rank(B0)+rank(C0).

The first equation puts the image of C0 in the kernel of B0, so

    rank(B0)+rank(C0) <= k.

Therefore `k>=rm`. Zero query differences can be removed from the
factorization, so at least rm queries must have negative determinant.
This argument uses binary field ranks only after the valid R-valued
representation has been formed.

For four DATA roles and three ADDRESS coordinates, at least twelve
queries are necessary. The twelve coordinate-reflection queries reach
the target. The bound is sharp. All ten- and eleven-query B3 words are
therefore impossible. This closes the mathematical B3 question even
though the earlier ten-query solver run returned UNKNOWN.

## Free DATA basis changes and unchanged dirty helper roles

An invertible binary DATA basis change S can move past a query by
conjugating N to `S N S^-1`. That matrix is still a binary rank-one
idempotent. Apply the ADDRESS group augmentation `g -> 1` to the full
word. Every query becomes identity. The complete target also becomes
identity, so the product of all free DATA basis changes is identity.
They can all be absorbed into the query projectors. Thus free binary
DATA basis changes do not evade the bound.

If there are extra dirty roles that must be unchanged on every input,
the represented target difference is `diag(e I_(rm),0)`. Telescope
the queries as before, and select the productive rows of B and the
productive columns of C. This gives `e I_(rm)=B_P C_P`, so the same
bound holds. The full endpoint again has identity DATA augmentation.
This extension requires complete arbitrary-input identity on the helper
roles. A clean-zero premise, discarded helper output or a different
global DATA endpoint does not meet that condition.

## Scope and attribution

The bound permits all binary rank-one idempotents and arbitrary nonzero
rational monomial weights. It does not exclude nonmonomial rank-one
unipotents, maps with higher-rank ADDRESS differences, helper roles with
other input or output contracts, different endpoints, or another compiler
model. It is a
finite word obstruction, not a lower bound for integer multiplication.
It gives no supplier gain and no new kappa.
The call count alone does not give a kappa ceiling for other constructions;
their child volumes, widths, helper state and recurrence invoices must
also be priced.

The native ADDRESS model is reused from PR521. The dual-number argument
was proposed by the coordinating research agent and reconstructed in
this independent audit. AI assistance was used. No global novelty claim
has been established by this packet.
