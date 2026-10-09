# Recycling dead bit registers at deferred births: argument and scope

**Setting.** This is the bit branch of the merged #144 (icekylinx), after the terminal elimination of #147 (hpst3r).
Its word is Swapnil Jain's round-seven PR97 word at h = 23:

- non-deferred and omitted reads at frame 0;
- early V gates, phase 1 and the copied centres;
- deferred reads of the selected slots at their sigma frames, in the inherited readout order;
- late V gates, the rest of L, the output reads, then L^-1 and V^-1 at the full frame.

#144 charges the resulting chains per vertex in dimension m = 69: auxiliary chain steps, source and target chains and
copied centres, each three times; one gauge child 3 dim(sigma) per selected slot; and 2v endpoint children.
W = 2v + R and the deficit is 2,024 per vertex. #147 deletes 1,549 terminal output slots; that plan is used here
unchanged, as is #144's choice of 9,543 selected gauges.

**Two changes.** Nothing else in the word moves.

1. *Reads run late.* The selected reads keep their inherited relative order, but each one is executed as late as
   these constraints allow, instead of in one block after phase 1:
   - a read precedes the first operation that touches its slot, and that slot's V gate follows the read;
   - the V gates of one leaf keep their inherited chain order;
   - every read on a target precedes the first redirected write into that target.
2. *Dead registers are reused.* A slot D that is not an output slot is never touched again after its last
   operation, where it sits at the frame U_D of that operation. For 3,338 pairs (B, D) with D's last operation
   before B's read and U_D inside sigma_B, the register of D is moved from U_D to sigma_B and becomes B. B is then a
   deferred slot without an entrance gauge. This is jamesyc's #124 birth-read operation, applied to the bit word.

**Scalar identity.** The inherited identity holds for arbitrary start values of all slots: a slot s with start value
z_s contributes C_{T,s} z_s to target T through L and the root reads, and its read subtracts exactly that, where C is
the exact integer adjoint.

- Delaying a read does not change what it reads. Until its first operation or V gate, the register holds its start
  value, and a read only writes into targets, which nothing reads back.
- For a recycled pair, B's start value is whatever D left behind, a linear form in the data and the other start
  values. D's last operation is before the read and B's first operation is after it, so B's read sees that value
  and B's own contribution carries the same value with the same coefficients. The two cancel as before.
- D's remaining contributions are unchanged, because no operation reads D after its last operation.
- The inverse pass undoes the register updates (operations and V gates) in exact reverse order, at the full frame.
  On a recycled register this removes B's V gate before D's operations are undone. The inherited order, with every
  V^-1 after L^-1, would not restore the registers; `verify.py` checks that it fails.

`word147.replay` runs the literal word on the 23,979 physical registers with random scratch and data, over Z with
the exact integer coefficients and over F2. Every register is restored and every target receives its defining sum.
Three tampered words must break the Z identity: a recycled read of the register's entrance value, a recycled read
taken before its donor's last write, and the inherited inverse order.

**Frames.** Every frame is an original frame key of the PR97 word, so nondegeneracy is inherited. `word147.ledger`
executes the forward word on frame keys. Each scalar gate must find all its registers at one common key, and no
register may retreat in dimension. The check of actual nesting is separate:

- A move between two keys of one inherited certified chain, in that chain's order, is nested by the pinned audits
  (`check_lifted.py` D, `check_frames.py` X and Q) that #144 relies on. Those chains are the original slot chains,
  the X chains in their original V order, and the target chains in readout order with positive Z support, ending
  at t_T^perp. A subsequence of a nested chain is nested.
- Every other move is checked exactly over Q with integer bases rebuilt by `check_lifted.py`, and both frames are
  checked nondegenerate. There are 4,878 such moves:
  - 3,338 hand-offs U_D -> sigma_B (993 of them have equal dimension, so the two frames are equal);
  - 935 target moves from the last remaining level to a redirected V frame;
  - 605 target moves from one eliminated slot's redirected frame to another's V frame. These arise because a
    redirected V write now runs just before its slot's first operation rather than in the late-V block.

Delaying the reads does not reorder any chain. With no elimination and no recycling, the delayed word reproduces
every histogram of #144's row; `verify.py` checks this as a control.

**Accounting.** #144's ledger (`notes/paired-cube-sharing.tex`) charges a physical role by its entrance gauge and
its frame chain. A recycled register enters with its first occupant's gauge, follows one nested chain to the full
frame, and has its raw value restored, so it satisfies the same completed-core contract. Relative to #147, one pair
(B, D) with d = dim U_D and f = dim sigma_B

- removes D's final step of rank 23 - d (three copies) and B's gauge child of width 3f;
- adds the hand-off step of rank f - d (three copies);
- lowers W by one.

The removed rank is 3(23 - d) + 3f and the added rank is 3(f - d), so the mass drops by 69 = m and the deficit stays
2,024. The row is rebuilt from the actual ledger moves (`word147.row`) and priced with #144's own functions
(`price147.py`): `exact_moment`, the full rare-class fallback, the complex certificate, the finite bridge and the
47-constraint assembly. The largest child falls from 66 to 60, which only shortens the recursion depth bound.

**Scope.** This is a finite conditional construction. Every interface that #144 retains stays an assumption:

- the unchanged complete scalar word and the inherited rational frame audit of PR97;
- the paired source scheduling and completed-core sharing;
- the uniform recursion, analytic and tape contracts.

Not established here:

- The replay runs one core on its own bank, as in #147. That is the premise the shared-core argument uses.
- The pinned PR97 frame audits are relied on, not rerun.
- The plan is one legal choice found by a matching heuristic (`make_plan.py`). No optimality is claimed, and the
  certified value does not depend on how the plan was found.
- The headline uses the merged atom exponent 1/1000. The value at 1/2000 (gupt1156's #148) is reported separately
  and rests on the retained requirement a_bit < beta < 1 - a_bit.
