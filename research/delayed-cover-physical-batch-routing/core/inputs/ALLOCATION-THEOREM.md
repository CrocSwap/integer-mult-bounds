# Safe finite allocation and a physical recursive owner dispatcher

2026-10-26. This is a conditional all-size implication theorem, not a
claim that a machine checked proof or the complete selected-source binding
has already been supplied. Its purpose is to isolate and prove the ownership
part without using ownership of recursive children as an assumption.

The important distinction is between (i) fixing an astronomically large but
finite compiled template and (ii) executing that fixed template at an
unbounded, input-dependent recursion depth. Fresh static names solve (i);
delimited tape segments and an actual return protocol solve (ii). Neither a
new physical tape per runtime depth nor one aliased owned bank per depth is
used.

## 1. Precise statement

Fix a uniform compiled template T before varying the multiplication input
length. Write W=B_N>=2 for its final productive width, m>=2 for its uniform
native rank, and s for its finite number of paid rank-one calls. W is not
the raw P104 count 13,444. Fix all its native/scalar programs, finite routing
lists, input/output formats and primitive transition tables. Its finite
control may contain an arbitrarily large number of states and use an
arbitrarily large but fixed number of tapes.

Assume the following premises. They are deliberately separated so a source
review can reject an ownership premise hidden in another assumption.

**S: finite syntactic program.** The source program and compiler expansion
give a finite list of public ports, private lifetime tags and operation
sites. Public inputs are arbitrary. Each private lifetime has one INIT,
only in-lifetime uses, and one last CLEAR; a recursive call can designate
any live actual field, including a parent's private center, as its input.
Within one primitive, declared distinct ports are distinct. No operation
clears a public port. Every call has an explicit destination and a finite
continuation. These are finite name/liveness/call-interface properties,
not a promise about recursive execution. A structural compiler proof may
establish S without materializing the expanded template. Safe alpha-renaming
uses (compiled unit occurrence, local lifetime occurrence), so an old label
reused after CLEAR gets a new static tag. It never credits a private tag as
a productive input.

**P: nonrecursive primitive realization.** Each nonrecursive native,
movement, arithmetic, base-case and formatting macro has a fixed finite
multitape implementation for the numerical parameter domain in question.
It has its stated virtual input/output meaning, time tariff and at most
c_T V active or visited virtual cells when used at a node of logical
volume V, including counters, descriptors, scratch, and visited blank
cells. One may instead use a finite sum of such bounds, since T is fixed.
This premise concerns isolated macro implementations. It does not give a
macro access to an ancestor, provide a callee-owned allocator, or assume
that a recursively invoked copy of T returns or clears its work.

The existence and numerical accuracy of these macros are the part retained
under native_all_columns and precision_tape. Absolute-origin code is
allowed: Section 3 derives confinement by simulation rather than requiring
it as another hypothesis. A mere algebraic native identity would not
establish P. Nor would a time bound with no storage/high-water bound.

**G: complete-row geometry and decreasing calls.** After one root padding,
each productive role of a node is a complete field of volume V/W. Its
compact-control and spectator ranges are complete, its row count is
divisible by the remaining power of W, and its record precision p is the
same global p. A paid recursive call acts on one such field and has
strictly smaller kernel parameter floor(e/m). A finite elementary remainder
is handled by the macros in P. Descriptors and headers have at most c_T V
cells, including at leaves. These are the retained compiler/layout and
precision size statements, not an owned-child postcondition.

Then there exists a single fixed finite multitape machine executing every
well-formed runtime invocation of T such that:

1. Every recursive call receives the exact encoded rounded input field
   supplied by its caller, independently of whether that field is public,
   dirty, correlated with another field, or a live parent center.
2. The caller's inaccessible suspended contents and continuation are
   physically preserved. After a child returns, its whole public output
   is installed in the caller's designated actual field. All other caller
   fields keep their suspended contents until the caller's next operation.
3. Each CLEAR erases only its current invocation's private lifetime. At a
   completed return, all child-private work and continuation symbols are
   erased; all bridges are empty. No stale private payload is supplied to
   a later INIT, and no public dirty helper is used as free zero storage.
4. The extra administrative time is at most

       C_T sum_{executed nodes v} V_v.

   The physical live and visited-high-water space is at most

       K_initial + C_T V_root/(1-1/W).

   K_initial records pre-existing visited backing, if that quantity is
   part of the machine model. Blank erasure is not physical deallocation.
5. The productive width, paid rank profile and mathematical program are
   unchanged. Extra private storage, routes, copies, resets, descriptor
   operations and return scans enter fresh finite ordinary/storage
   constants. No new productive credit or free recursive request is used.

