# Standalone elementary interchange and raw CRT boundary

## Domain and distinction from the rejected predecessor

This package defines a new standalone elementary binary service. It does not
instantiate or claim admission of Ordinary, RootSession, SelectedBinding,
SelectedTopology, a selected coefficient catalogue or a fitted program. No
selected-record authentication guard is changed. The R10 q2 dummy constructor
is not used. The five vendor files are byte-identical members of retained
PR2809's PR2753 predecessor; their digest inventory is VENDOR.json. They import
only each other. In particular, the source-wide loader, controller callback
factory and selected low-code vocabulary are absent from this dependency
closure. This is an explicit specialization of the elementary algorithm and
its allocation sites, not execution of the complete original ordinary wrapper.

Let H>=0 and A,G,S>=1 be encoded by LEFT, canonical little-endian binary digits,
RIGHT, followed by blanks. A descriptor's entry/return head is cell1. Let the
borrowed payload contain V=A*2^(2H)*G*S arbitrary bits, after LEFT at cell0,
followed by blanks, also headed at1. The five borrowed objects and owned output
are distinct; no borrowed object is a private bank role. Blank tails may have
arbitrary finite extent. The typed successful-input theorem assumes these
framing, volume and disjointness conditions. It is not a transactional rejection
or arbitrary malformed-tail theorem.

Elementary initializes exactly16 private physical tapes and one output tape.
Every one starts physically blank; its LEFT write and first unit move are
executed by Physical.__init__, not supplied as an uncharged marker premise.
No constructor receives a numerical width or native supplier. The output body
must have been consumed before reuse. Each call preserves all borrowed bytes,
returns their heads to1, produces the complete transposed output headed at1,
and returns every scratch body empty with its LEFT marker retained. close()
after output consumption erases all17 owned markers and leaves their heads at1.
A caller may repeat successful calls on the same17 physical roles. Erased backing
arrays are retained; fixed role count is not a bound on total backing space.

## Algorithmic refinement

The retained digit_swap with q=2 splits each (a,b) pair into four sequential
buckets, then reads bucket[b][a] when emitting the output position(a,b).
Counters copy encoded before/middle/suffix extents; payload values never enter
an address calculation. Each bucket is read exactly as often as it was written.
Thus the routine exchanges two single binary address digits with the supplied
spectators, preserves its borrowed source, and returns a fresh complete output.
Its source copy_bits, Counter and Natural bodies are unchanged.

For H>0 the retained atom_swap first sets gap=G*2^(H-1) and
tail=S*2^(H-1), pre=A. At digit pass i=0,...,H-1 it uses

    pre=A*2^i, gap=G*2^(H-1), tail=S*2^(H-1-i).

Its source radix_power iterator obtains H iterations by repeatedly dividing
the modulus2^H by2. The new service instead copies the already supplied encoded
H into an unchanged Counter. The preparation Counter omits its first doubling,
and each later pass doubles pre and exactly halves tail. Consequently both
programs make exactly the same ordered digit_swap calls on the same streams.
This is a mathematical iteration-count refinement, not an unexecuted Ring
supplier: no modulus, numerical arena or selected vocabulary is needed by the
new algorithm. The digit passes exchange the two complete H-bit fields in

    prefix, first, middle, second, suffix

while preserving internal bit order and every spectator. This can also be
verified inductively by exchanging the next corresponding binary digits; the
formula above tracks the spectator suffix between consecutive digit pairs.
For H=0 the new service performs a charged identity copy into its owned output.
This repairs the ownership ambiguity of returning a borrowed input at zero
passes. For H>0 the final private digit output is physically copied into the
fixed output port and erased; the new price includes that copy.

The original Binary wrapper's q2 padding has zero added rows. The new API does
not execute its redundant padding/restriction copies and does not claim their
old bill. It implements the same binary permutation directly, under its own
complete entry, ownership and price theorem.

## Fixed inventory and source allocation transport

Only three reachable module globals allocate scratch: stream.Tape inside
Counter, cardinality.Tape inside Natural, and bitstream.Tape inside digit_swap.
Bank.installed temporarily binds exactly these globals to a fixed allocator.
The original Tape constructor is sealed during execution. No selected loader,
controller.Callback adaptation, exception recovery factory or hidden native
constructor is installed. These global bindings are restored on every exit.
No imported unused Word/record helper is called by this execution path.

A lease denotes one of16 fixed physical slots. acquire scans this finite
inventory, chooses a free empty slot, and binds an active owner. clear physically
erases that slot's body before releasing it. Source local variables retain only
a bounded number of leases; a lease object is a finite slot/active/owner control
record, not another physical tape. No history of released leases is retained.
The Python identity check implements owner equality in this finite control.
Repeated close is rejected rather than being allowed to erase a later owner.

The exact live-role upper bound is13, independent of encoded H,A,G,S:

- preparation has three Naturals and one width Counter:4;
- each pass retains three Naturals, one width Counter and at most one previous
  digit output:5;
- a digit pass needs four buckets, outer and middle Counters and at most one
  copy_bits Counter:7 more;
- its merge additionally retains its new output:one more.

Thus5+7+1=13. Constructor-time and zero-pass cases are smaller. The previous
output is erased only after the next digit pass has returned; no live input
lease is prematurely reused. Source Counter.close, Natural.close and bucket
cleanup end every temporary lifetime. The fixed output lies outside the16-role
bank. Source rewind/clear routines restore cell1; Bank.empty checks the boundary.
All successful-call bodies and descriptor copies are cleared. The owned LEFT
markers are deliberately retained across calls and disposed once at close.

## Explicit conservative source-operation price

