# A literal complete row controller for one current CRT wire

## 1. Result and exact predecessor

At canonical base `e54523517d0f03e58352e647c403a5af3e525a57`, retain the
direct current-wire point consumer from CubeJerry commit
`be17dd21af36a8b0546942299ebca7b1c83c4675`, package
`research/current-crt-direct-switch-consumer`. Its 2,500-instruction graph
has digest `2257055b689e0f88dca29532548639323dc3fa27a6e5150ea6652ed5636e07a2`.
That predecessor supplies the literal computation, current-address access,
physical Boolean consumption, cleanup and complete point bill. Nick Petalas
#7504 supplies the canonical switch formulas and child closure; the canonical
Beneš network and CRT source are earlier credited work.

**Theorem.** On the ABI below, one fixed 10,123-instruction graph on the same
20 physical owners has forward and inverse entry ports. Forward maps the
current h-bit wire x to `(x+a) mod s` for x<s and fixes x>=s; inverse maps it
to `(x-a) mod s` on that interval and fixes the padding. Each entry executes
exactly Q=2h-1 complete unchanged point-consumer calls. It preserves all three
borrowed headers and the unary width, restores every head to its entry
origin, leaves the inactive owned row frame zero, and returns every point
private window blank. Every opaque exterior and all prior backing remain.

Write `P=popcount(2h-2)`. The exact additional controller instruction bills
on successful typed inputs are

```
D_forward = 14p + 36h - 12 - 7P,
D_inverse = 14p + 72h - 38 - 14P.
```

Thus the complete local bound is

```
T <= (2h-1) [1024(h+3)^2 + 128(p+h+3)] + 14p + 72h.
```

The per-role historical union of private work is bounded independently of Q
by the same fixed O(p+h) windows. No owner is newly acquired between queries.
Initial source/descriptor production, granted storage, physical acquisition
and movement before entry are external costs and premises. This is a local
uniform controller theorem and bounded actual source join; it proves no full
CRT, recursive allocator, foundational assumption discharge, or new kappa.

## 2. ABI, ownership and failure boundary

Use B5's alphabet `_,L,R,|,0,1` and its exact 20 role numbers. Every role may
have its own translated origin; its entry head is at that origin.

| Ports | Physical role and typed entry |
| --- | --- |
| 0..13 | B5's private point bank; every required window blank at entry. |
| 14 | Borrowed `L [p LSB-first bits of h] R`. |
| 15 | Borrowed `L [p bits of s] R`. |
| 16 | Borrowed `L [p bits of a] | R`. |
| 17 | Inactive owned `L [p arbitrary bits] R`; its body has no live value obligation. |
| 18 | Mutable `L [h bits of current x] R`. |
| 19 | Borrowed `L [h unary ones] R`. |

Require h>=1, p>=h+1, 1<=s<=2^h, 0<=a<s, and 0<=x<2^h. The binary h
header must equal the number of width marks; all p-bit fields have the same
declared precision and boundaries. These are typed consistency premises,
not consequences of seeing binary digits. All 20 owners are distinct;
ownership and blank windows are supplied capabilities, not synthesized from
source labels. Arbitrary earlier larger backing remains allocated and is
included in entry history. Exteriors outside the frames and granted point
windows are opaque and unchanged.

The row frame is writable owned scratch, not a borrowed live field to be
restored. Its arbitrary initial bits may correlate with other inputs; the
entry scan overwrites every bit and preserves its L/R markers. The graph
does not free the frame at exit; its complete body is zero and its head L.

The successful theorem is for this typed ABI. A point semantic rejection
returns its inherited REJECT, and a malformed graph entry can return
MALFORMED. Neither a rejected whole-route rollback nor complete failure-head
restoration is asserted. Missing/interior markers, owner aliases, inadequate
private grants and header/width mismatch are outside the successful theorem.
Finite negative controls do not enlarge this universal admission domain.

## 3. Fixed graph and all-row invariant

`compile_controller()` has no instance parameters. Its only replication loop
has four fixed modes: forward/ascending, forward/descending,
inverse/ascending, inverse/descending. Each embeds every original point
instruction once. Fixed jumps and read targets undergo an injective PC
renaming; successful halts become one jump to the mode's fixed continuation.
Unsuccessful halts retain their status. All tape operands are unchanged.
The four copies are finite-control return states sharing the same 20 owners;
they are not four banks or a variable-depth call stack.

Forward entry scans and zeros the complete row frame and moves the width
head to its first mark. Inverse entry additionally scans each mark after
the first and performs two literal row increments per such mark. Therefore
inverse starts at row M=2h-2. The bound p>=h+1 implies M<2^p, so every
construction increment fits. No decoded h or row number enters a runtime
operand: the width symbols determine iteration, and row digits determine
carry/borrow.

For 0<=r<Q, immediately before query r, let x_r be the current address.
The invariant is

