# Exact prescribed-target deletion budgets for signed two-ports

**All prescribed forests in C−; exact partition optimization in C±. No new κ.**

The selectable-target hierarchies and graph-code literature context are in
[HIGHER-GRAPH.md](HIGHER-GRAPH.md). Here the target coordinates are prescribed
in advance, which can change the optimal deletion budget.

## Model

Let p≥2. The vertices of G are 0,…,2p−1, with original matched pairs
{0,1},{2,3},…,{2p−2,2p−1}. The edges are all pairs of vertices from distinct
original pairs; there are E=2p(p−1) edges. These edges are the signed two-ports.
The code C− is the binary row span of the vertex-incidence matrix, and C+
also contains the constant edge row. For p≥3 that row is independent; at
p=2 the graph is a four-cycle and the two codes coincide.

For a prescribed target edge set T, delete a set D disjoint from T and
retain F=G\D. Every nontarget input on F remains unrestricted. The targets
are individually decodable precisely when every unit row e_t, t∈T, belongs
to the observation row span restricted to F. Define δ±(T) to be the minimum
|D|, or infinity if there is no such D. Independence of the target columns
by themselves is necessary but does not imply this unit-row condition on F.

All ranks, sums, and parity statements below are over F2.

## The exact optimization theorem

Let P partition the 2p vertices into h nonempty blocks, and let b(v) denote
the block of v. Let z(P) count the edges of G whose endpoints share a block.
For each target uv define its ordinary quotient column

    q_P(uv) = e_b(u) + e_b(v) ∈ F2^h.

Also color each block by s_v∈F2, allowing empty color classes. Let z(P,s)
count the edges of G inside blocks that join opposite colors. Define the
colored quotient column

    q_(P,s)(uv) = (e_b(u)+e_b(v), 1+s_u+s_v) ∈ F2^(h+1).

Colorings differing by a flip of an entire block are equivalent and may be
represented once. Define maxima only over partitions/colorings whose |T|
target quotient columns are linearly independent. Give an empty family
maximum −infinity, so an infinite resulting budget means infeasibility. Then

    δ−(T) = E−|T|−max_P z(P),                                  (1)
    δ+(T) = E−|T|−max{ max_P z(P), max_(P,s) z(P,s) }.          (2)

These formulas give an exact finite combinatorial optimization for every
prescribed target set and every p. Independence excludes a target from the
counted zero edges, because such an edge has zero quotient column.

To prove completeness, combine the desired unit decoders into a vector
output in F2^r, r=|T|, with target outputs the r standard basis vectors.
Their coefficients are vertex labels a_v∈F2^r and a constant vector b,
where b=0 in C−. The output at edge uv is a_u+a_v+b. Every retained
nontarget edge has zero output.

If b=0, group vertices with equal labels. Saturating every block with all
available induced edges adds only zero-output edges. The quotient target
columns map to distinct standard basis vectors and therefore are independent.
If b≠0, group labels into unordered pairs {a,a+b}, and color each block by
which label occurs. Saturating all opposite-color edges inside these blocks
again adds only zero-output edges, and the colored quotient columns are
independent. This proves that every feasible decoder is bounded by (1)–(2).
Conversely, independent quotient columns admit a linear map taking them to
the r standard basis vectors. Composing this map with the quotient columns
produces actual vertex coefficients and, in the colored case, a constant
coefficient. Retain the counted zero edges and T. This gives the required
unit rows and proves attainment. The argument remains valid if a saturated
block happens to split into several graph components.

## Feasibility and cycle interpretation

For a retained graph F, the nullspace of its incidence matrix is the binary
cycle space Z(F), namely all even-degree edge subsets. Its augmented
incidence nullspace consists of those z∈Z(F) with even cardinality. Write
π(z)=|z| mod 2 and ε_t(z)=z_t. Row-space/nullspace duality shows

    t is decodable in C−|F iff ε_t=0 on Z(F),
    t is decodable in C+|F iff ε_t vanishes on ker π.

The first condition says exactly that t is a bridge. The second says
ε_t=0 or ε_t=π as functionals on Z(F). Thus the constant row can supply
one global odd-cycle parity. For example, two edge-disjoint odd cycles
sum to an even dependency, so no edge on either can supply a target unit.
If odd cycles overlap, only their symmetric-difference edges are ruled out
by that particular dependency; shared edges must still be tested against
all cycles.

