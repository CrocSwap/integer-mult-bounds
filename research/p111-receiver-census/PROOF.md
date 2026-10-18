# Fixed-plan receiver census: scope and complete helper bill

The minimum helper count is **439**, attained by **2,646 of 19,683**
receiver assignments in one frozen P111 generator. This note proves why
ten small tables cover that complete domain. It is an optimality statement
only for the generator-defined class, not for bit suppliers or XOR circuits.

## Object and domain

The source is eumemic's PR555 generator in
`research/e8-bit-p111-tuned/code/gen_p3.py`, its frozen `data/plan-l3.json`,
and the parameters in `data/punct.json`. The punctured lines are
`P = [10,15,51,53,56,66,72,89,111]`. Freeze the free-keeper choices and
their assignment to D6 nodes produced by `plan_thirds` with seed 552.
Freeze all other construction rules, including the order and residual
convention in `express`, monotone missing-carrier closure, and junk-wire
reuse. Assignment seed 15 selects this investigation; it does not change
the inherited seed 552.

For each punctured line, its two eligible `(z,z)` D6 nodes may direct the
first, second, or both free keepers to its pseudo-target. Thus a receiver
choice is a vector in `{1,2,3}^9`, of size 19,683. The nine punctured lines
occupy distinct orthogonal four-frames. Their eighteen controlled D6 nodes
are therefore distinct, so no two entries overwrite one receiver choice.
The verifier must check these facts rather than infer them from the size
of P. Original receiver choices outside these eighteen nodes stay fixed.

Let B be a supplying D4 block and C its orthogonal complementary block.
The variable pseudo-targets served by B are the punctured lines in C:

| B | Variable pseudo-targets | Local assignments | Minimum extra cost | Minimizers |
|---|---|---:|---:|---:|
| 0 | 15, 66, 72 | 27 | 3 | 21 |
| 1 | 10, 51 | 9 | 1 | 9 |
| 3 | 56, 111 | 9 | 2 | 2 |
| 5 | 53, 89 | 9 | 4 | 7 |
| 2, 4, 6, 7, 8, 9 | none | one per block | 0 each | 1 each |

There are 60 local table entries. Their Cartesian product represents
all 19,683 global assignments, without identifying different circuits as
equivalent or sampling assignments.

## Why the tables separate

All source responses below are exact vectors over F2 on the 111 live
source coordinates. Punctured coordinates are absent. In particular,
a free keeper whose selected line is punctured has zero source response;
it still carries arbitrary helper dirt and is still charged as a helper.

Before the mini-nodes, the fixed cell/quad/D6 construction gives each
free keeper its fixed source response. A receiver choice for p in C
selects a designated free keeper in B and the desired replacement
response computed from p's hyperplane, d-single line, and D6 responses.
If both keepers are received, the second keeper's response is included
exactly as in the original generator. These data involve only B and C.

For a mini-node in B, the generator's ordered donor list contains B's
free keepers, B's extra carriers, and B's freed home sources. Retain the
original order, including the sequential order of pseudo-target writes.
An unsuccessful `express` call adds its precise residual coordinates to
B's missing set and skips that write. Rebuild from the original initial
responses after adjoining the missing carriers, as the original generator
does. This is not replacement by an arbitrary minimum-rank extension:
different residual or elimination conventions could select different
carriers and would define a different search class.

Each added carrier belongs to B. The missing-carrier update is monotone
and does not consult another block's variable state. A completed local
closure therefore depends only on the receiver choices for p in C.
The census records failures or nonconvergence if present; it must not
silently discard them as successful cases.

The subsequent D6 additions use those modified free keepers. Each live
target in C receives only the D6 responses and keeper responses determined
by this same local choice. Its remaining Q-part consequently depends only
on B's local table entry. Free-cell keepers and the home sources used by
the phase-B block node are distinct registers. Other mini-nodes cannot
alter these home-source responses. Geometry, the live port set, retained
totals, and complementary-block assignments are fixed.

Global helper numbers may shift when another block uses more carriers;
that relabeling does not change this dependence. The original donor order
within each class is retained. The local record must nevertheless match
the original generator on the selected parameters and checked variants.

## Complete helper count

The fixed allocation is 240 carrier registers, 180 cell-empty registers,
and nine pseudo-target totals: **429 helpers**. Puncturing does not remove
the two carrier registers allocated per original E8 line. Sources and
targets are separate and are not included in R.

For block B let e_B be its extra-carrier count, n_B its number of live
target outputs, and r_B the F2 rank of their Q-part source responses.
The phase-B generator appends a fresh independent dirt direction whenever
a required row is dependent. Exactly n_B-r_B such directions are needed:
every dependent row gets its own new coordinate; these coordinates cannot
create a new relation among the original source coordinates.

Let a_B count the extra carriers eligible for this reuse under the actual
generator predicate. Each eligible carrier has the same source response
as an available home source, so their sum supplies a zero-source dirt
direction. The generator uses each eligible carrier at most once. The
remaining newly allocated junk helpers are therefore

`j_B = max(0, n_B - r_B - a_B)`.

The complete count is

`R(choice) = 429 + sum_B (e_B(choice_B) + j_B(choice_B))`.

An extra carrier reused as junk is counted once, in e_B. Unused extra
carriers remain paid. Do not assume a_B=e_B without checking the original
eligibility predicate. Node elimination and randomized LU lowering occur
after these allocations and allocate no further helper registers; their
trial count cannot lower R in this fixed class.

Every global assignment is a choice of one entry per independent table.
Thus summing the per-table minima gives a lower bound on R for the entire
class. Concatenating local minimizing choices attains that bound whenever
the corresponding generator construction succeeds. Here the minimum is
`429+3+1+2+4=439`, with `21*9*2*7=2646` minimizing assignments. The complete
helper-count histogram is `{439:2646, 440:8127, 441:6642, 442:2052, 443:216}`.
The two implementations agree on the complete per-assignment record digest,
not only on this histogram. The selected receiver choice attains the minimum.

## Limits

This does not optimize the punctured set, skeleton plan, free-keeper
assignment, extra-carrier basis, greedy closure rule, register reuse
architecture, or frame schedule. A helper-count minimum need not minimize
ADDs, signed prefix growth, the recursive profile, or a hosted invoice.
Other assignments with 439 helpers may improve those quantities. Arbitrary
extra-carrier vectors and alternative elimination/residual rules are outside
the class, even if they implement the same endpoint. No such circuit is
excluded by this census.

Finite F2 source accounting and reconstruction do not discharge the
inherited arbitrary-dirt, frame, physical realization, whole-call hosting,
all-size compilation, precision/tape, or analytic transfer obligations.
A proposed supplier replacement still needs its complete checks and
invoice. This package does not change the selected frontier or claim a
new kappa, a practical runtime improvement, or a full multiplication proof.
