# Chronological cache paths and merged query flows

A fixed path has an exact linear-algebra test. The retained backward word
fails a stronger single-cone test. A scalar merge tree that produces one
nonzero centre query costs at least eight units of native rank. This last
bound does not add across outputs that share paid operations.

No construction below improves the complete supplier. A merged network
with several outputs remains open.

## 1. Native and scalar contracts

Let `T_U` be the exact canonical operator for frame `U`. A snapshot at
event `t` and frame `U` has physical value `T_U a z`, where `a` is its
row on the 712 arbitrary input fields. The coefficient ring is the
dyadic rationals. The same statements over a larger coefficient field
give relaxations, not a dyadic implementation.

A permitted cache transition from `U` to `V` must supply the exact
operator `T_V T_U^-1`, including its global phase and monomial maps.
Subspace inclusion alone is not a native recipe. In particular, an
alternating complement can prevent an assumed orthonormal embedding.
The transition cost is the rank of its supplied native children.

The cache starts at exact zero. Its initial arbitrary contents are
cleared. At a matching frame, a scalar ADD from a snapshot changes its
logical row from `a` to `a+c b`. A supplied transition changes the frame
and leaves that logical row unchanged. These statements hold on all
arrays, including arrays that are not tensor products.

For a path `U_0,...,U_m=FULL`, assign each snapshot read a time within its
recorded availability interval. These read times and transition times
must be in chronological order. If read coefficients are `c_i`, the
final physical value is

\[
T_{\rm FULL}\sum_i c_i a_i z. \tag{1}
\]

Thus the scalar module spanned by the available snapshot rows is the
exact set of logical rows that this path can form. This gives a necessary
and sufficient test for a fixed path, fixed read schedule, and supplied
native transitions. A rational solution is insufficient when its
coefficients are outside the permitted ring.

Let `E` contain the unchanged FULL X outputs and the restored FULL helper
outputs. A target query `q` can be cleaned at exit if

\[
q=\sum_i c_i a_i+dE. \tag{2}
\]

After the cache reaches FULL, add the `dE` terms. For eight queries,
complete all eight cleanups before the first X repair. Then subtract
`K` times the clean cache from X. This order preserves the endpoint rows
used in (2). A different order needs a separate invariant.

If each supplied edge costs `dim(V)-dim(U)`, one buffer costs
`9-dim(U_0)` along the path. Eight buffers on one path cost eight times
that amount. This is a conditional cost identity. It does not prove that
such a path has the required observations.

## 2. Exact retained-source test

