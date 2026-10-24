# Four-column binary input to actual fixed CRT repair

## Scope and successful boundary

This is a fixed-geometry finite-symbol instruction theorem with numeric binary input/output ports. It does not lower the entire repair machine to binary instructions. The six borrowed unary records encode (G,H,K,Y,J,B)=(2,2,6,8,2,0), and the borrowed ROM is a32-bit Boolean F with F[v]=F[v xor4], as in retained PR5105. Let M=4096, L=12, B=4LM=196608. For every address a=(u,t,y) and spectator back in {0,1,2,3}, choose an arbitrary12-bit payload v(a,back). Equal payloads are allowed.

The owned raw numeric tape holds the supplied raw-S permutation of these payloads in lexicographic (u,t,y,back,payloadbit) order, MSB first. The raw S contract acts on (u,t,y) and restores back. Raw cell0 is2, cells1..B are numeric0/1, and all remaining cells are4; its head is1. The fresh distinct output has one blank4 cell and head0. All seven borrowed lists are distinct from each other and both numeric backings. Their heads are0; all private roles are fresh blank lists at head0. Initial backing lengths, including blank tails, count toward K0. Rejection has no rollback guarantee.

The program consumes raw to all4 cells and head1, and returns numeric output `[2, ideal T-image bits, 4]` at head1, preserving every back column. All borrowed records/ROM remain byte-identical at head0. All four column tapes and all23 service-private roles return blank at head0, including their retained erased backing. Every finite-control register resets to None. This statement is conditional on the supplied raw-S endpoint; matching a producer fixture hash is not a proof that the whole raw producer/repair composition has been executed.

## Literal binary/record conversion

Demultiplexing installs `<` on each of four column tapes. A finite prefix tree reads exactly12 current numeric bits for one record, erases each consumed bit to4, and advances the same raw head by one. Its prefix and depth are encoded in the static program counter. Each of4096 leaves writes the constant alphabet symbol ('R',v) to the currently selected column and advances that column by one. No runtime integer accumulation, slice, gather, integer parsing, or numeric address operation occurs. The finite column register cycles through exactly four tape names. End-of-input is tested only before column0; an incomplete record/fiber rejects. At the end, each column receives `>` and is physically rewound to `<`. A physical scan returns raw to its2 marker, erases it, and moves back to head1.

After repair, each fiber reads one actual record from each column in order. The unchanged source `record` opcode requires ('R',v) with integer0<=v<4096; it does not admit a48-bit packed record. Twelve finite truth tables test membership of v in the2048-symbol sets having the corresponding bit set. Each result causes a charged numeric0/1 write and one-cell output move. Column records are erased as read. All four end markers are checked, erased, and the columns physically rewind to their `<` markers, which are also erased. Output gets numeric blank4 and physically returns to2, then moves to head1.

Induction on the prefix-tree depth proves that its leaf name is exactly the12 input bits. Induction on the four-column cycle proves column b contains precisely raw records at indices4a+b, in address order. The reverse induction on emitted bits and fibers proves reinterleaving in that same order. Since raw S restores the spectator back, each column separately satisfies the unchanged PR5105 input contract. Its theorem yields the T-image record order independently for each arbitrary payload column. Reinterleaving therefore yields the whole ideal binary endpoint. No distinctness or numeric interpretation of payloads is needed in the repair proof.

## Four actual calls and persistent ownership

Assembly inserts four complete copies of the actual8242-instruction PR5105 program. Only the constant role `data` is renamed to the corresponding column, static jump/branch targets are relocated, and its accepting halt becomes one jump to the next fixed continuation. `inline_check` compares every inserted instruction against the source program with exactly those transformations. It does not substitute a permutation oracle, call a Python repair function, or change the12-bit parser.

All four copies use the same11 outer work roles and12 key roles. No role bank is constructed between calls. The source theorem returns every service head to0, resets its registers, and erases all private roles, including the outer markers it installed. Consequently its postcondition is exactly the next copy's initial private-state premise. Other column tapes are untouched by each copy and remain at0. The seven borrowed headers/ROM are preserved. Induction over the four static copies proves reuse without resetting configuration heads for free.

The predecessor executor ordinarily creates zero heads. Our source-derived executor changes only that first assignment to accept the existing configuration-head map; the complete instruction dispatch body is unchanged. The AST of the original assignment is authenticated before replacement, and source hashes are checked before any assembly. NumericPort is an identity-preserving view of the actual numeric tape's bytearray: get/set use the requested current cell, and the executor's blank-extension operation appends numeric4 instead of its private-alphabet `_`. Heads updates the original numeric tape object's `.head` on each charged move. Neither backing is decoded or rebuilt. The same object identities are checked across the full run. The dictionary of heads and the program counter are emulator configuration, not runtime arithmetic operands. Diagnostic observers are read-only and their values never feed execution.

## Complete runtime instruction invoice

Each read, write, unit move, finite-register operation, branch, jump and halt costs one. Tuple/record symbols and the twelve bit tests belong to a fixed finite alphabet; these are not unit-cost unbounded integers. The large static tables are recorded separately below.

Let H be the number of1 bits in the raw stream. Repair permutes payload records and preserves H. Direct enumeration of the fixed adapter paths gives:

