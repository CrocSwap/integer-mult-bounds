# Independent static review of the recursive core connection

**Conditional PASS for the literal on-path CALL/RETURN and whole-high contract.
No blocking functional gap found under the explicit entry, primitive and owned-
growth premises below.** This review concerns current PR6719 source head
`e4e52d6ba2c805fa78bb57778c3b7bbc064edba5`, not the earlier one-edge snapshot.
I read the retained core PROOF/CONTRACT/README/recursive.py text, shape producer,
router, counter and machine-definition dependency text, plus only the supplied
ENTRY-EXCERPT. I did not read the full source checker/observer, expected results,
peer draft or source receipts, and did not import, compile, execute, simulate or
regenerate a program. All controls below are written arguments, not runs.

## Entry ABI and exact role separation

The router's actual ports are banks0..L-1, sourceL, outputL+1, binary A/R
inputsL+2,L+3 and scratchL+4..L+6. Core grants areL+7,L+8 and the additional
R guide isL+9. With K=max(16,L+11), reserved return K-1>=L+10 is distinct
from every one of those roles. Control,phase,four relays,depth,width,H are
K..K+8, all outside the payload range0..K-1 and pairwise distinct. This
resolves the import-dependent mapping; no assumed alias or dynamic tape choice
is needed. The actual dependency path is core/inputs/shape/producer.py,
whose machine/router/counter imports are under shape/inputs/PR6719/.

The supplied entry excerpt establishes two separate layers of marking:
all payload tapes have an outer physical LEFT marker, all nine globals an
outer BASE marker; logical packets are then encoded as three physical Z/O
symbols per logical symbol. Source,A,R,width include encoded logical LEFT,
positive canonical data where applicable and logical RIGHT. Their entry heads
are after the three-bit logical LEFT. Empty local work/output banks begin at
the first physical blank after their outer marker. Depth is instead a raw
readonly run of physical O marks, with its head at the first remaining mark
or the terminating physical blank. It is not a coded binary descriptor.

These outer markers and initial packets are **entry premises**. compile()
does not manufacture them from unmarked tapes, nor derive root w/depth/source
payload from an external integer. Their initial backing is charged in K_entry;
any production/initialization time before this program's entry is outside the
reviewed execution contract. All owned growth extents must really be blank;
they cannot contain arbitrary occupied cells disguised as workspace. No
rollback/cleanup guarantee is inferred for malformed inputs.

## Lowering and contiguous physical backing

Builder.logical statically relocates every source branch case, default and
goto to fresh labels. Source write/move fallthrough becomes the next lowered
source instruction, since labels are emitted in instruction order. Every
source halt becomes the named continuation; source rejection goes to the core
failure state. The runtime alphabet remains branch/write/unitmove/goto/halt/
reject. Python loops, constant arithmetic, importlib and metadata construction
occur during compilation, not as runtime operations on width/depth values.

The stack alphabet and encoded router alphabet cannot be confused. Physical
Z/O are machine ZERO/ONE; outer LEFT/BASE and control SEP/END are different
physical symbols. Every logical router symbol is encoded in Z/O only.
code_branch consumes exactly the three physical bits and moves back twice
after its two forward moves; the physical head is restored. It rejects code111.
A physical blank at an aligned origin represents logical blank under the valid
owned-empty ABI. code_write writes a three-bit code and returns to its start.
code_move(-1) is three unit moves; code_move(+1) first materializes logical
blank000 if the current origin was physically blank, then moves three steps.

That materialization is significant: a valid visited logical prefix has a
contiguous physical Z/O backing, including logical blank000, up to its first
physical blank. Raw copy/retire/park scans therefore do not stop at a logical
blank inside an allocated coded extent. Their preservation/retirement is not
obtained by treating000 as physical absence. On valid data each lowering
uses at most13 physical instructions for a source step, with one initial jump
per linked invocation; the retained coarse32 factor safely covers it. This
is a static macro count, not a claim that the emitted TABLE was regenerated.

## H generation and live descriptor connection

The high program maps its four logical roles to root width, global H and two
initially empty payload scratch roles. It creates H=1, converts the positive
preserved width to a unary guide, skips its first mark, and invokes the fixed-
base multiplier once per remaining mark. At each scanned old bit x and carry c,
writing(b*x+c) mod2 and continuing with floor((b*x+c)/2) is ordinary binary
multiplication by fixed b. The carry remains in0..b-1. Positive canonical input
has top bit1, so for b>=3 the final carry is positive and its drain ends in1;
the output remains canonical. The rewinds return to the first data bit.
Thus H=b^(w-1), without a host-decoded w or runtime arithmetic instruction.

