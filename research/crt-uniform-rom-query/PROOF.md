# Uniform encoded row-ROM query

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped proof for `machine.py`, not a proof of the CRT compiler or its
complete `E(p,ell)` allowance. The finite replay is a check on this proof's
implementation, not the reason its quantified statements hold.

## Interface and quantified proposition

There are ten semi-infinite tapes, all heads initially at cell zero. Borrowed
roles are `h,s,offset,target,rom`; owned roles are `out,count,col,row,limit`.
Owned tapes are initially blank. A borrowed record has exactly one left marker
`L` at zero, a finite payload of `0,1` symbols, then `R` and blank cells. This
framing is the input contract, not an admission check for arbitrary unframed
infinite tapes. Malformed finite parameter payloads are also checked in the
replay, provided they contain no additional `L` or `R` markers.

Integers use little-endian binary with no most-significant zero, except that
zero is the single digit `0`. Let

- `h >= 1`, `2 <= s <= 2^h`, `0 <= offset < s`, `0 <= target < 2^h`;
- `M = s*2^h`, and let the ROM payload be any word of exactly `M` bits;
- `b = bit_length(s)` and `w = h+b+2` (so `w >= 5`).

The *same* assembled program accepts, returns the bit at zero-based ROM index
`offset*2^h+target` in the owned record `L bit R`, preserves all borrowed cells,
erases all four scratch tapes including their markers, and returns all ten heads
to zero. Its complete instruction count is at most

`T <= 512*(M+1)*w^2`.

A fixed three-bit encoding of the five tape symbols gives the binary-action
upper bound

`T_binary <= 65536*(M+1)*(h+log2(s)+1)^2`.

The executed object is the marker-alphabet program. The binary bound is the
explicit local lowering proved below, not a measured binary emulator result.

Incorrect finite parameter records, out-of-range parameters, non-bit ROM
payloads, and short/long ROMs are rejected with owned tapes blank and all heads
returned. The displayed bound is for legal parameters and a correctly sized ROM;
there is deliberately no bound independent of the length of malformed headers.
For example, an arbitrarily long noncanonical header cannot be validated for a
cost depending only on its small decoded value.

## Fixed program and finite control

`assemble()` takes no arguments. Its only Python loops range over a fixed list
of role names. It always emits the same 752 instructions and fixed jump targets.
The 16 registers hold a current symbol, a comparison result, or a Boolean. None
holds an unbounded integer. The instruction set has reads, writes, unit moves,
finite-alphabet equality, Boolean branch, finite-register set/copy, jump and
halt. Every one of these instructions contributes one to the reported census;
equality and its subsequent branch are separate instructions.

The host interpreter's `pc`, tape-head coordinates, dictionary keys and census
are simulation metadata. The program has no instruction to inspect those
integers, array lengths, the trace, or a host-decoded input value. A head is used
only for its current cell. Branches use only a Boolean equality result. The
observer watchdog can abort a test; it cannot select an answer or certify a
partly executed query. Thus the program and the proof are independent of the
watchdog, interpreter memory allocation, Python timing and test-oracle decoding.

## Functional invariants and termination

`canonical` scans to `R`, requires at least one binary digit, and remembers
whether there was more than one digit. The final digit must be `1` unless there
was just one digit. These are finite flags. `is_zero(h)` rejects zero, and
canonical `s` has value at least two exactly when it has at least two digits.
All these scans return their head.

`copy_word` copies the complete encoded `h` to `count`, including its fixed
width. In `width_loop`, `count` is tested for zero and decremented bitwise once
per iteration. Leading zeroes created in this *private* countdown are retained.
The decrement routine is called only on a positive value: change low zeroes to
ones, change the first one to zero, and rewind. Hence it terminates without
crossing `R`, and there are **exactly h iterations**, despite h arriving in
binary. Each iteration appends one zero to `col` and `limit`. On termination,
`col` is an h-bit zero and `limit` is h zeroes followed by one, the encoding of
`2^h`. No host-sized h controls allocation or this loop.

`compare` scans both words from their least-significant digits, pads a word by
zero after its `R`, and replaces its comparison flag whenever the current digits
differ. The highest differing bit determines unsigned order. It stops when both
heads are at `R`, then rewinds both. Thus the three comparisons establish
`s <= 2^h`, `offset < s`, and `target < 2^h` without decoding a parameter. The
row counter is initialized to exactly b zeroes by traversing `s`.

Before ROM position j, the invariant is

`row = floor(j/2^h)`, `col = j mod 2^h`.

The h-bit column increment returns a carry exactly on wraparound. On carry,
the b-bit row increment runs. Until j=M, row <= s < 2^b, so row never overflows.
The endpoint **s=2^h** is included: then **b=h+1**, leaving room for the terminal
row value s. This extra bit is not discarded.

Before consuming a ROM bit, the program rejects if row=s. At each legal
position it compares row with offset and col with target; their simultaneous
match occurs exactly once, at j=offset*2^h+target. Only that bit is written to
`out`; `found` rejects an unexpected second match. At `R`, col must be zero,
row must equal s and `found` must be set. Thus short and long ROMs are rejected,
and the accepted output is the claimed bit. Every ROM symbol is read, with no
random lookup or multiplication of decoded indices.

All rejection paths enter the same cleanup after the scratch/output records
have been initialized. Scratch records always have a finite right marker;
clear scans to it, overwrites every visited cell and the right marker with
blank, rewinds to the left marker, then erases it. Borrowed roles are never
written. Their unique left marker makes rewind terminate. On rejection the
output record is erased in the same way; on acceptance its head already is zero.
No early return bypasses cleanup.

