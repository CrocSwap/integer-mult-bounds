# Exact partial acquisition on a cactus

This proof was produced by Nick Petalas. Apache-2.0.

## Model and theorem

Let G=(V,E) be a finite simple undirected cactus graph. Distinct simple
cycles may meet at vertices, but each edge is in at most one simple cycle.
Disconnected graphs and isolated vertices are allowed. An edge e={u,v}
offers the binary query q_e=x_u+x_v, with nonnegative acquisition price c_e.
Each source x_v is arbitrary and unknown to the decoder. It sees only
purchased replies. A purchased set S pays sum_(e in S) c_e once;
linear reconstruction of the requested targets is free in this relaxation.

Write B for the vertex-by-edge binary incidence matrix. Let the columns of
T be any finite list of requested coefficient vectors, including zero or
dependent columns. Thus the target responses are T^t x. They are feasible
exactly when each column has even parity on every connected component.
The statement holds coordinatewise for source fields of every positive
binary row width. This is not a price for their physical realization.

Choose any spanning forest F and any coefficient matrix R with BR=T.
For an edge e let r_e denote row e of R. Let C range over the simple
cycles and let E_br be the bridges. Then the exact minimum acquisition bill is

```text
OPT(T) = sum_(e in E_br, r_e != 0) c_e
       + sum_C [sum_(e in C) c_e - max_z sum_(e in C, r_e = z) c_e].  (1)
```

Here z ranges over binary rows of length equal to the number of targets.
It suffices to consider labels r_e actually appearing on C. In particular,
there is no enumeration of target superspaces or a bounded-codimension
hypothesis. The expression is independent of the chosen solution R.

For each cycle choose a maximizing label z_C. Keep bridge e exactly when
r_e is nonzero. On C keep e exactly when r_e+z_C is nonzero. These edges
and the modified coefficient rows give an attaining reconstruction. The
constructor can choose an attaining set that is a forest.

## Incidence solutions and the lower bound

For any graph, the columns of a spanning forest are independent. A nonempty
edge subset of a forest has a leaf of degree one in its nontrivial support,
so its incidence sum cannot be zero. Repeated leaf elimination also represents
every vertex vector having even parity on each component. This proves the
feasibility criterion and rank B=|V|-number of components.

Deleting one edge from each simple cycle of a cactus leaves a spanning forest.
Connectivity survives each deletion along the remainder of that cycle. No
cycle survives, because every surviving simple cycle would have been one of
the cycles just cut. Consequently the number of simple cycles is
|E|-|V|+number of components.

The incidence vector gamma_C of a cycle is in ker B. These vectors have
disjoint nonempty edge supports, hence are independent. The dimension
calculation shows that they form a basis of ker B. Thus every solution D of
BD=T has, independently for each target column, a unique cycle-basis expansion
relative to R. In row form this says

```text
D_e = r_e                     on bridges,
D_e = r_e + z_C                on the edges of cycle C.             (2)
```

There is no interaction between the choices z_C, including when two cycles
share a vertex. This is where the cactus hypothesis is used.

If S purchases enough queries, choose one reconstruction of every target
using S. Its coefficient matrix D has zero rows outside S. Since prices are
nonnegative,

```text
cost(S) >= sum_(e: D_e != 0) c_e.
```

Conversely, the support of any solution D is a feasible purchased set with
that support bill. The optimum is therefore exactly the minimum support bill
among all solutions of BD=T. By (2), a bridge's contribution is fixed, while
a cycle with shift z pays its total price minus the price of the rows equal
to z. Independent cycle minimization gives (1). An absent label saves zero;
a present label has nonnegative saved price, so one present label maximizes.
This proves the lower bound, including zero prices and an empty target list.

## Construction, certificate and independence of choices

Start with a spanning forest and give all nontree edges coefficient zero.
At each vertex pack its entries in the target columns into a binary row.
Process forest vertices from leaves to roots. Put the current vertex row on
its parent edge and add it to its parent's row. The residual at a root is
exactly the target parity on its connected component. All residuals vanish
if and only if T is feasible, and the resulting R satisfies BR=T.

Construct each fundamental cycle from a nontree edge and its forest path.
In a cactus these are precisely the edge-disjoint simple cycles. Group the
rows on each cycle by equality, total the prices in every group, choose a
maximum-price group, and apply (2). The displayed reconstruction proves
attainment. At least one edge disappears on each cycle because the chosen
label appears there, so the selected support is a forest. No cycles outside
this list exist.

The certificate records R, the cycle edge lists, each shift and saved price,
the modified rows, selected edges and bill. The checker reconstructs the
forest solution and cycles, checks every row relation, compares the chosen
saving against every present bucket, and verifies BD=T directly. Its
optimality implication is the proof above. It does not invoke the optimizer
or solve another acquisition problem. The decomposition routines are shared;
the finite subset oracle instead uses literal XOR spans and an independent
simple-cycle enumeration.

Replacing R changes each cycle's rows by a common translation, which merely
permutes its bucket labels; bridge rows do not change. Formula (1) is therefore
independent of R. Different spanning forests have the same consequence.
No assumption about a particular target basis or its rank is required.

## Small improvement and boundary

Take the triangle 01,12,02, with prices 4,3,2, and request x_0+x_1.
Its cheapest whole-span basis consists of edges 12 and 02 at price five;
both answers are needed to reconstruct this target from that basis.
The exact partial-target optimum is the direct edge 01 at price four.
With both independent triangle targets requested, formula (1) instead pays
five, as it should. These numbers are enumerated by the new verifier.

A general graph still has a cycle-space parametrization, but overlapping
cycle edges couple its shifts. Formula (1) is not asserted there. This
result does not optimize reconstruction XORs, storage, chronology, source
mutation, nonlinear observations, native frames, delivery or restoration.
A favorable acquisition bill alone supplies no complete recursive invoice.

## Credit

Ali Romman's [PR #5791](https://github.com/CrocSwap/integer-mult-bounds/pull/5791)
poses the partial-target boundary of whole-span binary query acquisition.
The new step here is the exact arbitrary-target cactus formula and its
certificate. Classical graphic cycle spaces, parity, linear reconstruction
and weighted grouping retain their usual credit. No literature-wide priority
for these ingredients or their general optimization setting is claimed.
Nick Petalas #5878 and #6654 are related general-pool results, not premises
or algorithms used in this proof.
