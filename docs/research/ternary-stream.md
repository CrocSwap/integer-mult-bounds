# Streaming producer deliveries through nested frames

This working note documents the register compiler in
`scripts/experiments/ternary_stream_reuse.cpp` and its exact small controls in
`scripts/experiments/ternary_stream_scratch.py`. It changes physical register
allocation, using the existing cancellation-free ternary scalar DAG and the
already audited rational source/dual frame cut. It does not require a new
scalar identity or a changed center map.

## One wire can supply successive consumers

Suppose a binary gate b computes a+x and another gate c computes a+y. If x is
an ancestor of y in the exact cancellation-free DAG, its source support is a
subset of y's. Consequently the source support of b is a subset of c's.
The implementation enumerates such ancestors to a fixed depth and records
only actual addition pairs present in the DAG.

The earlier gate b must be in the source region. If c is also a source gate,
its rational source frame contains b's. If c is a dual gate, every original
source indicator of c is orthogonal to every reachable side-target indicator
of c, by the exact intersection-two output support and cancellation-free
computation. Thus the source span of b is contained in the source span of c,
which is contained in c's assigned dual frame. Both cases permit the same
physical wire containing a to be used at b and then at c, with a nondecreasing
frame. No corresponding claim is made for a continuation starting at a dual
gate; those are excluded.

For ordering, process all source nodes by increasing source-support cardinality,
breaking ties by node ID, and then process all dual nodes in their original
topological order. The source region is ancestor-closed. Every original edge
within the source region strictly increases support cardinality, since the two
nonzero source supports of each sum are disjoint. A selected source-to-source
continuation also strictly increases cardinality; a source-to-dual continuation
respects the phase order. All original dual edges respect node order. The
combined computation and continuation constraints therefore have a valid
schedule, including after the exact star rewrite.

## Matching chooses compatible continuations

A delivery is a pair `(value, consumer input position)`. A candidate continuation
from a delivery at b to a delivery at c uses the same value at both gates and
has the certified frame inclusion above. Build a bipartite graph:

* A left vertex represents one binary gate b.
* A right vertex represents one input delivery at c.
* An edge selects the allowed continuation of one of b's input values to c.

A matching permits at most one input to continue beyond b and permits at most
one predecessor for each delivery at c. Thus at least one input at every sum
gate is at its final use on its physical wire. Overwrite that input with the
sum and preserve the other input. The local operation `(a,x) -> (a,a+x)` or
`(a,x) -> (a+x,x)` is invertible over F3. Any necessary additional output
channels are formed by adding the new sum into fresh dirty registers; these
copies are also invertible.

The selected continuations form paths of deliveries of the same scalar value.
They cannot form cycles because their schedule order strictly increases.
Each designated side output or retained center output is a separate protected
channel and is never used by a later consumer. The implementation assigns the
base output register to one channel and allocates one fresh register for each
remaining channel.

Let A be the number of active binary additions, q the designated output count,
v the input count, and s the matching size. Before linking, the total number
of outgoing deliveries, including designated outputs, is 2A+q. Every link
reduces the number of channels by one. Every active value has at least one
channel. There are v+A values, so the explicit allocation uses

    R = v + ((2A+q-s) - (v+A)) = A+q-s.

This is also checked independently by materializing every physical channel and
register in the full target-size DAG. The matching algorithm maximizes s within
the enumerated candidate graph. The graph is only a sufficient set of valid
frame inclusions; its maximum does not claim optimality among all possible
register compilers.

## Arbitrary dirty registers and exact signal map

No discarded input register is cleared or treated as a clean new register.
A continued input remains unchanged until its last use. A retired input keeps
its garbage and is left untouched until the inverse computation. A fresh
register means a distinct physical role, whose initial scratch content can be
arbitrary.

With zero auxiliary input except the injected source signals, induction along
the schedule gives the original scalar value at each delivery and every
designated output. Every local operation is linear and invertible on all its
registers. Therefore the producer is an invertible linear map L with exactly
the original signal transfer JLV. For arbitrary initial scratch z, the
transparent wrapper subtracts JLz, adds the input through V, then adds
JL(z+Vx); the difference is JLVx. Applying the inverse producer and removing
the source injection restores z exactly. The same argument applies to the
reversed invocation and the retained three-shear exchange. The small controls
evaluate every input and dirty-scratch basis simultaneously over F3, including
the forward/inverse wrapper and corrected bank exchange.

## Physical frame audit and rank sum

At every producer gate all participating physical roles are assigned its
previously certified nondegenerate frame. The full-size allocator checks every
incoming role transition. Its preceding frame must be either its value's
original producer frame, giving an original DAG inclusion, or the earlier gate
of its selected continuation, giving the inclusion proved above. Fresh roles
start at the zero frame. Output roles are checked to end at their designated
producer node, so a center or side output cannot silently acquire a larger
frame. Inverse gates use the same scalar inverses. Complementing the frame
sequence and reversing the schedule preserves nestedness and nondegeneracy.

The retained physical wrapper then has exactly its original descents: each of
the C(h,2) protected center outputs has dimension h-2. Their total downward
rank is L=C(h,2)(h-2). All other frame changes are nondecreasing in the relevant
orientation. The sum of changes in frame dimension telescopes over every
physical role. Initial and final endpoint dimensions give net change
`(2v+R)h-2v`; absolute rank charges add twice the downward rank. Consequently
each invocation orientation has total physical rank

    (2v+R)h - 2v + 2L.

This is an exact consequence of the checked complete physical allocation and
the audited nested-frame/endpoint proof, not a sample of edges or an estimate
from the addition count. At h=28, L remains 9,828 regardless of the matching.

## Working controls and current measured counts

The original direct h=8 producer changes from 546 to 454 roles at ancestry
depth one. Exact rational frame checks in both invocation directions give
loss 168 and total rank 4,752. All 566 data/scratch basis symbols pass the
full dirty wrapper. At h=10, depth four with source-to-dual continuations gives
7,642 to 6,952 roles, loss 360, total rank 74,776 in both directions, and
7,456 basis symbols checked through the full wrapper.

For the selected h=28 split followed by the exact star rewrite, depth four with
source-to-dual continuations has 1,874,692 candidate links and a matching of
878,674 links, including 39,045 ending at dual gates. It changes 9,925,832 raw
roles to 9,047,158 physical roles. The explicit schedule checks 18,775,674
ordinary and 878,674 reused input-frame transitions, protects every designated
output, and gives rank sum 258,647,200 in each orientation. These values depend
on that exact rewritten DAG; savings from other DAGs are not added to them.

The stream command is:

```sh
c++ -std=c++17 -O3 scripts/experiments/ternary_stream_reuse.cpp -o /tmp/ternary-stream
/tmp/ternary-stream DAG.bin TARGETS.bin 4 LINKS.bin mixed
python3 scripts/experiments/ternary_stream_scratch.py --h 10 --depth 4 --mixed
```

`DAG.bin` must come from the independently checked exact producer/rewrite.
`TARGETS.bin` is the matching source/dual audit's target export, containing the
delayed source flags. The optional final argument `mixed` enables continuations
from source gates into dual gates. Without it both endpoint gates must lie in
the source region. The integrated construction driver is responsible for
binding these inputs to their support and frame certificates.
