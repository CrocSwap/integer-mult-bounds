# The fifteen-owner equality case

## Statement

Let G=(B,D,E) be a finite nonempty simple bipartite graph. Assume minimum
degree at least three, no four-cycles, |B|=15, and the following bounds on
the number c6(d) of unoriented simple six-cycles through each d in D:

    c6(d) <= 1                    when deg(d)=3;
    c6(d) <= floor(deg(d)^2/4)    when deg(d)>=4.

Then both parts have fifteen vertices and every vertex has degree three.
The six-cycles are vertex disjoint. Write t for their number. Either t=0,
or 2<=t<=5. In particular, an equality graph cannot have exactly one
six-cycle.

There is also an explicit necessary matrix identity. Let C be its 15 by 15
zero-one incidence matrix, with rows indexed by B. Let J be the all-ones
matrix. There are partial permutation matrices P and Q with exactly the
same 3t active rows and 3t active columns such that

    C C^T C = 4 C + J + P - Q.                         (1)

P matches each vertex of B on a six-cycle to the opposite vertex of D on
that cycle. Q matches it to a vertex on a different six-cycle. Every active
row and column of either matrix contains exactly one 1. Furthermore

    (P-Q) C^T = C (P-Q)^T.                            (2)

These are integer identities. No coefficient-field reduction is used.
When t=0, (1) reduces to C C^T C = 4 C + J.

## 1. The new equality reduction

We use Sagar Thakrar's local path-counting inequality from PR3291,
PROOF.md section 2, as a cited lemma:

    |B| >= 5 deg(d) - c6(d).                          (3)

Its hypotheses are precisely minimum degree three and absence of four-cycles.
We do not re-audit the route extraction or the predecessor's floor proof.
For 4<=k<=15, the lower bound 5k-floor(k^2/4) takes the values

    16,19,21,23,24,25,25,25,24,23,21,19.

Every value exceeds 15. A simple graph with fifteen vertices in B has
no D degree greater than fifteen, so all vertices of D have degree three.

If b in B had degree at least four, root at an adjacent d. Its three B
neighbors have at least 3+2+2=7 other D neighbors. They are distinct because
there are no four-cycles. Each has two further B neighbors. There are at
least fourteen incidences to level three. Collapsing them to distinct B
vertices can save at most c6(d)<=1 vertices, by the collision count used in
(3). These vertices are outside the three first-level vertices. This would
require |B|>=3+14-1=16. Thus every B vertex also has degree three. Counting
edges gives 3|D|=3|B|, hence |D|=15.

This extends the predecessor's fourteen-owner contradiction to a structural
statement at its sharp equality size. It does not improve the bound fifteen.

## 2. Six-cycles are disjoint

Two distinct six-cycles cannot share a D vertex, by its cap. If they shared
a B vertex, each would use two of its three edges. They would therefore
share an edge and its D endpoint, also impossible. Thus all six-cycles are
vertex disjoint. The same cap of one now holds at B vertices. Each cycle
uses three vertices of each part, so t<=5.

## 3. The signed defect

For b in B and d in D, (C C^T C)_(b,d) counts length-three walks from b to d.
If they are adjacent, exactly five such walks exist: three backtrack at b
and three backtrack at d, with the single-edge backtrack counted twice.
A further walk would form a four-cycle. Thus the entry is five.

If b and d are not adjacent, all these walks are simple paths. Let p_b(d)
be their number. Two different paths between these endpoints have disjoint
interiors: sharing either interior vertex would create a four-cycle. Hence

    c6(b) = sum_(d not adjacent to b) binom(p_b(d),2).  (4)

Each six-cycle through b has a unique opposite endpoint d, which proves
both directions of this counting identity.

There are twelve length-three paths from b to nonneighbors: choose one of
three first edges, one of two second edges, and one of two third edges.
No such path can return to a neighbor, since there are no four-cycles.
There are also exactly twelve nonneighbors in D.

If c6(b)=0, (4) forces all twelve path counts to be one. If c6(b)=1, it
forces exactly one count to be two, exactly one to be zero, and the other
ten to be one. The doubled endpoint is the opposite vertex on b's unique
six-cycle. The zero endpoint is unique.

Apply the same argument after interchanging B and D. It shows that a
column of the defect matrix

    E = C C^T C - 4C - J

is zero off the six-cycles; on a six-cycle it has one +1 and one -1.
The row statement is identical. Thus the positive entries form P, the
negative entries form -Q, and their active row and column sets are exactly
the vertices on the six-cycles. This proves (1) and the asserted partial
permutation structure.

For an active b, its own six-cycle contains three D vertices. Two are
adjacent to b, while the third has two length-three paths from b. None is
the zero-path endpoint. The Q endpoint therefore lies on another cycle.
If there were exactly one six-cycle, there would be no such endpoint.
This excludes t=1.

Finally, E C^T = (C C^T)^2 - 4 C C^T - 3J is symmetric, since every row
of C has sum three. Transposing gives (2).

## 4. What this does and does not settle

The six-cycle-free duad/perfect-matching graph in PR3291 attains the
hypotheses, so the equality class is nonempty. Its established floor and
classical geometry retain their credit. We do not claim uniqueness of that
graph, nor exclude equality graphs with two through five six-cycles.

For a future route-labelled fifteen-owner search, every candidate can now
be restricted to a cubic fifteen-by-fifteen incidence with the signed defect
above. If it has a six-cycle, it must have at least two disjoint ones, and
the negative defect matches between different cycles. Actual route labels,
scalar coefficient equations and physical realization are additional
obligations. The present theorem supplies no common-kernel vector, cheaper
repair, paid profile, supplier admission or new kappa.
