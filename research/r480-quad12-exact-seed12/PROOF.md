# Fixed-transfer minimum, complete census and precision admission

The object is phase A, slice [849,872), at frame 314 of the pinned [PR503](https://github.com/CrocSwap/integer-mult-bounds/pull/503)/510 R480 word. In local order its six existing registers are [307,355,415,439,494,518]. Each elementary ADD changes one destination by adding a distinct source. Replacing these integer additions by XOR gives the actual bit circuit. The old and new programs have the same six-by-six positive integer matrix, so they agree modulo two on every incoming state, including arbitrary helper dirt. Their signed inverse matrices also agree exactly.

The fixed matrix is:

```text
3 2 3 3 1 1
3 3 4 3 1 1
2 2 3 3 1 1
3 3 4 4 1 1
1 1 1 1 1 0
1 1 1 1 0 1
```

## Minimum and exhaustive shortest-program count

Any positive unit-ADD program starts at the identity matrix and only increases entries. Every intermediate row therefore remains at least its corresponding identity row. Removing a possible last ADD subtracts one source row from one destination row, provided the result stays entrywise above the identity. This condition is necessary for every possible final gate. Conversely, a sequence of such subtractions that reaches identity reverses to a legal positive program. Repeated writes and arbitrary source/destination choices are allowed; no destination-once restriction is imposed.

Every subtraction strictly decreases total matrix mass. The backward graph is finite and acyclic. The adapted [PR925](https://github.com/CrocSwap/integer-mult-bounds/pull/925) row-tuple recursion examines every legal successor of each reachable state and computes its exact distance to identity. It visits 868,423 states and 5,005,248 edges. The minimum is 11. The stopping rule is complete graph exhaustion, with a one-million-state failure limit; the actual run completes below that limit. The seed 12 selects the object, not a random sample of this graph.

A separate flat-byte breadth-first implementation, also adapted and credited to [PR925](https://github.com/CrocSwap/integer-mult-bounds/pull/925), imports no search code. It checks the complete layers of depths zero through ten before first reaching identity at depth eleven. It visits 798,401 states and processes 4,163,706 edges from completed layers. Path multiplicities are accumulated when different gate orders meet the same state. Every shortest path has a shortest prefix, so retaining only minimum-depth arrivals loses no shortest program. This independently counts 252 shortest programs.

The supplied census has 252 distinct eleven-gate programs. Each is checked independently against the fixed target matrix. The independent total count, distinctness and validity together establish that the census contains every shortest program in this class. The census is not a proof about general Boolean circuits, signed additions, extra registers or different integer lifts.

## Four reverse classes and the local guard

The 252 programs fall into four classes with identical reverse positive matrices, of sizes 108, 72, 36 and 36. Every shortest program increases exactly three entries relative to the old reverse positive matrix. Thus none meets the entrywise reverse guard. [PR1002](https://github.com/CrocSwap/integer-mult-bounds/pull/1002) supplies a twelve-gate witness that does meet it after relabeling; the complete census independently corroborates the guarded minimum of twelve.

[PR1002](https://github.com/CrocSwap/integer-mult-bounds/pull/1002) has priority for the eleven-versus-twelve minimum statement. The explicit map from this package's local indices to its indices is [2,3,1,4,0,5]. The verifier checks equality of the original ordered gate lists after that map, not just an abstract matrix coincidence. No code from that pending contribution is executed. An overlap census tests all 60 R480 quads under all 720 wire permutations; only quad 12 has this exact positive transfer.

## Complete-word substitution and costs

Each replacement uses all six old registers at one unchanged frame, with no external read inside the replaced slice. Equal Boolean boundary states preserve every later read. C is rebuilt as the literal reverse of all z-destination gates in A and B at the full frame, preserving the inherited scalar-interface contract. No borrowed wire or unpaid operation is introduced. Every register follows its original ordered frame path; the independent record emitter and native checker verify this, including copy lifecycles and source restoration.

Twelve forward ADDs and twelve cleanup ADDs are removed. The complete cost, including dirt compensation, scatter, source reads, cleanup and frame operations, is 33,934 ADDs, 2,940 MOVEs, nine COPYs and nine ERASEs. The paid histogram and rank mass remain unchanged, so this is a finite scalar saving, not a recurrence-exponent improvement.

For precision, the checker interprets every emitted scalar instruction in both orientations with nonnegative bounds, including temporary copies and resets. The old forward/reverse maxima are 176,135 and 3,751,204. The four shortest-program classes have reverse maxima 3,723,720, 3,727,336, 3,723,748 and 3,729,576, respectively, with the same forward maximum. The inherited local envelope is 64 times F cubed times B squared; every class fits strictly below 2 to the power 104.

One representative suffices for each reverse class because its forward and reverse positive maps are identical to those of every member. Within either substituted block, positive additions are coordinatewise monotone, so the largest internal value occurs by the block's end. Identical boundary maps therefore give identical complete-word maximum bounds. Every census member is also checked to touch all six wires. Complete set-valued replay verifies the chosen word on all 720 input columns, and the unchanged C++ harness verifies the five-, nine- and eleven-stage formal columns.

This establishes only the stated finite contract and scoped minima. The native local envelope is not a newly certified whole-hosted invoice. All inherited physical, compiler, precision/tape and analytic assumptions remain; no proof-assistant certification of the multiplication theorem is asserted.
