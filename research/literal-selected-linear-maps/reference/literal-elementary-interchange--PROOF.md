# Complete local-symbol elementary interchange

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Domain and endpoint

Let H>=0 and A,G,S>=1 be arbitrary integers and V=A*4^H*G*S.
Five disjoint borrowed tapes contain SOURCE's V opaque binary cells and the
canonical little-endian words H,A,G,S. Each has LEFT at position0 and head1;
numbers have RIGHT after their most significant bit (zero is 0 RIGHT), and all
bodies have blank tails. Fifteen disjoint private tapes are initially entirely
blank with head0. External tapes are disjoint from every private tape. Input
initialization is supplied, not free production of these tapes. A caller with
preexisting erased backing may use it; its capacity is not credited as zero.

For every such input, init then run halts returned. SOURCE and all four words
are byte-for-byte unchanged, heads1. OUTPUT is a distinct owned V-bit body
with head1. Every other private tape has only its LEFT marker and blank body,
head1. At indices (a,x,g,y,s), with x,y in [0,2^H), output is the source bit at
(a,y,g,x,s). After the caller consumes OUTPUT by the included consume entry,
run may repeat on these same roles with any new admitted borrowed tapes. close
then erases all15 owned markers and returns all private heads1. No malformed
input rejection rollback or external alias detection is promised.

## What the executable is

program.assemble executes once offline. Its result has4589 instructions and
five entries; this word is independent of H,A,G,S and payload bits. Assembly
helpers, lambdas and Python loops do not survive into the machine. The only
instructions are test(role,symbol,yes,no), write(role,symbol), move(role,+/-1),
jump(pc), and halt(status). Role names and five symbols0,1,LEFT,RIGHT,BLANK are
finite constants. test performs exactly one local read. No arithmetic,
copy, counter, permutation, method call or allocator opcode exists. The PC
encodes finite carries and route choices. Host integers for heads/PC/censuses
are simulator configuration and observers, never decoded tape operands.
The all-width theorem concerns unbounded program semantics. execute's finite
max_steps is an observer watchdog and may abort a larger admitted instance.

This is a five-symbol multitape program over binary payloads, not a supplied
implementation over a two-symbol tape alphabet. A separate fixed-block binary
alphabet translation remains open. The result does replace the entire source
callee's host control, including arithmetic and scratch selection.

## Primitive invariants

rewind moves left until the owned/borrowed LEFT marker, then right once. clear
first rewinds, overwrites each body symbol up to the first BLANK, then rewinds.
It preserves retained backing. copy(source,target,end) traverses only binary
body symbols, checks each destination cell blank, writes the same bit, and
returns both heads. For a number it appends RIGHT; for a payload it leaves the
blank tail. Its target must be empty. All uses satisfy this premise.

zero branches true precisely on 0 RIGHT and restores head1 on both branches.
All number words used with it remain canonical. normalize scans to RIGHT,
replaces high zero cells by RIGHT while erasing the previous delimiter; if the
word becomes empty, it writes 0 RIGHT. dec is called only on a positive number:
it changes low zeros to ones up to the first one, changes that one to zero,
then normalizes. This is subtraction of one, including powers of two and one.

double shifts the little-endian bit stream by one place. Two PC states carry
the old preceding bit, starting at0. At RIGHT a carry1 becomes the new high bit
and a new RIGHT is written. Every use is positive, hence the resulting word
is canonical. half requires the low bit0, then copies each next bit one cell
left and moves the delimiter left, erasing its former cell. Every use divides
an even positive value, so its high bit remains1 and its result is positive.

counted(number,counter,body) clones the number to an empty dedicated counter,
tests zero, executes body and dec until zero, then clears it. Its source is
preserved. Bodies never alias their enclosing counter. The three nested
counter roles OUTER,BETWEEN,BITS are distinct; all sequential invocations
reuse them only after clear. No depth or role inventory depends on values.

## Complete digit pass and all-width induction

PRE,GAP,TAIL have values P,M,T. digit reads order (p,a,m,b,t), a,b in{0,1},
into four separate queues Qab in order(p,m,t), each of length P*M*T. Each read
and append is performed by counted loops and literal instructions. The second
traversal reads Qba in order(p,a,m,b,t); consequently it swaps those two binary
digits while retaining spectators. It checks source and each queue end,
restores source head, clears queues, and returns the new body head1. Total
volume is4PMT; opaque bits never determine a route or numerical counter.

