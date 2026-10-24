# Complete-row caller at a retained parking boundary

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
This is a conditional all-size wrapper proof, with finite simulator evidence.
It is not a complete recursive multiplication supplier or kernel-checked proof.

## Interface and scope

Eight distinct physical ports use the retained four-symbol alphabet: SOURCE,
OUTPUT, GUIDE, ROLE0, ROLE1, IO, PARK, TEMP. Except PARK, each has a separator at
position -1 and enters at position 0. SOURCE contains V=2RB bits, R,B positive;
GUIDE contains B unary ones. Both are borrowed. OUTPUT, both roles, IO and TEMP
are marked empty. Each stream has blank cells beyond its payload; arbitrary
physical retained blank backing is allowed. PARK enters at arbitrary h, with a
separator at h-1, arbitrary ancestor contents below it and blank cells above.
Markers and the unary descriptor are supplied inputs. Their construction and
binary-to-unary conversion are not claimed. GUIDE has B<=V/2 cells and its every
reset is charged below.

The fixed program copies successive complete B-bit rows alternately to ROLE0
and ROLE1. It invokes the original boundary_program/boundary, W=2, active=0 then
active=1, using the original extracted push/pop tables. It then interleaves
complete rows back to OUTPUT and erases both role payloads. SOURCE and GUIDE
are unchanged. All nonparking heads finish at zero and PARK returns to h with
its ancestor unchanged. Erased backing is not reclaimed by this claim.

Each child receives the original five-port Workspace, with n=RB=V/2 bits in
IO, the role streams empty, TEMP empty and ancestor parking suspended. The
child must return an n-bit IO result at head zero, empty marked roles and TEMP,
unchanged PARK contents/head, unchanged port identities, and preserve the
outer SOURCE, OUTPUT and GUIDE frame. The inherited stronger trace-locality
and uniform-time premises remain necessary: endpoint restoration alone does
not establish either. Child costs C0(n),C1(n) must hold uniformly over ancestor
contents/height. The simulator checks port identities but does not enforce the
semantic frame by unpriced snapshots. Contract violations can leave owned
state dirty; this is a successful-call interface, not a rollback guarantee.

This closes one complete-row caller seam. It does not provide a recursive
allocation protocol for the three outer ports or a child implementation that
itself recursively invokes this eight-port wrapper with fresh tapes at every
level. Such a fixed-tape recursive scheduler is an open obligation.

## Traversal invariant

At row j, SOURCE's head is jB, GUIDE is zero, and ROLE i contains exactly the
previous rows whose parity is i, in original within-row order. A local read of
GUIDE controls each bit copy; no address, length or payload slice is consulted.
Each copy advances SOURCE, the selected role and GUIDE once. At GUIDE's blank,
rewind scans the whole B-one guide and returns to its marker. Switching the
finite row state alternates parity. SOURCE may terminate only in row0; row1
termination and partial rows reject. Thus exactly 2R complete rows produce
n=RB bits per role. Final rewinds return all three payload heads to zero.

The retained boundary theorem now applies twice with equal n. The inactive
role is pushed, the active role moved to IO, the child called, the result moved
back, and the inactive role popped. After both boundaries each role holds its
child's length-preserving result. Merge repeats the guide traversal, switching
roles only at complete-row boundaries, writing OUTPUT and erasing consumed
role cells. Its terminal check ensures ROLE1 ends simultaneously. Therefore
OUTPUT is the row interleaving of the two child results, not bitwise zipping.

## Complete local invoice

One read, write, unit move, goto or halt costs one. These are fixed finite
instructions; 73 split instructions and 78 merge instructions do not depend on
B,R,V or payloads. Structural Python identities are simulator ABI checks, not
additional tape instructions. The four top phase edges are stationary control
steps. The retained boundary's own dispatch is already included below.

Initial probes cost 18 in either router. Per complete row split costs 11B+8,
merge costs 12B+8: split copies cost 8 per bit, merge adds one erase; the guide
terminal read costs one, rewind from position B costs 3B+5, and row-entry read
and next-row goto cost one each. Final payload rewinds cost 6V+15; terminal
read and halt add two, with one extra equal-end check in merge. Consequently
split = 17V+16R+35 and merge = 18V+16R+36.

Each original W=2 boundary costs 5(2n)-n+18-2=9n+16, independently of ancestor
height; two cost 9V+32. The whole wrapper therefore costs

    44V+32R+107 <= 60V+107,

because 2R<=V. Total including children is this wrapper invoice plus C0(V/2)
plus C1(V/2). No descriptor reset, cleanup, head return or boundary dispatch is
omitted. Supplied-input preparation and semantic child implementations remain
explicit separate contracts.

## Physical storage and ancestry

Local wrapper visits on SOURCE and OUTPUT stay in [-1,V], GUIDE in [-1,B],
ROLE0/ROLE1/IO/TEMP in [-1,n], and PARK in [h-1,h+n+1]. Counting all these
intervals, including erased prefixes, gives 4V+B+14+n+3 <= 5V+17 cells.
This bounds wrapper visits/growth, not arbitrary preexisting blank backing.
If K0 is total retained entry backing, its retained physical allocation plus
wrapper growth is at most K0+5V+17. If the children add S0(n),S1(n) cells beyond
entry backing, a conservative whole-call allocation bound is
K0+5V+17+S0(n)+S1(n). Without such child-space premises no whole-call space
bound is inferred. The finite fixture uses local flip/identity children and
checks complete ancestor snapshots, heads, erased cells and visited spans;
those diagnostic snapshots are not part of runtime admission.

## Reuse and open next questions

The actual predecessor verifier used host fixture_load, incoming[i::width]
and zip(*) at the nested boundary. Those abstract shims were explicitly
excluded from its physical theorem. The present machine replaces this seam
for W=2 complete rows. It directly reuses the row-padding package's finite
Builder and the parking package's controller, rather than altering either.
The fixed-tape ordered-shear router already gives guide-driven record copying;
its seven-symbol shear interface is not the four-symbol parking caller seam.

Open next questions: supply the unary descriptor from the desired external
ABI with a paid conversion; implement a recursive outer-port scheduling
protocol on a fixed global bank; supply children satisfying both semantic and
uniform resource contracts. A first step is to specify which outer tapes may
be reused at each recursive level before claiming a complete recurrence.
