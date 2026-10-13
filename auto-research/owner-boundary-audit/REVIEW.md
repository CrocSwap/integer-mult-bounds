# Event-boundary argument and independent review

This is a finite review of the selected PR626 owner's timing interface at
base `66849e1475c930fd7732b1a0067ffee7e1e95f60`. It makes no new bound claim.

## Review of the separate checker

The checker uses a reverse scan, rather than importing the emitter or
reconstructing the source audit's last-touch intervals. The invariant is:
immediately before a position is sampled in reverse order, the state for
each `(replica, pair)` names the first future relevant event on that pair,
if that event is an idle deadline; otherwise it is blocked. An idle sweep
sets its two children. A bridge blocks both its source and destination.
A local sweep blocks its own data pair **before** sampling helper
eligibility. Terminal events conservatively block the replica. The reverse
induction follows directly from these cases, so the state sampled at a
local call includes exactly the pending children whose next data event is
their completion. On this pinned source there is a touch between distinct
positive-child sweeps on the same pair. Thus the invariant gives the same
strict event-position intervals as the source check.

The checker received a separate OpenAI Codex agent review and an independent
run of `python3 -I -O research/owner-boundary-audit/verify.py`: it passed all 10,368
eligibility comparisons and all 35,424 roles, including 28,404
cross-replica roles. The optimized run confirms the checks are not disabled
by Python's assertion optimization. Its same-family mutation uses two
width-9 helpers at offsets 0 and 9 in a rank-32 child, so those residual
coordinate sets really are disjoint and within capacity; its rejection
tests the stronger whole-family requirement.

The source-chain review also checked the frozen558 setup:
`run_complex44.py` installs `ROUND20-PARENT-TEMPLATE.json.gz`, then
`prepare_supplier_base.py` preserves `recipe`, `idle_children`, and the
first 30 schedule events and copies `DATA-PHASES.json`. Those three
controller fields equal the archived direct-delivery parent used here;
their schedules differ only in final bank events 30 and 31, which occur
after all sampled calls. The phase files are byte-identical. This equality is
necessary to justify using the small archived input without rebuilding
the native suppliers. It is not a claim that the complete archived
template equals the selected generated template.

## What the interval condition establishes

Fix an owner replica and a positive-rank idle child. Its physical pair and
side are read from that child's `idle_cover_sweep`. Let `d` be the position
of that sweep in the expanded controller, and let `a` be the most recent
position before `d` at which a local sweep uses that pair, or a bridge uses
it as either source or destination. Use `a = -1` if no such event exists.
The source audit accepts a borrower whose complete local sweep starts at
position `c` only when `a < c < d`.

For the pinned controller, this condition is sufficient for the **timing
part** of whole-owner availability, subject to its inherited local
restoration and atomic-call contracts:

1. Per-replica projection preserves all 30 source events, including both
   endpoints of every bridge. Thus there is no source-data touch of the
   owner's pair between `a` and `d`. Initial windows are already pending
   before the first event. The positive children with later starts are
   released by bridges in this selected controller.
2. Every local invocation completes, including its wrappers, before the
   next controller event. Hence a borrow beginning strictly inside this
   interval finishes before `d`, and cannot straddle another replica's
   data event.
3. Distinct owner families within one invocation exclude both active-data
   aliasing and simultaneous helper aliasing. Across invocations, exact
   restoration of the spectator coordinates and disjoint paid residual
   footprints are the separate obligations allowing repeated use of one
   physical family. The interval check alone does not establish these.
4. Idle completion executes the remaining suffix only after those uses.
   Source `terminal_Y_translations`, `terminal`, and whole-stock correction
   occur after the positive-child deadlines. Omitting those event kinds
   from the source audit's `last` table therefore creates no missing touch
   inside this particular controller's borrowing intervals. This conclusion
   must not be generalized to controllers that move such events earlier.

Availability belongs to the **owner replica**. Testing it against the
invocation replica would be invalid for cross-replica borrows, even when
the stage numbers coincide. The source code correctly derives owner
replica, pair, side and port from the literal family identifier.

## Event positions versus call times

Strict inequalities above concern positions of individual controller
events. A block contains its local sweep first, then its replica-local
bridges and idle completions. Consequently the call at an idle completion's
block time is permitted; the call at a releasing bridge's block time is too
early. Treating both boundaries as open or both as closed in integer call
time changes the admitted set.

The selected data make this distinction observable:

| Owner replica / child | Release | Deadline | Admitted call times |
| --- | --- | --- | --- |
| 0 / 0 | Initial state | Event position 3, source event 2, block time 2 | 0, 1, 2 |
| 0 / 1 | Bridge at position 4, source event 3, block time 2 | Event position 10, source event 5, block time 5 | 3, 4, 5 |

