# Three prescribed targets in the nonempty proper-star decoder

Let p >= 5. Label the 2p signed coordinates by 0,...,2p-1, with original
matched pairs {2i,2i+1}. A signed two-port is an unordered pair of coordinates
from different matched pairs. Equivalently, ports are the edges of the
cocktail-party graph G = K_(2p) minus those p matched edges. There are
E = 2p(p-1) ports. All symbols and observations below are over F2.

For a deleted set D of ports, the surviving symbols are arbitrary and independent.
For each vertex v the supplied nonempty proper-star observation is

    s_v = sum of x_e over surviving edges e incident to v.

Fix three distinct target edges T, all required to survive. We ask for the
smallest |D| allowing exact recovery of each of their symbols from these
observations. Coefficients may depend on D and T. The empty star (global sum)
is excluded. Permitted target overlap-one corrections add no information:
for target {a,b}, that correction is s_a + s_b, including after deletion.

**Theorem.** The exact minimum is:

- Impossible, if T is a triangle.
- 6p-11, if T consists of three sides of the four-cycle on two complete
  original matched pairs.
- 6p-12, for every other T.

This classifies prescribed targets in this graph observation model. It
makes no claim about larger k, a supplied empty star, changed geometry,
interacting observation mechanisms, or a paid multiplication supplier.

## 1. Recovery is a bridge condition

Write H = G-D. The supplied rows are its binary vertex-incidence rows.
A sum of such rows is the cut of the selected vertex set. A surviving unit
edge row belongs to their span exactly when that edge is a bridge: a
singleton cut is a bridge. When e is a bridge, either of the two pieces
into which deleting e splits its original connected component produces
the singleton cut.

Arbitrary exact nonlinear postprocessing of these same observations does
not improve this criterion. If the unit functional were outside the row
span, there would be a vector in the observation kernel on which that
functional is nonzero. Zero input and that vector have identical observations
and different target values. Conversely a row-span expression is a decoder.
In particular, any cycle wholly in T makes recovery impossible. For three
edges the only possible cycle is a triangle.

If a feasible H is disconnected, add an edge of G joining two of its
components. Such an edge exists because G is connected. It creates no
cycle, preserves all marked bridges, and reduces |D|. Consequently an
optimal H is connected. Removing its three target bridges leaves exactly
four connected vertex blocks. All other retained edges lie inside blocks;
adding all available G edges inside those blocks preserves the targets as
bridges. Thus an optimum is obtained by partitioning V(G) into four blocks,
retaining all internal edges and just the three target crossing edges. The
target edges must form a tree on the four blocks.

Conversely, any four-block partition whose target quotient is a tree gives
a feasible deletion set: every target is the only retained edge across
one quotient-tree cut. This remains true even if an induced block is
disconnected. Such partitions may be included in a finite minimum census.
Its deletion cost is the number of crossing G edges minus three.

## 2. Why three singleton blocks suffice at an optimum

For a block of s vertices, its number of internal G edges is at most

    f(s) = binom(s,2) - max(0,s-p).

Indeed it contains at least max(0,s-p) complete matched pairs. This bound
is attainable. For positive s, f(1)=0 and the increments

    f(s+1)-f(s) = s - 1[s>=p]

are nondecreasing. Concentrating vertices in a largest block therefore
maximizes the sum of f over block sizes. For four blocks the unrestricted
upper bound is f(2p-3). If the sizes are not (2p-3,1,1,1), concentration
while preserving at least two nonsingleton blocks instead gives at most
f(2p-4)+f(2). For p>=5 their difference is

    f(2p-3) - f(2p-4) - f(2) = 2p-6 >= 4.

Since E-f(2p-3)-3 = 6p-12, every partition not having three singleton
blocks costs at least 6p-12+(2p-6).

For any forest T, its vertex-incidence matrix on the three target columns
has rank three. Choose three independent vertex rows, indexed by S.
Use those three vertices as singleton blocks and put all other vertices
in the fourth block. The quotient incidence matrix has rank three, so
its three edges form a tree. This proves feasibility. If h is the number
of complete original matched pairs in S, then h is zero or one. The union
of the three singleton-star supports has size

    3(2p-2) - (3-h) = 6p-9+h.

All three target edges are in that union, so deleting its other edges
costs 6p-12+h <= 6p-11. This is strictly better than every partition
without three singleton blocks. Consequently the exact optimum is
6p-12 plus the minimum h among independent three-vertex target rows.

These arguments rederive the needed graph bound directly. The underlying
cut-code interpretation and the selectable-target minimum are predecessor
results, credited below; they are not new claims of this contribution.

## 3. Classifying the one-unit obstruction

For a three-edge forest, choosing all nonroot vertices in each nontrivial
tree component gives three independent target rows. We show when they can
be chosen without a matched pair.

