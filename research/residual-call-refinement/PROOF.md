# Conditional residual and CALL refinement

This note independently audits one implication claimed in
[the fixed-role caller proof](../selected-bit-physical-caller/PROOF.md), sections
3, 4 and 6. The implication is that its literal residual blocks and CALL/RETURN
protocol implement the frozen source residual, once the completed operations
they call satisfy their stated contracts. The argument below makes that
implication explicit for every admitted width. It does not prove those operation
contracts, compatible stock, the physical reserve, a selected supplier, or a new
multiplication exponent.

The residual grammar, geometry formulas and recursive source contract are
predecessor results. David Arias supplied the all-size source in
[PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753).
Jose Manuel, `jmbarrancoml`, supplied the fixed-role lowering retained in
[selected-bit-physical-caller](../selected-bit-physical-caller/README.md).
This audit claims no novelty for those constructions. The source baseline and
file pins for this audit are in [SOURCES.json](SOURCES.json).

## 1. Scope and hypotheses

Fix a prime permitted by the frozen selected source, a precision \(w\ge1\),
and \(A=q^w\). Consider any admitted internal invocation of width \(n\ge64\)
and encoded depth \(h\). Write

\[
f=\lfloor n/64\rfloor\ge1,\qquad \delta=n-64f,\qquad 0\le\delta<64.
\]

The following hypotheses specify the implication being audited.

1. The residual definition comes from the production `SelectedBinding` and the
   fixed source compiler. Its plan has dimension 64, a selected rank
   \(1\le r\le42\), and the canonical good or fallback command grammar.
   Fallback child fields satisfy \(0\le i<k<128\), and their kind is `pair`
   or `unit`. A nonchild fallback command is `add` or `sign`.
   `Machine.block` receives the corresponding compiler-produced block.
   The fixture-only `axis` branch is outside this statement.
2. The current program, directory and encoded numerical context are canonical
   and describe this invocation. The directory has \(P\) physical prefixes,
   each with \(h+1\) fields including the current source field. Its stored
   prefix count is \(P\). Prefixes may repeat and their Boolean payloads may
   have arbitrary correlations. Directory production and validation preserve
   their order and multiplicity.
3. At residual entry the complete selected packet has coordinate order
   \([P][U][B][A^n][G][A^n][S]\), with all displayed cardinalities positive.
   `unused` contains \(U\), `before` contains \(B\), and `leading` contains
   \(UB\). The recursive stock premise supplies enough fresh rows for every
   generated child. The local divisibility check by 9475 alone is not this
   premise.
4. Completed packet operations, coefficient evaluation and source-bound child
   program extension satisfy their frozen contracts. In particular they preserve
   source inputs, complete prefix ordinals and spectator coordinates, and reset
   their declared heads. Paired completed child implementations return the
   same source-prescribed owned result on the whole input packet. This is a
   relative contract. Section 6 states the additional enclosing-node premise
   needed to discharge it by recursive induction.
5. Encoded arithmetic, copying, canonical commits, role transfer and parking
   satisfy their contracts. Arithmetic has the margins required by the source.
   Parking restores every parent role and live numerical slot, including empty
   roles, with its original symbols and declared head position. Its child grant
   slots, handoff ports and protected output port have the disjoint ownership
   specified by the caller.
6. At each completed block boundary canonical heads are reset, scratch is empty,
   and the only live numerical words are the declared persistent context and
   any declared active geometry. Execution is successful and well bracketed.
   Recovery from interruption partway through a parking operation is outside
   the claim.

The relevant definitions are
[`macro_code.compile_node`](../selected-bit-physical-caller/macro_code.py),
[`SelectedBinding`](../selected-bit-physical-caller/macro_binding.py),
[`Cursor` and `events`](../selected-bit-physical-caller/residual_blocks.py), and
[`Machine`](../selected-bit-physical-caller/macro_machine.py).
The admitted source domain and the stronger recursive stock premise appear in
the frozen [PR2753 proof](../selected-bit-physical-caller/inputs/pr2753/PROOF.md),
sections 1 through 4.

