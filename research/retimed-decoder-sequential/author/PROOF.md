# A charged representation of the retimed decoder's own control

## 1. Claim, source and boundary

This note treats the **decoder-owned control values** of the binary
`transport.Plan.decode` used by Ali Romman's #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. The comparison base is canonical
`e54523517d0f03e58352e647c403a5af3e525a57`; the immediately preceding storage
package is #8091 at `b500f72bbcf9c03a7f7fd40b366eedd6d1dd285b`.
`SOURCE-BINDINGS.json` pins each source and predecessor proof.

Let a successful production binary activation have height h>=3000,
N=2^h, B=N^92, and complete input volume W **bytes**. Retain the legal-call,
owner-custody and return conditions of the predecessor. Its numerical
corollary gives

    P = 18906, q = 104904,
    C* = sum_e count[e](q delay[e]+1) < 2 N^83,
    owner capacity < 2B.

The source geometry gives W/B>=3^(2N). We construct a value-exact binary
representation of the external rows, decoder `live` and `pending` tables,
ordered zero lists, current event and leaf continuation, together with an
explicitly stored immutable event tape and common exact chart dictionary.
The sum of uniform per-role allowances, including two state images and the
transfer workspace below, is strictly less than

\[
\boxed{32BNh\ \text{bits}<8W\ \text{bits}.}                 \tag{1}
\]

Thus this particular collection of control roles uses less than one W-byte
allowance. At a source event boundary the representation is injective on
admitted values, and its decoder has the same ordered interface calls and
returned Job values as the source. A suspended leaf retains the full ordered
job and its loop continuation, not only the one-axis argument of that leaf.

**This is not the full controller or fixed-tape theorem.** A bounded integer
slot names each resident native iterator. The iterator's own registers,
restoration lists, chart caches, suspended Python frames and numerical data
are separate service state; their storage and execution cost are not erased
by that name. The construction does not serialize a native generator across
a process restart. Other `Receiver`/`Frame` private controls, physical field
headers, input/output backing, outer CRT/Gaussian fields, setup workspace,
and all movement/time costs remain separate. In particular we do not infer
the retained fast tariff from a potentially slow table scan.

The reference program checks emitted bit images and source correspondence.
Its Python dictionaries, arbitrary precision integers and expanded objects
are a correctness emulator, not an asserted bit-space implementation of
CPython. The representation can be stored on sequential binary tapes and
looked up by scans; those scans and table construction require a later
explicit time analysis. No source runtime, selected certificate or activation
threshold is modified.

## 2. The actual axes have bases

A paid binary Job is not generally an integer axis list. The retained
`raw_binary.Axis` stores `(basis, column)`, and `placed_job` makes

    Job(owner, tuple(Axis(frame.word, i) for i in frame.mask)).

Dropping `basis`, treating the mask as a set, or replacing its order by a
sorted order is invalid. `Job.select` takes positions in the existing tuple
and preserves their order and the associated basis. The `job_frame` identity
shortcut also tests value equality when basis identities differ. Rebuilding
an equal immutable tuple is therefore valid; pointer identity is not a
scientific requirement at this interface.

### Exact paid-basis closure

The raw source has exactly three yielding branches:

* an inner MOVE uses `catalogue.difference(first,last)`;
* a QUERY uses `catalogue.head(port)`;
* an IDLE_ONE uses `catalogue.idle(stages)`.

The last has empty word. `head` lifts a fixed joint word.
`ActiveCatalogue.difference` lifts the fixed difference word returned by
`fixed_binary_charts`. No matcher/restoration word is emitted as a paid
Job basis. The target matchers used privately by the native generator remain
outside this decoder library and its storage claim.

The immutable eight-coordinate graph and caller give 104,904 ordered paid
labels: 100,908 MOVEs, 444 QUERYs and 3,552 IDLE_ONE labels. Every occurrence
is checked against its literal graph/caller site, including bank and rank.
There are 2,481 distinct paid shape requests. Deduplicating the exact
rational words from the source difference and joint tables, with one empty
word, gives **595 words**, each of length at most **61**. The signed
numerator and denominator bounds each need at most five bits in the stated
sign convention. This is a complete finite source census, not a claim
inferred from testing a few production heights. Its complete canonical JSON
encoding has 215,644 bytes, hence fewer than 2^21 bits; its SHA256 is
`734035814cb639382a12a81e7f408b222f949cd69ad28a28544aeb5d0490d3f9`.
The encoded dictionary stores the signed rational numbers themselves.

