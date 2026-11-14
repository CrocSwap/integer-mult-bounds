# Literal all-wire keys on the original thirteen-bit payload ABI

## 1. Exact claim and scope

Let h>=1, p>=h+1, N=2^h, 1<=s<=N and 0<=a<s. Write pi(i)=(i+a) mod s for i<s and pi(i)=i otherwise. This package constructs one fixed finite instruction graph with forward and inverse entry ports. On the typed physical interface below, it replaces the h allocated key words of every physical record i by pi(i), or by pi^-1(i) at inverse entry, in the original most-significant-key-bit-first format. It preserves every opaque payload bit, frame marker and exterior cell, returns all physical heads, clears the complete index/address and private work histories used by the invocation, and leaves the owned row body zero.

**The payload ABI is exactly one thirteen-bit codeword per record containing twelve arbitrary opaque payload bits.** The theorem is uniform in h,p,N and all admitted values; it is not a variable-payload-width theorem. Repeated or correlated payload values, including zero and 4095, are allowed. Keys are exclusively owned disposable workspace with valid initial codes. Their old values need not equal their physical positions for the key-production theorem. They are overwritten, not saved.

The exact all-wire controller removes B5's host `prepare_keys` loop, using unchanged B6 per-wire computation. It proves neither a complete CRT stage nor the selected multiplication theorem. Source acquisition, matching header production, ownership grants, current caller dispatch and the remaining radix/source orchestration retain their stated boundaries. No foundational assumption is declared discharged; no new kappa is claimed.

## 2. Pins and predecessors

Canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`. The exact B6 dependency is CubeJerry commit `4ccf407db96c7797dc3c83d90b033551f7d52c76`, package `research/literal-current-wire-row-controller`. Its graph has 10123 instructions on twenty physical roles, digest `f8f0bd615531c914efc110d8a9d5ce2fafa2b00c8a568bdbfb86bf24868a0ef7`. All 47 retained files are byte/blob pinned in `SOURCE-PINS.json`; the complete B6 notice and its inherited notices remain intact.

B6 derives from the published B5 point/caller package at CubeJerry `be17dd21af36a8b0546942299ebca7b1c83c4675`. B5's `caller.py:prepare_keys` is the exact seam lowered here. Its actual current source and payload providers originate in CrocSwap/integer-mult-bounds#7388 and #7352; canonical rotation formulas/child closure originate with Nick Petalas in CrocSwap/integer-mult-bounds#7504. The binary codewords and uniform literal stable radix are retained prior work, including #4982 and #5015. This package does not claim those formulas, primitives or sorting construction as new.

The key graph has 21135 locations, twenty-two fixed roles, and digest `8f5ae62b89de8308eb021920185269d884f07f625a5b3ee10b39f27aee5a393b`. Entries are forward 0 and inverse 444. There are 889 outer locations and two exact 10123-location B6 copies. All branch targets are statically relocated; all successful B6 halts become one fixed return jump, with all other instructions, tape operands and unsuccessful statuses unchanged. The copies express two finite return modes on the same owners, not two banks. `compile_pass()` has no h,p,s,a or payload argument.

## 3. Physical interface

Roles 0--13 are B6's fourteen granted blank private windows. Roles 14,15,16 are the actual H, S and A descriptors: respectively `L bits_p R`, `L bits_p R`, and `L bits_p | R`, with least-significant digit first. Role 17 is an inactive owned row frame `L bits_p R`; its initially arbitrary bits are disposable and become zero. Role 19 is `L 1^h R`. These roles enter at L and return there. The numeric value of H must equal the number h of unary width marks. Precision, complete boundaries and the B6 validity conditions are part of this typed interface, not deductions from digit shape alone. B6's point service additionally checks semantic domains along the actual execution.

Role 18 is a granted blank owned address window of h+2 cells; role 20 is a granted blank owned index window of h+2 cells. They enter and return at their window origins. The graph constructs their complete L/body/R frames and erases every such cell, including both markers, before successful exit. Previously retained larger extents remain allocated and counted. No owner is borrowed as disposable scratch without that permission.

Role 21 is the original binary payload owner, entering at the first bit of `<`. Fixed codewords are thirteen bits, least-significant bit first:

- `<` has integer code 5; `>` has code 6.
- Key digit 0 has code 2; digit 1 has code 3.
- Opaque record value t has code 4096+t, 0<=t<4096.

The frame contains `<`, exactly N records, then `>`. Every record consists of one payload codeword followed by h allocated key codewords in most-significant-key-bit-first order. Thus its length is L=13[2+N(h+1)] bits. The caller grants authority to overwrite those key cells and read/move over the full frame plus one right frontier cell. Opaque exteriors are unchanged. The frame may begin at an arbitrary physical offset; it need not be a global multiple of thirteen.

All twenty-two owners are distinct physical tapes/regions with their own head capabilities. The verifier's binder detects aliases; the graph does not implement dynamic allocation or infer separation from labels. Entry ownership, backing acquisition, typed source geometry and adequate windows remain explicit caller premises. The successful theorem does not assert rollback, complete cleanup or head restoration after malformed input or a rejected child. Bounded rejection controls illustrate detection, not a universal safe parser for arbitrary missing/interior markers.

`hardware.BitPort` is a fixed port alphabet rename between integer bits and the graph's symbols `0`,`1`, with one underlying bit read/write/unit move for each operation. It does not decode thirteen-bit words, inspect lengths or move a word at once. Other roles use the inherited fixed marker alphabet. The executable graph has only read-branch, write-constant, unit move, jump and halt instructions. All data-dependent loops and carry decisions are in those emitted instructions.

## 4. Complete record induction

Entry reads all thirteen bits of `<` and moves to the first record. It scans the unary width to construct `L 0^h R` on INDEX, while checking positive width, then returns width and index heads. ADDRESS is blank. No decoded h or N is an operand of the graph.

At the beginning of iteration i, 0<=i<N, the invariant is:

1. INDEX is the h-bit little-endian encoding of i; ADDRESS is blank.
2. PAYLOAD is at the first bit of physical record i. Earlier records have the required new keys; later keys have their original valid codes. All opaque payloads are unchanged.
3. All twenty-one marker heads are at their declared origins. B6 private windows are blank, prior history is retained, and the row is a valid owned frame.

The graph makes twelve unit moves across opaque bits, reads the payload tag 1 and makes one move to the first key word. It copies every INDEX digit into a newly constructed ADDRESS frame, returning both heads. It then executes one exact B6 forward/inverse entry. The B6 theorem gives destination pi(i) or pi^-1(i), with all its other fields/heads restored and row zero. This is the actual current physical address throughout all 2h-1 child queries, not a stale initial-index replacement inside a query.

Next it scans ADDRESS to its R marker, moves back to the highest digit, and emits digits high to low. For each digit it reads every bit of the old thirteen-bit key code: bit 0 may be either value, bit 1 must be one, and all remaining eleven bits must be zero. Only after that complete validation does it return thirteen positions and write/move over all thirteen output bits. Thus it preserves the exact original key encoding and reaches the next record. There is no uncharged symbolic key operation or runtime encoding converter.

ADDRESS is scanned forward, erased completely, and its head returns. INDEX increments by explicit binary carry and rewinds. Nonoverflow preserves the invariant for i+1. On overflow after i=N-1, all h index bits have become zero and the unique branch proceeds to the end check. Ordinary h-bit binary induction proves exactly N iterations without any host counter or decoded loop bound.

The graph checks all thirteen bits of `>` and returns to that word's start. It then scans aligned thirteen-bit words leftward. A fixed finite Boolean matcher reads all thirteen bits of each word, even after a mismatch. The only aligned code 5 in the valid frame is the initial `<`: payload codes have high tag one, key codes are 2 or 3, and the final code is 6. Therefore the scan returns to the actual original payload head and never inspects an exterior word. It then erases INDEX completely and halts. Every payload read, head movement and key write has been executed by the finite graph.

This induction covers arbitrary legal s,a, padding, payload values and initial valid key values. The h=1 case has two records and one row query per record; no special-case host branch is used.

## 5. Inverse keys versus inverse overwrites

The inverse entry writes pi^-1(i) at current physical position i. It does not undo the overwriting of arbitrary old keys. For a complete sorted roundtrip, assume the original physical-position key invariant: record i initially has key i. A forward key pass followed by the retained correct stable radix moves original record i to physical position pi(i), carrying its newly written key pi(i). The inverse pass at position j writes pi^-1(j); the second radix returns each original record to position i with key i. All opaque payloads and the original identity keys are restored exactly, even when payload values repeat. Frames, exterior bits, heads and local private retirement follow from the constituent contracts.

Without the original physical-position key invariant, those final keys are still i, and the arbitrary original keys need not return. The bounded test with original keys [3,2,1,0] ends with [0,1,2,3] while restoring payload values. This is an explicit limitation of the overwrite operation, not a claimed failure of the retained sorting algorithm.

## 6. Exact instruction bill

Charge one unit for every emitted instruction, including reads, writes, moves, jumps and halts. Successful B6 halt becomes one return jump, so its entire old instruction bill is unchanged. Let R_d(h,p,s,a,i) be the actual B6 instruction count in direction d on physical wire i. The new complete cost is exactly

`T_d = sum_(i=0)^(N-1) R_d(h,p,s,a,i) + N(156h+126) + 18h+203`.

The direction-independent added term follows from these emitted paths:

| Operation | Instructions |
| --- | ---: |
| Read/move across a fixed marker code | 26 |
| Construct INDEX from unary width, including origin checks and returns | 11h+17 |
| Copy INDEX to ADDRESS, with both complete head returns | 11h+15 |
| Skip twelve payload bits and check/move past tag | 14 |
| Validate and rewrite one thirteen-bit key code | 65 |
| Scan destination, emit h key words and return address head | 72h+5 |
| Erase one complete h-bit framed word and return | 7h+9 |
| Nonoverflow increment with c carried ones | 7c+9 |
| Final overflowing increment | 7h+8 |
| Full aligned payload return from `>` | 66N(h+1)+119 |

Across all N increments the number of carried ones is N-1, so their exact sum is 16N-8. Initial work is 11h+43. Each record excluding carry and B6 costs 90h+44, including the child-entry jump. Final marker, paid rewind, INDEX retirement and terminal halt add 66N(h+1)+7h+168. Summing gives the displayed exact term. These counts are proved from instructions; bounded execution checks them independently of varying payload/key values.

Every payload-port read/write/move is already included above. Its exact separate action count is

`B_payload = N(117h+66)+156`,

including exactly 13Nh key writes. The instruction count contains finite-control jumps as well; this action subcount must not be added again.

The full B6 envelope gives the explicit uniform bound

`T_d <= N{(2h-1)[1024(h+3)^2+128(p+h+3)]+14p+72h} + N(156h+126)+18h+203`.

This is O(N(h^3+hp)) for h>=1, p>=h+1, and includes all N complete B6 routes. It is not a runtime improvement inferred from eliminating a ROM. Relative to B6, this package executes the identical point and whole-route workload and supplies its formerly external all-wire key control. A comparison against retained ROM build/reuse must additionally price the full same-query workload, source work, storage and disposal under one tariff.

## 7. Complete historical union and ownership

At fixed h,p, B6's private windows are one p+2 interval, four h+3 intervals, one three-cell Boolean interval, one bit_length(h)+3 interval, and seven h+4 intervals. Their sum is `p+11h+bit_length(h)+48`. Every invocation retires those cells before the next route. Across all N(2h-1) point calls, count the union on each fixed role of its old retained interval with this same window, not a new allocation per call. Earlier larger histories and arbitrary opaque exteriors remain counted.

INDEX and ADDRESS each use h+2 cells and are retired completely. The four header/row frames use 4p+9 cells; unary width uses h+2. Thus if all marker windows are counted from their stated origins, the twenty-one marker roles have envelope

`5p+14h+bit_length(h)+63`.

For arbitrary prior history use the per-role unions instead of replacing old larger windows by this figure. The payload owner contributes its complete L-bit frame, its old retained history, and the visited right frontier cell. These are retained after return; none is treated as freed stock. No fresh role is acquired per record, query or sort key. Distinct physical owners, backing allocation and source access remain inherited capabilities, so this local bound is not a global stock theorem for suspended recursive ancestors.

## 8. Exact current-source join and limits

`join.py` authenticates B5 `caller.py` and substitutes only `prepare_keys`. The replacement binds the same private/header/width/index/address objects and the actual `record.tape`, selects one fixed entry, executes once and checks status. The unused historical `route_address` definition remains byte-for-byte in that caller; it is not called by the replacement. Source/header generation, numerical lease chronology, staging/commit, restoration and retained radix execution remain unchanged. These providers are explicitly credited.

The actual bounded joins execute both the exact #7388 four-tag source and its admitted modulus-three/left-two current-wire-sensitive variant, then full forward/sort/inverse/sort restoration. Each leg performs four routes and twelve point queries. The new outer graph adds 1991 instructions per leg; its payload subcount is 1356. The retained source and radix charges and all owner histories are checked against the exact B6 receipts.

The receipt reports a cost vector: encoded-source symbol actions, remaining outer marker actions, complete new literal key-pass instructions, remaining payload bit actions, and retained literal radix instructions. Marker actions within the new graph are subtracted from the old outer marker meter; its payload actions are likewise subtracted from the old payload-adapter remainder. Neither is double counted. No common all-caller symbol/bit tariff, free acquisition, source decoding or complete global bound is inferred from this vector.

The source caller still admits only its retained numerical domain; the generic local s=1 and s=N cases do not enlarge that source domain. Uniform multi-target CRT traversal, general payload widths, literal source/radix orchestration and the selected five foundational obligations remain open. The finite replays establish source binding and failure detection; the all-height claim rests on the explicit induction and invariant-preserving exact B6 embedding above.
