# A concrete sharing attempt and its complete cost gate

This investigation starts at PR673 commit
`156f259b99723468cfdd2b5d47d0ba894f09bea7`. The selected frontier is unchanged.
Its purpose is to price a construction before implementing a supplier.

## 1. Success means an operator and a paid invoice

The requested goal is at least 100 **net** paid rank units removed per local
invocation, not 100 removed from the local word while added at another
boundary. There are 288 invocations. Thus the requested net global credit
is at least 28,800 against the pinned rank mass 1,808,352.

Admission also requires a strict rational moment below one at some c>1/99,
using actual child widths and volumes, plus:

- The exact all-role BIT operator, including arbitrary incoming dirt.
- Legal common labels at every source read and every scalar operation.
- Chronological owners, exclusive access, and restored or explicitly owned
  disposable workspace; all live storage counted.
- Consolidation, chart transport, remaining idle work, source access,
  initialization, cleanup, fallback, and finite compiler costs.

The retained W=28416 denominator is productive volume. Extra work rows do
not enlarge it to make a hypothetical moment smaller. The nine existing
private center slots are already typed and have their own lifetimes.
This investigation supplies pre-construction gates, not the admission above.

## 2. Concrete mechanism: a running decoder cache

Ignore ADDRESS labels for one moment and follow the literal nine-stage
scalar bank schedule. There are eight initial data banks, each with 111
port coordinates. Encode an initial bank by a distinct bit. The source bank
read by each successive local shear has mask

    1, 3, 6, 14, 26, 58, 106, 234, 170.

The XOR of all nine masks is zero. The first eight are independent.
Therefore, for any fixed linear port functional L, the ninth value L(x)
equals the XOR of its eight earlier values. This is an actual scalar
sharing identity. It follows from the bridge/shear schedule; it is not
assumed from the similarity of the local words.

The nine retained decoder source functionals have binary rank nine. The
checker extracts them from the actual PR589 A word. It also runs inverse
C and B and verifies that the reflected word has the same retained scalar
forms at its copy boundary. Applying those nine functionals to the bank
masks checks the running-sum identity on all 888 source coordinates.

Maintain nine initially zero accumulators per replica. After each of the
first eight stages, XOR its nine **source-only** retained totals into them.
At stage nine the accumulators contain the required nine source totals.
Running sums need nine rows, not 72 rows holding all earlier values.

Two obligations prevent calling this a supplier:

1. The actual retained total also contains helper dirt. Its dirty part has
   rank nine; with independent private stage inputs the XOR of the nine raw
   snapshots has rank nine, rather than vanishing. Raw snapshots cannot be
   reused as clean source totals. One proposed local interface extracts the
   nine initial dirty forms into nine owned temporary rows, cancels them
   from the copied totals, and clears the temporaries after their last use.
   At the last stage the original dirty response must be supplied or the
   target preconditioner rebuilt. These are real operations, not free
   erasure of borrowed inputs.
2. The scalar relation is at aligned port indices. The physical supplier
   uses port-dependent cover routes and stage frames. A proof that the
   accumulators can be updated/read in these common ADDRESS charts is still
   required. No commutation of L with those routes is asserted here.

The pricing gate can reject this candidate without solving either issue:
grant extraction and alignment at zero recursive cost. The most it then
saves is the final stage's nine rank-7 copies per replica:

    32 * 9 * 7 = 2016 global units = 7 per local invocation.

This is already far below 100. Removing other producer computations would
be a different proposal, with different retained values and obligations.

### Storage and nonrecursive bill

Every cache is live from stage zero through stage eight. Reconstructing the
actual untouched windows shows none contains all nine stages. The plan
therefore allocates 9*32=288 owned full rows, rather than clearing a borrowed
data row. Nine further dirty-form temporary rows can be reused sequentially
between local calls. Keeping the original nine center slots gives a proposed
physical stock of 28425+288+9=28722 rows, before the inherited evaluator and
recursive workspace. Productive W stays 28416.

