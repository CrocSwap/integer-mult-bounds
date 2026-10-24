# Selected copied-query private stream: physical record and lifetime refinement

This written finite-program proof is conditional on the complete child/chart/
translation ABI in PR5039. It does not establish that child, global allocation,
selected numerical precision, a multiplication theorem or a new kappa.

## Actual record and source contract

The authenticated `physical-gaussian-tensor/tensor_sources.opened` cohort supplies
`records.Tape`, `ring_words.read_signed/write_signed`, and the original all-width
codec. A field is a LEFT marker, M successive complex records, then BLANK. Each
record consists of p least-significant-first two's-complement real bits followed
by p imaginary bits. There are no record separators. The interpreter operates
on those actual Tape objects, with their actual alphabet 0,1,LEFT=2,RIGHT=3,
BLANK=4. It does not decode field data or runtime descriptors into host integers.

M,p are positive canonical LSB-first binary descriptors ending in RIGHT. Entry
heads are one cell right of each unique LEFT marker. All fields have exactly
N=2Mp bit positions. X and Y are borrowed; Z is a pre-reserved owned private
field, whose old N positions may contain bits or blanks and whose later backing
is blank. Its old contents may be destroyed. Three private work bodies W,M,T
are blank, with caller-owned LEFT markers. All eight physical ports are distinct.
The initial and final marker convention matches the actual initialized physical
record bank; this routine does not allocate its tape objects or their markers.
Provisioning these fixed ports belongs to the caller, not an uncharged runtime
allocation inside the query. Descendant private streams must occupy other ports.

Input components and completed child outputs lie in the signed p-bit interval
[-2^(p-1),2^(p-1)-1]. Every componentwise Y+Z sum must also lie in that interval.
One sufficient condition for p>=2 is |Y|,|Z|<2^(p-2). Thus one guard bit beyond a
shared magnitude bound suffices. There is no rounding or wraparound on accepted
input. This range is a stated local premise; selected global precision remains
unproved. Invalid input/overflow rejection need not restore partially modified Y.

The actual selected CONTROLLER event5 is QUERY_SHEAR at stage2,pair0,forward;
its source/destination roles are0/1. PR5039's seven nonrecursive records surround
one whole rank-f child. We instantiate OWNED_CLEAR, COPY, ADD and OWNED_ERASE.
Right monomial, positive whole child, left monomial and T_f remain one explicitly
retained completed interval on Z. Its endpoint is Q_f^-1 X, preserving every
other port and all descriptors/work bodies, with all heads returned. No runtime
check of its mathematical semantics is claimed. The local finite test uses f=2
and one spectator axis, so M=8; the proof covers any complete M-record field.
This small chart fixture is not a materialization of the selected full address
space. Port0's actual q is source-bound; its chart is a named imported contract.

## Fixed control and preparation

The finite assembler and binary-to-unary macros are retained from David Arias's
PR2776. Their seven symbols are renamed bijectively to the actual record alphabet;
UNIT=5 and MARK=6 occur only on private work. No runtime parameter affects assembly.
Each program instruction branches on one scanned symbol, writes one symbol,
moves one head by one cell, jumps to a fixed state, halts or rejects.
`Invocation` only dispatches those instructions. Its object/state checks enforce
fixed simulator ports and legal phase order; physical port separation is the ABI.

Preparation converts p and M to UNIT^p RIGHT and UNIT^M RIGHT, preserving the
descriptors and clearing temporary T. Canonical shrinking binary decrement has
sum_{k=1}^n v2(k)=n-popcount(n), so the retained exact conversion cost is at most
44n microinstructions, with at most n unary cells and ell(n) temporary bits.
The predecessor proof supplies this macro bound; no constant-time host counter
is substituted.

For each of M marks, two complete p-mark scans overwrite Z's old component with
zero. Then a second complete M-by-two-by-p traversal copies each scanned X bit
into Z. Every record, both components and all spectator records are included.
W rewinds after every component, M after each full pass, and X/Z after COPY.
The exact terminal BLANK checks reject short/nonbinary X or an overlong field.
The unary counters remain owned and stationary throughout the completed child.
No value-dependent data survives in finite control across the child interval.

## Addition and erasure