| Phase | Cell operations | Instructions |
|---|---:|---:|
| entry, demultiplex, marker close and raw cleanup | 5B+17M+33 | 11B+57M+2H+67 |
| reinterleave, all column cleanup and output return | 2B+117M+36 | 9B+48M+H+76 |
| total adapter | 7B+134M+69 | 20B+105M+3H+143 |

For each input bit the demux reads, erases and moves; a1 follows two extra control instructions. Each emitted1 follows one extra jump. The remaining terms count per-record writes, four-way dispatch, one end test per fiber, and full marker/rewind paths. The table includes initialization/reset of the four adapter registers and final halt. Source accepting halts are replaced one-for-one by jumps and retain their charge. The two-fiber test has B=96,H=39 and gives exactly1009 cell actions and2390 instructions, but the formulas follow the loop invariants and path enumeration, not extrapolation from that test.

For arbitrary admitted F and payloads, use the retained source bound

`T_service <= 6,294,271,835,487`.

The whole bound is

`T_total <= 4*T_service + 20B+105M+3H+143 <= 4*T_service + 23B+105M+143`.

The complete combined control graph has no control-only cycle; its checked longest path after cutting cell operations and halts is D=1212. Independently `T_total <= (D+1)(C_total+1)`. This includes the four initialization/final-reset intervals and their joins, rather than using a per-call factor across an unchecked join.

The canonical fixture uses the actual middle layer h3/modulus5/offsets[0,2,4,0]. Each original payload ordinal x=4a+back has label `(x xor ((x>>12)*1237)) &4095`. These expressions only construct test inputs and expected results. It has H=98304. The inherited canonical service count167388895 instructions/52900280 cells is payload-independent on valid records. Thus the predicted four-call fixture invoice is674212875 instructions and213526309 cells. The full verifier must independently observe those totals, all four complete service intervals, all2944 bad-address key calls in each column, and the entire196608-bit ideal endpoint.

## Static program, setup and complete retained backing

The combined program contains86646 instructions, not an implicit cost-free conversion oracle. Its explicit pack tree has4095 internal prefix states and4096 record leaves. Assembly examines48*4096 Boolean table entries for the four copies of the12 bit tests and retains98304 set members (twelve distinct2048-member tables, physically duplicated in the description). It copies/relocates4*8242 actual service instructions. Tables and code depend only on the fixed declared geometry, never on runtime input payloads. The typed RESULT includes the exact serialized description byte count, table cardinalities,609 finite registers and an abstract-shape upper bit allocation. Register shapes are a checked monotone fixed point: reads and atomic constants cost13 bits; fixed tuples reserve four tag bits and one separator plus the width of each field; fields are conservatively bounded by their parent width. A set constant, if assigned, reserves16+13 times its cardinality. Every assignment must fit its allocated width. The finite set predicates are explicit static tables, not runtime numeric arithmetic. Static assembly is the supplied Python indexed compiler, just as the inherited source compiler is; no physical on-tape compiler is asserted. Its generation, serialization size, finite table cardinality and fixed-control storage are recorded, separately from the executed tape-instruction bill. A caller requiring dynamic construction/installation must pay that explicit fixed setup; it is not absorbed into the runtime formula or claimed to have zero cost. Literal whole-program binary lowering, including this finite control, remains open.

Every service/private tape has retained extent at most K=M(L+1)+64=53312 cells: the three largest record/key tapes are bounded by N(L+1)+2 with N=2944, other outer tapes by M+2 or fixed unary lengths, and retained key service extents by the fixed header/word bounds. Each column has M+2 cells, also below K. All27 private/column tapes therefore fit27K retained cells even when erased; this deliberately loose bound includes coexistence of all four columns and the reusable service bank. Raw and output each retain B+2 numeric cells for the minimal fixture. Numeric alphabets need three bits per cell. The union has4096 record symbols, at most64 stencil tuple symbols, and fewer than64 marker/bit/header symbols, hence fewer than8192 symbols, so13 bits per service/column cell suffices; charging only12 payload bits would omit markers. With K0 the entire initially retained backing in BITS (three bits per numeric cell and13 bits per borrowed/private cell, including raw, fresh output, borrowed records and fresh blanks), a conservative new-backing bill is

`K0 + 3(B+2) + 13*27K` bits,

plus the fixed compiled-program description and finite-control registers. Initial blank tails remain in K0. Program/register storage is fixed but nonzero; it is listed separately rather than hidden among erased tapes. The verifier records every final retained length and checks the27 private extents; no tape is truncated or deallocated to fake erasure. The executor constructs no new tape during the four calls, only extends an existing backing with blank cells on a charged move.

## Open next questions and limits

The complete numeric raw producer and this persistent-head service still require a literal end-to-end run to claim that composed lifecycle, even when their canonical raw hashes match. Variable geometry, source ROM/descriptor preparation, dynamic program installation, binary lowering of the full record/stencil alphabet, production reservoir and complete E/native/precision/outer multiplication admission remain open. No new kappa or selected-frontier change is asserted. The independent finite oracle and controls corroborate the scoped induction; they are not human or kernel acceptance of the broader source theorem.

Credit: retained CRT contributions of Cinna Davis, Hiroki KUMAZAKI, ToikY, Jose Manuel, Ryanson Jonathan and Douglas Colkitt, and the PR4637/4795/5105 chain. Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
