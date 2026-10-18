# Literal owners and the recursive-rank invoice

This finite check concerns Marius-Paul Dumitrean's PR2942, head
`a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`. Its four paired helper extractions
are the construction under test. They change helpers249,251,265,267 from width
nine to eight and increase the cleanup namespace from 82 to 86 private buffers.
The construction, literal fill and existing native/outer receipts belong to
their credited authors. This package supplies a separately implemented
frame-to-owner-to-moment check. It claims no new construction or kappa.

## Model and source boundary

There are 74 replicas, nine local calls per replica, four data-bank pairs, two
sides per pair and 112 ports per side. The actual order is the 666-entry
`ORDER.json`, not the historical totals retained in PLAN or TEMPLATE. A physical
data-family *name* in this combinatorial model is
`(owner_replica, bank_pair, side, port)`, giving `896*74=66304` live data-family
names. Actual native operators and physical tape embeddings are inherited
premises; a valid name is not itself a physical realization.

The input template supplies18 positive-rank idle children, each with 112 ports.
Every child's capacity is checked equal at every port. It also supplies the
per-replica source event graph and idle consumers. Its local/bridge graph is
checked against the separate recipe. All1332 replica-child consumers and all
149184 replica-child-port bins are included, including empty bins. Cached
PLAN.windows, historical replica counts and historical stock/profile totals
are not used to reconstruct these objects.

`frames.py` computes the 408 ordered helper widths from the exact local words.
For each register it uses the dimension of the terminal frame minus that of
the entrance frame, with full GF(2)^9 subspaces rather than dimension-only
inclusion. It also reconstructs every paid local frame climb and the separate
centre descents. See `FRAMES-PROOF.md`. The owner invoice consumes that result;
the saved provider registry is only a checked comparison, not the source of
the widths used to price the fill.

## Source-event windows

Expand the actual call order into template stage blocks. Within each call,
events have positions `(call_index, slot_in_block)` in lexicographic order.
A local call touches its recipe's bank pair; a bridge touches both source
and destination pairs. For each `(replica, pair)` collect its complete sorted
list of source-touch positions. For a particular idle consumer, binary search
finds the last source touch preceding the consumer position. Let its call index
be `lo`, or -1 when no source has yet touched the pair, and let the consumer's
call index be `hi`. The permitted helper-call indices are exactly

```
lo < helper_call <= hi.
```

This is the inherited source-event loan contract. The open left boundary
forbids a helper loan during the source-touching call itself; the closed right
boundary permits a loan in the local call followed by that idle consumer.
The within-call event position matters: an idle consumer may precede a bridge
in that same call. The bridge then belongs to subsequent windows, not the
one just consumed. This is a derivation from the declared graph, not a proof
that a different physical caller obeys this contract.

This implementation collects complete access timelines before querying them.
It does not import or execute the predecessor owner engine's incremental
last-touch algorithm. `source_window_sha256` canonically binds all derived
capacity/lo/hi tuples for reproducibility.

Several child names can refer to the same physical family at different cuts.
For every `(replica,bank,side)` stream, the complete loan windows are sorted
and consecutive windows must satisfy `hi_old <= lo_new`. Thus their sets of
permitted helper-call indices are disjoint, even at a shared boundary. The
pinned data have 592 such streams and 740 successive window transitions; the
property holds on every port because the source windows are port-independent.
This strengthens per-call name uniqueness with an explicit cross-child
lifetime check. A control aliases two child sides and fails this invariant.

## Whole helper placement and every remainder

A literal fill row is `(time, helper, owner, child, port, offset)`. At each
call the rows must name each of the 408 helper identities exactly once. Their
physical data-family names must be distinct at that call, and each row must
satisfy its derived source-event window. The provider dispatch must bind every
actual call exactly once. A width-w helper occupies the integer interval
`[offset,offset+w)` in the named owner bin, with endpoints inside its capacity.

