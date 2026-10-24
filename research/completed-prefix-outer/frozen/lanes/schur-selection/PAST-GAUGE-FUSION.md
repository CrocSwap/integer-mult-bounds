# Fusing the retained local-nine gauges does not reduce the active count

The complete selected owner histories have a useful property: the active
parts of successive required local-nine gauges are disjoint on each
old owner. Thus adjacent view fusion does not reduce the active lower
count from [the corrected catalyst proof](PAST-CATALYST-v2.md).

This note preserves the required local-nine Walsh gauge at each call.
It permits arbitrary intermediate gauge paths between calls. It does
not cover a different local gauge with extra common exterior factors,
a different owner content path, or algebraic rewriting that removes a
required call boundary. The retained idle native factors are counted
separately. No optimized global compiler is claimed.

## Required gauge visits

Use the fixed split P plus A from the catalyst proof. Express each job
in its physical owner's fixed port coordinates. The local-nine space
has the form

    U_j = S_j direct-sum A_j,

where S_j lies in P and A_j is spanned by some active coordinate axes.
For a productive data job at positive stage s, A_j is the fresh block
E_s. For a helper job, A_j is its occupied active pending axes. Its
spectators are all in P.

The exact check covers every data and helper use on every one of the
14,336 old physical owners. No active axis occurs in two of these jobs
on the same owner. The retained idle remainders use the other active
axes, with no repetitions. Every individual owner completes all 64
active axes exactly once. This is stronger than an equality of total
counts: the check retains the bit mask for each separate owner.

## The cost of a transition

Let a_j=dim(A_j). For consecutive required gauges, the active parts are
orthogonal coordinate spaces with A_j intersect A_(j+1)=0. Each partial
Walsh operator factors into its P operator and its A operator. Hence
the relative gauge

    W_(U_(j+1)) W_(U_j)^-1

has an active tensor factor W_(A_j direct-sum A_(j+1)). Its full Fourier
rank is at least a_j+a_(j+1), irrespective of the two past factors.
The initial and final stored gauges are confined to P, so the first
and last transitions have lower ranks a_1 and a_last.

These bounds also apply when a transition is divided into several
Clifford factors. If the Fourier blocks of two factors are B_1 and B_2,
the product has block A_1 B_2+B_1 D_2. Therefore

    rank(B_product) <= rank(B_1)+rank(B_2).

An intermediate gauge path cannot have total native rank smaller than
the Fourier rank of its required endpoint map. This statement charges
all native transformations in that path. It does not treat arbitrary
new past transforms as free operations.

Summing along an owner's required visits gives

    a_1 + sum_j(a_j+a_(j+1)) + a_last = 2 sum_j a_j.

Thus replacing separate exits and entries by their exact product saves
no active rank in these histories. The old native past-coordinate work
was already granted free in the favorable comparison. This argument
concerns the prescribed gauge transitions, not a different factorization
of the complete core and controller. In particular, it does not count
intervening native content progress as a gauge-only path. Folding a
gauge through in-core scalar or phase operations needs a separate proof.

## Complete count

The check covers 32,256 data visits and 69,120 helper visits. Their active
direction mass is

    229376+468976 = 698352.

The required gauge transitions, including the stored input and output
boundaries on each owner, have native rank at least

    2*698352 = 1396704.

Keeping the old idle factors adds active mass 219,152. Their active axes
are disjoint from every local active visit on the same owner. If an
idle factor is fused into a gauge-only transition, its Fourier block
is a disjoint active block and its rank adds to that transition.
The resulting
lower count is 1,615,856, compared with productive active mass 917,504.
No averaging of helper owners is used.

The remaining gauge-history escape must change the required spaces
U_j, change the owner content paths, or change the call interface.
For example, a common exterior Walsh factor at a call changes every
required U_j. Its compatibility with all data and borrowed helper roles,
its preparation, and its final removal need a new calculation. Merely
retaining each local-nine gauge longer does not address the present
disjointness obstruction.

## Reproduction and scope

The source and original count receipt is [PAST-CATALYST.json](PAST-CATALYST.json),
SHA256 `5eefd5390bdf778d9ca1a34b8efc19f295f069138e1ca1f4784af3ad9e0bd320`.
The new check independently reads the selected template and original
complex phase table from the pinned archive. It does not import the
first checker. It verifies 704 distinct owners at every call and every
individual owner's complete active mask.

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/schur-selection/check_past_gauge_fusion.py
```

The command prints `PASS_DISJOINT_OWNER_GAUGES_AND_FUSION_BOUND` and writes
[PAST-GAUGE-FUSION.json](PAST-GAUGE-FUSION.json). It uses integer masks
and exact counts. Independent proof review is recorded separately. OpenAI
Codex assisted with the proof and checker. This is a scoped obstruction;
it does not change the selected supplier or the complete kappa value.
