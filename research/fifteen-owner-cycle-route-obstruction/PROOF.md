# The four-six-cycle equality graph has no selected route labeling

The result is a scoped proof in the historical calls-0/4 whole-later-query
block-repair model. The scalar field is Q, R or C. The binary route matrices
act on distinct physical owners by regular right multiplication. These fields
and actions have different roles.

## Cited premises

Write r_p for column p of the selected eight-by-112 matrix R. The old and
required observations are

    Sx(g) = R x(g),
    Tx(d) = sum_p (r_p/4) x_p(d rho_p).

The following are mathematical inputs, credited to their original packages.
Their scientific verifiers and enumerations are not replayed here.

1. Sagar Thakrar's [PR #3291](https://github.com/CrocSwap/integer-mult-bounds/pull/3291),
   [proof](../centre-block-moore-bound/PROOF.md), derives the support incidence
   graph from a nonzero common-kernel vector. Each edge has its port label p
   and a nonzero scalar coefficient. Incident labels are distinct. At each
   vertex the incident columns have a nonzero linear dependence. Every simple
   six-cycle alternates between two labels forming one of the fifty braid
   pairs in the exact source-bound inventory. The graph has no four-cycles.
2. Nick Petalas's [PR #5182](https://github.com/CrocSwap/integer-mult-bounds/pull/5182)
   proves that support on fifteen source owners forces a cubic graph on
   fifteen vertices in each part, with disjoint six-cycles.
3. Krzysztof Wójt's [PR #5239](https://github.com/CrocSwap/integer-mult-bounds/pull/5239),
   [proof](../centre-equality-six-cycles/PROOF.md), proves that every such
   graph containing a six-cycle is isomorphic, preserving its two parts, to
   [the displayed graph](../centre-equality-six-cycles/WITNESS.json).

The third premise is a finite classification with a written coverage proof.
The corollary below inherits that premise. The exclusion of the displayed
graph itself needs only its listed incidence rows and named cycles.

## 1. Unique completion of a braid pair

**Finite lemma.** For every selected braid pair {a,b}, exactly one other
selected column r_c lies in span(r_a,r_b). Neither coefficient in its expansion
in those two columns is zero.

The standalone verifier establishes this new property by exact rational
arithmetic. It uses the predecessor extractor only to prepare R from the
authenticated canonical word. It takes the braid-pair inventory as cited
input. It does not run the predecessor's route, dependent-triple, graph or
subgroup census.

For each pair choose row indices i,j with

    delta = r_a[i] r_b[j] - r_a[j] r_b[i] != 0.

For each of the other 110 columns z, set

    u = z[i] r_b[j] - z[j] r_b[i],
    v = r_a[i] z[j] - r_a[j] z[i].

Test all eight coordinates of u r_a + v r_b = delta z. This is equivalent
to membership in the two-column span. The selected columns are rational,
so the same nonzero-minor and rank criterion works over R and C. All fifty
pairs have exactly one completion, with u and v nonzero. The command prints
the complete fifty-entry table and its input hashes. It checks 5,500 candidate
columns. The new lemma is stronger than merely bounding the number of braid
pairs in a dependent triple.

## 2. Propagation along six-cycles

Consider a cubic incidence graph satisfying the cited route and coefficient
conditions. Let C be one of its six-cycles. Its edges alternate between a and b.
At each vertex of C, the third edge must have a label c outside {a,b}, because
incident port labels are distinct. A nonzero three-column dependence forces
r_c into span(r_a,r_b). Section 1 makes c unique. Therefore all six edges
leaving C have the same label, denoted c(C).

Make an auxiliary graph whose vertices are the disjoint six-cycles. Join
two of them when an incidence edge connects them. That edge leaves both
cycles, so its single label equals both c(C) and c(C'). Hence c is constant
on every connected component of this auxiliary graph.

If a vertex outside the cycles has two neighbors on cycles in the same
auxiliary component, its two incident edges have equal labels. This violates
the distinct-incident-label condition. This implication is independent of
the numerical values of the nonzero edge coefficients.

## 3. The explicit contradiction

In the labels of PR #5239, the four cycles have the following vertex sets
on each side:

    C0 = {0,1,2}, C1 = {4,8,9},
    C2 = {5,10,11}, C3 = {7,13,14}.

The auxiliary graph contains the connected square

    C0--C1--C3--C2--C0.

For example, B1-D4 joins C0 to C1, B9-D13 joins C1 to C3,
B11-D14 joins C2 to C3, and B2-D5 joins C0 to C2. Thus every cycle
has the same external label c. But B3 has neighbors D0, D6 and D7.
D0 lies on C0 and D7 lies on C3. The two distinct edges B3-D0 and
B3-D7 must both carry c. This is impossible.

**Theorem.** The displayed four-six-cycle graph admits no labeling by the
selected routes with nonzero coefficients satisfying both local query
dependencies. Every graph isomorphic to it is excluded as well.

**Corollary, conditional on the cited classification.** Any nonzero
common-kernel perturbation on exactly fifteen source owners in this fixed
model must have a six-cycle-free incidence graph. An actual route search
may discard the nonzero-six-cycle equality branch. This does not exclude
the six-cycle-free branch or increase the fifteen-owner support floor.

## Limits and credit

This result answers the nonzero-six-cycle branch of PR #5239's route-realization
question. It does not assign routes to the remaining branch, change the
observation contract, establish a physical cost saving, or improve kappa.
The five selected framework assumptions remain. No selected cold replay,
native admission, Lean, Docker, independent human review or proof-kernel
formalization is claimed.

The new contribution is the unique-completion check and the forced-label
contradiction. Credit Krzysztof Wójt for the graph and its classification;
Sagar Thakrar for the route/column-to-graph theorem; Nick Petalas for the
equality reduction; and Matarener's PR #3656 for the distinct 4,080-owner
coset construction. Retain Ross Richardson #3071, dcharb78 #3147, Gonzalo
Mier #3097, Sudarsh Chaturvedi #3168, Aaron Wang/navinor, ywz65 and the
selected centre lineage for the query model, extraction and route premises.
All predecessor files and credit lines remain unchanged. Apache-2.0.
