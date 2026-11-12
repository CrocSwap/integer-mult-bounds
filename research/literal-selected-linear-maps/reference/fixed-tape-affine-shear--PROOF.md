# Literal runtime affine shear and its source half-coefficient leaf

This is an algorithmic proof for the supplied finite programs. It is not a
proof-kernel result, a native operator proof or a complete supplier admission.
The split/merge idea and the local machine/counter/copy macros are David Arias's
PR2776. Charles Bethin's unit-carry kernel is the closest fixed-carry successor.
The new feature is an arbitrary **runtime** coefficient and offset, with their
complete conversion, wrap, reset and cleanup costs.

## Contract and fixed machine

For every positive integer `P,Q,G,S` and `0<=c,C<Q`, let `V=P Q^2 G S`.
Canonical positive LSB-first binary words encode `P,Q,G,S,c+1,C+1` on six
separate preserved input tapes. The source tape contains every Boolean payload
bit in lexicographic order on `[P] x [Q] x [G] x [Q] x [S]`, between distinct
LEFT/RIGHT markers. Input heads begin on the first symbol. Output and eleven
private tapes are completely blank and have independently supplied origins.
No input/output/private roles alias. Arbitrary bit values, gap/suffix extents
and different translated tape origins are allowed.

The two 877-instruction programs have nineteen tapes and seven symbols. Their
only operations are one scanned-symbol branch, one-cell write, one unit move,
fixed jump, halt and reject. Assembly consumes **no** runtime extent, coefficient,
payload or Python callback. Each executed microinstruction costs one transition.
All sources and descriptors return byte-for-byte with their original heads.
Output is a separately owned marked stream with its head on its first bit.
Every private symbol, marker and head returns to its original blank state.
Their permutation is

```
(p,x,g,y,z) -> (p,x,g, y +/- (c*x+C) mod Q, z).
```

The total cost, including descriptor conversion, all carries, rewinds and
cleanup, is at most `1024V` transitions and `64V` visited tape cells. The space
bill includes visited cells subsequently cleared; it is not a final live-space
count. Invalid inputs need not be cleaned up on rejection. This is a valid-input
contract; inspecting one initial cell does not certify an otherwise unbounded
scratch tape is empty.

## Split invariant and termination

PR2776's retained binary-to-unary macro preserves its canonical input and
returns its work tape blank. Convert seven values: `P,Q,G,S,Q,c+1,C+1`.
The second Q copy is a genuine independent x-traversal counter. Remove one
unary mark from each last counter, and compare each with the Q counter to
reject `c>=Q` or `C>=Q`. These comparisons are literal finite loops.

At a boundary the two split tapes have lengths `(L,R)=(Q-r,r)` with `0<=r<Q`,
both heads on their right markers. Transferring one mark changes `(L,R)` to
`(L-1,R+1)`. When `L=0`, transfer all Q right marks back, erasing old right-marker
tails, so the representation becomes `(Q,0)`. Thus one completed transfer is
exactly `r -> r+1 mod Q`. The transient `(0,Q)` is reset before any payload.
Initialization advances by C. At the start of the x-th group, therefore,

```
r = C + c*x mod Q,  (L,R) = (Q-r,r).
```

For every gap g, gather the first L source records into A and the remaining R
into B; a record has S opaque bits. Advance the split by exactly c mark transfers
and advance the **separate** Q counter once. This works for zero and nonunit c:
traversal does not depend on the order or period of the offsets. After Q groups,
`C+cQ = C mod Q`, so no prefix reset or reconstructed coefficient is needed.
The same invariant applies to each next prefix and to the emission pass.

Forward emission consumes B's next R records, then A's next L. This moves each
source y to y+r modulo Q. Inverse compilation reverses the two gather segments
and the two emission segments: it gathers R then L and emits L then R, giving
`y-r`. Both are permutations for **every** c; c need not be a unit because x is
preserved. Every copied bucket cell is consumed exactly once. Rewinds preserve
source and descriptors. The retained eraser clears each private region back
through its temporary LEFT origin marker and returns that head to its origin.

All loops use finite positive unary counters or finite segments. Each x iteration
finishes c transfers; each wrap finishes Q transfers; P,Q,G,S are finite. This
proves termination and all endpoints for every permitted shape and payload.
Finite coefficient grids corroborate this argument; they do not replace it.

## Complete uniform transition ledger

The retained positive conversion takes
`24n - 7 popcount(n) + 15 bit_length(n) + 12 <= 44n` transitions.
A rewind from a right marker after h symbols costs `3h+3`; scanning/deleting one
unary suffix marker uses the actual local instructions in the retained source.
The following conservative blocks are upper bounds obtained by summing those
instructions. Every extent monomial displayed is at most V.

| Executed block | Transition bound |
|---|---:|
| Initialize output and eleven private marked tapes | `36 <= 36V` |
| Seven conversions | `44(P+G+S+2Q+c+C+2) <= 308V` |
| Decode c+1,C+1 by one-mark removal | `6c+6C+22 <= 22Q <= 22V` |
| Two strict coefficient/Q comparisons, including rewinds | `11c+11C+22 <= 22Q <= 22V` |
| Initialize the split and advance C (no wrap) | `14C+3Q+6 <= 17Q <= 17V` |
| Two payload/traversal phases, excluding coefficient advancement | `23V+20PQ^2G+28PQG+20PQ+20P+8 <= 119V` |
| All coefficient advancements and cyclic resets in both phases | `2P[Q(17c+4)+c(10Q+3)] <= 54PQ^2 <= 54V` |
| Finish gather and rewind both buckets | `3V+9 <= 12V` |
| Finish output, source/output rewinds and all eleven complete erasures | `<=111V` |
| Final halt | `1 <= V` |

