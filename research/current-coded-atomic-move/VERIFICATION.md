# Verification, partial physical evidence and bounded attempts

Prepared for @CubeJerry with substantial OpenAI assistance.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Exact status

The universal source-composition theorem in PROOF.md has been cross-reviewed
under its explicit predecessor contracts. Physical evidence is **partial**:
there is no completed exit trace, complete three-factor sliced witness, or
uninterrupted whole-MOVE receipt. A timed-out command is not counted as a
pass and is not a mathematical obstruction to the stated theorem.

The bounded source/administrative receipt authenticates 119 retained files
and checks all 512 original source columns, 262,144 matrix positions and
absolute phases. The literal right/C/left map agrees with every independently
computed original-source column. Four altered phase, direction, axis and
missing-exit controls fail that equality and the separate full-packet oracle.
There are five typed source rejects, three alias rejects, one retained-source
corruption reject, 24 exact-cost administrative successes, four rejection
cases, shrinking reuse, and an unstaged rollback countercontrol. The two
source words have (early,late) counts (5,6) and (5,7), giving 92 and 104
ordinary calls per outer-row for f > 1 and zero at f = 1.
A capacity-65 constructor gives 4,118 ports and rejects the capacity-64
4,106-port inventory. This checks the constructor-dependent inventory
statement and does not admit its ordinary numerical supplier.

The primitive tape definitions preserve literal read/write/unit-move state
transitions and counters. A 30,000-command deterministic comparison, seed
19658963, and eight illegal-instruction rejects are regression evidence for
those definitions, not a new hardware theorem or an algorithmic speedup.

The lead separately reviewed the source geometry, tensor-coordinate join,
absolute phase, sufficient grid/range condition, complete staged rollback,
actual origin/transfer/commit/retire loops and retained backing. The lead
independently confirmed the 22V + 35 / 13V + 21 added action formulas. This is
author-side AI review, not human or proof-kernel admission.

## Completed physical traces

Every row below uses the full 4,096-record, 73,728-bit packet, the same
157-bit descriptor, and 4,106 fixed private ports. Source and header hashes,
exact boundary-byte comparisons, ancestry/origin checks, complete private
erasure and provider closure checks are retained in the raw receipts.

| Trace | Numerical factor actions | Added raw actions executed | Total | Observed status |
|---|---:|---:|---:|---|
| Entrance | 3,310,255,976 | 589,838 transfer | 3,310,845,814 | Exit 0 within 590-second watchdog; exact elapsed not recorded |
| Positive leaf | 316,156,063 | 0 | 316,156,063 | Exit 0 in 56.097 s |
| Reachable late leaf rejection | 236,586,113 | 368,647 stage retirement | 236,954,760 | Exit 0 in 42.567 s |

The compatible successful entrance/leaf prefix totals **3,627,001,877**
literal actions. Its exact returned stage equals the complete middle packet
used by the reference composition. The physical trace stops before the exit
and final commit; the full source endpoint is an independently checked
reference answer, not a completed physical output.

For the negative test, original coefficient index 4063 is zero; its exact
right-monomial image is the unique zero at address 4095, in the final C pair.
The actual leaf on that reachable postentrance packet raises
`inexact Gaussian halving`, preserves its complete stage input, and returns
all heads and retired work. The separately executed stage retirement leaves
the protected original bad input unchanged. This tests the actual late leaf
and cleanup boundary. It does not execute entrance plus failed leaf in one
process, and it is not a full failed-MOVE physical receipt.

The two compatible positive traces have 3,213,246 materialized private body
cells when each role's maximum is retained, versus 2,023,183 if one wrongly
takes only the largest active slice total. Including fixed private origins
and ancestor prefixes gives 3,233,774 private cells. The complete materialized
prefix state, including public and descriptor, has 3,307,679 cells. The
unexecuted exit cohort contributes only its initial blank cells to these
**partial-prefix** observations; no measured full-MOVE backing is claimed.