Let U=V/W be a full role's volume including all spectators, and X(U), P(U),
Z(U) be charged aligned XOR, copy, and clear scans. Each dirty form can be
initialized by copying its first nonzero operand and XORing the others.
The sum d of the nine dirty-form support sizes is 471 (recomputed in the
receipt). A conservative temporary extraction bill over all local calls is

    288 * [9 P(U) + (d-9) X(U) + 9 Z(U)].

The running sums require 2304 X(U); cancelling dirt in those sums requires
another 2304 X(U). The existing raw center is left unchanged for the decoder:
XOR the raw center and then the dirty temporary into the accumulator. Cache
initialization and terminal clearing cost 576 Z(U). At the last stage,
copying the dirty temporary into the center replaces its old source-copy
scan; adding the cached source part requires another 288 X(U). This proposed
aligned interface adds 2592 P(U)+137952 X(U)+3168 Z(U), before new routing,
descriptor work and head returns. The ordinary decoder/scatter and existing
center-copy/clear scans are inherited; no saving in their scalar cost is
claimed. The extra 297U persistent/temporary stock is about 1.05% of
productive V and is not a child-volume discount.

Chart transport could require additional recursive children; its exact bill
is unresolved. The receipt's best-case invoice grants those costs zero and
only subtracts the 288 last-stage rank-7 copies. Since this favorable invoice
already fails and its mass credit is only 7, we do not implement the cache.
This is an upper bound on benefit and a lower bound on cost, not a complete
physical realization of the candidate.

## 3. Concrete hosting plan for vacated helper slots

A larger proposal is to share enough producer work to eliminate thirteen
complete helper paths per local invocation. Each starts at rank zero and
ends at rank eight, so the apparent local credit is 13*8=104. To avoid
presuming a scalar construction, grant a hypothetical replacement producer
for free; this is strictly more favorable than paying for one.

The checker independently expands the existing frozen selection into all
3951 (stage, helper) reservations per replica, or 126432 globally. A
reservation has idle-child index i, owner copy c, offset o, width eight,
stage s and helper h. The physical family is

    replica*888 + (2*pair(i)+side)*111 + port,
    with (side, port) = divmod(c,111).

The owner's pending idle-coordinate interval is [o,o+8). Window membership
proves that no local call or bridge touches this owner before its boundary.
Offsets are disjoint. Existing reservations are left in place.

For each removed helper, return its eight coordinates to its **original
owner's idle child**. Join those coordinates with that child's remaining
pending subspace and execute one child of the resulting rank. This uses a
fixed coordinate chart for a subspace of the original commuting pending
projector; there is no new family or volume denominator. Any actual chart
adapter has the retained fixed-routing cost. The largest original window is
42<64, so these completed idle children remain proper recursive calls.

This is a specific boundary plan with every reservation identified, rather
than a nominal +104 charge placed in an unspecified bucket. For helpers
0..12, the receipt lists all 117 reservations in one replica; other replicas
translate the family index by 888. The precise boundary histogram is
regenerated, including consolidation of returned holes with the old tail.

Every deleted role profile has mass eight. Every vacated reservation adds
eight to its idle child. Consequently

    local credit = 288*104 = 29952,
    owner boundary debit = 29952,
    net credit = 0.

The best-case target moment becomes 1.027203943736788 from 1.027739494928555.
There is a small benefit from less fragmentation, but no net rank reduction
and no target admission. The checker repeats the conservation check for all
439 possible single-helper withdrawals, and then grants **all** helpers free.
Even that latter profile, with actual data paths retained, fails at
1.009534083299681. No deleted helper producer is claimed to exist.

Source access, scalar cleanup and a replacement producer's own child work
cannot turn zero net rank credit into positive credit unless they change a
separate boundary obligation. They add nonnegative costs to these favorable
invoices. The inherited fallback is charged separately for every resulting
child, using the new child count, including completed idle children.

## 4. What the 100-unit arithmetic relaxation omitted