Their sum is at most `802V`, below the stated `1024V` allowance.

For the phase row, one record copy costs at most `(11+consume)S+4`, and a segment
of length l costs at most `(11+consume)Sl+10l+4`, including its length rewind.
The two segment lengths sum to Q regardless of gcd(c,Q). Summing the actual
P/x/G loop branches and unit moves gives the displayed two-phase polynomial.
No uniform distribution of offsets is used in this bound.

For the advancement row, a coefficient rewind costs at most `3c+3`; c ordinary
transfers plus loop tests cost at most `14c+1`. Each cyclic reset adds at most
`10Q+3`. Across all Q x-groups at one prefix there are exactly c resets, since
the total advance is cQ starting at C<Q. Therefore that entire prefix costs at
most `Q(17c+4)+c(10Q+3)`. In particular, even `c=(Q+1)/2` incurs `O(Q^2)`,
which is absorbed by the actual complete-pair payload volume Q^2GS. Repeating
whole unit-shear invocations would instead cost O(cV); this program does not.

The last cleanup row includes both consumed bucket regions (total at most V
cells), P/G/S counters, both split lengths, binary work, c/C counters and the
x counter. At their current right heads, the retained eraser costs `4h+2`.
This gives at most `98V` for private erasure, `6V+7` for output/source returns,
and the extra output end-marker write; the stated 111V is conservative.

## Space, including cleared work

Let M be the maximum bit length of the seven converted integers and let B be
the sum of the six input descriptor bit lengths. The union of visited intervals
has size at most

```
3V + P+G+S + 3Q + c+C + B+M + 40
 <= 3V + P+G+S + 5Q + B+M + 38 <= 56V < 64V.
```

Source, output and the two buckets contribute `3V+8`. The remaining terms pay
all unary counters, both potentially Q-long split intervals, the maximum binary
work interval, all six input intervals and every marker. The bucket lengths
may be very unequal (for example c=C=0); only their sum V is used. Each
positive descriptor has bit length at most its value, and each such value is at
most V. Tape translations change no interval length. No cell outside these
intervals is accessed.

## Literal half descriptor and actual source leaf

PR4989's retained actual frame506 schedule includes
`ordered_shift(addresses=[3,0], coefficient=[1,2])`. Its interpreter defines
address0 as source and address3 as target. For every source odd prime q and
`e=w-1>=1`, the complete high fields have common extent `Q=q^e`, and

```
2 * ((Q+1)/2) = Q+1 = 1 mod Q.
```

Thus the runtime multiplier is c=(Q+1)/2. The negative half leaf is the inverse
program. This grows with e; treating the rational factor as a fixed number of
unit shears would be an invalid uniform-time argument.

The complete linked half program includes a **literal** preparer on the same
nineteen-tape bank. It checks that Q's low bit is one and at least one further
bit exists, copies the remaining bits into an owned blank coefficient tape,
then performs a ripple increment beginning at its second bit. The copied
integer is floor(Q/2); the result is `floor(Q/2)+2=(Q+3)/2=c+1`. The final
high-bit check enforces canonical encoding. It returns Q and both input heads.
After the generic kernel, a literal scan erases every coefficient bit and its
markers, returning its tape to its original blank origin. These tables are
retained in TABLE.json.gz together with the generic programs; linking adjusts
only finite state destinations, not runtime addresses.

Preparation costs at most `40 bit_length(Q)+80 <= 67Q` for Q>=3. Complete owned
descriptor erasure costs at most `8 bit_length(Q)+8 <= 11Q`. Their tape cells
already lie within the generic space ledger. The linked half call therefore
costs less than `880V`, still within `1024V` and `64V`, including preparation and
cleanup. General c,C are supplied descriptors; preparing arbitrary rational
coefficients from a caller is not made free by this half-specific construction.
The offset descriptor is C+1=1 for this actual source leaf and is preserved.

For an actual complete source packet, group every coordinate before source0 as
P, those between source0 and target3 as G, and those after target3 as S. Their
extents may be enormous; the proof quantifies over them. No sorting, random
access, hidden high-coordinate lookup or ordinary interchange is used. This
binds the later-target half leaf on the complete-high-fiber interface. The
finite executed fixtures compress these spectator dimensions and do not
materialize the full source high matrix or prove the whole native invocation.
Other later-target +/-1 and +/-1/2 slots have the same interface; no claim about
reversed-field slots or unit_scale is implied.

## Remaining obligations and decision

This closes one physically priced ordered-affine primitive with a source-bound
half descriptor. It does not construct PR4989's complete low-type cache, native
canonical call, raw-body call, completed ordinary swap, ROW padding or the full
compiled matcher. Installation in the whole recursive owner bank, matched
physical tape allocation, reserve/precision/threshold constants and the P3
recurrence remain open. Output/source separation is explicit; replacing the
source owner by the output or erasing that original source needs the caller's
paid ownership protocol. No selected frontier or multiplication exponent is
changed. Continue only after one of those separate contracts is selected and
its complete allowance is stated; another small coefficient fixture is not a
new contribution.