This implication discharges physical allocation, suspension, ownership and
erasure if S, P and G are established from the actual selected source and
the *non-ownership parts* of the other four retained assumptions. If a
source binding establishes them only by quoting a completed-child owned
contract, that binding is circular and the implication does not discharge
the named assumption. Sections 8 and 9 make the remaining binding work
explicit.

## 2. Static allocation is finite and safe

Enumerate the finitely many private lifetime occurrences of T. Give each
one a distinct logical bank. Likewise give the finitely many primitive
scratch/counter/descriptor ports their declared distinct logical ports.
The sets are disjoint from the productive/public ports. A local label used
twice after a CLEAR is compiled to two different tags. This is the safe
allocation; its size can exceed both the peak-live count and the number of
reused source labels.

The source liveness check means that a lifetime cannot be read before INIT,
read after CLEAR, or clear a public field. The compiler's occurrence-tagged
substitution maps every local operation, including every nested source
operand and destination, through the same injective name map. Therefore
there is no capture. This conclusion is structural and does not assert
anything about machine execution or numerical accuracy.

One may instead retain one bank per static owned label when the same
finite liveness check proves that its successive lifetimes do not
overlap and every reuse follows CLEAR. That implementation merely
identifies nonoverlapping fresh tags; the proof below still applies.
Neither version identifies banks belonging to simultaneously suspended
unit occurrences. Consequently occurrence-tagged allocation can keep
the source's within-unit label reuse without assuming a global peak
allocator.

The safe allocation is paid in the full private inventory O and ordinary
constants. Its private fields are not counted in W. The present argument
does not need or claim an improved peak allocator. In particular, the
existing lockstep completion proof already provides a more economical
logical allocator; it is not being reproved as a new result here.

For current P104-style examples, separate LOCAL occurrences receive
separate bank tags even when their words use the same raw integer label.
All 31 local lifetimes of the 25,984-event word must be checked; using
only its peak 13 or allocated-label count 29 as a lifetime census would
be incorrect. At the raw 18-LOCAL/15-query caller level, the simple
per-lifetime upper count is 18*31+15*104=2,118. The actual finite source
binding can instead use 18*29+104=626 private banks, reusing the 104
query banks across the 15 completed, sequential query contexts and
retaining typed reuse within each LOCAL. These are two different safe
allocations, not two counts of the same storage. Neither is the expanded
compiler's final O, and no final O is inferred from either raw number.

## 3. A fixed-tape primitive can be confined to its current segment

This elementary simulation removes an otherwise dangerous hidden premise.
Take any one of the finitely many finite-tape macro machines in P. Encode
each virtual alphabet symbol, including its virtual BLANK and LEFT/RIGHT
markers, by a fixed-length nonblank binary code. Use a distinct physical
delimiter and physical blank outside the encoded extent. Thus an internal
virtual blank never terminates an extent scan. All reserved symbols such
as UNIT and MARK are ordinary encoded virtual symbols. The selected
query machine's seven-symbol alphabet is included without identifying its
virtual BLANK with physical unallocated space.

For a two-way virtual tape use two one-sided encoded tapes, one for
nonnegative coordinates and one for negative coordinates in reverse
order. Finite control records which half contains the virtual head. A
move across virtual zero switches halves at their local origins; neither
half moves left across its physical delimiter. An absent encoded block
is interpreted as a virtual blank and, when visited, is written as its
nonblank code. It is harmless to retain such coded blank blocks until
the invocation ends. Track alphabets or a fixed-length binary code give
the same constant-factor construction.

Reading/writing one virtual symbol or moving one virtual cell takes at
most a fixed number of physical reads/writes/unit moves. The transition
table and the symbol-code width are fixed with T. Relative origin tests,
virtual markers and virtual blank tests are exact. The simulator does
not inspect a physical coordinate, an ancestor marker, a host dictionary,
or a host stack. It cannot cross the current delimiter by construction.
Its encoded visited extent is at most a constant times the macro's
virtual visited extent plus a fixed number of delimiters. Consequently
P's time and space tariffs survive up to new finite constants.

Apply this translation to **all** primitive ports, not only public data:
scalar scratch, compact-movement work, private-query counters, dimension
descriptors, output temporaries and normalizer work are included. Source
Python objects, absolute dictionary indices and audit observers are not
machine inputs. If a claimed retained implementation cannot be represented
by the finite transition-table premise P, this simulation does not repair
that separate native/movement gap.

We may wrap each macro with origin normalization at its finite public
boundary. Scanning its current coded extent to its local origin costs
O(V) under P and restores a standard port-head convention. Alternatively
the continuation codec can save actual head offsets; either construction
has the same asymptotic bill. No scan reaches an ancestor prefix.

