# Written review of the exact increment cost and sharp uniform constant

**PASS under the stated marked-counter entry and counting contract.**
The actual source increment macro has the exact from-zero count

    C(k)=13k-7popcount(k)+5ell(k),  k>=1,

and satisfies the sharper homogeneous uniform bound `C(k)<=15k`.
Equality occurs exactly at k=4, so15 is the least such coefficient for this
literal macro and convention. This is an isolated macro result, not a lower
bound for all increment algorithms or a recosting of the complete producer.

The exact formula and its coarse18k consequence are already stated in
thu-nmrc PR6719's SHAPE-PROOF at source head
`3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`. The review reconstructs the source
paths and tightens that local uniform coefficient; binary-counter amortization
and the arithmetic identities are classical, not new generic arithmetic.

## Source, exposure and allowed evidence

I read only the inert shape-producer, counters, machine and SHAPE-PROOF text,
then statically read the coordinator's shared emitter.py before its first
execution. I did not run, import, compile or simulate a source program, inspect
an emitted table after execution, generate a table, or write a verifier.
The source proof already disclosed the claimed formula, so this is a
source-aware independent written derivation rather than a blind discovery.

The relevant code is producer.increment, counters.emit_rewind and the retained
machine/Assembler grammar. A label/fresh-name operation emits no instruction.
Each branch, write, unit move and goto costs one executed microinstruction.
The count ends immediately after the final rewind move returns the head to1;
it excludes a wrapper HALT, initialization and any caller loop/control work.
The machine's counted reads are the symbol-branch reads, not host instrumentation.

## Entry, arithmetic and exit invariant

For positive n, the target has LEFT at0, canonical LSB-first binary digits at
1 through ell(n), RIGHT at ell(n)+1 and head1. The unique temporary-zero
representation is LEFT0, RIGHT1 with no body digit; set ell(0)=popcount(0)=0.
Replacing that state by a body ZERO is a different entry convention and
changes the exact initial cost.

Future growth cells are genuinely blank owned writable cells, distinct from
every live protected input or other physical role. This matters because the
growth branch writes the new RIGHT without first checking that cell is blank.
The macro alone does not validate all such ownership/blankness conditions.

Let t be the number of trailing ONE digits of n. The t carry iterations each
change ONE to ZERO and move right. If the next symbol is ZERO, it becomes ONE
and all higher digits/RIGHT remain unchanged. If it is RIGHT, the old marker
becomes the new high ONE and a new RIGHT is written one cell farther right.
These are precisely the binary additions n->n+1. The top positive digit
remains ONE, and the initially empty state becomes canonical1. The existing
LEFT is never overwritten. Rewind returns head1, so induction permits the
next call with the same convention.

This proves positive canonical output from temporary zero. It does not prove
cleanup or complete validation on malformed inputs: a default failure can
occur after earlier carry writes, and rewind itself uses its default for any
non-LEFT symbol. The valid entry invariant supplies the required marker order.

## Exact instruction paths, including rewind

A carry iteration costs four instructions: branch, write ZERO, move right,
goto. For rewind starting at head h>=1, there is one initial move left;
h-1 non-LEFT cells each cause branch, move left, goto; and the LEFT branch
plus final move right cost two. Rewind therefore costs exactly3h.

After a nongrowth terminal ZERO, the head is t+1. Its terminal work is branch,
write ONE and goto rewind, costing3. After terminal RIGHT, work is branch,
write ONE, move right, write RIGHT and goto, costing5, and the head is t+2.
Consequently:

| Path | Branch/read | Write | Move | Goto | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| nongrowth | 2t+2 | t+1 | 2t+2 | 2t+1 | 7t+6 |
| growth | 2t+3 | t+2 | 2t+4 | 2t+2 | 7t+11 |

The branch to RIGHT is counted, and so are every rewind branch/move/goto.
No return or hidden host arithmetic is omitted: the macro finishes by ordinary
instruction fallthrough after its final move. If a harness executes an appended
HALT, its observed full count is one larger per invocation, unless it stops
at that continuation boundary before executing HALT.

## Summing the first k calls and proving15k for all k

Write s(n)=popcount(n), with s(0)=0. Every increment obeys
`s(n+1)-s(n)=1-t(n)`, including a complete carry. Summing n=0 through k-1
gives `sum t(n)=k-s(k)`. A growth occurs exactly when the new value n+1 is
a power of two, including1. There are exactly ell(k) such events up to k.
Writing the per-call total as `7t+6+5*growth` yields

    C(k)=7(k-s(k))+6k+5ell(k)
        =13k-7s(k)+5ell(k).

The aggregate opcode counts are also exact:

    branches=4k-2s(k)+ell(k),
    writes  =2k-s(k)+ell(k),
    moves   =4k-2s(k)+2ell(k),
    gotos   =3k-2s(k)+ell(k).

They sum to the displayed C(k). These are symbolic identities, not counts
inferred from a finite grid or convolution.

