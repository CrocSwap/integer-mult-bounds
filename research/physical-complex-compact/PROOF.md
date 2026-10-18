# Encoded physical completion of the compact operation

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I refine the compact algorithm from PR2250, head
`d404b48a1e7b147556b309497d55089c837dddb2`, into marked unit-step streams and
encoded control arithmetic. I use PR2899, head
`2f0911ad735643a069b9790302fbf179e49f74f8`, for the completed binary ordinary
callee. I preserve those exact archives and their source arguments. I do not
derive their universal claims from the small fixtures in this package.

## 1. Domain and result

Fix a finite field schema with m named fields. Compile distinct wide source and
target names, or a constant toggle, and the earlier/later source order. Supply
canonical Count tapes for n>=1, K>=1, G>=1, 0<=rho<K, each field width, positive
record width R and arbitrary positive outer-row count C. Supply the complete
payload and borrowed parameter tapes with their heads at their local origins.

Require width `(n+1)K` for each wide source/target. Require width nG for u,t,b,
with u and t before the target and b after both wide slots. Require the declared wide-source
order. Additional complete spectator fields may have width zero. These are
exactly the fields the local operation visits; external parked regions remain
outside its owned inventory.

Write

    f=n+1, a=sum(field widths), M0=2^a, v0=M0*R,
    M=C*M0, V=C*v0, A=2+a+ceil(log2(R+1)),
    delta=min(1,n*(2*2^(-G)+8*2^(G-K))).

I implement XOR from the source into the target at positions `rho+jK`,
`0<=j<f`, or toggle those positions for a constant source. I restore u,t,b,
the wide source and unselected bits, preserve each R-bit record's order, and
return rows in their original order. I preserve the borrowed input and parameter
tapes and return a distinct protected output at its origin.

Assume a completed binary ordinary upper bound

    T_B1(v,b) <= K_q*v*(1+b^tau),  0<tau<=1,

with arbitrary complete spectators, preserved source and restored owned work.
The pinned B1 supplies `tau=99830289/100000000` under its named C0 endpoint,
chronology, refinement and cost arguments. I require an eligible fixed prime q
for that asymptotic statement. Small tests at q=2 or3 have their stated fixture
scope and do not establish that large-prime theorem.

I obtain the complete time bound

    s*sum_(j=1)^C T_B1(v0,nG)
       + O_m(V+M*A^6+delta*M*A*(R+A)),

where s=4 for an earlier source or toggle and s=12 for a later source. There
are sC actual binary calls. I use the volume-linear upper bound to sum their
costs; I do not replace them by s whole-packet executions.

In the retained domain `f<=p`, `A=O(p)`, `G=4*ceil(log2 p)+6`,
`K/log p -> infinity`, with R exceeding each fixed power of p, I obtain
`O_q,m(V*(1+((f-1)G)^tau))` time and linear workspace for a fresh invocation,
plus fixed compilation storage. I retain the displayed terms at independent
finite sizes. I state occupied and retained backing space separately below.

I prove successful admitted execution. I make no rollback guarantee after an
interrupted or invalid internal operation. The caller consumes the protected
output before reuse. I do not complete a Gaussian monomial, recursive complex
layer, formal machine refinement or multiplication theorem in this package.

## 2. Encode the numerical controls

I keep numerical parameters, field values, extents, keys and loop indices on
canonical binary Count tapes. I use the inherited ripple Counter for countdowns.
The fields' names, their order, the finite operation tags and source-order flag
belong to compiled control; I do not decode widths or addresses into that control.

`compact_counts.py` implements variable bit windows, shifts, XOR, modular sums
and fixed-width key serialization through sequential reads, writes and unit
moves. I build an empty Count body through its borrowed physical view so that
I retain its active scratch lease. I normalize the result and release the lease
only when the Count closes. I include discarded high zeros and markers in the
write/erase accounting.

`compact_layout.py` constructs field radices and complete-row extents by encoded
arithmetic. I decode an address by repeated binary division through the fixed
field tuple, and encode it by the inverse multiply/add sequence. Prefix decoding
sets later fields to zero; rotation controls all precede their target, so those
zeros cannot change the offset. I use a fixed number of field Counts, not one
control register per address or per selected digit.