Consequently, prescribed T is feasible in C− iff T is a forest. It is
feasible in C+ iff it is a forest or has exactly one cycle in total and
that cycle is odd. For necessity, any dependence among columns of T
survives every deletion. The cycle space of T must have dimension zero in
C−; in C+ the parity map must be injective on that cycle space, forcing
dimension at most one and odd parity in dimension one. For sufficiency,
retain only T. This statement includes multiple tree components alongside
one odd unicyclic component.

## Every prescribed forest has an exact matching formula

If T contains a cycle, δ−(T)=infinity. Otherwise let T be a forest of r edges,
including isolated vertices among its components Q_1,…,Q_s. Then

    s=2p−r.

Construct a bipartite graph with these components on the left and the p
original matched pairs on the right. Give Q_i capacity |Q_i|−1 and each
original pair capacity one. Join Q_i to an original pair when Q_i contains
at least one of that pair's vertices. Let ν(T) be the maximum integral
b-matching size. Then

    B(T) = binom(s,2) − p + ν(T),
    δ−(T) = E − r − B(T).                                  (F)

In particular this is an exact polynomial-time combinatorial formula for
any prescribed target forest, not just a generalized-weight bound for a
selectable target set. The empty forest has ν=0 and δ−=0.

## Matching interprets the best root construction

Choose one root in each Q_i, and let R be the r nonroot vertices. The
maximum possible number of original pairs hit by R is exactly ν(T).

For one direction, choose one representative vertex from R for each original
pair hit. Assign that representative to its target component. Each component
receives at most |Q_i|−1 representatives, giving a feasible b-matching.
For the converse, realize a maximum b-matching by choosing, for each matched
component/pair incidence, one vertex in their intersection. Different matched
pairs give distinct vertices. Fill each component's chosen vertices to its
capacity |Q_i|−1, leaving one root. This extension cannot hit more than ν(T)
original pairs by the first direction, and it already hits ν(T), so equality
holds.

The s roots contain exactly p−ν(T) complete original matched pairs: a pair
is wholly among the roots exactly when R does not hit it. Retain all graph
edges induced by the roots, and retain T. There are B(T) zero edges. Every
target component meets the root block once, so contracting that block leaves
a forest. Hence every target edge is a bridge and supplies its unit row.
This constructs the budget on the right side of the forest formula.

## Any retained witness has no more zero edges

Let F be an arbitrary feasible retained graph and H=F\T its nontarget graph.
Every target edge must be a bridge in F, because the nullspace of a graph's
binary incidence matrix is its cycle space. Removing the r bridges creates
r additional components, so H has at least r+1 components.

Also every component of H meets each target tree Q_i at most once. Otherwise
the target path between two such vertices, together with an H-path joining
them, would put a target edge on a cycle, contradicting the bridge condition.

If H has at most one nonsingleton component, that component is therefore a
partial root transversal. Extend it to one root in every Q_i, and saturate
the resulting root block. This retains at least as many zero edges and
is bounded by B(T). This handles H with more than r+1 components as well.

It remains to bound H with at least two nonsingleton components. A set of
v vertices induces at most

    f(v)=binom(v,2)−max(0,v−p)

edges. The increments f(v+1)−f(v)=v−1[v≥p] are nondecreasing. Concentrating
vertices into one largest block while preserving a second nonsingleton
block, and making all other blocks singletons, gives

    |H| ≤ f(s−1)+f(2)=f(s−1)+1,                            (M)

provided s≥3. If s≤2, H cannot have two nonsingleton components, since its
at least r+1=2p−s+1 components leave at most s−1≤1 vertices beyond one per
component.

The gap between the unrestricted one-block maximum and (M) is

    Δ=f(s)−f(s−1)−1=s−2−1[s−1≥p].                        (G)

We compare it with the loss f(s)−B(T).

### When r≤p

Here s≥p and

    f(s)−B(T)=r−ν(T).

Any r vertices hit at least ceil(r/2) original pairs. Thus ν(T)≥ceil(r/2)
and the loss is at most floor(r/2). If r≤p−1, equation (G) gives
Δ=2p−r−3≥p−2≥floor(r/2) for p≥3. If r=p, it gives
Δ=p−2≥floor(p/2), also for every p≥3. Consequently

    f(s−1)+1 ≤ B(T).