Put d=ell(k)>=1. Then s(k)>=1 and k>=2^(d-1), so

    C(k)-15k =5d-7s(k)-2k <=5d-7-2^d.

For d=1 and2 the last expression is strictly negative; for d=3 it is zero.
For d>=3 the gap `2^d-5d+7` increases by `2^d-5>0` on passing to d+1.
Thus it is nonnegative for every d, proving C(k)<=15k for every positive k.
Equality requires equality in each step: d=3, s(k)=1 and k=2^(d-1), hence
k=4. Directly from the exact paths, the first four costs are11,18,6,25,
whose sum is60=15*4. Any smaller homogeneous coefficient fails there.

## Arbitrary starting values need an initial accounting term

For canonical initial n>=0 and k increments, the same path proof gives

    C_n(k)=13k+7(s(n)-s(n+k))+5(ell(n+k)-ell(n)).

It is not legitimate to discard its initial-value terms. In particular,
starting from the d-bit all-ONE value2^d-1 gives one growth cost7d+11.
Starting from n=3 therefore costs25 for one call, exceeding both18 and15.
The source's18k is an amortized from-zero statement, not an18-step per-call
bound for arbitrary initial words.

For example the standard popcount accounting yields
`C_n(k)<=18k+7s(n)-7s(n+k)`, since at most k calls grow. For the sharper
coefficient define `Psi(n)=2n+7s(n)-5ell(n)` with Psi(0)=0. The proved15n
bound says Psi(n)>=0, and the exact formula gives

    C_n(k)=15k+Psi(n)-Psi(n+k).

Thus arbitrary entry needs its initial credit/potential rather than a free
from-zero bound. This accounting identity does not install physical work or
authorize reclaiming owned storage.

## Space, heads, markers and ownership

Across the first k calls from temporary zero, the head stays in
0 through ell(k)+1 and returns to1 after every call. Every newly needed
position is reached on growth, and rewind reaches0; the visited target-cell
set is exactly that interval, of size ell(k)+2. The final explicit packet
contains LEFT, ell(k) body digits and RIGHT. Erasing a later packet would not
erase these visits from a space bill. Arbitrary starting words must instead
include their initial extent; inaccessible backing and physical entry
ownership remain separately charged.

No other tape is an instruction operand of this macro. Other roles are
preserved when they are genuinely distinct physical tapes; numerical role
names alone do not rule out aliased host Tape objects. The increment leaves
its delivered packet owned and live. It does not retire its output, reset its
head to0, provide an independent productive input, or make marker installation
and eventual erasure free.

## Static extraction review before first execution

The reviewed emitter text has SHA256
`c55e00e397dc06c402b2033652fd2dd5baf385b41e9ca4a1b4c14f8d21080fd9`.
The shared emitter authenticates all three complete source files first. It
parses producer text but selects only its single top-level increment FunctionDef,
without modifying the body. It checks the exact four arguments
asm,tape,fail,prefix and absence of defaults/decorators/variadic parameters.
The actual pinned function has no definition-time annotations or other such
side effects. The producer module's importlib loader, router imports and full
build functions are not executed by this extraction.

The pinned machine and counter modules supply their real constants, Assembler
and emit_rewind. The source machine's symbol values are preserved: BLANK0,
LEFT1,RIGHT2,ZERO3,ONE4,UNIT5,MARK6. The temporary public module alias machine
is restored in finally, allowing the original counter's import to bind the
intended source module. The helper loads module definitions; it does not
construct or run the source Machine or Tape, nor call binary-to-unary setup.

The emitted macro begins at PC0 with its first branch. The following HALT is
recorded as stop_pc, and the separately appended failure reject as fail_pc.
This correctly permits a harness to measure the macro up to but excluding
stop_pc. The JSON roundtrip changes tuple/list representation, not opcode,
symbol, direction or resolved target values. The two numerical engines share
this extraction/emission dependency; that must not be described as independent
source compilers. Their own simulation and actual table outputs have not been
inspected or certified by this written review.

## Precise remaining scope and credit

Conditional proof and static extraction review pass; no material gap found.
This does not verify a complete quotient/product producer, input converter,
linked router, codec/stack caller, all-size1000V/100V bill, numerical input
validation/cleanup, physical allocator or any paid/native/compiler/outer
claim. The isolated15k bound is not automatically a changed full invoice,
tariff, exponent, selected frontier or discharge of a framework assumption.
Literal extraction/execution receipts and independent simulations are separate
coordinator obligations, not facts supplied by this note.

thu-nmrc/PR6719 retains the increment implementation, exact source formula and
child-grant application credit, with substantial OpenAI Codex assistance.
David Arias/PR2776 retains the exact machine, Assembler, counter/rewind and
marked-tape framework credit; the source's Ali Romman/whole-high and retained
lineage remain unchanged. Binary carries, popcount telescoping, amortization
and bitlength bounds are classical. This external written AI review adds an
exact isolated sharp-constant audit, not a generic arithmetic invention,
independent human acceptance or proof-kernel certificate. Apache-2.0.
