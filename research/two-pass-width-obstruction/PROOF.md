# A minimum-order failure of the width-product test

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and exact statement

Records are distinct, initially ordered 0,...,n-1. A stable two-lane pass
assigns each record to one of two lanes and produces any interleaving of
the resulting streams that preserves each lane's incoming order. Empty
lanes are allowed. Records cannot be copied, deleted or modified. Routing
descriptions are unrestricted; this model charges passes only.

For a target record order p, let w(p) be its longest decreasing-subsequence
length. The following claims have different evidence:

1. The ten-record order p=(3,2,1,6,5,4,9,8,7,0) has w(p)=4 and needs
   exactly three stable two-lane passes. The arguments below are written
   combinatorial proofs; two separate finite exclusion engines corroborate
   the lower bound.
2. No order of at most nine records with w<=4 needs more than two passes.
   This is an exhaustive finite certificate at n=9, followed by restriction
   of its routes. Thus ten is the minimum possible order of an obstruction
   to sufficiency of the two-pass width-product bound four.

The universal width-product necessity and its general failure of
sufficiency are prior work. In particular Mark Karpilovskij,
[Composability of Permutation Classes, Theorem 15 and Question 16](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v26i1p41),
Electronic Journal of Combinatorics 26(1), P1.41, 2019, already states
I_k I_l is strictly smaller than I_(kl), where I_k is the class of
permutations partitionable into k increasing subsequences. That known
noninclusion is not claimed as new. The new repository result is this
explicit minimum-order certificate and routing obstruction. No historical
priority claim is made for the example or elementary methods.

## One-pass alphabet

A record order can be produced in one pass if and only if w<=2.
Necessity follows because a decreasing triple cannot share two stable
lanes. For sufficiency, assign each entry its longest decreasing-subsequence
length ending there. If an inverted pair had the same depth, appending
the second entry to a decreasing subsequence ending at the first would
increase its depth. Each of the at most two depth classes is therefore
in increasing record order and is a legal incoming lane stream.

If the first pass outputs record order a and the second uses the sequence
b of indices into that order, the final record order is a[b[i]]. Both a
and b must avoid a decreasing triple. Conversely any such pair supplies
two legal passes. This fixes the composition convention used by the checker.

## A forced four-cycle rules out two passes

Suppose a two-pass route exists for the displayed p. Give each record
its ordered pair of lane choices. Two records with the same pair retain
their initial relative order through both passes. Relabel the lanes of
each pass so that record 0 has pair 00. Every other record finishes before
0, although it starts after 0. Consequently none can have pair 00.

Each of the blocks {1,2,3}, {4,5,6} and {7,8,9} is reversed in p.
Its three records must have distinct pairs. They therefore use exactly
01,10,11, once each. Choose A with pair 01 in the first block, C with
pair 11 in the second block, and B with pair 10 in the third block.
Write <_M for the total order after the first pass.

- Record 0 and A share first lane 0. Their initial order forces 0 <_M A.
- A and C share second lane 1. Their final block order forces A <_M C.
- C and B share first lane 1. Their initial block order forces C <_M B.
- B and 0 share second lane 0. Their final order forces B <_M 0.

This is the impossible cycle 0 <_M A <_M C <_M B <_M 0.
It covers every lane assignment and every intermediate merge, including
empty lanes and choices dependent on the complete layout. No search
assumption or restriction on merge positions enters the argument.

The width is exactly four. A decreasing subsequence before the terminal
0 stays inside one of the three value-separated blocks, so it has at most
three records. Appending 0 permits four, for example 3,2,1,0.

## Three passes attain the endpoint

The following complete orders and lane-1 record sets describe the route.
The other lane contains every remaining record.

| Pass | Output record order | Lane-1 records |
|---|---|---|
| 1 | 1,2,3,4,5,6,7,8,9,0 | 0 |
| 2 | 2,1,3,5,4,6,8,7,9,0 | 2,5,8 |
| 3 | 3,2,1,6,5,4,9,8,7,0 | 3,6,9 |

For each row, both lane subsequences in the preceding order are identical
to those in the output. Hence every pass is legal. All record payloads
are transported intact. The lower bound makes this three-pass route optimal.

## Finite certificate that smaller obstructions do not exist

The checker generates the complete one-pass alphabet at order nine by
inserting the largest record into every smaller generated permutation.
A new decreasing triple must begin with that largest record. It exists
exactly when the suffix following the insertion contains a decreasing
pair. Thus the insertion is permitted precisely when that suffix is
increasing. Removing the largest record gives a unique predecessor, so
induction proves completeness and absence of duplicates.

A separately implemented scan of all 9!=362,880 permutations tests every
literal triple. Its one-pass set agrees exactly with the 4,862 generated
factors. The checker composes all 4,862^2=23,639,044 ordered factor pairs
and retains their complete set of final orders. Independently, a quadratic
longest-decreasing-subsequence dynamic program scans all 362,880 orders
and retains those of width at most four. The two sets are exactly equal,
with 261,808 elements. This set equality is the finite minimum-order
certificate; the count alone would not establish coverage.

For an order on n<9 records, append the remaining larger records in
increasing order. Its width stays at most four. The nine-record certificate
provides a two-pass route for this extension. Remove the appended records
from the initial, intermediate and final orders and from both lane streams.
Restriction preserves their relative orders, giving two passes on the
original records. Hence no smaller order is an obstruction. This argument
does not construct a uniform all-size routing controller from a width test.

As a second exclusion engine, every one of the 16,796 complete one-pass
factors a at order ten is tested. The unique possible second factor is
b=a^-1 p, and its decreasing width is always greater than two. This
corroborates the four-cycle proof without depending on the lane-type
argument. The verifier also visits all 4^9 normalized two-pass lane
assignments for p. Exactly 216 survive the necessary inverted-pair test;
every survivor has the displayed four-cycle, and an independently built
order graph is cyclic in every case.

## Scope

This is a finite routing certificate and a scoped combinatorial proof.
It supplies no physical stream controller, tape/head cost, workspace or
reversible cleanup implementation. More lanes, additional passes, record
copies, random access, a different routing model or a changed layout can
escape this obstruction. It is not an unconditional multitape lower bound,
a native supplier, an improved kappa, or a complete multiplication theorem.