### When r≥p

Here s≤p, and

    f(s)−B(T)=p−ν(T).

This is the number of complete original pairs in an optimal s-vertex root
set, at most floor(s/2). For s≥3, equation (G) gives
Δ=s−2≥floor(s/2), so (M) is again at most B(T). The case s≤2 was already
handled without a two-block comparison.

Thus every feasible H has at most B(T) edges. Together with the root
construction this proves (F) for p≥3. Ties with multiblock witnesses are
allowed and do occur; the theorem only needs existence of a root optimum.
For p=2, G is a four-cycle: every nonempty proper edge subset is a forest
and requires exactly one deletion. Directly ν=1 when r=1 and ν=2 when
r=2 or 3, so (F) gives one in each case. The empty set gives zero.

## When the constant row provably cannot improve a forest budget

Let C+ also include the constant row, and suppose r≥1. A vector decoder
assigns vertex coefficients a_v∈F2^r and a constant b∈F2^r, with edge output
a_u+a_v+b. If b=0, its optimum is already (F). If b≠0, every zero edge
satisfies a_u+a_v=b, so the zero graph H is bipartite.

For h components of H, the target quotient columns have an incidence part
of dimension at most h−1 plus one parity coordinate. Independent target
units therefore require h≥r. The largest possible bipartite edge count
with at least r components is bounded above by

    floor((2p−r+1)^2/4)=floor((s+1)^2/4),

using the nondecreasing increments of floor(v²/4) to concentrate component
sizes. It follows that

    B(T) ≥ floor((s+1)^2/4)  implies  δ+(T)=δ−(T).          (C)

This is a sufficient criterion, not asserted to be necessary.

In particular, for every p≥6 and every forest with 1≤r≤p, condition (C)
always holds. Indeed,

    B(T) ≥ binom(s,2)−p+ceil(r/2)
         = binom(s,2)−floor(s/2),

and s≥p≥6. For even s=2a the difference from floor((s+1)^2/4) is a(a−3),
nonnegative for a≥3. For odd s=2a+1 it is (a−1)^2−2, nonnegative for a≥3.
Thus adding the constant row never changes any such prescribed-forest
budget. This statement makes no claim for arbitrary r>p or for infeasible
C− target sets such as odd cycles.

## Prescribed triples, including the constant row

Suppose p≥3 and |T|=3. Call T exceptional if it is a three-edge path in the
K_(2,2) formed by two original matched pairs. Then:

| Targets | δ−(T) | δ+(T), p≥4 |
| --- | --- | --- |
| Triangle | infinity | p²−4 |
| Exceptional forest | 6p−11 | 6p−11 |
| Any other forest | 6p−12 | 6p−12 |

At p=3, δ+(T)=5 for every triple; the C− column remains valid. At p=2 every
triple consists of three edges of the four-cycle, and both budgets are one.

### The forest matching number for triples

At r=3 the forest formula becomes δ−=6p−9−ν(T). The exceptional connected
path meets just two original pairs, so ν=2. Every other forest triple has
ν=3, as the following explicit choices of three isolates show:

* A connected three-edge tree has four vertices. Unless exceptional it
  meets at least three original pairs. Isolate vertices from three different
  pairs and take the fourth as root. A three-edge star cannot use only two
  original pairs, since the pair opposite its center supplies at most two leaves.
* For a two-edge path plus a separate edge, if the path meets three original
  pairs, choose an endpoint of the separate edge, then isolate path vertices
  from two different pairs avoiding that endpoint's pair. If the path uses
  two original pairs, its repeated pair is exhausted by its endpoints. The
  separate edge therefore has an endpoint in a third pair; select it and
  one path vertex from each of the other two pairs.
* For three disjoint edges, select one endpoint from each with distinct
  original-pair indices. Hall's condition holds: two edges involve at least
  two original pairs, and three disjoint edges cannot fit into two pairs
  because that would put six vertices into four positions.

### The nonzero-constant bound