For `compact_control.py`, I copy the finite operation word from the authenticated
PR2250 `operations()` method. Its dummy numerical constructor constants never
enter runtime arithmetic. I implement offsets, inverse execution, selected masks
and the guard in the new encoded routines. The checker disables the reference
class's numerical methods during physical execution.

For each of n digits I extract the source bit and dirty t digit and accumulate
the packed offset modulo the target radix. For `1-2t_i`, I branch only on zero:
otherwise I form the positive magnitude `2t_i-1` and negate its reduced residue.
I retain modular overflow on exceptional addresses. During inverse execution I
reverse the finite word and evaluate each offset on the current inverse state.
I never use the original forward controls for a later inverse step.

Let `B=2^G`. I test the original guard using encoded comparisons:

    t_i < B-1,
    2B <= g_i < 2^(K-1)-2B,
    u_i < B-1 for a later source,

where g_i contains the K-1 target bits above selected bit i. If
`2^(K-1)<=4B`, I mark the address exceptional: the guarded interval is empty.
This handles negative or empty upper thresholds without unsigned underflow.

## 3. Realize the raw word and binary boundary

I retain Douglas Colkitt's raw modular word and the proof in PR2250. An earlier
source or toggle uses four rotations and four width-nG swaps. A later source
uses ten rotations and twelve swaps. The scalar dirty-control identity is

    y += 2*z*t;
    t += parity(y);
    y += z*(1-2*t);
    t -= parity(y) XOR z.

On the guarded packed domain, this toggles the selected parity by z and restores
t. The load/unload swaps move a front compact field to the complete back field;
they do not initialize the original dirty back value.

For a rotation with target radix Q and suffix extent L, I compute the offset
u modulo Q from the encoded prefix ordinal. I split the next Q blocks into
lengths `(Q-u)L` and `uL` on two owned streams. I recompute the same offset during
merge and emit the second piece before the first. Both traversals enumerate
prefixes in the same order. Thus I realize the modular address rotation for
arbitrary wraparound while preserving the order inside each suffix block.

For a compact swap I derive the complete preceding, intervening and trailing
extents from the fixed field schema. I suspend the compact allocation scope and
invoke the actual `Binary.run` with borrowed physical views. B1 uses its own
fixed roles and its sealed C0 path. After return I restore the compact scope,
copy the protected binary output into an owned lease, and clear its output and
marker. I then consume the old owned row stream. This preserves B1's source
contract and the compact interpreter's consuming-intermediate contract together.

I use the binary interface here. PR2899 pads each active field to the least
q-power above `2^(nG)` and restricts afterward; its native volume is below
`q^2*v0`. Its bound already includes that fixed factor and its internal reserve.
The native same-q shortcut used by the BIT successor does not apply to these
binary compact fields.

## 4. Complete exceptional repair and the final bit

Let S be the raw word and T the desired operation on its low n selected bits.
I retain the original exceptional set E. From PR2250's guarded identity, S=T
on its complement. T preserves E because it changes selected parities while
fixing the guard bits and dirty compact labels. Each raw rotation has a
target-independent offset, and each swap is invertible. Thus S is a bijection;
since it agrees with T on the complement, it also preserves E.

I enumerate current row addresses q with an encoded counter. For each record
I append its exception flag to the hole stream. I append a good record to the
good stream. For an exceptional record I compute the full encoded destination
`T(S^-1(q))` and append its fixed a-bit key followed by its opaque R-bit record.
I use current inverse controls and the declared modular field widths throughout.

`stable_radix` performs a literal stable two-bucket partition for each key bit,
from least to most significant. It reads one key into a Count, visits the
encoded pass position, writes the fixed-width key and copies the complete
record into the chosen bucket. It concatenates bucket0 then bucket1 and clears
the old stream and buckets. Induction on the pass position gives increasing
order of the processed suffix of each key, with stability among equal suffixes.
After a passes I obtain full numeric key order. I allocate no bucket per key.

