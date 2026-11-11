# Tape-driven balanced-node entry into the actual CRT numerical producer

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
All inherited source bytes and proofs are pinned in SOURCES.json.

## 1. Exact statement and source boundary

Let d>=2 be a power of two and ell>=2. Declared widths satisfy
h_i in {ell-1,ell}. Supply one physical #5353 axis stream, at head one,
containing ROOT, the positive unary width h_i, WORD_END, its h_i padded
modulus bits, WORD_END, its h_i padded current-coordinate bits, RECORD_END,
for each axis, between LEFT and RIGHT. Moduli satisfy 2<=s_i<2^h_i and
are pairwise coprime; coordinates satisfy 0<=x_i<2^h_i. Thus each h_i>=2
on the admitted domain. Put

    A=sum_i h_i,       M=2+3A+4d,       P_G=1+sum_(i in G) h_i.

M is the framed logical length. Let K_source be the complete supplied
source backing capacity, including any older inaccessible tail after RIGHT.
K_source>=M and no such tail is omitted from storage accounting.

**Theorem.** The fixed finite-symbol controller `frontend.Iterator`, given
only that stream and its fixed provider modules, enumerates the aligned
balanced nodes in increasing level and increasing start order. At each node
it constructs the exact canonical left/right records and unary guide of
#5353, physically prepares eight exact-P_G protected zero words, and invokes
the unchanged #5219 Entry and #5053 numerical producer using the unchanged
#5505 63-role owner. The result is the actual numerical result for the
current coordinates in that source. The source bytes and head are restored
at every result handoff and close. The consumer follows the linear-use
current-lease protocol in Section 4: one live result at a time, consumed once.

There are exactly 78 owned physical roles:63 numerical/descriptor roles,
eight protected words and seven topology/width roles. The supplied source
is additional. The program decodes no variable axis count, start, level,
width or precision into a host integer. On full completion or an early
close at a retired boundary, all 78 histories are blank at head one.

There is a fixed input-independent constant C_front such that the complete
one-lifecycle source-operation bill is at most

    C_front(M+2)^2 + 4096
       + sum_G [2^20(P_G+2)^4 + 2^16(P_G+2)^2 + 4096].        (1)

The sum has exactly d-1 nodes. It includes each actual numerical invocation
and retirement; reuse does not remove time occurrences. For A<=p the bill
is O(p^4) under the declared near-equal widths. Owned retained storage is O(p^2),
with the explicit rolewise bound in Section 6.
The new frontend alone has the explicit raw local Port-action envelope
2^16(M+2)^2. A numerical finite-control refinement constant is not certified;
C_front includes that remaining fixed factor. Equation (1) is therefore a
uniform asymptotic source bound, not an explicit complete-control constant.

This is a **numerical-node iterator**, not a CRT permutation of the source
or payload. It does not supply encoded synchronized row/target selection,
ROM-header preparation, three-epoch reservoir transport, source production
or binary lowering of the complete pipeline. Those remain named interfaces.
No complete `analytic_recovery` discharge or new kappa is claimed.

## 2. Manufacture and maintain the topology on tapes

The seven roles are `axis`, `depth`, `halve_a`, `halve_b`, `half`, `double`
and `width`. They use the existing fixed record alphabet. In `axis`, ONE
means an ordinary axis, STEP the current node start and VALUE the pending
next node start. None of these symbols contains an unbounded index.

Construction scans the actual source once. For each validated record it
appends one token both to `axis` and to `halve_a`. The width role is built
from the source's unary header and used to check both padded field extents;
it is cleared before the next record. No source-width array is supplied.

Repeated pairwise halving of the count tape writes one token to `depth`
per successful halving. A finite parity bit detects an odd count greater
than one. The source count is admitted exactly when it is a power of two
at least two; `depth` then has k=log2(d) tokens. The halving roles are
cleared and reused at each step. `half` starts with one token, and the
first `axis` token becomes STEP. Source and count heads return locally.

At the beginning of level j, the invariant is:

- `half` has H=2^(j-1) tokens;
- the depth head is on its jth token;
- STEP occurs at start a, where a is an unprocessed multiple of2H;
- no VALUE marker is live before entry; all other axis cells are ONE;
- source, axis and half heads are at their prescribed entry positions.

