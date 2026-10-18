# A local counting proof for the selected owner-block model

This note separates three statements: a counterexample to PR3147's intermediate
triangle bound, a sharp abstract graph theorem, and its consequence for the
fixed whole-later-query observation model. The counterexample does not refute
the physical owner-block conclusion. The abstract sharpness example is not a
labelled construction for the selected routes.

## 1. The omitted complement-triangle term

Let \(G\) be a simple graph on \(m\) vertices, let \(H\) be its complement,
and write \(U=|E(H)|\), \(W=\sum_v\binom{\deg_H(v)}2\). Inclusion-exclusion
on the three possible nonedges in a vertex triple gives the exact identity

\[
t(G)=\binom m3-U(m-2)+W-t(H).
\]

If \(2U=mq+r\), where \(0\le r<m\), convexity gives

\[
W\ge W_{\min}=(m-r)\binom q2+r\binom{q+1}2.
\]

PR3147's `check_c4_free_degree_feasibility` uses
\(\binom m3-U(m-2)+W_{\min}\) as a lower bound for \(t(G)\). The omitted
term \(-t(H)\) makes that implication invalid.

An incidence graph within the relevant abstract minimum-degree and
four-cycle-free class witnesses the error. Its nine points are
\((x,y)\in\mathbb F_3^2\), and its nine lines are

\[
y=ax+b,\qquad a,b\in\mathbb F_3.
\]

Both sides have degree three. Distinct points lie on at most one retained
line, so the bipartite incidence graph has no four-cycle. The distance-two
graph on the points is \(K_{3,3,3}\), with its three parts indexed by \(x\).
It has 27 triangles. Its complement is three disjoint triangles, with
\(U=9\), \(W=W_{\min}=9\), and \(t(H)=3\). The source expression is
\(84-63+9=30\), whereas the correct value is \(30-3=27\).

Nine of those 27 triangles are the three points on one retained line. The
other 18 correspond bijectively to six-cycles of the incidence graph. Thus
the source expression overstates the forced six-cycle count as 21 instead
of 18. Each point and each line lies on six six-cycles. In particular this
graph **does not** satisfy the route-derived degree-three cap of one; it is
a counterexample to the intermediate graph bound, not to the final physical
claim.

A sound general replacement is

\[
t(G)\ge\max\left(0,\binom m3-U(m-2)+
                 \left\lceil\frac{2W_{\min}}3\right\rceil\right).
\]

Indeed each triangle of \(H\) accounts for three wedges, so
\(t(H)\le W/3\). This replacement is exact on the nine-point control.
The proof below does not need this global bound or a degree-partition census.

## 2. A sharp abstract graph theorem

**Theorem.** Let \(I=(B,D,E)\) be a finite nonempty simple bipartite graph
with minimum degree at least three and no four-cycles. For each \(d\in D\),
let \(c_6(d)\) count the unoriented simple six-cycles containing \(d\).
Suppose

\[
c_6(d)\le
\begin{cases}
1,&\deg(d)=3,\\
\lfloor\deg(d)^2/4\rfloor,&\deg(d)\ge4.
\end{cases}
\]

Then \(|B|\ge15\). No connectedness assumption is needed. The bound is
attained by an abstract graph satisfying all these hypotheses.

Fix a root \(d\in D\) of degree \(k\). Its first level contains \(k\)
vertices of \(B\). Each has at least two other neighbors in \(D\).
Four-cycle-freeness makes these second-level vertices distinct, with unique
first-level parents. There are consequently at least \(2k\) of them.
Each second-level vertex has at least two other neighbors in \(B\), and
none of those neighbors is in the first level. Let \(S\) count these
second-to-third-level edges, so \(S\ge4k\).

For a third-level vertex \(b\), write \(r_b\) for the number of its
second-level neighbors. Those neighbors have different first-level parents:
two with the same parent would form a four-cycle. Each unordered pair of
them therefore determines one simple six-cycle through the root. Conversely,
every six-cycle through the root arises from exactly one such pair. Hence

\[
c_6(d)=\sum_{b\text{ in level }3}\binom{r_b}2.
\]

Since \(\binom r2\ge r-1\) for every positive integer \(r\), the number
of third-level vertices is at least \(S-c_6(d)\). The first and third
levels are disjoint subsets of \(B\), giving the local inequality

