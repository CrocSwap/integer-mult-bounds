# A finite nearest-Clifford obstruction on the round-three contact graph

Cinna Davis / 1337isnot1337, with substantial OpenAI Codex assistance.
Apache-2.0. This is a written finite argument with executable certificates,
not a formal-kernel or independent human acceptance claim.

## Object and tariff

The input is Cao Yifan's frozen PR4610 round-three word retained by
`research/general-gaussian-contact-search/inputs/round3-word.json.gz`.
The exact commit, blob and SHA256 provenance are in SOURCES.json and the
predecessor package. Its forward contact graph has 19,197 actual chart nodes.
It includes every formerly zero transition, every native warp, both endpoints
of each of 408 distinct arbitrary helpers, and eight paid rank-eight centers.
The scalar order, coefficients, logical native maps and main ABI are fixed.
Owned, main and explicit adapter gauges remain frozen.

We use the inverse-chart convention of Dugongue's PR4654. A Clifford gauge
F has chart L=F^{-1}L0, a Lagrangian in the 18-dimensional binary symplectic
space. For charts A,B the Fourier rank of the physical transition is

    d(A,B) = 9 - dim(A intersect B) = rank(stack(A,B)) - 9.

A native logical warp K with binary action S instead costs d(SA,B).
The helper's complete productive rank is the same distance between its
entrance and exit charts. No dimension difference is substituted for this
distance outside nested canonical charts. These are the predecessor's
Gaussian rank tariff and source all-column ABI premises; this package does
not re-prove their full native or all-size supplier theorem.

Each scalar contact has one common actual gauge for its operands. Different
contacts may use independent Clifford gauges, including different subspaces
and symmetric forms. Gauge telescoping explains why such a change is a
valid geometric candidate; a favorable candidate would still require its
actual phase/adapter implementation, native replay and downstream admission.
There is no favorable candidate here.

## Two explicitly different move domains

The first domain contracts original zero-rank identity transitions. All nodes
of such a component are constrained to have the same changed chart. The
component is frozen if any member is frozen. This leaves 1,075 groups, of
which 800 can move, and 3,938 charged edge/helper incidences. A move can thus
change many original contacts together, while preserving those particular
zero edges. Warps are not contracted or presumed free after a change.

The second domain contracts nothing. There are 18,240 unfrozen chart nodes.
A move changes one node and prices every affected edge, including transitions
that were originally free. These two finite domains do not exhaust joint
independent assignments of all charts. Contraction constrains equal charts;
it is not an assertion that zero edges must stay free in every construction.

## Complete nearest-chart alphabet

Let L be an n-dimensional Lagrangian over F2. A nonzero functional alpha on
L determines the hyperplane K=ker(alpha). In the two-dimensional symplectic
quotient K-perp/K there are exactly three lines. One is L/K; the other two
give exactly two Lagrangians L' with L intersect L'=K. Thus every L has

    2*(2^n-1)

distinct neighbors at distance one. For n=9 this is 1,022.

Choose w whose pairing with L is alpha and v in L with alpha(v)=1.
The transvections T_w and T_(w+v) send L to the two neighbors: their new
lines are represented by v+w and w, respectively. Every such transvection
is the binary action of a Hermitian Pauli quarter turn. The choice of w
modulo K does not change either neighbor. The enumerator solves the pairing
equations exactly and emits these two representatives for each alpha.
The independent Python checker also enumerates all nonzero Pauli axes on
every Lagrangian in dimensions 1,2,3 and compares the full neighbor sets.
Literal Clifford circuits check independent axes at the two ends and their
sequential composition in dimensions 1,2. These checks support the algebraic
conventions; they are not a materialized nine-axis native supplier.

## Exact exhaustive rank certificate

For each baseline node/group, enumerate every neighbor, keeping all other
charts fixed. Independently recompute every incident paid, native-warp and
helper rank. Reject loss of strict helper productivity. Both censuses have
zero rejected moves. With delta_r denoting the change in paid multiplicity
minus helper multiplicity at rank r, the local energy is

    E(C) = sum_(r=1)^9 delta_r * r^(1-C).

Main outputs and controller charges are fixed, so a larger complete
target-minus-paid moment would require E(C)<0. Rank-zero instructions have
zero cost and are omitted from this polynomial.

The contracted domain has 817,600 moves and 417 distinct signed polynomials.
The uncontracted domain has 18,641,280 moves and 157 polynomials. Their
multiplicities, first witnesses and graph hashes are committed in RESULT.json.
The registered replay recompiles and reruns both complete censuses; it does
not trust a saved floating objective or merely inspect the frozen histogram.
For every polynomial bucket, Python independently reconstructs the witness
chart and its entire affected rank invoice. Bucket equality and total counts
are checked separately. Zero polynomials account for 43 and 168 moves.

## A rigorous interval of exponents

Every polynomial is nonnegative for every real C in [0,1/200]. The proof
uses two independent sufficient tests, recorded per census:

1. If sum_r delta_r min(r,k)>=0 for all k=1,...,9, discrete concave dominance
   implies sum_r delta_r f(r)>=0 for every increasing concave f with f(0)=0.
   Indeed, each such f on these integer ranks is a nonnegative combination
   of r and min(r,k). This covers 339 and 147 polynomials.
2. For each remaining polynomial, its rank mass E(0) is a nonnegative
   integer. If it is zero, outward lower bounds on E'(C)>0 on the whole
   interval prove E(C)>=0. If it is positive, direct outward bounds on E(C)
   prove positivity on each subinterval. The contracted and uncontracted
   cases require only 16 and 8 subdivisions, respectively.

`intervals.py` uses integer arithmetic with outward rounding at 128 bits.
It bounds log(r) by the positive atanh series after reduction to [1,2],
including the geometric tail. It bounds exp(C log(r)) by 18 positive terms
and twice the next term, valid because C log(r)<1/2. Reciprocal intervals
then enclose r^(1-C). Signed sums select the appropriate outward endpoints.
Derivative bounds use -delta_r r^(1-C) log(r). Sampling never supplies the
interval claim. The zero exponent-saving endpoint is handled by E(0), not
by dividing by C. No conclusion is asserted for C>1/200.

Consequently neither declared nearest-chart move domain improves this
source's complete moment anywhere from zero saving through .005. This is
a finite source-specific local obstruction. It does not prove a global
optimum of the contact graph, exclude larger joint chart changes, or bound
all controllers or multiplication algorithms.

## Exploratory composition and next premise

The optional compiled discovery also composes independent quarter turns
sequentially, instead of resetting to a common-axis binary model. The three
recorded runs perform one strict pass, 30 contracted plateau passes and
four uncontracted plateau passes. Their complete final rank invoices agree
with the starting invoice. The 1,960 accepted plateau moves found no strict
improvement. This is bounded search evidence, not an exhaustive exclusion
of plateau components or multi-contact moves. Floating comparisons decide
discovery moves only; they are not part of the exponent certificate.

A next constructive attempt must coordinate several different groups at
once, use a larger move, change scalar contacts or change the native/owned
protocol. The certificate does not authorize more unchanged single-chart
sweeps as a new kappa contribution. No selected frontier, compiler,
ordinary BIT, outer ledger or unconditional theorem is changed.
