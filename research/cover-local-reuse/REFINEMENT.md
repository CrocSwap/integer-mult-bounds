# Refining the compensated reuse word

`refine_reuse.py` regenerates this checkpoint from the canonical late-reuse
compiler. It uses four deterministic steps in this order:

1. Move equal operation frames together when their external predecessor and
   successor frames permit a lower paid moment. Source injections, source
   gauges, root frames and the initial reuse handoffs remain fixed.
2. Reselect the 780 late aliases. Donor candidates are ordered by descending
   final-frame dimension, then death position and role number. Augmenting paths
   preserve the maximum matching size; this ordering is a heuristic for its
   paid histogram, not a claim of globally optimal weighted matching.
3. Adjust existing nonzero source gauges, retaining the scalar chronology,
   read deadlines, operation frames and alias mapping. Every changed gauge
   remains between its donor's last frame and its own first gate frame. On
   each target it must follow every earlier read frame and precede every later
   read frame. Equal gauges sharing a target may move as a complete group.
4. Optimize operation frames again, including reuse handoffs. A donor's final
   frame may move only inside the recipient's fixed source gauge. The recipient
   starts at that gauge. Every operation still uses one common frame on both
   physical registers, and every physical chain remains nested.

The first operation pass changes 2856 gates. The gauge pass changes 88 gauges.
The final operation pass changes a further 2473 gates. These counts describe
successive passes and must not be added as a count of distinct final changes.

The scalar DAG, read deadlines, deferred-role inventory and operation order
remain unchanged. There are still 2483 disjoint aliases: 1703 early and 780 late.
The compiler updates all recorded handoff frames after the final operation pass,
then independently reconstructs the complete source and target frame chains.

All descent comparisons use frozen integer weights. The final claim comes from
an independent exact moment calculation on the reflected physical word. The
audited local word has 20494 physical auxiliary roles and 7075117 expanded scalar
operations per stage. With the fully paid padded triple geometry, its coarse
saving is **4.25192098e-4**. This is a local coarse value; the outer certificate
separately computes the all-size multiplication saving and its overhead charges.

Reproduction runs the complete compiler from the pinned PR117 witness. The cold
build compares the resulting operation frames, source gauges, alias pairs and
read deadlines with the independently audited candidate before writing the
profile and running the full literal reflection audit. Dirty-scratch replay
includes controls that omit compensation or perform it before the donor's last
value-producing gate; both must fail the target identity while restoring scratch.