For a fixed base word v=(v_0,...,v_(m-1)) and positive column multiplier c,
`Catalogue.extend` emits the ordered concatenation

\[
 L_c(v)=\mathop{\Vert}_{i=0}^{m-1}\mathop{\Vert}_{j=0}^{c-1}
           \operatorname{coordinate}(v_i,k\mapsto kc+j).       \tag{2}
\]

It also emits the ordered mask `(i*c+j for i in mask for j in range(c))`.
Equation (2) is the literal pair of loops in the source; concatenation
induction proves it for every positive c. A difference or joint base word
has coordinates in 0,...,7. The constructor's ambient check ensures every
expanded coordinate and paid mask entry lies below N. Identity masks may
use the larger body-axis range, and are still below N by the same check.
The Plan constructor's four-rank margin and funded paid-to-target inequalities
ensure every productive and paid axis list has length at most N.

Consequently every paid Job can be represented by an owner, a basis-kind bit,
a common-word index, c, and the **ordered** list of actual coordinate numbers.
Plain external/zero Jobs instead carry the integer-axis kind. Empty bases
use one canonical empty token with c=1, without identifying typed axes with
integer axes. A selected nonempty subjob inherits its word token and its
ordered subsequence; no new basis is needed. The decoder's zero exemplar
is a selection of an external integer row, and binary `Machine.zero`
preserves that exemplar's axes. Induction over opens, paid resumes and
pending-loan collection proves closure for the actual caller.

A token's expansion is checked by exact rational equality. The inverse lookup
may try the finite common dictionary; for a nonempty candidate base word its
possible c is determined by the ratio of word lengths. If different tokens
expand to the same word, choose the first fixed dictionary entry. This does
not change any source value. An unsupported basis is rejected, rather than
stored as a free opaque object.

## 3. Inclusive tables and fixed-width scalar values

Put C=2N^83. The inherited inclusive lifetime argument bounds live or
currently opening/closing native origin contexts by C*. It includes the
closing resume after the last paid label. In particular

\[
 |live|<C,\qquad \sum_{context}|zeros|\le P C.                 \tag{3}
\]

A pending loan is created by one paid resume of its still-live origin.
Each context has q paid resumes. It is collected during the issuing tick,
and the descending-delay custody proof puts its child return before the
parent resumes or closes. The deliberately coarse bound

\[
 |pending|\le qC                                                \tag{4}
\]

therefore follows even if every live context were charged all q of its
pending records at once. Selection aliases an owner; it does not make a new
owner. The descriptor count and the physical owner count are distinct.

The source keeps B external rows, each with N ordered integer axes. The
representation below charges all of them separately, without assuming
pointer sharing. It also charges every zero-list entry separately, even
when its axes could be shared. There is no free dictionary of arbitrary
Jobs in the storage argument.

Choose one scalar width

\[
 w=128h\ \text{bits}.                                          \tag{5}
\]

All dynamic scalars at this boundary are nonnegative. Signed rational basis
coefficients reside in the charged common dictionary. A negative owner,
negative axis or unsigned scalar overflow is rejected by the codec.
Here are sufficient source bounds for the nontrivial scalar fields:

* owner identifiers are less than 2B=N^92*2;
* native slots and live counts are less than C<N^84;
* pending counts are at most qC<N^85;
* `ticks=N^82`, `rounds=N^2`, and the number of bands is less than N;
* the largest actual `count[e]` is below 2N^6, so a context identifier
  `(birth*span+band_index)*maximum+replica` is below 2N^89;
* the total paid serial count is `q*ticks*sum(count)<2qN^88<N^90`;
* `source_width<=B`, and a tested external index before its guard is below
  `B+source_width+1<3B`; valid row indices are below B;
* a common word index is below 595, while lengths, columns and axes are at
  most N. The row/bit offsets in the encoded images below are below N^96.

All fit (5) for h>=3000. In the external-index estimate, `_external`'s base
is inside the source interval assigned by the constructor; `cycle` can only
reach that interval's end when the source's round guard rejects it.
`group<ceil(B/source_width)` gives the displayed bound. The event clock may
continue past `ticks`, but a context identifier encodes its birth, which is
strictly before `ticks`. Negative trial births are never emitted as records.

A Job record contains owner, common-word index, multiplier and list length
in four w-bit fields, one kind bit, and its ordered list in h-bit coordinates.
Its maximum bit length is

\[
 J=4w+1+Nh<2Nh.                                                 \tag{6}
\]

The last strict inequality uses N>=2^3000, not an unasserted small-instance
convention. The generic reference codec uses explicit limits instead.