The previous rank-8 screen is valid as a lower bound, but it is not a plan
for consolidation. The 222 data roles each have total local growth seven.
Under role-preserving consolidation at the same endpoints their children
have rank at most seven. Grant all their mass at rank seven and every other
local unit at rank eight, including fractional calls. Keep the old remainder.
With s units removed from the non-data mass the relaxed profile is

    H = Hidle + 288*222 e7 + 288*(3512+63-s)/8 e8.

| s | Exact-interval moment at 1/99, displayed approximately |
|---:|---:|
| 99 | 1.000371348790695 |
| 100 | 1.000209625827279 |
| 101 | 1.000047902863863 |
| 102 | 0.9998861799004471 |

All changes are compared by two independent rational interval engines.
Fractional packing and free deletion are deliberately favorable assumptions.
This fence preserves the data endpoints and old remainder. It is not a
universal 102-unit lower bound for changed endpoints or changed hosting.

More fundamentally, under the retained boundary/cover accounting identity,

    D = mW - mass = 32*(8*111 - 9*C),

where C is the paid COPY mass per local invocation. Helpers and their
returned idle directions cancel from this identity. The original C is 63.
Even C=0 saves only 63 per invocation. Saving 100 at these endpoints would
require C=-37, an impossible nonnegative charge. A valid attempt at the
100-unit goal must alter this identity's **data/cover boundary term**, not
just its producer, scalar basis, number of helpers, or cache allocation.
The claim is scoped to this accounting identity, not arbitrary suppliers.

## 5. Do not turn that obstruction into a universal cost claim

Returning helper coordinates changes the remainder histogram. Thus a fixed
remainder screen cannot reject every redesigned hosting plan. As a control,
erase all helper computations, consolidate each data climb, and restore all
owner directions at their original idle boundaries. With C=63 its moment is
1.006919923493207 (fails). Additionally grant C=0 and its moment is
0.9967176251943854 (passes). Neither free construction is supplied.

This passing control removes only 63 rank units per invocation. It shows
that 100 units is a chosen construction goal, not a necessary condition for
every possible bit supplier reaching the rate. The full moment is always
the decisive rate test. A change to the requested goal should be explicit;
these relaxed profiles do not meet the current goal's construction gate.

## 6. Evidence, attribution, and next gate

The exact owner expander and backward window audit are written independently
of DaysSky's hosting_core, then compared to that source's output. The pinned
local word's complete Boolean replay and the previous positive-atanh price
engine are reused with hashes; the inherited Mercator engine independently
checks every target interval. No optimizer or network runs in replay.
These are finite schedule/price checks, not a fresh all-size compiler proof.

PR589 supplies the punctured tuned word (eumemic, with Claude assistance),
PR555 the frozen selection and v=111 pipeline, DreamingOfClouds the generalized
chain, and DaysSky/chafreaky the hosting lineage. The current scalar sharing
identity is an elementary consequence of that chain; no priority claim is
made. PR521 (applecrusher) and PR677 (commdata2338) were read for native
unipotent fusion and its restored boundaries. Their two-to-one local query
count does not furnish a drop-in replacement for these nested owner paths.
PR717's format-limit axioms independently emphasize boundary conservation;
this package's claims are proved and checked above rather than adopting its
solver-dependent results. Exact reviewed heads are in SOURCES.json.

The final queue refresh through #762 also read the descriptions of #757
(rseligm2) and #761 (VibeCodyH), which supply algebraic proofs of the fixed
P111 label-functional COPY floor 63 with careful source ordering, and #760
(ishan-1729), which audits R420's cleanup/restoration debt. Those independent
results are not imported or independently reverified here. Our extracted
forms use the actual PR589 word's ordering; the sharing identity, explicit
owner restoration and changed-remainder prices are separate from their
factorization and ghost-return theorems.

The next admissible nomination must specify which term replaces
32*(8*111-9*C), or supply a different fully priced profile and explicitly
revisit the mass-saving goal. It needs an actual operator with different
endpoint/cover obligations before another supplier build. No positive
nomination meeting that gate has been found here. The goal remains active.
