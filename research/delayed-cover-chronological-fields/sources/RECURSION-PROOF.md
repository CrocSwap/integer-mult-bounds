# On-path physical recursion at fixed atom width

## Scope and precise source specialization

Fix L>=2, q>=3 odd and N>=1 before execution. For the actual delayed cover,
q is the eligible fixed prime, L=B*|GL_N(F_q)| and b=q^(N*N). All these are
finite template constants. The actual source fixes w throughout one stopped
recursion T(n,w). We do the same and generate H=b^(w-1) from its physical
root width header. A sequence of different widths is not introduced.

The root descriptors are canonical positive LSB-first binary w,A0,R0 and
a readonly unary string of d=D-1 ones. On the source domain, for T,R_body>=1,

    A0=T*(L*H)^d, R0=H*R_body, V0=L*A0*R0.

Each descriptor is an actual marked physical packet. All other local banks
start physically blank after their fixed segment marker. No H value, child
grant, decoded root descriptor, parent pointer or runtime callback is supplied.
Producing w and d from an outer integer input is a separate boundary.

The fixed grammar recursively visits bank 0 and bank 1. At remaining depth
zero it complements bank 0 and merges all L banks. This is an arbitrary-bit
production/return mechanism, not a Gaussian child or a complete BIT supplier.
The mathematical source connection is the exact batch and continuation ABI;
the final compiled BIT template's local word is not substituted for this leaf.

## Literal finite control

`recursive.build(L,q,N)` emits one finite table of the retained PR2776
instructions `branch`, `write`, unit `move`, `goto`, `halt`, `reject`.
Execution is solely by that retained microinstruction machine. Branches inspect
one scanned symbol. Targets and tape numbers are compile-time constants.
There is no high-level recursive interpreter, callback instruction, runtime
allocation or multiplication/division primitive in the emitted table.

For L=4,q=3,N=1 the single table has 20,897 instructions and 25 tapes.
Exactly the same table executes every width, depth and payload in the stated
domain. The Python recursion in the separate expected-output oracle is test
instrumentation and supplies no program value or branch.

The physical stack alphabet is bijectively renamed into the retained machine
alphabet. Physical binary zero/one are distinct nonblank symbols. A logical
router symbol is its three physical binary digits; logical BLANK is 000,
which is real backing, not physical blank. `code_branch` reads the three
bits through finitely many states and restores the physical head. A physical
blank at the code origin implements logical BLANK. `code_write` writes the
three bits and restores its head. `code_move(+1)` materializes 000 before
crossing a physical blank and then moves exactly three unit steps. The reverse
move is three unit steps. These are the retained stateless codec semantics.
Each lowered logical instruction takes at most 32 physical microinstructions.

The existing router and shape-producer tables are linked at compile time,
with each branch target statically relocated. They are not interpreted as
runtime callbacks. Their exact source bytes and the stack/return predecessors
are pinned in SOURCES.json.

## Producing H from the root width

`high_program` starts an owned binary H at one and converts the preserved
positive width w into a unary guide through the unchanged counter microcode.
It skips the first guide mark, then multiplies H by b once for each remaining
mark. Multiplication scans the LSB-first bits in place. Its carry belongs to
the fixed finite set {0,...,b-1}. For old bit x and carry c, the emitted state
writes (b*x+c) mod 2 and moves to the state floor((b*x+c)/2). Those two values
are calculated while assembling that finite state, not during execution.
At RIGHT it emits the remaining fixed carry bits and a new RIGHT.

Induction on scanned digits proves ordinary multiplication by b, with a
canonical positive result and the head returned to its body origin. Induction
on the width guide therefore gives H=b^(w-1). The width header is preserved,
the guide and conversion work are erased, and their physical 000 backing is
also retired. H is now immutable across every node; only its head moves during
descriptor conversion, and that head is restored. H is physically retired
after the root invocation completes.

This is standard fixed-constant arithmetic, credited as such. The new use is
to remove the external H grant from the actual recursive control path.