Array extents measure materialized cells, not all visited blank positions.
The rigorous conservative upper bound for all visited cells of this prefix
is **3,627,100,418**, obtained from its initial regions plus its total literal
actions. Every newly visited cell requires a unit move. This loose observed-
trace bound is distinct from the size-dependent predecessor backing proof.
The rejection has its own separately reported materialized/visited bounds;
its freshly seeded state is not appended to the successful prefix as though
that reset were free.

`receipts/MANIFEST.json` authenticates the saved receipts. `SLICED-RESULT.json`
and `check_receipts.py` recompute exact source/interface consistency, complete
executed-prefix bills and rolewise retained storage, with five changed-byte,
header, action, stage and false-scope controls. Running that checker does
**not** re-execute any long physical trace. No complete exit receipt is
present or synthesized.

## Attempts that did not complete

1. The first whole 4,096-record packet used retained DenseTape. A ten-minute
   research stop was enforced through the tool session; observed elapsed was
   643.677 s, exit 130, no complete receipt. A cross-command OS signal could
   not locate the process; the session interrupt stopped it and the watchdog
   was closed. This is not represented as exact termination at 600 seconds.
2. One whole-packet retry used the independently checked literal primitive
   tape. `timeout 590s .../check_move.py packet` returned exit 124, with no
   complete receipt. Computational source bodies were unchanged.
3. The single exit-factor slice hit its 590-second bound, returning exit 124
   at 590.102 s with empty stdout. It was not extended or restarted.

The exact attempt records are in `ATTEMPTS.json`. None is a performance
lower bound or mathematical negative result. No background execution remains
scheduled for these attempts.

A proposed 512/1024-record fixture was rejected before execution: positive H
and the complete front/back reservations imply a >= 12 at native rank nine.
The reduced H = G = K = 1 descriptor is a valid local interface but is not
the enclosing producer's H = dG, K = 128G allocation. No guard was weakened.

## Returned-state equivalence and replay

The returned stage and descriptor are compared byte for byte with the next
slice's full inputs, with all heads at their origins and all ancestors intact.
Each completed numerical cohort is blank and closed. Later providers use
separate, still-unused cohorts and finite control, exactly matching their
fresh slice state. Reinsert earlier blank tails: later factors never read
those roles or their diagnostic highwater/call counters. The rolewise maxima
retain their storage. This justifies the observed entrance/leaf prefix join
and the general proof's composition rule; it does not manufacture the
uncompleted exit trace.

The registered normal/optimized source and receipt-consistency gates are:

```sh
python3 -B scripts/research_package.py --package research/current-coded-atomic-move
```

Expected markers are `PASS_CURRENT_CODED_ATOMIC_MOVE_SOURCE_AND_WRAPPER`,
`PASS_CURRENT_CODED_ATOMIC_MOVE_RECORDED_SLICES`, and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=partial`. All four registered commands passed: source/interface checks and saved-receipt
consistency checks in both normal and optimized Python. The captured output
is in `GATES.log`. Metadata/source-pin validation also passed. The declared total
budget is 480 seconds. Long physical traces are deliberately separate from
these gates and are not implied by their success:

```sh
timeout 590s python3 -I -B research/current-coded-atomic-move/check_slices.py entry
timeout 590s python3 -I -B research/current-coded-atomic-move/check_slices.py leaf
timeout 590s python3 -I -B research/current-coded-atomic-move/check_slices.py reject
```

The same exit command is available as `check_slices.py exit`, but its observed
attempt did not complete within that bound. Do not count its unrecorded work
as part of the successful action invoice. Whole `check_move.py packet` and
`failure` modes are also available; neither has a successful whole-process
receipt in this package.

## Remaining limits

The exact raw current_local source triple and already normalized local
geometry are the theorem's boundary. Nested caller tokens, real placement,
stock, producer geometry, full common-grid allocation, stronger ordinary
supplier, nonleaf tariff, literal Controller.execute_table export and full
selected cold replay remain outside it. The arbitrary-interruption or
malformed-late-output rollback problem is outside its named failure domain.
All five selected assumptions and the selected certificate remain unchanged.
No new kappa or unconditional multiplication theorem is claimed.
