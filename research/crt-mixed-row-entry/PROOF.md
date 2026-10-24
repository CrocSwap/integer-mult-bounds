# Entry at a mixed-width CRT row

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Domain and result

Use the logical Caller in the pinned mixed-width source. Its fixed topology
has d>=2 axes, d a power of two, ell>=2, and declared widths h_i in
{ell-1,ell}. The supplied moduli satisfy 2<=s_i<2^h_i and are pairwise
coprime. One compiled node has interval [a,a+n), n=2^level, a divisible
by n, and midpoint b=a+n/2. The compiled global row is in [0,2ell-2].
The source is one sequential tape. Each axis has the record

    ROOT, ONE^h_i, WORD_END, h_i modulus bits, WORD_END,
    h_i current coordinate bits, RECORD_END.

Bits are little endian. LEFT is at cell zero; RIGHT ends the entire stream;
the head is one. The tape is the encoded representation of the actual
caller's moduli and current row state, not a host integer argument to the
bridge. Representation of that upstream state is a premise. The bridge
checks all field lengths, bits and delimiters. Modulus validity and equality
to the chosen logical Caller are domain premises; the numerical consumer
also checks its own modulus and coprimality guards.

Let S=sum_{i=a}^{a+n-1} h_i and P=S+1. Eight distinct borrowed numerical
ports have the retained P-bit ABI, arbitrary contents and legal heads.
They are disjoint from the source. Their production is a supplied boundary.
All new ports are fresh and blank. The program uses only local port reads,
writes and unit moves for runtime data. Topology loops and axis labels are
compiled finite control; no input modulus, coordinate, product or numerical
width is decoded into host control.

For an active node, RowEntry produces the canonical paired left/right
streams and the unary P guide, invokes the unchanged Entry and produce,
and returns their actual owned result. Its offsets are exactly the actual
Caller.offsets values on this node. close consumes the result, retires all
63 owned ports, and preserves every borrowed byte and entry head. A node
with no active target does no tape work and makes no numerical invocation.
This is a source-operation entry theorem. It does not implement a Beneš
key machine, the whole row permutation, native admission or E(p,ell).

## Sequential representation proof

The program scans all d input records once in order. Compile-time position
decides whether to copy a record to the left stream, the right stream, or
neither. Every selected width symbol appends one ONE to the guide. One final
ONE gives P=S+1 without multiplication or binary-to-unary expansion of a
host integer. Since every selected modulus is at least two, its width is at
least two, S>=4, and P>=5. Also product(s_i)<2^S=2^(P-1). Thus the exact
consumer's width and complete-product margin hold. The source's padded
coordinate fits h_i<P bits.

For each copied h_i-bit field, canonical_end scans its trailing high zeros
backwards and erases them. If it meets the preceding ROOT or WORD_END, it
writes one zero. Otherwise it stops at the highest ONE. It then writes
WORD_END. The resulting number is unchanged and its encoding is minimum
length, including zero. Every removed cell is blank. A later field can reuse
these cells by ordinary writes. The two fields and RECORD_END have exactly
the retained canonical pair ABI. All supplied source bits are read only;
a local rewind restores head one. The guide and paired streams then satisfy
every representation premise of the retained Entry proof.

The retained Entry initializes its 60 owned ports, pads the canonical
streams, executes the unchanged numerical producer, and consumes and retires
its state. The additional three ports are retired after that call. Each
canonical body is contiguous through RIGHT and has only blank cells after
it; clear therefore erases all of its allocated nonblank cells. Its LEFT
marker is also erased. No borrowed port is retired. Failure rollback is
outside the successful-domain theorem.

## Binding to the actual caller

The comment in Caller.offsets uses the word original for the unchanged
left-child slice of a level. Its executable decode_group inverts the
already completed child transform. It does not interpret that slice as
original mixed-radix digits. The retained current-coordinate producer has
that exact decode_group contract. At any micro-row of one level, the left
child is unchanged. It therefore reconstructs the same k_A as the frozen
level controls, or zero if a left coordinate is invalid.

For each right axis j, the producer advances the prefix through every
preceding right modulus. Its output is

    offset_j = k_A * (product_{i=a}^{j-1} s_i)^(-1) mod s_j.

This equals Caller.offsets. The modulus product has an inverse at each
step by pairwise coprimality. Feeding those offsets to the logical row
query thus selects the identical retained Beneš table and target bit.
The bridge itself returns a sequential numerical result; physical transport
from that stream into a key/ROM query is not supplied by this theorem.

Do not apply the returned new-coordinate field as a micro-row update.
It is the endpoint of an entire cyclic rotation. In a partial Beneš path,
a valid endpoint can pass through a padded target coordinate. The actual
row still queries that coordinate; gating it on x_j<s_j changes the
permutation. The independent source case (7,3), widths(3,2), input(1,1)
returns (1,2), while that gate returns (1,3).

For widths(3,3,4,4), ell4, the short axes are idle at global rows3 and4.
They are active at row0. The active set in the bridge is exactly the
source local_row criterion; an all-idle node returns before any port
allocation or source movement.

The main discriminator is moduli(5,7,11,13), state(1,5,0,9), level2.
The current left child decodes to11, with product35. The right offsets
are0 and3; the whole-rotation values are0 and12. Ignoring the preceding
right modulus11 would give7 on modulus13. This is a semantic distinction,
not a choice of formatting or a new CRT identity.

## Complete invoice

Put L=2+sum_i(3h_i+4), the supplied source extent including end markers.
Selection, copying, zero trimming, guide construction, rewinds and final
retirement of the three entry ports take at most

    128(L+P+n+1)

local and finite-control operations. Each input symbol has a fixed number
of tests and moves. Each selected bit is copied at most once and scanned
backwards at most once during trimming. Rewinds and retirement each visit
only the constructed stream lengths. The fixed overhead is absorbed by
the displayed constant. The code uses no whole-array read, slice, length,
absolute head assignment or host numerical field conversion for this work.

The complete existing Entry and numerical tariff must be included once:

    T <= 2^20(P+2)^4 + 2^16(P+2)^2 + 128(L+P+n+1).

This is a constructive upper bound, not a measured speedup. The source
numerical theorem and arithmetic-operation model remain inherited.

The guide retains at most P+1 cells. The two canonical streams together
retain at most 2(P-1)+4n+4 cells: each copied field can temporarily use all
h_i bits, even if high zeros are later erased. Thus the three additional
ports retain at most 3P+4n+4 cells. Include all existing Entry storage:

    K_owned <= 57(P+2) + 3(P-2)(2P+4) + 6 + 3P+4n+4.

Borrowed storage is separate and charged: L source cells and 8(P+2)
numerical cells, plus any preexisting blank backing. No erased backing is
subtracted. These are per-invocation fresh-owner bounds; the complete
trace uses separately retired owners. An arbitrary persistent bank's
history, global backing, codecs and literal binary lowering need their own
contracts. The complete kappa calculation is unchanged.