A decoder with nonzero constant has a bipartite zero graph H with at least
three components, so |H|≤(p−1)² and its deletion budget is at least p²−4.
For p≥5 this is greater than 6p−11 because
p²−4−(6p−11)=(p−3)²−2>0. Thus it cannot improve a forest triple's C− budget.
At p=4 the bound is twelve: all ordinary forest triples already attain it,
while the exceptional thirteen-deletion case requires the argument below.

### Triangle targets attain p²−4 for every p≥3

Adding the three target unit equations around a triangle forces
b=e_1+e_2+e_3≠0, so p²−4 is a lower bound. For attainment isolate two triangle
vertices, and on the remaining 2p−2 vertices retain a complete bipartite
graph with sides p−1,p−1, along with the three target edges.

The isolates come from distinct original pairs, so the large block consists
of p−2 full matched pairs and two orphan vertices. If p is even, place one
orphan on each side and split full pairs equally. If p is odd, place both
orphans on one side and fill both sides with whole pairs. No missing matched
edge crosses sides, so all (p−1)² bipartite edges exist. The quotient target
triangle has three independent augmented columns: its sole cycle has odd
parity. Thus the construction gives actual units and exactly p²−4 deletions.

### Why the exceptional p=4 path cannot improve to twelve

If it had a twelve-deletion decoder with b≠0, its bipartite zero graph H
would have nine edges and at least three components. Concentrating component
sizes shows that nine requires a six-vertex K_(3,3) plus two isolates: a
second nonsingleton block allows at most floor(25/4)+1=7 edges, and four
components allow at most floor(25/4)=6. Full original matched pairs inside H
must lie on the same side, hence their vertex decoder labels are equal. In the target
path, the two vertices of each of its original pairs are joined by a target
path of length two. Those two unit equations force their labels to differ
by the sum of two distinct standard basis vectors. Therefore each target
original pair must contribute an isolate. The two isolates are exactly one
vertex from each of the two target pairs.

The remaining target vertices are H's two orphans. As both bipartition sides
have odd size three and full matched pairs stay on one side, the two orphans
must lie on opposite sides. Their joining edge is therefore in H. If it is
a target this contradicts H∩T=∅. Otherwise it is the fourth edge of the
original K_(2,2), and together with T forms an even four-cycle, again giving
a target dependence. Thus thirteen deletions are necessary, and the C−
witness attains them.

### A hand-checkable p=3 boundary certificate

The lower bound is five: b=0 requires at least six deletions by the forest
formula, and b≠0 requires at least five by the bipartite bound. The following
table supplies an upper bound for all triples. Matched pairs are
{0,1},{2,3},{4,5}; notation 02
means edge {0,2}. Retain H=K_(L,R) and the targets. Every listed H has four
edges, so F has seven and exactly five edges are deleted.

| Orbit size | Target edges, in order | L | R | Reduced target columns |
| --- | --- | --- | --- | --- |
| 24 | 02,03,04 | 1,2 | 4,5 | 5,7,1 |
| 12 | 02,03,12 | 0,2 | 4,5 | 4,6,5 |
| 48 | 02,04,12 | 2,3 | 4,5 | 5,1,6 |
| 48 | 03,04,12 | 1,2 | 4,5 | 7,1,4 |
| 24 | 04,05,12 | 0,4 | 2,3 | 4,6,1 |
| 8 | 02,04,24 | 0,1 | 3,5 | 5,6,7 |
| 24 | 03,04,24 | 0,1 | 2,5 | 5,6,2 |
| 24 | 03,05,24 | 0,1 | 2,4 | 5,6,4 |
| 8 | 05,13,24 | 0,1 | 2,4 | 6,5,4 |

For the last column, use color zero on L and color one on R. Color the two
isolates zero, order them numerically, and assign them block coordinates
1 and 2; assign the large component coordinate zero. The parity coordinate
is the bit 4. Each displayed integer is the corresponding three-bit column
from the optimization theorem. Every triple consists of distinct nonzero
vectors whose XOR is nonzero, so every triple has rank three. This verifies
the individual target units on the entire retained graph.

The nine orbits are under permutations of the three original pairs and
independent swaps inside them (48 automorphisms). Their sizes sum to
220=binom(12,3). Completeness can also be seen by shape: one star orbit;
three connected-path orbits (two original pairs, or a repeated pair at
path distance two or three); three two-edge-path-plus-edge orbits (repeated
path-end pair, or the separate edge joining partners of center/end versus
both ends); one triangle orbit; and one perfect-matching orbit. The table
therefore proves δ+=5 for every p=3 triple without a large computational
assumption.