Width is read/copied/rewound by the retained counter, not written. The guide
and work are logically erased, then the outer retire calls remove their real
coded000 backing as well. Global H is thereafter used only as the readonly
second input of the shape table, with its body head restored by that primitive.
The builder tests odd q>=3 and N>=1; it does not test primality or
L=B*|GL_N(F_q)|. Those actual-cover compile-time facts remain external premises,
not facts proved by the builder's argument guards.

At internal depth j, the retained producer is mapped to the live A_j header,
the global H header and live R_j header. Its output grants are fresh distinct
local roles. Under its named exact-division/cleanup ABI, they are
A_child=A_j/(L*H), R_child=H*R_j. The source specialization makes division
valid at every internal depth. No root-precomputed grant list supplies a
child's grandchildren, and substituting current R_j for global H is not what
the literal mapping does.

## CALL: capture before suspension, clear before reentry

After each split, site0/site1 is a fixed control label, not a tape-selected
bank index. The selected complete bank is raw-copied to the input relay;
its head is realigned to its logical body. Both grants are copied to the A/R
relays, then locally retired. Guides/work are physically retired. The phase
holds one raw bit,Z for site0 or O for site1, and push consumes it into the
control record before entering the child.

For each payload, push records a static role tag and unary head offset relative
to the nearest outer LEFT. It scans the parent's contiguous physical backing
and appends one child LEFT delimiter at its first physical blank. The child
segment begins empty immediately after that delimiter. The role tag for the
reserved return field isZ; all other tags areO. These tags are fixed ABI tags,
not a runtime inference that every other field contains a packet.

The three relays then initialize only child source,A,R. body() puts their
heads after their coded logical LEFT, while every other child payload remains
empty at its new origin. All three relays are physically erased before the
depth head moves right and control jumps to the single node-entry label.
Thus the next recursive CALL can reuse the same globals without aliasing a
live ancestor relay. Depth remains readonly; only its head is moved.

## RETURN: protect output, retire child, destructive pop

After the complete merge, temporary banks and router scratch are retired.
Moving one control cell left distinguishes actual root BASE from saved-frame
END. A nonroot first copies the entire coded output to the separate global
output relay, which is outside the K payloads. Only then does the loop retire
all K child payloads, including child source,headers and output. Their former
bytes were owned copies, not the original borrowed root inputs.

Pop requires these child heads at the blank immediately after each child
LEFT. It removes that delimiter, scans backward over the parent's unchanged
Z/O backing to its parent LEFT and restores its saved offset. If the saved
head was offset h from the first body cell, push recorded exactly h O marks;
pop advances exactly h positions and consumes those marks. Empty parent roles
have offset0. The control frame and its restored phase are consumed/cleared,
and control returns to the previous END/BASE top. No host parent pointer or
continuation is consulted.

The depth head moves left once and must see the parent's O mark. The protected
output is installed in the reserved empty parent return role; the output relay
is then retired. The restored phase selects the two fixed continuations.
The program clears phase, retires only the selected old parent bank, copies
return into that bank, retires return and realigns the bank body. Site0 then
continues to site1; site1 continues to merge. All other parent banks and the
parent source/A/R bytes are untouched. Their saved heads are restored before
the appropriate later primitive resumes.

At root completion, no pop occurs. The delivered output is retained, global H
is retired, and control returns from BASE to its original first blank. The
root source,A,R,width bytes and heads, and the raw depth string/head, remain
preserved. All other owned bodies are blank under the primitive exit ABI.
Outer markers and visited blank backing remain present/charged; erasure is
not physical deallocation.

## Whole-high address and all-depth induction

For a fixed parent bank, use the unique mixed-radix decomposition

    a_parent=(a_child*L+l_child)*H+h_child,
    r_child=h_child*R_j+r_parent.

The ranges0<=l_child<L,0<=h_child<H,0<=r_parent<R_j give a bijection.
Then the actual full-stream offset identity is

    a_parent*R_j+r_parent
      =(a_child*L+l_child)*(H*R_j)+r_child.

Therefore the child packet is exactly one complete parent bank, with
V_child=L*(A_j/(L*H))*(H*R_j)=A_j*R_j=V_j/L. No parent high/ancestor
coordinate was discarded. The inherited split/merge inverse maps apply to
these entire packets, rather than to a smaller volumeV/(L*H).

At remaining depth0 the literal leaf complements bank0 and merges all L banks.
At positive depth the two recursive calls use the above descriptors, preserve
all siblings, return their complete outputs and install them before merge.
Induction on the remaining raw unary marks therefore proves the stated endpoint
and parent restoration at every finite depth, conditional on the named split,
merge,shape,counter and machine contracts. The depth decreases before child
entry and is restored before a sibling call; this also proves termination.
There is no inference from a small fixture to arbitrary depth.

## Time and retained-space premises, with K-wide work aggregated

