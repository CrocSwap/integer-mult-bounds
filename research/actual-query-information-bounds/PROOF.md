# Exact statements and proof map

This file states only the results included in this package. The linked
source notes contain the full proofs and retain their historical context.
Different sections have different hypotheses.

## 1. One fixed source in nine charts

Let `G` be the finite cover group containing the actual chart routes. Let
one complete field have dimension `N=|G| dim(W)` on the full module
`C[G] tensor W`. Use the right regular cover action. The selected ordinary
ports are the complement of the two fixed eight-port minors A and T.
Their source matrix obeys `R_U R_U*=48I`.

For the nine actual routes `D_s`, set

```text
B_s = R_U D_s,
P_s = B_s* B_s / 48,
S = P_0 + ... + P_8.
```

Each `P_s` is a projection of rank `8N`. The exact normalized moments of
S are `72,120,244,1649/3,47467/36`. A positive stage that occurs once in
a cyclic projection word can be removed at trace factor `1/12`. This uses
its fresh coordinate block and the actual port bases. It is not a freeness
assumption. The alternating fourth-order contraction is `23/216`. The only
new fifth-order type has contraction `23/2592`; the finite route check uses
194,400 supported triples and finds exactly 4,320 matching terms.

Use weighted Cauchy with `9-S` and `f(S)=19S-6S^2`. Since `0<=S<=9I`,
the first five moments give

```text
tr((9-S) f(S))/N = 5016,
tr((9-S) f(S)^2)/N = 57057,
9 rank(S)/N - 72 >= 5016^2/57057 = 40128/91.
```

Hence `rank(S)/N >= 15560/273`. A cache through which all nine queries
of this one source factor has at least this dimension in complete-field
units. It needs at least 57 whole fields. Whole eight-field cohorts require
at least eight cohorts, or 64 fields.

The bound is sharp for the continuous positive-measure problem with these
five moments and spectrum in `[0,9]`. The witness has nodes
`0,(19-2 sqrt(22))/12,(19+2 sqrt(22))/12,9`, nonzero mass `15560/273`,
and mass `8/7833` at nine. This is not a claim about integer multiplicities
or the spectrum of the actual finite operator.

Full proof: [QUERY-MOMENTS.md](payload/lanes/temporal-reuse/QUERY-MOMENTS.md).
Review: [QUERY-MOMENTS-REVIEW.md](payload/lanes/cover-algebra/QUERY-MOMENTS-REVIEW.md).
The replay checks the source matrix, exact physical-to-logical chart
alignment, route order, all stated contractions, and both moment bounds.
It does not construct a cache or replace changing controller sources with
one fixed source.

## 2. Support distance and a common snapshot span

Let R be the actual `8 by 112` query matrix. Every nonzero complex scalar
row `aR` has at least 53 nonzero ports. The 112 old-root coefficient
directions all attain 53.

The columns consist of 14 signed quartets. If t coefficients on a quartet
are nonzero, the respective lower bounds for its eight evaluations are
`0,8,4,6,5` for `t=0,1,2,3,4`. A generic real projection preserves each
complex zero sum and does not kill any nonzero coefficient. Equal-sum
subsets of positive real coefficients form an antichain. The permutation
chain count, together with opposite sign pairs, gives the quartet bounds.
The exact check adds those bounds over all 255 nonempty coefficient supports.
The minimum is 53.

Restrict to the valid input family `X=JY`, with all helper and private inputs
zero. The actual snapshot support theorem states that a row in frame U
uses only ports whose labels are perpendicular to U. Every actual frame
of rank at least two permits at most 20 ports. Thus two such birth fields
cannot form a nonzero query: they use at most 40 ports.

If m independent birth fields span k query dimensions, their coefficient
code has minimum nonzero weight at least three. Deletion of two coordinates
is injective, so `k<=m-2`. For full fields, use a linear section of the
reconstruction map and delete two field blocks. The same proof gives
`kd<=(m-2)d`. This requires each birth field to have source-port support at
most 20, with no extra uncounted source reads.

Full proof: [QUERY-SUPPORT-DISTANCE.md](payload/lanes/history-encoding/QUERY-SUPPORT-DISTANCE.md).
Review: [QUERY-SUPPORT-DISTANCE-REVIEW.json](payload/lanes/cover-algebra/QUERY-SUPPORT-DISTANCE-REVIEW.json).
This is a field-count bound for one common span. It does not price a general
shared network.

## 3. One snapshot cone

The pinned snapshot source contains 12,271 exact scalar rows, 16,687
availability intervals, and 1,004 actual frames. The independent source
replay checks all 712 formal inputs, all interval endpoints and interiors,
and the final map `(x,y,h,c)->(x-Jy,y,h,0)`.

For each positive proper actual frame U, put
`E_U={p:q_p is not perpendicular to U}`. The exact minor certificate gives
`rank(R_E_U)=8` for all 1,002 choices of U. On `X=JY`, helper/private zero,
and Y supported on `E_U`, every snapshot at a containing frame vanishes.
Every completed X and helper baseline also vanishes. The required queries
can take all eight independent values. Therefore no nonzero completed query
can be formed from that cone, even when all times and all these baselines
are granted.

