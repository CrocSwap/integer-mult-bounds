# Persistent numerical ownership at the actual CRT row entry

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.

## Statement and actual missing boundary

PR5219 constructs a fresh60-role numerical owner; Ali Romman's PR5353
constructs three more descriptor roles from an actual padded-axis stream.
Closing one call erases all63 roles, but its constructor allocates new
physical objects on the next call. Its theorem permits repeated invocations
only while the same precision guide remains fixed. This package implements
the missing *retire and reopen at a different guide* boundary on one fixed
bank of63 physical backing objects. It does not change the numerical
producer, RowEntry transport or arithmetic routines.

Take any finite sequence of successful admitted PR5353 node/row calls.
Each has power-of-two node size n>=2, node width sum P-1, P>=4, admitted
pairwise-coprime moduli, padded current coordinates, canonical source tape
and eight legal protected numerical words. Let m=t=n/2 and H_L,H_R be the
left/right sums of declared widths, so H_L+H_R=P-1. External sources, dirty
words and their heads may vary between calls; their production is supplied,
not free computation by this owner. Each borrowed backing is disjoint from
the bank. The compiled topology and the source's finite-operation model
remain premises.

The bank begins with63 distinct, wholly blank finite arrays, heads1, each
of capacity at least1. Arbitrary *blank* prior capacity is permitted and
charged. Its first acquisition may construct those physical objects before
the call sequence. No physical Port, Word backing or Arena constructor is
needed during any call. Python wrapper/control objects with fixed63-role
inventory do not represent extra physical tape storage.

On every successful call, the returned result is exactly the unchanged
RowEntry result. It remains live under a unique lease until close. Close
consumes that result, executes unchanged numerical retirement, and restores
the whole bank to blank with heads1. All borrowed bytes and heads are
preserved. The next call can use any admitted P, including a smaller one,
without changing backing identities or shrinking allocated tails.
Concurrent/reentrant calls and double retirement reject. Failure rollback,
arbitrary dirty owned scratch and changed input preparation are not claimed.

## Fixed role correspondence and paid marker reentry

Source allocation order is fixed, independent of numerical values:

| Role indices | Source purpose | Count |
|---|---|---:|
|0|RowEntry unary guide|1|
|1,2|canonical left/right descriptor streams|2|
|3..58|Entry private numerical words, source slots8..63|56|
|59|Entry numerical zero template|1|
|60,61|Entry padded left/right records|2|
|62|Entry returned offset/value stream|1|

`Bank.take` replaces only the Port factory. A derived Entry overrides
`new_port` to use that factory; inherited word initialization, padding,
invocation, consumption and close execute unchanged. The actual RowEntry
uses the same factory for its first three descriptors. Exactly63 requests
are made on an active row; an all-idle row requests none and does no tape
work. The numerical Arena still has its fixed64 slot wrappers, with eight
borrowed slots and56 private slots; allocator order is the predecessor's.

A retired role is at head1 with no LEFT marker. Acquisition reads blank
at1, moves left, checks blank at0, writes LEFT, and moves right. These are
five charged tape operations; no host head assignment or array replacement
reinstates entry. The original initialization then writes through the actual
encoded guide or input stream. After unchanged close, release checks blank
at1 and0 by four local operations and returns to1. It does not claim that
these two observations validate arbitrary dirty tails: whole-tail blankness
is an inductive successful-owner premise, checked separately by the verifier.

## Why a longer retained word backing remains sound

This point is stronger than applying a generic maximum-capacity lemma.
The original eager Entry presents a word with array length P+2; a reused
word may have a longer array. Every runtime arithmetic scan in the pinned
words module is delimited by LEFT/RIGHT, not by array length. Array length
appears only in the local step-bound safety check. Constructors and the
checker-only `inspect` method are excluded; the producer uses `.bits` only
for the encoded >=4 guard. The source declarations bind these exact bytes.

At entry to a new precision, guide-driven `word_storage` writes blank cells
through the new delimiter position in each private role, and writes P zeros
then RIGHT into the template. Arena.zero copies that template and writes
RIGHT at the same position. Thus each live numerical word has the new
P-bit delimiter regardless of its old capacity. Source arithmetic never
crosses that delimiter except its proved bounded local movements, so the
extra blank suffix is unreachable numerical data. The looser backing-length
safety check does not change an admitted execution. Source-relative
simulation gives identical values, heads, slot choices and writes through
the active extent. No host P decode or shortened-array view is introduced.

At retirement all live numerical data and RIGHT markers are erased by the
unchanged consumer/free/template routines. Descriptor and output streams
are erased through their existing delimiters, then their LEFT markers are
removed. Everything beyond the current written extent was blank at entry
and untouched, or was blanked during earlier longer successful calls.
Induction on calls proves the *entire historical backing* remains blank.
In particular, shrinkage needs neither a free tail reset nor a scan through
old high-water capacity; that tail is already blank. The same reasoning
applies to canonical and padded streams, whose meaningful lengths vary.

## Source-derived capacities, not maximum aggregate accounting

Let C_r be the initial blank capacity of role r. For one active call j,
the following source bounds q_r(j) cover every allocated cell, including
transient writes and later-erased cells:

