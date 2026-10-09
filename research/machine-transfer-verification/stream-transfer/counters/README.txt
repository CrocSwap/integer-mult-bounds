Physical binary ripple counters with returned heads
=================================================

RippleCounter.lean defines an actual one-tape, six-state finite-control
increment/decrement primitive using the existing TapeStack four-symbol alphabet
(blank, separator, zero, one), Action and perform. Each instruction reads one
head symbol, writes at most that cell and moves by at most one position. The
table does not receive a length, index, list, descriptor or tape position.

A width-w counter is little-endian between two separators, with its head on the
least-significant cell. The left and right exterior tape contents are arbitrary
and preserved. Width zero is also supported (the two separators are adjacent).
The representation is

  ready bits ancestor suffix =
    Tape.mk₂ (separator :: ancestor) (bits.map bit ++ separator :: suffix).

Mode.carry true increments; Mode.carry false decrements. On encountering a bit
that propagates carry/borrow, the machine flips it and moves right. It flips the
first resolving bit and returns left; if it reaches the right separator, it
sets the overflow flag and returns left. The left separator returns the head
to the original least-significant position. Both boundaries remain unchanged.
The fixed-width result wraps modulo 2^w. Underflow is a destructive zero test:
decrementing zero returns all ones and flag=true. Clients reset before using
the next block; this primitive does not pretend the zero word was preserved.

Main proved statements
----------------------

counter_correct: literal run of the finite table returns the updated word,
correct terminal flag and original head position in exactly 2k+2 steps, where
k is the initial carry/borrow prefix length. Exterior contents remain identical.

counter_running: every earlier time n<2k+2 is active. The stated count is the
first completion time, not an upper bound obtained by stuttering in done. This
allows a surrounding controller to react immediately to the done state.

increment_value and decrement_value: exact natural-number modular arithmetic
equations, including the 2^w wrap term. increment_overflow_iff_max detects exactly
value+1=2^w. decrement_underflow_iff_zero detects exactly input value=0. updated
and iterate preserve the word width; value is always below 2^w.

total_steps_bound: for N consecutive primitive calls IN ONE FIXED DIRECTION,
starting with any width-w word, the sum of literal instruction counts is at
most 4N+2w. Increment uses number of ones as amortized potential; decrement uses
number of zeros. Arbitrary alternating directions are not covered by this
bound. It includes the return of the head on every call.

countdown_value, countdown_not_finished and countdown_final_underflow: starting
from B-1, emitting one payload item and then decrementing detects underflow
exactly on the B-th item, with no early boundary. complete_block_cost bounds
those B counter calls by 6B provided w<=B. The hypothesis remains explicit;
canonical binary length preparation, or a separate width charge, must establish
it. Leading-zero padding is allowed by the generic 4N+2w theorem and is charged
through w; it is not granted a free O(B) bound.

Cost and composition boundary
-----------------------------

totalSteps sums separate correctly specified physical primitive calls. It does
not itself implement a controller that restarts them, emits payload, switches
row class or resets the counter. Those mode changes and payload operations add
a constant per call; copying/resetting a local saved-length template and head
returns must be charged separately. The root routing/reset modules are designed
to supply that composition. Nothing here scans a larger descriptor per payload
bit or assumes free access to a selected bit of a global address counter.

The proof is uniform in the arbitrary exterior tape contents, which are never
traversed. Counter initialization, binary descriptor arithmetic, nested loops,
stream routing, full ordered-affine primitives and the multiplication-machine
recurrence are outside this two-module package.

Validation and reproduction
---------------------------

There are 36 new audited declarations: 13 in RippleCounter and 23 in
CounterArithmetic, including arithmetic/tape helper lemmas. TapeStack contributes
23 unchanged dependency audits. The manifest binds all source hashes. Only
propext, Classical.choice and Quot.sound (or subsets) are permitted; no new
axiom, admitted proof, or native_decide is present. Existing packages are unchanged.

With Lean4.21.0/Lake on PATH and the pinned existing Mathlib project:

  python3 outputs/stream-transfer/counters/check.py \
    --lake-project work/agents/lean-foundations/formal/lean

The checker installs nothing, rebuilds TapeStack and both new modules in a fresh
temporary directory and checks every printed axiom report. --tapes-dir and
--output override dependency/report locations. The Mathlib revision is
308445d7985027f538e281e18df29ca16ede2ba3. Fresh delivered logs and receipt are in
verification/. declaration-scope-map.json gives the exact mathematical meaning
of each declaration.

This formalizes the ripple-counter subargument in upstream/build/sections/
02-streams.tex. It reuses the prior TapeStack physical tape/action interface.
It does not claim a new counter algorithm or completion of elementary stream
routing by this module alone.
