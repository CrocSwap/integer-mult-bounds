# A literal binary pass at the CRT repair consumer

JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.

## Boundary and quantified claim

Take any n>=0 records `(v_i,k_i)` with `0<=v_i<4096` and nonempty finite
binary key strings k_i. Set K=sum |k_i| and D=n+K. The bad tape is
`< (R,v_1) k_1 ... (R,v_n) k_n >`, followed by blank cells. Each bucket
has just the permanent `<` at cell zero and is otherwise blank. All three
heads start at cell zero. Source symbols use the exact 4104-symbol alphabet
of #4982; in particular, the other eight symbols are `_ L 0 1 R < > =`.
The physical input consists of those symbols' thirteen-bit predecessor
codewords, source cell j at physical cells 13j..13j+12. Codes 8..4095 are
unused and excluded from this entry contract. Misaligned heads, dirty
buckets, missing/duplicate outer markers and arbitrary unused binary codewords are
not admitted inputs. Finite control may initially be arbitrary bits.

The emitted fixed program returns the stable concatenation of the records
with last key bit zero and then those with last key bit one. Each output
key is rotated from a_1...a_l to a_l a_1...a_(l-1). The payload bits are
opaque and unchanged. The bad tape has exactly the same occupied extent;
its final END stays in source cell D+1. Both buckets become blank except
for their permanent `<`. All heads and all finite-control bits return to
zero. There are three physical tape roles, 72 one-bit control registers,
180 source instructions and 3885 static binary instructions. This is one
fixed program for all n and key lengths, not one program per test input.

For a finite stream with exactly one LEFT (at cell zero), exactly one
final END, and other symbols in the declared alphabet, validation rejects
any malformed record/key structure before
writing output. It returns the bad head and clears finite control, while
bad and the empty buckets remain unchanged. Missing/duplicate LEFT or END and a nonzero initial head are outside
the contract, not promised rejection cases. Unique LEFT is essential to
the rewind invariant: an interior LEFT would stop a rejection rewind early.

## Stable symbolic algorithm

`radix.py` assembles the source algorithm in the unchanged #4752 Builder.
The eight reserved-symbol comparisons recognize a record because the
entry alphabet is precisely the eight reserved symbols plus 4096 records.
No payload value is inspected or used as an address. First validate every
record, followed by at least one key bit, and the final END; all validation
reads only bad. Rewind bad before starting the output. Thus failure cannot
partially change either stream.

During partition the main invariant is that bad points to the next record
or END, the completed records have appeared in order in their chosen
buckets, and both bucket heads point to the next unused cell. Hold the
payload in one finite register. Walk to the next record/END, step back to
the final key bit, save it, and walk back across the key to its payload.
The key is nonempty, so both scans terminate without crossing LEFT.
Append payload and final bit to its chosen bucket. Hold the first original
key bit; before each further key bit is consumed, append the held bit and
replace it by the current bit. On the first nonbit, the final held bit is
the original final key bit and is deliberately not appended again. This
appends precisely the other l-1 bits and returns bad to the next payload.
This also covers l=1: the inner append loop has no iteration.

The invariant gives stable order within each bucket, including repeated
keys and repeated payloads. Write an END on each bucket, rewind, and copy
bucket zero followed by bucket one to bad. Exactly D data cells are copied;
write the final END in D+1, then rewind all three. Erase bucket data and
END, return their heads, preserve permanent LEFT. This proves the endpoint
by induction on records and cells. It is the same endpoint as the retained
`bridge.one_pass`, although validation and fixed-control branching have
additional paid work. No assertion about an identical event trace is made.

If all keys have length L>=1, repeat this same program L times on the same
tapes. Pass j stably sorts on original bit L-j+1 and rotates it to the
front. Induction is the standard stable LSD radix invariant; after L
passes key orientation is restored and order is stable lexicographic
ascending on the original keys. Buckets and control satisfy the next
invocation's entry contract after each pass. The n=0 case also returns.

## Full source-control and bit-action bill

A source instruction is one read, write, unit symbol-head move, finite
assignment/copy, equality, branch, jump or halt. There is no host integer
key, length, address lookup, source-cell dictionary access or sort inside
the emitted program. The assembler sees only the predecessor Builder;
it receives no record, parameter n or L. Tape dictionaries, PC indices
and counters in the emulator are observer metadata.

