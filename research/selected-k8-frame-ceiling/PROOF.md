# All legal frame reassignments of the selected k8 word

This is a finite-domain, quantified obstruction with an exact rational dual
certificate. It extends navinor's retained X4 frame method to the different
selected k8 seven-slot word. The finite optimization concerns every frame
assignment in the stated domain, not a sampled neighbourhood.

## 1. Fixed object and quantified domain

The decompressed word has SHA256
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
The unchanged SLOT-PINS-k8 record identifies it as the selected local word.
It has 112 source ports, 112 target ports and 480 helpers: 704 registers.
Its A, B and early-cleanup sections contain 3,451, 1,846 and 116 gates.
The retained R492 evidence file is a different predecessor and is excluded.

Fix every scalar gate, coefficient and chronological position, all start
and end frames, the eight centres and their cut, target levels, the
precondition and cleanup, and the membership/order of early cleanup.
Each of the 5,413 A/B/early-cleanup gate frames may be any subspace of F2^9.
Both operands of an ADD share that frame; a SCALE has one operand.
Frames must be nested along each register. Centres and targets have their
prescribed frames at the A/B boundary. The end-of-B frame at every register
in a low-end helper's inverse-row or dirty-column cone is contained in that
helper's fixed end frame. These are the retained auditor's necessary rules.

We allow a charged climb into the fixed A/B pins, although the native
auditor requires the preceding frame already to equal the pin. This only
enlarges the domain. Other native/physical conditions can further restrict
it and are not needed for this lower bound.

One strict dimension-d climb costs one rank-d child. The centre descents
are eight fixed rank-eight children. The given word has the paid profile

    P = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8},
    sum_r r P_r = 5586.

Let

    a_lo = 1690054109088 / 10^15,
    a_hi = 1690054109089 / 10^15,
    a_target = (21/20) a_hi.

**Theorem.** At each of a_hi and a_target, the given profile minimizes the
paid local moment over every legal frame assignment above. More precisely,
its cost attains the lower bound of the complete local-polytope relaxation.
Under the unchanged width-73, 896-family/nine-call coverage law, centre
charge 64 and idle-rank cap 51, no such frame assignment, combined with any
idle packing, can certify a primitive saving a >= a_hi. The optimum of
the favorable packing relaxation lies strictly between a_lo and a_hi.

Thus even freeing all frames leaves the established packing-ceiling upper
bound unchanged to its certified 10^-15 grid. It cannot meet the card's
5% ceiling-improvement target. This does not assert frame optimality at
every exponent or rule out a different scalar word or endpoint contract.

## 2. Complete frame intervals

Construct a directed event graph. Every register has start/end nodes and
an ordered chain through its gate nodes and applicable A/B pin. One gate
node is shared by its operand registers. Parallel register edges have
their multiplicities retained, because each register pays its own climb.

Forward propagation joins predecessor lower frames. Fixed nodes keep
their prescribed frame. Backward propagation intersects successor upper
frames and the exact cone ceilings at the last pre-tail event. Fixed
nodes again keep their prescribed frame. Induction in the respective
topological order proves that every legal assignment satisfies

    lo_g <= F_g <= hi_g.

The primary implementation obtains cone ceilings from full exact prefix
matrices. The separate implementation computes selected forward columns
and propagates inverse row covectors through inverse gates, using exact
rational arithmetic. Both obtain the same 101 register ceilings.

All subspaces of each quotient hi_g/lo_g are enumerated, then lifted.
The largest quotient dimension is three. Their complete counts are the
Gaussian-binomial sums 1, 2, 5 and 16. The independent implementation
instead enumerates closed bitset subspaces by adjoining vectors. The two
implementations agree on every lower/upper frame, domain and graph edge.

Of 5,413 gate nodes, 3,672 are forced and 1,741 are free: 1,098 have two
choices, 613 have five, and 30 have sixteen. Free gate nodes connected by
register adjacency form 135 components. Their sizes are

    117 x 1, 2 x 8, 4 x 10, 6 x 21, 3 x 90, 1 x 181,
    1 x 326, 1 x 665.

All edges incident to free nodes belong to their component's unary or
pairwise costs. Edges between forced/fixed nodes and the centre descents
are counted separately. Their sum reconstructs the complete given bill.

## 3. Local-polytope bound and exact duals

For each gate g and frame F in its complete interval, use a nonnegative
variable x(g,F). For each adjacent free pair (g,h), use y(g,h,F,G) for
every nested frame pair F <= G. Normalize each x distribution to one and
set both y marginals equal to the corresponding x distributions.

Each literal legal assignment yields a feasible zero/one point. The LP
may have additional fractional points, so its minimum is a lower bound
for the actual assignment minimum. Unary costs count edges to fixed or
forced neighbours; pair costs count their register-edge multiplicity
times the rank of the dimension jump. No common-operand edge is dropped.

