# Native-history action equivariance

Chris R with OpenAI Codex assistance. This adapts the source semantics of Jose
Manuel's #2899 Ordinary/PhysicalArena and numerical caller, the retained
#2769/#2635 numerical parking lineage by ywz65, and #3385's actual complex
composition. The authenticated #4167 closure is the scientific input. No
predecessor bytes, allocator queue, slot identity or numerical implementation
are changed. The executable `mechanism.py` is a checker and source-kernel
experiment, not an extra runtime operation.

## Statement and precise domain

Fix the compiled source, capacities, programs, q, numerical/descriptor widths,
and profiles. Use the same authenticated deterministic plan selector/factory,
independent of allocator order, and semantically inert observers. Compare two successful invocations of retained
`ordinary.Ordinary.execute_plan`, including its genuine fitted branch and all
recursive native children. At entry require the same encoded borrowed payload
and descriptors at the same heads, the same empty output contract, and the
same fresh/rearmed marker phase. All six arenas are source-owned, have no live
or escaped numerical residents, and have the source-defined template state;
the runtime codec is at its exact closed baseline. Different **legal free-slot
orders and previously visited blank backing are permitted**. Exclude active
reentry, interrupted/failing invocation recovery and externally retained
handles to released slots.

Then both invocations have equal ordered (reads, writes, unit moves) totals,
equal semantic output bytes and output heads, and preserve the same borrowed
bytes/heads. They restore the corresponding successful closed state, permitting
different resulting free orders and historical backing. Equality is coordinate
wise and so holds under every fixed positive weighting of these three actions.
It is not equality of Python wall time, total implementation instructions,
physical-role trace addresses, or per-role high-water space.

The theorem compares **equal corresponding numerical values**, not arbitrary
arithmetic inputs. A separate source data-flow argument is required to extend
it to changed payloads whose numerical control computations are equal. In
particular `Ring` and `Unsigned` have value-dependent paths; this theorem does
not erase changed-core dependence by fiat.

All calls in the actual complex composition enter Ordinary warm: the retained
`CompactEngine` constructor explicitly completes `native.finish(False)` and
erases its output marker before exposing the engine. The actual invariant
therefore supplies matched marker phase even at the first monomial invocation.
`Binary.run` also erases the consumed native output marker after each return,
so subsequent complex calls retain that warm-erased phase. Generic standalone
Ordinary clients need the rearm correction below.

## Source access boundary

The relevant source modules are loaded from the immutable archives behind
#4167's authenticated runtime, rather than a replacement numerical model:

| Source | Slot/history-sensitive sites | Treatment |
|---|---|---|
| `physical_words.PhysicalArena` | fixed `words`, `available`, `live`, `initialized`, template | Six fixed role inventories; preparation and marker retirement scan actual tapes. |
| `words.Arena` | `zero`, `free`, `free_many`, `rollback` | Allocate/pop and free/push fixed labels; numerical bodies use corresponding logical word handles. Rejection rollback is outside successful theorem. |
| `bank_codec.BankParking` | sorted live-slot scan; fixed-width label serialization; original-slot restore | Equal-length records within each bank; phased parent/child relation below. |
| `macro_machine.Machine` | `boundary`, `call`, `restore_context`, frame closure | Typed header references to modulus, one, cap, size and depth are mapped, saved and restored with their parent activation. |
| `role_parking.FiniteFields` and `RoleParking` | fixed-width header fields, four-bit symbol encoding | Equal lengths and fixed scans, even when encoded slot digits differ. |
| `session.RootSession` / `ordinary.Ordinary` | six-arena prepare/erase/rearm, fixed pools, codec baseline | Marker phase and corresponding widths are included, not inferred from `.closed` alone. |
| `controller.Callback`, `children`, `numeric` | protected live sets | Corresponding logical resident sets; no slot-valued numerical operand. |
| `scratch_pool` | separate slot/lease map | First-free fixed pool has no persistent available-order queue. Identical logical allocations have identical live pattern. Its lease generations are not PhysicalWord safety. |

