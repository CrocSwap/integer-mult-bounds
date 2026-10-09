Literal fixed-tape parking primitives — Lean4.21.0

The two new modules define actual deterministic tape transitions over Mathlib's
bidirectional Turing.Tape. Payloads are arbitrary bit lists. The finite alphabet
contains blank, separator, zero-bit and one-bit. The pop table has six states
and uses three tapes; the push table has three states and uses two tapes.
The push source tape is explicitly reused as the pop output in the round trip.

This is more than an abstract list append/reverse cost model: instruction tables
receive only a finite state and the currently scanned symbols. Each emitted
action writes at most one symbol and moves each head by at most one cell.
head_local_refinement proves that those finite tables are exactly the step
functions whose iterations occur in the correctness/time theorems. Lists in
the statements describe initial/final tape contents; no transition reads a
list length or performs an atomic list append/reversal.

FORMAL RESULTS
TapeStackPush.push_correct: from a source bitstream of length n at its origin
and a parking stack at its current top, push the entire stream plus separator,
erase the source, and return its head to the origin in at most2n+2 transitions.

TapeStack.pop_correct: from that parked bitstream and empty temporary/output
interfaces, recover the original left-to-right stream in at most3n+5
transitions. The output head returns to the first payload cell. The temporary
returns to its empty interface, and the parking tape returns to the exact
previous top with the full arbitrary ancestor suffix preserved.

The pop first transfers the parked stream into a temporary in reverse order,
then transfers it back into the output and rewinds the output. This avoids
assuming a unit-cost length counter or a primitive seek-to-length operation.
The bounds contain no term depending on ancestor depth or stored length.

park_pop_round_trip composes the proved functions, explicitly reusing the
erased source as output. The two invocation counts sum to5n+7. A transition
table for the combined entire scheduler is not supplied: finite control
handoff and other surrounding primitives still need integration.

Boundary markers are explicit preconditions, never payload bits. install_boundary
and remove_boundary prove that two local transitions can install/remove the
left marker while preserving the head position and all payload. For an empty
work tape, remove_empty_boundary restores a genuinely blank tape. Thus the
marker convention has only constant initialization/cleanup cost; an empty
marked tape is not mislabeled as literally all blank.

SCOPE AND ADVERSARIAL QUALIFICATIONS
All36 declared theorem audits are included in the fresh verification receipt.
Only propext, Classical.choice and Quot.sound occur. No admitted lemma, custom
axiom, native computation shortcut, variable alphabet or variable tape count
is used. The runtime theorems establish an upper bound by a specified run
length; first-halting/minimal runtime is not separately proved because done
states stutter.

This is a custom finite-control multitape transition system over Mathlib Tape,
with a proved finite instruction-table implementation. It is not claimed to
be an embedding into a preselected universal-machine instruction language.

The ancestor's final contents and head position are formal consequences.
The tables and phase invariants stop at the local separator and show why no
ancestor scan is required; a separate quantified intermediate-trace safety
theorem is not part of the present package.

The whole recursion scheduler is not proved. Its glue must preserve the
parked parent record AND its stack head across each child execution, return
reused source/temporary tapes in the specified empty forms, bind its finite
call schedule, and account for active I/O, descriptors, row splitting and
frame operations. These primitives close one concrete linear-cost obligation,
not the entire integer-multiplication machine theorem.

REPRODUCTION
Use the pinned cached Mathlib project (revision
308445d7985027f538e281e18df29ca16ede2ba3) and Lean4.21.0:

  python3 check.py --mathlib-project /path/to/formal/lean \
    --lean-bin /path/to/lean-4.21.0/bin

check.py copies the two sources into a fresh temporary module directory,
rebuilds dependencies in order, checks all36 theorem/axiom reports, and writes
source hashes and logs under verification/. It installs nothing. review.txt
records an independent source/specification review of the delivered modules.
