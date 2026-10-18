# Joint nested endpoint and frame bound

## Object and scope

The fixed selected k8 word is identified by decompressed SHA256
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
SLOT-PINS-k8 and the retained lineage reconciliation bind the R480 word to
the selected construction. It has 112 source ports, 112 target ports,
480 helpers, and 5,413 A/B/early-cleanup scalar gates.

Fix all scalar operations, coefficients and order, every entrance,
centre/cut/target interface, and early/full cleanup membership and order.
For each of the 78 originally restricted helpers q, let S_q and H_q be
its original entrance and end. Permit every new end E_q satisfying
S_q <= E_q <= H_q, where <= means subspace inclusion in F2^9. The other
402 helpers occur in full-frame cleanup and retain full ends. Every
A/B/early-cleanup gate frame may vary, subject to monotone register paths,
common frames for both operands of ADD, and the native low-end cone rules.
The centre descents remain eight rank-eight children.

The model charges climbs into fixed A/B centre and target pins; the native
auditor requires the preceding frame already equal its pin. Allowing the
charged climb enlarges the feasible set. Thus a lower bound for this
model applies to every native assignment in the stated class. The shipped
attaining assignment also passes that stronger native condition.

This changes the fixed-gate-frame premise of PR1583 and the fixed-endpoint
premise of PR1671. PR1030/1090 already supply particular contracted-end
constructions. Neither a new LP method nor first discovery of smaller
helper ends is claimed.

## Complete finite model

Each register has an ordered chain from its fixed start through shared
gate nodes and applicable A/B pins to its end. Positive edge multiplicity
counts how many registers pay the same frame transition. A strict jump
of dimension d creates that many rank-d children. End nodes for the 78
restricted helpers are variable, with their original H_q as upper cap.

Derive the exact scalar prefix P including its dirty-target compensation.
For each restricted helper q, compute

    K_q = (support of row q of P^-1)
          union (support of column q of P), excluding q.

If b(k) is register k's last pre-tail node, native admission requires
F_b(k) <= E_q for every k in K_q. Add these as zero-charge containment
edges b(k) -> E_q. They constrain frames and never create recursive work.
The helper's own condition follows from its register chain. There are
106 such edges, retained separately from the 10,222 merged paid edges.

All edges go forward in the event order. Join predecessor lower frames
in that order, and intersect successor upper frames and end caps in
reverse order; fixed nodes retain their prescribed frames. Induction
proves lo_n <= F_n <= hi_n for every feasible assignment. Enumerate every
subspace of hi_n/lo_n and lift it. The largest quotient dimension is
three; complete domain sizes are 1, 2, 5 and 16.

The resulting domains have:

- 1,741 free gates: 1,098 with two choices, 613 with five, 30 with sixteen;
- 46 free ends, each with exactly its forced rank-seven lower frame or
  its original rank-eight upper frame;
- 32 restricted ends forced to their original subspaces, and 402 full ends.

This covers the simultaneous choices; it is not an enumeration of 2^46
complete native words. Shared-node and cone constraints still apply.
Free nodes form 135 components of sizes

    117 x 1, 2 x 9, 4 x 10, 5 x 21, 1 x 23,
    3 x 90, 1 x 197, 1 x 326, 1 x 691.

An independent implementation reconstructs all bounds, domains and edges
using 512-bit subspace sets, quotient closure and inverse row covectors.
It agrees with every geometry digest and count in EXPECTED.json.

## Variable mass must be recharged

Let P_r count all local rank-r children, including centre work. A register's
climb dimensions telescope from its fixed start to its chosen end.
Consequently local mass L = sum r P_r varies with the ends. The old
fixed-mass reduction subtracting L times the rank-one price cannot be
used as a constant objective here.

Under the unchanged width-73, 896-family/nine-call coverage law, total
paid rank mass per call is

    T = 72 (896/9) + 64 = 7232.

Any decrease in local mass exposes exactly as much idle mass, T-L.
The strict halving guard permits idle rank at most 51, since
2*51^2 < 73^2 <= 2*52^2. For a>=0, cost per unit rank decreases with rank.
Every idle packing therefore costs at least fractional rank-51 packing.
Put w=896/9 and define

    h_d(a) = (d/73)^(1-a),
    Phi_d(a) = 73 [h_d(a) - (d/51) h_51(a)], d=1,...,9.

The complete favorable normalized bill is

    B_P(a) = [sum P_d h_d(a) + ((T-L)/51) h_51(a)] / w
           = [T (73/51)^a + sum P_d Phi_d(a)] / (73 w).

