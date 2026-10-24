# A plane phase involution without a replica

The actual paired planes admit an exact involutive endpoint with two
unpaid directions. It differs from the original complex plane phase
by an affine address map. No extra data field or spectator bit is
needed. This resolves the local phase condition for a possible new
plane core. It does not implement its scalar queries or restore its
borrowed owners.

Every selected positive-stage route fails to preserve the matched
plane. The note gives explicit replacement routes on 65 coordinates.
They preserve both plane directions and cover all coordinates in nine
local calls. A complete core and owner schedule on that geometry remain
open. No supplier or kappa improvement is claimed.

## The exact local operator

Use the actual convention

    C_q=((1+i)I+(1-i)X_q)/2,  C_q^2=X_q.

Let q,r be an ordered orthonormal pair for the binary dot product.
Put E=span(q,r), and let P be the orthogonal map that exchanges q and
r and fixes E perpendicular. Its explicit action is

    P x=x+((q+r) dot x)(q+r).                           (1)

Use the same symbol for its address-permutation operator. Let

    C_E=C_q C_r, A=X_r P, T=C_E A.                     (2)

Operator products act from right to left. Thus A first exchanges the
two plane coordinates, then translates by r. Since P sends r to q,

    A^2=X_(q+r)=C_E^2.

The swap P commutes with C_E, and translations commute with C_E.
Consequently A commutes with C_E. The exact formulas are

    T=C_q C_r^-1 P, T^2=I.                            (3)

There is no scalar phase in (3). The two plane directions remain
native Fourier directions. Right multiplication by the monomial A
preserves the Fourier rank and the output Lagrangian of C_E. Thus the
new endpoint has the same plane frame as the old one. A fitting mask
derived only from those frames does not change. Complete physical
scalar words still need their ordered phase adapters.

## Compatibility with the actual full phase

Let F=C_(e_0)...C_(e_8) be the nine-coordinate phase. An orthogonal
swap of q and r need not commute with F. The needed condition is

    wt(q)=wt(r) modulo 4.                              (4)

To prove this, set w=q+r. Orthogonality gives an even intersection of
the supports of q and r. Under (4), wt(w)=2 modulo 4. For any x with
w dot x=1,

    wt(x+w)-wt(x)=wt(w)-2|support(x) intersect support(w)|

is zero modulo 4. For w dot x=0, P fixes x. Hence the Fourier multiplier
i^wt(x) is invariant under P, so PF=FP. This proof also applies in any
larger canonical address space when q and r lie in it.

Every actual matched label has weight 3 or 7. Thus every selected pair
satisfies (4). All line phases commute with F, so

    FT=TF                                                   (5)

on every actual plane.

Choose an orthonormal basis B=(q,r,b_2,...,b_8). Let C_B be its product
of line phases. There is an exact translation delta with

    C_B=F X_delta.

For coordinate a, set
`delta_a=(sum_(b in B) b_a-1)/2 modulo 2`. The same mod-four expansion
as in the preceding plane-repair proof gives this identity. In the
actual case, delta dot q=delta dot r=1, so P fixes delta. It follows
that

    FT=X_(delta+q) C_(E perpendicular) P.              (6)

The middle factor uses the seven displayed complement directions.
Equation (6) gives a rank-seven physical data advance, with all phases
and address maps explicit. Splitting the seven directions into three
and four gives two halving-compatible native children. The surrounding
address operations and their legal selected-slot implementation still
need a finite invoice. The operator identity does not set their cost
to zero.

## A scope limit and an even-rank extension

At tensor depth lambda, take the tensor power of (2). The same monomial
adapter gives T^2=I. On one four-dimensional plane space, trace(T)=2.
Therefore the dimension of the negative eigenspace at depth lambda is

    (4^lambda-2^lambda)/2.                             (7)

The one-column negative eigenspace has dimension one. This does not
give a one-quarter volume code at arbitrary tensor depth; the ratio
in (7) tends to one half.

More generally, let E have an even orthonormal basis grouped into
pairs. Let P exchange each pair, and let b be the sum of one chosen
axis from every pair. Then A=X_b P has square equal to the product
of translations along all axes in E. It commutes with C_E. Therefore
T=C_E A is an involution with the same Fourier frame as C_E. If the
two axes of every pair have equal weights modulo four, P also commutes
with the canonical full phase.

There is a precise odd-rank limit to this particular construction.
For an orthogonal P on a binary dot-product space, the characteristic
vector omega is fixed. Thus `(I+P)b` always has even parity. An affine
map X_b P cannot square to translation by the sum of an odd number of
orthonormal directions: that sum has odd parity. This statement covers
orthogonal affine address square roots only. The nonorthogonal
controlled map using an extra spectator bit is a counterexample to
any unrestricted version of the statement.

## The retained routes fail, and exact plane routes exist

The selected route for port q fixes q and exchanges all eight axes of
q perpendicular in the base nine-space with a fresh eight-space.
Since its partner r belongs to q perpendicular, every positive-stage
route sends r out of the base plane E. Thus none of the 896 positive
port-stage routes preserves its matched plane. The old geometry cannot
be used without a new interface proof.

Here is one exact replacement geometry. Use 65 coordinates, with the
base nine-space and eight disjoint fresh seven-spaces E_s. For a plane
chart B as above, define rho_s to fix q,r and exchange b_2,...,b_8
with the seven standard axes of E_s. It fixes every other coordinate.
Let rho_0=I. Each rho_s is an orthogonal involution and commutes with
the plane phase and the adapter A. The nine local spaces are

    E plus span(b_2,...,b_8), E plus E_1, ..., E plus E_8.

Their complement parts are disjoint and their sum has dimension
`2+9*7=65`. A common orthogonal cover on 65 coordinates can therefore
carry these exact plane-preserving routes at the level of labels.
This is a route construction, not an owner-matching construction.
The changed dimension also changes helper jobs, idle work, cover size,
parent volume, and the recursive exponent calculation.

The present scalar mask has an independently checked rank-49 fitting
matrix and a rank-48 lower bound. Its queries, responses, and free
corrections are explicit. This local plane involution removes the need
to double that core solely to obtain T^2=I. It does not make any of
those 49 queries, responses, or owner paths free. Their copied-rank
cost must be derived for the new plane frames; the old line-only
functional is not an admitted plane cost.

## Exact checks and credit

Run from this directory:

    python3 -I -O -B check_plane_involution.py

Expected first line:

    PASS_EXACT_PLANE_INVOLUTION_AND_ROUTES

The checker consumes the pinned matching from [PR #1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825),
the actual DATA-PHASES member, and the frozen plane charts. It checks
(3) on all four spatial basis columns, (4)--(6) on all 512 characters
for all 56 actual planes, every retained positive-route failure, and
all 504 replacement routes. It also checks the complete dimension-65
span and rejects a wrong translation in A. All arithmetic is integral
or exact Gaussian arithmetic. The all-depth and even-rank conclusions
follow from the displayed proofs.

The predecessor supplied the matching. The plane-repair proof supplied
the exact phase lift and charts. The cover-algebra lane supplied the
rank-49 scalar construction; its native implementation remains open.
This work used substantial OpenAI Codex assistance under the user's
direction. It does not alter frozen evidence or the selected frontier.
