# Literal current-source CRT leaf headers

## 1. Exact result and dependencies

This package lowers the precise `emit_headers` source controller from
CrocSwap/integer-mult-bounds#7388, head
`d6f4a69202ad0bba4a915f4d4f3eaba1fe431c86`, into an input-independent finite
instruction graph. It constructs the same H, S, A, zero-row and unary-width
streams from the actual borrowed encoded source, axis cursor, precision
guide and current numerical result. A separate entry retires all five
owned outputs. Forward and inverse entries continue physically into one
unchanged copy of the complete B7 destination-key pass.

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`. B7 is published
at CubeJerry `f789e7318ef89b26c2e358c4c1eb09ce93d21f73`, package
`research/literal-all-wire-crt-keys`, graph digest
`8f5ae62b89de8308eb021920185269d884f07f625a5b3ee10b39f27aee5a393b`.
The 56 retained dependency objects and original notices are byte/blob
pinned in SOURCE-PINS.json. Its source/offset lineage includes #7352;
the canonical switch predicate is Nick Petalas's #7504 construction.

New work is this literal header controller, its exact source binding,
complete prefix/precision/copy/retirement bill, historical-width accounting,
and static join into B7. The source grammar, numerical algorithm, lease,
switch formulas, complete key pass and radix are credited prior work.
Numerical offset production, owner acquisition, current-lease dispatch,
source commit and radix orchestration remain external. No new kappa or
discharge of any complete foundational assumption is claimed.

## 2. Typed physical domain

All roles are distinct and supplied with adequate access and backing.
Roles 0--21 are exactly B7's physical owners. Roles 14,15,16,17,19 are
initially blank owned windows for H,S,A,J and WIDTH; role0 is a granted
blank mode cell which is cleared before any B7 entry. The remaining B7
private/index/address/payload contracts apply whenever a key entry is used.
In particular its payload is the original fixed thirteen-bit-codeword
frame with arbitrary twelve-bit opaque payloads, not an arbitrary-width
payload service.

Roles 22--25 are the actual borrowed source, axis, guide and result.
Role26 is the actual iterator's owned temporary width role, with a LEFT
guard and blank body. All five native roles enter at their first body
cell and return there. Marker outputs and B7 private owners enter at their
supplied marker/window origins. Origins may be translated; exterior data
is untouched. Valid bodies contain no extra LEFT guard. These are typed
bounded streams; this is not a universal parser for absent/interior guards.

For the uniform local theorem let the axis body start `ONE^m STEP`, m>=1,
and let the borrowed source consist of m+2 records followed by RIGHT.
Every width w is positive, and one record has the exact grammar

`ROOT ONE^w WORD_END bits_w WORD_END bits_w RECORD_END`.

Write w_1,...,w_(m+1) for the skipped prefix and left widths, u=w_(m+1),
U=sum(w_i), W=max(w_i); the final right width is h>=1. The guide is ONE^p
followed by blank, with p=u+h+1>=4. The result prefix is ROOT followed by
exactly p bits, WORD_END, and arbitrary untouched remaining fields.
Its first integer is a; the right modulus field's integer is s. The
current numerical/source admission gives 1<=s<2^h and 0<=a<s. The header
construction itself does not compute or certify the numerical relation.

The actual #7388 selected nonroot leaf is a specialization: the total axis
count is dyadic, its half count is one, the node is last, and the preserved
axis suffix is STEP ONE RIGHT. `NodeEntry` manufactures precisely
p=u+h+1, and `_record` has left its actual width scratch blank. The local
proof permits other m with the same stated header grammar; it does not
enlarge the numerical provider's domain. In particular a local unit-modulus
header fixture is not an actual admitted unit-modulus CRT caller.

The fixed alphabet is the original numeric 0--13 plus the marker `|`.
`NativePort` merely renames numeric symbols into fourteen distinct graph
tokens; each operation calls one actual read, write or unit move. It does
not decode, resize or copy a field. Numeric LEFT/RIGHT/BLANK become L/R/blank.
The original binary payload uses B7's unchanged fixed bit renaming.

## 3. Record and header construction proof

The graph first checks all five output origins, each native LEFT guard,
the positive nonroot axis prefix, a nonempty guide and blank width scratch.
It constructs H and J by two guide-driven zero scans. The guide and each
new marker head return by explicit local movements. Each output is now
`L 0^p R`.

For every initial ONE in the axis prefix, it validates one complete source
record and then advances the axis one cell. Record validation manufactures
ONE^w RIGHT in the actual blank width scratch while scanning the positive
source width. Two scans of that scratch read exactly w bits and then the
required source delimiter. Thus neither a delimiter-only skip nor a host
width lookup is used. The complete scratch, including its temporary RIGHT,
is erased and its first-body head returns before the next record.
At STEP the same finite record routine validates exactly the left record.
Two fixed routine copies supply the different fixed continuations; there
is no runtime call stack or variable host return.

The next source record is the final right record. The graph emits one
WIDTH mark for every source unary width mark. After k marks, H has value k
in exactly p bits. Its explicit binary carry routine scans all p digits
and returns to L. Because h<2^p, none of these h increments overflows.
This proves the H/WIDTH consistency required by B7 from the same physical
source width rather than importing a decoded header.

The WIDTH scan copies exactly h source modulus bits into S while advancing
the actual guide. It verifies the following WORD_END and pads S with zero
until the guide's blank. Since p=u+h+1>h, this is the same p-bit value s.
A second complete WIDTH scan validates the right coordinate field and its
RECORD_END; the following source RIGHT is checked. The source, axis, guide
and WIDTH heads return physically to their declared entry cells.

Finally the graph checks the actual result ROOT, copies exactly p bits
under the same guide, checks WORD_END, and emits the offset `|` and R.
It returns both borrowed heads. Thus the successful outputs are exactly

`H=L bin_p(h) R`, `S=L bin_p(s) R`, `A=L bin_p(a) | R`,
`J=L 0^p R`, and `WIDTH=L 1^h R`.

Roles22--25 are never write targets in the emitted table. Each loop has a
finite typed extent, each original value is only read, and all temporary
record-width cells are erased. These invariants prove borrowed preservation
and successful head/owned-body restoration for every stated width and
prefix, including W much larger than p.

## 4. Continuations, key composition and retirement

BUILD enters with a blank mode cell and returns HEADERS. FORWARD/INVERSE
write one fixed mode symbol in role0 and enter the same construction.
At completion the graph reads that cell, erases it and jumps to the fixed
B7 direction entry. Every old read branch and jump is relocated by the
same constant offset; all old writes, moves and halts are unchanged.
Consequently every one of B7's 21135 instructions is retained exactly once.
The mode cell lies within its already granted private window and is blank
before B7's entry checks. There is no host-selected query or record loop.

B7 then supplies its complete per-wire row routing and all-wire key writes.
The new headers satisfy its p>=h+1 condition and exact H/WIDTH agreement.
The active current result remains borrowed only until the combined graph
returns. Headers remain live for the retained radix provider. Numerical
lease retirement and source commit keep their previous ordering.

RETIRE scans each typed output body to its R, erases each body cell and R,
returns to L and erases L. It never steps past R. The offset `|` is erased
as an ordinary owned body symbol. All five heads return to their original
blank cells. This entry never touches the native roles, so it is valid at
the original post-sort cleanup seam after the numerical lease has closed.
Previously retained larger blank tails remain blank and allocated.

Successful construction, key composition and retirement have the stated
restoration. Malformed input may reject after partial changes; complete
failure cleanup, rollback and head return are not asserted. Owner alias
rejection is a binding requirement, not an allocation theorem.

For a full sorted forward/inverse roundtrip, the original physical record
i must start with key i. B7's proof then applies unchanged: forward keys
and radix move i to pi(i), inverse keys at j are pi^-1(j), and the second
radix restores the original key and opaque payload. Inverse key emission
does not undo arbitrary overwritten old keys.

## 5. Exact complete literal bill

One unit is charged for every emitted read, write, unit move, jump and halt.
Let pop(h) be the number of one digits in h. A marker rewind from cell d
to its L costs 3d+1. A native rewind from cell k to its first body cell
costs exactly 3k, including its initial left and final right moves.

| Complete operation | Instructions |
|---|---:|
| One guide-driven zero header | 12p+13 |
| One width-w skipped record, including scratch construction, both fields, erasure, all returns and fixed continuation | 32w+39 |
| Height increment with c propagated one digits | 6p+c+8 |
| Full typed marker retirement with n body symbols | 7n+9 |

Summing the h height increments uses sum(c)=h-pop(h). Directly adding the
setup, prefix-axis scans, both zero headers, skipped records, right record,
modulus padding, result copy and all returns gives the exact BUILD count

`B(h,p,m,U)=6ph+53p+41U+57m+42h+199-pop(h)`.

The exact RETIRE count is `R(h,p)=28p+7h+53`. Each joined direction has
B+2 header instructions before its unchanged B7 entry: the mode write and
the cleared fixed continuation account for the difference from BUILD.
Thus a combined successful header/key pass followed by retirement costs

`T_key + 6ph+81p+41U+57m+49h+254-pop(h)`.

Here **all** key work is retained:

`T_key = sum_(i=0)^(2^h-1) T_B6(direction,i) + 2^h(156h+126)+18h+203`.

No source-prefix term is hidden. The terminal source RIGHT is at distance
`Q=3U+4m+3h+9` from its LEFT guard, so the header bill is
O(Q+p(h+1)), equivalently O(L_source+L_result+p(h+1)) with the observed
result prefix length charged. W, U and m are not bounded by current p.

The new native read/write/move overlap is exactly

`A_native=30U+47m+12h+20p+113`.

It comprises source `12U+17m+12h+41`, axis `4m+8`, guide `16p+20`,
result `4p+14`, and scratch `18U+26m+30` actions. It is a subcount of the
literal bill, not an additional charge. The actual caller already meters
these exact physical native owners; subtract precisely this overlap from
the retained source component when reporting the combined cost vector.
Likewise subtract actual marker and payload actions from their old meter
remainders once. Numeric source, retained radix and literal graph retain
their separate execution models; no common all-caller tariff is inferred.

## 6. Historical windows and complete access

The five output windows contain 4p+h+11 cells including all markers.
Their retirement reaches no extra frontier. The mode cell consumes no
additional role or interval beyond B7's existing role0 origin.
The native source visits [0,Q], axis [0,m+1], guide [0,p+1], result
[0,p+3] and scratch [0,W+2], relative to their LEFT guards. The result
prefix's post-delimiter cell is visited during its paid return; later
contents remain unchanged. Scratch uses W+3 historical cells, regardless
of how small the current guide is.

For every role count the union of that interval and all older retained
history. The actual iterator's `_shape` already used the same width role
for every source record; reentry does not allocate a fresh owner per
record. The 27 bindings are shared physical objects, including five
native roles already owned/borrowed by the retained source caller.
B7's own per-role history union remains intact. Source/result/axis/guide
access, physical grants, backing acquisition and any external transport
are explicit supplied capabilities and costs. This is not a global stock
theorem for recursive suspended ancestors.

## 7. Resolved meter suspicion and actual source seam

An initial audit suspected that guide/result Port meters were omitted by
the old source sum. The exact bank implementation disproves that concern:
`Bank.open` sets `adapter.Port=Bank.take`; `NodeEntry` receives its guide
from bank[0], and the numerical result is bank[62]. Both belong to the
63-role bank already included in `numerical`. Four fresh actual legs
measure exactly 100 guide and 31 result header actions, all included.
Together with source192, axis14 and width-scratch255, the original helper
has 592 native actions and zero omissions. This is a resolved negative
audit, not a correction to an earlier published result.

The new `join.py` authenticates the original B7 join and B5 caller and
replaces two declared source blocks: header construction plus key emission,
and final output retirement. All numerical source/lease/commit and radix
provider code is retained. One fixed combined direction entry is selected
per externally requested leg; no current width, source value or header is
decoded to select a runtime loop. Receipt snapshots are observations only.

The actual four-tag h=2,p=5,m=2,U=8 case has B=1049, B+2=1051,
R=207 and A_native=571. The sensitive modulus-three/left-two caller's
complete new literal bills are 25679 forward and 25835 inverse. Remaining
retained source symbol counts are 117453 and 359559; remaining marker
actions14, remaining payload actions156, and retained radix instructions
43162 per leg. These are a cost vector, not a single bit-time improvement.
No prior result is improved merely by avoiding host control.

## 8. Limitations and open next questions

Current numerical offset production, linear lease acquisition and selected
leaf dispatch remain retained providers. This graph does not authenticate
an arbitrary supplied result as current, nor implement the whole balanced
source iterator. The fixed thirteen-bit payload ABI, source numerical
admission, physical access and owner grants remain explicit. General
payload widths, all-target CRT orchestration, full source/radix lowering
under one tariff and the five foundational assumptions remain open.

The proof is uniform over its typed domain; finite replays establish exact
source binding, accounting and detection of specified mutations. They are
not substitutes for universal source admission or global multiplication
analysis. No new kappa is claimed.

Prepared for @CubeJerry. Prior source authors and originating PRs retain
their credit; substantial OpenAI assistance was used for construction,
proof, implementation and review. Apache-2.0 notices are retained.