## Standalone finite verifier and receipt

Python 3.10 or later is required. From the repository root:

```sh
python3 -I -B research/asymmetric-hypercube-decoder/graph_targets_verify.py
python3 -I -O -B research/asymmetric-hypercube-decoder/graph_targets_verify.py --self-test
python3 -I -B research/asymmetric-hypercube-decoder/graph_targets_verify.py --write /tmp/graph-targets.json
python3 -I -B research/asymmetric-hypercube-decoder/graph_targets_verify.py --check /tmp/graph-targets.json
```

The standard-library script imports no repository or scratch modules. By
default it recomputes and compares [GRAPH-TARGETS-RESULTS.json](GRAPH-TARGETS-RESULTS.json).
`--write` writes only after all computations and requested checks pass;
`--check EXISTING --write OUTPUT` verifies EXISTING before touching OUTPUT.
Writes use a same-directory temporary file and atomic replacement. The
self-test copies only the script and receipt into an otherwise empty
directory, performs an isolated optimized replay, rejects a corrupted
mathematical receipt field while preserving an existing output, and checks
cleanup and preservation after a simulated atomic replacement failure.
Every mathematical check uses an explicit exception, not a removable assertion.

The finite coverage is independent of the uniform proofs:

* For p=2 and p=3, enumerate every retained graph and test each target unit
  by exact binary column rank. A maximum superset transform obtains exact
  budgets for all 16 and 4,096 target sets. Compare both models with separate
  partition optimization: 8,224 model/target cases. The cycle-functional
  characterization is checked on every retained graph in both models.
* For p=4, enumerate all 16 triple and 57 quadruple target orbits, covering
  2,024 triples and 10,626 quadruples. Compare partition optimization with
  exhaustive decoder vertex-label assignments satisfying the actual distinct
  standard-basis target values: 266,240 C− and 4,063,232 C+ assignments.
  All 146 model/orbit exact optima agree. Every attaining witness retains
  its targets and passes direct unit-row tests.
* Independently compute ν by augmenting-path capacity matching and literal
  root-choice dynamic programming. Their forest formula agrees with all
  p=2/p=3 targets (15/1,083 forests) and all p=4 orbits (65 forest orbits).
  The concentration and constant-row arithmetic is also checked for the
  9,996 pairs 3≤p≤100, 1≤r≤2p−1 in the respective stated domains.
* Verify the nine literal p=3 witnesses above, their orbit sizes, and their
  reduced target columns. Reject all 1,845 one-deletion restorations of the
  p=4 optimum witnesses. Other adversarial checks reject omission of the
  constant row, even target cycles, two edge-disjoint odd cycles, and the
  false inference from target-column independence to retained unit decoding.

The receipt includes all 73 p=4 representatives and literal retained masks,
plus complete budget histograms and hashes of the p=2/p=3 budget tables.
The quadruple results below are exact finite findings; no uniform
prescribed-quadruple theorem for C+ is inferred from them.

| Domain | C− budgets, with target-set counts | C+ budgets, with target-set counts |
| --- | --- | --- |
| p=3 triples | 6:200; 7:12; infinity:8 | 5:220 |
| p=3 quadruples | 7:408; infinity:87 | 6:480; infinity:15 |
| p=4 triples | 12:1968; 13:24; infinity:32 | 12:2000; 13:24 |
| p=4 quadruples | 14:8124; 15:1728; infinity:774 | 14:10524; infinity:102 |

## Interpretation and attribution

For k=2, the permitted overlap correction C_1({a,b}) equals the sum of the
two singleton-star rows at a and b, including after deletion. Adding such
corrections changes neither observation span. Arbitrary exact postprocessing
of the same linear observations also cannot defeat the unit-row condition:
if a target coordinate does not vanish on the observation kernel, two inputs
with the same observations have different target values.

These are observation-span deletion budgets. They assign no physical cost
to helper creation, access, copying, or restoration, and make no claim about
multiplication bounds or κ.

Prepared by Sam Sung with substantial OpenAI Codex assistance. Copyright
2026 Sam Sung; Apache-2.0.
