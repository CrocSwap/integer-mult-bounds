# Whole first-node preparation ownership

This source-level adapter surrounds the unchanged PR2697 Consumer.apply retained
by PR2825. It closes the preparation interval from entry through the invocation
of packet_engine.run, including constructors before the original try/finally.
It does not change the selected result, implement physical banks, or claim
bytezeroization of host memory reclaimed by Python. PR5135 supplies the separate
successful source-array reserve; it explicitly excludes this error obligation.

## Contract

The admitted runtime is the authenticated private PR2825 cohort, with canonical
Arena metadata, disjoint residue/index arenas, and well-formed fixed-width live
Words and erased available Words. All incoming borrowed heads and templates
start at1. The Context, Program, source, old directory, old_count, before, gap,
suffix and immutable source specifications belong to the caller. The first-range
geometry, arithmetic margins and retained source semantics are inherited. A
source guard may reject, including insufficient capacity and malformed source
records whose inspection leaves these storage invariants intact. We do not
promise termination on arbitrary noncanonical symbol streams. The observation
callback is absent, and the private runtime is used exclusively on one thread:
no concurrent unwrapped call, host tracer retaining arbitrary locals, malicious
callback, or reentrant consumer may run while the hooks are installed.

Host allocation/interruption failures, failed Tape.__init__, corrupted arena
metadata, foreign mutation of protected bytes, and failure after packet handoff
are excluded. The adapter catches ValueError from source preparation only.
These limitations are substantive: this is not universal exception recovery.

## Complete allocation and guard boundary

All counted source arrays are created by records.Tape or words.Word. Arena.zero
owns every Word permanently in arena.words; no numerical constructor can hide a
Word outside the arena. On canonical entry, zero checks inventory before creating
a slot and initializes its complete delimiter before returning. Later arithmetic
can reject but preserves the fixed RIGHT delimiter. Available slots remain erased.

All Tape aliases imported by counts/cardinality/stream/directory/records refer to
the same authenticated class. The temporary initializer wrapper registers each
completed new Tape in a weak dictionary. It therefore does not retain a history
of already dead objects. Every still-reachable new array is discoverable on error;
Python's active source traceback additionally keeps partial constructor locals
alive until cleanup. An object already unreachable has no remaining source owner
and is reclaimed normally; no physical erasure claim is made about its old bytes.

| Preparation phase | Allocations and possible rejection |
| --- | --- |
| request/view/bind/plan | finite specification checks; no source arrays |
| directory cardinalities | expected/emitted Count and Counter Tape copies; radix-power numerical scratch and arithmetic guards |
| old prefix | saved serialized Tape, countdown and decoded numerical words; code, digit, boundary and extent checks |
| high enumeration | complete or partial Odometer digit matrix, directory output, count increments; capacity/carry checks |
| width/depth | divisor, one, columns, remainder, fields; first-range and carry guards |
| geometry/layout | copied cardinalities and fixed numerical roles; positive extent/context checks |
| first frame | read_prefix output, Fields empty constructor array, Callback fixed Words and four Stack arrays; program/prime-power/rank/depth guards |
| frame close/validation | closed-but-retained arrays, released numerical roles, final extent equality guard |
| packet invocation | ownership transfer; hooks removed before original packet body |

This list includes the partial Odometer whose list comprehension fails before
assignment, Callback whose constructor raises before frame is assigned, and
constructor RHS objects that die before their caller receives them. No catch
needs the partially initialized owner object itself. Existing source finally
blocks may release subsets first; the final arena difference is idempotent with
respect to those releases. All such paths are inside the outer transaction.

The PR2749 authenticated count inventory has98 owned/borrowed roots. The retained
backing argument permits coexistence of previous LHS and constructor RHS, giving
196, conservatively200 Tape roots. Setup adds directory output, two saved-prefix
holders, first-prefix output, the empty Fields constructor, and four frame stacks:
at most209. The registry bound216 covers these simultaneous source roles. Loops
replace rather than accumulate Count objects; there is no count-bearing recursive
call in setup. The finite fixture peak is a control, not this proof. Metadata is
O(H_R+H_I+216), where H are allocated numerical slot counts; it is not fixed finite
control. Runtime dictionary/set operations are explicitly host bookkeeping.

