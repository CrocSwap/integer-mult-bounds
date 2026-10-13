# Two replica groups with a joint whole-helper assignment

This construction keeps PR799's admitted X4 local complex supplier, its scalar
programs, frames, entrance and terminal conditions, residual widths and data
phase recipes. Before finalizing the construction, the selected certificate
was rechecked at base `f567884aeb8851b6e794af1184119a3bfbe1e631`: the accepted
baseline is PR799 with κ = `0.001661634653669567`. PR741 is retained as an
ancestral and regression-control supplier. This package changes the global
controller from eight to sixteen data replicas and assigns the resulting 144 complete invocations jointly. The two
groups are interleaved: invocation `(stage, replica)` of the old eight-replica
order is followed by `(stage, replica + 8)`.

The local construction and its all-column, phase and wrapper admission are
inherited. All-size compilation, common-label realization, complete-invocation
hosting, precision/tape accounting and analytic transfer remain conditional.
The finite checks below do not prove those assumptions.

## Scalar and controller semantics

Project the new execution schedule onto any one data replica. Its thirty
replica-local source events occur in exactly the original order, including all
nine complete local invocations, all bridges, idle-child sweeps and terminal
events. The final bank-padding and whole-stock correction remain after all
replica-local events. Thus the controller uses the same per-replica data
identity and phase argument. The two groups have distinct data families.

A hosted helper may use a family belonging to the other group. This relies on
the existing whole-invocation interface: the hash-bound local supplier and its
normalization wrappers restore arbitrary initial helper contents after each
complete invocation. The scheduler does not interleave operations inside a
local invocation. At its boundaries, the borrowed family therefore has the
same contents it had before the borrow. This is why a cross-group helper
assignment does not introduce a new scalar coupling between the two data
controllers.

The local program itself is unchanged. In particular, the independent local
replay remains the evidence for arbitrary dirty columns, both orientations,
normalization wrappers and all local endpoint conditions. The new independent
checker does not claim to replace that replay.

## Actual windows and whole-helper ownership

Do not obtain the actual owner windows merely by replacing every old time
`t` with `{2t, 2t+1}`. At the end of a window, the first group's idle sweep may
already have occurred before the second group's invocation. The independent
checker instead expands the source event stream and reconstructs every strict
interval from the last local or bridge touch of the physical pair to the
actual idle-child sweep. It checks the complete invocation position against
that interval. For this candidate there are 480 replica-local events, 144
bridges and 288 positive-rank idle windows.

Each of the 72,576 roles names one complete helper in one invocation. The
checker verifies all of the following directly from the roles and input
artifacts:

- Every invocation contains helpers `0..503` exactly once.
- A helper uses its exact local residual width; no helper is split.
- Each physical family hosts at most one helper during the invocation and is
  distinct from that invocation's active source and target families.
- The invocation lies strictly inside the family's actual idle window.
- All occupied slices in an idle child are disjoint, remain within capacity,
  and form a contiguous prefix. The remaining suffix is charged as one idle
  child when nonempty.

The local width inventory is unchanged:
`{4:80, 5:32, 7:54, 8:122, 9:216}`. The local paid profile is recounted from the
canonical frame chains and checked against the local replay. Thus changing the
number of invocations does not hide a change to their individual price.

For every routed slice, the independent checker builds the actual
73-dimensional orthogonal port basis from the pinned data-phase inputs,
selects exactly the pending axes at the declared offset, supplies `9-width`
distinct spectator axes, and completes a permutation of all 73 axes. It
verifies 112 port bases and all 8,546 distinct charts used by the assignment.
The whole-family uniqueness rule is necessary even for narrow slices:
spectator coordinates can borrow other coordinates of that family during the
invocation.

The emitted-controller audit separately binds these roles, routes, local
program hashes and phase recipes to the actual serialized global template.

## The strict moment gain

PR799 retains PR741's physical assignment and width inventory. Two independent
copies of that accepted assignment would have idle profile

```
{48:4792, 44:2, 3:2, 1:2}.
```

The joint assignment changes eleven roles and has

```
{48:4793, 44:1, 2:1, 1:2}.
```

Its difference is `H48 - H44 + H2 - 2 H3`; its rank-mass difference is zero.
The complete global profile is