For each bin, sort all occupied intervals by their starting offsets. Starting
at cursor0, each next interval must start exactly at the preceding endpoint.
Thus these intervals are disjoint and their union is exactly a compact prefix
`[0,used)`. A bin of capacity c contributes one residual child of rank `c-used`
when this is positive, and none otherwise. This counts every unused bin, every
partially filled bin and every completely filled bin. It is independent of the
presentation order of fill rows.

This sorted-interval calculation replaces the predecessor's per-bin bitmask
implementation. The mathematical contract is inherited and explicitly credited;
using another data structure does not create a new hosting theorem. In
particular, native axis embeddings and prefix/tape constraints are not supplied
by interval packing alone.

For the actual source the reconstructed counts are:

| Quantity | Value |
| --- | ---: |
| Calls / helper roles |666 /271728|
| Source windows / owner bins |1332 /149184|
| Occupied / empty owner bins |121893 /27291|
| Total bin capacity |3580416|
| Hosted helper width mass |2204460|
| Unused owner rank mass |1375956|

The complete residual histogram is

```
{1:17316, 3:5861, 5:6215, 14:1, 48:27291}.
```

The local histogram is `{1:2434,2:632,3:286,4:104,5:26,8:8}` at every one
of the 666 calls. Adding those actual local charges to all owner residuals
gives exactly

```
{1:1638360, 2:420912, 3:196337, 4:69264,
 5:23531, 8:5328, 14:1, 48:27291}.
```

The rank mass is 4816512, equal to `65088*74`; its difference from `73*66304`
is 23680, equal to `320*74`. These aggregate identities cross-check the
construction but do not replace the individual row/window/bin checks.
The single rank14 child is an actual residual, not dispensable rounding.

## Private namespace count

The frame analyzer checks that the actual cleanup-buffer names are exactly
`704+h` for every protected endpoint h, with 86 distinct names. Both providers
agree; the parent has 82. The inherited finite namespace contract adds 408
helper families, eight centre families and two coefficient families to the
66304 data-family names. Hence the namespace total is

```
66304 +408 +8 +86 +2 =66808.
```

The checker emits disjoint half-open name ranges for these four private
categories. This is a complete count for this stated namespace contract. It
is not a full live-storage, physical capacity, movement, numerical scratch or
all-size reserve proof. It also does not price each zero buffer as a recursive
child. Such costs must be joined through the actual caller's contract.

## Mathematical controls and remaining implications

Controls change actual rows, source events or invoices: a missing or duplicate
helper, same-call family collision, a loan at its last source touch or after
its consumer, capacity spill, overlapping intervals, an unpaid prefix hole,
omission of the unique rank14 residual, the old 82-buffer namespace total,
unknown dispatch, a missing bridge and reversed per-replica chronology. A stale
nine-wide helper is also tested against the actual unchanged fill. Their
failures are checked at the intended predicates. Positive controls reverse
all fill rows and corrupt only historical cached totals; the derived receipt
is unchanged in both cases. These checks remain active with Python -O.

The exact moment comparison and a sharp *conditional* spare-child budget are
proved in `MOMENT-PROOF.md`. The new coverage is the raw finite source-to-rank
bridge; it is not merely another evaluation of a saved root. Prior PR2960
checks simultaneous dirty-input algebra and private-zero return separately.
This package checks cleanup syntax and names, not those operator identities.
Native phases/residuals, complete physical axis hosting, coefficient/prefix
and precision/tape costs, outer admission and inherited all-size/compiler
assumptions remain separate. This is a finite exhaustive replay plus written
arguments for its algorithms, with separate AI mathematical review; it is
neither an independent human review nor a formal-kernel theorem.

Credit follows `inputs/CREDITS.md` and `inputs/NOTICE`: Dumitrean/2942/2930,
Hale/2917, Diviney/2908, Kothe/2894/2833, Lu/2857, Dugongue, Tekalign,
icekylinx and retained lineage. ToikY supplied the prior explicit-subspace
frame-ledger method on PR2917, acknowledged in `FRAMES-PROOF.md`. New code
and this argument were prepared by Ross Richardson with substantial OpenAI
Codex assistance, under Apache-2.0.