**A path on four vertices.** Any three of its four vertex rows are
independent. If its four vertices contain at most one matched pair, omit
an endpoint of that pair (or any vertex if there is none). The remaining
three use distinct original pairs. If there are two complete matched
pairs, every three vertices contain a pair. Because adjacent vertices
cannot be mates, a path v1-v2-v3-v4 then has mate pairs {v1,v3} and
{v2,v4}. It is precisely three sides of the induced four-cycle on those
two pairs. Vertices outside T have zero target rows and cannot help.
Thus exactly this case has h=1 at every vertex-row basis.

**A three-leaf star.** Its center cannot be a mate of a leaf. Among three
leaves there is at most one matched pair. Choose the center and two leaves
that are not mates. These are independent rows with h=0.

**A two-edge path a-b-c and a disjoint edge d-e.** Either adjacent pair
{a,b} or {b,c} gives two independent rows for the path and is itself
mate-free. Both choices d and e are blocked as a third vertex only if
the mates of d and e are exactly that adjacent pair. Two distinct adjacent
pairs cannot both equal this fixed two-element set. Choose an unblocked
pair and one of d,e to obtain h=0 and three independent rows.

**Three disjoint edges.** On their six vertices, the target matching and
the restriction of the original mate matching form alternating paths and
even cycles. This graph is bipartite. Either color class chooses exactly
one endpoint of each target edge and never both endpoints of a mate pair.
The three chosen target rows form the identity matrix, and h=0.

These are all three-edge forests, proving the theorem.

## 4. Counts, controls and scope

There are 4 binom(p,2) exceptional triples: choose two original pairs and
one of the four edges of their cycle to omit. There are 8 binom(p,3)
triangles: choose three original pairs and one sign from each. Every
other one of binom(2p(p-1),3) target triples has cost 6p-12.

The primary finite check enumerates every four-block partition and every
automorphism orbit of target triples for p=5,6. It supplies literal
star-coefficient decoders and checks every surviving source column.
Restoring any one deleted edge destroys simultaneous recovery, as a
separate bridge check verifies. This restoration check is a minimality
control, not by itself a proof of global optimality.

The independent program optimizes over all normalized F2^3 vertex labels
whose differences on the three target edges are the three unit vectors.
Unlike the partition implementation, it permits all eight label values.
Its deletion support is every non-target edge with unequal labels. These
are precisely triples of star coefficients giving unit target rows. It
also checks witnesses by binary row-space elimination. These finite
computations support the uniform written proof, not a proof-assistant
verification of multiplication.

The exclusion of the empty star matters. Retain just a triangle and grant
its global sum. For each target edge, that sum plus the star of the
opposite vertex recovers its symbol. Without the extra observation, zero
input and the all-one triangle have the same vertex-star observations.

## Predecessors and cost boundary

Sam Sung (@the-missionary-company), PR669 at
`7d526020fc368ce4157cd436995c2f4fcf683318`, establishes the complete k=2
selectable-target hierarchies in `HIGHER-GRAPH.md`, and the optimal-triangle
criterion for prescribed triples in `HIGHER-WEIGHTS.md`. That historical
pinned version left larger budgets unclassified. The argument here was
developed independently for k=2 without the empty star; both inspected
predecessor texts remain unchanged with SHA256 and Git-blob pins in SOURCES.json.

Before submission, @woklerx's PR966 at
`7eaf5665ac246310293fda06a3cf245fe72f6012` published this classification for
p>=3, and Sam Sung's PR669 at `8f4600b41bf1f0f5d07f209e5d3950eb22ef5cad`
added it together with broader forest and empty-star statements. Those
results subsume this theorem statement. This proof is retained as an
independent derivation; no new classification or priority is claimed.
The package's additional contribution is independent unrestricted
coefficient enumeration at p=6, as detailed in README-INDEPENDENT.md
and VALIDATION.md. No code or numerical output from those concurrent
extensions is imported.

The graph incidence/cut-code connection is credited there to José
Martínez-Bernal, Miguel A. Valencia-Bucio and Rafael H. Villarreal,
*Generalized Hamming weights of projective Reed–Muller-type codes over
graphs*, arXiv:1812.04106v2, Corollary 2.13. This note uses the elementary
cut argument above and makes no literature-wide priority claim. The
proper-star lineage includes Joel Pulikkan / GamingPuzzled (#231),
icekylinx and eumemic, and the global-star work of Luke Mansoor (#732),
Sagar Thakrar (#725), Alishan Ladhani (#747) and ellipsi2 (#772), as
attributed in the retained predecessor texts.

A deletion budget is an information threshold, not a circuit invoice.
Supplied stars are observations for this theorem; their preparation,
source access, copies, dirty restoration, legal frames, recursive
children, hosting and full assembly costs remain unpriced. No new κ,
physical supplier, selected-frontier change, unconditional multiplier,
or resolution of the inherited compiler/analytic assumptions is claimed.

Prepared for DLamdata with substantial OpenAI Codex assistance in proof,
implementation, independent computation and adversarial review. Both
review roles were AI-assisted; no independent human review is claimed.
Apache-2.0.
