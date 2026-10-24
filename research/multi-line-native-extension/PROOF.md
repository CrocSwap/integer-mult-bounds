# A partial native map and one late capacity

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
This is a written linear-algebra proof, not proof-kernel verification.

Let V be an n-dimensional vector space over an arbitrary field, A,C subspaces,
and h:U→U′ an isomorphism between subspaces of V. All these are actual embedded
subspaces/maps, rather than dimension-only descriptors. Write

    u=dim U, a=dim A, c=dim C,
    d=dim(A∩U), k=a−d, c0=dim(C∩U′).

**Theorem.** There exists G∈GL(V) with G|U=h and G(A)⊆C if and only if

    h(A∩U)⊆C,                 k≤c−c0.                    (1)

If the field has q elements, the exact number of such G is

    q^(c0 k) ∏_(i=0)^(k−1)(q^(c−c0)−q^i)
              ∏_(i=u+k)^(n−1)(q^n−q^i).                (2)

Empty products equal one. The count is zero if (1) fails. Arbitrarily many
prescribed equations G(x_i)=y_i first define h exactly when every linear
relation among the x_i is also a relation among the y_i; h is injective exactly
when the converse holds too. Thus equality of the two relation spaces is an
additional necessary condition for a list of equations to have a GL extension.
Repeated, dependent and zero vectors must be processed, not silently discarded.

## Necessity

The first inclusion follows from G(A)⊆C and G|U=h. Choose a complement X of
A∩U in A. Its dimension is k. Since G is invertible, G(X) is disjoint from
G(U)=U′. Also G(X)⊆C. Projection π:V→V/U′ is therefore injective on G(X),
and π(C) has dimension c−c0. This proves the second inequality. In particular
the available quotient is by *all* of U′, not only by h(A∩U).

## Construction and sufficiency

Fix a basis u_1,…,u_u of U and a basis x_1,…,x_k of X. The concatenation
is a basis of U+A. Choose z_1,…,z_k in C whose images in C/(C∩U′) are
independent; (1) makes this possible. Then

    u_i ↦ h(u_i),       x_j ↦ z_j

defines an injective map on U+A. Its image of A∩U is in C by the first
condition, so its image of A is in C. Complete the source and target independent
lists to bases of V and map the added basis vectors in order. This gives G.
Gaussian elimination implements every step over the supplied field; no finite
ambient enumeration is required for the construction or theorem.

## Counting

Keep the chosen bases of U and X fixed. There are exactly

    ∏_(i=0)^(k−1)(q^(c−c0)−q^i)

ordered independent quotient images π(z_j) in π(C). Each independently has
q^c0 lifts in C. These choices are in bijection with the allowed injective
restrictions on U+A: every G determines its unique values on the fixed x_j,
and each such choice determines the restriction. Fix any basis of a complement
of U+A in V. Its ordered images can be chosen successively outside the span
of the preceding images in exactly ∏_(i=u+k)^(n−1)(q^n−q^i) ways. This proves
(2) without overcounting a choice of intermediate subspace or basis. It also
explains why replacing an inclusion G(A)⊆C by equality changes the problem
unless a=c (in which case inclusion already implies equality).

## Why separate line tests do not compose

Over F_2^3 take A=〈e3〉 and C=〈e1,e2〉. Fixing e1 alone leaves c−c0=1=k,
and yields 8 completions; fixing e2 alone also yields 8. Fixing both makes
U′=C and c−c0=0<k, so there is no completion. Testing each prelude pair
independently and conjoining those successful tests would accept a false edge.
This is a quotient-occupancy obstruction, not an inconsistency of h itself.

The other condition is independent: A=〈e1〉, C=〈e2〉, h(e1)=e1 in dimension
two passes quotient capacity (k=0) but cannot carry A into C. Likewise agreeing
only on dimensions and intersection ranks cannot replace the actual inclusion
h(A∩U)⊆C. Noninjective or inconsistent prescribed equations give additional
distinct failures before either subspace condition is evaluated.

## Exact source boundary

Cao Yifan's PR4610 `helper_line_milp.py` selects one late contact per operator;
when there are other proper contacts, it asserts that they specify one common
one-dimensional prelude pair. `constrained_map.py:line_matching_map` implements
that single-line case in binary dimension nine. The twelve affected operations
are 47 through 58. Their prelude contacts are 1→1 and their selected late
contacts are 4→4 in the frozen source word. In F_2 a nonzero line has a unique
nonzero vector, so that line contact really prescribes h(a)=b.

For one nonzero prescribed a↦b, if a∈A then d=1 and the first condition is
b∈C. When b∈C the capacity inequality becomes dim A≤dim C; this is the
source's accepted branch. If a∉A then d=0: when b∈C the inequality is
dim A<dim C, while when b∉C it is dim A≤dim C. These are exactly the source
predicate and its two branches. Empty prelude lists recover dim A≤dim C.
The new implementation treats any number of consistent prelude equations at
once and gives the previously unstated exact number of completions.

The caller adapter authenticates the frozen source files, extracts the actual
normalized positive-map contacts from both orientations, and checks each
completed matrix on every source-frame vector and every prescribed prelude
vector. It compares the literal old one-line predicate across the original
source frame catalogue. It does not execute the predecessor MILP or claim that
multiple independent prelude lines already occur in that source. Augmenting
the twelve contracts with an additional vector image from each retained map
is explicitly a stronger calibration fixture, not a changed emitted word.

This is an algebraic GL contract. No physical normalizer, absolute phase,
symplectic constraint, multiple independent late capacities, paid invoice,
precision/stock/outer theorem or new κ follows from it. Classical basis
extension supplies the method; no literature-priority claim is made. Nick
Petalas's #4919 three-subspace result and codyw912's #4735 extension argument
are related predecessors, with different prescribed-data interfaces.
