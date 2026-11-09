# Same-tape microcontrol for the no-context scalar executor

Prepared for @CubeJerry with substantial OpenAI assistance. This is a
finite-control and serialized-clock lemma, not a source-tariff conversion,
complete recursive compiler, supplier admission or new multiplication bound.

## 1. Exact proposition, source and prior scope

We lower `execute_table(table, ports, readonly_context=())` and its called
CodedPort/origin routines from `research/compiled-owned-bank-lifecycle/machine.py`,
CubeJerry commit `ab239cb6ee884e7a900dd9101c34448077fad0b0`, Git blob
`acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. No Controller method is lowered.
The previous lifecycle proof already asserts finite expansion and a
constant-factor simulation. Its 13t bound prices coded primitive calls;
the rounded scalar proof separately counts table rows. The new contribution
is an explicit microstate generator, closure guards, rejection/head endpoint
equivalence, state/setup bill and a numerical serialized TM clock. The
general finite-control simulation principle is classical.

Fix a nonempty N-row table and P>=1 distinct tapes BEFORE runtime input.
`validate` requires exact row lengths/types, the six source opcodes,
integer ports in [0,P), write symbols0..6, unit moves±1, closed targets
and write/move fallthrough, and unique branch keys0..6. Rejection labels
are fixed strings of the finite source description. Duplicate-key tables,
zero-port cases, arbitrary malformed Python objects and readonly-context
ports are explicitly outside this grammar. In particular no altered
last-key-wins semantics for duplicate dictionaries is asserted.

The generated program uses the SAME P tapes and physical alphabet0..6.
Its finite states are `read(port,seven successors)`, `write(port,symbol,next)`,
`move(port,±1,next)`, `nop(next)`, and terminal success/rejection labels.
All ports, successors, symbols and labels are constants of finite control.
There is no runtime source-row lookup, program-counter arithmetic, payload
integer, decoder register, new tape or descriptor in the target machine.
Rejection labels are finite terminal observables, not strings emitted
for free on an output tape.

Let A count the source's actual raw read/write/unit-move calls, INCLUDING
successful final origin scans. Let U count fetched source rows, including
halt/reject when reached. For every terminating admitted execution the
target has identical mathematical tape contents, head positions and
terminal/rejection label, with exactly

    C = A + U

transitions. This is the clock of the chosen serialization, not an optimal
TM clock or a tariff unit. A finite-prefix correspondence also holds for
nonterminating executions; no totality theorem for looping tables is claimed.

## 2. Machine and origin domain

Canonical `02-streams.tex` permits at most one read/write per tape and at
most one unit movement of each head per step. A stationary head and a
step affecting only one tape are allowed. Every microinstruction is thus
one valid step. If a total simultaneous transition-function notation is
required, expand the7^P scanned-symbol tuples in finite precompilation:
inactive symbols are preserved and inactive heads remain stationary.
There is still exactly one transition per microinstruction.

Such a conventional transition can inspect inactive scanned symbols
implicitly. We do not identify those incidental reads with A. Exactness
concerns clock and tape/head effects. The verification simulator's active
action log matches the source raw calls; its host dictionaries, state
indexing and Python integers are NOT the target runtime or cost model.

For the usual local-origin guarantee, every distinct tape has its LEFT=2
at coordinate−1, an initial head at a nonnegative multiple of3, and no
other LEFT in the local body. Canonical bodies contain physical bits0/1;
malformed fixtures may contain other non-LEFT alphabet symbols. Coded
writes produce only bits. Completed coded operations preserve alignment.
A left move from0 detects LEFT and restores the original head before
rejecting, so an admitted aligned path cannot cross the protected marker.
Successful halt therefore returns every port to0. For more general marker
placement the compiler still reproduces the source loop exactly; it does
not promise that an interior LEFT is the caller's intended origin.

Initial head sites and all source movement sites are charged. No no-op or
state change visits a new head position. Inactive transition entries
preserve mathematical symbols without allocating extra host cells. The
target therefore has the same visited regions and historical head bounds.
No new assertion about a particular RAM-list allocator's capacity is made.

## 3. Literal primitive expansions

Each row has one dedicated dispatch no-op, charging one transition for
that source fetch. Its continuation is fixed, never a runtime row lookup.

**Read.** First perform the raw BLANK=6 probe. On blank, return logical4
to the precompiled branch target. On nonblank, retain the source's repeated
read of the SAME first bit. Three finite bit-prefix phases encode the
partial value as states. Each valid bit is followed by one right move.
A nonbinary bit rejects immediately at the current displaced head, with
no rewind. After three valid bits, perform all three left moves; only
then reject decoded111 as `unused virtual codeword`, or select its fixed
branch target. A valid nonblank read has4 reads and6 moves; blank has one
read. The target has no runtime integer accumulator.

**Write.** Write the three literal code bits, each followed by a right
move, then move left three times. This is3 writes and6 moves. Enter the
fixed next row dispatch.

**Move right.** Read the current cell. At physical blank, execute the
complete write-code4 routine, which returns to that head. Then move right
three times. Nonblank uses1 read+3 moves; blank adds3 writes+6 moves.
Frontier materialization is fully retained.

**Move left.** Move left once and read. On LEFT, move right once BEFORE
rejecting. Otherwise move left twice more, then enter the next row.
The rejection head is the original head, not the marker position.

**Goto/reject/halt.** Goto's dispatch jumps to a fixed row dispatch.
Reject's dispatch enters its terminal without origins. Halt's dispatch
enters the common origin chain. Each port uses three states: left move;
read and either loop to that left move or proceed on LEFT; right move.
Initial/loop left moves share one state. The P-port loop is unrolled;
its final right move enters success. Terminal states take no transition.

## 4. All-width invariant and exact clock

Relate a source row entry pc to target dispatch state pc with identical
tapes and heads. Within each coded routine, relate its next literal raw
action and finite phase/value to the corresponding microstate. Section3
covers every physical symbol0..6 and every error branch. A source raw
action becomes one target transition with the same active effect. A source
fetch becomes one dispatch no-op. Primitive completion reaches the correct
fixed row dispatch; halt enters the literal origins; all rejection paths
terminate without success cleanup.

Induction on interleaved row-fetch/raw-action events proves the relation
for every finite prefix, independently of widths, number of components,
values or column multiplicity. Counting events gives C=A+U. There is no
extra terminal transition. An infinite self-goto loop has A=0 and infinitely
many dispatches; an infinite origin search has the same raw-action loop
on both machines. Neither is described as total.

This is an execute_table theorem only. Work retirement, Controller
recursion, source/header export, owned/history wrappers and readonly
contexts are excluded. Successful private bodies remain uncleared exactly
as in the source executor. A caller supplying even unused readonly-context
tapes still requires its own separate interface lowering; none is inferred.

## 5. State, setup and backing bills

A branch decoder uses1 preliminary read,1+2+4=7 prefix-read states,
2+4+8=14 forward-move states and3*8=24 value-specific rewind states:
46 primitive states. Write uses9, positive move13, negative move5.
There are N dispatch states, at most N literal rejection terminals, three
shared protocol-error terminals, one success terminal and3P origin states.
Thus, including unreachable generated states,

    S <= N + 46N + N + 3P + 4 = 48N + 3P + 4.

`check_program` verifies every state/port domain and all successors.
The compact description has at most7S successor edges. Its encoded size
is at most a constant times the FULL source description length plus
S*(log(S+1)+log(P+1)+1), including rejection labels. An explicit total
simultaneous transition function has at most7^P*S entries, each containing
P output symbols/movements and a fixed successor. The alphabet expansion
cost is finite but is not free.

Let F(T,P)>0 denote actual finite precompilation, validation, encoding and
installation work for the chosen representation, including reading the
whole table/labels. F is separate from runtime payload execution. The
generator explicitly builds finite trees/chains and resolves bounded
identifiers. Ordinary sequential lists and finite binary arithmetic on
tapes suffice to implement this finite computation; no unit-cost RAM
assumption is needed for finite F. A deployment rebuilding its program
must pay F again. The total bill is F+A+U. No new numerical setup bound
or absorption of F into a historical tariff is claimed.

The target has exactly P runtime tapes and no new workspace. Its fixed
program description/state inventory remains a positive cost. The identical
active head trajectory preserves visited-region and historical bounds;
this lowering does not clear old backing, remove caller/ancestor storage,
or create productive helper credit. Those separate obligations remain.

## 6. Executed evidence, limitations and credit

The author verifier compares exact active-action traces, terminal labels,
tape contents, heads, visited regions and C=A+U against the UNCHANGED
source executor. It checks17 primitive cases and90 instances of three
small retained rounded SCALE tables, widths1..4:79 successes and11 range
rejections. Primitive cases cover all seven decoded symbols, physical
blank, unused111, each malformed bit position, blank materialization,
goto, fixed rejection, left-origin restoration and multiple final origins.

Eleven malformed-table guards reject. Two compiled-graph mutations remove
the initial raw probe or the left-origin restoration; trace/head/clock
comparison detects both. A bounded100-step self-goto prefix tests that
looping programs are not described as total. These finite checks support
the universal bisimulation proof rather than replacing it. The simulator
is explicitly separate from the target-machine definition.

The new implication is a concrete unit-labelled finite-control conversion
for the exact no-context executor. The scalar/pass invoice still needs
its own volume/price bridge; C=A+U does not supply that missing tariff rho.
No full arithmetic catalogue, caller admission, global assumption
discharge or new kappa is claimed. Credit CubeJerry's lifecycle and rounded
scalar predecessors, canonical stream-model authors and the complementary
model-assisted reviewers. The underlying simulation principle is classical.
