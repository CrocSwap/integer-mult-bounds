# Exact transition and witness preservation

## Declared model

Let d>=1 and m>=0 be integers. Use precisely PR1523's observable
dirty-connector correction model. A state
k in F2^d records the correction carried by the connector at one prescribed
observation. Coordinate j has positive complete correction price w_j.
Its distance is D(h,k)=sum_j w_j [h_j != k_j]. At stage i a reader a_i and
demand b_i require a_i dot k=b_i, unless an independently priced output
correction pays v_i for the one-bit defect. The initial and terminal states
are zero. Sources execute their prescribed restored mutation tour. This proof
changes how the existing preparation recurrence is evaluated; it assumes the
predecessor's correspondence between that recurrence and legal complete words.

Write F_i(k) for the minimum prefix price and p_i(k) for the lexicographically
smallest minimum-price state sequence ending at k. All such sequences have
length i. Initially F_0(0)=0, p_0(0) is empty and other states are unreachable.
For a given destination k, the predecessor scan minimizes

    (F_(i-1)(h) + D(h,k), p_(i-1)(h)).

The stage penalty depends only on k, so adding it does not change the selected
predecessor. Appending k also preserves the predecessor order. In connector-only
mode, delete the states with nonzero defect. In paid-output mode, add v_i times
the defect. These are exactly the original filtering and penalty rules.

## Hypercube invariant

Give each reachable prefix a distinct integer rank r(h), in its complete
lexicographic path order. Initialize mask h with the label
(F(h),r(h),h), or infinity if it is unreachable. Process coordinates in fixed
order. For each pair of masks differing only in coordinate j, simultaneously
replace the two labels with their minimum against the opposite label plus
w_j. The rank and origin fields travel unchanged.

After processing a coordinate set J, the label at k is the lexicographic minimum

    (F(h) + sum_(j in J) w_j [h_j != k_j], r(h), h)

over precisely those h equal to k outside J. Induct on the processed set.
The states equal to k in the newly processed bit come from its old label.
The remaining states come from the opposite endpoint's old label plus that
bit's price. Those two sets partition the possible origins. Their minimum is
the stated new label. Taking both old endpoints before either assignment
implements this induction literally. After all d coordinates, every origin
is included and the cost is the full weighted Hamming distance.

Ranks are injective on reachable canonical paths. Therefore the rank tie-break
chooses exactly the same whole predecessor path as the original solver. The
origin tie-break cannot change that choice. An unreachable layer remains
unreachable; no finite label is introduced without a finite origin.

## Maintaining path ranks and returning the witness

At destination k retain the selected predecessor h as a backpointer. Its new
canonical path is p_(i-1)(h) followed by k. Order the retained destinations
by (r(h),k), and assign their new dense integer ranks in that order. Equal-length
prefixes compare first by their predecessor path and then by the last state,
so these are exactly the lexicographic ranks of the new complete paths.
Different destinations have different last states, hence distinct paths and
distinct ranks. This proves the rank invariant by induction, including every
cost tie.

Store each F_i table unchanged. At the terminal boundary select the smallest
(F_m(k)+D(k,0),r(k),k). Every candidate appends the same final zero, so the
rank again selects the original lexicographic witness. Trace the stored
predecessors back to the initial zero and append the terminal zero. The empty
stage sequence returns [0]. The output-defect bits are then computed from
the same readers, demands and selected states. Thus every returned field
equals the original planner on their common input domain, including all
Bellman tables, the whole path, correction bits, copied weights and prices.

The original emitter receives the same plan and unchanged source specification.
It therefore emits the same gates in the same order, including both B calls,
all reader prewrites, source mutations, correction operations and final
connector restoration. The improvement cannot remove a data observation,
dirty-state obligation or paid inverse call.

## Complexity and bounded implementation

Let N=2^d. One transform visits dN/2 undirected pairs, considering at most two
directed relaxations per pair. Filtering and cost-table storage are O(N).
Sorting at most N keys for path ranking uses O(N log N)=O(dN) comparisons;
each key has two bounded integers, rather than a growing path tuple.
The terminal distances cost O(dN), and reconstructing one witness costs O(m).
Consequently the complete abstract preparation recurrence costs
O((m+1)dN) arithmetic operations and label comparisons, and O((m+1)N)
stored labels/integers, including the returned tables and all backpointers.

These are arithmetic and comparison counts. If prices use at most B bits,
finite prefix prices use at most B+O(log((m+1)(d+1))) bits and ranks/indices
use O(d) bits. Multiplying the operation bound by
O(max(d,B+log((m+1)(d+1)))) bounds elementary bit work for the displayed
operations. Program construction, input/output and physical data operations
retain their separate costs; they are measured in the full finite pipeline.

The executable enforces d<=8, m<=256 and B<=256, with positive integer prices.
These are resource bounds, not hypotheses of the abstract induction. Inputs
outside these bounds are rejected before table construction. The original
solver has no corresponding stage/price-bit cap; equivalence is claimed on
the declared common bounded domain. The maximum table and backpointer lengths
are each (256+1)*256 entries, and simultaneous transform/rank arrays have
256 entries. No recursion or unbounded retry is introduced. All functions
remain shorter than sixty physical lines.

## Implementation discipline and deviations

The owned new-code loops are bounded by the enforced width, stage, price-bit
limits or fixed verification inventories. Source consumers retain their
unchanged internal algorithms; they are authenticated comparison inputs and
are not new production dependencies. Their implementations are outside the
new algorithm's complexity claim.

Power-of-Ten rule 3 requires a managed-runtime deviation. Python allocates
integers, tuples and list elements during execution. The limits above bound
simultaneously live planner storage and integer sizes; verifier inventories
and benchmark subprocesses are finite, with a sixty-second child timeout.
Exact conformance, limit rejection and both optimization modes exercise these
controls. A fixed-buffer native implementation would require a separate change
if such a backend is requested.

Rule 8 also requires a bounded source-loading deviation. The compatibility
loader compiles only repository source bytes after checking every declared
live input's SHA256 against SOURCES.json. It restores temporary import names
and search paths in a finally block. This permits the unchanged complete
consumer to exercise the new solver without modifying its files. A corrupted
digest is rejected. No data-demand input is compiled as program text.
The scientific commands run with warning diagnostics enabled. Assertions are
not used for acceptance and optimized Python retains every rejection check.