## 4. Fixed tape resources and physical continuation

Choose a fixed multitape realization of all nonrecursive routines,
including the finite row router and descriptor arithmetic described
below. Let q be its number of virtual payload/work ports. After the
two-sided translation, use k=2q physical segment tapes. The continuation
controller needs three further tapes: control stack, active descriptor,
and descriptor-reversal scratch. A return bridge uses b fixed encoded
stream tapes, where b is the fixed number of external stream components
in the chosen public ABI (one concatenated bridge is also possible).
Let r be the fixed number of elementary transfer/shape-counter tapes if
they are not already counted among q. The inventory is exactly

       k + 3 + b + r = 2q + 3 + b + r,

with all q,b,r chosen before input width varies. There are no tapes indexed
by runtime depth. This formula is an inventory, not a claim of a minimal
tape count. Every one of its tapes is covered either by current segments,
the continuation stack, or a bridge/scratch emptiness invariant.

The general-k version of the retained segment continuation routine has
frame grammar

       [ descriptor : b_0 u^H_0 ; ... ; b_(k-1) u^H_(k-1) ; ]

where H_i is the unscanned part of the current coded segment. Its loops
over k and its role mask are finite control because k is fixed. The
published k=16 proof generalizes by exactly those fixed finite loops.
Its push+pop action bound is

       24d + 12H + 32k + 64 + 8U,

where d is the saved descriptor length, H=sum H_i, and U is the total
child coded payload/descriptor extent erased at pop. The proof preserves
the actual parent words and physical head positions and does not scan
older stack frames or ancestor payload. It charges failed terminal tests,
delimiter writes, rewinds and erasure. The bound does not include child
execution or useful output delivery; those are charged in Section 5.

The descriptor contains the finite return PC, current dynamic dimensions
and needed source/destination selectors. A finite template with L sites
uses at most ceil(log2(max(2,L))) bits for its return PC. On pop, a fixed
finite automaton decodes it and jumps to the corresponding finite control
state. No host recursion stack is used. Dynamic integers such as e and
the row/record counts live as coded tape words. Division by the fixed m
or W uses ordinary finite-state long division, with linear bit cost;
global p and the remaining shape parameters are copied, not recomputed
from an ancestor's payload. All descriptor and arithmetic work belongs
to the stated d and r/q inventories.

## 5. Complete-row routing and the two bridge transfers

First establish a routine omitted by an abstract stack-only argument.
For fixed W, a contiguous stream of complete rows can be split by
u=Wg+w into W output streams and merged in the inverse order in time
C_W(V+descriptor size). The finite controller cycles w through
0,...,W-1. A tape guide of the declared complete-row length controls the
bitwise transfer of one row; rewinding that guide costs at most the row
length again. A binary-to-unary guide of length L is produced in O(L)
amortized actions using a low-bit-first decrement counter: total carry
distance over L decrements is O(L). Initial bit-length setup is absorbed.
The row length is at most the current volume and all guides are cleared
before recursion. Whole rows include the compact-control, spectator and
record suffix coordinates. No compact-field bit is used as the row
selector. Empty ranges and the finite small-size cases use explicit
finite branches.

The inverse merge takes rows in the same fixed cyclic order, thereby
restoring the caller's original record order. This is a sequential
copying/router routine, not a unit-cost random-access gather. It works on
arbitrary encoded payload symbols. The one root padding supplies the
divisibility needed at every descendant, so descendants do not re-pad or
change the global precision.

At a paid call, perform this actual protocol:

1. While the parent segments are active, copy the designated complete
   input field, including every rounded bit, into the empty bridge.
   Save/canonicalize affected parent heads. Put the return PC and parent
   dimensions in the active parent descriptor. Stage the child descriptor
   alongside the bridge input; do not overwrite the parent descriptor
   with child parameters before it is pushed.
2. Push the parent continuation, installing fresh child delimiters on
   every segment tape. Install the bridge input into the child's public
   input representation, using the row router where required. Initialize
   child private formats and install the staged child descriptor into
   the now-empty active descriptor segment. Erase the bridge and transfer
   work.
3. Execute the recursively dispatched child. The bridge is empty on
   entry, so any deeper call may use the very same finite bridge bank.
4. At the child's complete return boundary, serialize its **entire public
   output**, including all helper/output components and their current
   rounded bits, into the bridge. Public components promised to be
   restored algebraically are still copied; their numerical residuals
   are not silently discarded.
5. Pop the child continuation. This erases all its remaining private,
   public-copy, counter, descriptor and scratch bodies and restores the
   parent's actual suspended words, heads and PC. The result is safe
   outside those erased bodies in the bridge.
