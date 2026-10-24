# Every retained center still costs rank eight

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## Exact model

Work in the nine-dimensional binary chart space of Cao Yifan's PR4610 word.
Keep the scalar order, coefficients, field references, logical warp maps,
main endpoints and explicit adapter boundaries. Each scalar operation must
still use a common chart on its operands. Persistent transports keep their
original ascending orientation; zero-length positions may acquire an
ascending transport. A logical warp G remains monomial and maps its entire
new input space to its new output space. All helper boundaries are free.

Keep the owned center protocol: clear/copy or gather, one complete Gaussian
center call at the retained position, scatter or copy back, then erase.
There is no added center transport between its scalar contacts. Thus its
live chart between these contacts is common. Its zero reset has no chart
constraint until its first nonzero use. Both center endpoint charts may
change. No source center chart is fixed by hand.

All charts can be arbitrary subspaces of F_2^9. They need not be one-axis
edits, superspaces or subspaces of the submitted charts. This is not a
search over 511 directions or a local optimum statement. Descending
persistent moves, additional center calls, new scalar circuits, changed
logical maps or boundary contracts, enlarged ambient spaces and maps
between digit columns are outside the model.

## Inclusion graph

Give every chart boundary and scalar contact a node n with unknown
subspace V_n. A main endpoint or explicit adapter has its original fixed
space. Other nodes, including every helper endpoint and every center
contact, are unconstrained initially.

An ascending persistent transport from a to b imposes V_a subset V_b.
The two endpoints of a center call are initially unrelated: the closure
adds **no inclusion arc for that call**. This deliberately relaxes its
implementation contract. A common scalar contact shares one node. Persistent arrival at that contact
imposes inclusion, permitting a newly paid ascending step. Nonzero owned
center state has no intervening transport, so its consecutive contact
nodes are equal. A cleared zero state imposes no previous chart relation.

A logical warp imposes G V_a = V_b. Encode this with both directed
inclusions G V_a subset V_b and G^-1 V_b subset V_a. Warps are not frozen
to their old charts. Every constraint is of the form

    A V_a subset V_b,

where A is an invertible binary map or the identity. The original word
is checked as a feasible assignment of the whole graph, including all
scalar contacts, all warp maps and both complete paid profiles.

## Universal lower and upper spaces

Initialize lower spaces L_n to {0}, except that a fixed node has its
fixed space. For each arc A V_a subset V_b, repeatedly replace

    L_b <- span(L_b union A L_a).

For every feasible assignment, induction gives L_n subset V_n. Each
replacement is a necessary consequence of one actual inclusion. The
process terminates: every strict replacement raises one finite binary
subspace dimension. At a fixed point the lower assignment itself obeys
all graph inclusions and fixed spaces, so it is the least assignment.
The verifier uses actual XOR span; set union alone would be incorrect.

Initialize upper spaces U_n to F_2^9, except at fixed nodes. Repeatedly
apply the reverse implication

    U_a <- U_a intersection A^-1 U_b.

For every feasible assignment V_n subset U_n, again by induction. Each
strict update decreases dimension. Its fixed point is the greatest
assignment. Neither calculation assumes that different chart choices are
independent. Equalities, scalar sharing and warp maps propagate globally.
Original feasibility guarantees that no propagated bound contradicts a
fixed boundary. The implementation checks every final inclusion as well
as containment of the submitted assignment inside the interval.

## Result on the actual centers

For both the forward and backward word, each of the eight center calls
has its originally lower/higher endpoints lo,hi satisfying

    U_lo = {0},       dim(L_hi) = 8.

Thus **every** feasible reassignment has V_lo={0} and dim(V_hi)>=8.
The nesting and direction for the center follow from the bound, although
neither was imposed on its unknown endpoint spaces in the closure.
Its Gaussian rank is at least eight, and the eight calls together retain
at least 64 units of paid rank mass. For 0<t<=1 their paid moment is at
least 8*8^t; at t=0 all eight positive calls remain paid. Any phase forms
within a grammar where nested Fourier rank is at least the dimension
difference cannot lower this bound.

The verifier checks the original eight rank-eight calls, so the floor is
attained in this model. This proves a center-bill floor, not optimality
of the other paid calls or the full native word. A different paid shape
with the same center bill could still improve K. The conclusion also does
not price a redesigned center protocol with multiple calls or shared data.

## Evidence boundary and credit

The bound is a finite exact structural theorem about the source's binary
chart model. It is not a new native construction or multiplication exponent.
Native/absolute-phase, all-column, ownership, compiler, precision, tape and
outer hypotheses are not re-proved. There is no Lean or independent human
proof review. Both queue orders and a change of every frame basis produce
the same center intervals; three actual source mutations are rejected.

Credit Cao Yifan/PR4610 for the source word; Dugongue/PR4654 for the broader
chart and phase question; Cinna Davis/PR4665 and PR4696 for phase barriers;
Cinna Davis/PR4470, zxv, Jacob Alan Sussman and the retained native, helper
and compiler contributors. The source blob is retained exactly with its
original commit/path provenance. No predecessor package is copied.
