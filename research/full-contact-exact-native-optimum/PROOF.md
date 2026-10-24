# Ghost ranks at the fixed-source face of the original relaxation

This is a written argument about the original PR5016 marginal/rank-selector
model, together with a finite source-bound certificate. It does not establish
the full-contact native optimum, a global integer/LP optimum gap, or a defect in
the original binary MIP. A stronger pair-consistent LP is outside this result.

## 1. Exact formulation

For every flexible vertex v, the original model enumerates all subspaces
L_v <= V <= H_v, with one-hot variables x[v,V]. Its mapped edge a -> b with
invertible map M imposes, for each A, x[a,A] <= sum_{B containing M A} x[b,B]
when that allowed set is not the whole target domain. For every flexible-to-
flexible edge e it separately creates one-hot rank variables y[e,r], where r
ranges over dimensions dim B - dim A of allowed pairs. Its remaining row is

    sum_B dim(B) x[b,B] - sum_A dim(A) x[a,A] = sum_r r y[e,r].

Every column has bounds [0,1]. The original MIP requires every column integral.
We study the continuous relaxation obtained by removing only this integrality.
For integral x and y the containment and dimension rows force the actual edge
rank. For fractional y they constrain only its first moment.

The objective maximizes discount d_t(r)=r-r^t, with d_t(0)=0 and 0<t<1.
Rigid edges and eight owned rank-eight operations are included unchanged. The
original floating coefficients are not used to certify our inequality.

## 2. Source-bound edge and witness

Both orientations of the frozen actual word have the edge
(a,b,M)=(9288,11432,I_9), with multiplicity one. Original frame bases are

    A = [1,4,10,16,34,64,128,256], dim A=8,
    B = [1,2,4,8,16,32,64,128,256], dim B=9.

Their actual rank difference is one. The allowed domains also contain
C=[5,11,16,35,64,128,256] at both ends, so (C,C) gives rank zero and (C,B)
gives rank two. Thus the original model includes y_0,y_1,y_2 on this edge.
All vectors here are nine-bit binary vectors; listed bases generate subspaces.

Fix every x to the actual original one-hot assignment and every other edge's y
to its original rank. Change only this edge from y_1=1 to y_0=y_2=1/2,
y_1=0. Every column remains in [0,1]. All x-only rows and all rows for other
edges are unchanged. The modified y sum is one and its mean rank is
0/2+2/2=1, so this edge's two rows also hold. Therefore the witness satisfies
EVERY row and bound of the full original continuous relaxation. It is not an
integer solution and does not describe another native schedule.

Its paid-price contribution on this edge is 2^t/2=2^(t-1), strictly less than
1 for every 0<t<1. Equivalently its discount increases by 1-2^(t-1)>0. No
floating comparison is involved. All other terms, including every owned-cell
term, are unchanged. This includes the source's t=1-15108879/5000000000.

On the face fixing all x to source values the integer model necessarily has
y_1=1 on this edge (and the actual rank on every other edge), so the witness
proves a strict continuous/integer gap ON THAT FACE. It also proves the global
continuous optimum is strictly better than the source objective. The global
integer optimum remains unknown; this does not imply a global integrality gap.

## 3. Why pair consistency removes this witness

Introduce nonnegative pair variables z[A,B] only for allowed pairs, with source
and target marginals x and rank totals y_r=sum_{dim B-dim A=r} z[A,B]. When
both x marginals are fixed one-hot at (A,B), nonnegativity and the marginal
identities force all z mass onto this single pair. Its rank is one. Consequently
y_1=1, contradicting the ghost mixture. Thus the example motivates the already
requested pair-consistent formulation; it does not refute that formulation.

## 4. Source and computational boundaries

`model.py` authenticates every declared live input. It parses the frozen
`discovery/search.py` and executes its unchanged AST statements from
`retained = verify.source()` through all column/row bounds and integrality
assignments (lines 26–135). It stops before sparse-matrix serialization and
solver execution. A data-only substitute supplies the solver constants and LP
record; no solver is imported. These are ALL mathematical constraints in that
source: later code serializes these same arrays and solves them, adding no rows.
The upstream source loader reconstructs the actual retained native word.

For backward orientation only, an explicit adapter binds that word to the
builder's hard-coded `forward` source slot and selects the backward flag in the
independent replay. No builder expression or constraint is rewritten. Each word
is separately fingerprinted; the full row matrices have different hashes.

`verify.py` checks the original and changed assignments with Fraction arithmetic
against every exported row and column bound in both orientations, and checks
that only the three named y columns change. The full census is 15,935 vertices,
1,339 flexible contacts, 4,684 domain choices, 9,276 columns, 9,432 rows and
41,952 nonzero coefficients per orientation. The retained builder also runs its
original source endpoint replay and floating warm-start check; those are
upstream consistency checks, not the basis of the exact price inequality.

Native-word and interval correctness retain their predecessor assumptions.
This certificate does not rerun their full historical suites or certify a
physical all-column/compiler/outer supplier, a new kappa, or a selected frontier.

The independent checker uses explicit sets/XOR for transported vectors and
subspace cardinality for dimension, rather than the builder's transport or
rank helpers. Each domain entry is verified to be a subspace in its interval;
distinctness and the exact sum of Gaussian binomial counts prove enumeration
completeness. It reconstructs the full constraint multiset from all graph edges
and accounts for every column exactly once. It additionally verifies the
explicit (C,C) and (C,B) allowed pairs above. Wrong total selector mass, wrong
mean rank, negative selectors, a deleted original row, and the ghost mixture
under pair consistency are rejected. The unchanged source passes pair
consistency. Direct replay compares the entire receipt with frozen RESULT.json;
`--record` emits a candidate receipt for deliberate regeneration only.

For completeness the checker also converts every stored binary floating
objective coefficient to its exact Fraction value and verifies that the witness
strictly increases that finite model's stored objective. This is a separate
finite check of the actual coefficient bits; the all-real-t statement above
comes from the analytic inequality, not from those rounded coefficients.