## 4. A concrete tape format and exact correspondence

The state image begins with five w-bit fields: group, round number, row
count, live count and pending count. Then it contains:

1. the B external Jobs in their original order;
2. live contexts in increasing identifier order; each has identifier, native
   service slot, zero-list length, then its zero Jobs in original order;
3. pending loans in increasing serial order; each has its serial and Job.

Counts delimit the variable lists. Padding at the final byte is zero and
validated. Parsing rejects duplicate/out-of-order keys, duplicate service
slots, overflow, unknown basis kinds and trailing or truncated fields.
The sorted **dictionary keys** impose a canonical representation; they do
not sort any scientific axis list or the zero retirement order. The external
service table contains the native bodies. Its resident service associated
with a slot is part of the explicit hypothesis, not serialized by this format.

Packing followed by unpacking preserves every Job value by Section 2 and
every integer field by fixed-width binary uniqueness. It preserves the exact
associations and zero-list ordering. Source `live` dictionary iteration order
is immaterial: the source only addresses/pops the supplied identifiers and
checks final emptiness. Similarly pending keys are looked up by serial.
Thus changing dictionary representation has no effect on the native interface.

The transition proof is induction on source records:

* **Open.** A kind-1 binding removes precisely the same pending Job. A kind-2
  binding applies the identical cycle/index guards and calls `axes` on the
  same source row. Otherwise both call `zero` on the same ordered selection
  of row zero. The port sequence and columns passed to `native` agree.
  A fresh bounded service slot records that same resident iterator, and the
  zero-list is kept in its source order.
* **Paid.** Both resume the same related native service. The returned Job and
  size guard agree. Both issue one-axis leaves in increasing k from selected
  through size-1, then retain exactly the selected prefix when it is nonempty.
  The code also roundtrips the full paid Job and `(ident,serial,size,selected,k)`
  at every leaf callback. Returning from that callback restores the full
  continuation for the next k.
* **Close.** Both remove the context, perform its final native resume and the
  same no-extra-loan check, then retire zero Jobs in their original order.
  The slot is released only for that completed context. Complete native
  cleanup itself is inside the retained service contract.

At all callback boundaries the interface arguments and call order agree;
related native service states can therefore be advanced together. Complete
successful execution ends with the same empty live and pending tables.
This proves observational equivalence at the stated boundary; it is not a
serialization theorem for the external native implementation.

During a partial open/paid/close operation it suffices to reserve
`(2P+8)J+(4P+20)w` extra bits for port/zero lists, the current/full/selected
Jobs, the current row, cursors and finite program counter. The two partial
P-entry lists are charged separately, even if entries alias. Closed lists
or old locals can be discarded after their last use; in the representation
this is explicit local overwrite, not retirement of a scientific owner.
For the delivered expanded Job basis, allow an additional `256Nh` bits:
at most 61N operations, two h-bit coordinates and two signed five-bit rational
fields per operation, plus mask and header, fit that bound at h>=3000.
This extra is a bridge for one currently transferred Job. It does not pay
for all basis copies still retained inside native service bodies.

## 5. The calendar is charged too

The source caller passes `self.events()` into each decode. Leaving that
generator's own `pending` dictionary uncharged would merely move the problem.
For this representation store its **entire immutable event tape**, once per
installed Plan, and reread it for each group and round. `Plan.events` depends
only on the fixed Plan, starts serial at zero, and is identical on these
calls. Store a scalar number of records, then prefix-decodable rows: opcode
0 has two more leading scalars and P kind-delimited bindings; opcode 1 has
four more scalars; opcode 2 has one. The parser knows P and validates each
kind, so no free row separator or host object is required.

Let S=sum(count)<2N^6 and T=ticks=N^82. There are exactly TS opens, qTS paid
rows and TS closes. An opening has at most 3+4P scalar fields. Hence the
complete stored tape has at most

\[
 K_{events}=w+TS(5+4P+5q)w
       <w+2N^{88}(5+4P+5q)w < BNh.                            \tag{7}
\]

Empty/boundary replica cases do not increase this count. The very large
fixed tape is counted in space even though it is not constructed at a
production height by our tests. Its construction time, source Plan setup
workspace and movement to successive records remain open costs. They are
not assigned the old constant or removed from the complete multiplier bill.

## 6. Uniform per-role allowance and histories

For the two state-image roles, separately use the bound

\[
 K_{state}=5w+BJ+C(3w+PJ)+qC(w+J)<3BNh.                    \tag{8}
\]