6. Install the bridge result into exactly the designated parent field,
   in the inverse row order, erase the bridge/transfer work, and resume
   the parent PC.

Only steps 2--3 execute a child with its own current private slots. Its
CLEAR instructions cannot address an ancestor slot: every port maps to
the child segment and its virtual origin, even if the input value was
copied from a parent's owned center. A child cannot clear the global
bridge because its segment translator does not expose those physical
tapes as primitive ports. The dispatcher's own bridge actions are fixed
administrative routines.

The apparent global-bridge conflict is absent. During step 3 the caller's
bridge input has already been installed and the bridge erased. After
step 4 there are no recursive calls before step 6 erases that result.
Thus bridge occupancy intervals never overlap between runtime depths.
Each transfer scans only the current node or its child, never an older
ancestor. Its time is O(V_parent), and its size is O(V_child) plus current
descriptors; using the weaker O(V_parent) bound is sufficient.

This protocol changes the convenient stack ABI “deliver outputs before
pop” into a realizable operation. Keeping the output only on child
payload tapes and then popping would erase it. Installing it into a
parent tape before that parent becomes active would instead violate the
confinement proof. The bridge is the explicitly paid solution to both.

## 6. INIT, COPY, CLEAR and the noncircular induction

INIT writes the prescribed zero field in its fresh private lifetime
segment and records the active format; its cost is linear in that
complete field. CLEAR scans and erases that private field's whole coded
extent, including coded virtual blanks and residual data. It cannot
target a public field by S. It does not imply that previously visited
physical cells cease to count as backing storage.

Distinguish two meanings of copy. Administrative serialization is a
bitwise copy of the *actual* rounded state. The mathematical COPY opcode
in the native word is implemented by the retained arithmetic ADD into
the ideally zero owned destination. If MOVE or earlier numerical work
has left a residual in that destination, ADD retains it. No exact-value
overwrite is substituted to erase error merely because the ideal
destination is zero. New exact initialization happens only at a fresh
INIT; all earlier lifetime uses have ended. Additional numerical errors
of arithmetic remain subject to precision_tape, unchanged in kind.

Now induct on the positive kernel parameter e (or equivalently the
well-founded runtime call tree). In the elementary case P supplies the
nonrecursive virtual computation; Section 3 provides a confined physical
realization, and the source's finite liveness/cleanup sequence plus the
dispatcher erase all current private segments on return.

For the induction step, nonrecursive macros before the first call act
only in current segments by simulation. At a call the first two bridge
steps establish a well-formed child input with empty private work and
empty bridge. Its kernel parameter is strictly smaller by G. The
induction hypothesis, not a retained completed-child ownership premise,
therefore supplies its completed output and confined cleared return.
Steps 4--6 restore the exact caller context and install that output.
Proceed through the finite instruction sequence. The same argument
applies to arbitrarily dirty public helpers, overlapping *values* and
suspended centers because it uses address/tag separation rather than
probabilistic independence or zero payload assumptions.

At the end, source CLEARs have completed each intended lifetime. The
dispatcher additionally erases every remaining child work/format field
after serializing the public result. This extra erasure cannot affect
the returned output, an ancestor, or future work because those addresses
are disjoint. The return postcondition follows. The finite machine is a
dispatcher with a serialized PC, not a recursively executing host
function; the induction is a proof about its execution.

## 7. Time, storage and changed constants

At a current node let its logical volume be V_j=V_root/W^j along an
active recursion path. P and G bound the total coded current payload,
visited extent, descriptor, marker overhead and local temporary work by
C_T V_j. Markers and finite PCs are included because V_j>=1. The row
guides, reset scans, source/return serialization, origin normalization,
and push/pop therefore cost C'_T V_j per call boundary or local
administrative event. There are only finitely many such events in T,
so enlarging the constant gives C''_T V_j per invocation. Summing over
all executed nodes gives the theorem's time bill. It is *not* merely a
sum over the active path and does not hide a parent-volume scan inside
each descendant's local cost.

For space, each physical payload tape consists of consecutive suspended
ancestor segments followed by its current segment. A later sibling
reuses the erased suffix. Its visited high-water length is at most its
initial backing plus the maximum, over active paths, of the sum of the
current segment bounds. The control stack has the same geometric bound;
descriptor-reversal scratch is at most the current frame size. Bridge
and transfer work are at most a constant times the current parent's
volume. Thus, after summing the fixed tape inventory,

       space <= K_initial + C_T sum_(j>=0) V_root/W^j
             = K_initial + C_T V_root/(1-1/W).