Full proof: [SNAPSHOT-CONE-OBSTRUCTION.md](payload/lanes/history-encoding/SNAPSHOT-CONE-OBSTRUCTION.md).
Source review: [SNAPSHOT-ROWS-REVIEW.md](payload/lanes/circuit-interface/snapshot-audit/SNAPSHOT-ROWS-REVIEW.md).
The theorem does not include captures from incomparable cones, a changed
core, or new observations inside a native child.

## 4. Shared linear networks and exact cuts

A node v has a fixed free observation matrix `A_v`. A finite causal linear
circuit may share, add, and cancel values at a node. All unlisted input
channels are absent. For a set of nodes Omega containing the output nodes,
let `A_Omega` stack all inside observations and granted baselines. Then

```text
d_Omega = rank(Q restricted to kernel(A_Omega))
        = rank([A_Omega; Q]) - rank(A_Omega)
        <= sum of entering field capacities.
```

Restrict the input to the kernel. An induction in circuit order shows that
every inside value depends only on values that entered the cut. Re-entry is
charged again. This proof does not require an upward-closed cut.

If nonnegative rational cut weights charge every allowed edge by at most
its cost, the weighted demand is a lower bound for the whole network cost.
For N-dimensional fields, each demand and capacity scales by N. In the
application, a frame edge `U -> V` preserves logical content, requires
`U subset V`, and costs `dim(V)-dim(U)` per carried field. The original
core and source-port meaning remain fixed.

The global flag certificate uses binary basis
`[243,249,311,132,131,489,442,405,178]`. The nine source-shell ranks are
`[0,1,1,2,8,6,8,8,8]`, with sum 42. Pivot inclusion charges each increasing
edge by its dimension increase. The proof applies to shared values and
cancellation. It does not add separate output-tree bounds.

The rank-five certificate covers frames
`630,631,632,633,635,637,734,735,736,737,739,741`. Each displayed overlap
has dimension five. Five unit cuts are injective on it, so every requested
k-dimensional subspace costs at least `5k` before the common merge.
No new observations enter afterward; completion costs at least `4k`.
The resulting bound is `9k`. The independent review checks the complete
712-column overlap and every actual inclusion edge in each stated model.

For each rank-eight cone V in `{983,991}`, seven unit cuts have exact
source restriction rank eight and valid edge charges. Append FULL to
those cuts and add the singleton FULL cut. Every direct edge `U -> FULL`
is charged by at most `9-dim(U)`. Each cut is injective on any requested
k-query subspace. Thus the bound is `8k`, even if branches bypass V and
merge only at FULL. Proper frames must remain actual subframes of one
chosen V. The two cone certificates cannot be combined without checking
the new cross-cone edges and observations.

The [general cut proof](payload/lanes/cover-algebra/MOVABLE-SNAPSHOT-CUTS.md)
and its [proof review](payload/lanes/history-encoding/MOVABLE-CUT-THEOREM-REVIEW.md)
state the linear model. The numerical results have separate
[global](payload/lanes/history-encoding/SNAPSHOT-FLAG-CUT-REVIEW.md),
[rank-five](payload/lanes/cover-algebra/RANK5-UNION-CUTS-REVIEW.md), and
[rank-eight](payload/lanes/cover-algebra/MOVABLE-RANK8-CUTS-REVIEW.md) reviews.
The global result here is 42. No global bound of 64 is claimed.

## 5. A complete residual channel

This section uses the pinned nine-stage bank recipe and the separate
abstract routed interface `R_s R_s*=56I`. Let `C_0` be the old controller
before its final signed swap. Let C omit all nine centre blocks. Define
`d=dim(intersection_s im(R_s*))` on the full regular cover.

The nine old-prefix bank rows have rank eight and unique relation
`c=(1,-1,-1,1,1,-1,-1,1,1)`. Every proper subset is independent. Write
`V_s=R_s(v_s tensor I)` and stack them in V. The kernel of `V*` has
dimension d, so `rank(V)=72|G|-d`.

For the bank symplectic form Omega and strict lower block matrix
`L_ij=V_i Omega V_j*` for `i>j`, the chronological recurrence gives

```text
C_0^-1 C - I = Omega V* (4I-L)^-1 V.
```

The relation coefficient has bank area four. On `ker(V*)`, the form
`4I-L` equals `-47/14` times the common-image inner product under its
specified identification. It is nonsingular. Thus the decoder loses no
additional rank, and `rank(C-C_0)=72|G|-d`. Every proper omitted-stage set
S gives exact rank `8|S||G|`.

The separate two-projection cover theorem gives `d<=8|G|/183`. It uses
the full regular action, actual route products, and exact traces `4/7`
and `27/343`. Therefore the residual rank is greater than `71|G|` per
replica and greater than `1151|G|` across all 16 independent replicas.
A complete linear residual channel needs 72 or 1,152 whole cover arrays,
respectively. A joint encoder across replicas does not change the latter
ceiling.

Full proof: [residual-syndrome/PROOF.md](payload/lanes/residual-syndrome/PROOF.md).
Reviews: [residual algebra](payload/lanes/residual-syndrome/review/REVIEW.md)
and [cover traces](payload/lanes/source-domain/COVER-REVIEW.md).
Application to the native controller inherits the
[local lift](payload/lanes/interface-proof/PROOF.md) and
[endpoint normal form](payload/lanes/encoded-controller/CONTROLLER.md).
Their native replay is not repeated in this package.

This bound concerns one declared residual channel. It does not count peak
workspace, native child rank, or a procedure with later data reads. No
complete kappa calculation changes.
