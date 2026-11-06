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
4. dcharb78's [PR #3147](https://github.com/CrocSwap/integer-mult-bounds/pull/3147),
   [README, Pillar 3](https://github.com/dcharb78/integer-mult-bounds/blob/5cbc48b18cb05327a8dacab3f626412d3bc5e924/research/centre-sink-duality-and-braid-quotient/README.md),
   states that every selected braid pair extends to exactly one dependent
   triple of distinct query columns. This is the cited unique-completion
   premise. Its exact source head is `5cbc48b18cb05327a8dacab3f626412d3bc5e924`.

The third premise is a finite classification with a written coverage proof.
The corollary below inherits that premise. The exclusion of the displayed
graph itself needs only its listed incidence rows and named cycles.

## 1. Propagation along six-cycles

Consider a cubic incidence graph satisfying the cited route and coefficient
conditions. Let C be one of its six-cycles. Its edges alternate between a and b.
At each vertex of C, the third edge must have a label c outside {a,b}, because
incident port labels are distinct. A nonzero three-column dependence forces
r_c into span(r_a,r_b). Cited premise 4 makes c unique. Therefore all six edges
leaving C have the same label, denoted c(C).

Make an auxiliary graph whose vertices are the disjoint six-cycles. Join
two of them when an incidence edge connects them. That edge leaves both
cycles, so its single label equals both c(C) and c(C'). Hence c is constant
on every connected component of this auxiliary graph.

If a vertex outside the cycles has two neighbors on cycles in the same
auxiliary component, its two incident edges have equal labels. This violates
the distinct-incident-label condition. This implication is independent of
the numerical values of the nonzero edge coefficients.

## 2. The explicit contradiction

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

## 3. Finite corroboration of the new implication

The verifier reads only the cited graph. It checks the named cycle boundaries,
constructs their auxiliary square and finds the repeated-label edges at B3.
It enumerates all 256 assignments of four colors to the four external cycle
labels. Exactly four obey the square's edge equalities, and none gives
different labels to B3-D0 and B3-D7. This finite color domain loses no label
equality pattern, since four cycle labels use at most four distinct values.
The written argument above proves the implication directly for any label set.

No predecessor query, route, rank, graph-classification or subgroup census
is part of the registered replay. Unique completion is inherited, rather
than a new claim or a validation deliverable.

## Limits and credit

This result answers the nonzero-six-cycle branch of PR #5239's route-realization
question. It does not assign routes to the remaining branch, change the
observation contract, establish a physical cost saving, or improve kappa.
The five selected framework assumptions remain. No selected cold replay,
native admission, Lean, Docker, independent human review or proof-kernel
formalization is claimed.

The new contribution is the forced-label contradiction and its application
to the equality branch. Credit dcharb78 for unique completion;
Krzysztof Wójt for the graph and its classification;
Sagar Thakrar for the route/column-to-graph theorem; Nick Petalas for the
equality reduction; and Matarener's PR #3656 for the distinct 4,080-owner
coset construction. Retain Ross Richardson #3071, dcharb78 #3147, Gonzalo
Mier #3097, Sudarsh Chaturvedi #3168, Aaron Wang/navinor, ywz65 and the
selected centre lineage for the query model, extraction and route premises.
All predecessor files and credit lines remain unchanged. Apache-2.0.
