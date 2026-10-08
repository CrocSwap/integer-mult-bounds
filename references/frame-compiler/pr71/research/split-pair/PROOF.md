# Finite certificate and inherited scope

## 1. Exact change and provenance

The scalar provider starts with the preserved PR62 interval-strip/core-aware
pair graph as carried by PR65 at
`49e84f939d15b618b50714eb039cabf97c74256a`. It changes only the group partition
and point permutation. The compiled region orders are PR65's `cover-core`
for h=23 and `reverse-node` for h=25. The reclamation engine composes PR67's
all-rank profile-cost selection with PR68's pending live-carrier lifecycle and
both frame-containment tests, then scores pending controls against their
known next-use frame. Its exact diff from the original PR67 engine is
preserved in `engine-changes.patch`. The inherited PR60 engine, independent
word/profile tools and refined arithmetic remain byte-identical archived
dependencies. The configuration, compiler records, literal words, transition
records and profiles belong to this package's separate `split-pair` namespace.

PR59's split operation, PR62/63's pair graph, PR65's scheduling and arithmetic,
PR67's cost selection, PR68's pending controls, PR60's ranked reclamation and
PR57's reversible compiler have different
authors. The source archive and NOTICE retain that provenance. No optimality
assertion in an inherited discovery discussion is used in this certificate.

## 2. Ordered partition, contraction, and weighted scalar identities

At recursive level d, begin with the ordinary ordered groups of size one or
two. The vector `[1,1,2]` requests the first group for d=0,1 and the middle
group for d=2. A selected two-point group is replaced by its two singleton
groups, and no point is lost, repeated, or reordered. A singleton is left
alone. At later levels no split is requested. Splitting is permitted only
when the number n of points is greater than three.

For n≥4, the resulting number of groups is at most ceil(n/2)+1≤n−1. For n=3
the unchanged grouping has two groups. Blocks of size at most two use the
inherited direct base case. Thus every recursive call has fewer points and
the recursion terminates. This is a general contraction argument, not an
inference from the two finite compilation runs.

The recursion accepts disjoint weighted vertices and edges. Between two
coarse groups, its coarse edge is the sum of all original edges between them.
A coarse vertex weight contains every old vertex weight in its group and
every internal edge of that group. These terms partition the original
weighted total. By induction, recursive totals and all single/pair exclusions
therefore have exactly the intended supports.

When both groups contain two points, the preserved four-output assembly
combines their common distant total, the appropriate two strips, and the
remaining cross edge. Each sum uses disjoint supports. With a singleton
group, the inherited generic decomposition supplies the corresponding sum.
The specialized four-output identity is never called on an invalid group
shape. Interval strips provide the sum omitting each designated strip value;
their supports follow from the cyclic-interval recurrence. The provider's
scalar verification checks all final exclusions, disjoint additions, and the
common-point condition. The focused tests additionally check the weighted
identity at every recursive block and verify strict partition contraction.

## 3. Aligned common-point permutations

For common point c, take the inherited alternating permutation of all points
other than c. Among fixed global pairs (0,1), (2,3), … disjoint from c, choose
the lexicographically first pair. Move those two points to the front, in their
pair order, leaving the other points in their previous relative order. There
is always an intact pair for h=23,25. The resulting list is a permutation of
exactly the points other than c.

Relabeling a scalar exclusion circuit by a permutation preserves its total
and exclusion identities. Applying that relabeling separately at each common
point preserves the intended full triple-input map. The first split pair is
now aligned across copies whenever the selected intact pair agrees. This can
change the shared addition DAG and physical cost without changing the linear
map. Dense scalar outputs and exact supports are checked in both dimensions.

## 4. Actual schedules and physical reversibility

The PR65 wrapper sorts regions by `(rank, cover, core)` for h=23 and
`(rank, -minimum_node)` for h=25. It changes only their execution order.
Before compilation, every incoming dependency is required to precede its
consumer and every carrier candidate is required to go to a later region.
No backward candidate or dependency is admitted.

Within each region, the inherited reversible synthesis completes the desired outputs
and retained carriers to a full independent physical basis, synthesizes an
invertible XOR transformation, and reclaims retired roles only when frame
containment and signal-span checks permit it. All clearing XORs are literal
operations in the word.

The pending map records the already assigned next-use region of each live
physical role. Incoming roles are removed from this map on entering their
assigned region. A retained carrier or outgoing copy receives its next-use
entry when assigned. A live role in frame F with next-use frame G is eligible
as a clearing control in frame E only when F⊆E⊆G. Its inclusion in a
compile-time elimination basis does not itself perform an operation. If a
selected literal clearing expression uses it, the role is an XOR control,
so its value is unchanged. Its charged frame raise F→E remains compatible
with its later raise E→G. Repeated uses recheck the then-current frames.