There are 112 actual child-0 helper roles at call time 2. One is stage 1,
invocation replica 0, helper 207, family 335, port 111, offset 7, width 9.
There are 111 actual child-1 helper roles at call time 5. Thus closing the
window before processing its deadline block's local call rejects selected
valid roles. Conversely opening child 1 at the beginning of block 2 admits
a call that precedes the bridge creating that pending region.

No local sweep is literally the same event as a bridge or idle sweep. A
mutation from `<` to `<=` at those event-position boundaries cannot change
the finite set of local call positions on its own. Meaningful negative
controls must change event order, a release/deadline transition, or the
admitted call set. Rejection of an artificial equal-position call does not
establish an additional physical theorem.

## Useful negative controls

- Open a post-bridge child before its bridge, including the bridge's block
  call. Child 1 at replica 0 / time 2 is a concrete witness.
- Close an initial child before the local call in its deadline block.
  Child 0 at replica 0 / time 2 has actual selected roles as witnesses.
- Insert a bridge touching the owner pair between a formerly legal local
  call and its idle deadline. The call must become inadmissible, whether
  the owner is the source or destination. This exercises the barrier
  transition directly.
- Use the borrower replica's state instead of the owner's state. This can
  produce plausible windows while describing the wrong physical family.
- Use one physical family for two helper roles in the same call, including
  disjoint residual offsets. A whole-family helper invocation still owns
  its spectator coordinates; residual disjointness alone is insufficient.
- Present an unknown event kind. A standalone checker should fail closed,
  rather than silently treating an unmodeled event as harmless.

## A boundary test cannot establish bridge presence

Deleting any **one of all 72 literal bridges** leaves the next-touch
admission matrix unchanged. This was checked separately during review.
At the call samples, an idle deadline immediately before the original
bridge, or a local barrier on the destination pair, already determines
the same admissibility. There is no intervening local call at which that
bridge alone changes the pending-child state. This is a concrete
limitation of the finite timing predicate, not a permission to remove
the bridge from the construction.

The bridges implement the controller's data transformation, which is
outside the timing predicate. The exact source pins and preservation of
the source event projection remain necessary. The checker should retain
the unchanged-matrix deletion experiments as successful limitation
controls, and use inserted intervening bridges to test its source and
destination barrier transitions. A bridge-deletion experiment that
leaves this matrix unchanged is neither a construction improvement nor
a proof that the bridge is redundant.

A small scalar check exposes the difference. Write the eight wires as
`(x_0,y_0,...,x_3,y_3)`. The retained interface has forward local action
`y_i += x_i`, reverse local action `x_i -= y_i`, bridge `(d,s,c)` action
`x_d += c*x_s; y_s -= c*y_d`, and terminal action
`(x_i,y_i) = (y_i,-x_i)`. These are the formulas already used in
`research/split-centres-global/code/complex_replay.py`; the scalar
identity and omission methodology are predecessor work, not new claims
of this audit.

Composing the pinned recipe over the integers gives the identity matrix.
Deleting its first bridge instead makes entry `(0,2)` equal `-1` rather
than `0`: input `x_1 = 1`, all other wires zero, acquires an erroneous
`x_0 = -1`. Deleting each of the nine recipe bridges gives a nonidentity
matrix (the same calculation applies independently to each of the eight
replicas). This also follows algebraically: every event matrix is
invertible and every bridge `B` is nonidentity. If the original product
`QBP` is identity, the product `QP` obtained by deleting `B` cannot also
be identity, since multiplying `QP = QBP` by inverses would give `B = I`.
This is a finite scalar-interface fact; it does not validate the full
physical or all-size realization.

## Predecessor and scope

[PR553](https://github.com/CrocSwap/integer-mult-bounds/pull/553), inspected
at head `0c3e5ee4719d705afd63fefd001091d70e55182b`, already formalizes
strict interiors of 144 borrowing windows for the historical PR531
504-helper ownership table and a projected 242-event controller. Its
description explicitly excludes physical implementation, atomic execution,
charts, exact scalar endpoints, and the uniform compiler. This audit does
not claim novelty for the strict-window principle, nor does it replace
those Lean certificates. Its distinct evidence targets the selected
PR626 492-helper table and checks the timing interface by a separate
event-state traversal and boundary controls.

Credit: PR626 ownership repair by chafreaky with OpenAI Codex; PR622/PR623
supplier and allocation work by jeremykothe2 and the credited Claude Code
agents; inherited PR531 ownership work by icekylinx; historical finite
formalization in PR553 by Rohan Arun with substantial OpenAI Codex
assistance. See the retained source packages' notices for the complete
ancestry. This review was prepared with substantial OpenAI Codex assistance
and is covered by the repository's Apache-2.0 license. It is an independent
reasoning pass within this automated contribution, not an independent
human audit or a formal proof of the multiplication theorem.
