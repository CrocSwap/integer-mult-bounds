# Fixed-bank recursive complete-row caller

JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0. This is a
written all-depth conditional machine refinement, with finite source-bound
checks, not a kernel proof or multiplication supplier.

## Domain and exact imported programs

Fix B>=1 and d>=0; N=2^d rows contain V=NB arbitrary bits. Nine pairwise
distinct physical tapes are SOURCE, OUTPUT, GUIDE, ROLE0, ROLE1, IO, PARK,
TEMP and CONT. Every nonparking tape has a separator immediately left of
its entry head, with no other separator in its payload. SOURCE contains V
bits; GUIDE contains B unary ones; others are marked empty. PARK has arbitrary
ancestor contents below its entry separator and blanks above. Origins may be
translated independently. Arbitrary retained blank backing is allowed and
counted by K0. Input markers and unary guide are supplied, not free outputs
of a claimed descriptor conversion.

The exact PR5134 compile_router supplies its 73/78 instruction split/merge
programs. Both exact W=2 boundary_program phase tuples and the unchanged
extracted push/pop and move primitives are reused. The callback phase is now
a jump in finite control, not a host recursive call. The fixed nine tapes and
program tables are allocated before invocation; no tape is allocated at descent.
`nodes`, `leaves`, `steps` and simulator visits are observers, never operands.
The Python loop simulates finite q/active/pc and local-symbol transitions.

A leaf is recognized by scanning one supplied GUIDE length on SOURCE and
rewinding both. A blank next source symbol means exactly one complete row.
Otherwise the existing splitter demands complete even rows. The claimed
successful domain is dyadic; this is not a full validation/rollback contract
for arbitrary malformed or nondyadic inputs.

## Ownership induction and continuation grammar

At every enter state, SOURCE is borrowed relative to that invocation; OUTPUT,
roles, IO and TEMP are empty, GUIDE is shared and unchanged. Each local splitter
makes the two alternating complete-row streams of length v/2. The original
boundary first pushes the inactive role and moves the active role into IO.
At that exact child phase all roles and TEMP are empty.

The adapter pushes parent SOURCE above the inactive-role parking frame and
writes the active bit (0 or 1) on CONT, advancing its head. It moves IO into
SOURCE and jumps to enter. Thus the descendant reuses the identical physical
ports. Its SOURCE is an owned transferred copy from its parent's perspective.
There is no saved Python list, callback frame, ancestor pointer or per-depth
program object. CONT contains the root-to-current active bits, and its head
always stands at the next blank cell. Only that finite alphabet represents
pending return control. PARK carries the corresponding sibling then source
frames with the original literal delimiters.

On completed descendant OUTPUT, one step left on CONT reveals the active bit.
The controller erases that bit, erases the owned child SOURCE, moves OUTPUT to
IO, and pops parent SOURCE. The original boundary resumes at move_out and
then pops its inactive role. At active0 completion it executes active1; after
active1 it invokes the unchanged merger. If CONT instead reveals its original
separator, the root is complete and its head advances back to entry. Hence
root SOURCE is never erased, every saved parent input and sibling is restored,
all output-role copies are consumed, and CONT and PARK return exactly to entry.
No descendant visits a parking cell below its own entry separator; restoration
uses only the frames it owns. The stronger inherited trace-locality premise,
not merely endpoint restoration, is respected by these actual primitives.

The default leaf program copies and complements each source bit into OUTPUT,
then returns both heads. It does not touch GUIDE/PARK/CONT or other work. For
an arbitrary replacement fixed leaf table the same induction holds only under
its explicit source-preserving, length-B, restored-head, other-port-frame and
uniform resource contract. No arbitrary Python child is admitted. With the
default leaf, the completed endpoint is bitwise complement of SOURCE. The
structural theorem is more general: each original B-bit row receives the
supplied leaf function, and the unchanged interleaving restores original row
positions. No multiplier leaf or selected GL64 supplier is supplied here.

## Full time invoice

Use the retained global-transition model. One primitive table step may read
several fixed tapes and perform their unit writes/moves. A router instruction
costs one step. New auxiliary reads/actions and each outer-loop dispatch each
cost one; a simultaneous write/unit move is one permitted action. Compilation,
Python instrumentation and checking are outside execution, not hidden decisions.

For an invocation of length v, leaf classification costs 8B+10: paired scanning
and both marker rewinds are included. Erasing n owned bits costs 4n+5. The
default leaf router costs 12B+12. These identities follow by counting the
literal loops, not the finite fixtures.

At an internal node v=2RB, the two routers cost 35v+32R+71. Both boundary
primitive costs total 9v+22 (their dispatches are counted by the new outer
control, not counted twice). For each child, the added source push/pop costs
5v+7, IO/source and OUTPUT/IO moves total4n+4, erasure costs4n+5, and CONT
push/pop costs5: total5v+8n+21=9v+21, n=v/2. The two adapters cost18v+42.
At most16 outer dispatches belong to an internal node, and classification is
at most4v+10. Consequently the internal local toll is at most
66v+32R+161 <= 82v+161 <= 100v+200. This includes all descriptor rewinds,
source preservation, sibling parking, continuation bits and cleanup.
A leaf costs at most24B+40 including dispatch; the final root continuation
separator inspection costs at most3 separately. Counts are conservative where
primitive and router models permit simultaneous actions.

Thus, for the default leaf, summing the binary recursion tree proves

    T(V,B,d) <= 100 V d + 200(N-1) + N(24B+40) + 3
              <= 100 V d + 264 V + 3.

For a replacement leaf, replace its default router charge by its admitted
uniform L(B); no unproved child time is set to zero. This is a uniform theorem
over ancestor contents/heights and payloads. Guide construction and external
input/output encoding are separate supplied-input obligations.

## Retained physical allocation

Each nonparking tape visits at most its entry separator through a prefix of
length V, except CONT which needs d bits; d<=V. Counting all eight nonparking
intervals conservatively gives8(V+2). Along a live root-to-leaf path, each
level parks v/2 sibling bits and v parent-source bits, plus two delimiters.
Their geometric sum is less than3V+2d. One extra boundary cell on either side
bounds all stack visits by3V+2d+2 beyond entry backing. Therefore retained
physical allocation is bounded by

    K0 + 11V + 2d + 18 <= K0 + 16V + 32.

Erased prefixes are included, never reclaimed by fiat. Arbitrary preexisting
blank backing remains K0. The default leaf uses only the counted source/output
prefixes. An alternate leaf must obey that same interval contract or add its
explicit retained-growth bound; endpoint restoration alone is insufficient.

## Reuse, verification and remaining obligations

PR5134 proves one node but explicitly excludes fresh outer tapes at every
recursive level. This construction closes precisely that exclusion with paid
source preservation and a physical continuation stack. It does not replace
internal output-ownership exchange, grant binary-to-unary descriptors, or
execute arbitrary supplier children. The retained original parking and row
Builder authors retain credit, including commdata2338 and the Lean table
lineage. No Lean build or formal-kernel claim is made.

Open next questions: connect an actual supplier leaf and prove its frame/time
contract; provide paid external descriptor conversion; generalize to a supplied
nondyadic tree only after pricing its shape and return grammar. No new kappa.