The source is `history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz`, with
decompressed SHA256
`3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
It has 12,271 exact rows and 16,687 intervals. Our independent checker
`review_snapshot_support.py` reads that payload and the pinned
`circuit-interface/INTERFACE.json`. It imports no source producer.

The checker substitutes the valid test input

\[
x=Jy,\qquad h=0,\qquad c=0.
\]

All 480 helper inputs are zero in this test. No helper is assumed clean
in a proposed circuit. Every completed X row and every restored helper
row vanishes on this input family.

For every snapshot at frame `U`, exact integer arithmetic verifies

\[
\operatorname{supp}(a_U)\subseteq
S_U:=\{p:q_p\perp U\}. \tag{3}
\]

The check includes 104,088 nonzero port incidences, counted once per
availability interval. The source checker counts distinct frame/row
pairs instead; this accounts for the different total.

For every one of the 1,002 positive proper actual frames, our checker
selects and evaluates a nonzero exact eight-column minor of

\[
R_{E_U},\qquad E_U=\{p:q_p\not\perp U\}. \tag{4}
\]

On inputs supported in `E_U`, all snapshots in frames containing `U`
are zero, while `Ry` is arbitrary. Therefore no nonzero centre-query
combination can be formed from that cone, even with all read times
granted and all final X and helper rows granted. Exact phases cannot
change a zero input. This proves the source cone theorem in its stated
scope.

The eight normal lines are absent from the actual rank-one frames. A
cache can start empty in a new normal-line frame, but its first nonzero
snapshot is still at an actual frame. A subsequent monotone path then
lies in the cone of that actual frame.

A separate exploratory screen used the 2,880 distinct retained native
climb edges. It found 6,068 rank-two-to-FULL paths. Over `GF(65521)`, every
path had zero query intersection after quotient by the 112 completed-X
rows and 402 FULL helper baselines. It granted every snapshot time at
each path node. This screen is not used as a rational impossibility
certificate; the exact support argument above gives the stronger result.

## 3. The support annihilator of a query

The independent checker also tests all 511 nonzero binary lines. It
gives exact nonzero minors for each rank claim:

\[
\operatorname{rank}R_{\{p:q_p\cdot v=1\}}=
\begin{cases}
7,&v\in\{42,7,25,52,82,127,97,76\},\\
8,&\text{otherwise}.
\end{cases} \tag{5}
\]

At normal `n_k`, row `k` is zero on the excluded columns. A nonzero
seven-column minor on the other rows proves that this is the entire
left kernel. Hence a nonzero query row `aR` has a source-support
annihilator of dimension at most one. If that dimension is one, the
line is `n_k` and `aR` is proportional to row `k` of `R`.

Two independent query rows have trivial common annihilator. This does
not by itself give a rank-weighted network cost bound.

## 4. A scalar monotone merge-tree bound

Consider one rooted tree. Each edge carries one scalar-content field
from a child frame into a containing parent frame. Each leaf forms an
arbitrary scalar combination of granted snapshots in its frame. At a
merge, form a scalar linear combination of the incoming fields. The
root frame is FULL. Each edge has native cost at least its dimension
increase. This model permits cancellations and grants all read times.
It excludes address changes to the logical content and paid
subexpressions shared with a second output tree.

For a node `v`, let `I_v` be the intersection of its descendant leaf
frames. The total cost below `v` is at least

\[
\dim U_v-\dim I_v. \tag{6}
\]

For a leaf this is zero. Suppose `v` has `k` children. The induction
hypothesis and the `k` incoming edge costs give the lower bound

\[
k\dim U_v-\sum_{j=1}^k\dim I_j.
\]

All `I_j` are subspaces of `U_v`. Codimension subadditivity gives

\[
\sum_j\dim I_j-\dim\bigcap_j I_j
\leq(k-1)\dim U_v,
\]

which proves (6). A new snapshot added at an internal node can be
represented by a zero-length leaf in that node's frame, so the proof
also covers such reads.

Every leaf row is supported on ports perpendicular to `I_root`.
The same is true after every scalar cancellation. If the final row is
a nonzero centre query, (5) gives `dim(I_root)<=1`. Thus the cost is at
least `9-1=8`. Eight separate trees cost at least 64. This conclusion
requires separate paid trees. It is not a bound for a shared
multi-output DAG, a different core, or cuts inside native children.

## 5. Exact formulation for a shared network

A time-expanded network node specifies an exact frame and an event cut.
It has a matrix `O_v` of available snapshot rows. Every native edge has
a supplied same-content recipe and an integer field capacity `c_e`.
Let `B_e` be the matrix of logical rows carried by that edge.

A proposed network is a scalar certificate if, at each node, every
outgoing row is in the permitted-ring module generated by its incoming
rows and `O_v`. At FULL, the eight rows of `RY` must be in the module
generated by incoming rows and the unchanged endpoint rows `E`.
Explicit coefficient matrices for these inclusions give a circuit by
COPY, ADD, and CLEAR on owned fields. A storage schedule must preserve
each incoming field until its last use. The native cost is

\[
\sum_e c_e\,\operatorname{cost}(e). \tag{7}
\]

Conversely, any linear cache circuit in this model gives such row
matrices. This is an exact algebraic formulation. It does not remove
the native recipe, timing, storage, coefficient, or complete-cost
obligations.

There is a useful necessary cut inequality over any coefficient field.
Let `Omega` be a set of nodes containing the output. Let `S_Omega` be
the span of all observations at those nodes and the granted endpoint
rows. Then

\[
\operatorname{rank}(Q+S_\Omega)-\operatorname{rank}S_\Omega
\leq \sum_{e:\,e\text{ enters }\Omega}c_e. \tag{8}
\]

Indeed, all information used inside the cut is generated by these
observations and the incoming edge rows. The inequality holds even
when the cut is not closed under the time order.

Nonnegative cut weights give a cost lower bound if, for each edge, the
sum of weights of cuts that it enters is at most that edge's cost.
This gives a precise route to a shared-network lower-bound certificate.
No cut family with total bound 64 is supplied here. The scalar-tree
proof must not be used in place of that missing certificate.

## 6. Reproduction and limits

Run the independent exact check with:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/review_snapshot_support.py
```

It writes `SNAPSHOT-SUPPORT-REVIEW.json`, with all 1,002 frame minors and
all 511 line minors. The result is
`PASS_EXACT_SNAPSHOT_SUPPORT_AND_SINGLE_CONE_EXCLUSION`.

The check did not rerun the full snapshot producer or a new native
cache word. The source proof was inspected. No actual shared-network
solution, global owner assignment, or full supplier invoice is claimed.