PR67 enumerates eligible dependent retired roles and records their literal
clearing expressions without mutating any physical role while comparing
candidates. A stored expression therefore remains valid. Its integer score
uses the fixed-basis transition profile with weights
floor(t·midpoint(log(t))·10^30), with exact rational log enclosures. For a role
currently in frame F, promoted to E, and cleaned up at G, the score is

    H(F→G) − H(F→E) − H(E→G).

The new rule uses a pending role's already known next-use frame as G; for
other roles G remains the full-space cleanup endpoint. This changes only the
heuristic ordering of valid expressions. Eligibility, the full invertible
basis construction, containment checks and literal charging remain required.
There is no use of runtime data to choose a word and no claim that the score
optimizes the final moment.

Full-basis replay checks both orientations on every
ordinary input and every dirty scratch basis column; scratch is arbitrary,
not an uncharged supply of zeros. Final outputs, copied centers and distinct
terminal roles are checked. The frame checker reconstructs every raise from
the literal word and requires equality to the recorded transitions.

The fixed-I+J profiler consumes those actual transitions. It uses the pinned
bounded-minor bound and CRT moduli, checks their sufficient product, and
requires agreement. Every resulting profile is recomputed and compared.
Mutation tests reject missing operations, invalid frames, aliased terminals,
missing centers, missing transitions and understated physical width.

## 5. Complete paid recursive profile

Put a=23, b=25, m=ab=575, and
N=binom(23,3)binom(25,3)=4,073,300. The verified auxiliary role counts are
R23=27,455 and R25=36,015. With vh=binom(h,3),

    W = 2N + (N/v23) R23 + (N/v25) R25 = 135,075,665.

Every part of the recursive child multiset is included:

| Source | Multiplicities |
|---|---|
| Two data orientations | 18N children of rank 1; 2N each of ranks 21,17,481 |
| Endpoint copy | N children of rank 1 |
| Axis h internal profiles | (N/vh) times every nonzero entry of its actual profile |
| Axis h exterior | (N/vh)Rh children at each rank h and m−2h |
| Axis h data growth | 2N children at each rank 1 and h−2 |

Each axis profile satisfies sum(t·blocks[t])=hRh+h(h−1), has no omitted
positive multiplicity, and contains no rank-zero child. Consequently

    L = Σh (N/vh) h(h−1) = 2,226,400,
    Σt t nt = mW − N + L = 77,666,660,475,
    mW − Σt t nt = 1,846,900.

Every child has 0<t≤529<m. The complete multiset is constructed from the
two serialized words and appears in `split-pair-kappa.json`. The data
geometry, ten exact rational recoveries, and complex branch are unchanged.

## 6. Directed arithmetic and strict balanced assembly

For bit saving s, the recurrence moment is

    M(s) = Σt nt · t/(mW) · exp(s log(m/t)).

The pinned logarithm helper encloses each logarithm rationally. For
0≤u≤s log(m/t)≤v<1, the degree-eight Taylor sum S8(u) is a lower bound.
The first omitted term at v is v^9/9!, and every subsequent ratio is at
most v/10. Hence S8(v)+(v^9/9!)/(1−v/10) is an upper bound. Directed
rounding at denominator 10^40 preserves both inequalities. This is PR65's
unchanged exact enclosure, not floating-point evaluation.

The accepted s=12854322426487/250000000000000000 has M(s)<1. The lower enclosure
at s+10^-18 is greater than one. An independent atanh logarithm expansion
using base 3/2 and 60 terms, a degree-12 exponential expansion, and a separate
tail bound confirms both strict signs. The full pinned PR67 child list has
lower moment greater than one at this new s; the comparison therefore uses
the complete prior network rather than selected auxiliary role counts.

The inherited balanced assembly uses backoff h0=10^-12 and the unchanged
complex saving 717/10^7. It checks all 47 strict inequalities and all seven
exponent margins for

    κ = 51414646104039/10^18.

The next κ grid point is rejected by a controlling strict margin. A coarser
10^11 grid is reassembled as a precision control, and its moment also passes
the original enclosure. Negative tests reject zero backoff, the old guard,
the original prefix, and the old exposure accounting. Eventual arithmetic
cutoffs are recomputed with the same inherited routine.

## 7. What this does and does not prove

This is a reproducible finite conditional witness. Its scalar identities,
physical reversibility on arbitrary dirty inputs, literal frame costs,
fixed-basis profiles, complete recursive multiset, exact strict moment and
balanced inequalities are checked. The general ordered affine-residual
compiler, all-size recursive construction, finite scalar alphabet and cost
overhead, routing, prime selection, exact recovery, fixed-tape simulation and
analytic transfer remain inherited dependencies. A finite word does not by
itself formalize those all-size statements.

Arithmetic cutoff output addresses the listed arithmetic inequalities only;
other inherited eventual thresholds remain required. No full multiplication
implementation, measured practical speedup, global optimum, new formalized
all-size theorem, or removal of the inherited hypotheses is asserted.
