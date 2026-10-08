# Finite certificate and inherited scope

## 1. Exact change and provenance

This construction preserves PR71's anchored `[1,1,2]` split recursion,
PR65 region schedules, PR67 profile-cost reclamation and PR68 pending live
controls with next-use scoring. It composes three finite choices: PR69's
balanced coarse parenthesization, future-compatible unit completion, and a
bounded adaptation of PR70 carry exchanges. The contributor originals,
licenses and notices are retained in hash-checked archives. The published
PR71 source, words and complete arithmetic certificate are preserved at
`1bef94fd40a746452548c84a4a8f8834670a3113` for the full-profile comparison.
The new namespace is `balanced-split`. Two portable engines differ from the
independently audited discovery engines only in the repository-relative ROOT
constant; their relocation patches and SHA256s are recorded.

The h23 coarse cell uses columns when `i+j<ng-1` and rows otherwise; h25
uses rows throughout. Both dimensions use future-compatible unit completion.
Only h25 performs up to three improving carry-exchange passes, making
1,000 accepted exchanges. This is a reproducible selected finite witness,
without a global optimality claim. Each changed strategy still passes the
unchanged scalar, invertible-basis, literal physical and exact profile gates.

Credits with source PRs: @eumemic ([#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57), [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69));
@rohangar1 ([#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59));
@ikeboy ([#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62));
@DominikScholz ([#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63), [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68));
@rohanarun ([#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65), [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67));
@alejandrozu ([#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70));
@chafreaky ([#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60), [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71)).
Chafik Boukhalfa prepared this selection, adaptation and certificate with
OpenAI Codex assistance. Inherited AI disclosures and notices remain intact.

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

The balanced coarse edge groups the same Cartesian-product edge terms by
rows or columns before totaling them. Each orientation partitions those terms
into disjoint subsets, so its sum and all subsequent weighted exclusion
identities are unchanged. The half-plane rule chooses only the orientation
from fixed coarse indices. It depends on no input values. Scalar tests check
every weighted recursive block and the final dense outputs; changed
parenthesization can change intermediate exact envelopes and sharing costs.

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

Future completion leaves the independent desired-output and selected-carrier
prefix fixed. It scans all standard input unit vectors in the order of
compatible future-use count (descending), fixed symbolic support popcount,
and input index, appending a unit only if it is independent of the prefix.
The final span contains every standard unit: a rejected unit was already in
the span, and later additions cannot remove it. Thus it is the whole input
space, the number of rows equals the number of inputs, and the unchanged
Gaussian elimination yields an invertible XOR synthesis on arbitrary dirty
roles. The priority uses fixed graph incidence and symbolic signals, never
runtime data. The focused audit checks the actual priority function and
2,250 arbitrary independent-prefix completions and their literal synthesis.

The bounded carry exchange keeps the candidate set and temporal/envelope
eligibility unchanged. An occupied future use can be reassigned only after
removing its current carrier and checking independence in the new region;
a different old region only loses a row. For an unoccupied future use, one
carrier from the same region is removed and independence is checked with
that row omitted. Both cases preserve carrier cardinality and unique use
assignment. A fixed exact integer profile score strictly decreases on every
accepted exchange, and at most three passes are made. Final cardinality and
independence assertions remain mandatory. Five targeted cases and 800 random
linear/partition matroid cases audit every actual accepted exchange. The
heuristic score does not establish moment improvement; the freshly generated
physical word, complete paid profile and exact recurrence do that.

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
R23=27,297 and R25=35,684. With vh=binom(h,3),

    W = 2N + (N/v23) R23 + (N/v25) R25 = 134,126,064.

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
    Σt t nt = mW − N + L = 77,120,639,900,
    mW − Σt t nt = 1,846,900.

Every child has 0<t≤529<m. The complete multiset is constructed from the
two serialized words and appears in `balanced-split-kappa.json`. The data
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

The accepted s=51748303221339/10^18 has M(s)<1. The lower enclosure
at s+10^-18 is greater than one. An independent atanh logarithm expansion
using base 3/2 and 60 terms, a degree-12 exponential expansion, and a separate
tail bound confirms both strict signs. The full pinned PR71 child list has
lower moment greater than one at this new s; the comparison therefore uses
the complete prior network rather than selected auxiliary role counts.

The selected width satisfies `2^26 < W=134126064 < 2^27`, so the bit-wire
field changes from 28 to 27. Recompute the row coefficient from the bit and
complex branch halving degrees and wire bits: it is 843. With row degree
2000, the degree gap is `2000-(51/25)*843=7007/25` and suffix slope is 8000.
All five fields are checked against the reconstructed bridge; independent
negative controls reject a stale or changed value in each. The complex branch,
its recovery data, and the inherited directed arithmetic routines are unchanged.

The inherited balanced assembly uses backoff h0=10^-12 and the unchanged
complex saving 717/10^7. It checks all 47 strict inequalities and all seven
exponent margins for

    κ = 25872812736433/500000000000000000.

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
