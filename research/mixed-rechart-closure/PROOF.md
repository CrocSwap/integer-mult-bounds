# Mixed line/hyperplane rechart closure

This scoped written proof was produced by Nick Petalas. New work is Apache-2.0.
The maximum-closure/min-cut equivalence and distributive-lattice methods are
classical. The new step is the explicit mixed rechart representation and its
linear-price optimization consequence.

## Contract and theorem

Let V be a finite-dimensional vector space over any field. Fix a hyperplane H
and a line L with L not contained in H. At each vertex v of a finite directed
graph, an original subspace U_v is given. Every edge u -> v obeys U_u subset U_v.
An allowed replacement at v is any distinct member of

    A_v = U_v intersect H,
    U_v,
    P_v = A_v + L,
    B_v = U_v + L.

Require replacement subspaces to remain nested on every edge. Any vertices
may be pinned to named allowed options. Zero edge rank gaps are permitted.
The objective is any rational linear combination of vertex dimensions and
edge rank gaps, where the gap is dim(V_v)-dim(V_u). Prices may have either sign.

**Theorem.** This exact optimization problem reduces to maximum-weight closure
on at most 2N Boolean nodes, at most 4E nesting implications, and at most 2N
fixed Boolean values. It has an exact polynomial-time algorithm, including
infeasibility detection for incompatible pins. No assumption on field
characteristic or on the signs of the prices is needed.

This is a dimension-linear optimization theorem. It is neither a computation
of the nonlinear P104 power invoice nor a proof of native realization.

## 1. The local options are Boolean lattices

If U subset H, the options reduce to A=U and B=U+L, with a single Boolean
choice. If L subset U, they reduce to A=U intersect H and B=U=A+L, again a
single Boolean choice. These two cases cannot overlap because L is transverse.

Otherwise dim A=dim U-1, P=A+L has dimension dim U, and B=U+L has dimension
dim U+1. U and P are distinct: equality would put L in U. Their intersection
is A and their sum is B. Thus the four options form a Boolean diamond, with
atoms U and P above A. Label these atoms J_1,J_2. A subset S of the two atoms
represents the sum of A and the selected atoms, and

    dim V(S) = dim A + |S|.

The single-choice case has one atom J_1=B and the same formula. Each local
lattice is therefore represented by one or two independent bits. Inclusion
within this lattice is exactly subset inclusion of those bit sets.

## 2. Nesting becomes implications

For an original nested edge u -> v, A_u subset A_v and B_u subset B_v. For
an atom J_a at u, consider the allowed options at v that contain J_a. This
set is nonempty because B_v contains J_a. It is closed under intersection,
so has a unique least member, represented by some bit set R(a).

Require x_(u,a) <= x_(v,b) for each b in R(a). There are at most four such
implications per edge. Equivalently, b lies in R(a) exactly when J_a is not
contained in the option at v with every bit except b set. This gives an
explicit construction using only subspace containment tests.

These implications are necessary for V_u subset V_v. They are sufficient
because A_u subset A_v, and V_u is spanned by A_u and its selected atoms.
Every selected atom then lies in V_v. This proves exact equivalence, including
edges with equal endpoints. Pinning an option fixes its one or two bits.

## 3. The objective and cut construction

Collect all vertex and edge coefficients into rational numbers alpha_v and
a constant C. In particular, an edge coefficient beta adds beta to alpha_v
and subtracts beta from alpha_u. The objective becomes

    C + sum_v alpha_v dim A_v + sum_(v,a) alpha_v x_(v,a).

Hence it is a maximum-weight closed-set problem. Multiply by a common positive
denominator for an integer network. For a bit of positive weight w, add a
source arc of capacity w. For a bit of negative weight, add a sink arc of
capacity -w. Each implication gets capacity M, where M=1+sum |w|. Forced-one
bits get source arcs of capacity M and forced-zero bits get sink arcs of
capacity M. The source side of a cut is the selected bit set.