## Borrowed state and rollback

The source preparation reads source/old directory/Program/count arguments and
context.highs without writing their bytes. It changes cursors only. Numerical
arithmetic copies input Words; the source writes only freshly owned temporaries.
Protected numerical Words are never freed or moved left of cell1. This follows
from the authenticated rewind/read loops and free arguments in the phase table;
foreign aliasing of an owned temporary with a borrowed role is excluded by Arena.
The complete borrowed Tape set is those eight root roles (four count arguments),
deduplicated by identity. Other suspended caller arrays are never accessed.

At entry the adapter records protected live slot identities and free-list order,
not byte snapshots. On a pre-handoff ValueError it takes a bounded strong list of
currently reachable new Tape objects. It rewinds and clears each. Each such Tape
has a nonblank prefix followed by a blank tail, so clear erases its entire logical
content, including a partial writer prefix. LEFT is retained. Arena.rollback
clears every newly live Word and rewinds protected Words. The original free order
is restored, followed by newly allocated erased slot identities. Historical new
backing is not shrunk or silently reclaimed. The two templates and all borrowed
Tape heads are restored to1. A Tape paused at LEFT is handled by one right step;
Word operations preserve the stronger head>=1 invariant needed by rewind.

Consequently protected identity sets, bytes and canonical heads equal entry,
all surviving newly owned numerical slots are erased and available, and no new
reachable source Tape retains logical content on outward rejection. The outward
exception is freshly raised outside the original except suite with the same text;
it retains neither the original source traceback nor a context chain. Exception
identity/traceback are deliberately not preserved. Success removes hooks before
calling the exact original packet function with unchanged arguments and returns
its result; the original Consumer finally still runs. Post-handoff exceptions
propagate according to that unchanged source, with no additional rollback claim.

## Charged cleanup and bounded bookkeeping

Let Z be the sum of retained lengths of all distinct tracked/borrowed Tape arrays
at rejection plus (H_R+1)(R+2)+(H_I+1)(I+2), including numerical templates. Let T
be their number of distinct Tape objects. Cleanup performs at most

    10 * (Z + T + H_R + H_I + 1)

source reads+writes+unit moves. A rewind costs at most twice the visited extent
plus a constant; clearing after rewind scans and blanks a prefix and rewinds
again, below seven times its backing length plus a constant. Each numerical slot
is cleared or rewound once, and each template rewound once. Tape aliases are
removed before charging. This bound uses failure-time retained extent, not a new
entry-parametric preparation-time theorem. Setup work before failure remains
charged separately by its actual source meters. Metadata copying/restoration
costs O(H_R+H_I+T) operations/identities; registry updates cost dictionary operations
per new Tape, with at most216 live entries. No payload snapshot, unbounded strong
allocation log or free byte-comparison oracle is used by the adapter.

## Evidence and limits

The verifier uses byte snapshots only as independent test oracles. Actual retained
width64/rank1/depth2/mod3 preparation reaches the packet edge; full selected payload
is not executed. Inventory failures at residue capacity17 and index capacity10
reproduce the original leak and are restored by the adapter. Controls cover old
record parse guards, width/layout/frame constructor boundaries and final frame
validation, success transfer and post-handoff exceptions. Finite injections
support the source proof; they do not enumerate all possible inputs or failures.

No physical compiler, bank zeroization, full recursive error recovery, complete
GL64 payload replay, outer bootstrap or selected-frontier admission is claimed.

## Open next questions

1. Lower reachable-source ownership to physical bank reclamation with a charged
   erasure protocol; Python deallocation is not physical tape cleanup.
2. Extend the transaction boundary through the packet engine and actual recursive
   callees, including output ownership when a callee violates its contract.
3. Derive an entry-parametric whole preparation/rejection time bound rather than
   the failure-extent cleanup bound used here.