Entry scans the source and axis tape together until STEP. The remaining
source cursor is therefore exactly the first record of that node. It
consumes H records into the left canonical stream and then H into the right
stream, using the half tape as a physical unary counter and rewinding it
between the two groups. It never passes RIGHT prematurely: a is aligned
and 2H divides d. If another node follows, the next axis cell becomes VALUE.
Otherwise the axis cursor is RIGHT and the finite `last` flag is true.
STEP is retained until the numerical result is closed.

Closing first retires the numerical result and its guards. Only then does
the controller erase STEP and promote VALUE to STEP. At a last node, it
consumes one depth token. If another level exists, it doubles the half tape
through the separate `double` role and marks the first axis. If depth ends,
it retires all seven roles. Thus the invariant advances to the next node or
level, including the last/rightmost node. Induction proves the exact order
and count sum_(j=1)^k d/2^j=d-1. No callback or observer supplies the next
start, level or half size.

This uniform controller is new. The balanced node order itself is inherited
from the CRT construction and mixed-width caller. The Wave 1 whole-tree
state package still uses compiled topology; this package has no runtime
dependency on that pending contribution.

## 3. Actual input contract, not an abstract schedule

For every selected record, `_record` reads the declared unary width and
the actual padded bits. It appends that many guide tokens and copies the
two words to the selected canonical stream. The unchanged #5353
`canonical_end` removes only high zero padding and retains one bit for zero.
After both groups, the controller appends one extra guide token. Hence
the guide contains exactly P_G tokens and the two streams are bytewise
the same canonical records as an admitted #5353 RowEntry at that node
and synchronized row zero. Row zero activates every selected axis on the
declared width family. No row-zero numerical identity is used: the numerical
result depends on the source values and the selected node, not that row.

The source scanner restores its physical head to one. It writes no source
cell, including during canonical trimming. It has validated the whole
source's framing at construction, so stopping a later projection after
the selected node does not lose an unexamined shape premise.

The eight protected words are owned auxiliary roles. Before each entry,
`_prepare_guards` scans the live guide, writes exactly one zero per token
on each role, writes RIGHT, and restores both heads. The eight words are
disjoint from the source and numerical bank. They satisfy the unchanged
dirty-word contract using its admitted all-zero case; a historical old
width is never passed as a new exact-width word. The numerical entry and
producer preserve them. After numerical retirement, local scans erase their
data and markers before any new guide is constructed.

The complete node modulus product is <2^(P_G-1); P_G>=5 and the selected
groups are nonempty. These are exactly the guide/numerical capacity premises
of #5219/#5053. The old Entry constructs its templates and padded records
from the actual guide, with its existing `Extent` rather than a decoded P.
Its numerical producer is unchanged and actually invoked.

The #5505 Bank is unchanged. It still acquires the three canonical/guide
roles first, then56 private numerical words, a template, and three padded
input/output streams:63 roles. Its public `open` call has a fixed legacy
signature; the new controller passes `None` in every compiled-geometry
position and supplies the actual new scanner through its bridge argument.
The scanner rejects any non-None geometry argument. Its `active` is the
fixed successful-node case. All source/protected alias, acquisition-count,
marker, head and release checks remain the actual predecessor checks.

This substitution is justified by the identical canonical inputs and
guide, identical acquisition sequence, and source restoration just proved.
It does not infer compatibility merely from similarly named interfaces.
The existing producer's left-invalid disabling and padded-right semantics
are inherited. It computes current-coordinate CRT reconstruction, not a
host reconstruction from purported original digits.

## 4. Handoff, retirement and failure boundary

The physical interface has three finite phases: retired, current-result-live
and complete. Calling next in the retired phase acquires the single current
result; its one close consumes that result and returns to retired or complete.
The consumer may inspect or use the current output according to the inherited
port contract, then must relinquish the lease and its borrowed output aliases.
It may not retain a consumed lease as a token to submit after a later next.
These are linear-use preconditions, not a runtime generation-validation API.

The numerical lower/product words and output stream remain live in their
actual bank until the returned lease closes. Their production, framing,
head returns, pending capacity and subsequent disposal enter the numerical
bill. The iterator hands off these owned roles; it does not claim a free
copy to an external consumer. Any consumer's additional copy or routing
must be paid by that consumer. The observer in verify.py is outside runtime
and never supplies a value or branch to it.

