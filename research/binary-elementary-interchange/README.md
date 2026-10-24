# Binary elementary interchange

This package closes the first open question in the literal elementary
interchange package: a fixed block encoding and an actual binary alignment
program. It lowers all 4,589 source instructions and all five entries to
58,608 binary instructions on the same 20 tapes. The program does not depend
on the input width. Runtime instructions contain no source executor,
numeric loop bound, allocator callback, or decoded geometry.

The proof below gives exact state, cost, and retained-storage refinement.
RESULT.json records 68 full entry comparisons over 16 sessions, including
eight independent payload columns, caller install, and a growing then
shrinking call history. The verifier also checks 153 local instruction cases,
three unused codewords, and seven failure controls. Finite checks support the
written proof; they do not replace it.

Run from the repository root with Python 3.12 and the standard library:

```sh
python3 -I -W error -B research/binary-elementary-interchange/verify.py
python3 -I -O -W error -B research/binary-elementary-interchange/verify.py
python3 -B scripts/research_package.py --package research/binary-elementary-interchange
```

The direct result is `PASS_BINARY_ELEMENTARY_INTERCHANGE`.
SOURCES.json pins every consumed source at
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. The verifier checks these bytes
before and after execution. A fresh test-only directory runs the unmodified
source machine; the binary runtime does not call it. The complete receipt
is compared with typed canonical JSON, including under optimized Python.

## Refinement theorem

Encode the five source symbols ZERO, ONE, LEFT, RIGHT, BLANK as 001, 010,
011, 100, 000, respectively. Each allocated source cell becomes three
allocated binary cells. A source head at h becomes a binary head at 3h.
Unallocated source cells are BLANK; unallocated binary cells are zero.
Thus both views have the same blank extension. Tape roles remain disjoint.

At a source instruction boundary, let the source and binary states obey
this relation. The lowered program has the following behavior.

1. A test reads all three bits through a fixed depth-three decision tree.
   Two unit moves advance the head. At each leaf, two unit moves restore
   it. Each of the five valid leaves jumps to the matching source successor.
   Each unused codeword halts with `rejected` after head restoration. A valid
   test uses three reads, four moves and one jump. It changes no tape cell.
2. A write stores all three bits. Two forward and two backward unit moves
   restore the head. A jump reaches the next source instruction. This uses
   three writes, four moves and one jump. If a write extends the source
   array to h+1 cells, the last binary write extends its array to 3(h+1).
   Every gap is zero. This also holds when the new symbol is BLANK.
3. A legal source unit move becomes three binary unit moves and one jump.
   It allocates no cells. Legal left moves cannot cross the binary origin.
4. A source jump becomes one binary jump. A source halt keeps its status.

These cases prove the state relation by induction at every source
instruction boundary. All tests have a bounded depth. Every inserted path
reaches a source successor or a halt. Compilation checks the complete
finite instruction alphabet and rejects control-only cycles. The actual
binary program has at most three consecutive jump instructions; its
control factor is four. No extra head or tape is required.

Suppose a terminating source entry has R reads, W writes, M moves, J jumps
and one halt. The binary entry has exactly

```text
reads  = 3R
writes = 3W
moves  = 4R + 4W + 3M
jumps  = R + W + M + J
steps  = 8R + 8W + 4M + J + 1 <= 8(R + W + M + J + 1).
```

Allocated length is exactly three times source allocated length at each
source boundary. During a microprogram it does not exceed the length at
the next source boundary. Reads and moves do not allocate. All three bit
writes are charged even for zero. Therefore erased backing remains in the
account. For every valid sequence of calls, the binary retained-storage
history is three times the corresponding source history. This is a
relative theorem; it does not supply a new absolute source-space bound.

Apply the theorem to the source program's valid domain: H >= 0,
A,G,S >= 1, V = A*4^H*G*S, canonical encoded descriptors and disjoint roles.
The source proof supplies the interchange permutation and five-entry
lifecycle. The binary program inherits those properties on encoded states.
If L = H + bit_length(H) + bit_length(A) + bit_length(G) + bit_length(S) + 8,
with bit_length(0) taken as one, its complete init/run/consume/close session
cost is at most 2^23*(H+1)*(V+1)*(L+1)^2. This follows from the source bound
2^20*(H+1)*(V+1)*(L+1)^2 and the instruction factor eight. Caller install
has the exact per-entry factor above; the quoted session excludes install.

## Scope and limits

This is a finite program plus a written uniform representation proof.
It uses the source program's all-width correctness proof as a premise.
The finite replay here has maximum H=3 and V=64. It does not repeat the
predecessor's 196,608-cell source fixture or claim a new all-size acceptance.
The proof applies to all valid widths because its induction is per opcode.

Encoded descriptors and payloads are supplied at the boundary. The Python
fixture encoder is not a free runtime adapter. A caller must provide encoded
data directly or pay for a separate codec, its heads, storage and disposal.
Unused codewords are rejected only when a test reads them; this is not a
global input validator or an error rollback guarantee. State refinement
does not cover a source move that crosses the origin.

No selected file, supplier, physical stock, native operator, precision claim,
ROM producer, whole raw/repair caller, outer recovery proof or complete
kappa calculation changes. Selected kappa remains 60403/20000000. There is
no independent human or proof-kernel acceptance claim.

## Open next questions

- Integrate the encoded callee with the complete raw/repair caller. Identify
  the representation of every port and pay every codec and lifecycle cost.
- Apply a source retained-backing theorem to obtain an absolute binary
  storage grant. Include all old erased arrays and varying call histories.
- Independently check the source all-width proof and this instruction
  refinement. A finite execution receipt alone cannot discharge either.

## Attribution

JoyboyBrian supplied the literal five-symbol program, lifecycle, source
proof and binary-lowering handoff in PR #5188. Its source notices retain
Jose Manuel's ordinary wrapper, the PR #2809 and PR #2753 stream/cardinality
authors, Cinna Davis, Hiroki KUMAZAKI and Douglas Colkitt. This package does
not modify those sources. PR #5286 is related retained-backing work; it is
not a consumed proof premise here. Ali Romman prepared this refinement
with substantial OpenAI Codex assistance in proof, code and verification.
Apache-2.0.
