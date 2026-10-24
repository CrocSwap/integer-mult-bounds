# Independent proof review of the affine product cover

Result: accept `COVERAGE.md` with its separate `AMENDMENT.md`.
The original proof hash is
`9f2e1ace092f732b2c839cc03be02ce7c2348bdeda4357b754947531517f9373`.
The required amendment hash is
`38e6fe5b73f68d18315cff6b285830773c6ef09288c8ea4de5231f994793f96d`.

This is a bounded proof review. The producer checker was read, but it
was not imported or run. Its finite counts are not independent
computational results of this review.

## Point criterion

The domain condition `W_0 subset E` is required and is now explicit.
Equal row weights imply that each difference `x_i+a` is even and has
`q_a(x_i+a)=0`. Each triple through row 1 makes a pair of these
differences perpendicular. Thus the quadratic form is zero on their
whole span. For one or two rows, there is no missing pair condition:
the difference space has at most one generator. Conversely, each odd
row sum is `a+w`, and the displayed weight identity proves its residue.
This proves the criterion for all `n>=1`.

## Prescribed extension

The complete quadratic sum is the real part of the product in (3).
The odd-weight terms of that product are imaginary; its even-weight
terms are precisely `(-1)^q_a(w)`. This proves the formula directly.

At odd width the polar space `E` is nondegenerate, and the sign of the
sum gives the stated split or nonsplit type. A prescribed singular
vector can be the first vector of a hyperbolic pair. Changing the
partner by `q(v)u` makes it singular. For every other vector of the
prescribed singular space, adding its dot product with the partner
times `u` puts it in the orthogonal complement. Its quadratic value
stays zero. This preserves the prescribed space while the construction
continues. The final Witt index is therefore also attainable by an
extension of every prescribed singular space.

This is a polynomial binary procedure. A search for the next singular
vector does not need a search through the whole vector space. Test
basis vectors, then pair sums. If none is singular and there are at
least three basis vectors, all basis values and pair polar products
are one, so a sum of three basis vectors is singular. Dimension two
can be checked directly. Thus the stated algebraic construction does
not conceal an exponential search.

At even width the radical is `span(omega)`. If `q_a(omega)=1`, the
prescribed space avoids that line and projects to an isotropic space
in the symplectic quotient. Extend it to a Lagrangian. The preimage
has zero polar form and dimension `f`, so the quadratic form is linear
there. Its kernel has dimension `f-1`, contains the prescribed space,
and is the unique singular lift of that Lagrangian.

If `q_a(omega)=0`, add the radical line first and descend to the
nondegenerate quotient. Its quadratic sum is half the sum on `E`.
The preferred residue gives the split case; residue `f+2` gives the
nonsplit case. Lifting a maximum extension in that quotient gives
exactly the dimensions in the proof. The small empty residue cases
prevent a nonexistent negative zero-dimensional quadratic space.

It follows that every point belongs to a product piece of the sharp
fixed-residue dimension. The product cover is valid for `n=1` and
`n=2` as well as for larger row counts.

## Multiplicity

For a prescribed singular space in a nondegenerate quadratic space,
take its perpendicular quotient. Removing a hyperbolic plane preserves
the split or nonsplit type. This gives `Z_plus` and `Z_minus` at the
stated reduced arguments. In the even singular-radical case, the
dimension to remove is `dim(W_0+span(omega))-1` after quotienting by
the radical. This gives the displayed argument `f-r'`.

In the even nonsingular-radical case, the unique singular lift proved
above gives a bijection with extending symplectic Lagrangians. This
gives `L(f-1-r)`, with no additional factor.

The nonzero singular-vector counts in the proof follow from the
quadratic sums. Incidence counting by a nonzero singular line gives
the displayed products, with `Z_plus(0)=1`, `Z_plus(1)=2`, and
`Z_minus(1)=1`. Every reduced nonsplit argument is at least one.
These counts enumerate the optimal product pieces containing a point;
they do not enumerate all nonproduct affine pieces at other residues.

## Corrected scope

The unrestricted maximum-dimension residue statement requires `n>=3`.
For `n=2, lambda=2`, the diagonal affine sector `{(x,x)}` is maximum
and contains nonpreferred residues. The amendment now states this
counterexample and limits the consequence to the reviewed rigidity
hypothesis. For `n>=3`, rigidity and this cover prove that the union
of all globally maximum affine sectors is exactly the preferred
residue part or parts.

No physical Fourier-address read, adaptive code selector, general
code stream, shared implementation of the cover, or native supplier
is constructed. The classical polynomial procedure returns a code
when a Fourier address is supplied as explicit binary data. That
input is not available for free in the physical owner stream.
The existing affine coverage limits therefore remain in force.

Both findings are resolved by the pinned amendment. No frozen producer
or earlier review file was changed. No PR, commit, or push was made.
Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