Because `T S^-1` permutes E, its destination keys are distinct and occupy
exactly the recorded holes. During reinsertion I consume the next good record
at a zero hole. At a one hole I read the next sorted key, require equality with
the current encoded address, and consume its record. I check complete exhaustion
of all three streams, clear them and rewind the output. The resulting payload
has the low-selected endpoint T on the original input.

I then apply the highest selected bit at `rho+nK`: a toggle or an XOR from
the matching source bit. I derive its absolute address position on Count tapes.
The toggle uses two complete suffix buckets; XOR uses four, with a fixed
four-state permutation. I preserve the intervening and trailing extents and
erase each owned bucket after its complete slab. This gives the requested f-bit
endpoint and restores all other labels.

I repair one complete outer row at a time. The raw and ideal words preserve
that row label, so the domain is closed under both. A fixed dirty-field slice
need not be closed. For example, the retained n=2,K=2,G=1,rho=1 early word sends
`(u,t,x,y,b)=(0,1,2,2,0)` to `(0,3,2,8,0)`, whereas the ideal low endpoint is
`(0,1,2,0,0)`. Repair must cross the two t slices. I retain that witness as a
control and do not partition repair along dirty coordinates.

The outer loop copies one complete row from the borrowed source, finishes its
operation, appends its result to the protected output and clears the row lease.
I advance the source cursor without rereading earlier rows and rewind it after
the complete packet. I reassemble all rows before return; I introduce no complex
child per row and no altered recursive schedule.

## 5. Charge arithmetic, sorting and disposal

All new field/control operands have O(A) bits. A shifted packed term can exceed
its target width before reduction, but its bit length remains O(A): it has at
most one compact digit's width plus one wide-field position and a constant
margin. The number of fields and raw operations is fixed.

The inherited Count product and division use O(A) iterations of linear scans,
so I charge O(A^2). Dynamic power and shift routines perform at most O(A) such
linear scans. Bit windows and the fixed tuple's encode/decode routines have
polynomial cost. An offset processes n<=a digits; O(A^3) suffices for its shifts,
modular reductions and sums. I use the conservative envelope O_m(A^6) for the
complete preparation, inverse, guard and key work, including counter setup,
normalization, copies, rewinds and erasure.

For each rotation I compute an offset twice per prefix fibre and move each
payload bit a bounded number of times. There are at most M0 fibres per row.
I therefore charge `O_m(v0+M0*A^6)` per rotation, including its piece-length
products and clearing. The highest-bit operation has one encoded extent setup
and linear complete-slab movement. A suffix counter's initialization costs
O(log(1+suffix)), which its ensuing complete suffix copy pays.

During repair I evaluate the guard on all M0 addresses and compute inverse
states and destinations on the exceptional ones. I charge `O_m(M0*A^6)`.
For each of a radix passes I move at most `delta*M0` records of R+a bits.
I include key scanning, serialization, bucket concatenation, rewinds and
clearing in `O(delta*M0*a*(R+a))`. Any conservative extra polynomial key-control
charge fits the already included `M0*A^6` term. Hole generation and reinsertion
add O(v0) movement. Empty exceptional streams need only the polynomial pass
overhead; they do not trigger a scan of the full payload for each radix bit.

I create `Counter(C)` once, outside these preparations. Its complete ripple
traversal costs `O(C+log(C+1))`; no row ordinal enters offset, guard, inverse
or destination arithmetic. Since each row contains at least one bit, I absorb
this charge into O(V). Initial row copies, final appending and the borrowed
source rewind also cost O(V).

I charge the sC binary calls with their individual row volumes, including the
returned-port copies and marker operations. The uniform B1 upper bound then
gives the time statement in section 1. I include fixed source compilation once;
fixed q-dependent marker work per call belongs to its volume-linear constant.

For asymptotic absorption, eventually `K>=G+4*ceil(log2 p)+10`. With n<=p and
the retained G, the source estimate gives `delta<=5/(128*p^3)`. Consequently

    M*A^6/V = A^6/R -> 0,
    delta*M*A*(R+A)/V = delta*A*(1+A/R) = O(p^-2).

I obtain the stated compact bound in that domain. I do not infer a practical
cutoff or use finite timings to establish it.