Closing consumes the numerical result, closes Entry, retires the three
canonical/guide roles and eight protected words, and releases the bank
before advancing the encoded cursor. Every numerical role follows #5505's
delimiter-driven varying-precision reentry. A shorter new use cannot expose
old numerical data, since the historical suffix was blank before entry.
Longer use grows only by local writes. The topology roles obey the same
append/clear discipline. No list backing is replaced or shortened.

An early iterator close is allowed only at a retired node boundary and
clears all remaining topology roles. Current-phase errors, such as next or
iterator close while a current result is live, or a second close before any
later next, require no tape traffic and can be rejected by the finite phase
state. Charge a fixed input-independent C_reject for each such external
attempt. An arbitrary count of rejected or post-completion calls is not
hidden inside a single-lifecycle bound. One terminal next() returning None
is included in(1).

The Python interpreter additionally checks each NodeLease object's closed
flag, even if an external client retains that old object through later
entries. This convenience guard is outside the physical error interface:
no constant-space validation of an unbounded history of stale host identities
is claimed. Under the linear-use protocol, the fixed current continuation
fields can be reused at each node. The interpreter's fresh wrapper objects
and an observer's retained trace are not extra physical tape roles. The
duplicate-close control in verify.py runs before a later next, so its physical
analogue is exactly the retired-phase error just specified.

During initial shape preparation, a framing or nondyadic-count ValueError
restores the source head and retires all seven preparation roles. Numerical
entry has not begun, and the 63 bank and eight guard roles are still blank.
For a well-framed finite source whose count is rejected, this cleanup has
the same quadratic frontend allowance. The domain does not claim rollback
after a later violated arithmetic/coprimality premise, arbitrary external
port corruption, interruption, or malicious consumer mutation.

## 5. Complete source-operation time

The cost unit is the retained fixed-alphabet source operation: local symbol
reads/writes, unit head movement and bounded finite control. It is not a
literal binary-TM transition or a count of Python heap operations.

Here is a conservative audit of the new frontend. For a record with width h,
all width manufacture/rewinds, two field scans, optional guide/canonical
copies, canonical trimming and width retirement use fewer than 64(3h+4)
raw Port actions. This follows by charging each width/field bit for its
read, copy, unit moves and both return scans; canonical trimming visits at
most h cells per word. Record and endpoint constants are covered by the
four tags in3h+4. Thus a prefix-plus-node source scan costs at most64M.
It includes a rightmost node, which may require the entire source.

For one protected word, direct expansion of the unchanged Port methods gives
9P+14 raw preparation actions and 5P+15 retirement actions. The total is
14P+29, so all eight words use at most128(P+2)<=128M actions. This count
includes the guide scan and its repeated rewinds; it is not the compiled
constant-width preparation count from the earlier whole-tree package.

Source/axis rewinds, half-counter passes, pending-cursor installation,
canonical/guide endpoint formation and retirement, and cursor advancement
bring the new per-node raw-action allowance below 512(M+2). Reentry/release
of the 63 numerical roles is separately paid by the inherited4096 allowance.
Root shape manufacture plus rejected-shape or final cleanup is below
512(M+2). Pairwise count reduction processes fewer than 2d tokens in total.
Half doubling across completed levels processes fewer than d tokens in
total and adds less than 128(d+2) actions. These charges count every reset,
not only the initial source scan.

There are d-1 nodes. Including the initial/final allowance, the preceding
raw counts are bounded by 512d(M+2)+128(d+2), which is below
2^16(M+2)^2 for d<=M and M>=22. This is an explicit envelope for the new
local reads, writes and unit moves; it does not count a particular expansion
into primitive finite-control instructions. The verifier's numerical
comparison uses this raw-action envelope only.

