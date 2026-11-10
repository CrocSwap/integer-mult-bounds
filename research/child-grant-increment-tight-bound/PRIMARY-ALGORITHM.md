# Primary method: actual increment table, sparse physical tapes

Status: static implementation written, **unexecuted**. No import, source
constructor, AST evaluation, compile, checker, interpreter or test has run
by this codewriter. Root alone seals and runs scientific firsts. I have not
read the oracle code, output or certificate.

## Authenticated shared construction

The frozen metadata hashes are CASES
`56065d4fc3a98c411cb068714eebc2c06d330976873093a28791193096b74cba`,
SCHEMA `ff29b35fef8e469938c6f0c7cbd0b17228e75e46fad6bdbab5e2ca2d262abed7`,
and final SOURCE-PINS
`e08bed306ef62f5f05c5ae22969857c348b508cb0037f5310c01aaf9af145e73`.
The earlier acquisition-usage pin is superseded before any first run; root
retains its original bytes separately. Six sources and exactly twelve FILES
core paths must authenticate before construction: both interpreters, root's
emitter, the three metadata files and six source inputs. Peer code is read
only as bytes for manifest authentication, never imported.

At execution the primary imports root's shared emitter by its explicit local
file location, friendly to isolated Python. emit_table() supplies the actual
source increment function's emission through the original assembler and
counter rewind. This shared construction is not an independent compiler.
The primary independently interprets its full returned table data and never
uses source Machine or Tape simulation. All table keys, instruction arities,
integer operands, branch cases/defaults, unit moves and bounded PCs validate;
the macro stop points to the wrapper HALT and the fail point to rejection.

## Independent sparse state and observation

Each tape is a dictionary of nonblank integer-position symbols. A write of
BLANK deletes one entry; a move changes one physical head by one. The two
heads and tape dictionaries are distinct. The active counter starts at head1
with LEFT0, its LSB-first body and RIGHT. Temporary zero has RIGHT at1.
Guards are MARK at-1 and UNIT at4096. Tape1 has its own fixed nonblank cells
and head-7 and must remain byte/head identical.

Each literal branch, write, move or goto costs one transition. Rejection is
observed as the actual rejection tag, not input prevalidation. Execution
stops BEFORE executing the wrapper HALT; no wrapper halt/caller loop is
included in the documented macro cost. Per-call visited positions start
with {1}; every active move includes its start and destination. Min/max
reset for each invocation. Sequential tape contents persist, while the PC
returns to the fixed macro entry and cumulative cost sums only macro steps.
A100000-step per-call cap makes an unexpected loop fail.

Every successful endpoint is decoded from the actual tape. It must equal
the expected increment and be canonical, with exact LEFT/body/RIGHT and no
extra or missing cells relative to the fixture's complete sparse dictionary.
That comparison includes both guards; the spectator dictionary/head is also
checked. This verifies the owned blank-growth fixture, not rejection of all
occupied hidden backing or a general allocator theorem.

## Frozen positive domains and certificate

The complete sequential profile contains1024 source-macro calls from
temporary zero, recording actual value, measured steps, cumulative measured
steps, final head and per-call min/max visited. Each measured cumulative
cost is compared to the source's already stated exact formula
`13k-7popcount(k)+5bit_length(k)` and the proposed15k homogeneous bound.
The actual k4 row must supply cumulative60, the sharp witness. Source owns
the exact formula; the written unbounded15k proof is a separate argument,
not extrapolation from these1024 cases.

Long-carry rows use the ten CASES widths through256 bits. Each starts from
the corresponding all-ones counter, and independently checks measured cost
7*bits+11, full counter endpoint, head, guards and spectator. These are
arbitrary-start scope controls, not applications of a from-zero total bound.

The common certificate retains the complete actual table, canonical table
SHA256, every sequential/carry row, all eight actual controls, provenance
and exact witness `{k:4,cost:60,uniform_coefficient:15}`. Default replay
regenerates the entire own certificate and compares canonical JSON bytes
to actual CERTIFICATE.json, or the explicit --certificate path. --emit is
an explicit write mode and emits only after every gate passes. Certificate
proof integers exclude booleans; Boolean true is allowed only at the exact
eight control fields. Duplicate keys, floats and nonfinite tokens reject.
Canonical comparison covers every field, not merely flags/table hashes.

## Real table mutations and strict controls

- Follow the actual entry's ZERO branch to its ONE write; replace the symbol
  with ZERO and run from2. The real program must fail the endpoint check.
- Follow the ONE/carry branch to its ZERO write; replace it with ONE and run
  from1. Require the actual wrong counter endpoint, not a parser rejection.
- Replace the final return move+1 with-1 and run from0. Require a head-return
  mismatch after actual execution.
- Give the raw interpreter UNIT at1 and RIGHT at2. The unmodified table must
  reach its exact fail PC and reject. Change only the entry default to the
  ZERO branch. The mutant must actually accept and produce canonical1.
  No counter input prevalidator can satisfy this control.
- Run the real macro from3 and require25 steps>18, disproving an18-per-call
  interpretation without contradicting the source's from-zero amortization.
- Require intended parser diagnostics for duplicate JSON keys and a numeric
  float, and an explicit proof-integer rejection for True.

Endpoint controls catch only the expected endpoint exception and diagnostic;
baseline default rejection requires the actual fail PC. Unrelated exceptions
cannot count as a passing semantic control. All gates are explicit, so -O
does not remove them.

## Proposed first and limits

Root may run isolated managed Python3.12 with `-I -B primary.py --emit <first
certificate path>` only after FILES and code/input seals exist. Expected
work is roughly tens of thousands of sparse dispatches for the1024 prefix
and a few thousand long-carry steps. Forecast resource use is below10seconds
and64MiB, not a measurement. First failures and any code correction must be
retained. No scientific execution has been used to tune this implementation.

This result concerns the isolated actual emitted increment. Full producer
quotient/product, imported converter correctness, linked router, consumers,
1000V/100V, stack/codec, all-size physical allocation and selected framework
assumptions remain outside. Retain thu-nmrc for source emission, David Arias
PR2776 for assembler/machine/rewind/counter, and the arithmetic/controller
predecessors. Binary-counter amortization is classical; the external literal
program verification and any sharp bound application are not a new generic
arithmetic theorem. Substantial OpenAI Codex assistance; no human/kernel or
frontier acceptance claim.