\[
\boxed{|B|\ge5k-c_6(d).}
\]

Put \(m=|B|\) and suppose \(m\le14\). A simple bipartite graph has
\(3\le k\le m\). For \(k=3\), the local bound gives \(m\ge14\).
For \(k=4,\ldots,14\), the respective lower bounds
\(5k-\lfloor k^2/4\rfloor\) are

\[
16,19,21,23,24,25,25,25,24,23,21.
\]

Thus \(m\le13\) is impossible, and if \(m=14\), every vertex of \(D\)
has degree three.

In this remaining case, if a vertex of \(B\) had degree at least four,
root at any adjacent \(d\). The root's three first-level vertices would
have at least \(3+2+2=7\) distinct second-level neighbors, producing at
least 14 edges to the third level. The root lies on at most one six-cycle,
so this would require \(m\ge3+14-1=16\), a contradiction. Therefore
both sides are cubic. Edge counting now gives \(|D|=|B|=14\).

At every root \(d\), the local bound gives \(c_6(d)\ge15-14=1\).
The cap forces equality at all 14 roots. But every six-cycle contains
exactly three vertices of \(D\), so

\[
14=\sum_{d\in D}c_6(d)=3\,c_6(I),
\]

which is impossible. This proves \(m\ge15\).

For sharpness, let \(B\) be the fifteen unordered pairs (duads) of a
six-element set, and let \(D\) be its fifteen perfect matchings
(synthemes). Join a duad to each matching containing it. Each matching
contains three duads, and each duad belongs to three matchings, so the graph
is cubic with 45 edges. Two disjoint duads determine the remaining duad
of their unique common matching, excluding four-cycles. Three duads that
are pairwise contained in matchings must be pairwise disjoint and hence
form one matching together; they cannot form a six-cycle using three
distinct matchings. Thus there are no four- or six-cycles. This is an
abstract equality example with \(|B|=15\); no selected route or column
labelling is supplied.

## 3. Connection to the fixed physical-owner model

The corollary uses the same one-to-one owner and whole-later-query contract
as the retained selected-centre information-floor packages. Fix a coefficient
field \(\mathbb K\in\{\mathbb Q,\mathbb R,\mathbb C\}\). Distinct physical
owner labels are distinct elements \(g\) of the inherited binary matrix
group; right multiplication by a route is an injective action. There are
112 ports. For a finite owner set \(B\), let
\(x(g)=(x_p(g))_{p=0}^{111}\in\mathbb K^{112}\), extended by zero outside
\(B\). The old and required observations are exactly

\[
(Sx)(g)=R x(g),\qquad
(Tx)(d)=\sum_{p=0}^{111}H[:,p]x_p(d\rho_p),\qquad H=R/4.
\]

The required output includes **every** later query owner \(d\), not a
projection onto a smaller chosen list. Owner aliasing, chart identifications,
different route schedules, additional old observations, and nonlinear or
adaptive measurement models are not included.

As in the predecessor, compared executions have equal arbitrary ordinary
target/helper dirt. Owner blocks form a disjoint partition, and additional
linear observations at a block only use its source coordinates; no other
source-dependent state is available. The global decoder may be arbitrary,
including nonlinear. The native interpretation of the displayed equations
retains the predecessor's common-frame, constant-endpoint and source-adapter
identities as assumptions, rather than newly proving that adapter here.

The following source-bound finite premises are checked or replayed by the
primary verifier. The route matrices are over \(\mathbb F_2\); dependence
of the scalar columns is over \(\mathbb K\). These are different fields.

1. The matrix \(R\) has rank eight, all columns are nonzero, and no two
   columns are parallel. The matrix \(H\) is exactly \(R/4\).
2. The 112 routes \(\rho_p\) are distinct involutions, and all 12,432
   ordered products \(\rho_a\rho_b\), \(a\ne b\), are distinct.
3. The complete reduced-triple classification establishes that every
   cyclically reduced six-route identity is an alternating braid relation
   \(\rho_a\rho_b\rho_a=\rho_b\rho_a\rho_b\). This uses the full
   1,379,952-product census; pair-product uniqueness alone would not imply it.