For the complete source bound, all additional control is a fixed finite
refinement. The seven dictionary keys and all role selections are fixed;
the role loops have lengths two, three, seven or eight. The remaining variable
loops read a local tape symbol on each iteration. Their predicates inspect
fixed-alphabet symbols, finite flags, or identities among the fixed role
slots. There is no recursive call or input-sized host-container traversal;
the call depth is fixed. Under the linear-use interface, the current entry,
lease and provider references are a fixed set of reusable continuation
fields. Expanding these finite blocks gives some fixed multiplier for
each local action and a fixed allowance per entry/exit. Their exact
primitive-instruction counts have not been enumerated here, so no numerical
multiplier such as32 is asserted. Since the numbers of nodes and levels
are at most d, a fixed input-independent C_front bounds all this control
and the raw actions by C_front(M+2)^2. This proves the first term of(1)
without inferring a universal constant from the finite measurements.
The predecessor arithmetic remains in its own source tariff.

The unchanged Entry/numerical theorem contributes
2^20(P_G+2)^4+2^16(P_G+2)^2 per node. The unchanged bank contributes4096
initially and 4096 per node. These and the frontend give(1). There is no
unfunded setup, cleanup, source seek, final-node or output-lifetime term.

For completeness, near-equal widths imply d(ell-1)<=A<=p. Summing by node
size n=2^j, with d/n nodes per level, gives

    sum_G(P_G+2)^4 < (8/7)(ell+3)^4 d^4 <=715p^4,
    sum_G(P_G+2)^2 < 2(ell+2)^2 d^2 <=32p^2.

The second geometric series has ratio2. The proof does not reuse the false
4/3 coefficient corrected in Wave 1 review. Also M<=8p and d<=p. Hence(1)
is O(p^4), with a constant depending on the fixed frontend refinement.
No explicit complete-control numerical majorant is asserted. This is a
numerical-node statement. It is not a full E(p,ell) bit-step theorem
or a complete multiplier bound.

## 6. All historical storage

Write P*=A+1. #5505's rolewise bounds apply because the new canonical inputs
and guide have the same formats and acquisition order. A safe envelope for
all 63 roles is

    (P*+1) + 2(2A+2d+2) +57(P*+2) +3[d(P*+2)+2].          (2)

This includes transient canonical padding before high-zero trimming.
The guide, canonical left/right streams,57 word/template roles and three
padded streams are all separate physical backings. It bounds the maximum
of each role's entire history, then sums; it does not take the maximum of
standalone aggregate node storage.

The eight protected roles add8(P*+2). Each of axis, depth, the two halving
roles, half and double has capacity at most d+2; width has capacity at most
A+2. Both endpoints and every retained blank tail are counted. Including
the supplied source, the complete envelope is

    K_source + (2) + 8(P*+2) +6(d+2)+(A+2).               (3)

There are78 owned roles plus source. For A<=p, (3) is K_source+O(p^2).
It becomes O(p^2) including source when K_source=O(p^2), in particular for
the exact framed input. The source
production workspace and any external result consumer are separate,
explicit boundaries. The bound counts retained tape cells, not Python
allocator capacity. No erased cell is treated as physically deallocated.
The theorem covers one iterator lifecycle; constructing another fresh
iterator does not entitle an enclosing caller to discard the previous
78-role backing. Same-bank whole-iterator restart is not an implemented API
here and would require its own entry/marker argument.

## 7. Evidence and next obligation

The verifier executes14 actual numerical nodes in four complete trees,
including nonzero starts, changing half-size and precision, invalid-left
disabling and padded right coordinates. One fixture traverses all seven
nodes of an eight-axis tree. It independently solves the small congruences
by exhaustive integer search and compares the actual lower/product words
and complete numerical output records. The oracle is observation only.

Runtime geometry/decoding names in the new module are poisoned; physical
constructors and Word.inspect are sealed after initial fixed acquisition.
Every source snapshot, bank identity, protected current extent and complete
retired historical tail is checked. Controls detect live reentry/close,
double close, a supplied host geometry, stale history, malformed dyadic
count with actual cleanup, omitted half doubling, and a Boolean/integer
receipt substitution. Finite execution corroborates the written proof.

The next consumer seam is the actual #5496 row query: it still takes a
compiled row/target selection and manufactures h/layer ROM headers from
host constants. This iterator supplies its numerical input objects, but
does not yet replace those remaining arguments or update source coordinates
between synchronized rows. Encoded row selection and retirement-before-write
binding must be proved before claiming a uniform whole-tree CRT transform.
All five selected assumptions and kappa .00363005817 retain their status.