The named primitive bounds used by the source are: whole shape generation/
delivery consumption at most1000V logical steps; split and merge at most94V
each, hence188V together; and physical codec factor32. For two internal call
sites these contribute at most64000V+6016V physical steps. Their source proofs
are retained premises here, not independently recertified by executing their
checkers or rediscovering the underlying arithmetic.

Raw work must be bounded by the **sum** of the participating local extents,
not K times their maximum followed by another hidden K factor. One conservative
top-level helper grouping per call is11 before push,1 aggregate push,9 for
child initialization/relay retirement,5 for protection/retirement/pop/output
installation and5 for resume/bank replacement:31 groups. Finite phase/depth/
jump bookkeeping and node cleanup fit the source's looser fewer-than64 groups
per site. Every K-wide retire/push/pop loop is one aggregate group scanning
the sum of K local extents, not K separately charged maxima.

For example push costs at most a constant times sum(saved offsets)+sum(parent
extents)+K. Pop scans its control record, the parent extents and saved offsets
a constant number of times. A saved offset is bounded by its own local extent.
Raw copy/retire/body helpers similarly have constant passes, each with far
fewer than128 emitted steps per scanned position; four complete participating-
extent passes is ample for the source's coarse charge. Conditional on its
summed local/record extent bound100*K*V, two sites'512 passes give
512*128*100*K*V=6553600*K*V, not an O(K^2 V) accounting shortcut. The leaf
complement and per-node cleanup are linear local scans within the larger bill.

The once-only fixed-b work has largest binary length O(bitlength(b)*w), so
its w-1 multiplications cost O(bitlength(b)*w^2); the source's coarse
(100+20*bitlength(b))*w^2 plus44w conversion has ample finite-loop slack.
For b>=3,w^2<=2*b^(w-1)=2H (check w=1,2, then induct using
((w+1)/w)^2<=9/4<3 for w>=2). H<=R0<=V0. Thus this setup and its physical
scratch retirement can be included once in the declared C_time V0 term.
This static argument does not claim an exact20897-instruction count or a
fresh certificate of every numeric constant in the underlying primitive bills.

Along an active chain, the local shape volumes are V0/L^j. Marker,header,
backing and control-record extents are included in the per-frame budget, so
summing gives the stated geometric space form. Popped child delimiters/frames
are cleared, and the next sibling starts at that same first physical blank.
Payload bit values change symbols, not coded lengths/head ABI. Completed
siblings therefore do not append a new backing region per call. Initial
inaccessible prefixes, supplied descriptor backing and marker preparation
remain charged entry premises. The time sum is over all occurrences,
V0*sum_(j=0..d)(2/L)^j, not just the active chain; in particular L=2 keeps
its depth factor. A different final template with c child sites needs its
actual c-site recurrence and cannot inherit the two-site price.

## Written discriminating controls and limits

* Pop or retire child output before protecting it: child output is erased,
  and the parent's output field is still empty. A later copy cannot recover
  the arbitrary returned bits. The literal program protects first in a global
  relay outside the payload retirement loop.
* Omit the depth-left move after pop: a one-edge parent resumes site1 while
  depth still sees its child's blank terminator; the later expect(O) fails,
  or deeper siblings take the wrong remaining depth. No invalid rollback is
  claimed. The actual code restores and checks it.
* Replace H with current R in the grant map: with w=2,H=3,R_body=1 the root
  has R0=H, so a single edge hides the error. At its child R1=H^2, so the
  wrong divisor usesL*H^2 instead ofL*H; the given two-level shapes then fail
  to produce the correct grandchildren. This pass-one-edge control requires
  that specific source domain, not arbitrary R_body or H=1.
* Replace R_child=H*R by R or cap away h_child: the displayed offset map loses
  high coordinates and the full child packet has the wrong volume. Matching
  some aggregate count cannot repair a collision between arbitrary input bits.
* Leave a transfer relay dirty before child entry: the next nested CALL's
  copy-to-empty guard fails or aliases a live ancestor value. The real program
  retires all three input relays before reentry and output relay after install.

These are unexecuted hand controls. The finite fixtures, observer statements,
mutations, compressed emitted table and numerical receipts were not inspected
or rerun. The root w/depth and numerical ancestor descriptors are supplied;
source GL-cover specialization, final-template leaves/routes, Gaussian native
realization, stock, precision, complete invoice, all selected assumptions and
frontier remain outside. No new arithmetic, physical supplier, kappa or scientific
adoption is admitted by this review.

Credit thu-nmrc for this current recursive connection; Ali Romman/PR5829 for
whole-high layout; David Arias/PR2776 for the finite machine/counter/assembler;
the retained stack/output-before-pop and PR6719 codec/router/shape lineage;
and all native/precision/analytic contributors. This separate source-aware
OpenAI Codex-assisted static review is not human or proof-kernel acceptance.
Apache-2.0.

