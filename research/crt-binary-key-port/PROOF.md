# Literal binary key at the retained repair port

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Object and claim

This lowers the actual `service.py` program of #4795 (head
`4e4cf7e47f3fc1c40e775d84fb2e7cd2603658cd`). For each fixed J in {0,1,2},
its domain remains u2,t2,y8, every 12-bit address, and a supplied 32-bit F
independent of yJ. The source proof gives the key T(S^-1(q)), three current-y
queries, borrowed counter/ROM preservation, private erasure/head return,
append of twelve source bit symbols and at most 3,287,110 source instructions.
Those source semantics are a retained premise; this package proves their
literal binary realization and tests its actual caller interface.

There are the same fifteen physical tapes. Each source cell j is represented
by bits 13j through 13j+12, little-endian; each source head j corresponds to
physical head 13j. The stream may start at any source-cell boundary after an
arbitrary legal payload/key prefix. Its twelve-symbol append advances the
physical head **156** bits, not twelve. No input conversion occurs at a call.
Packet construction/encoding and ROM supply are external entry premises.

The complete program uses only one-bit reads/writes, unit physical head
moves, one-bit assignments/copies, XOR (including a literal-bit operand),
AND, OR, NOT, Boolean branch, jump and halt. Each executed instruction costs
one action. It is the executable program, not a multiplication of an old
receipt. A finite instruction transition includes its sequencing; explicit
branches/jumps are charged instructions as well.

## Encoding, including opaque payloads and finite control

The source symbols have these thirteen-bit integer codes:

| Symbol | blank `_` | `L` | `0` | `1` | `R` | `<` | `>` | `=` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Code | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |

The opaque record `('R',v)` has code 4096+v, for 0<=v<4096. Thus all 4,104
symbols are distinct, and the all-zero physical background represents blank.
Codes 8..4095 are unused. The port theorem assumes correctly encoded finite
records and aligned heads; it is not an arbitrary-bit-string admission theorem.
`=` is a source finite-control value; including it in the common alphabet is
harmless even though the retained key program does not write it to a tape.

Each source register uses fourteen one-bit registers. A symbol is its 13-bit
code followed by tag zero. Boolean false/true has low bit zero/one, twelve
further zeros, and tag one. This distinguishes Boolean true from symbol `L`
and Boolean false from blank. The source uses finite-control equality results
as Boolean branch conditions; tape values and `0`/`1` arithmetic are symbols.
Dropping the tag makes equality of true and L incorrect even though both have
low code one. Registers and code locations have fixed finite cardinality.
The compiled full service has 492 one-bit registers, independent of address,
source ROM contents or stream-prefix length.

Complete service compilation emits 492 initial zero assignments and another
492 before each reachable halt. Only one halt is reached per invocation, so
**984 lifecycle actions** are executed. The verifier deliberately starts the
emulator registers dirty; input initialization and final erasure are paid.
No free host allocation/reset is needed in the claimed machine. Primitive
block tests omit this wrapper to supply arbitrary initial register values.

## Per-block simulation

Take any source state at an instruction boundary, with tape cells/heads and
initialized register operands represented as above. The following invariant
holds after each corresponding nonterminal binary block: all source-visible cells,
registers and heads have exactly the indicated representation, and the binary
PC is the relocated address of the next source instruction. Compiler-private
comparison bits are not source-visible and are erased by the final lifecycle.

| Source instruction | Binary implementation | Core actions |
| --- | --- | ---: |
| read | 13 single-bit reads, 12 moves right and 12 left, set the symbol tag to zero | 38 |
| write / write_reg | 13 writes and the same 24 moves; return to cell start | 37 |
| move ±1 | 13 unit moves in the same direction | 13 |
| set / copy | fourteen one-bit assignments/copies | 14 |
| eq / eq_reg | zero accumulator; 14 XOR+OR pairs; 13 Boolean output-tag/upper-bit assignments; NOT accumulator to low output bit | 43 |
| xorbit / andbit / orbit | one Boolean gate on low operand bits, then 13 assignments to the remaining `0`/`1` symbol-code bits | 14 |
| branch / jump / halt | one corresponding fixed-control operation | 1 |

Read/write move only inside one encoded cell before returning, so they cannot
read or overwrite neighboring payloads. Write writes all thirteen bits even
when the old cell is dirty. The source data bits are codes two and three,
which differ exactly in their low bit; the other code bits and tag are restored
by the bit-arithmetic block. It computes the output low bit before assigning
upper bits, so source/destination aliasing is safe.