The observations in this refinement are complete packet symbols, physical
coordinate ordinals, source scope, ownership, declared live numerical slots and
head reset conditions at completed blocks. They exclude checker counters,
temporary allocation history and literal Python object identity. An Event
word may be read only during its documented borrow lifetime.

## 2. Literal residual expansion

Let \(b_1,\ldots,b_\ell\) be the successive blocks returned by a fresh
`Cursor(plan)`. Then, for the same geometry and source binding,

\[
\operatorname{execute}(\text{page})
=\operatorname{events}(\text{page},b_1)\cdots
 \operatorname{events}(\text{page},b_\ell)
\tag{1}
\]

as ordered Event values and requests during their borrow lifetimes. Boundary
events also have the corresponding current parent identity. Equality here does
not identify the temporary Word objects used by the two executions.

For a good plan `Cursor.take` returns `forward`, `good`, `backward`.
The first and last call the same `adapters` routine as
[`trace.execute`](../selected-bit-physical-caller/inputs/pr2753/trace.py).
The backward routine reverses both column order and command order. The middle
block calls `child` with first position 0, second position \((128-r)f\),
width \(rf\), and kind `good`. These are exactly the arguments in `execute`.

For a fallback plan, induct on its finite command position. A nonchild block
performs the same complete ascending column loop, `Geometry.point` calculations
and coefficient Requests as `execute`. A child command expands into stages
0, 1 and 2. Stage 1 agrees with the main invocation in `trace.pair_command`,
including the pair field and tail reversal flag. Stages 0 and 2 both vanish
when \(i,k\) are in different banks or when \(f=1\). Otherwise both give
the same half-reset invocation as `pair_command`. This proves (1).

The source computes one half word and lends copies to its two resets. The
block expansion computes an owned half word for each reset. The values and
their release obligations agree at the completed block boundary. The source's
unused half computation for a cross-bank command has no observable packet
effect under the arithmetic hypothesis.

`Cursor.take` advances before it returns a block. Thus its serialized state is
the next block, including the stage following a half-reset. For a fixed plan,
the cursor bounds depend only on the finite source command list. No column
index or input width enters that serialized state.

## 3. Geometry and the complete packet identity

The logical residual body has \(128f\) atoms. Its embedding into the original
two-bank body is

\[
\phi(p)=
\begin{cases}
p,&p<64f,\\
p+2\delta,&p\ge64f.
\end{cases}
\]

This is `Layout.physical`; `Machine.geometry` retains the original parent
width \(n\). The omitted \(2\delta\) atoms are the peeled head and tail
remainders surrounding the original external gap. They remain spectators.

Every emitted child has width \(c>0\), ordered disjoint chunks, and each chunk
is contiguous in one original bank.

* A good child has chunks \([0,rf)\) and
  \([(128-r)f,128f)\). Since \(r\le42<64\), each lies on its stated side
  of the embedding discontinuity.
* A main fallback child has chunks \([if,(i+1)f)\) and
  \([kf,(k+1)f)\). Distinct row fields give disjoint chunks, each within
  its bank.
* Put \(d=\lfloor f/2\rfloor\). A retained half-reset has chunks
  \([kf,kf+d)\) and \([(k+1)f-d,(k+1)f)\), both within row \(k\).
  Its middle spectator has \(f-2d\) atoms. This is one atom when \(f\)
  is odd and zero when \(f\) is even. If \(f=1\), the reset is absent.

Consequently, with \(a=\phi(\mathrm{first})\) and
\(b=\phi(\mathrm{second})\), all the checks in
[`Layout.child_extents`](../selected-bit-physical-caller/inputs/pr2753/layout.py)
hold: \(a+c\le b\), \(b+c\le2n\), each mapped last atom equals its
physical interval's last atom, and neither chunk crosses the old gap.

Define \(\epsilon_B,\epsilon_G,\epsilon_S\) to indicate which of the three
spectator regions contains the original gap. Explicitly,

\[
(\epsilon_B,\epsilon_G,\epsilon_S)=
\begin{cases}
(1,0,0),&a\ge n,\\
(0,0,1),&b+c\le n,\\
(0,1,0),&a<n<b+c.
\end{cases}
\]

In the third case bank contiguity gives \(a+c\le n\le b\). The alternatives
are exhaustive and disjoint. The projected extents are

