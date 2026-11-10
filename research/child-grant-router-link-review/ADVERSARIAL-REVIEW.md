# Adversarial written review of the fixed producer/router link

**No material gap found under the stated isolated component contracts.**
This is a source-aware written review of thu-nmrc PR6719 head
`3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`, limited to
`shape/producer.py:linked_split`, the retained split-router port/control
interface, the six-tag machine grammar and the one-parent-bank address law.
No source program, import, constructor, table generator, interpreter, new
verifier, scientific calculation or proof kernel was executed.

I read the coordinator argument and the four permitted inert source files,
not the separate INTERFACE-REVIEW. During this review the coordinator added
the explicit distinct-physical-tape and every-successful-halt premises, and
strengthened the default-relocation example to the complete toy below.
Those corrections were considered before this verdict; this is not a claim
that the earlier wording had all these qualifications already.

The reviewed coordinator text has SHA256
`b308014179825e32fea14ee2399da59c2c36c01529b2893350cc87815d074a54`.
The four reviewed inert source SHA256 values are:

- shape-producer.py.txt: `dbd58802087ce10e39a72202960dbb5d4aa5ce50dc1b99b7ec98e07273c292b6`
- core-router.py.txt: `ccfb60465cacd3d0f458f96a505c43f5ccda6bb8eacd6ca67f8177f5fb1796a3`
- machine.py.txt: `04b7b76b9f06653d94d2158196cdd1bed7883dd1f59fcbc81a486e3ffb248681`
- shape-PROOF.md: `1f6dd1a7fad635e9109da48c9d96ff089dcc3c04eb3589372dd9135258390d2f`

## Tape map and physical-state contract

For every fixed integer L>=2, the router domain is exactly0 through L+6.
Its bank keys0 through L-1 are disjoint from the seven later reserved keys.
The image of the source dictionary is exactly
`{3,4,5,6,8} union {9,...,L+10}`. The first set has five distinct members,
the interval has L+2 members, and they are disjoint. Thus the map is total,
injective and in range of the L+11-tape linked program. The unused router
output L+1 is also mapped, even though split mode does not access it.
No producer input0,1,2 or retired guide7 is in the image.

At L=2 the banks become9,10, source11 and unused output12; repeat/block
inputs become3,4 and scratch becomes5,6,8. This boundary has no accidental
reuse of the router's old numerical source role2 as producer input2.
The same disjoint-set argument proves every larger fixed L, without a
finite grid or dependence on runtime descriptor values.

An injective numerical map alone would not rule out supplying the same host
Tape object under two indices. The added premise that all L+11 roles are
genuinely distinct physical tapes is therefore necessary for the intended
renamed-state simulation. The source Machine constructor does not itself
certify such absence of host-object aliasing. The review correctly treats
aliased fixtures as outside the hardware contract rather than claiming they
are automatically rejected by the table.

## Every control-transfer case

Let s,t be the two valid nonempty instruction counts. Producer rows retain
their indices, and its entry remains unchanged. The only changed producer
tag is halt, replaced by one goto to s plus the router entry. Its branches,
including defaults, and gotos remain inside0..s-1. A valid original write or
move cannot be the final row, so its implicit successor stays within that
piece; appending the router creates no accidental producer fallthrough.
Producer reject remains the same exception with the same reason string.

Router row j is placed at s+j. A branch's tape is renamed and both every
named-case target and its default are translated by s. A goto's target is
translated by s. For write and move only the tape index changes: the next
PC is s+j+1, equal to the translated original successor and in range by
the original Program validity condition. Halt and reject carry no tape or
jump operand, so copying them is correct. The grammar admits no seventh
instruction type that could conceal another relocation requirement.

Consequently the relation between a router state and its linked copy is:
PC differs by s, and each tape's entire contents and head equal those at
its renamed physical role. A branch sees the same symbol, including when
the default is selected. Writes, unit moves and gotos preserve the relation.
Halting and rejection have the same outcomes. The proof covers arbitrary
run prefixes, including nontermination, under the component-state contract.

The producer can have several syntactic halt rows. Every successful halt
reachable from an admitted input must satisfy the exit ABI; correctness at
only one nominated halt is insufficient because the comprehension replaces
all of them. On any one successful execution the first reached halt becomes
the dispatch. Once in the router, all explicit and implicit successors stay
in its relocated region, so the program cannot return to another producer
halt. The successful dispatch occurs exactly once. Invalid-input behavior
and rejected-input cleanup are not inferred from this valid-input argument.

## ABI and preservation at the jump

Only roles0 through8 can be touched during the producer phase. The preloaded
source L+9 and initially blank child banks9 through L+8 are therefore intact
at dispatch. The producer's positive marked outputs3,4, with heads1, are
exactly the mapped binary repeat/block inputs. The router receives these
physical descriptor tapes, not a decoded host value.

