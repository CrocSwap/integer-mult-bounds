# Independent physical-router review

PASS, subject to the stated valid-input and distinct-port ABI. No implementation,
direction, workspace or head-restoration blocker was found. The source proof's
all-size invariant and exact ledgers agree with independent inspection of every
instruction path. This is internal AI-assisted author-side review, not external
scientific acceptance or a formal proof-kernel result.

The physical macro realizes an existing address map. The whole-high batch
geometry, fresh-cylinder rule, divisor L=B*|GL_N(F_q)|, ancestor-weight condition
and abstract allocator are predecessor results, especially PR5829. The new
scope is a concrete fixed-control low-type split/merge machine and its complete
local bill. It does not itself supply a whole Gaussian child, generated-weight
evaluator, right matcher/fallback implementation or full production dispatcher.

## Code and entry conditions reviewed

The final `router.py` snapshot has SHA256
`ccfb60465cacd3d0f458f96a505c43f5ccda6bb8eacd6ca67f8177f5fb1796a3`.
`machine.py` and `counters.py` are the unchanged pinned PR2776 sources.
SOURCE-SNAPSHOT.json records all reviewed bytes. The earlier router annotation
was merely tightened from its looser resource bound to94V/13V; the assembled
instruction tables did not change.

L>=2 and direction are compile-time choices. Runtime A,R are positive canonical
LSB-first binary descriptors. Data inputs and descriptors have LEFT at local0,
their data starting at1, RIGHT immediately after their declared extent, and
heads at1. Each destination and scratch local work body is physically blank
at its origin0. All physical ports are distinct. Only these local extents are
owned by the macro. Protected ancestor prefixes and existing entry backing are
not claimed free. This is not a total recognizer for all malformed global tape
configurations; missing or malicious LEFT markers are outside the valid ABI.

The source interpreter's Tape/Machine classes are not used by this audit.
`audit.py` imports the finite assembler and producer only to compare their actual
serialization with all eight sealed TABLES.json records. It then walks the
sealed records with a separate implementation of branch, write, unit move,
goto, halt and reject. Only the external test interpreter knows head positions,
step counts or sparse dictionaries; the emitted program can read none of them.

## All-size value and head argument

Before batch a, a*L*R source bits have been consumed and each low-type output
contains a*R bits. `copy_block` rewinds its unary R guide, copies exactly R
bits into the next fixed bank, and advances both data heads by R. Both payload
symbols have the same instruction count. Repeating its fixed L copies leaves
the invariant for a+1. On the A guide's RIGHT marker, the source head is exactly
at its required data-end marker. The merge uses the same induction with bank l
as the source and one output; its inputs may be arbitrary changed child results.
It never reinstalls the saved original source instead of returned data.

The binary converter preserves its source bytes. It copies the descriptor to
one scratch, decrements that canonical copy with shrinking right delimiter,
and writes one unary mark for every positive countdown value. At powers of two,
all lower bits have become ones when the top delimiter shrinks. At zero, the
entire work body has been physically blanked, leaving only its caller-installed
LEFT. All three converter heads finish at1. This permits immediate reuse of the
same binary work tape for R after A.

At router completion, source and destination rewinds stop at their own valid
LEFT markers and finish at first-data position1. Descriptors were already
restored by conversion. Unary guides are erased backward through all UNITs,
their RIGHT and their installed LEFT. The binary work body is already empty;
its retained LEFT is removed by the same erase routine. All three scratch heads
finish at their original blank origin0. No valid execution reaches a negative
local coordinate, so unrelated protected prefixes are preserved.

## Exact action count

Let c(x)=24x-7popcount(x)+15bit_length(x)+12, the retained counter ledger.
For d=L split destinations or d=1 merge destination:

| Actual code part | Transitions |
| --- | ---: |
| Destination/scratch marker installation | 3d+9 |
| Binary guide construction | c(A)+c(R) |
| All payload copies plus R-guide rewinds | 12V+4AL-3R |
| A loop and its terminal branch | 3A+1 |
| Input ends and output terminators | L+1 |
| All source/destination head returns | 6V+3(L+1) |
| Three scratch erasures, including markers | 4(A+R)+18 |
| Final halt | 1 |

