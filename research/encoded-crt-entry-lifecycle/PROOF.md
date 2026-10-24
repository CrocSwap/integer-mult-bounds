# Encoded numerical entry and complete current-child consumer

JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.

## Statement and precise boundary

Fix P>=4. The caller supplies a unary P guide (LEFT, P ones, blank tail),
canonical paired modulus/current-coordinate streams, and eight distinct dirty
P-bit numerical ports. Numerical ports have LEFT, P binary cells, RIGHT;
their heads may be anywhere inside the numerical word. Stream/guide heads
are1. Canonical paired streams use the retained ROOT/WORD_END/RECORD_END tags,
minimum-length little-endian numbers (zero is one zero), and terminal RIGHT.
All supplied ports are mutually disjoint. Work storage is new, owned and blank.

Both groups are nonempty. Moduli are>=2 and pairwise coprime across the whole
invocation; their complete product is<2^(P-1). Coordinate words fit P bits.
Left values may be padded invalid coordinates; the inherited consumer then
disables the update. Right values>=their modulus remain unchanged. The same
P/guide remains fixed during a live owner's repeated invocations; each new
stream obeys the same premises. Upstream production of these inputs is not
part of this theorem.

The new entry constructs56 owned numerical ports, one owned template and
three owned record ports, invokes the exact retained PR5053 produce function,
and returns its lower/product words, validity flag and complete offset/value
stream. Results have their original semantics. consume erases both returned
words and all three record bodies. close erases all60 owned ports, including
markers, and returns their heads1. Supplied input and eight dirty ports retain
all bytes and heads. Successful-domain cleanup is proved; malformed-input
rollback or cleanup after failed initialization is not claimed.

## Genuine width and storage representation

Extent represents the integer P by the guide itself. Its only supported
observation, >=4, reads up to four unary cells and rewinds. It returns exactly
P>=4. int conversion rejects. No scalar P is stored in the new context.
The pinned producer has exactly one .bits use, this guard. The pinned words
module uses .bits only in Arena/Word constructors; none of its runtime
arithmetic uses it. Those constructors are replaced by the new initialization
and forbidden during actual invocation. No frozen source or authentication
is changed, and no dummy scalar width is substituted.

Each owned numerical port is built with a paid LEFT write, one local write
and movement per guide unit, and a paid delimiter-cell write. Non-template
bodies are blank, including their future delimiter; the template is P zeros
then RIGHT. The guide is restored after each traversal. Thus the physical
arrays have exactly P+2 cells, as required by the original Word local-boundary
checks, without multiplying a host list by P or filling a width-sized slice.
HostedWord inherits the original arithmetic methods; its cells and head
properties reference the physical port directly. There is no free copied
head restoration or detached backing representation. Its arena/slot bindings
are the genuine fixed context and finite slot number. Eight supplied dirty
ports occupy slots0..7; they are protected, never allocated or retired.

All object/slot inventories here are fixed constants. Port growth occurs
only at a local write to the next blank cell. Head/buffer bounds in the
simulator implement tape semantics; they do not decode an input width.
This is a source-operation representation refinement, not a literal finite
instruction compilation of the whole numerical arithmetic.

## Allocator correspondence

The reference original arena begins with live slots0..7, no recycled slots,
and next unused slot8. The new arena starts with all64 word wrappers, live
slots0..7, and available stack [63,62,...,8]. At every numerical boundary its
stack equals this descending unused suffix followed by the reference's
recycled LIFO stack. If the recycled stack is nonempty, both pop the same
slot. Otherwise both select the least unused slot and remove it from the
suffix. free erases the identical word and appends the same slot to the top.
Induction gives identical slot choices and ownership events, not just equal
peak counts. Original numerical values, physical heads, byte extents and
alias identities are related at each operation. The predecessor proves the
consumer's inventory stays within64 including eight protected words, so the
new zero method never reaches the forbidden Word-constructor branch.