For the 180-instruction source program, call a transfer backward when its
next PC is no greater than its current PC. Between two backward transfers
the PC strictly increases, so at most 180 instructions execute. The
following are **all** backward transfers on a legal invocation. Bucket
stream lengths D0,D1 satisfy D0+D1=D. Each rewind counts a jump for each
source-cell step left, including the final END position.

| Control section | Backward transfers |
|---|---:|
| Validation key/next-record branches | K |
| Validation rewind from END | D+1 |
| Right and left key scans | 2K |
| Key rotation append loops | K-n |
| Return to next record | n |
| First three rewinds | 2D+3 |
| Bucket copies | D |
| Second three rewinds | 2D+3 |
| Forward bucket erasure loops | D |
| Final bucket rewinds | D+2 |

Summing gives exactly B=4K+8D+9, including B=9 for the empty stream.
The rejection rewind is unreachable on a legal input; it is not omitted
from the program. Therefore source execution T satisfies

`T <= 180*(B+1) = 180*(8n+12K+10)`.

This bound is constructive and covers validation, comparisons, both
choices of bucket, marker writes, all explicit branches/jumps, merge,
erasure and return. It is deliberately conservative because increasing
PC segments often skip instructions. No measured runtime is used to
prove it. The verifier checks the independent source execution at every
compiled instruction boundary in three fixtures and corroborates the
exact B formula there.

Use #4982's unchanged `compile_program(..., lifecycle=True)` and bit
machine. Its fourteen-bit tagged registers distinguish symbols from
Booleans. Each core source instruction expands to at most 43 actions:
single-bit read/write, unit physical head move, one-bit assignment/copy,
Boolean operation, branch, jump or halt. The exact local simulation is
retained in its pinned PROOF.md: writes set every one of thirteen bits;
read/write returns to the aligned cell start; a source move is thirteen
unit physical moves; full tagged equality handles destination aliasing.
Our source uses only read/write/move/copy/eq/branch/jump/halt and its
private names avoid `$different` and `$xor`. Every reachable branch
operand is the Boolean result of equality. Hence its induction applies
for every input here, including arbitrary initially dirty finite control.

Initialization and the reached halt suffix each assign all 72 one-bit
control registers. These 144 actions are paid, not emulator allocation.
Consequently one complete pass costs at most

`43*180*(8n+12K+10)+144 = 7740*(8n+12K+10)+144`

literal actions. For fixed width L this is
`7740*(n*(12L+8)+10)+144`. L repeated passes cost at most L times that
quantity. This is a sequential finite-tape bit program bill, not merely a
symbol-cell meter. Static code construction and initial serialization
are outside the invocation contract. They have not become free globally.

## Actual caller and remaining ledger

The actual fixture retains #4982's original `bridge.split`, actual raw
middle-layer payloads/mask, two complete bit-level key executions and
continuation to the third marked address. The predecessor fixture closes
the captured completed prefix with END as explicit verifier setup. Our
adapter replaces its subsequent `bridge.one_pass` call, receiving the
**same** `bad.raw`, `b0.raw`, `b1.raw` objects. It neither decodes a key
into a program parameter nor materializes a replacement tape. The
original caller's postchecks inspect payloads, rotated keys and heads;
we also check bucket and control erasure. The enclosing split's symbol
facades remain an unlowered outer boundary. This demonstrates one actual
local connection, not complete repair or production geometry admission.

| Obligation | Status |
|---|---|
| Stable consumer action and cleanup for all valid finite encoded streams | proved here; explicit finite upper bound |
| Inherited thirteen-bit compiler's block simulation | retained pinned premise; observer corroboration here |
| Original two key calls and continuation before new consumer | executed bounded fixture, predecessor source proof retained |
| Full 2944-hole layer and complete sort/reinsert | unrun; not discharged by the captured prefix |
| Split/reinsert binary control, uniform geometry and descriptor/ROM construction | unknown here |
| Physical tape placement, whole CRT tariff E(p,ell), compiler creation cost and all-size supplier transfer | unknown here |

No new kappa, selected supplier, complete multiplication theorem, native
implementation or formal proof-kernel acceptance follows. The declared
family decision is narrow: close this explicit consumer boundary and
stop, rather than authorize an automatic full-repair expansion.
