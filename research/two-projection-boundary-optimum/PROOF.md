# Exact minimum frame cost over all readout-boundary choices

## Statement

Fix the ten source events

```text
B0 B1 B0 B1 B2 B3 B4 B2 B4 B3
```

The helper pair has state in `F2^2`. Sources `B0,B1,B2,B4` inject in
direction `(1,0)` and `B3` injects in direction `(1,1)`. Each readout is a
paired use of one of the covectors `(1,0)` (the `all` projection) or `(1,1)`
(the `regular` projection). The only paid frame changes are the row shears

```text
u0 = [[1,1],[0,1]]       u1 = [[1,0],[1,1]].
```

There are eleven boundaries, numbered 0 through 10. A boundary-readout node
is one pair `(boundary, projection)`, so there are 22 possible nodes. The
claim proved here is:

> Among all node sets that can provide a paired readout for every nonzero
> five-bit source mask, the least possible number of paid row shears in a
> legal frame schedule is exactly 10.

This optimizes every choice of the two boundaries for every output mask, for
this fixed source word, source-direction assignment, two projection vectors,
and two shear generators. It does not optimize over other source words or
operation alphabets.

## 1. Boundary nodes characterize all paired readouts

Write `a_s` for the XOR of source labels in the first `s` events. Write `r_s`
for the same XOR with label 3 omitted. These are respectively the `all` and
`regular` projected source prefixes. For a fixed projection `p`, two calls to
the same output map at boundaries `s<t` cancel the arbitrary initial helper
contents and contribute the source mask `p_s XOR p_t`.

Let `S` be a set of requested boundary-readout nodes. Define the nonzero
mask coverage

```text
Cover(S) = {a_s XOR a_t : (s,all),(t,all) in S, s<t, a_s != a_t}
         union {r_s XOR r_t : (s,regular),(t,regular) in S, s<t, r_s != r_t}.
```

Then `S` supports all 31 nonzero output masks exactly when
`{1,...,31} subset Cover(S)`. Necessity follows because each output is read
twice in one projection and the two boundary prefixes must differ by its
mask. Conversely, for every mask in `Cover(S)`, choose a witnessing same-
projection pair and use those two boundary calls on that output row. Several
outputs can use the same boundary node: their target rows are distinct, and
the calls leave both helper rows unchanged. This produces exactly two
readouts per output. The outputs therefore impose no capacity constraint on
the nodes beyond the availability of their required frames.

## 2. Complete enumeration of node sets

Represent the `all` nodes and `regular` nodes by two 11-bit integers `A,R`.
There are exactly `2^11 * 2^11 = 4,194,304` such pairs. For each projection
and each 11-bit subset, the checker computes the difference set incrementally.
If `i` is the newly added boundary and `T` is the previous subset, the
recurrence is

```text
Cover(T union {i}) = Cover(T)
                    union {p_i XOR p_j : j in T and p_i != p_j}.
```

This recurrence lists each unordered boundary pair once, so every set and
every nonzero pairwise difference is included. Equal prefix values produce no
mask bit because zero is not a requested output. The checker records every set whose cover
contains all 31 nonzero masks. It finds 848 such sets; their total node-count
histogram is recorded in `RESULT.json`.

## 3. Exact frame-transition cost

The legal frames are the six invertible 2 by 2 matrices over `F2`, namely
`GL(2,F2)`. The generators `u0,u1` each cost one full-row XOR and generate
this group. Breadth-first search from identity computes the exact shortest
word length `d(g)` for every group element. Moving from frame `F` to frame
`G` costs exactly

```text
d(G F^-1).
```

The equality is exact: any physical row-XOR sequence inducing the transition
is a word for `G F^-1`, so has at least its shortest-word length; a shortest
word realizes the transition.

At a boundary requesting `all`, the frame must have first row `(1,0)`; for
`regular`, it must have first row `(1,1)`. If both are requested, either
ordering is legal and the dynamic program checks both. At source event `B_j`,
the current frame must send its fixed injection direction `v_j` to `(1,0)`.
The dynamic program processes these constraints in chronological order,
minimizes the sum of exact transition distances, and includes the final
return to identity. Every legal schedule induces one of these state paths;
every path considered is realized by shortest row-shear words. The dynamic
program therefore returns the exact minimum for each node set, not a bound on
a relaxation.

## 4. Result and attainment

Across all 4,194,304 node sets, exactly 848 support all nonzero masks. Their
minimum costs have histogram:

| Full-row XORs | Supporting node sets |
|---:|---:|
| 10 | 38 |
| 12 | 248 |
| 14 | 386 |
| 16 | 176 |

Thus every valid assignment requires at least 10 row XORs. The retained
two-projection certificate in `two-projection-connector-seed51a5` supplies
one valid node set and chronological schedule costing 10, so the lower bound
is attained. The checker independently verifies all 31 pairs of that witness
against the prefix recurrence and recounts the schedule's shortest transition
costs.

## 5. Scope boundary

The result is exact only for this finite interface model. The source word,
source directions, readout covectors, number of helper rows, and allowed
generators are fixed above. The enumeration does not include other ten-event
words, another choice of the special source, more projections, other row
operations, additional helpers, or non-paired readout schedules. It is not a
lower bound for all two-row connectors.

The exact value 10 counts full-row XOR operations. It does not compare their
physical cost with a rank-one multiplication child, and it does not show that
the extra dirty helper row or frame schedule can be hosted in the selected
supplier. No kappa change follows.