| Roles | q_r for each role |
|---|---|
|0|P+1|
|1|2H_L+4m+2|
|2|2H_R+4t+2|
|3..59|P+2|
|60|m(2P+4)+2|
|61,62|t(2P+4)+2|

For role0, the source emits exactly P guide ones after LEFT; moving to the
blank terminator does not allocate it. A descriptor record has ROOT, two
at-most-h-bit fields, two WORD_END markers and RECORD_END, plus final RIGHT
and initial LEFT. Canonical trimming can erase high zeros but cannot exceed
the untrimmed2h+4 record envelope, including the last field's transient
zero writes. This proves the two descriptor bounds even when their maxima
occur under different distributions of H_L and H_R.

For roles3..59 the guide loop writes through position P+1, exactly P+2
cells including LEFT; the inherited arithmetic stays in that extent. Padded
records and output records each have two P-bit fields and four record
markers, with initial LEFT and final RIGHT. Their counts are m,t,t. Erases
write only already represented cells. Port.read and Port.step do not
allocate; Port.write at the next cell appends exactly one cell. Thus these
bounds concern retained allocated backing, not merely visited heads or
nonblank content.

After any k calls, each role has capacity at most

    max(C_r, max_{active j<=k} q_r(j)).

This follows directly from the local write rule and the per-call extent
simulation above. The bank total is the sum of these63 rolewise maxima,
not the maximum of one-call totals. The principle of historical rolewise
accounting is inherited, notably from PR5286's distinct15-role interchange
owner; its application is not claimed as a new general lemma.

For an explicit call-count-independent grant, let P_* and n_* bound all
active precisions and node sizes. Put

    Q0=P_*+1,
    Q1=Q2=2(P_*-1)+2n_*+2,
    Q3=...=Q59=P_*+2,
    Q60=Q61=Q62=(n_*/2)(2P_*+4)+2.

Then the complete retained bank is at most sum_r max(C_r,Qr).
The descriptor bound uses H_L,H_R<=P_*-1 and m=t<=n_*/2;
all capacities are monotone. For a fresh bank C_r=1, this becomes

    57(P_*+2)+(P_*+1)+4(P_*-1)+4n_*+4
       +(3n_*/2)(2P_*+4)+6.

Borrowed source, dirty-word and any outside backing remain separately
charged. Increasing P_* may increase capacity; completed erasure never
returns productive storage credit. This is logical tape capacity, not
Python heap bytes, and no global supplier stock theorem follows.

## Complete local time

Use the unchanged RowEntry one-call source-operation invoice, where
L=2+sum_all_axes(3h_i+4):

    T_j = 2^20(P+2)^4 + 2^16(P+2)^2 + 128(L+P+n+1).

Fresh Port marker setup is already included in T_j. Reentry replaces it
with at most5 local operations, and release adds4 per acquired role.
All bank inventory, role checks and ownership tests concern a fixed number
of roles (63 plus at most9 borrowed roles), not input-size arrays. The
new adapter adds fewer than4096 tape/finite-control operations per active
call, conservatively including these checks, wrapper dispatch and leases.
Initial physical owner construction costs at most4096 additional such
operations for63 fresh one-cell roles; a supplied blank owner is an explicit
entry premise. Total sequence cost is at most4096+sum_all_calls(T_j+4096).
This deliberately retains the full bound even for all-idle calls, covering
the source's topology validation without treating its width-list traversal
as constant. All-idle calls have zero tape traffic. No scan proportional to retained old
capacity is hidden. Numerical traffic and port traffic are separately
metered, including successful retirement; their sum is not itself claimed
to count Python control instructions.

## Corroboration, limits and next questions

Actual producer calls P6→P15→P6 use (7,3), then (5,7,11,13), then (7,3).
The large current state(1,5,0,9) reconstructs lower11 and offsets(0,3).
The same63 backing identities retain536→1238→1238 cells; all historical
tails are blank after each close. Additional padded, invalid-left and idle
calls preserve the appropriate source semantics. Physical constructors are
sealed throughout each active initialization/invocation/retirement.

Two P6 geometries (7,3) and (3,7) each use536 fresh cells but retain537 in
one owner because canonical left/right maxima occur on different calls.
This concretely refutes maximum-of-standalone-total accounting. Controls
also exercise constructor bypass, missing marker reinstatement, premature
reentry, double close, omitted preexisting blank capacity and a corrupted
old suffix hidden beyond a smaller current word. They are finite evidence
for the written all-sequence source proof, not a substitute for it.

Open next questions: (1) integrate this owner with the actual physical ROM
query and whole-level state stream, pricing all borrowed/returned objects;
(2) derive a complete binary numerical lowering without host-sized runtime
values; (3) supply canonical input production and failure-path ownership if
required by a larger caller. No h4 ROM replay, complete exceptional key,
native/outer theorem, new kappa or selected-frontier claim is made.

Credit Ali Romman's PR5353 actual RowEntry; JoyboyBrian's PR5219 numerical
Entry and PR5053 arithmetic; Hiroki KUMAZAKI's current-coordinate caller and
PR5286 history analysis; Ross Richardson's earlier retained-arena work;
Cinna Davis, ToikY, Jose Manuel, Douglas Colkitt/John-Michael Smith and all
authenticated predecessor notices. No frozen source is modified. No
independent human or formal-kernel acceptance is claimed.