The reused router scratch is5,6,8. The producer contract must guarantee
genuine erasure of its cells and installed markers, with heads0; logical
zero values or merely returning head positions would not suffice. The
router then installs its own LEFT markers. Guide7 remains erased and is
never a router operand. The child's unused split-output L+10 is not another
delivered bank; it is unreferenced and retains whatever entry state the
caller gave it, with no output or erasure credit inferred.

Conditional router correctness preserves source L+9 and generated grants3,4,
returns their heads1, delivers child banks at heads1 and returns work5,6,8
blank at heads0. Original parent headers0,1,2 and retired guide7 are outside
the mapped router roles, hence retain their producer-exit states. These
conclusions depend on the isolated arithmetic/conversion/router contracts;
the linker does not independently establish them.

## One bank, exact addresses and ownership

Divisibility and positivity give A=L*H*A_c and R_c=H*R. Thus the required
child-source length is A_c*L*R_c=A*R. This is one supplied parent bank,
not the full parent stream of length V=L*A*R. Each of the L new banks has
A_c*R_c=A*R/L bits, and their combined length is A*R. The marked source
must have precisely this length and initial head1; the equality of integers
does not itself create or stage that packet.

For any parent-bank address (a_p,r_p), divide a_p by H to get a unique
quotient m and remainder h_c; divide m by L to get unique a_c,l_c. Then
a_p=(a_c*L+l_c)*H+h_c and r_c=h_c*R+r_p lies in0 through R_c-1.
The exact identity

    a_p*R+r_p = (a_c*L+l_c)*R_c+r_c

matches the router's source indexing. Conversely, division of r_c by R
recovers h_c,r_p and reconstructs a_p. The map is therefore bijective with
all displayed bounds, including H=1 and R=1. The subsequent split places
l_c in the child bank index and leaves h_c in the ordered high part of r_c;
it does not merely prove equal volumes or transpose that high field into
another bank. The original source remains preserved; new copied banks and
descriptors are owned data and receive no free productive credit.

## Counts and written controls

The machine increments its step count before dispatching every tag, including
halt. Replacing the producer halt by one goto therefore preserves that final
producer step count; there is no extra call/return instruction. Under the
same isolated initial/boundary states and an uncapped successful execution,
the linked count is exactly T_producer+T_router, when both isolated counts
include their halt. Counted branches/reads, writes and unit moves similarly
add. Visited-address sets form a union on the renamed physical tapes, with
overlap on reused scratch. This does not certify additive peak nonblank
storage, inaccessible backing, simulator initialization or any numerical
1000V/100V/codec/stack bound.

The strengthened default control is a complete valid control-flow example:
producer [goto2,halt,halt], entry0; router
[branch(tape0,{BLANK:0},default1),reject(default)], entry0; scanned ONE.
Correctly relocated default reaches linked4 and rejects. Leaving only that
default untranslated reaches producer1, which has become goto3, and cycles
3 to1 to3. No instruction changes the scanned symbol. This is a written
observable failure, not only a wrong-region observation, and was not run.

The other scope controls are correctly bounded. Implicit write/move successors
need the original validity constraint; a future target-carrying opcode needs
a new relocation case. Aliasing two guides at role5 invalidates the state
correspondence and two-live-guide ABI. For L=2,H=2,A_c=1,R=1, the correct
child low indices for source offsets0,1,2,3 are0,0,1,1, whereas the stale
a_p mod2 rule gives0,1,0,1; offset1 is concretely misrouted. Supplying all
V bits instead of A*R violates the exact-end source premise. These are
hand-derived controls, not executed mutants or a finite census.

## Verdict, credit and remaining work

No further correction is requested for this linking implication under the
explicit physical-entry and every-valid-successful-halt contracts. This
does not certify isolated producer arithmetic/validation/erasure, counter or
router correctness and bounds, literal emitted-table execution, source-bank
staging, retire_delivered, codec/GrantBridge/stack protection and return,
H-from-width, generated ancestor weights/descriptors, arbitrary-depth
production, routes/fallbacks, Gaussian children, physical or paid resources,
precision/stock/tape/compiler/outer application, or any of the five selected
framework assumptions. There is no new tariff/kappa, frontier change,
independent human acceptance or proof-kernel certificate.

The producer/link and new child-grant implementation remain thu-nmrc PR6719's
work with substantial OpenAI Codex assistance. Ali Romman PR5829 retains
geometry/whole-high/allocator credit; David Arias PR2776 retains machine,
assembler and counter credit; Mason Hale, codec/stack/return authors,
Jose Manuel and the binary-divisor lineage retain their named contributions.
Renaming/simulation and Euclidean division are classical. This separate
adversarial AI written review adds scrutiny only. Apache-2.0.