This is a source finite-symbol/tape model, not a materialized binary transition
table or a hosted Python instruction-time claim. A read, write, unit move,
finite carry/branch/assignment and fixed-slot bookkeeping step costs one. The
control states of multiply/divide-by2 are bounded carries/remainders. Bank
allocation scans at most16 slot flags; its inspection counters are observers,
not decisions. Input values and countdowns remain on tape. Constant-size call
frames and local lease references can be represented in finite control.

Put D=H+bitlen(H)+bitlen(A)+bitlen(G)+bitlen(S)+4. Every live numerical tape
has at most D significant/framing cells up to a harmless constant. Each source
helper's per-bit loop has fewer than128 such primitive/control operations,
including lease acquisition/release. Counter construction/close and one worst
case decrement, a Natural doubling/halving, descriptor validation, and their
head returns are each below1024(D+1)^2. This intentionally ignores the source's
stronger amortized countdown estimate.

In one digit pass every positive suffix block contains at least one payload
bit, so the number of copy calls, outer/middle iterations and Counter lifetimes
is bounded by a constant multiple of V+1. There are two traversals; each visits
V payload bits. Bucket setup/rewind/erase and complete source/output returns add
only a constant number of linear scans. Bounding these by64(V+1) helper/scan
units and allowing another factor16 for the finite loop/control structure gives
at most2^20(V+1)(D+1)^2 per pass. Preparation has H-1 doublings, two width scans
and fixed descriptor copies; the final output copy/disposal is linear. The same
allowance for one extra pass covers them and the17 initial/disposal markers:

    E(H,A,G,S) = 2^20 (H+1) (V+1) (D+1)^2.

This is deliberately loose. It includes initialization and successful close,
and applies to one call. For a sequence, summing these per-call bounds safely
pays shared initialization/disposal more than once. The verifier records actual
Tape traffic including the constructor writes, and tests it against the bound;
finite observations do not prove the uniform bound.

## Actual raw compact caller

Raw specializes the source's ten-shear word to u2,t2,y8,back2, target position2.
Its data and ROM ports are distinct from all28 private ports. Its input is196608 bits:16384 arbitrary12-bit records in lexicographic
(u,t,y,back,payloadbit) order. ROM is a separate borrowed32-bit tape with the
same LEFT/blank framing. Define f(y)=ROM[y mod32]. For the source good-set/ideal
switch interpretation require f(y)=f(y xor4); the raw permutation itself is
well-defined for any supplied Boolean table. The whole input and ROM are
serialized entry data; producing the ROM is outside this boundary.

The two y rotations are, modulo256,

    y += 8*(u mod2)*t;       y += 4*(u mod2)*(1-2*t).

The t rotations, modulo4, add y[2] and subtract y[2] xor(u mod2), respectively.
The u rotations add f(y), then subtract its newly read current-y value. The
schedule is F, u+=f(y), F, u-=f(y), where F contains the four y/t rotations.
Every t or u update first exchanges that field with the trailing dirty back2
field, performs a target-last complete-fiber rotation, and exchanges it back.
The u descriptors are(2,1,1024,12); the t descriptors(2,4,256,12). There are
six exchange pairs, hence twelve actual standalone calls. Each pair restores
back at all addresses; no good-set assumption is used for back restoration.

compile_rotation is an offline fixed-geometry compiler. Its prefix enumeration
is never decoded from runtime data. The resulting immutable ordered node list
specifies each complete coordinate fiber at its current physical position.
For a cut c, copy the first(radix-c)*tail bits into left and the last c*tail
bits into right, then emit right followed by left. This implements addition
of c to the target coordinate, including modular wrap and zero cuts. All
buffers are physically cleared before the next fiber. Runtime u-source cuts
are selected by actual ROM reads at the compiled current y index, followed by
ROM head return. No host function computes a source value or rotation cut at
runtime. The fixed PREVIOUS table encodes bounded copy counts as finite control
states; it does not contain input values or a host-decoded address.

The source arithmetic above and the fiber permutation establish equality with
compact for every input payload. This is a written fixed-geometry proof, not a
claim that one12-bit label pattern uniquely names every14-bit address. Tiny
independent-column tests and the actual complete fixture corroborate it.
Raw consumes and rewrites its owned data tape through charged copies; it returns
the same data object with the raw S-image at head1. ROM bytes/head are preserved.
Its28 private physical roles are the17 elementary roles, eight fixed descriptor
tapes and three rotation tapes. close erases all28; the result data and borrowed
ROM are not disposed by this owner.

For a conservative whole-raw source-operation bound use12 times the maximum
E for its two descriptor tuples plus2^16(V+1). The latter covers all ten fiber
rotations, the twelve caller-side output transports,8192 ROM lookups of at
most31 forward cells plus return, descriptor setup/disposal and fixed schedule
control. A rotation/transport is at most128(V+1) operations per scan group;
there are fewer than64 such groups, and ROM traffic is below128*8192. These
terms are comfortably within the displayed extra allowance. The implementation
records physical read/write/move totals separately from new bounded control
counters. It does not relabel those observations as an exact all-source
instruction count.

## Remaining boundaries

The unchanged #5105 parser rejects48-bit string records. This package returns
the binary raw stream and does not invoke that parser or claim repaired output.
A separately paid four-column interface is needed. The supplied-ROM production,
all-size CRT evaluator/source amortization, full E, current selected/native
supplier admission, full binary lowering, precision and outer multiplication
remain open. No selected result or kappa changes. Exceptions do not have a
transactional rollback guarantee; all success/ownership conclusions use the
stated typed domain. Original sources and guards remain unchanged.
