# Serial low packets on a fixed number of tape heads

For one paid site use the inherited address
((uL+l)H+h)H^j+a, where 0≤l<L and all high and body digits are genuine.
Treat each (h,a,body) run as an opaque block. Stable binary digit passes
on l turn (u,l,block) into (l,u,block). The reverse direction places
returned arbitrary data back in (u,l,block) order. If generating the
original (u,l) key is expensive, replay the stable-partition decisions
in reverse on the *same physical sizes*: at each pass recompute the flags
in the previous order from the known mixed-radix counters, read the
zero/one return streams in that order, and emit to one parent stream.
Both directions require O(log L) full passes (or the separately paid
older field-exchange primitive). The number of tape heads is fixed.
The separate factor log L matters for comparison with the old L+7-head
router, which had ≤94V transitions per direction for each fixed L.

For a literal binary pass j, put d=2^j and (Q,R0)=divmod(L,d).
Before this pass the order is (b,u,z,block), where 0≤b<d,
0≤z<Q+[b<R0], and the next flag is z modulo two. Generate two loops
of lengths R0 and d−R0, one A loop per b, and a Q or Q+1 run per u.
Its flag simply alternates. Use binary shifts on L followed by unary
guides for these lengths and the opaque block size. Their construction
costs O(A+R+d+Q+log²(L+1)) moves per pass, absorbed by O(V) since
A,R≥1 and V=ALR. Rewind a guide only at the end of its own positive
run; its rewind is then paid by the same run. For the inverse, first
emit one unary mark per zero-labelled return block to get the split point,
copy that prefix to the zero stream and the suffix to the one stream,
then replay the same flags in the previous order. Two sequential data
scans per direction and the space for the unary marks cost O(V) per
digit, without an individual key per payload bit.

After transposition, transfer the entire type-major word backwards onto
a pending stack, reading from its rear, with the first bit of its first
low packet at stack top. Preserve a readonly input that the interface
requires with one extra copy outside the loop. At a current low ordinal
pop exactly the complete packet length in forward order, erasing its stack
cells. The pending head is now at the next sibling boundary. Push child
frame markers on both stacks. All child operations on these stacks use
only fresh top suffixes. The returned stack can already contain changed
results of earlier siblings. Pop the child's complete result to a scratch
stream, remove both isolated child frame markers, and append the returned
packet in forward order to the parent's result stack. Continue with the
next low group. The final result stack can be popped in reverse once,
reversed, and passed through the inverse type permutation. Each child can
return any contents. Both directions preserve all high-label and body
records.

Unrelated live parent banks are parked once at entry to the paid site.
A stack may never push a scratch frame across a long, unconsumed sibling
suffix from a head in its interior. The top-only arrangement puts the
unconsumed sibling suffix physically *behind* the pending head and the
finished packets behind the returned head. The child has its own delimited
region on both tapes. Removing its own slots returns both heads to their
previous boundary. The current low index and continuation state are at
the top of a separate control stack. If old descriptors are needed by the
weight evaluator, carry only the live ancestor descriptor chain, charged
at the source tariff. Seeking those descriptors under parked siblings
would invalidate this implementation.

For a parent volume V with L nonempty children, the direct serial stack
operations use a constant times V+L plus descriptors and source/subroutine
instructions. Transposition and numerical low-ordinal evaluation have
their own tariffs. A per-low polynomial-in-w cost is paid once per true
low and amortized by its entire high or body fibre; w=1 at a genuine
ordinary root entails e=1 in the specified selection rule. At positive
large w, the full H^(j+1) portion remains available. At a cut where a
classifier emits multiple paid children on one bad low, they run on its
own retained packet and carry the existing explicit bad-branch factor.
Restoring the complete type order at the end of a native paid site avoids
rematching low groups across partially completed outputs.

At any time unconsumed and already returned siblings at one parent have
combined volume at most V, apart from an active copied packet plus its own
temporary stack suffixes. Descendant frames use their actual fractions.
Historical maxima are bounded by the sum of these extents on one active
chain; all sibling cells are erased before they are reused. There is no
persistent descriptor or tape head per low type.

The finite stack probe in stack_cut.py checks 15 variable-radix nested
cases, including four levels, uneven shapes, and different arbitrary
returns per ancestor path. An independent per-input-index Euclidean
decoder computes the expected answer. It checks the exact two-stack
access count 8 times (sum of node volumes + number of internal nodes),
including all markers. The same probe executes the actual forward and inverse sequential radix
passes and checks them against direct ordinal maps in 544 more geometries.
It does not measure individual transducer clock cycles of those passes.
The original fixed-head comparison and whole-row source geometry are
documented in the [physical splitter](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/delayed-cover-physical-batch-routing/PROOF.md)
and [complete ordinary caller](https://github.com/CrocSwap/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/ORDINARY.md).