First propagate forced-one bits along implication paths. Reaching a forced-zero
bit certifies infeasibility. Otherwise the propagated set itself is feasible.
A feasible cut has capacity at most sum |w|. Thus every minimum cut avoids
all M-capacity arcs. If W_plus is the sum of positive weights, its weight is
W_plus minus the cut capacity. Restoring the constant gives the exact optimum.
Standard exact max-flow algorithms give polynomial time; rational denominator
clearing has polynomial bit length in the encoded input size. Subspace basis
and containment operations have their usual field-arithmetic cost. This is
not an assertion of polynomial bit cost over an unspecified encoded field.

## 4. Mixed choices can strictly improve both one-sided optima

Over F_2^3 let H=<e1,e2>, L=<e3>, U=<e1+e3> and W=<e1+e3,e2>.
There is one nesting edge U -> W. Maximize dim(W')-dim(U').
The original value is 1. Growth-only choices U or U+L, and W or W+L, have
maximum 2. Shrink-only choices U or U intersect H, and W or W intersect H,
also have maximum 2. The mixed choices U'=0 and W'=V give 3. Thus separate
one-sided optima do not bound this mixed family, even on a single nested edge.
This illustrates the optimization distinction; it is not a supplier invoice.

## 5. Two explicit limits on extension

**Positive rank need not define a closure family.** In F_2^3 take H=<e1,e2>,
L=<e3>, U=<e1> and W=<e1,e2+e3>.
The strict-nesting choices (U,W) and (U,U+L) are both allowed. Their componentwise
intersection is (U,U), which has zero gap. Every family of implication-closed
bit assignments, including auxiliary bits and pins, is closed under intersection
and union, and projection preserves these operations. Consequently exact strict
gap feasibility in this representation cannot always be expressed by implications,
even after adding auxiliary Boolean variables. This does not exclude richer
optimization methods or another encoding that does not preserve these operations.

**A power price is not dimension-linear.** For 0<t<1, h(r)=r^t satisfies
h(0)+h(2)<2h(1). Use the same U,W,H,L as the strict-gap example. At the lower
vertex choose U or U+L. At the upper vertex choose U+L or W+L. These are
allowed options; all four pairs are nested, with gaps 1,2,0,1 in that order.
The lower choice varies its one bit. The upper choice fixes the projected
atom and varies its other bit. A linear bit objective must have zero mixed
difference. This table instead has 2h(1)-h(0)-h(2)>0. Thus the linear reduction
cannot silently substitute the nonlinear power invoice.

## Sources, scope and obligations

ToikY PR #7459 at 4f3dc4a40e2a3bee5fc0d6d5dfd7e4e95614fc22 poses mixed growth
and demotion as an untested direction after its common-hyperplane screen.
Its one-sided numerical bound and its #7456/#7454/#7334/#7113 lineage are
credited premises about that work, not replayed or used to prove this theorem.
This proof uses no predecessor executable, invoice, construction or receipt.
David Ganz / Dugongue's merged PR #556 already optimizes binary U/P(U)
frame choices for one oblique projection over F_2, with monotone nonlinear
paid edge prices. It is background on earlier frame cuts. That option family
is different from this four-option lattice and is not generalized here to
nonlinear signed prices. No part of its numerical search is replayed.
The maximum-closure reduction is classical; no literature-wide priority is
claimed. The explicit local lattice and scope examples are the contribution.

The theorem fixes one transverse line/hyperplane pair, a nesting graph and
linear rank prices. It does not cover arbitrary independent recharts, strict
gap constraints, nonlinear recursive powers or physical execution. A P104
application still needs a current complete edge inventory, scalar/native
legality, positive productive ranks, endpoint contracts, ownership, dirty
restoration, precision, stock and full fees. No new kappa, admitted supplier,
selected-frontier change or complete multiplication theorem is claimed.