\[
B'=BA^aG^{\epsilon_B},\qquad
G'=A^{b-a-c}G^{\epsilon_G},\qquad
S'=SA^{2n-b-c}G^{\epsilon_S}.
\tag{2}
\]

The volume identity is therefore

\[
P U B' A^c G' A^c S'
=P U B G S A^{2n},
\tag{3}
\]

because the atom exponents sum to
\(a+c+(b-a-c)+c+(2n-b-c)=2n\), and the gap indicators sum to one.
More than volume is preserved. Formula (2) groups the before, middle and after
intervals in their original coordinate order. The child head and tail are the
two retained contiguous intervals. The resulting mixed-radix regrouping is a
bijection that identifies each original coordinate, even for arbitrary payload
correlations. Preserving a regrouped spectator ordinal therefore preserves
each constituent coordinate.

The distinction between \(U\) and \(B\) matters here. Ordinary operation
scans use `Layout.before=leading=UB`. `Machine.prepare_child` instead passes
the original `before=B` to `child_extents` and copies `unused=U` to the child
`rows` port. Thus (3) has exactly one factor \(U\). Address spectators never
supply fresh rows. The complete prefix count and entire packet are passed;
the call does not select one representative fibre.

## 4. Source binding and child program

`Machine.prepare_child` first requires

\[
\text{event.parent_identity is self.program},\qquad
\text{event.source_code}=\text{definition.code}
 =\text{layout.geometry.source_code}.
\]

The page created by `Machine.geometry` supplies precisely that current Program
view and definition code to the literal trace. Under hypothesis 1 all other
boundary labels and numerical geometry follow from section 2. The call gate is
not a validator for arbitrary externally supplied block tuples or Events.

`SelectedBinding.child_program` constructs one child Request with the Event's
kind, field, reversal and half flag. The frozen
[`children.extend`](../selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/children.py)
copies the unchanged parent program and appends its source code, rank, finite
flags, parent size and exact generated child size. The child sizes are
\(rf\), \(f\), or \(\lfloor f/2\rfloor\), respectively, and depth becomes
\(h+1\). They agree with section 3. The callback's canonical program checks
are in
[`Callback.step` and `_validate_program`](../selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py).

Reading the first directory prefix validates the context for this extension.
`extend` does not use its numerical high-field values to choose the descriptor.
Its output depends on the parent program, fixed source specification and finite
child flags. `Machine.prepare_child` copies the full directory and stored
prefix count separately. Consequently the use of a first prefix does not
collapse repeated prefixes or replace a whole-packet invocation by one
invocation per high value.

The relation between source and target programs is equality of their canonical
encoded program and source scope. Within each active target frame, Events must
refer to its exact current Program view. After a return, `restore_context`
creates a fresh view of the restored canonical program tape. That fresh view
represents the same source Program. Literal Python object identity across CALL
is not part of the relation. The old Event has already ended its borrow lifetime
before this view changes.

## 5. Completed block and CALL simulation

For a sweep, an adapter block, an empty reset, or a child of width \(c<64\),
`Machine.block` consumes the whole literal Event stream through
[`packet_engine.run`](../selected-bit-physical-caller/inputs/pr2753/packet_engine.py).
Equation (1) and the completed-operation hypotheses give the same packet as
the source. The canonical commit only replaces the target result role and
resets heads. The below-cutoff branch keeps the source's complete eight-stage
weighted leaf sequence and its matching ENTER/RETURN boundaries.

For \(c\ge64\), the compiler-produced child block consists solely of one
internal `trace.child`. The source yields ENTER, INVOKE and RETURN with the
same boundary labels and values. In `packet_engine.run_generator`, ENTER and
RETURN maintain validation state. INVOKE performs the one whole-packet child
substitution. No primitive packet action occurs between them. Under the child
contract their combined effect is exactly one substitution with the capsule
from sections 3 and 4.

`Machine.block` obtains ENTER and `prepare_child` copies that capsule into
independent handoff ports. It copies modulus, child width and child depth into
the three grant slots. The `finally` clause then closes the trace before CALL.
Closing the suspended `trace.child` executes its two cleanup clauses, releasing
the borrowed Event depth, first position, second position and width. No Event
word is subsequently read. `close_geometry` also releases the cached columns,
geometry constants, layout words and field count before the parent is parked.