Numerical record methods in `records` use encoded **numerical index values** to
seek stream records. Those are not PhysicalArena slot labels and are preserved
as numerical data. `PhysicalWord.slot` denotes a fixed tape role, not a distance
along one tape. No head jumps or dictionary host lookup distances are imported
into the action tariff. The dictionary codec separately charges every literal
read/write/unit move and every executed two-tape interpreter transition.

## Phased relation, not one fixed permutation

1. **Active numerical computation.** Pair every live logical word handle with
   its counterpart, preserving arena, value, width, head and alias relation.
   Pair the remaining free slots by their ordered position in each available
   stack. Pop extends the live bijection; free removes the handle and pushes
   its paired labels. Equal-value arithmetic follows the same bit tests,
   carries, loops and allocation/free schedule. Every corresponding read,
   write and unit move has the same charge. Template copies are width-equal.
   Object-identity shortcuts, such as `a is b`, are preserved by injectivity.

2. **Parent suspension.** Save the parent logical handle map and the five typed
   numerical references in the finite header. `numerical.park` scans each
   fixed capacity in physical-slot order. A global permutation need not
   preserve that order: logical records can be reordered. Nevertheless the
   same number of live, non-granted records is written for each bank, and all
   words in that bank share the same template width. Fixed-width bank/slot
   digits have the same length. The bit-erased two-tape machine has identical
   control and action shape. Hence the complete frame has the same length and
   action bill; equal-length record permutations do not change stack head
   displacement, including above an existing matched-length suspended prefix.

3. **Child activation.** Child grants are corresponding retained live words;
   all remaining slots are paired afresh by available-stack order. This map
   need not equal the suspended parent's map. Child allocation may reuse a
   parked parent's physical slot, legally, because its body was erased and
   its logical parent value lives in the saved record. The child induction
   preserves its own numerical values and exact return contract. It frees all
   grants/work before restoration. No inactive parent object is used as a
   current resident.

4. **Parent restoration.** Each source record carries its own bank and original
   slot label. `_restore_word` selects that exact original slot, moves it to
   the top of the finite free map and allocates it. Equal-width records restore
   the saved parent words at their original physical objects. Both executions
   therefore recover their respective saved parent bijection even though they
   pop different logical orders. After the whole frame, re-pair the still-free
   slots in queue order. `restore_context` consumes the restored typed header
   references and rebinds modulus/one/cap/size/depth; their numerical values
   remain equal. This is a separate activation-domain relation, not a claim
   that a single physical permutation commutes with sorted parking.

5. **Root completion and repeated use.** Each successful session closes live
   scopes and templates exactly as the retained source specifies. Empty-role
   marker scans depend on the complete fixed inventory, not previous capacity
   usage. The two fitted outer native calls retain initialized templates in
   between; no reset is inserted there. At eventual Ordinary completion every
   resident is released. A new invocation can begin with a different free
   order, so induction covers arbitrary finite sequences of successful calls
   and all finite terminating recursion depths admitted by the source.

The proof preserves arbitrary legitimate prefixes/suffixes, spectators and
nonconstant correlated payloads under equal-input hypotheses. Numeric width,
range, exact C arithmetic and all admission/termination premises are inherited.

## Exact numerical codec invoice

Let bank b have capacity c_b, word data width w_b, slot width
s_b=max(1,bitlength(c_b−1)), n_b=1+s_b+w_b binary record bits, and m_b parked
words. For a complete matched numerical park/restore frame with canonical heads
and no retained grants, excluding the intervening child body, the source bill is

```
(R,W,M) = (15,2,12)
        + sum_b m_b (14 n_b + 10 w_b + 32,
                      6 n_b +  3 w_b +  8,
                     12 n_b + 10 w_b + 30).
```

The source-derived decomposition per word is:

| Component | Reads | Writes | Unit moves |
|---|---:|---:|---:|
| `_supply` | 2n+2w+5 | n+1 | 2n+2w+6 |
| interpreter `push` | 4n+6 | 2n+2 | 3n+3 |
| source `Arena.free` | 2w+3 | w+1 | 2w+4 |
| restore top test + interpreter `pop` + `_restore_word` | 8n+6w+18 | 3n+2w+4 | 7n+6w+17 |