This bounds each image at every source cut, regardless of which context,
zero list or pending loan attains a maximum. Add (7), the transfer workspace
from Section 4, and the common dictionary's 2^21 bits. Thus

\[
 K_{total}=2K_{state}+K_{events}+(2P+8)J+(4P+20)w
                  +256Nh+2^{21}<32BNh.                     \tag{9}
\]

These inequalities use fixed P<2^15, q<2^17, h>=3000 and N=2^h. For example,
J<2Nh, C=2N^83 and P,q<N make the non-row terms in (8) at most a fixed
multiple of N^85 h, whereas BNh=N^93 h. Each static or transfer term is also
below a fixed multiple of N^89 h. The explicit rational/integer arithmetic
in the checker records the substitutions at three heights; the unbounded
conclusion follows from the displayed powers and increasing N, not those
three examples.

The actual compiled owner field is

    W/B = unused * low * high * older * alpha^(2Nf) * gap * suffix,

with all factors positive, alpha>=3, f>=1. It is consequently at least
3^(2N)=9^N. Since h<=N and 4N^2<=9^N for every integer N>=2,

\[
 (32BNh)/8 =4BNh \le B9^N\le W.
\]

The elementary inequality starts at N=2 and propagates because
`(N+1)^2<=9N^2`. This proves (1). Byte-rounding a fixed number of physical
files adds fixed end padding; it can be covered by the strict slack in (9),
or charged explicitly as that many seven-bit allowances. It does not change
(1) at production heights.

### Conditional ancestor and warm-history consequence

The predecessor's actual same-stage child has volume at most W/B; the
covered child is smaller still. If the described fixed roles are installed
as LIFO control tapes, each ancestor contributes its own coordinatewise
allowance, and for one stage the extra control history is strictly below
`W*(1+1/B+...)<2W`. This is an additional control-representation term,
separate from the previous ordinary **data-file** coefficient.

For a fixed installation of m<=7 stages, the predecessor's stage entrance
bound is W_j<2^(m-j+1)T_ternary, with T_ternary<9X. Thus this additional
control representation has historical extent below

\[
 2\sum_{k=1}^{7}2^k\,T_{ternary}
       =508T_{ternary}<4572X.                               \tag{10}
\]

The sum is over fixed roles and maximum histories; it does not assume their
peaks are simultaneous. Each per-role quota is uniform over permitted
shapes, so X can be replaced by X_max for differently shaped public calls
in one installation. With initial reserved endpoints K_init,r, use
`max(K_init,r, c_r X_max)` per role. Erasure never subtracts an old historical
reservation. A different installation, added role or change to the callback
boundary requires a new check. Equation (10) excludes other controller and
service state exactly as (1) does, and must not be added to a total-space
claim that silently omits those remaining terms.

## 7. Evidence, limitations and credit

The author checker authenticates all copied sources; reconstructs the fixed
rational library; checks the complete 104,904-label incidence; and tests all
2,481 paid shape requests at columns 1,2,5, including reversed and sparse
ordered selections. It also executes the actual raw source generators and
actual chart constructors for one complete 104,904-loan native word at one
column, abstracting numerical bank data actions. That test checks metadata,
labels and owner existence, not the numerical field operator.

Twelve supplied-calendar fixtures execute the unchanged source `Plan.events`
and `Plan.decode`, then compare their complete ordered service traces with
the packed replacement. They include external source periods, the failed
external index guard, zero inputs, selected loans, child return and complete
closure. Counts/delays are supplied small fixtures, not production mass
outputs. Exact emitted-bit roundtrips and negative controls cover signed
source bases, axis order, truncation, header underwidth, forgotten zeros and
a mutated actual source loop which wrongly serves the borrowed prefix.
Finite runs corroborate the universal source/encoding argument.

Open next work is to charge the actual suspended native restoration and
register state, then the remaining whole-Receiver headers, and to supply
fixed-tape lookup/movement and setup tariffs. None is made free here. This
local implication advances a stated `precision_tape`/`owned_erasure` control
interface but discharges no complete canonical assumption and changes no κ.

Ali Romman and the retained contributors receive source, fixed-chart and
retimed-schedule credit. #8091's owner census, numerical corollary and ordinary
geometry remain predecessor theorems. The generic coordinatewise-history
principle belongs to the credited #5286/#5404 lineage; the new content is the
actual typed-axis closure, exact decoder image, charged event tape and its
source-specific bit allowance. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Model-assisted review is not independent human
acceptance or a formal-kernel proof of the multiplier. Apache-2.0.