4. The graph of braid pairs on the 112 port labels is triangle-free. Every
   linearly dependent triple of columns of \(R\) contains at most one
   braid pair. The latter premise is checked on all port triples, not only
   the triples encountered in a chosen incidence graph.

Suppose \(x\ne0\) lies in \(\ker S\cap\ker T\). Make an edge labelled
\(p\) from source owner \(g\) to output owner \(d=g\rho_p\) exactly
when \(x_p(g)\ne0\). Discard inactive vertices. Distinct routes and the
free right action give a simple bipartite graph with distinct incident port
labels at every vertex. Each source vertex has degree at least three because
one or two nonparallel columns of \(R\) cannot cancel; the same argument
with \(H\) gives minimum degree three at output vertices.

A four-cycle would give two equal ordered nonidentity route products, with
different ordered labels, contradicting premise 2. A six-cycle has distinct
adjacent port labels and gives a cyclically reduced six-route identity, so
premise 3 makes its labels alternate between one braid pair.

At a fixed root \(d\), a fixed unordered incident braid pair \(a,b\)
determines at most one six-cycle. Starting at \(d\), all the other owner
labels are fixed by successive right multiplication. In particular the
third source owner is
\(d\rho_a\rho_b\rho_a=d\rho_b\rho_a\rho_b\); there is no second
choice of a physical owner carrying the same group label. This is where
the one-to-one owner premise is needed.

At a degree-three output vertex, its three incident nonzero coefficients
give a dependence among three columns of \(H\), equivalently of \(R\).
Premise 4 and uniqueness per braid pair give \(c_6(d)\le1\). At an output
vertex of degree \(k\ge4\), the induced braid graph on its \(k\) distinct
labels is triangle-free. Mantel's theorem gives at most
\(\lfloor k^2/4\rfloor\) braid pairs, and hence that many six-cycles.
All hypotheses of the graph theorem now hold. Therefore every nonzero
common-kernel perturbation has at least fifteen source owners.

For every fixed owner block of size at most fourteen,
\(\ker S\cap\ker T=\{0\}\). Since \(R\) has rank eight,
\(\dim\ker S=(112-8)|B|=104|B|\), and \(T\) is injective on that kernel.
If additional scalar linear observations \(Lx\), together with \(Sx\),
determine every required \(Tx\), then
\(\ker S\cap\ker L\subseteq\ker T\). Thus \(L\) must be injective
on \(\ker S\), requiring at least \(104|B|\) scalar observations.

This count is attained in the observation model by reading 104 complementary
coordinates per owner: choose eight pivot columns of \(R\), observe the
other 104 coordinates, and reconstruct the pivot coordinates from \(Rx\).
That reconstruction determines the entire input and hence all later queries.
This is an exact information count, not a physical implementation tariff or
an assertion that those observations, routing or restoration are free.

## 4. Evidence and limits

The primary checker binds the predecessor sources and finite route/column
premises. The independent checker imports no primary or predecessor executable.
It constructs the nine-point and fifteen-point graphs from their definitions,
enumerates literal simple six-cycle walks, checks all root collision identities,
and compares the resulting graph and numerical certificates. The universal
graph argument and observation-dimension implication are written proofs with
these finite premises, not proof-kernel theorems.

PR3147 supplies the dependent-triple claim and the incorrect intermediate
triangle formula audited here. PR3097 supplies the complete route-relator
argument; PR3168 supplies its independent Fano audit and the released request
to check the larger block claim. The earlier selected-centre packages supply
the owner-query model, source matrix, and observation-count lineage. This note
does not revisit PR3147's separate circle claims.

The result excludes compression within this fixed observation interface on
blocks of at most fourteen owners. It supplies neither a physical labelled
fifteen-owner construction nor a barrier for arbitrary centre sharing, changed
query interfaces, different geometry, supplier implementations or multiplication
algorithms. No selected exponent changes.

## Open next questions

- Can a fifteen-owner abstract equality graph be labelled by the actual routes
  with all required scalar column dependencies? Its graph-theoretic existence
  alone says nothing about that stronger realization problem.
- Can a changed observation or owner interface reduce the required information
  while keeping a complete chronological, routing, restoration and recursive
  cost account? Such a change needs its own quantified contract.