```
forward j_r = r; inverse j_r = M-r;
width head position = 1 + min(r,M-r);
all header/address/row heads are at their L origins;
all fourteen private owners satisfy the original point entry contract.
```

The target equals `1+min(j_r,M-j_r)` in both directions. The unchanged
point graph consequently queries row j_r at the actual x_r and toggles
exactly its prescribed physical target bit. It returns the cursor to that
same target, all other heads to L, and all private work blank. Thus the next
address is precisely the canonical row action on x_r, including any padded
intermediate wire; no test x_r<s suppresses a switch.

Ascending control moves the cursor right. A next `1` gives another ascending
query. At R it moves left twice and changes to descending mode; a next `1`
gives the first descending query. At L it finishes. Descending control moves
left and similarly either queries or finishes. It visits exactly the target
sequence `1,...,h,h-1,...,1`, of length Q. When h=1, the center transition
moves from R through its sole mark to L and terminates after one query.
Before every further query the row is changed by +1 forward or -1 inverse.
Neither overflows nor underflows on the displayed invariant.

Each canonical row is an involution. Forward therefore executes its complete
network in source order; inverse executes exactly the reverse row order.
This proves the stated complete padded rotation and inverse. Final zeroing
retires the row body, whose head returns to L. The cursor has reached L by
literal movement, and no host head reset occurs.

## 4. Exact controller invoice

One R, W, unit M, J or H instruction costs one. The original successful H is
replaced by one J, so the number of instructions inside a point copy is
unchanged. Every added transition lies among the 123 controller instructions.

A full zero-row routine costs exactly Z=7p+7: entry probe/move cost 2,
each bit costs read/write/move/jump=4, the terminal read costs 1, and rewind
from R costs 3(p+1)+1. It is called once at entry and once at retirement.

A row increment with c trailing ones, or decrement with c trailing zeros,
costs C(c)=7c+8: entry probe/move=2; each propagated digit costs 4; the
terminating read/write costs 2; rewind over c+1 positions costs 3(c+1)+1.
The successful typed call always has a terminating digit inside the frame.

For the M increments from 0 to M, the total propagated digits are

```
sum_{k>=1} floor(M/2^k) = M-popcount(M).
```

The M decrements from M to 0 have the same total. This identity follows by
writing M in binary, so it applies at every height and is not a sampled fit.
Thus either full update sequence costs 8M+7(M-P).

Forward initialization after zeroing costs 4. Across all queries the cursor
cost is 4h+1: h ascending steps/read pairs, one three-instruction turn,
and h-1 descending step/read pairs. The M update-to-point jumps cost M;
the final halt costs 1. Hence

```
D_forward = 2Z + 4 + (4h+1) + M + [8M+7(M-P)] + 1.
```

Inverse initialization beyond its entry zeroing costs
`6h+8+[8M+7(M-P)]`, including every unary scan, both increments per mark,
terminal read, complete width return and jump to the first point. Its later
decrements have the same bill as forward's increments. Subtracting the
forward startup 4 gives the claimed inverse expression. Both expressions
are at most 14p+72h. All frame scans, carry propagation, jumps, zero writes
and returns are included; no arithmetic on a decoded integer is a runtime
primitive. Fixed alphabet encoding changes these bounds by an absolute
constant; the executed object here is the marker-symbol graph.

## 5. Historical storage and actual caller seam

The new controller never leaves the supplied row or unary-width frames.
At fixed h,p every point invocation uses the same per-role interval as B5,
regardless of s,a,j,x: private H may visit p+2 cells, the four copied numeric
inputs each h+3, the output three, the height countdown bit_length(h)+3,
and the other seven private roles each h+4. Their sum is

`p + 11h + bit_length(h) + 48 <= p + 16(h+4)`.

For earlier retained interval K_t on each role t, count the union of K_t
and that role's stated interval, then sum over roles. Repeating Q calls does
not multiply those fixed intervals; every retired cell is still counted.
The point cleanup establishes reentry on the same physical backing. Input
framing/acquisition and opaque older exteriors remain supplied and charged.

`join.py` authenticates B5's `caller.py` and substitutes exactly its
`route_address` function. The replacement binds the same 20 objects, selects
one fixed direction entry for the caller's leg, executes once, and checks
its final status. All outer wire enumeration, actual numerical lease/header
production, source staging/retirement/commit, payload access, key writes and
literal radix providers remain the retained implementation. They keep their
own model and costs. The actual finite caller evidence is consequently a
join to retained providers, not their reimplementation or a uniform literal
all-wire/source dispatcher theorem.

No ROM-reuse speedup follows merely from this lowering. A complete N-wire
workload still pays N full row controllers plus all actual source, payload
and sorting work; compare that with ROM build, the same queries and disposal
under a common tariff before making any performance or supplier claim.