## 6. Fixed roles, blank return and backing extent

I allocate `8*m+256` compact scratch tapes before reading numerical inputs.
The layout retains m+3 Counts; at most one decoded state retains m Counts;
fewer than 64 additional Count, Counter and payload roles suffice for the active
branch, including nested product/division temporaries, keys and buckets. I close
predecessors before advancing or replacing a result. Thus `2*m+64` gives a
conservative live census within the configured allowance.

I count the protected output, borrowed descriptors, Binary's 96-slot pool and
the native ordinary inventory separately. I suspend the compact factories
while the binary/native scopes use their own roles. The global constructor
guard remains active during this switch. I never allocate a physical tape per
row, prefix, selected digit, exceptional key or radix pass.

For occupied contents, a conservative compact-side envelope, including borrowed
input and protected output, is

    4V+2*delta*M*a+M+O_m(A+log(C+1)).

I include the good/bad/hole streams, current/output row streams, key buckets
and fixed numerical operands. I add B1's private workspace and fixed source
compilation storage. In the long-record domain, `a/R` is bounded and I obtain
linear occupied workspace.

I distinguish erasure from backing allocation. The retained Tape implementation
blanks its cells but does not shrink the Python bytearray. For a fresh engine,
each compact-pool tape has maximum extent

    O(v0+delta*M0*a+A+log(C+1)).

Multiplying by the fixed pool capacity bounds its backing storage. I add the
global input/output and the inherited B1 backing allowance. For a reused engine,
I take each role's maximum extent over preceding invocations. I do not bound
retained arrays from an earlier larger input by a later smaller V. If these
calls belong to one enclosing invocation, I use that enclosing volume to bound
the maxima, with its retained source allowances.

On successful return I require no live scratch leases, erase their markers,
close numerical contexts and leave their heads at their local origins. I retain
only the protected output contents. At reuse I restore blank markers with local
writes. I do not scan an old blank backing tail to reclaim it. This gives the
claimed locality independently of earlier physical extents.

I treat Python object bookkeeping, Tape meters and provenance masks as simulator
or checker machinery, not extra numerical registers of the tape program. The
implementation selects no instruction or operand from those observations. I
have not expanded this structured program into a complete transition table or
proved its correspondence in a proof assistant.

## 7. Evidence and the remaining complex boundary

I compare encoded controls with the authenticated indexed oracle on 151 states,
including 904 offsets, both guard regimes, modular inverse chronology and the
cross-dirty-slice witness. I check complete physical early/late/toggle rows,
odd-prime binary padding, reuse after erasing the protected marker, and two
complete 4096-record two-digit rectangles. I check 8192 mixed-guard records
through actual raw movement, repair and the final bit. For payloads I carry an
independent mask per input bit in checker state while runtime cells remain
Boolean. I disable indexed reference arithmetic during physical execution.

The separate 1024-column handoff uses the actual Binary wrapper and a declared
reduced fitted B1 body with two C0 roots. I verify its live parent numerical
objects and suspended factory scope. The small complete Compact cases use
B1's elementary branch. I retain its universal faster-rate argument as an
explicit predecessor, not an inference from those timings or endpoints.

The failure controls reject omitted repair, omitted inverse-key computation,
reversed radix order, altered source archives, namespace contamination and
physical allocation inside a sealed call. I also reject reuse of an unconsumed
output while preserving its contents. These controls do not establish recovery
after an arbitrary internal interruption.

PR2534 already executes selected child 7 with retained Compact on complete dirty
outer rows. I add encoded controls, fixed physical roles and the actual B1
boundary. I do not claim that earlier fixture as new work. PR2378/2422 supply
separate formal phase results; PR2476/2700/2756 supply repair accounting and
partition boundaries. I preserve that division of scope.

A complete Gaussian monomial still needs its encoded phase pass and signed
record traversal, followed by integration with the actual complex caller,
proper-width children, private lifetimes and root precision grid. The written
PR2287/2298 implications remain separate from that payload execution. I leave
the selected exponent unchanged. I also do not transfer B1's coarse rate to
the higher modern candidate in PR2979: that would require a stronger ordinary
contract or a different transfer argument.
