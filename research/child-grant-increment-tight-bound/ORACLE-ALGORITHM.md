# Dense-list transition oracle — unexecuted implementation

The oracle independently interprets the actual isolated increment table with
two dense-list tapes and its own dispatch loop. It reads no primary code or
first output. It never instantiates or runs the retained source Machine or
Tape classes. The candidate table construction is deliberately shared:
emitter.emit_table authenticates the three source objects, extracts the exact
increment function by AST and uses the retained Assembler/counter emission
helpers. The original complete producer module is not imported. This is
independent transition checking, not independent end-to-end construction.

No oracle import, emission, compilation, AST evaluation, interpreter run or
test has occurred at this readiness point. Root alone seals and executes
the firsts. Reading source text and hashing bytes are not such executions.

## Tape model and exact cost boundary

Each simulated tape is a dense list with a fixed index offset, supporting
the declared negative spectator positions and positive counter/work extent.
Its head is an integer held by the observer implementation. The interpreted
program obtains only a scanned symbol. Dispatch has separate cases for
branch, write, unit move, goto and rejection. A premature halt is an error.

Execution stops when the PC reaches stop_pc, before the wrapper HALT.
Each source branch, write, move and goto contributes one step; the wrapper
HALT contributes none. Branches honor both every explicit symbol target and
the default target. A write/move advances PC by one. A move records both
its starting and destination positions. Per-call visited sets start with1
and reset for each macro invocation; sequential tape contents persist and
cumulative_steps sums actual completed macro counts. No closed cost formula
is used to generate the measured rows.

The active tape has LEFT at0, MARK at-1 and a far UNIT sentinel at4096.
Temporary zero is RIGHT at1 with no digits. Positive results must have
only ZERO/ONE digits, a most significant ONE, one correctly placed RIGHT,
and final head1. Every other non-sentinel position is physically BLANK.
The entire spectator tape1, including its head-7 and dense contents, is
compared before and after each accepted invocation.

## Positive finite domains

The sequential fixture begins at temporary zero and executes1024 actual
increments on the same active tape. The PC returns to entry for each call,
but no counter data is reset. Each row contains the observed integer value,
actual step count, cumulative count, final head and per-call visited extrema.
Every observed cumulative count must be at most15 times its call count.

The long-carry fixtures are initialized independently to2^d-1 for each
frozen d through256. Their values are decoded by the external observer
only after actual execution and must equal2^d. The certificate retains
the actual counts and extrema, not values inferred from a formula.
The observed long-carry count must additionally equal7*d+11. This is a
check on actual execution, not a formula used to manufacture its row.

The k4 sharp witness must be recovered from the actual fourth cumulative
row as60. The retained uniform coefficient15 is the declared target whose
all-k proof belongs to the separate written argument. A finite domain,
even1024 calls and256-bit carries, does not itself prove that universal
bound or any complete producer/router resource ledger.

## Eight executed controls

Four mutations change actual instruction data in a private table copy:

1. At the entry ZERO path, replace its ONE write by ZERO. Executing on2
   must return the wrong canonical value2 rather than3.
2. At the carry ONE path, replace its ZERO write by ONE. Executing on1
   must return the wrong canonical value3 rather than2.
3. Replace the final return move+1 by-1. Raw execution from temporary0
   must end at head-1; the endpoint observer must then reject specifically
   for the head1 requirement, not for an unrelated exception.
4. Execute malformed UNIT at head1 followed by RIGHT at2 directly through
   the raw baseline stepper, without canonical-input prevalidation. It must
   reach fail_pc and reject. Changing the entry default target to the ZERO
   path must instead accept and rewrite that same malformed body to1.
   This checks the actual default-guard behavior rather than a host parser.

The remaining controls observe that one actual call on3 uses25>18 steps,
and reject duplicate JSON keys, a numeric float token and a Boolean in a
proof-integer position. Nonfinite JSON tokens are also forbidden by the
decoder. Guard rejection and semantic endpoint failures are distinguished;
an arbitrary exception is never accepted as evidence for a control.

## Provenance and complete certificate protocol

CASES, SCHEMA and SOURCE-PINS have fixed literal SHA256 bindings. Before
candidate construction or execution, FILES.json must authenticate exactly
twelve core files: primary, oracle, emitter, those three metadata files and
the six retained source objects. Unexpected, duplicate or missing paths
fail. Source-pins byte equality is additionally checked. The shared emitter
also authenticates its three emission sources before using them.

SOURCE-PINS usage wording was corrected before any scientific first:
the old94776e... manifest is preserved separately, and the final bound
manifest is e08bed306ef62f5f05c5ae22969857c348b508cb0037f5310c01aaf9af145e73.
The correction distinguishes selected source-emission execution from the
unused source Machine/Tape runtime. CASES and SCHEMA stayed unchanged.

The certificate retains the entire emitted table, its complete canonical
hash, all sequential/carry rows, all eight control outcomes and the actual
sharp witness. Proof integers reject Boolean values; controls require real
Boolean outcomes. Duplicate keys, numeric floats and nonfinite tokens fail
before certificate acceptance. Default replay loads actual HERE/ORACLE.json;
--certificate PATH selects an actual external packet for tampering checks.
Every field is compared against a full canonical regeneration. Table/row
counts or summary flags alone cannot admit altered data. --emit PATH is
the explicit certificate-writing mode.

The complete original source program, original resource annotations and
the source's generic arithmetic theorem remain predecessor work. No
physical source Machine/Tape run, full producer/router/stack/codec admission,
κ change or selected-frontier update is claimed. Standard-library Python3.12
only, no assertion-based acceptance and no new dependency is required.

Resource forecast: bounded local lists, at most1024 sequential calls and
ten carry calls, small finite table copies and per-call cap100000. Expected
runtime is below30seconds and memory below128MiB, within root's180-second
first cap. These are unmeasured forecasts; failures must be preserved.

Before any scientific first, root's static review requested the two explicit
cost acceptance gates above. The unexecuted pre-gate version is preserved
as ORACLE-before-cost-gates.py. No source/case/schema/table or control was
changed, and this was not a response to a failed execution.