The copied grants and capsule therefore suffice for the child. There is no
suspended parent column loop or source generator when the dispatch loop begins
executing child instructions. The source's later INVOKE/RETURN bookkeeping is
discharged by the child substitution and the restoration protocol below.

Let \(k\) be the current compiled PC. `Machine.call` stores \(k+1\), the
parent mode, root flag, and finite labels of its persistent numerical words.
It parks the canonical roles, then numerical state, adopts the handoff copies,
and sets child PC to 0 in `binding.child_mode`. The production binding uses
mode 0. The compiled word starts with NODE and places RESIDUAL_END after the
residual blocks, so \(k+1\) is an in-range successor label. It is fixed source
control, not a decoded width or column index.

When the child completes, its result is on the protected output port.
`Machine.complete_return` closes child geometry, roles and numerical work,
restores numerical state, then restores canonical roles. It reads the saved
header, reconstructs the parent context and Program view, and transfers the
protected result into parent `current`. Thus the parent source roles, directory,
prefix count, extents and unrelated state have their pre-call contents, while
`current` has exactly the completed child output. The output port is empty again.

Both descent and parent restoration return `"jump"` to the dispatch loop.
The loop increments its PC only for `"next"`. The resumed instruction is
therefore exactly \(k+1\). It neither repeats the child block nor skips a
following block, and cannot repeat RESIDUAL_BEGIN or an earlier adapter.
This is the same continuation as the already advanced residual cursor.

## 6. Conditional theorem and remaining obligations

Under hypotheses 1 through 6, related source and target residual entries
produce the same complete Boolean packet, preserve the same physical prefix,
row and spectator ordinals, and reach related completed residual exits.
The caller's borrowed inputs and unrelated roles retain their contents.
RESIDUAL_END installs the completed result in the declared destination and
clears the residual directory/count work. The target uses the exact successor
of each completed child block. Source Program scope corresponds to the active
target Program view as defined in section 4.

To prove this statement with completed children supplied as contracts, induct
on the finite residual block sequence using sections 2 through 5. Every emitted
child satisfies

\[
0<c\le42f\le\frac{21}{32}n<n.
\]

Children below 64 complete inside their block. Internal children have smaller
width and, by the recursive stock and canonical-context hypotheses, remain in
the admitted domain. Thus strong induction on width is available to a complete
caller proof. That proof also needs the enclosing node compiler to agree with
the source NODE, hosting, local-word and return composition when its residuals
and children satisfy their contracts. This note does not audit that separate
node correspondence. Supplying it permits the induction hypothesis to establish
the completed child contract used here. Width descent alone does not establish
that contract.

The scoped implication proved here therefore concerns residual expansion and
the CALL substitution and continuation. It does not prove the correctness of
the entire node compiler, each packet operation, stock provision or a physical
implementation of every retained operation.

The earlier finite cursor comparisons in
[`continuation_checks.cursor_checks`](../selected-bit-physical-caller/continuation_checks.py)
already check selected good and fallback traces at representative widths and
reconstruct their return cursors. Such comparisons are evidence for individual
instances of (1). The all-width assertion here rests on the structural argument
and hypotheses above. No finite replay establishes those hypotheses over the
whole source domain.

## Open next questions

* Compose this lemma with [PR2989's separate whole-word ordering
  audit](https://github.com/CrocSwap/integer-mult-bounds/pull/2989), then bind
  the actual NODE/peel/split and MERGE/return operations to their source
  contracts. Start with their complete physical row coordinates under root
  coupling. Abstract instruction ordering does not discharge those payload,
  stock and ownership obligations.
* Prove or replace the retained packet-operation contracts with the stronger H2
  contracts required by the selected supplier. Start with one actual route or
  weighted leaf and price its coefficient evaluation and head movement. The
  present baseline CALL refinement supplies no H2 saving.
* Join the independently established stock provision and parking contracts to
  the residual entry relation. Start with the exact child capsule and preserve
  the separate \(U\) coordinate and all borrowed inputs. This requires the
  full recursive stock premise, not merely the runtime's local quotient check.