The frame overhead includes both empty-port checks, begin/end, final F test and
all rewinds: park (6,1,5), restore (9,1,7). Loop terminator reads, append checks,
RIGHT/LEFT markers and empty cases are counted. Granted words change which
records are parked, not the fixed scanning count or record tariff. Their later
child destruction is part of the child bill, not this expression.

`mechanism.checks()` uses actual capacity-four PhysicalArena instances. Legal
completed numerical allocations/frees produce orders [3,2,1,0] and [3,0,1,2].
The same logical nonconstant words occupy [0,1,2] versus [2,1,0], so their encoded
slot IDs and record order genuinely differ. Real park, intervening child reuse,
and restore cost (1273,460,1168) on both sides; after removing the measured child
body the exact formula gives (1179,428,1068). Original object identity, values,
heads and all terminal numerical/codec cleanup are checked. This kernel fixture
supports the proof; the separate fitted tests exercise actual Ordinary recursion.

All 490 entries of the actual parking transition table collapse consistently
into 360 classes after replacing 0 and 1 by a common binary-symbol shape. Next
state, write presence and head moves coincide. A mutation making one binary
value move a different distance is rejected. This finite table certificate,
combined with the fixed-width loops above, proves bit-shape action invariance;
finite equal timings alone would not do so.

## Freshness, control and storage

For a standalone warm engine let K be the number of markers initialized by its
literal `rearm` loops, excluding its own output and dictionary packet marker:

```
K = |outer pool| + sum_four_banks(capacity+1)
  + |runtime roles| + |runtime handoff| + |runtime pool| + 1
  + (runtime arena capacity+1) + (runtime index capacity+1).
```

Each `initialize_marker` costs (2,1,2). Own-output checks cost (2,e,2), with
 e=1 for a BLANK marker and e=0 for an already retained LEFT marker; dictionary
marker preparation costs (1,1,2). Thus the exact rearm bill is
(2K+3,K+e+1,2K+4). A fresh standalone invocation skips this bill. The source
complex Compact path starts and returns in the same warm-erased phase, so equal
call comparison includes the same rearm work rather than treating it as free.
The actual marker-only capacity-four control checks K=452 and rearm actions
(907,453,908) with retained LEFT versus (907,454,908) with erased BLANK: a
false-canonicality claim would miss exactly one write. This is explicitly a
marker control, separate from the genuine fitted arithmetic evidence.

The result introduces zero runtime resets, zero fresh engines, zero extra
physical tapes and zero numerical-width work. For finite-control realization,
capacity c is fixed before input: an available ordered free list and its live
complement have at most (c+1)c! representations. Six queues therefore require
at most ((c+1)c!)^6 states (a deliberately loose bound). Each pop/push/live test,
stable slot selection and removal/reappend is a direct transition on that
finite state. Slot-bit decoding keeps its s_b literal steps. This supplies a
fixed resource realization without a width-dependent sort or scan. It does
not assert Python `list.remove`, dictionary access or `set` operations take the
same elapsed time. Enclosing instruction/selector compilation costs retain the
separate model and threshold in the complete comparison.

Previous visited blank cells are not reclaimed. The theorem permits differing
high-water totals on individual physical slots; only current numerical contents
and heads participate in action coupling. Any total-space claim must sum the
historical maximum backing over each fixed role, including both codec tapes.
No-escaped-resident ownership is a source premise, not discoverable from an
empty `live` set: old Python Word references are not generation-checked leases.

## Open next questions

The history result removes the native allocator-order residual on the stated
same-input domain. It does not itself price changed numerical descriptors,
additional producer/service work or any unmatched controller context. Apply the
complete comparison ledger and a separate data-flow proof before cancelling
changed-core calls. The physically worthwhile decision remains governed by
that full fair-baseline inequality, not this local equivariance theorem.