The finite stopping depth and positive integral volumes only shorten this
series. Previously visited blank backing is included in the high-water
argument; it is never charged once per historical invocation. Nothing
uses a new tape per depth or adds a root-volume buffer at every depth.

The normalized runtime recurrence changes only by an additional constant:

       F(e) <= (s/W) F(floor(e/m)) + old_nonchild(e) + C_T.

The retained nonchild allowance already includes a positive O(1) term.
This raises its finite coefficient and leaves its exponents unchanged.
All representation operations are exact bit manipulations, so they do
not add arithmetic coefficient growth; more private formats and work
cells do change storage/precision setup constants.

In particular, **do not reuse the raw constant 10^9 as a bound for this
expanded dispatcher.** Let O_T, R_T, G_T and C_T be freshly counted or
overestimated finite private-bank, route/ordinary, growth/format and
machine constants for the fixed expanded instance. Safe allocation may
make them enormous. The retained precision/outer argument may absorb
them only by increasing its eventual input-size threshold using its
strict exponent margins. This does not prove that a previously chosen
small carrier N already absorbs them, nor that an old finite admission
receipt is numerically unchanged. The mathematical paid profile and
asymptotic kappa are unchanged if that eventual-threshold substitution
is valid under the remaining assumptions.

## 8. Exact source obligations for a complete discharge

The physical proof above has no premise that a child already satisfies
owned erasure. Nevertheless its application must establish these
specific finite/retained facts, not merely declare the source compatible:

* The actual current P104 INIT/COPY/CLEAR stream and caller give S for
  every owned lifetime, all 18 LOCALs and all query contexts. Label
  reuse is renamed per lifetime. No public helper is cleared or credited
  as initialized storage. Actual source operands, not just a histogram,
  pass through the name map.
* Product, completion, splitting, residual/exit programs and uniform
  compiler substitution preserve that syntax using occurrence-tagged
  fresh names. The old logical allocator's statement “the unit clears
  its bank” cannot stand in for this physical proof.
* The nonrecursive implementations used under native_all_columns and
  precision_tape satisfy P as finite machines with the stated active
  and visited-cell bounds. Their algebraic all-column correctness alone
  is insufficient. If their only available theorem assumes recursive
  owned storage, extract the nonrecursive result rather than citing
  that circular aggregate theorem.
* The final compiler has W=B_N>=2, decreasing calls, complete rows and
  one global precision parameter. Physical layouts, input/output field
  formats and shape lengths match the router. The seven-symbol query
  ABI is encoded on every port, including held W/M/T counters; it is
  not silently treated as a binary source program.
* The eventual precision/storage argument permits the new finite
  constants and full visited-high-water count. It must not use the old
  raw 10^9 envelope or count only peak private banks while actually
  running the safe allocation.

The first two are candidates for new actual-source evidence. The third,
fourth and fifth are the precise non-ownership pieces needed from the
other retained assumptions. Exposing them makes the implication
falsifiable; adding “the child returns owned work correctly” to any of
them would make the argument circular.

## 9. Relation to existing results and present status

This proof intentionally reuses rather than claims novelty for:

* `research/lockstep-completion-pass/PROOF.md`, Lemma B: finite logical
  safe allocation and a stronger logical LIFO peak formula.
* `research/segment-continuation-stack/PROOF.md`: the delimited local
  push/pop mechanism, exact action invoice, arbitrary nesting proof and
  treatment of visited blank cells. Its stated source/caller limits
  include output delivery and full source lifetime compilation.
* `research/selected-owned-query-private-stream/PROOF.md`: literal
  fixed-port query prep/resume tables and linear copy/add/erase bills,
  whose global slot supply is an entry premise there.
* `notes/batched-complex-rows.tex`: complete-row padding/splitting,
  exact V/W volume, common global precision and spectator geometry.
* `research/final4610-independent-admission/SPECIALIZATION.md`, Section 6:
  fresh constants for the expanded finite template and eventual
  threshold substitution; no reuse of a raw 10^9 bound.

The new proposed bridge is the complete combination: static source
fresh-name allocation, confinement derived for every physical port,
explicit input/output bridge transfer, serialized finite PC and a
well-founded ownership proof for the actual recursive dispatcher. A
finite codec prototype can corroborate those interfaces but cannot by
itself prove the universal statement.

**Current status:** proof draft of the generic physical lowering, with
the incomplete actual-source bindings detailed in BINDING-STATUS.md. It supports a
whole-assumption removal only once those bindings are supplied without
using owned_erasure itself. Until then it is a concrete conditional
bridge theorem, not a justified claim that the repository has moved
from five retained assumptions to four.
