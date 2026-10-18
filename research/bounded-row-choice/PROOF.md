# A sharp bounded-choice row-conditioning contract

PR2097 gives a complete-fresh-row condition and a GL_2 counterexample to
unrestricted current-row-dependent edge choice. We quantify a restricted
replacement. The following hyperplane-union and union-bound arguments are
standard finite geometry/probability; no literature-priority claim is made.
The contribution is their exact resource boundary at this source contract.

## Linear-minor family: exact optimum in every dimension

Let q be a finite-field order, m>=2, and G uniform in GL_m(F_q). For each nonzero
normal v, the candidate edge is bad when the first row u of G satisfies u.v=0.
Proportional normals define the same candidate. Fix at most M>=1 candidates
before inspecting G. A deterministic selector may inspect G and choose one
candidate, retaining the identity row route and exact row restoration.

The maximal bad fraction over all such families and selectors is

    [q^(m-2) (1+M(q-1)) - 1] / (q^m-1),   1<=M<=q+1,
    1,                                     M>=q+1.

This is a statement about one linear-minor family, not the complete collection
of selected higher-rank bad-minor varieties. For M=1 it is
(q^(m-1)-1)/(q^m-1); 1/(q+1) is its m=2 specialization only.

Every nonzero first row has the same number
product(j=1..m-1)(q^m-q^j) of invertible completions: after choosing j independent
rows, the next row may be any vector outside their q^j-element span. Thus first
rows are uniform over F_q^m minus zero, regardless of the selector's access to
the other matrix entries.

The selector can fail only on the union of its candidate hyperplanes. Conversely
it can choose the first containing hyperplane whenever one exists, and choose
the first candidate otherwise. This deterministic selector attains that union.

For M distinct hyperplanes, the first has q^(m-1) points. Every later hyperplane
intersects the first in q^(m-2) points and therefore adds at most
q^(m-1)-q^(m-2) points to the preceding union. The union has at most

    q^(m-2) (1+M(q-1))

points including zero. Deleting zero and dividing by q^m-1 proves the bound.
Duplicates cannot improve it. No assertion about all pair intersections being
disjoint is used.

For equality choose the normals (1,a,0,...,0), a in F_q, together with
(0,1,0,...,0). They form a projective pencil. Any two hyperplanes meet exactly
in K={u:u_1=u_2=0}. Outside K their contributions are disjoint, each of size
q^(m-1)-q^(m-2). Any M<=q+1 attain the formula. All q+1 cover the whole space:
any nonzero pair (u_1,u_2) has one projective kernel normal, while K is in every
hyperplane. Extra candidate budget does not raise a probability above one.
This proves all m,q,M; finite enumeration only corroborates it.

## General candidate sets and conditional histories

On any finite uniform domain Omega, suppose each of M fixed candidate bad sets
B_j has fraction at most beta. For every selector h:Omega->{1,...,M},

    Pr[x in B_(h(x))] <= Pr[x in union B_j] <= min(1,M*beta).

This bound does not require independence or equally likely header outputs.
Individual header fibers may be entirely bad; it is a bound before conditioning
on that current-field header. If each fixed branch has a genuine permutation
route, use its inverse image of the bad set as B_j. A different current-dependent
route with no fixed-branch bijection proof does not inherit the premise.

The same argument holds separately on each complete fresh invocation domain
conditional on its ancestors, provided all M candidate sets obey the bound on
that domain. A fixed-width b-bit transcript has at most M=2^b possible values.
ALL current-field-dependent branch, coefficient, route, guard and stopping
choices relevant to that edge must be functions of this declared transcript.
The number of individual queries is not a substitute for the number of possible
full histories. Prefix-dependent ancestor information can be fixed before this
analysis; undeclared private current-field information cannot.

This is an information-cardinality condition, not a free header or a physical
selector construction. It grants no unpriced decision, preparation, routing,
copying or storage. For several fixed charged edge positions with nonnegative
input-independent weights, linearity sums their individual bounds. A branch may
not silently select larger weights, more positions, or different failed-child
costs; such changes need their own maximum/complete invoice. No recursive
admission follows solely from this one-domain counting statement.

## The selected sufficient allowance, without a new supplier claim

The retained selected ordinary BIT source uses m=64, an eligible odd prime
q>2^80 avoiding its fixed denominators and rank witnesses, and per-fixed-edge
bad fraction at most 2m^3/q=2^19/q. PR2097 authenticates the selected PR589/1087
source binding and the retained allowance 10^-16. We reuse its unchanged
authentication, selected constants and GL2 witness, and independently check
the new counting formulas. We do not reprove that inherited polynomial bound.

If a proposed adaptation supplies at most seven fixed-width current-field
bits, and every one of its candidate edges separately satisfies the SAME
eligible-prime bad-set bound on the fresh domain, then

    2^7 * 2^19/q < 2^-54 < 10^-16.

Its per-edge bad-fraction term therefore fits the existing numerical allowance.
This does not remove the selector cost or prove good-path rank, endpoint,
hosting, full-program history, field eligibility or recursion contracts. The
fixed candidate family must be covered by the stated eligible-prime assumption;
new denominators/rank witnesses cannot be introduced for free.

For eight bits the coarse q>2^80 argument only yields a cap of 2^-53, which is
greater than 10^-16. This is failure of this sufficient worst-q guard, not an
eight-bit impossibility, necessary threshold, or exhibited selected failure.
Larger eligible q or better actual candidate intersections can admit more choices.
The exact pencil theorem concerns a smaller linear-minor family and is not
silently substituted for the selected full-degree bound. No stock coefficient,
moment root, selected program or kappa changes.

## Countermodels and evidence boundary

The controls separate one fixed edge from adaptive choice; intersecting
hyperplanes from a false disjoint count; GL2 from higher dimensions; nonzero
uniform rows from all rows; declared headers from hidden kernel selection;
unconditional bounds from entirely bad header fibers; and a complete fresh
domain from a restricted single bad row. The 7/8-bit guard is checked exactly
with rational arithmetic. The source's identity route/restored endpoint does
not prevent any of these selection-conditioning failures.

The verifier independently enumerates projective normal sets, their actual
row-zero masks, deterministic selectors and literal GL2 matrices. These finite
checks do not establish a selected all-size compiler. A future adaptive caller
needs an explicit full transcript/dependency certificate and a complete charged
implementation before this local bound can enter its invoice.
