# A sharp affine product cover of each correlated phase sector

This note gives an exact algebraic covering theorem. Every point of a
fixed correlated phase sector lies in an affine product piece of the
largest possible dimension for that residue. A binary quadratic-form
extension constructs a piece from the point. This is a statement about
Fourier addresses. It does not make those addresses available to the
physical stream, or supply a cheap way to select a different code for
each address.

The note uses the sharp fixed-residue dimensions from
`../review-gauss/maximal-affine-sectors/RIGIDITY.md`, SHA256
`46b218bc3486f2581fad40ad4c0d7e1257f87fad999129d41d40252bc99bd049`.
That proof uses the common-form argument in the reviewed
correlated-access packet. The covering proof is given here.

## 1. A pointwise quadratic-form description

Let `X` have `n>=1` rows `x_i` in `F_2^lambda`, where `lambda>0`.
Let `S_(n,d)` be the matrices for which every odd row sum has weight
`d` modulo four. Set

    a=x_1,
    E=omega^perp,
    W_0=span(x_i+a : 2<=i<=n),
    q_a(w)=wt(w)/2+a.w mod 2,  w in E.

The form `q_a` is quadratic on the even-weight space `E`, and its
polar form is the dot product. The following criterion is exact:

    X in S_(n,d)
       iff wt(a)=d mod 4 and q_a vanishes on W_0.          (1)

For necessity, equality of the weights of `a` and `x_i` first shows
that `x_i+a` is even. It also gives `q_a(x_i+a)=0`.
For distinct `i,j>=2`, the odd row sum `x_1+x_i+x_j` gives
`q_a((x_i+a)+(x_j+a))=0`. Polarization then makes the two differences
perpendicular. Thus `q_a` vanishes on their whole span. There is no
pair condition to check when `n<=2`.

Conversely, every odd row sum is `a+w` for some `w` in `W_0`. The
identity

    wt(a+w)-wt(a)=2 q_a(w) mod 4

proves sufficiency. This criterion applies to the complete all-odd
sector. It does not identify the sector from only the supplier's 112
port labels.

## 2. The largest extension of the difference code

Write `lambda=2f` or `2f+1`. For a nonempty residue define

    kappa_lambda(d)=f     if d=f                at even width,
                    f     if d=f or f+1         at odd width,
                    f-1   otherwise.

At width one, only residues zero and one occur and both have
`kappa=0`. At width two, residues zero, one, and two have dimensions
zero, one, and zero; residue three is empty.

Every totally singular `W_0` in (1) is contained in a totally singular
space `W` of dimension exactly `kappa_lambda(d)`. Therefore

    X belongs to (a+W)^n subset S_(n,d),
    dim((a+W)^n)=n kappa_lambda(d).                       (2)

The dimension in (2) is the sharp affine upper bound. Thus the
products in (2) cover every fixed-residue sector. In even width only
the preferred residue is covered by the maximum-dimensional sectors
of the unrestricted `S_n`. In odd width this applies only to the two
preferred residues. Other residues need their smaller optimal pieces.

Here is a direct proof of the extension statement. The complete
quadratic sum is

    sum_(w in E) (-1)^q_a(w)
      = Re((1+i)^(lambda-wt(a)) (1-i)^wt(a)).              (3)

For odd width, `E` is symplectic of dimension `2f`. The sum in (3) is
`+2^f` exactly for the two preferred residues, and is `-2^f` otherwise.
Its quadratic form is split in the first case and nonsplit in the
second. Their largest singular dimensions are `f` and `f-1`.

These facts and the prescribed extension need no code classification.
In a nondegenerate binary quadratic space, choose a nonzero singular
vector `u`. Choose `v` with `u.v=1`, then replace `v` by
`v+q(v)u`. This makes `v` singular and gives a hyperbolic plane.
Its orthogonal complement is nondegenerate. If `u` belongs to a
prescribed singular subspace, adding a multiple of `u` to each other
basis vector puts the remaining prescribed space in that complement.
Repeat. A hyperbolic plane has quadratic sum two, so (3) determines
whether the final two-dimensional remainder is hyperbolic or
anisotropic. This constructs an extension of every prescribed
singular space to the stated largest dimension.

