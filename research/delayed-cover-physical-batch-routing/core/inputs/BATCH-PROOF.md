# Whole-high-matrix allocation lemma

## Source contract and new implication

Fix one final compiled BIT template, with B>=2 productive roles, C private
roles, ambient dimension N, and an eligible fixed odd prime q. B,C,N,q are
constants chosen before the multiplication input. This is the final template
contract in `DELAYED-COVER-BRIDGE.md`, Sections 7 and 8. It is not the historical
PR589 raw inventory or the numerical example in `three-stage-cover-bit.tex`.
Private storage receives no productive credit. Its allocation and erasure costs
remain part of the local machine obligation.

Fix atom width w>=1 for one stopped recursion, as in the source recurrence
T(n,w). Put G=|GL_N(F_q)|, H=q^(N*N*(w-1)), L=B*G and W=L*H.
The chart g=g0+qG1 is unique. Each of the G low matrices has exactly H lifts.
A logical productive bank has a complete cover fiber. Use one stream for each
(role,g0) low type, and put G1 in its address. There are L such stream types,
independent of w. Each private role uses G streams of the same shape.

The source already states that all high matrices are batched and that the
volume divisor is the fixed low-type count. The fresh-fiber predecessor proves
complete cylinders and their bad-class frequencies. The new implication here
is the explicit batch address/return map which connects those statements to
the allocation theorem in PR5814. It distinguishes consumed stock from retained
batch volume at every depth. It does not claim a new cover or routing algorithm.

Assume a depth bound D and a row reserve P=T*W^D, with T>=1. A complete body
fiber of size R accompanies each row. R includes all data, atom and spectator
ranges required by the invocation. A child changes its active width by making
unused main coordinates spectators; it does not discard their ranges. The
root volume is V=P*R. One outer padding from Q>=W^D to P=ceil(Q/W^D)*W^D
has P<2Q. All padded rows must execute until the restored endpoint.

## Explicit address maps

Read the fresh row factors from least to most significant. A root row is a
slab t and D pairs (l_i,h_i), with 0<=l_i<L and 0<=h_i<H. At depth j a batch
fixes l_0,...,l_(j-1), but retains every h_0,...,h_(j-1) as an address field.
Its address can be written

`b = U*H^j + A`, where `A = sum(h_i*H^i, i<j)`.

U is the unused stock index. Divide it as

`U = U'*(L*H) + l*H + h`.

The child low type is l. Its new batch index is

`b' = (U'*H+h)*H^j + A`.

The inverse, given l and b', recovers A by division by H^j, then h by division
by H, and returns `(U'*(L*H)+l*H+h)*H^j+A`. These are inverse Euclidean-division
identities. They preserve all independent input addresses and all body fields.
They require no assumption about numerical payloads.

At depth j there are L^j low-type prefixes. Each has exactly P/L^j row
addresses, because it retains H^j ancestor high values and
T*(L*H)^(D-j) unused-stock values. Thus

`V_j = V/L^j`, and `unused_stock_j = P/(L*H)^j`.

A child has volume V_j/L, not V_j/(L*H). The latter formula discards H
independent high-matrix values. At w=1, H=1 and the formulas agree. This
boundary case explains why a low-residue-only test cannot expose the error.
Sequential siblings restore the supplied address and reuse the same unused
stock. Two completed body calls also reuse it. No per-level padding is needed.

## Routes, external weights and return

A fixed right matcher permutes (g0,G1) on the complete cover. In the current
factor of U this is a permutation of l,h which preserves the role. It fixes A,
U' and the body fields. It can move data among the fixed low-type streams;
it cannot be implemented by permuting only G1 within one low type when g0
changes. The inverse route restores the entire cover row, including carries.
The source retains the physical route cost and old interchange dependency.
The reference map does not replace that implementation.

The parent's current cover becomes exposed ancestor data at the child. Its
high coordinate stays in A instead of being fixed to one value or dropped.
Consequently a child weight may vary with A, the fixed low prefix and atom
indices. At any fixed ancestor A, it is independent of the child's fresh
l,h in U. This gives one permitted common generated weight descriptor across
all child fresh roles and cover values. Arbitrary ancestor variation is allowed.
A numerical value for each ancestor need not be stored in separate program
state: the address retains the ancestor and a permitted descriptor evaluates it.
This is the source's descriptor premise, not a new evaluator implementation.

The child returns a complete batch in the same b' order. Apply the inverse map
and inverse fixed matcher to install each output in its original parent row.
A complete arbitrary-data child endpoint then transfers pointwise. Private
child banks must be fresh, cover the same complete batch and be cleared before
return. Their exact physical machine and costs remain premises. An address
bijection alone does not prove their lifecycle.

## Space and time consequences

For each fixed template, assume the isolated local macros, descriptors, private
banks, bridges and retained backing at a node use at most K*V_j space, with K
independent of w and the input length. Include the C*G private streams in K;
each has V_j/L volume, so their data contribution is C/B times V_j. This does
not change the productive divisor L. Any precision/marker factor in the local
space contract must also be retained consistently.

Under the depth-first return discipline of PR5814, an active chain has space
at most

`K*V*sum(L^-j, j=0..D) < K*V*L/(L-1) <= 2*K*V`.

This is the correct geometric bound for whole-high batches. A false divisor
W would give a smaller bound with no justification when H>1. The parked high
fields are already included in V_j. The two completed body calls are sequential,
so they do not require two concurrent recursive reserves. Fixed child types
and low types give a finite port inventory; the count does not grow with w.
This proof does not assert that the existing 23-tape prototype already executes
the final template or that its local constant K is established.

The time bill remains the source's sum over low-type edge occurrences, with
child volume V_j/L. High-matrix cardinality cancels from the normalized bill,
but remains in the row reserve W^D and its O(w*D) digit cost. Neither a smaller
moment nor a new kappa follows. The source's fallback and all fixed right routes
remain charged. Their local time and space implementations are not set to zero.

## Evidence boundary

The written division identities and induction apply to all stated integers.
The checker compares an independently assembled coordinate product with the
reference maps over eight complete finite domains and every depth. It executes
full descent/return with independent root labels and ancestor-dependent values.
A separate GL_2(Z/9Z) census checks all 7,776 two-role rows and their actual
right-matcher inverses, including nonzero carry and spectator preservation.
The controls reject omitted high fields, reused ancestor stock, early padding
pruning, missing inverse routes, fresh-dependent weights and private credit.

The existing fresh-fiber theorem supplies predictable invocation and complete
execution conditions. This package does not prove those conditions for an
unmaterialized compiled word. The remaining admission chain is the old ordinary
BIT macro's local space, physical route/fallback implementation, the full finite
production dispatcher, and actual precision. All five project assumptions keep
their status pending complete source binding and independent review.