The reference lazy allocation's first unused word is blank with LEFT and
P+1 blank cells; the eager port has exactly that state. Every original zero
copies the same template, so reads/writes/moves during arithmetic are identical.
New setup and retirement are extra paid operations. The finite sets and
stacks contain only64 possible slot labels; no growing numerical register
inventory or input-dependent host integer bound is hidden here.

## Canonical transport and full lifecycle

pad traverses each original ROOT pair and processes two words. For each guide
unit it copies the next binary input bit, or writes zero after WORD_END has
been reached. At guide exhaustion it requires a nonempty canonical word and
its delimiter; this rejects a too-wide or noncanonical representation.
Delimiters are copied to the fixed-width retained ABI. No input-dependent
integer is decoded. Rewinding restores guide and original stream; the owned
padded stream has exactly m(2P+4)+2 cells for m records.

The records argument retains the original read_word/append_word functions
and tags. Only Tape construction is supplied by the single already initialized
output role, with a one-use check. This replaces a real constructor obligation,
not its numerical or parser semantics. produce executes unchanged, including
current-child reconstruction, modular inverses, preceding right prefix,
padded-coordinate handling and its finally ownership cleanup. Its successful
exit leaves only protected words and the two returned numerical results live.
consume frees those exact words and clears all record bodies. It restores the
entry invariant for another call at the same P. On terminal close, each owned
numerical body is already blank; its marker is erased. The template body is
erased by its original Word.erase before its marker is erased. The three
record markers are removed by paid local writes. No borrowed port is retired.

## Complete cost and retained backing

Let m,t be left/right record counts. Since every modulus>=2 and the complete
product<2^(P-1), m+t<=P-2. Setup makes57 guide scans and initializes57(P+2)
numerical cells; padding visits at most(m+t)(2P+4)+4 cells plus corresponding
guide scans. Source output has t(2P+4)+2 cells. Retirement visits every template
cell, both padded streams, the result stream and all owned markers; arithmetic
word erasure is already charged by the retained consumer/free operations.

A conservative bound for all new setup, transport, finite slot bookkeeping,
result consumption and terminal retirement is 2^16(P+2)^2 source operations.
To see the constant without a timing inference: each guide or canonical bit
causes fewer than64 local/finite-control operations; each padded field visits
at most P+1 cells; initialization visits57(P+2), record traffic and disposal
visit fewer than16(P+2)^2 cells, and fixed wrapper/stack setup costs fewer than
4096 operations. The displayed constant dominates their sum for P>=4.
Include the predecessor's complete numerical consumer tariff once:

    one call with setup and retirement <= 2^20(P+2)^4 + 2^16(P+2)^2.

For k>=1 calls under one owner, a conservative bound is k times the
displayed expression: setup/retirement occur only once, so counting them
k times only enlarges the bound. Time is not uniform in the call count.

The verifier separately records numerical and port read/write/move traffic;
the written bound includes finite control and is not inferred from those
observations. There is no speedup claim.

Numerical owned backing is exactly57(P+2). During one call the record backing
is at most(m+2t)(2P+4)+6. Erasing does not shrink it. Across arbitrarily many
successful calls at fixed P, maxima of left, right and output lengths may
occur at different calls; each record count is<=P-2. Consequently total
retained owned backing is at most

    57(P+2) + 3(P-2)(2P+4) + 6.

Borrowed guide, input streams and dirty ports are separate supplied storage.
The result is a tape-cell bound, not a bound on Python allocator bytes. Dirty
port production, arithmetic binary lowering, full ROM/raw/repair, E(p,ell),
native/selected supplier and outer multiplication remain outside the theorem.

## First actual source discriminator

For moduli(5,7), current coordinates(1,5), the exact producer returns lower11,
left product35, and right modulus13 offset7. Right coordinate9 becomes3;
padded coordinates13..15 remain unchanged. Original-coordinate interpretation
would give26 and offset0. This is checked through actual initialized context,
not only an oracle or serializer. P10 is sufficient for total product455;
P9 violates the retained product high-margin condition and must reject.
The written refinement is for all admitted P, not extrapolated from fixtures.