For even width, the radical of `E` is the line spanned by `omega`, and

    q_a(omega)=f+d mod 2.

If this value is one, projection of `W_0` to `E/span(omega)` is
injective and isotropic. Extend its image to a symplectic Lagrangian.
On the preimage of that Lagrangian the polar form is zero, so `q_a`
is linear. Its value on `omega` is one. Its kernel is the required
extension of dimension `f-1`.

If `q_a(omega)=0`, first add `omega` to `W_0`, then pass to
`E/span(omega)`. The quadratic form descends to this symplectic
space of dimension `2f-2`. Its quadratic sum is half of (3), namely
`+2^(f-1)` for `d=f` and `-2^(f-1)` for `d=f+2`.
The nondegenerate extension just proved, followed by addition of the
radical line, gives dimensions `f` and `f-1`.

All steps use binary row reduction and hyperbolic-pair construction.
For example a direct dense implementation uses a polynomial number
of bit operations in `lambda+n`. This describes an algebraic
certificate for one Fourier address. It is not a native query or a
physical stream-cost estimate.

## 3. Exact multiplicity in this product cover

The covering theorem also gives an exact count of the optimal product
pieces that contain a specified point. This count is not the number
of all affine pieces of maximum dimension at a nonpreferred residue.

Define

    L(g)=product_(j=1)^g (2^j+1),                 g>=0,
    Z_plus(0)=1,
    Z_plus(g)=2 product_(j=1)^(g-1) (2^j+1),      g>=1,
    Z_minus(g)=product_(j=2)^g (2^j+1),           g>=1.

Here `L` counts symplectic Lagrangians. `Z_plus` and `Z_minus` count
largest singular subspaces of split and nonsplit nondegenerate
quadratic spaces of dimension `2g`.

Put `r=dim W_0`. At odd width, the number of products `(a+W)^n` in
(2) that contain `X` is

    Z_plus(f-r)       at a preferred residue,
    Z_minus(f-r)      at another nonempty residue.

At even width with `q_a(omega)=1`, the count is `L(f-1-r)`.
At even width with `q_a(omega)=0`, put
`r'=dim(W_0+span(omega))`. The count is

    Z_plus(f-r')      if d=f,
    Z_minus(f-r')     if d=f+2.

The arguments of `Z_minus` are at least one in every nonempty case.
The counts follow by taking the perpendicular quotient by the
prescribed singular subspace. The split or nonsplit type is unchanged
when a hyperbolic plane is removed. In the case `q_a(omega)=1`, each
Lagrangian in the symplectic quotient has exactly one singular lift,
namely the kernel of `q_a` on its preimage.

For completeness, the quadratic counts follow from a short recurrence.
A split space of dimension `2g` has
`(2^(g-1)+1)(2^g-1)` nonzero singular vectors. A nonsplit one has
`(2^(g-1)-1)(2^g+1)`. Count pairs consisting of a largest singular
subspace and a nonzero vector in it, then take the perpendicular
quotient by that vector. The initial counts are `Z_plus(1)=2` and
`Z_minus(1)=1`. This gives the displayed products.

## 4. Exact checks and the remaining access question

`check_coverage.py` uses only the Python standard library. It directly
checks the point criterion on all row tuples in small dimensions.
It enumerates self-orthogonal row subspaces through width six, checks
the signed sums, extends every singular subspace by direct containment,
and compares the exact multiplicities with the formulas above. It
does not import a producer or another lane's checker.

The construction in `../affine-projector-stream/` supplies a physical
stream for the standard pair-code pieces. This theorem supplies other
algebraic pieces and an address-dependent choice. It does not supply
their address maps, a shared implementation of many pieces, or a
native operation that makes the Fourier address readable. The affine
coverage lower bounds therefore remain in force for any fixed list
of such encodings.

Proof and exact checks: OpenAI Codex under the user's direction.
The parent proposed the maximum-sector rigidity question. The
independent rigidity proof supplies the sharp fixed-residue bound;
this note adds the point criterion, prescribed extension, and exact
cover multiplicity. No PR, push, or commit was made. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