For equality, after bit i the scratch accumulator is the OR of all differences
through i. Negating its final value is exactly equality of the full tagged
words. All comparisons finish before writing destination bits, so aliasing a
source and destination register is also safe. The reserved scratch names do
not occur in the authenticated source program. Copying a word to itself is
safe. The source's reachable branch operands are Booleans; their low bit is
therefore the correct decision, and branch targets are statically relocated.

At halt no source instruction remains; the source-visible register correspondence
is replaced by the promised all-zero control endpoint. Source halt has a separate lifecycle suffix of 492 assignments and the halt
itself; the table's one-action halt is its core, not a claim that cleanup is
free. The initial 492 assignments precede the first source block. Labels are
relocated after these expansions, including jumps across either halt suffix.

Induction on the actual source execution proves the simulation, termination,
key and ownership result. In particular, all cleared source private cells
become thirteen zero bits, borrowed cells are unchanged, private/counter/ROM
heads return to zero and the protected stream prefix is unchanged. All finite
control bits also finish zero. This argument applies to every legal source
input; testing a finite subset is corroboration, not the induction hypothesis.
For a framed input on which the source rejects and cleans up, the same
simulation gives rejection/cleanup, without claiming the legal-input time
bound for arbitrary malformed packets.

## Complete bound

Let T be a legal #4795 source execution length, including its one halt, and
let R=492. Every core block costs at most 43, and initialization/termination
cost 2R. Therefore

`T_binary <= 43*T + 2R <= 43*3,287,110 + 984 = 141,346,714`.

This includes every executed bit action and Boolean/control instruction,
current-state descriptor/header work, all three ROM traversals, full carry
arithmetic, append, private erasure, physical head return and finite-control
initialization/erasure. No asymptotic compiler bound is asserted: the compiler
emits one of three fixed finite programs (106,583 / 106,713 / 106,843 bit
instructions). Its static program size contains two halt cleanup paths; its
runtime takes only one. The sampled counts near 0.9 million actions/key are
not used to prove the upper bound.

The interpreter's PC, register-number lookup, sparse tape dictionary indices,
head coordinates and action census are emulator metadata. `Machine.step`
never exposes a coordinate, tape length, decoded word or count to the program.
Runtime values read from tapes or registers are individual bits. There is no
symbol decoder or original key evaluator inside the binary executor. The
source is compiled before any address/ROM/payload is supplied. All data paths
in the executable are the stated primitive bit operations.

## Caller-bound evidence and limits

The verifier constructs the same middle-layer source ROM, raw compact-word
payload stream and original guard mask as the retained source caller. The
unchanged `bridge.split` runs on facades whose **only storage is physical bit
tapes**. Facade reads decode symbols for the unlowered outer controller; facade
writes/moves perform the corresponding bit operations. This outer decoding
is an explicit boundary, not part of the binary key program or its tariff.

At the original `evaluate_key(counter,bad,...)` call, the new adapter gives
`Machine` those same underlying tapes, without reading/converting an address
into an executor parameter or copying in/out a computed key. Observer-only
address decoding checks the source reference, but never feeds the executor.
The first two actual marked-hole calls return, and the original split then
continues to the third hole at address two. This checks that both 156-bit
advances and the next opaque payload write obey the original caller contract.
The verifier interrupts before executing that third key, not after a full
layer. It then closes the captured two-completed-pair prefix with an END marker
as explicit verifier setup and passes it to the unchanged original `one_pass`.
Its radix split preserves the captured payloads, rotates their actual returned
keys correctly and returns the consumer heads. Closing/projecting the prefix
is not claimed to be the full split/sort/reinsert algorithm.

The first two caller addresses are simple keys; a separate transported parity
case at q=892 checks every one of 44,340 source-instruction boundaries, all
physical head scales, every written block and every defined register result.
Three further complete binary runs cover nontrivial carry/boundary behavior
and all retained targets. Primitive checks cover all 4,104 encodings and their
read/dirty-write blocks, plus 172 equality/Boolean/alias cases. Mutants expose
short physical moves, incorrect Boolean tagging, a dirty borrowed head and
omitted finite-control erasure, and a colliding marker code. Three framed malformed
packets also reject with complete physical/control cleanup. These are new execution/representation checks,
not a replay of #4795's 376-case census.

Not supplied: a full 2,944-call binary layer, a literal binary lowering or full
control tariff for the outer producer/scanner/sort/reinsert, physical creation
of raw S or the source ROM, encoded variable-width CRT parameters, uniform
compiler/constructor cost, or complete E(p,ell). No multiplication theorem or
new kappa follows. The fixed-geometry source proof and its predecessor credits
remain explicit. Other current reservoir/layout or stopped-recursion results
address different obligations.
