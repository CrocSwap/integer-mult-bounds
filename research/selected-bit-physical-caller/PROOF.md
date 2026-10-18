# A fixed-tape lowering of the selected BIT caller

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I give a constructive source-level lowering of the p=1 caller in David Arias's
[PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753), at
`7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`. I retain his endpoint, stock,
root-coupling and local-cost hypotheses. I replace depth-dependent logical tape
objects by permanent roles and a sequential parking stack. I use the numerical
codec from my [PR2769](https://github.com/CrocSwap/integer-mult-bounds/pull/2769),
at `d97f150d89e3f3eebdf625a468a445c9c0f1e6c9`, and ywz65's two-tape controller
from [PR2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635), at
`1662dda699d9ea57b3fb13a23873b087d765149f`.

I implement the finite macroprogram and its dispatch loop, both checkpoint
codecs, the actual numerical Frame substitution and the residual return cursor.
I execute complete reduced-source programs through the fixed-role controller.
I do not materialize the selected GL64 word or supply one fully expanded
microtransition table. Readers must assess the source-level compilation argument
separately from the finite checks. Section 9 binds the implemented controller to
the construction below.

## 1. Statement and retained hypotheses

Fix the source-admissible prime q and the selected source vocabulary. Use the
complete input domain of PR2753, PROOF sections 1, 5 and 6: compatible fresh-row
stock, canonical programs and directories, minimal root word widths and the
specified root coupling. In particular the internal node has

\[
V=C R B G S A^{2n},\quad A=q^w,\quad R=WNHU,\quad W=28416,
\quad N=|GL_{64}(\mathbb F_q)|.
\]

**Claim.** One can compile this caller to a multitape machine with a number of
tapes depending only on q and the pinned source. The machine computes the same
complete Boolean endpoint and preserves the same physical row/prefix ordinals.
It uses \(O_q(V_{\rm root})+F_q\) cells and preserves the baseline local toll
\(O_q(V(n+w))\). It uses no numerical-width, precision, tape-length or recursion-
depth value in finite control. Here \(F_q\) covers one-time source compilation.

This claim concerns the p=1 baseline. I retain the stronger H2 route/leaf
contracts, the outer borrowing wrapper and the complex supplier as separate
obligations. I claim neither the historical sharp parking constant nor a new
multiplication exponent. I leave the selected result unchanged.

The proof uses successful, well-bracketed execution on admitted inputs. A
caller may reject malformed input. The claim does not require transactional
recovery from interruption halfway through a parking-table command.

## 2. Three kinds of state

The source stores numerical values in fixed-width Word slots, arbitrary
cardinalities and sequential records on Tape objects, and source labels in
finite host objects. These require different encodings.

* I keep two permanent Word banks of capacity \(2^{24}\), with the root residue
  and index templates. I assign bank/slot labels to finite control. PR2753's
  source inventory bounds simultaneous numerical use below \(2^{22}\); the
  three fresh call grants fit the remaining capacity.
* I assign a fixed collection of canonical stream roles to the node input,
  peeled input, W family packets, 661 ordinary local packets, the private
  packet, the retained COPY input, residual input/current/output, programs,
  directories and cardinalities. I add fixed capsule and return ports. None of
  these roles changes its physical tape identity at a recursive call.
* I encode the program counter and finite source/slot labels in a fixed-width
  control record. A finite source label may have an enormous q-dependent
  alphabet; it still cannot contain n, w, h, a spectator value or a tape offset.

For a convenient allocation, reserve W+1024 persistent stream roles. The named
roles above, three child extents, eight node cardinalities, context.highs,
driver row count, three borrowed root input tapes and eight handoff ports fit
this allowance with room to spare.
Inactive roles hold an empty body after their LEFT marker. I also reserve
\(q^2+128\) scratch roles as justified in section 5. The machine can therefore
use at most

\[
2\cdot2^{24}+W+q^2+1156
\]

tapes: the Word banks, two Word templates, persistent and scratch roles, and
the parking tape and its packet port. I count the protected output and handoff
ports among the W+1024 persistent roles; the reusable checkpoint set excludes
those ports. This is a conservative existence bound, not an optimized machine.

I allocate the role inventory once. Clearing a role erases its body; clearing
does not release its identity. For borrowed Fields I construct a view of the
declared prefix role and omit the source's immediately overwritten empty Tape.
I retain a Stack's two roles until its Callback closes, even when a pop empties
them. These ownership rules avoid reliance on Python garbage collection.

## 3. Compile the whole caller to a finite word of blocks

All loops in `Driver.global_word` range over fixed source data: the global
schedule, replicas, ports, pairs, literal local events and GL64 low classes.
All source request labels and their good/fallback plans also range over fixed-q
sets. At compilation, unroll these loops in their source order. The resulting
word can be huge; its length contributes to \(F_q\), not to an input-dependent
oracle. Compile `LocalState.accept` and `finish` along each finite literal word,
preserving its version and private-COPY guards.

Use the following block vocabulary. A label names fixed roles and source data;
encoded dimensions and cardinalities remain on their declared tapes.

| Block | Action and successful return contract |
| --- | --- |
| NODE | Validate incoming weight; compute stock and extents; peel the remainder; split into canonical families. |
| GATHER_ROUTE | Gather the declared native low packet and route it to its fixed local role. Preserve the family. |
| RESIDUAL_BEGIN | Produce the current directory and prefix count, bind the fixed source plan, and initialize the residual current role from its source. |
| FORWARD/BACKWARD | Complete the plan's column adapter sweep in the source order, including reversed columns and commands on the backward sweep. |
| SWEEP | Complete one fallback ADD or linear-sign column sweep. |
| CHILD | Compute one good/main/half child boundary from encoded geometry; run the complete leaf or perform the call protocol in section 6. |
| RESIDUAL_END | Commit the complete residual result into its declared local/private/idle destination; clear residual work. |
| XOR/COPY/ERASE | Perform the corresponding literal operation on fixed roles, retaining the source's private-copy lifetime and guard. |
| ROUTE_SCATTER | Route a completed local role back and scatter into the latest contents of its family. |
| BRIDGE/EXCHANGE | Complete the two chronological bridge XORs, or exchange contents through one temporary role. |
| MERGE_RETURN | Merge the final families, place the owned result in the protected return port and clear the frame's roles. |

NODE and MERGE_RETURN bracket the fixed global word. A local event emits the
source's residual blocks at the exact point where `Driver.local` calls them.
An idle event emits them between its gather and scatter. A COPY first copies
its source into the retained COPY role; after its residual returns, it places
the output in the private role and clears that retained copy. ERASE clears the
private role at the original guarded position. No low class or physical prefix
is deduplicated.

For a good residual, emit FORWARD, CHILD(good), BACKWARD. For a fallback plan,
emit one SWEEP for each nonchild command. For each pair command emit the three
ordered CHILD candidates: half reset, main pair/unit, half reset. Each half
candidate checks the fixed same-bank condition and the encoded half width;
it does nothing when the source would omit that half. This preserves odd-column
central spectators and the source's f=1 case.

`residual_blocks.Cursor` gives this part of the construction explicitly. Its
state consists of a finite command position and one of three stages. It advances
before the block, so its serialized state denotes the return continuation.
All variable column loops finish inside a FORWARD, BACKWARD or SWEEP block.
A below-cutoff leaf finishes inside CHILD. An internal CHILD has no suspended
column iteration. Thus a recursive cut needs only the next fixed instruction
label, the root/child flag and finite slot labels. The caller never retains a
Python generator or an input-dependent host iterator across that cut.

The compiled node word applies to each generation. The child uses the same
word with new encoded size, program, directory and cardinalities. The fixed
CHILD label determines the pending destination and return action. Re-entering
at its successor cannot repeat a LocalState acceptance or a completed adapter.

## 4. Canonical commits and semantic refinement

When a completed primitive returns a new owned result, clear the old canonical
destination, transfer the result body into it and clear the result role. Preserve
the primitive's borrowed sources until it completes. `role_parking.transfer`
implements this destructive transfer with reads, writes and unit head moves.
Its work is \(O(L_{old}+L_{new})\); the source and destination return to LEFT.

Use distinct canonical roles even when the logical caller returns its input
unchanged. Copying that input into the designated result role removes pointer-
identity cases from the recursive interface. Within an atomic macro, finite
role labels suffice for the source's bounded aliases. A completed exchange uses
three transfers through a fixed temporary role. A scatter replaces its family
before the next gather or scatter reads it. This last rule preserves the
latest-family chronology in the source, including earlier helper returns.

Induct on completed blocks. NODE agrees with source peeling and row splitting.
Each nonrecursive block performs the same ordered source primitive operations
and then transfers their complete result without changing its contents. The
three-way residual expansion agrees with `trace.execute`, including reverse
adapter order and half-reset omission. Section 6 gives the recursive induction
step. MERGE_RETURN therefore produces the source's complete endpoint. The same
argument preserves borrowed inputs, source-program scope and physical prefix
multiplicity, since transfers copy symbols in order and no block identifies
equal prefix values.

## 5. Fixed scratch roles inside atomic blocks

Every source numerical array has fixed source dimensions and uses the permanent
Word banks. The only unbounded coefficient-evaluation nesting uses the existing
sequential pending/value Stack tapes. It does not allocate a matrix or Callback
per ancestor. I retain the source's preparation cost and encoded arithmetic.

For stream scratch, the following counts include nested callees but exclude
canonical inputs and destinations. They give a conservative lexical allocation;
the global reserve \(q^2+128\) exceeds their maximum.

| Source path in the frozen PR2753 export | Tape roles |
| --- | ---: |
| `predecessor/cardinal_counts.py`, `layout.child_extents` | 16 |
| `predecessor/fresh_rows.py` split/merge, excluding W canonical outputs | 8 |
| `predecessor/vendor/directory.py` context/produce | 12 |
| `predecessor/vendor/selection.py` gather/scatter | 10 |
| `predecessor/vendor/routes.py` complete owner route | 20 |
| `packet_engine.py`, `stream_runner.py`, `vendor/stream.py` complete ADD and coefficient | 32 |
| `vendor/bitstream.py` complete atom swap | \(q^2+24\) |
| `linear_sign.py` complete address sign | 16 |
| `recursive_call.py`, `vendor/children.py` descriptor preparation | 16 |

For each row, allocate the named lexical temporaries once for that macro's
active call path, and reuse them only after their last borrower finishes.
The variable loops justify that reuse as follows.

Count.product retains factor, scan and result, plus the one temporary copy in
Count.add; it closes that copy before the next multiplier bit. Directory
production clears its saved prefix before the next old-prefix ordinal. Routing
partition clears its key after each record and reuses two buckets; route_cube
alternates completed pass outputs. Fresh-row splitting assigns its W outputs
to permanent family roles and reuses its counters.

Digit swap uses exactly q² bucket roles, one output and bounded outer/middle/bit
counters. Atom swap additionally retains three cardinalities and the previous
digit result. It clears the previous result before the next pass. The packet
interpreter reuses one prefix copy, one local fibre, one changed fibre and its
partial packet output. These lifetimes fit q²+24. Address sign uses the PR2753
linear scanner, not the older w-pass sign.

The largest control-tape overlap occurs in `children.coefficient`: two Callback
objects and one extended Program. Each Callback owns two Stacks, each with a
main and reverse tape. That accounts for eight stack roles and one descriptor
role. The evaluator processes arbitrary history by pushing records on these
fixed tapes. Prefix, packet and arithmetic-counter roles fit the ADD allowance
of 32. Matrix and scalar temporaries use Word slots, not further stream tapes.

For lowered ownership, `Count.close` and `Counter.close` end their lexical
borrow. Callback.close/abort end all four Stack-role borrows. Borrowed Fields
create no placeholder role. Returned directories, cardinalities and descriptors
transfer to canonical destinations before their scratch scopes end. A Stack.pop
does not release its reverse role. No source variable loop retains a growing
collection of live Tape identities under these rules.

Inside a nonrecursive macro the call nesting depth is bounded by the finite
source call graph, except for the already serialized callback evaluation. Assign
distinct scratch roles to simultaneously active lexical owners. Each operation
then acts on a fixed tape or chooses among finitely many role labels. Replace
the Tape simulator's cell-array access by the stated read/write/unit-move
instruction. The head position remains a physical head, not a control integer.
This supplies a finite-tape implementation for each block; it does not add a
constant-time random-access operation.

The translation specializes the source's known callbacks and factories. It is
not a compiler for arbitrary Python callbacks. Replace known lambdas by their
explicit macro operands, omit observer/meter histories, and replace `.head==1`
guards by the quiescent-head invariant or a one-cell LEFT probe. Interpret
`.cells` only as the simulator representation of a tape. Initialize Word slots
by scanning the existing encoded root templates; do not read `.bits` into
control or construct new per-child templates. The original-program identity
guard becomes the declared current-frame program role and fixed source label.
Finite live/free slot maps remain finite control because capacity is fixed.

## 6. Call, park and return

Maintain the following cut invariant: canonical role bodies have no interior
BLANK or LEFT; heads stand immediately after LEFT; scratch roles are empty;
live Word slots have the unchanged root templates. Record the successor PC,
root flag and required finite Word-slot labels on the control role.

Prepare the child's full input capsule before parking: copy the current packet,
current directory, extended source program, prefix count, unused stock and the
three projected extents into fixed handoff ports. Copy modulus, width and depth
into three fresh Word slots. These copies belong to the child. The descriptor
and projected spectator formulas are the unchanged PR2753 formulas; the capsule
contains the whole packet, not a representative prefix or visible subchunk.

Park the canonical parent roles, including empty roles, in fixed order on an
outer PR2635 frame. For each body symbol write its four-bit code to the shared
packet port, clear the source symbol, then PUSH the record. Keep the role order
in finite control. `RoleParking.park` implements these steps. Open an inner
numerical frame on the same parking tape and call PR2769 PARK with the three
child grant slots. That codec parks the other live parent slots and preserves
their exact labels. The child now owns the empty reusable role bank and the
three grants. It adopts the handoff copies, clears the ports and starts at NODE.

On child return, put its completed output in the protected return port. Clear
its canonical and scratch bodies, close its numerical work and grants, then
restore the inner numerical frame. Restore the outer stream frame in reverse
fixed role order and read the parent control record. The output port lies
outside both restore sets. Transfer its result into the parent current role
specified by the CHILD return label, clear the port and continue at the recorded
successor PC. The source's saved borrowed roles and Word aliases have their
original contents and identities. Restore source ownership before any parent
comparison, cleanup or coefficient evaluation resumes.

Use a finite root flag in the current control state to distinguish final return
from a parent restoration. At a deeper call, save that flag with the parent and
set the child's flag to false. The machine needs no depth counter to find its
parent: the matched frame delimiters supply the stack discipline.

At the final root return, copy or transfer the protected result to the declared
output tape, close owned numerical words and erase the two templates by scanning
to RIGHT. Erase LEFT on each owned role and the parking port marker after all
matched frames have closed. Reset those heads by the known marker position
before erasing it. Leave the borrowed root input tapes intact. This final work
costs the sum of the fixed templates and cleared role extents, hence O_q(V_root)
on the stated domain. Intermediate calls retain the templates for reuse; the
outermost cleanup does not assume their cells disappear with a host object.

Induct on the finite decreasing-width call tree. The leaf blocks satisfy the
retained source contract. A completed child preserves the capsule's row and
spectator coordinates, while the parent remains unchanged on the parking tape.
The inverse codecs restore the complete parent; the protected result supplies
the one substitution expected at CHILD. The induction proves the compiled
caller's return contract. It also proves that parent frame delimiters cannot be
mistaken for child payload or partial records.

`numerical_frame.py` separately substitutes this numerical protocol into the
actual source Frame call site. It copies all three grants before PARK and
restores before the parent engine resumes. Its failure handling closes children
while the parent remains parked. That executable integration retains the source
generator scheduler; the finite macroprogram above removes that separate layer.

## 7. Movement and cell charges

For r canonical role records containing L source symbols, the role codec sends
S=4L bits through PR2635. Its matched frame costs exactly
\(5S+7r+3\) table steps, in addition to the explicit encoding, erasure and port
work. Those additional scans cost \(O(L+r)\). All r roles, including empty ones,
pay their delimiter cost. The numerical codec has its PR2769 linear invoice in
parked word bits, record labels and fixed bank-capacity scans. A fixed bank scan
is q-dependent constant work, not a scan through ancestor frames.

At each internal boundary, capsule copies, two checkpoints, restoration and
output commit cost \(O_q(V)\) under the retained local metadata envelope. There
are a fixed-q number of such boundaries at each node: a good request has one;
a fallback request has at most 49911, independently of f. Thus the total added
checkpoint work per node is \(O_q(V)\).

Canonical result commits need a separate charge. Fixed global/local event
commits add \(O_q(V)\). Adapter-column commits add \(O_q(fV)\); digit-pass
commits add \(O_q(wV)\). Consequently the complete added local work is
\(O_q(V(n+w))\), which preserves the p=1 recurrence in PR2753. I make no
claim that every canonical commit belongs to an O(V) node toll.

Let \(M_j=8V_j+32\Delta_j+E_j\) be the retained logical frame envelope. Canonical
ownership and the handoff ports add a fixed number of copies of already charged
complete packets, programs, directories or counts. Their total is at most a
q-dependent multiple of \(M_j\). Four-bit serialization adds another constant
factor. Scratch roles contain at most the retained block's live data; cleared
tails do not count as live symbols, but the machine may have visited them.

For a visited-cell bound on reusable tapes, bound each tape's largest occupied
prefix by the sum of charged frame/block extents that could occupy it. The fixed
role count multiplies the largest relevant extent by a q-dependent constant.
Each role keeps a dense body and moves only within that prefix or its adjacent
delimiter cell. The parking tape holds exactly the active ancestor encodings;
the packet port holds at most one current record. This argument includes erased
but visited tape cells and permanent markers/templates.

PR2753 proves \(M_j<(10+2^{-125})V_j\) on the stated domain and
\(V_j=V_{root}/(WN)^j\). Hence the physical reserve, including the complete
active parking stack, is

\[
O_q\!\left(\sum_j M_j\right)+F_q=O_q(V_{root})+F_q.
\]

For padded widths or uncoupled histories retain the explicit M ledger and the
preparation costs; do not use this absorption. I do not carry over the sharp
logical coefficient 11 to the physical construction.

## 8. Evidence and open boundary

The checks compare 16362 trace events in 36 good/fallback cases after 180
serialized cursor reconstructions. They cover f=1, odd f, both banks, threshold
63/64/65 and half threshold 127/128/129. A separate iterative fixture performs
1500 nested complete stream/numerical checkpoints with four permanent stream
roles and three allocated index slots. It retains its child result in a distinct
port through all restores. It uses an encoded countdown and no parent-object
stack.

The actual selected Frame checks cover normal return, constructor failure after
PARK and a deeper child failure. The complete small q=2, dimension=2 model covers
9216 addresses, 12 internal calls and 156 residuals using one numerical bank
pair. It uses one family, cutoff 2 and root coordinate projectors; its children
execute all twelve conjugated GL2 good/fallback forms. That model retains the
logical payload scheduler. Neither it nor the
cursor fixture executes the complete selected macroprogram from section 3.

Readers can review the fixed-role source compilation independently of those
finite controls. Section 9 adds complete small payload replays through the
generated controller. Stronger H2 primitives and the outer wrapper retain their
own mathematical contracts. I establish no new selected frontier or complete
integer multiplication theorem.

## 9. Executable fixed-role controller

I implement the finite source expansion in `macro_code.compile_node`. It follows
the retained schedule/replica/low/local order, authenticates LocalState during
compilation and emits explicit COPY, XOR, IDLE, bridge and exchange instructions.
It inlines each residual's finite block sequence. The compiler consumes only
fixed-q source labels and plans; input dimensions and high fields never enter
this pass. The complete selected expansion is effective but enormous. The
replays materialize complete reduced-source words, not a sampled GL64 word.

`macro_machine.Machine` runs one dispatch loop. Its header contains the root flag,
program-mode label, successor PC and five Word-slot labels: modulus, one, cap,
size and depth. I retain a derived Geometry/Layout only within the active
residual. I close its eight index words before CALL, so no cached object or
generator survives child descent. After RETURN I rebuild constructor-free views
of the five restored words and derive geometry again only if another block needs
it. I never rerun directory production, an accepted literal event or node setup
on a parent return.

The implementation uses W+s+21 reusable stream roles, where s is the largest
local owner count plus its private role. It adds eight handoff ports, one output
port and q²+128 scratch tapes. With the two numerical banks/templates and two
parking tapes, it uses at most

\[
2\cdot2^{24}+W+s+q^2+162
\]

working tapes. For s=662 this is below section 2's bound, including eleven
borrowed root input ports. The simulator creates Word backing objects lazily,
but each object has a slot in the fixed bank. Provisioning and clearing those
fixed slot markers adds q-dependent constant work; it does not allocate a bank
per child. I initialize word bodies by the existing template scans.

`scratch_pool.ScratchPool` selects a free role from a fixed inventory. A lease
contains a finite slot label and an active bit. Clearing the owned scratch value
ends that lease. A later stale close does nothing, while a stale read rejects;
it cannot erase a newer borrower of the role. The source's lexical-lifetime
inventory in section 5 bounds the simultaneous leases and aliases. The simulator
may create many lease objects over time, but it retains no lease history and
none crosses CALL. Meter and allocation counters are checker observations.

I specialize the authenticated source's Tape globals and default factories for
these leases. I add the four Stack-role releases at Callback.close and create
borrowed Fields views without allocating discarded placeholders. Stack.pop still
retains its reverse role. During execution I reject any new physical Tape or
Arena constructor call. This specialization implements the source rewrite in
section 5; it leaves the frozen files unchanged. Its Python namespace installation
is harness setup, not an input-dependent machine operation.

At successful root return I erase working bodies, permanent LEFT markers, Word
templates and the parking-port marker. I keep only the declared output and
borrowed inputs. Boundary probes use scanned LEFT symbols, and the controller
checks the exact declared live numerical slots. I require borrowed root input
ports to lie outside the reusable working bank.

`macro_binding.SelectedBinding` calls the retained selected coefficient and
descriptor routines. The selected junction replay checks a native rank-42
descriptor, repeated frozen prefixes, the exact projected gap, encoded successor
PC and parent restoration. It also runs actual adapter and generated-child
coefficient evaluations for an identity projector, with independently expected
values 0 and 2. Its 23-bit controlled body and unused stock 11 test this junction;
they are not an admitted complete selected payload.

The complete GL2(F2) controller replay executes 5859 macros from 483 descendant
and 63 root instructions, with 12 internal calls, 156 residuals and 9216 output
bits. It preserves the pinned logical replay's complete payload hash. The source
recursive Invocation constructor is disabled throughout the run. It uses 24
canonical stream roles, eight handoff ports and at most 20 live scratch leases
from its 132-role pool.

The complete GL2(F3) replay uses all 48 lows and four families, n=2, w=1, weights
(2,1) and external gap 2. It executes 25415 instructions on 31104 bits, including
192 MOVE, 96 COPY and 384 IDLE residuals. Independent projector formulas check
the private COPY data before its cancelling XORs; independent address formulas
check both intermediate sweeps and the final endpoint on all rows. I precompile
only this fixture's finite coordinate-zero coefficients, retaining source/view
and high-field checks. Production does not use that table. This fixture has no
internal child, while the GL2(F2) replay tests recursive control.

Additional controls reject stale leases, exhaustion and forbidden allocation.
A complete 1458-bit nonzero remainder peel checks the unpeeled coordinates and
external gap. A 2430-bit modulus-9 atom swap checks reuse across two radix digits.
These tests support the source refinement and ownership annotations. They do not
replace the parametric proof, prove stronger H2 or exhaust the selected GL64
source and arbitrary precision domain.

I also corrected the parent-identity coverage gap that starship-s reported in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960884).
The earlier deterministic signature omitted that identity. I reproduced its
acceptance of 214 corrupted candidate boundaries, including 42 invocations.
I now validate identity against `page.parent_identity` on both reference and
reconstructed paths before projection. Twelve controls cover None and foreign
parents for ENTER, INVOKE and RETURN on both paths. I serialize no object address.
The generated call gate separately rejects a missing parent, a different Program
view and a wrong source code before it prepares or parks a child.

For simulator efficiency, a scratch lease delegates append, rewind and clear to
the same retained Tape methods. Those methods still perform their literal reads,
writes and unit moves. I update the observational lease meter from their actual
counter differences; no counter value selects computation or a head position.
An exact-traffic control compares leased and ordinary tapes on empty, singleton
and longer bodies. This removes repeated Python wrapper calls without introducing
a bulk-copy or constant-time rewind primitive.
