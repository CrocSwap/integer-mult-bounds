# Exact query dimension on bipartite masks

This is a scoped algebraic theorem, not a physical supplier or a complete
multiplication theorem. All dimensions below are integers. The field is arbitrary.

## Contract and result

Let G=(L disjoint-union R,E) be any finite simple bipartite graph. At vertex v
there are d_v>=0 source coordinates and d_v target coordinates. Put D=sum_v d_v.
A fitting matrix M has D rows and D columns, partitioned by these vertices, with

    M_vv = I_(d_v),
    M_uv = 0 if u != v and {u,v} is not an edge.

Each permitted ordered block is arbitrary. Rectangular blocks, asymmetric
opposite blocks, noncommuting coefficients and empty blocks are allowed.

Define the maximum integral edge sharing

    nu = max sum_(e in E) x_e,
    x_e integer >= 0,
    sum_(e incident to v) x_e <= d_v for every v.

Define alpha_d(G) as the maximum of sum_(v in I) d_v over independent vertex
sets I. Then, over every field F,

    min_(M fits G) rank_F(M) = D - nu = alpha_d(G).       (1)

Equivalently, a linear query factorization M=A B needs at least alpha_d(G)
intermediate field coordinates, and a factorization of exactly that size exists.
Any factorization gives rank(M)<=its intermediate dimension. Conversely a rank
factorization exists by selecting a basis of the column space of M.

The new repository statement is this complete bipartite-mask contract with
unequal payloads. Weighted matching and cover duality are classical. We give
the elementary proof rather than claiming a new graph-theoretic theorem.

## Integral sharing equals minimum weighted vertex cover

Construct a directed network with source s and sink t. Give s->u capacity d_u
for u in L, u->v capacity D+1 for every {u,v} in E, and v->t capacity d_v for
v in R. Start with zero flow. As long as a residual s-to-t path exists, augment
by the smallest residual capacity along that path. Every capacity and flow stays
integral. Each augmentation increases the flow value by at least one, and the
value is at most D. Thus the process terminates, including when D=0.

At termination let S contain the residual vertices reachable from s. There is
no positive residual arc leaving S, and t is outside S. Therefore every original
arc leaving S is saturated and every original arc entering S carries zero flow.
Conservation shows that the flow value equals the capacity of this cut. Every
flow value is at most every cut capacity, by the same conservation identity, so
both are optimal. This proves the needed integral flow and cut statement.

The cut capacity is at most D because the cut containing only s costs at most D.
It therefore cannot cut a D+1 arc. Write P=S intersect L and Q=S intersect R.
Every neighbor in R of P lies in Q. Consequently

    C = (L minus P) union Q

is a vertex cover, and the cut capacity is exactly sum_(v in C) d_v. Conversely
a vertex cover C defines such a cut by taking P=L minus C and Q=R intersect C;
its capacity is the cover weight. Edge flows x_e satisfy the vertex capacities,
and every feasible integer x extends to a network flow. Hence nu is exactly the
minimum weighted vertex-cover value.

A set is independent exactly when its complement is a vertex cover. Taking
complements gives alpha_d(G)=D-nu. Zero weights and isolated vertices need no
special convention beyond empty sums.

## Lower bound for every fitting matrix

Choose an independent set I of weight alpha_d(G). The principal submatrix on
all coordinates at vertices in I is the identity of size alpha_d(G). The
nonedge condition forces every off-diagonal vertex block in this submatrix to
vanish. Taking a submatrix cannot increase rank. Thus every fitting M has
rank at least alpha_d(G), regardless of its permitted coefficients or the field.

## Attainment by coordinate pairs

Take optimal integral edge counts x. Allocate x_(uv) distinct, previously unused
coordinates at u and the same number at v. Pair them across edge {u,v}. The
vertex constraints make these allocations possible. Each unallocated coordinate
is private. A pair contributes the matrix

    [1 1]
    [1 1]

on its two coordinates, and a private coordinate contributes [1]. Put zero in
all other positions. After a simultaneous permutation this is a direct sum of
rank-one two-coordinate matrices and rank-one private matrices. It fits G,
because the only off-diagonal entries join an edge and each diagonal block is
its identity. Its rank over every field is

    number of pairs + number of private coordinates
      = nu + (D - 2 nu) = D - nu = alpha_d(G).

A query for a pair is the sum of its two source coordinates, read by each of its
two targets. A private query is its source coordinate. These give literal A,B
with M=A B. Each receiver may subtract its neighbor contribution in the usual
fitting-matrix interpretation; physical side-information access is a separate
contract. The theorem only states the algebraic factorization.

This proves (1). It also proves integrality: multiplying every d_v by a positive
integer k multiplies the optimum by k. Vector payload mixing gives no rate gain
beyond scalar coordinate pairing on this graph class. This is a dimension
statement, not a claim that a physical pair query costs one native operation.

## First example and decision

For a star with center width 4 and three leaves of width 1, D=7, nu=3 and the
exact rank is 4. The larger bipartition-side total is sharp here. On a
path with widths (4,1,1,4), the two side totals are both 5, but the independent
endpoint set has weight 8, nu=2, and the exact rank is 8. Merely taking the
larger side total can therefore underprice even a connected bipartite mask.

In this contract, searches for arbitrary block coefficients on a bipartite mask
cannot beat an integral edge-sharing construction. To seek a lower algebraic
query rate, change the graph class, the diagonal/zero contract or the type of
encoding. Tekalign's #3362 treats the nonbipartite five-cycle and its P112
principal core. That result is a credited model antecedent, not an input or a
result replayed here. We do not claim a stronger full-P112 lower bound.

## Finite evidence and scope

The verifier has an integral residual-flow constructor and a separate exhaustive
independent-set oracle. It expands the pair construction, checks every required
matrix entry and computes actual ranks over GF(2), GF(3) and GF(101). A second
finite experiment enumerates every ordered binary fitting block in its declared
small domain, including nonsymmetric completions. These checks corroborate the
proof; they do not replace its all-field and all-dimension arguments.

The mathematical theorem has no bound on graph size or dimensions. The checker
has explicit finite capacities. It imports no predecessor code and has no
runtime input from another package. No claim is made about coefficient bit cost,
nonlinear queries, native COPY tariffs, source acquisition, frames, arbitrary
dirty-state restoration, ownership, hosting, stock, precision/tape, all-size
compiler admission, a complete supplier or outer multiplication transfer.

This contribution is produced by Nick Petalas. Credit Tekalign/#3362 for the
unequal-payload block-fitting interface; Sagar Thakrar/#2484 and ywz65/#2471 for
the P112 cycle setting, and the classical matching/vertex-cover and block-fitting
methods. Cinna Davis, Adam Gall, ctoth, Philippe Van Velzen and the retained
P112/E8/native/compiler lineage retain their predecessor credit. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