## Entry, CALL and RETURN invariants

At node depth j, with 0<=j<=d, the live input descriptors and stream are

    A_j=T*(L*H)^(d-j), R_j=H^(j+1)*R_body,
    V_j=L*A_j*R_j=V0/L^j.

The readonly unary depth head is j positions after its root origin. It sees
one exactly when j<d. The current node's entire source packet and two binary
headers are its live inputs; ancestor payloads lie below physical delimiters.

The node first executes the unchanged full split. If j<d, immediately before
each statically named CALL it runs the retained shape table on its **current**
A_j,R_j and the generated H. Exact divisibility holds because d-j>=1, giving

    A_child=A_j/(L*H), R_child=H*R_j.

The generated grants are actual owned packets in that node's frame. Their
unary/conversion work is erased. The selected complete bank and both grants
are copied to three fixed BASE relays; the local grant packets and all coded
scratch backing are physically retired before push. Thus no parent's grant
cache or host list supplies a grandchild.

The node writes one physical phase bit naming its fixed call site, and the
literal stack push records the payload heads and that phase. It appends a
child delimiter to every fixed payload tape. The child inputs are then copied
from the relays to these empty segments; all three relays are erased before
the program reenters its single node-entry state. The depth head moves right
once. No host stack retains a continuation.

At child completion, the entire output packet is copied to a fourth separate
relay **before** retiring the child fields or popping. All child payloads
are then physically retired. The literal pop restores every parked parent
byte and exact head, restoring its physical phase. The depth head moves left
once. The protected output is installed in the previously empty reserved
return role, then replaces only the selected owned parent bank. The return
role, relay and phase are erased. Phase zero continues with site one; phase
one continues to merge. Both branches are finite control labels.

The root is identified from the actual previous control marker BASE rather
than END. It delivers its output without pop, erases generated H, and halts
with the root inputs and heads preserved. All other owned banks, relays,
control and phase bodies are physically blank. Segment markers and the
visited backing remain charged; clearing does not deallocate a physical cell.

## Whole-high address and endpoint induction

At a fixed parent low bank, write

    a_parent=(a_child*L+l_child)*H+h_child.

Then exactly

    a_parent*R_j+r_parent
      =(a_child*L+l_child)*(H*R_j)+h_child*R_j+r_parent.

The child receives all parent high and earlier ancestor/body coordinates,
with R_child=H*R_j. It does not receive the false smaller volume V_j/(L*H).
The inherited split and merge are inverse address maps on these complete
packets. Their arbitrary input bits are never presumed zero or duplicated
for productive credit.

At j=d, the literal leaf complements bank zero and merge gives its exact
full-packet endpoint. Inductively, the two child outputs are computed on
arbitrary complete selected banks and installed only after protected return.
All other banks are unchanged. Merge therefore yields the recursively
specified endpoint on every input. CALL decreases the remaining unary length
and RETURN restores it, so this induction also proves termination, complete
parent restoration, and reuse between siblings at every finite depth.

This proves a scoped all-depth machine property. The finite cases alone are
not used to infer the induction.

## Complete time and retained-space envelope

Write k=K=max(16,L+11), e_b=bitlength(b). The payloads include two local
grant banks, one extra guide and a distinct reserved return role. Nine global
tapes hold control, phase, four transfer relays, unary depth, root width and
generated H. There are k+9 tapes at every width and depth.

At a node V=L*A*R, A,R,H<=V on the source domain. At an internal node
A>=L*H and H*R<=V/L^2. The retained shape proof bounds its whole generation
and delivered-grant consumption by 1000V logical steps. There are two such
generations. Split and merge together use at most188V logical steps.
The codec bound therefore charges at most 64,000V+6,016V physical steps
for these linked tables. No quotient or unary setup is treated as free.

