# Literal division at the actual current CRT leaf call

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Base: `e54523517d0f03e58352e647c403a5af3e525a57`.
No new kappa; no whole numerical producer, compiler, or multiplication claim.

## 1. Exact source obligation and retained premises

The source operation is `Unsigned.divmod` in the exact `words.py` Git blob
`8d4ba37e2778acb35b34e0719df2caf138fbeb50` (SHA256
`5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9`).
Its actual caller is `encoded-current-crt/producer.py`, blob
`a327b0161eca57a1cc44ec2aa8e3defed2167ddc`, merged in
[CrocSwap/integer-mult-bounds#5053](https://github.com/CrocSwap/integer-mult-bounds/pull/5053).
The current entry and mixed-row interfaces come from
[#5219](https://github.com/CrocSwap/integer-mult-bounds/pull/5219) and
[#5353](https://github.com/CrocSwap/integer-mult-bounds/pull/5353).
The live encoded frontend/leaf path is pinned through
[#7352](https://github.com/CrocSwap/integer-mult-bounds/pull/7352) and
[#7388](https://github.com/CrocSwap/integer-mult-bounds/pull/7388).
The unchanged header/key program is CubeJerry commit
`4c7cee36538bb48dc2598806af2ca42554fa63c0`, bundled under `inputs/headers`.
The older full binary refinement of the PR5105 fixed program is not a
refinement of this current Word/context grammar. Division arithmetic and
generic finite composition are prior results. The contribution is the
literal current-Word implementation with dynamic-owner binding and a
replacement for the old allocation-event coupling.

We retain current numerical admission, encoded source/guide construction,
persistent bank, lease/commit, other arithmetic, header/key/radix providers,
and their machine models. The binder's finite64-slot metadata control and
grant service remain external and separately charged. The whole producer,
its Euclidean loop and the source dispatcher have not been lowered here.

**Primitive theorem.** Let P>=4. Four distinct numerical roles N,D,Q,R have
the actual Word ABI: LEFT at0, head at1, P binary digits followed by RIGHT
for N,D; Q,R have LEFT at0 and blank inactive owned cells1..P+1. The active
frames and all supplied owners are disjoint. Suppose 0<=N<2^P and
0<D<2^(P-1). Give four distinct inactive owned selector windows of eight
backed cells, with heads at their first cells, disjoint from all64 numerical
roles. ACQUIRE, four fixed setter entries and DIVIDE return
Q=floor(N/D), R=N mod D, incoming N/D and every numerical role except Q/R
unchanged (in particular, all preexisting live data is preserved), every
numerical head at its entry position, and all selectors blank at their
origins. Rebinding the same roles and entering RETIRE blanks every Q/R body
and right delimiter and returns all heads, preserving their LEFT guards
and all exterior data. Total literal lifecycle cost is <=2^14(P+2)^2.

Incoming live inputs may be arbitrarily correlated. Inactive Q/R bodies
are blank as supplied by the current Arena; this is not borrowed-dirty
erasure. Malformed entries may stop after partial work. Rejection cleanup
or failure head return is not claimed.

**Actual-call theorem.** In every admitted current one-left/one-right leaf,
replace its sixth raw divmod by this graph and the explicit binder below.
A weak owner-renaming simulation preserves all live numerical values and
the exact old source continuation, including offset/updated-coordinate
streams, retained source/payload semantics and terminal ownership. All
arithmetic at this replaced call is literal. Metadata binding remains a
finite-source premise; it invokes no hidden division and decodes no P,N,D.

## 2. The actual sixth call and its margin

NodeEntry copies the selected two half-groups, appends their width marks
to the guide and invokes Entry. If the encoded half has one mark, each
group has one axis. Let widths be u,h and moduli s,t. The actual guide has
P=u+h+1 marks. Source admission gives s,t>1 and coprime; their binary
fields imply s<2^u and t<2^h<=2^(P-2), hence the required high-bit reserve.
Invalid/padded coordinates do not change this modulus margin.

The first five raw calls are (1) remainder(1,s), giving base1; (2) the
single Euclidean division s divmod1 in inverse(1,s); (3) its qmod=s mod s;
(4) local=0 mod s; and (5) digit=left_value mod s. The inverse terminates
after that one iteration because the next remainder is zero. Modular
add/multiply and exact product perform no further raw divisions. Following
the left update prefix=s, including the padded-coordinate branch. The next
call is therefore s divmod t at the first right remainder. Its operands
are distinct live source Words. This proves the call identity for every
admitted leaf, beyond the bounded fixtures.

The binder reads the actual current half: read ONE, move right, test RIGHT,
rewind. This costs eight native actions and returns the head. A seven-state
phase counter0..6 is enabled for that producer invocation; its sixth raw
call runs the graph, after which phase6 is saturated. Other raw calls and
nonleaf invocations retain the original implementation. The same wrapper
applies to the forward producer and pinned one-line inverse specialization.
The bounded current caller visits two such leaves per leg. No slot tuple
is hardwired from a trace.

## 3. Physical roles, selectors, grants and binding

The64 numerical roles are the Entry's eight borrowed dirty ports0..7 and
56 owned bank Word ports8..63. They are not the entire63-port Bank; template,
guide, padded streams and output have other retained roles. HostedWord's
cells/head are properties of its actual backing Port. NumericPort delegates
to that same HostedWord, without replacing backing or resetting a head.

A selector is LEFT, six low-to-high slot bits, RIGHT, with head at LEFT.
All256 setter entries are fixed parts of the graph, each costing31 literal
instructions. Every logical numerical read/write/move is expanded offline
into a six-level literal decision tree. It checks LEFT, reads/moves over
six bits, checks RIGHT, makes seven paid left moves, and executes the
operation at the fixed physical port named by that leaf. Read branches
target kernel continuations; write/move have a paid return jump. Numerical
reads cost30 instructions and writes/moves31. There is no runtime indexed
tape instruction or host-selected arithmetic operation.

Descriptors reuse the actual caller's first four of14 private marker
owners, acquired before numerical production and unused until headers/keys
are built. The old one-cell grant does not imply eight-cell capacity. The
changed caller explicitly requests eight backed cells per descriptor:
seven additional cells on each fresh owner,28 total. Its external grant
cost A_grant is a separate vector entry. ACQUIRE physically writes all32
cells blank and returns all heads in89 instructions. For reuse, required
capacity is max(old grant,8); exterior data is untouched. GrantedSelector
enforces the eight-cell window even when the underlying Tape can grow.
No growable-tape behavior supplies a missing grant. The same owners return
blank before unchanged header/key control, retaining their larger history.

The binder validates fixed slot/arena identities, complete live/free
partition, two free roles, protected0..7, and the exact N/D object bindings.
It pops two free roles and marks them live without externally zeroing:
DIVIDE physically validates/initializes their bodies. Head1 for all Words
is inherited from the source boundary; selected heads are also checked by
the graph's one-step LEFT-guard access. No unbounded head coordinate or
numerical value is read by metadata control.

The declared finite-control tariff is separate from literal-bit cost:
256 units for four-grant binding;32 per producer boundary;16 per raw call's
phase dispatch;16384 per replaced call for inventory validation, reservation,
setter choice and return metadata. These are conservative bounded64-slot
source-control invoices. A64-bit live bitmap,64-entry six-bit free stack,
and64-cell seen bitmap suffice: initializing costs64 cell operations;
checking free entries uses fewer than8*64 bounded operations; partition
and identity checks fewer than12*64; pops and setter choices fewer than256.
Even a fourfold allowance is below16384. This uses bounded metadata
operations as units, not a newly proved physical bit tariff. Lowering their
representation and allocation remains outside scope. For I invocations,
R raw calls and J replacements the invoice is
C_bind=256+32I+16R+16384J, plus A_grant.

## 4. Arithmetic invariant and complete return

DIVIDE checks pairwise inequality of the four descriptors. It scans N/D
in lockstep, enforcing >=4 digits with a fixed prefix state, binary input,
equal RIGHT positions, nonzero D and a zero high bit. It checks then writes
every Q/R cell zero, explicitly writes their RIGHTs, and places N/Q at
their high digits and D/R at their low digits.

After k input digits let v_k be the high-to-low prefix. The invariant is
v_k=D*q_k+r_k with 0<=r_k<D; the written quotient prefix is q_k. For the
next bit b, an in-place forward shift writes2r_k+b. Since2r_k+b<2D<2^P,
its final carry is zero. A low-to-high comparison remembers the latest
different digit pair, hence compares complete unsigned values. If shifted
R>=D, exact subtraction has final borrow zero and writes quotient bit1;
otherwise the bit is0. The invariant follows for the next prefix. After
P digits, Q=floor(N/D) and R=N mod D.

D/R return physically to their LEFT guards and then one cell right after
each sweep. N/Q move left once per digit and terminate at LEFT, then move
right once. There are no N/D writes. Each numerical access names only its
decoded fixed physical role and returns the selector head before the
operation. Final cleanup writes every selector cell including both guards
and returns to its first cell, without exterior access. RETIRE erases Q/R
digits and RIGHTs, scans back to unchanged LEFT and returns to cell1,
then erases the rebound selectors. All other data/heads are preserved.

## 5. Replacing allocation-event coupling by weak simulation

Old divmod allocates a scan copy, Q, R, shifts and subtraction temporaries.
The new program reserves only Q,R and changes R in place. Identical
allocation events and equal output slot numbers are generally false.

At a structured primitive boundary relate the contexts by a bijection pi
on slots0..63, fixing protected0..7 and preserving externally live Word
references, values and heads. Ordered available stacks correspond by
position; live membership corresponds; free bodies and retained inactive
tails are blank. The zero template is fixed separately. Use identity at
the changed call's entry. At return fix every incoming live slot, map old
Q to new Q and old R to new R, then pair the available stacks in order.
This is a full bijection: both leave exactly two distinct additional live
outputs and every other entry-free role blank/free; neither touches live
inputs. The arithmetic theorem gives output equality. This is a relation
between executions, not a physical tape permutation.

Complete relevant identity-use audit: Arena.zero selects the free-stack
top and tests live membership; copy checks arena identity; free checks
arena/live and appends its slot; free_many preserves explicit argument
order. Word.slot occurs in these operations, producer protected/keep sets
and words[slot]. Arithmetic never branches on slot magnitude. Compare has
an object-identity shortcut, and add/subtract avoid moving an aliased
operand twice; bijections preserve these tests. Carry/borrow, comparison,
zero and high-bit tests depend only on related digits. Each subsequent
ordered primitive therefore preserves the relation, as do fixed-capacity
failure conditions. New peak ownership at the changed call is no greater:
two outputs replace an old algorithm simultaneously holding at least
scan/Q/R. Corresponding live cardinalities agree outside the replacement.

The final producer cleanup iterates tuple(arena.live), whose order need not
be preserved by pi. Here simulation is deliberately weak. Non-kept words
are erased on disjoint owners; their clears commute on values and final
heads. Both leave related protected/returned live objects and equally
sized free sets. Re-pair the actual resulting free stacks in order while
fixing live objects. The relation is restored after this block.
Arena.rollback has a similar unordered loop but is not called on the
successful producer path. This argument does not extend malformed-core
failure cleanup. All success-path admission and capacity tests remain
valid in related source states. Output serialization reads related digits,
so the exact offset/coordinate streams agree.

Entry.consume frees the related returned lower/product. Entry.close tests
that exactly0..7 remain live and retires the56 owned physical Words. This
terminal condition is invariant because pi fixes0..7. No numerical result
survives to observe changed free-stack order. This establishes the exact
source continuation and terminal owner semantics.

## 6. History is charged on actual physical owners

A proof permutation never moves old physical capacity. For each actual
Word role t retain its own history H_t. The graph accesses only positions
0..P+1. Entry already prepares all56 owned Word frames at current P, and
the frontend prepares all eight dirty guards at that guide. Numerical
history is thus bounded by sum_t max(H_t,P+2), not a relabelled old profile.
Across contexts use their maximum P; larger earlier tails stay blank and
are retained. Actual checks include reused larger bank frames.

Each descriptor's history is max(its prior history,8,its later unchanged
header/key extent). The same four owners serve all replacements; no role
is allocated per digit or per raw call. Other header/key histories remain
their physical predecessor histories. The bounded caller retains100
distinct symbol owners per leg and200 across its separately acquired
forward/inverse legs. The new grants affect sizes, not this owner count.
Receipts report complete final retained-cell totals, and keep A_grant and
growth separate. No per-role stock profile is transferred by permutation.

## 7. Universal bill and complete same-workload cost vector

Let c=popcount(floor(N/D)). Count each logical R,W,M,J,H before numerical
dispatch as one kernel instruction. Each descriptor inequality costs51,
so all six cost306. Initialization costs17P+27. Per input digit, shift
costs7P+5, comparison11P+9 and input/quotient control5. Each quotient1 adds
12P+9 for subtraction. Final test/returns/selector erase cost125. Hence

L_div=18P^2+36P+458+(12P+9)c <=30P^2+45P+458.

Every expanded logical instruction costs <=31 physical instructions.
ACQUIRE costs89; four setters124; logical RETIRE costs14P+131. Including
ACQUIRE, descriptor setters, DIVIDE, descriptor setters again and full
output retirement, with external metadata C_bind still charged separately:

T<=337+31(30P^2+59P+589)<2^14(P+2)^2, for P>=4.

This pays every descriptor read, numerical initialization, source-digit
access, move, return and erase. No P-size extra scratch Word is needed.
The numerical frames are supplied by the existing actual allocator;
their acquisition/preparation remains counted in the retained source bill.

The actual caller consumes Q/R through the original continuation and
Arena.free, and does not redundantly execute RETIRE. Its complete cost
vector has unchanged header/key literal instructions; new divider literal
instructions (one ACQUIRE per binding lifetime, setters/DIVIDE per replaced
leaf); retained radix bit instructions; retained payload actions; retained
native source actions; residual marker actions; C_bind; and A_grant.
The eight native actions per boundary query stay in the source bill.

HostedWord inherits Word.read/write/step: these increment arena.meter and
access backing cells/head properties directly. They do not increment the
backing Port meter. The caller sums arena and source/backing-port meters,
so new numerical actions appear exactly once in its raw source total.
Subtract exactly the graph's numeric-action count from that total, plus
the unchanged header graph's separately counted native actions. Descriptor
wrappers call marker Tape methods, so their actions appear once in the
old outer-adapter total; subtract exactly that count there. The literal
instruction bill then includes both classes once, together with all
branches/jumps. Grant and metadata units remain separate. Both unchanged
B9 and changed same-workload vectors are retained in receipts. A common
bit tariff or speedup is not inferred by adding unlike units.

## 8. Evidence and residual obligations

test_core.py checks124 exact-integer cases: every4-bit numerator and
admissible positive divisor, plus seeded widths5,9,17,33, changing slots
and257-cell old histories. It checks the exact logical count, full
lifecycle bill, all incoming bytes/heads, descriptor exteriors and full
output erase. Alias, zero divisor, high margin, malformed digit and absent
grant controls reject. Returning wrong quotient, corrupted live input and
stale well-formed descriptor controls show why successful halt and clean
heads alone are inadequate. Finite checks support, not replace, the proof.

test_join.py executes six actual source/payload roundtrips with distinct
left moduli and valid/padded coordinates. Each of24 replaced calls also
runs the original divmod on a separate observational clone of the entry
state; the checker constructs the full64-slot relation, checks incoming
backing/head identities, and audits the exact arena/Port meter split.
Six incoming free-stack fingerprints occur. The unchanged B9 caller runs
separately on the same fixtures, with identical forward source/payload
bytes. The inverse restores source, payload and physical-position keys.
Clones and observations never select the actual graph's work.

The universal theorem concerns the emitted R/W/M/J/H graph. Program's
receipt/history arrays, Binding's observation counters and optional observer
are verification instrumentation, not extra physical transcript owners.
The Python replay's20,000,000-instruction watchdog can stop a larger admitted
fixture; that verifier bound is not a stopping rule of the emitted machine
or the source-bound graph substitution theorem.

Remaining: other numerical primitives and loops, native data admission,
actual grant/acquisition services, finite-slot binder lowering and complete
source/radix orchestration. The fixed13-bit record code/arbitrary12-bit
opaque payload ABI is inherited. This removes one actual arithmetic macro
obligation and proves its owner interface, while retaining all five full
foundational assumptions and the selected kappa.
