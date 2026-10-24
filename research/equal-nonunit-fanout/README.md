# Exact equal-nonunit dirty-fanout tariffs

Scoped written proof with exact finite corroboration; no new κ.
For demand `(2,2,2)` over `Z/4`, the exact destination-priced dirty-fanout
frontier consists of seven count vectors. More generally, every common
nonzero demand over a commutative unital ring has the tariff below, at every
row count and every positive stationary coefficient-independent price.

This settles the first all-nonunit example in lee-phys's
[#5163](https://github.com/CrocSwap/integer-mult-bounds/pull/5163), whose theorem
requires a unit demand. Krzysztof Wojt's
[#5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045) already settles
two rows. The new scope is equal nonzero demands on arbitrarily many rows,
including three or more nonunit demands. The return argument and echo
construction retain their predecessor credit.

## Contract and result

Let R be a commutative unital ring with `1 != 0`, let `lambda != 0` in R,
and let `q,w >= 1`. There are q arbitrary independent dirty rows
`a_i in R^w` and a preserved disjoint source `p in R^w`. Require

    A_i = a_i + lambda p,   for every 0 <= i < q.

The allowed finite straight-line gates are

    P_i(beta):    A_i <- A_i + beta p,       price mu_i > 0;
    E_ij(alpha):  A_i <- A_i + alpha A_j,    price c_i > 0, i != j.

All nonzero coefficients and ordered row pairs are available. Prices are
stationary, coefficient-independent complete abstract prices. An ADD's price
depends only on its destination. Zero-coefficient gates can be deleted.
Every original dirt column must return. There are no extra rows, cleared
registers, observations, adaptive choices or free basis changes.

For a nonempty subset S of the q rows define

    V(S) = (P_i = 1 if i in S else 0;
            K_i = 0 if i in S else 2),

where K_i counts all incoming ADDs at i. Then

    OPT = min over nonempty S [sum_(i in S) mu_i + 2 sum_(i not in S) c_i].

Exactly the `2^q-1` vectors V(S) form the Pareto frontier of aggregate source
and destination counts. Each vector is uniquely cheapest at some strictly
positive price vector. Equivalently, with `a_i=min(mu_i,2c_i)`,

    OPT = sum_i a_i + min_i (mu_i-a_i).

This last expression takes O(q) arithmetic/comparison operations after the
prices are supplied. It does not price the physical implementation of a gate.
The common demand can be a nonunit or a zero divisor. No division by it is used.
For the excluded zero-demand case the empty word has optimum zero.

For `(2,2,2)` over `Z/4`, the complete seven-term answer is

| Source support S | Exact price | Counts `(P0,P1,P2,K0,K1,K2)` |
|---|---|---|
| `{0}` | `mu0+2c1+2c2` | `(1,0,0,0,2,2)` |
| `{1}` | `mu1+2c0+2c2` | `(0,1,0,2,0,2)` |
| `{2}` | `mu2+2c0+2c1` | `(0,0,1,2,2,0)` |
| `{0,1}` | `mu0+mu1+2c2` | `(1,1,0,0,0,2)` |
| `{0,2}` | `mu0+mu2+2c1` | `(1,0,1,0,2,0)` |
| `{1,2}` | `mu1+mu2+2c0` | `(0,1,1,2,0,0)` |
| `{0,1,2}` | `mu0+mu1+mu2` | `(1,1,1,0,0,0)` |

At `mu=(1,9,9)` and `c=(1,1,1)`, the exact optimum is five, attained by

    E_10(-1), E_20(-1), P_0(2), E_20(1), E_10(1).

## Proof over arbitrary ring size and row count

Write M for the q-by-q matrix of original dirt coefficients. It starts and
ends at I. Every prefix is invertible, since P leaves M unchanged and every
E has its negated-coefficient inverse. Testing free input coordinates gives
these matrix equalities even when R has zero divisors.

A row cannot receive exactly one nonzero ADD. If row i had its only incoming
ADD `E_ij(alpha)` at prefix M, its dirt row would change from e_i to
`e_i+alpha m_j`. No later operation into i could restore it. Thus restoration
would require `alpha m_j=0`. Multiplying on the right by the inverse prefix
matrix yields `alpha e_j=0`, so alpha=0, a contradiction. This is the credited
incoming-row return lemma of #5163 and its #3063/#4916 lineage. It counts total
arrivals, without asserting that each individual directed edge occurs twice.

Let S be the rows receiving at least one source insertion in an arbitrary
valid word. S is nonempty, since without insertions the source column stays
zero, whereas its required endpoint is the nonzero common value lambda.
For i in S, the word pays at least mu_i. For i outside S, its source
coefficient starts at zero and must become lambda, so it receives an ADD.
The return lemma forces at least two arrivals, costing at least 2c_i.
These disjoint row bills show that the word's count vector dominates V(S)
and its price is at least the displayed minimum. Repeated insertions,
feedback, cancellation and arbitrary interleavings are covered.

Conversely, choose any nonempty S and any r in S. For every i outside S,
prepare `E_ir(-1)`. Execute `P_r(lambda)`. Undo the preparations in reverse
order with `E_ir(1)`, then execute `P_i(lambda)` on every other i in S.
An echoed row becomes

    (a_i-a_r) + (a_r+lambda p) = a_i+lambda p.

The chosen row and directly inserted rows also end correctly. Every dirt
column returns, and the count vector is exactly V(S). This proves attainment.
Its literal inverse reverses the gate order and negates every coefficient,
with the same abstract prices.

Different V(S) are pairwise incomparable. Every realizable vector dominates
one of them, and every one is realizable, so they are exactly the Pareto
frontier. To expose a particular S uniquely, put c_i=1 for every row,
mu_i=1 on S and mu_i=9 elsewhere. Including a row of S reduces its local cost
from two to one; including any other row increases it from two to nine.
The unique minimizing source support is therefore S.

Finally, for a chosen inserted root r, every other row may independently
choose its cheaper direct or echo bill a_i. This gives
`mu_r + sum_(i != r) a_i`. Minimizing over r proves the O(q) formula.

## Exact finite evidence and reproduction

The standalone standard-library verifier imports no predecessor code.
It checks 23,433 attaining words and their literal inverses, accounting for
298,716 formal-column executions, over `Z/n` for n=2 through 12 and the
non-chain local ring `F2[e,h]/(e^2,eh,h^2)`. Rows range from one through six;
every nonzero common demand, nonempty insertion support and allowed chosen
root is enumerated. The ring checks examine 6,595 element triples.

For the seven `Z/4` witnesses it also enumerates all 256 scalar assignments
to the three dirt rows and the source, totaling 1,792 assignments with both
forward and inverse checks. There are 480 heterogeneous-price comparisons
and 120 separately exposed frontier vectors across the six row counts.
Seven rejecting controls and positive source-insertion/inverse controls pass.

An independently implemented flattened-matrix interpreter certifies seven
three-row `Z/4` minima by exhaustive forward/reverse balls. For each nonempty
S use mu_i=1 on S, mu_i=9 otherwise, and c_i=1 everywhere. The attaining
cost is `6-|S|`, between three and five. Any cheaper word excludes price-nine
gates, so every remaining gate costs one. The two balls of total radius
`5-|S|` are disjoint. They contain, by source-support mask, respectively
`(299,299), (299,299), (25,381), (299,299), (25,381), (25,381), (28,28)` states.
All nonzero modular coefficients and all six ADD directions are available.
These are complete lower-cost searches, rather than an arbitrary depth cap;
they are not an enumeration of the entire affine state graph.

From the repository root, run

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/equal-nonunit-fanout
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/equal-nonunit-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/equal-nonunit-fanout/verify.py
```

Expected output includes `PASS_EQUAL_NONUNIT_FANOUT`. Each run prints a generated
JSON receipt with the evidence counts and SHA256 hashes of all five package
files. No receipt is handwritten. The universal claim rests on the written
proof; finite checks corroborate the stated finite domains. Independent human
and formal proof-kernel review are unclaimed.

## Scope, sources and overlap

Scientific base is canonical main
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7. The historical
`bit-helper-contract` card is marked changed in TASK.json. Its native H2/K
question is replaced by #5163's explicit all-nonunit tariff handoff; the card's
original example is not replayed, because that would not answer this task.
The handoff's first working example is the `(2,2,2)` case above.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145537)
records the question before substantial work. Entry coverage included live
open PRs and this account's recent submissions, recent handoffs and active
Discussions, distinctive main README and merged-PR searches, and cached
snapshots of 314 open PRs and 4,389 Discussion records. The local cached scan
covered 151 of 6,996 note paths before widening; arbitrary diffs and unpublished
work remain unsearched. A lack of matches is not a novelty certificate.
Exact historical predecessor documents are provenance-pinned in SOURCES.json;
none is an executable input or a rechecked deliverable.

No unequal-demand classification, general directed-edge tariff, extra dirty
workspace theorem, physical caller, complete supplier invoice, native/tape or
precision admission, selected-frontier change or multiplication theorem is
claimed. The selected κ remains 0.00302015. Lean, Docker and selected supplier
cold replay are outside this algebraic contribution and were not run.

## Open next questions

1. Determine the destination-priced tariff for `(e,h,e+h)` in the eight-element
   square-zero ring. This is #5163's second all-nonunit example, whose demands
   are not common multiples of one unit-normalized coefficient. Start with
   source-support lower bounds and the generated demand ideal. The missing
   multi-insertion sharing argument blocks applying this theorem.
2. Determine the all-positive directed-edge tariff for `(2,2,2)` over `Z/4`.
   Destination totals lose which source supplied an arrival. Start with a price
   matrix whose cheap edges form a directed cycle and an explicit restoring
   word; a matching directed-cut lower bound is still missing.
3. Supply one physical caller's complete stationary tariffs. Source access,
   coefficient application, routing, frame changes, precision and restoration
   must all be paid before this abstract optimum implies any supplier gain.

## Engineering constraints

The verifier has no recursion, external imports, background processes, solver,
network access or dynamic code evaluation. Every loop has a finite domain:
12 ring fixtures of size at most 12, at most six rows, 63 source supports,
six chosen roots, at most eleven common-demand values and 80 price fixtures
per row count. Words have at most eleven gates and formal rows seven entries.
Each oracle ball has radius at most two and at most 27 gates, so at most
757 candidates are stored per ball. Python exact objects, sets, dataclasses
and JSON allocate dynamically, a managed-runtime deviation from Power-of-Ten
rule 3. Live collections and integer sizes are bounded by these fixed fixtures;
standard-library allocation internals are not audited. Functions are kept
below 60 physical lines; warning-strict normal and optimized replay is
registered. Internal checks use explicit exceptions and remain active under -O.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0. Credit lee-phys
#5163 for the explicit `(2,2,2)` handoff and incoming-row formulation; Krzysztof
Wojt #5045 for source-count classification and nonunit two-row constructions;
Nick Petalas #4916 for the ring-valued free-module contract; Ross Richardson
#3063/#3121 for destination/edge tariffs and dirt restoration; Cinna Davis
#1944/#1968, Anthony #774, Oscar Fennell #759, Tekalign #3130 and the retained
common-source fanout lineage. The new claim is the common-nonzero-demand
arbitrary-row destination-price theorem and its exact frontier, rather than
priority for the credited return lemma or echo construction.