On resumption all eight heads are checked against their local LEFT marker.
For each component the carry starts at zero. At bit i the two scanned bits a,b
and carry c form t=a+b+c. The finite state writes t mod2 into the ORIGINAL Y
cell and continues with floor(t/2). The W delimiter identifies the sign bit.
At that bit, equal input signs and a different output sign reject; this is the
standard necessary-and-sufficient two's-complement signed-overflow condition.
Otherwise the p written bits represent the exact integer sum. Carry is reset
before the imaginary component and before the next record. No host integer
arithmetic on unbounded data appears in the program: a,b,c each have two states.

Z is only read during ADD. After exact end checks, Y/Z/M return to their first
cells. A local scan blanks every one of Z's N cells, then returns its head. The
unary work tapes are similarly erased including RIGHT delimiters; T was already
blank. Their LEFT markers remain caller-owned. X, both descriptors and all
outside fields are untouched, Y has exactly the componentwise sum, and all
private visited cells other than the specified initial markers are blank.

Combining this with the retained child endpoint gives the actual local query
(X,Y,H)->(X,Y+Q_f^-1 X,H), while Z returns to its reusable empty representation.
This is the complete local lifecycle, not an isolated copying kernel. The
18480 logical-record count remains the predecessor's count, not a tape-step bill.

## Explicit physical cost and backing

Count M complete complex records and N=2Mp bits. A guarded entry costs24 local
instructions plus three initial blank-work checks in preparation. A retained
rewind from relative head h costs3h. The clear component loop costs9p+4, and
the copy component loop costs11p+4. The outer record loop adds3M+1 per pass.
End guards and complete rewinds add at most9N+6M+32 across preparation.
Together with44(p+M) conversion, preparation is at most128N+128.

The valid addition component costs11p+4, including its initial carry jump and
W rewind. Both components and outer loop total11N+11M+1. End checks/rewinds
cost at most6N+3M+16. Erasing Z costs7N+4 and erasing W/M costs7(p+M)+10.
Including the24-instruction resumption guard gives at most64N+64. Since
p+M<=2Mp=N for positive p,M, these loose bounds hold uniformly, including p=M=1.
The whole local ABI costs at most192N+192, hence the advertised conservative
256N+256 transitions. The completed child and its two chart normalizers and
translation have separate retained costs C_child; total is256N+256+C_child.
No child's internal cost is set to zero.

Only three data streams range over N bits. W and M range over p and M marks;
T ranges over max(ell(p),ell(M)); descriptor lengths are ell(p),ell(M). Count
all visited cells, including blanks later erased, and every marker/end cell.
The total is bounded by

3N+p+M+ell(p)+ell(M)+max(ell(p),ell(M))+16 <= 8N+32.

This includes the visited spans of borrowed fields and metadata, not arbitrary
pre-existing blank capacity. If K0 is the sum of entry backing lengths, retained
backing throughout is at most K0+8N+32. Erasure does not reclaim that backing.
A capacity bound independent of K0 requires a separate bounded-entry-capacity
premise, which is not assumed here. Owned private bodies alone use at most3N+8
visited cells. The finite field has no extra productive-input
credit. The source child's separate backing is not included in this local bound.

## Two suspended parents

`SuspendedPair` requires16 distinct ports, making two complete eight-port slots.
Prepare parent A, prepare B, complete/resume B, then complete/resume A. Between
A's preparation and resumption, B's program never addresses any A tape. A's Z,
its counters and borrowed fields therefore retain their exact bytes/heads.
The named child also preserves the other slot. Each local proof applies in
reverse return order, with no shared mutable cursor or private output. Total
local transitions are at most256(N_A+N_B)+512 and visited cells at most
8(N_A+N_B)+64, plus the separate children. Retained backing is bounded by the
two-slot entry capacity K0 plus this visited-span allowance. Holding storage is paid for both
unfinished fields, even while no local instruction runs. This is a two-slot
local composition theorem, not a global unbounded-depth allocation proof.

## Open next questions

- Bind the selected child's actual finite numerical execution and normalizers
  to this record/range contract; the fixture's semantic child is not admission.
- Incorporate per-suspended-parent private slots and initialization into the
  finite compiler's global reserve recurrence, rather than reusing one slot.
- Prove the selected global precision/range invariant needed for the checked
  exact addition. A local no-overflow condition does not establish it.
