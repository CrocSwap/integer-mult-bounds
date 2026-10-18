# Sprint claim

Track: complex supplier. OS-random assignment seed: **35**, generated once
with Python `secrets.randbelow(100)` on 2026-10-13 at sprint start.
Base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
Started 15:21:55 UTC; expected finish 15:51:55 UTC. The final 7.5 minutes are
reserved for verification and handoff.

Three narrow candidates were inspected: deferred sign gauges (already PR919),
individual coefficient preparation (already PR837/882), and deferral of one
power-of-two magnitude scale through a historical JP8 nonzero-frame run.
The third is chosen. Positive magnitude gauges change addition coefficients;
this differs from PR919's sign correction and PR969's deferred permutations.
PR949's fixed 26-ADD factory gauge search is a separate closed search class;
this experiment holds the JP8 event word fixed and tests single-register live
intervals, with every intervening macro and restoration explicitly charged.

Object: both orientations of the frozen PR626 JP8 scalar event word. Exhaust
every start at a scale by magnitude 2 or 1/2 in a nonzero frame, and every
later restoration cutoff before a copy/swap touching its register or a frame
or non-scalar boundary. Clear may reset the gauge for free; a later scale
can absorb the restoration. At most one register is gauged in an interval.
Compare against the minimum of all four PR837 circuits and eligible PR882
bounded-grid circuits, using the same rule before and after.

Deliverable: exact finite census, frozen receipt, complete cost argument,
independent checker and negative controls. Any saving is a historical scalar
result, not a new kappa or a complete physical supplier. No candidate found
will be reported only for this finite class.

No pinned sprint coordination issue was available (open issue inventory:
#650 and #913). PR metadata was refreshed through #972 immediately before
this local claim. No direct duplicate was identified.

Result (2026-10-13 15:47 UTC): completed the finite 221-start / 557,559-interval
cost census per orientation and checked one literal witness. One evidence-driven
pivot composed the witness with credited PR755 fan-out and PR751 fan-in, which
already beat its unshared form. Backward cost is 135 -> 102 per real component
after identical known-zero work-clear elision: 66 further real primitives.
Local backward row L1 grows 109/4 -> 109/2; no physical admission or new kappa.
Four arbitrary-input block maps, twenty mathematical controls, nine package
controls, optimized offline closure and source/base bindings pass.
Handoff branch: https://github.com/ToikY/integer-mult-bounds/tree/codex/complex-seed35
Final overlap refresh through PR975 adds related X4 Horner work; its object and
method differ, and no superiority over general varying-magnitude methods is claimed.