The first block starts with the R guide at1, so it saves3R compared with later
blocks. A copied bit has nine transitions; each subsequent guide rewind costs
3(R+1). These observations independently give the payload row of the table.
In particular scratch erasure is4(A+R)+18, not4(A+R)+12: each of its three
marker cleanups contributes six.

The sum is exactly

    T=c(A)+c(R)+18V+4AL+7A+R+4L+3d+33.

Because c(A)+c(R)<=44(A+R)<=44V, AL<=V and A,R<=V/2,
the first variable terms are at most70V. Then d<=L<=V and33<=16.5V
give T<=93.5V<94V. Split at L=2,A=R=1 attains187/2 transitions per
payload bit; merge takes184 transitions. No payload-dependent shortcut enters
the bound. It is a valid all-size inequality, not fitted timing data.

## Exact visited-space classification

Every visited set is contiguous within its local nonnegative interval, and
its end is determined directly from the loops:

| Physical tapes | Sum of visited spans |
| --- | ---: |
| Preserved data source(s) and new destination(s) | 2V+2L+2 |
| Preserved binary descriptors | ell(A)+ell(R)+4 |
| Unary A and R guides | A+R+4 |
| Reusable binary work | max(ell(A),ell(R))+2 |

Thus

    S=2V+A+R+ell(A)+ell(R)+max(ell(A),ell(R))+2L+12.

Use A+R<=V, ell(A)+ell(R)<=A+R, maxell<=max(A,R)<=AR<=V/2,
L<=V and12<=6V. This gives S<=12.5V<13V. The smallest instance has
25/2 visited cells per payload bit. The full-execution visited union bounds
every prefix; blanking a scratch cell does not subtract it from the bill.
Unused tapes and pre-existing backing must remain in K_entry, so the correct
total statement is K_entry+13V, not a claim of deallocation on erase.

## Independent PR5829 address check

The reviewed predecessor writes current parent and child row indices as

    b = (U'*(L*H)+l*H+h)*H^j + ancestor,
    b'= (U'*H+h)*H^j + ancestor.

Here U' has range A=T*(LH)^(D-j-1). For fixed U',l the complete tuple
(h,ancestor,body) has contiguous range R=H^(j+1)*R_body. Therefore the
parent's physical bit address is precisely ((U'*L+l)*R+r), while the output
bank's address is U'*R+r. Removing l is exactly the new splitter, and
reinserting l is exactly the merger. No original high value, ancestor
coordinate or body fiber is removed. Its volume divisor is the fixed L,
not the input-dependent L*H. At w=1, H=1 and the formulas specialize correctly.

L=B*|GL_N(F_q)| is fixed only after the final finite template and q are fixed.
The runtime high-matrix count H belongs inside the streamed block R, not in
the number of physical ports. This is the predecessor's existing whole-high
batching result; the physical table implements its boundary. Forming the
binary A,R descriptors and evaluating weights remain separately charged work.

## Independent finite evidence and limits

`audit.py` executes198 full split/merge cases, including powers-of-two conversion
boundaries, large asymmetric extents, three payload patterns, and fixed L=2,3,5,96.
Every source/descriptor byte, output bit/order, head and scratch marker is
checked, including protected negative-coordinate guards. It independently
executes the binary-converter table for every N=1..256 and compares the exact
c(N)+halt ledger. Five malformed local inputs must reject. Its largest ratios
are exactly187/2 transitions and25/2 cells per payload bit, matching the
written extremal instance. This grid corroborates the static proof; it is not
the reason that the unbounded theorem holds.

Run `python3 -I -B audit.py` or `python3 -O -I -B audit.py`. Default runs are
read-only and compare INDEPENDENT.json. The output banks are source-preserving
owned copies. Their later release, bridges and any simultaneously retained
copies must be charged by the enclosing caller, with no productive credit.
This local theorem does not change paid Gaussian jobs or kappa, remove a full
framework assumption, establish global precision, or claim scientific admission.