Define unnormalized child weights and reduced charges

    M_d(a) = d (73/d)^a,
    C_d(a) = M_d(a) - d M_1(a),  d=2,...,9,
    C_0 = C_1 = 0.

Along every register, climb dimensions telescope from its fixed start to
its fixed end. With centre work included, every legal assignment has mass
5,586. Subtracting M_1 times this fixed mass therefore preserves all
cost comparisons. It also permits symbolic dual vectors in C_2,...,C_9.

For each component write the LP as min c.z subject to A z=b and z>=0.
The retained DUALS payload assigns each equality row a rational linear
form in those eight charges. The checkers rebuild all constraints and
verify, column by column,

    c - A^T q >= 0,
    b^T q = the given assignment's reduced cost.

The objective equality is an exact coefficient identity, independent of
any numerical approximation. There are 17,507 rows and 23,004 columns:
16,564 reduced-cost vectors vanish identically, and 6,440 have rigorously
positive value at each displayed test exponent. There are 239 distinct
reduced vectors including zero. Weak duality proves the local theorem;
the given legal assignment attains the bound.

HiGHS and sparse floating-point solves only nominated the rational
coefficients. Neither checker imports a solver or trusts its objective,
primal point, basis or OPTIMAL flag. Every nominated coefficient is
subsequently checked against the reconstructed exact constraints.

## 4. Full packing screen

The unchanged coverage law gives paid mass per call

    72 (896/9) + 64 = 7232.

Subtracting the invariant local mass leaves 1,646 idle rank units per
call. For a>=0, cost per unit of rank mass is

    (r/73)^(1-a) / r = 73^(a-1) r^(-a),

which is non-increasing in r. The strict halving guard admits at most
rank 51: 2*51^2 < 73^2, whereas rank 52 fails. Every idle histogram is
therefore at least as expensive as fractional rank-51 packing.

For the given local profile the favorable normalized bill is

    B(a) = [sum_r P_r (r/73)^(1-a)
            + (1646/51) (51/73)^(1-a)] / (896/9).

Exact interval arithmetic gives B(a_lo)<1<B(a_hi). At a_hi, every
candidate local frame bill is at least the given one by Section 3; its
idle bill is at least the displayed relaxation. Hence its whole bill is
strictly above one. The conclusion also holds if different invocations
choose different legal frames, since the per-call inequality can be
summed. Additional expenses cannot improve this lower bound.

Every actual child rank is less than 73, so its cost is increasing in a.
Failure at a_hi excludes all larger savings, without requiring a dual
certificate at every larger exponent. The given profile supplies the
lower bracket for the favorable relaxation, not a physically realizable
fractional packing. Under the retained balanced transfer the associated
planning bound is kappa < 1690054109089/1001690054109089. This is the
existing approximately 0.001687202646 ceiling, not a new exponent claim.

A simpler per-register relaxation independently permits each gate
occurrence to choose any integer dimension in its interval, dropping
agreement between operands and subspace-containment restrictions beyond
dimension monotonicity. Exact dynamic programming on each chain gives
a normalized lower bill above 1.000125724118 at a_target. Even this
weaker screen rejects 5%; the coupled duals establish the sharper bound.

## 5. Arithmetic and controls

The primary checker uses the unchanged ceiling engine's outward atanh-log
and Taylor-exp intervals. The independent checker brackets a between
adjacent 96-bit dyadic exponents, builds the required fractional powers
by repeated integer-square-root enclosures at 256-bit fixed precision,
and multiplies with outward rounding. Monotonicity in the base and in
the exponent proves the resulting bounds. The upper exponent's carry
to one is handled explicitly. Exact squaring calibrates all 72 child
square-root cases; an intentionally incorrect root oracle is rejected.

The independent checker uses 512-bit sets for frame spans and direct
column inequalities for the dual; it imports neither predecessor math
code nor the primary checker. It shares source-binding/JSON utilities
and the same candidate dual payload. This is separate implementation
evidence by the same AI-assisted author, not independent human review.

The unchanged native auditor checks both the given word and the distinct
all-upper-frame assignment on all 704 input columns in both orientations,
with the predicted bills and low-end cones. Controls reject a removed
frame option, common-gate edge, centre charge, component, overstated
dual, wrong coverage, source drift and malformed receipts. These support
the implementation; the quantified implication is the argument above.

Reordering gates, changing read sets or coefficients, new entrances or
ends, moving tail membership, shared centre work, changed coverage laws
or helper inventories, and different billing interfaces remain outside
scope. No full selected cold replay or complete multiplication theorem
is claimed.