The first term is constant across endpoint choices. Minimizing the sum of
Phi charges therefore minimizes the *complete* relaxed bill even though
local mass varies. All local ranks are at most nine and every possible
nested contraction leaves idle mass nonnegative.

The cost of omitting this recharging is observable: for the attaining
profile below, retaining the obsolete idle mass 1,646 instead of 1,650
makes the 5% target incorrectly pass. The control checks this false
positive using exact outward bounds. Released workspace is not free work.

## Exact dual certificate and attainment

For every free node n and complete frame choice F, use a nonnegative
variable x(n,F). For every edge between free nodes, use y(n,m,F,G) for
every nested pair F<=G, with both marginals equal to the corresponding x
variables. Normalize each x distribution to one. Unary costs count edges
to fixed/forced nodes; pair costs count paid multiplicity, including zero
for the additional cone edges. Every literal legal assignment gives a
zero/one feasible LP point, so the LP minimum is a lower bound.

For each component write min c.z subject to A z=b, z>=0. DUALS.json.gz
supplies a rational linear form in Phi_1,...,Phi_9 for every used equality
row. The two checkers reconstruct all rows/columns and prove

    c - A^T q >= 0,
    b^T q = the shipped primal component cost, coefficient by coefficient.

There are 18,033 rows and 23,456 columns. Of the reduced-cost vectors,
14,927 vanish identically and 8,529 are strictly positive at each of the
two test exponents below; 443 distinct vectors occur. No solver tolerance,
status, primal float or numerical basis is acceptance evidence. HiGHS
only nominated the rational certificate and integral assignment.

The complete primal is checked against every domain and containment edge.
Together with fixed edges and centre work its profile is

    P* = {1:2400, 2:446, 3:416, 4:142, 5:82, 8:8},
    L* = 5582,  T-L* = 1650.

It contracts helpers 574,575,580,581 to rank-seven ends. The unchanged
native auditor accepts its actual annotated word on all 704 input columns
in both orientations, including arbitrary dirty helper data, frame paths,
entrances, full cleanup, endpoint maps and low-end cones. Baseline and
credited PR1090 two-end words pass the same audit. This is exact local
scalar/frame validation. Emitted native programs, phase/wrapper admission,
a new physical owner allocation and the outer invoice were not replayed.

## Certified ceiling and 5% exclusion

Set

    a_lo = 1690198050302 / 10^15,
    a_hi = 1690198050303 / 10^15,
    a_target = (21/20) (1690054109089 / 10^15).

The exact dual inequalities and primal-objective identities hold at a_hi
and a_target. At these exponents P* minimizes the complete LP relaxation.
Independent outward arithmetic proves

    B_P*(a_lo) < 1 < B_P*(a_hi),
    B_P*(a_target) > 1.

At a_hi every legal assignment has local excess cost at least P* and idle
cost at least the rank-51 relaxation. Its full bill exceeds one. Every
actual child has rank less than 73, so its cost increases with a; the
failure at a_hi excludes all larger savings. Summing the per-call bound
also permits different legal endpoint/frame assignments in different calls.

The feasible P* assignment supplies the lower bracket for the favorable
relaxation; fractional idle packing need not be realizable. Thus the best
relaxed ceiling lies strictly between a_lo and a_hi. Relative to the old
ceiling's certified lower endpoint, the ratio is less than

    563399350101 / 563351369696 < 1.0000852.

Joint nested contractions can therefore improve that ceiling by less than
0.00852%, and cannot meet the 5% gate. Under the retained balanced planning
transfer, kappa < 1690198050303/1001690198050303. This is a bound on the
stated mechanism, not a new multiplication exponent.

The theorem does not assert optimality at every exponent, classify all
attaining assignments, compare all possible helper inventories, or exclude
nonnested ends, changed entrances, scalar rewrites, reordered/changed
cleanup, shared centres or a different coverage law. The small bracketed
ceiling gain does not establish an attainable global improvement.

## Arithmetic and verification limits

The primary uses the retained outward log/exp engine. The separate checker
uses 256-bit integer-square-root intervals and 96-bit dyadic exponent
brackets, outward multiplication and an explicit carry-to-one case. Exact
square comparisons calibrate 72 rank cases; an invalid root oracle fails.
Both implementations share source/JSON utilities and certificate data, but
no frame, LP or moment mathematics. Both were written by the same
AI-assisted author; no independent human or proof-assistant review is claimed.

Finite controls additionally reject omitted frame/end choices, centre work,
common-gate edges, primal nodes, dual components, overstated objectives,
wrong idle mass/coverage, source drift and malformed JSON. They support the
implementation; the universal implication within the finite domain follows
from the complete-domain and weak-duality argument above.