On legal inputs the four private tapes occupy exactly
`bit_length(h)+2h+b+9` cells including their eight markers; the owned output
uses three more cells. This is O(h+log s) private space, with ten tape roles
and sixteen finite-control registers independent of every parameter. There
is no copy of the ROM. All occupied private cells return to blank.

## Static instruction charging

The following bounds come from the emitted instruction paths, not from sampled
maxima. Let d be a payload length, or the maximum of the two lengths for compare.
A head may start at its right marker for rewind. Each table entry includes all
branch tests, branches, jumps and final rewind operations.

| Routine | Repeated path and its number of iterations | Upper bound |
| --- | --- | ---: |
| rewind | each non-L cell: read, eq, branch, move, jump; <=d+1 iterations; final read/eq/branch | 5d+8 |
| canonical | <=11 instructions per digit; finite last-digit checks; one rewind | 32(d+1) |
| copy_word | <=7 per digit, terminal branch/write, two rewinds | 32(d+1) |
| is_zero | <=8 per digit, terminal branch, one rewind | 16(d+1) |
| decrement | <=6 per borrowed zero, one terminating bit update, one rewind | 16(d+1) |
| increment | <=8 per propagated one, terminal zero/overflow path, one rewind | 16(d+1) |
| compare | <=32 per paired/padded digit, <=6 terminal instructions, two rewinds | 64(d+1) |
| clear (starting at L) | <=6 per digit, terminal marker erasure, rewind, erase L | 16(d+1) |

All admitted parameter/counter words have length <=w-1:
`bit_length(h)<=h`, `b<=h+1`, `bit_length(offset)<=b`,
`bit_length(target)<=h`, and `limit` has h+1 digits. In each width-loop
iteration, the zero test and decrement use at most 32w instructions together;
append/branch/jump uses at most nine more, hence at most 40w. Its h iterations
cost at most 40w^2; its final zero test is separate.

For clarity, deliberately rounded phase bounds are:

- **Startup <=256w^2.** The four canonical scans cost <=128w, the first h zero
  test <=16w, h copy <=32w, final countdown test <=16w, three range comparisons
  <=192w, row initialization <=32w, and terminal column/limit rewinds <=10w.
  The s-length head return costs <=5w. All remaining initialization, branch,
  append termination and finite s-length tests cost <=96. Together with 40w^2
  this is <=40w^2+431w+96, which is <256w^2 for
  w>=5. The `h` countdown cost is explicitly present.
- **One ROM-bit iteration <=256w.** There are three comparisons (row/s,
  row/offset, col/target) costing <=192w; column and optional row increment
  cost <=32w; remaining tests, saved finite flags, selected-bit output, movement
  and jumps cost <=40. Since w>=5, the sum is <=256w.
- **Finishing <=256w+8M.** The column zero test and row/s comparison cost <=80w.
  Four scratch rewinds/clears cost <=128w, four parameter rewinds <=20w, the
  ROM rewind costs 5M+8, and the remaining branch/status/halt steps fit in
  28w+3M-8. On an accepted execution no output erase is needed.

Thus `T <=256w^2+256Mw+256w+8M`. For w>=5 this is smaller than
`512(M+1)w^2`. The constant is intentionally loose; no measured case is used in
this inequality. Rejection cleanup is verified and terminates, but rejection
cost is not silently included in the legal-input bound.

## Fixed binary lowering

Encode `_`, `L`, `R`, `0`, `1` respectively as `000`, `001`, `010`, `100`, `101`
on each of the ten binary tapes, whose blank background is zero. A logical
head at cell j is represented by a physical head at 3j. The finite registers
and the 752 instruction addresses are part of the fixed finite control; their
number does not grow with h, s or M.

A symbol read reads three bits, uses four unit moves to visit them and return,
and retains the three bits in finite control. A symbol write writes three bits
with the same four moves. One logical move is three physical unit moves.
An equality of three-bit symbol codes needs at most three XORs, two ORs and one
NOT; a register assignment copies/sets at most three bits. A Boolean branch,
jump or halt is a fixed control transition. Charging the associated local
sequencing and bit decisions as well, **32 binary read/write/move/Boolean/control
actions per marker-alphabet instruction** is a common upper bound (the largest
listed data-access path uses fewer than 16). No decoded multi-bit integer,
unbounded arithmetic, address multiplication or variable lookup is introduced.
This is a constant-state local compilation, so concatenating it over the entire
executed program gives `T_binary<=32T`. Initial encoded packets/ROM are supplied;
converting an external representation to those packets is outside this theorem.

Write q=h+log2(s)+1. Since b<=log2(s)+1 and q>=3, w<=q+2<=2q. Consequently
`32*512*(M+1)*w^2 <=65536*(M+1)*q^2`.

## Caller and remaining costs

For PR4739 the row-query parameters are h=5,s=17, with the 544-bit ROM retained
in `FIXTURE.json`. Its two transported witnesses use query sequences
`(offset,target)=(5,0),(4,20),(4,20)` and `(5,0),(5,0),(4,20)` respectively.
The component returns the same six source bits. The caller must still serialize
its computed descriptor/offset into this canonical interface, pay for ROM
construction and CRT reconstruction, and account for three invocations plus
its remaining key/repair work. This package does not execute that adapter or
replace the entire predecessor key. Its different instruction model must not
be subtracted from PR4739's read/write/move-only census as a speedup claim.