```
{1:366914, 2:48673, 3:61920, 4:27936,
 5:8064, 8:1152, 44:1, 48:4793}.
```

Here `m=73`, the live family count is `W=14336`, total paid rank mass is
`1041408`, and `m W - mass = 5120`. These are the doubled baseline quantities,
except for the zero-mass idle-profile change. Merely duplicating the baseline
would leave its normalized moment unchanged.

For a saving parameter `0 < b < 1`, a rank-r child contributes a positive
common factor times `r^(1-b)` to the native complex moment. The vector
`(48,2,0)` strictly majorizes `(44,3,3)`: both have total 50, while their first
partial sums are 48 versus 44 and their first two partial sums are 50 versus
47. Since `x^(1-b)` is strictly concave on nonnegative reals,

```
48^(1-b) + 2^(1-b) < 44^(1-b) + 2 * 3^(1-b).
```

Consequently the normalized moment strictly decreases at the old saving
parameter. Monotonicity of the moment in `b` yields a strictly larger complex
saving endpoint, provided the new finite controller and invoice are admitted.
The exact numerical endpoint and the final strict outer assembly are computed
by the retained rational engines; this argument does not substitute an
unimplemented cost model for those checks. It also makes no optimality claim
for sixteen replicas or larger pools.

## Namespace and finite reserves

The hosted candidate has the following disjoint half-open physical ranges:

| Role | Range |
|---|---|
| Data and owner families | `[0,14336)` |
| Private centres | `[14336,14344)` |
| Reserved local tableau | `[14344,14848)` |
| Coefficient work | `[14848,14850)` |

There are 14,850 physical families. The private workspace is shared by serial,
complete invocations under the existing erasure/restoration contract. It is
not duplicated as live data and is not offered as a helper owner.

A conservative dedicated-bank parent must also have valid geometry. Doubling
replicas does not permit sixteen old helper lanes in a single 73-dimensional
bank. The parent lift duplicates the bank families for the two eight-replica
groups and retains each group's original lane number. This parent supplies a
conservative finite reserve; final hosted helper owners are independently
replaced and checked.

Let `B` be the maximum scalar/Horner prefix exponent in the freshly bound
local native replay, across both orientations. The independent checker and
the invoice read this value from that replay; neither carries PR741's value
forward as an assumption. The global formula is

```
B + ceil(73/2) + 144 invocations + 144 bridges + 4 = B + 329 < 512.
```

The fresh PR799 native replay gives `B=72`, so the candidate requires
`72 + 329 = 401 < 512` bits. The ancestral PR741 replay independently gives
the same value and remains a regression control.

The normalized invocation and bridge endpoint bounds used in this formula
are inherited; idle children, phase operations, spectator endpoints and
terminal translations retain their unitary bounds. The global count includes
both groups. With the same 73-dimensional group factor, physical stock has
2,642 bits, so the retained row formula is

```
2 * 2642 + 9909 + 252 + 2 * 512 = 16469 < 20161.
```

The maximum child remains 48, and `73^2 = 5329 > 2 * 48^2 = 4608`.
These checks establish prefix, row and halving headroom. The complete fresh
invoice must still recount primitive work, all wrappers, bridge and translation
work, routing, precision and tape bounds using the enlarged controller. The
source reserve guards are retained rather than weakened.

## Independent controls and scope

`independent_check.py` imports no constructor or controller auditor and uses
explicit failures that remain active under `python -O`. Its six controls
reject an owner in the private namespace, a collapsed replica number, a
missing helper, a split helper, a truncated helper width, and a complete role
moved past its actual idle event. The last control uses the reconstructed
bridge-aware window, not a copied allowed-time list.

This package credits PR799's JointXF paired read exchanges and their inherited
PR741 frames and global assignment, the carrier/phase/whole-helper work
retained in those packages, and the independent local replay used as its
dependency. PR799 changes the per-invocation paid profile to
`{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8}` while preserving every helper's
residual width. The outer two-group trade is therefore unchanged. The new
contribution is the two-group controller and joint assignment with a strict, exactly priced idle-profile
gain. Prepared for haoyan with substantial OpenAI Codex assistance.
