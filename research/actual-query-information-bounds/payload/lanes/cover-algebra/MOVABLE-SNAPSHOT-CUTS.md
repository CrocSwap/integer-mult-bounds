# Movable cuts for passive snapshot networks

A cut need not contain every frame at which its source test gives zero
observations. It can use a smaller node set. The rank of the required
output on that test is still a valid cut demand. Upward closure is useful
for a search, but is not required for the cut proof.

This note gives a theorem for the declared snapshot model. It gives no
new numerical bound for the actual nine-coordinate network.

## Linear observation model

Work over Q or C. Let x be the full logical input vector. A node v has
a fixed free observation matrix A_v. A circuit can read these values at
the node and perform arbitrary scalar linear operations there. It can
split or reuse a computed value. Each paid edge e carries n_e fields
and has cost c_e per field. Each output field is a prescribed row of
Qx, at an output node.

All carried fields start at zero unless their initial values are included
as free observations. The computation is a finite causal linear circuit.
There is no unlisted input to a node. This includes passive snapshots
of a fixed core. It does not include an edit to that core which changes
the observation matrices.

For the application, nodes are canonical frames. An allowed edge U to W
has U contained in W and cost `dim W - dim U`. Its field keeps the same
logical content when its native frame changes. The declared edge set
must include every transition allowed in the proposed network. Granting
extra edges or observation times only makes a lower bound harder.

## Cut theorem

Let Omega be any node set that contains all output nodes. Stack all free
observation rows inside Omega into A_Omega. This stack must include any
terminal baseline that the model grants at an inside node. Put

    H_Omega = kernel(A_Omega),
    d_Omega = rank(Q restricted to H_Omega).

Then

    sum_(e entering Omega) n_e >= d_Omega.                 (1)

To prove (1), restrict the input to H_Omega. All free observations inside
the cut are zero. At each operation inside the cut, its output is a
linear combination of values that entered through cut edges. This follows
by induction over the finite circuit. It also holds when a value leaves
the cut and later returns. Each entering field contributes at most one
dimension. The final output has rank d_Omega, which proves (1).

No upward closure assumption occurs in this proof. If all edges follow
frame inclusion, upward cuts avoid re-entry and are a useful restricted
family for an exact search.

The demand can be computed without a kernel basis:

    d_Omega = rank([A_Omega; Q]) - rank(A_Omega).          (2)

Here the semicolon means vertical row stacking. Equation (2) follows
by quotienting the row space by row(A_Omega). It is the strongest demand
obtainable from an input subspace on which every inside observation
vanishes: every such subspace is contained in H_Omega.

If a field has payload dimension N, use the actual block observation
matrices. Each entering field has rank at most N. In the scalar tensor
model, A_Omega and Q are tensored with I_N, so both sides of (1) scale
by N. The bound in field units is unchanged. This statement requires
the stated nodes, observations, and edge costs; it does not permit an
unpriced change to a frame or to its logical address meaning.

## Weighted certificates

Choose finitely many cuts Omega_j and nonnegative rational weights w_j.
If every allowed edge satisfies

    sum_(j: e enters Omega_j) w_j <= c_e,

then every admitted network has total paid rank at least

    sum_j w_j d_(Omega_j).                               (3)

Multiply (1) by each weight and sum. The edge inequality bounds the
charge to every carried field by its paid cost. This proves (3), with
arbitrary sharing, cancellation, and unequal edge multiplicities.

An exact certificate needs only the cuts, their test spaces or exact
demands, nonnegative rational weights, and all edge-charge inequalities.
The method that proposes the weights does not enter the proof.

## Source-port tests for the actual snapshots

For the pinned clean backward word, use the valid input family
`X=JY` with all 480 helper inputs and private inputs zero. All completed
X and restored helper baselines are then zero. The accepted support
certificate states that an observation at U uses only ports p with
`q_p` perpendicular to U.

For a source-port set E, define

    Omega_E = {U: for every p in E, q_p is not perpendicular to U}.

On inputs Y supported on E, every observation in Omega_E is zero. This
set is upward closed. For any cut Omega contained in Omega_E and with
all output nodes inside, the demand is at least

    rank(R_E),

or `rank((SR)_E)` for a requested query subspace with coefficient matrix
S. The smaller cut has the same test demand. Only its entering edges
change.

For a fixed node cut Omega, the largest coordinate source test allowed
by this support law is

    E_Omega = {p: q_p is not perpendicular to U for every U in Omega}.

Replacing E by E_Omega does not change any edge charge and cannot lower
the demand. In contrast, replacing Omega by the larger Omega_E can move
the charge to different edges. That replacement is not free in a family
of weighted cuts.

If restriction to E is injective on a query space of dimension r, then
the same cut has demand k for every k-dimensional subspace of that
space. Thus a certificate whose positive cuts are all injective gives
a bound proportional to k. No sum of bounds from different common-merge
models follows unless their cuts form one feasible certificate on the
complete allowed graph.

## Why movable placement can strengthen a certificate

Consider the chain of frames `0 < span(e1) < FULL2`, together with its
direct `0 -> FULL2` edge. Costs are the dimension increases. There is
one source coordinate with label e1 and one required query equal to
that coordinate. Grant its free observation only at frame zero.

The maximal zero-observation cut is `{span(e1), FULL2}`. Its single-cut
bound is one. The smaller cut `{FULL2}` also has demand one. Give both
cuts weight one. A rank-one edge enters one cut; the direct rank-two
edge enters both. The joint bound is two. Thus a certificate restricted
to maximal zero-observation sets can miss the full path cost.

This is an example for the cut theorem. It is not a claim about a new
actual snapshot path.

## Exact scope for the next certificate

The actual source payload is
`history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz`, with decompressed
SHA256 `3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
The independently checked support law is recorded in
`cover-algebra/SNAPSHOT-SUPPORT-REVIEW.json`.

A global certificate must state whether it permits all actual frames,
only one contained-frame graph, or synthetic intermediate frames. It
must charge every allowed edge. It must also state where new observations
stop. A certificate for one common merge cannot be added to another
one without checking shared edges and fields. Chronological phase
recipes, changed native cores, and operator changes to logical address
meaning remain separate obligations.
