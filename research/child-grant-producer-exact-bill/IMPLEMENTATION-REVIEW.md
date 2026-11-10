# Post-first static implementation review

**PASS for the declared finite execution/certificate scope; no blocking
discrepancy found.** This review follows the separately sealed written producer
proof and pre-first emitter review. I read both implementations, emitter,
CASES and retained certificate data only after the firsts. I ran no scientific
program, source import, compilation or simulator and made no code edits.
Only static byte comparison and hashing supplemented the source reading.

Reviewed SHA256 identities:

- primary.py: `10845e839163b147e810c9583a172b12e9b1c788fc504e1f32b1a1f67e48ea30`
- oracle.py: `625adc3af46b16f0a2d79a3092dc5e48aa49e984f920d32eaf4e8def210697f1`
- emitter.py: `e68f68d3937a35a0ec558ab9f06aeb24be4284344848b038764f827bcc7bf6a2`

The retained CERTIFICATE.json and ORACLE.json are byte-identical, both SHA256
`4ea1cffdc2d4a3b8e443daec4d397e7adbedddae896d18c1e51171c0fa6a5800`.
The coordinator reports agreement of all261 case rows and ten controls, plus
four normal/optimized actual-certificate passes. Those executions were not
rerun here; later external corruption/cold/hosted outcomes need their own receipts.

## Construction and literal semantics

Both engines authenticate frozen CASES/SCHEMA/SOURCE-PINS and the exact
thirteen-file core closure before emission. This includes both engines,
emitter, the four executable source dependencies and three inert source texts.
The shared emitter authenticates the source bytes and invokes the actual
producer.build only for L=2,3,4,7. A,H,R remain runtime tape data. Source
Machine/Tape execution, router building, linked_split and delivered consumers
are not invoked. This is explicitly shared candidate construction, not two
independent end-to-end source constructors.

Primary's sparse dictionaries and oracle's dense lists implement their own
dispatch loops. They inspect scanned symbols, follow explicit branch cases
or default, perform actual writes/unit moves/gotos and raise at source REJECT.
Both increment their step total before dispatching HALT and return only after
that charge. There is no S7-style stop-before-wrapper boundary here. Thus the
291-step smallest witness includes the producer's real success HALT.

Primary checks observed steps against the independent exact formula after
execution; it does not use that formula to generate step counts. Oracle
independently counts dispatches and checks the60 envelope rather than deriving
steps from the formula. Both observe visited-address sets, including initial
heads and every accessed/moved-to address, and record nine min/max/count triples.
They check the10(S+K) envelope. Neither adds a separate executed equality guard
against the symbolic exact visited-expression: that equality is supplied by
the written proof and inspectable complete visit records, not an extra test.

## Endpoint, heads, erasure and guards

Fixtures create nine distinct tapes: raw binary A,H,R at heads1 and blank
output/work origins at heads0. Each tape has guards MARK at-1 and UNIT at8192.
The declared cases keep valid growth far inside that extent. Observers do not
create q or HR on an executed tape; host arithmetic is used only to check the
already completed result. All source data-dependent arithmetic is performed
by the emitted instructions.

Primary compares the entire preserved input maps/heads and output maps with
their exact packets. Oracle snapshots complete dense input arrays before
execution, compares them afterward, parses the actual output digits, verifies
positive canonical high ONE/RIGHT/LEFT and rejects extra nonblank backing.
Both require output heads1, all four scratch heads0 and scratch containing
only untouched external guards. Thus scratch markers and bodies must really
be erased; a zero numeric value or correct outputs alone cannot pass.
All near/far guards are preserved. Those guards are outside the owned growth
region; they do not imply preservation of occupied cells inside a required
growth extent. Fixture setup and untouched backing are outside the runtime bill.

## Ten controls and complete retained-certificate comparison

Four controls change instructions in the actual emitted table and run the
respective literal engine. Changing the quotient or product ZERO-write site
causes a canonical2 instead of the intended3 in the selected fixture. Oracle
checks that actual wrong value; primary requires the intended endpoint failure.
Changing the last WORK erase to LEFT leaves a physical marker at0. Reversing
the last input0 return move leaves its head at-1. Their observers reject the
specific erasure/head faults rather than merely comparing changed table bytes.

Nondivisible A, a redundant high-zero descriptor and occupied WORK origin
are raw malformed fixtures required to reach source REJECT. Primary additionally
checks the source reason string; oracle checks the explicit reject row. These
controls do not promise rollback or cleanup after rejection. Duplicate-key,
float and Boolean-as-proof-integer controls complete the ten; both decoders
also reject nonfinite JSON constants. Explicit exceptions remain active under-O.

Incoming certificates have exact top-level and row keys, lengths, integer
types excluding booleans, table operands/targets, control keys and true Boolean
outcomes checked. The complete actual table collection and digest,261 ordered
case rows, all outputs/heads/visits/endpoint digests, bounds and small witness
are then compared canonically with fresh regeneration. Canonical string
comparison avoids bool/int equality accidents and does not ignore altered
scientific fields. Oracle's lighter structural checks on some digest/order
fields are backed by that complete equality, not accepted as substitutes for it.
Missing or mutated retained certificate data cannot pass merely by preserving
a summary flag or updating its claimed hash.

## Limits and verdict

The root proof's exact ledger and safe60(S+K) bound are consistent with the
reviewed code's counted object and smallest291/30 witness. The finite261-case
plan corroborates the literal program; the all-L/all-input result comes from
the separately reviewed invariants and count inequalities, not finite agreement.
No generic optimality of60, complete linked/consumer1000V/100V bill, supplier
price/native implementation, allocator/stock/precision/compiler/outer admission
or selected-frontier/kappa change follows. All five framework assumptions remain.

No code correction is requested for this bounded contract. Source producer,
counter/machine and retained lineage keep thu-nmrc, David Arias and predecessor
credit. This post-seal source-aware AI static review used substantial OpenAI
Codex assistance; it is not independent human or proof-kernel acceptance.
Apache-2.0.