For completeness, a coarse direct bound suffices for the raw continuation
loops. The current source, banks, possible output/return, binary headers,
unary guides, conversion work and their code/markers occupy fewer than100kV
physical positions in one local frame. Every binary header length is bounded
by its positive value; all unary guide lengths are bounded by A+H+R. A stack
record adds one presence bit per payload, unary saved head offsets bounded
by those same local extents, separators and one phase bit. A complete raw
copy/retire/push/pop pass uses at most a fixed 128 microinstructions per
scanned position. Per call site there are fewer than64 aggregate raw helpers in the
emitted source; an aggregate push/pop counts all payloads together. Each
helper uses at most four complete scans or rewinds of its participating
local/relay extent. Both sites therefore use at most512 such passes per node.
At128 steps per position and100kV positions this costs at most
6,553,600kV steps, with per-tape markers included in the larger bound below.

Width conversion costs at most44w logical steps. Each fixed-b multiplier
uses O(e_b*w) logical steps at its largest width; summing w-1 multiplications
costs at most (100+20e_b)w^2. For b>=3, w^2<=2b^(w-1)=2H. Since H<=R0<=V0,
the once-only H generation and its actual physical scratch retirement are
also covered by the following explicit coarse constants:

    C_time=10^8*(k+e_b+1), C_space=1000*(k+e_b+1).

For the actual emitted two-site grammar, including setup, generated grants,
all routing/copy/erasure, protected return and root H retirement,

    time <= C_time*V0 + C_time*sum_over_nodes V_node,
    local visited/retained backing
      <= K_entry + C_space*V0*sum_(j=0..d) L^(-j)
      < K_entry + 2*C_space*V0.

K_entry includes supplied inaccessible prefixes and input backing. The time
sum is V0*sum_(j=0..d)(2/L)^j for these two sites. It is not a universal94V
bound. If a final template has c compiled recursive call sites, its required
bill is the actual occurrence recurrence c*T_(d-1)(V/L)+C_time*V; this package
does not replace c by two when pricing that different template.

Sequential sibling calls reuse restored suffixes. Packet lengths and parked
head offsets depend only on the stated shapes, not numerical payload bits.
They cannot accumulate a new backing block per completed sibling. Along an
active chain the V/L^j geometry bounds data, descriptors and stack records;
root width/depth/H work is already included. Physical 000 backing is explicitly
erased and its visited extent remains in the bill.

## Evidence and executed controls

The same table is executed on the actual GL1 source shapes w=1 at depth0,
w=2 at depths1 and2, and w=3 at depth1. The two-level case has

    (A,R,V)=(144,3,1728) -> (12,9,432) -> (1,27,108),

seven actual machine entries and six protected physical returns. The observer
checks every generated grant, the live child headers, all parent bytes/heads,
ancestor delimiters, the complete root endpoint, absence of writes to original
source/header bytes and actual owned erasure. It supplies no program branch.

Literal-program mutations omit output protection, omit depth restoration,
or replace the global H wire by the current parent R wire. The last mutation
passes the one-edge case because R0=H, but fails on actual grandchildren
where R1=H^2. This distinguishes the new on-path connection from another
root-precomputed one-edge fixture.

## Remaining production boundary and credit

The source's numerical ancestor weight descriptor, local ordinary BIT leaf,
fixed matcher/fallback routes, production stock and precision interfaces are
not executed here. Root w/depth generation from the external input is also
not claimed. A shape header does not determine those numerical descriptors.
No new paid invoice, kappa, final-template implementation or scientific
admission follows from this scoped control result.

PR5829 supplies the address/space lemma. PR2776 supplies the finite machine,
counter and assembler. The retained stack and output-before-pop protocol,
PR6719 codec/router and shape-producer predecessor retain their original
credit. Fixed-constant arithmetic is standard and overlaps the already cited
binary-control/R437 work; it is not claimed as a new arithmetic theorem.
The new contribution is their emitted finite recursive connection with
generated live-frame grants and the explicit scoped induction/bill.

Prepared for thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
Independent static review is pending; this is author-side evidence.