SCAN starts at H. It decrements once before each potential doubling, and stops
if zero. Thus GAP=G*2^max(H-1,0), TAIL=S*2^max(H-1,0), PRE=A. REMAIN starts atH.
The first pass uses SOURCE and B0. Subsequent passes alternate B0/B1; each
clears the consumed owned buffer before reuse. Before pass i>0, PRE doubles
and TAIL halves. Therefore at pass i=0,...,H-1:

    PRE=A*2^i, GAP=G*2^(H-1), TAIL=S*2^(H-1-i).

TAIL is even precisely whenever the next half is taken. Each pass has volume
4*PRE*GAP*TAIL=V. This is exactly the retained atom_swap/digit_swap digit
schedule specialized to q=2, or PR5162 Elementary.run's encoded-H schedule.
The retained source proof's index induction exchanges the two H-bit blocks
in H adjacent digit-pair passes; no new source ordering or padding is assumed.
The program duplicates three finite pass bodies for SOURCE/B0/B1, not H
bodies. H=0 takes the SOURCE return branch and copies to a distinct OUTPUT.
At H>0 the selected owned buffer is copied to OUTPUT and cleared. PRE,GAP,
TAIL,REMAIN are then cleared. This proves the endpoint and repeat-call
invariant. init and close explicitly create and remove all15 markers.

PREDECESSOR.json pins the exact PR5162 export and all cited source members.
The original vendor notices are inside that unchanged archive. Verification
authenticates it before reading the source. It is evidence for the written
refinement, not a hidden runtime source executor.

## Complete price and capacity boundary

Let L=H+bitlen(H)+bitlen(A)+bitlen(G)+bitlen(S)+8, with bitlen(0)=1.
Every numerical body in the proof has length at most L. For example GAP and
TAIL add at most H-1 bits and PRE at most H-1. Each rewind/clear/copy,
normalization/decrement, double/half of a number uses fewer than128(L+1)
literal instructions, by summing the displayed tests, moves, writes and
jumps per scanned cell, including origin/delimiter branches.

A digit pass traverses2V payload bits. There are at most2V suffix countdown
iterations; enclosing outer/between iterations and counter constructions
are at most8(V+1), since A,G,S and the intermediate extents are positive.
Payload transfer contributes fewer than16(V+1) instructions. Queue clearing
and source/queue returns together traverse fewer than8(V+1) cells. Charging
all these, including countdown setup/normalization/clear, gives the safe
bound4096(V+1)(L+1) instructions per digit pass. Descriptor setup and SCAN
cost at most1024(H+1)(L+1)^2. Updating PRE/TAIL is at most256(L+1) per pass.
Final output transport, clearing the final buffer, caller consume (or paid source installation) and owned
marker disposal cost at most128(V+L+1). These inequalities are conservative
termwise loop bounds, not inferred from elapsed time or finite fixtures.

In particular the complete init/run/consume/close session is bounded by

    T <= 2^20 * (H+1) * (V+1) * (L+1)^2.

The finite admission checker independently excludes control-only cycles.
For this word, at most two jumps occur between cell instructions or halt;
thus T<=3(C+k), where C counts actual reads+writes+unit moves and k
is the number of executed entries in the session (k=1 for one execute call).
Tests are paid reads even when merely checking a precondition.
Successful output computation is priced with caller consumption/disposal,
not only the routing core. Reusing a live initialized owner omits only its
already-paid init and eventual close; all per-call costs remain.

Fifteen private roles is an exact inventory, not a bound on total retained
backing under arbitrary histories. clear does not shrink arrays; total
backing-space grants remain a separate obligation. Simulator allocation and
wall time are not the local-symbol model's instruction price.

## Actual caller and limits

The actual PR5162 raw u/back descriptor is H2,A1,G1024,S12, V196608.
The verifier executes the same whole literal callee, compares every output
bit with the independent address permutation and also executes a paid
copy-back to the original source port before disposal in the caller probe.
That extra caller transport is separately metered. No raw12-shear replay,
ROM producer, repair, current selected/native supplier, all-size CRT/full E,
precision, outer multiplication or improved kappa is asserted here.

Finite single-column and adversarial controls corroborate this written proof;
they do not prove its quantified claims or confer human/kernel acceptance.
