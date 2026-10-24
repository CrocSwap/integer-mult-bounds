# Numerical capacity before a whole first-node return

For the original PR2697 Node/Driver at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, every pending numerical allocation,
from Node construction through successful Node.run cleanup, fits the same
componentwise extra capacities37672 residues and41 indices that PR2845 proved
only for Consumer.apply. The new result is the larger caller domain: it removes
the arbitrary declared-capacity premise from the numerical part of PR5165's
whole-Node source backing grant. It neither improves those constants nor imports
a successful run as a premise for excluding inventory exhaustion.

## Domain and exact boundary

Use the authenticated original50-file source cohort, dimension64,
64<=parent_size<128, selected ranks1..42, admitted odd prime-power arithmetic,
canonical encoded Programs/fields/counts, valid word margins and fixed selected
source tables. The incoming Context/Ring, Program, parent_size and depth are
already initialized borrowed inputs; Context construction and compiling a
catalogue are outside this Node-entry boundary. All live external residents
(including suspended callers) count in L_R,L_I. K_R,K_I count all allocated
slots, including erased free slots. Two distinct canonical arenas partition K
into live and duplicate-free erased available slots. Word arrays do not resize;
templates and incoming heads meet the inherited source contracts.

The statement concerns every finite prefix before a first noncapacity error.
Noncapacity semantic validity, termination, admitted coefficient/leaf contracts,
and actual source membership remain premises. It does not assert that a finite
fixture proves these. Numerical-neutral observers/specification lookups/factories
and an exclusive nonconcurrent runtime are required. Foreign Word construction,
malicious mutation and host allocation failure are excluded. Native fixed-q
rational chart compilation is not an Arena Word computation and is not priced
as physical arithmetic by this theorem.

At an Arena.zero call, demand is live+1 before its guard or allocation. Ordinary
states between requests are included. The conclusion is

    demand_R <= L_R+37672,   demand_I <= L_I+41.

Hence sufficient capacities are C_j>=max(K_j,L_j+B_j), B=(37672,41). These
bounds need not be sharp or attained together. The backing consequence is

    (max(K_R,L_R+37672)+1)(b_R+2)
      +(max(K_I,L_I+41)+1)(b_I+2).

LEFT, RIGHT, erased slots and both templates are included. Substitute these
numerical terms for the declared-capacity terms of PR5165; its independent
payload/count/directory/program/continuation/external-resident hypotheses and
terms stay unchanged. This does not turn that source-array grant into a physical
bank or recursive-parent implementation.

## Prefix calculus and credited components

A source effect (P,N) bounds all pending requests by P above its input resident
set and retains N fresh Words on normal return. Sequential composition uses
max(P1,N1+P2); loop iterations that restore their baseline do not accumulate
scratch. A partial fixed-size list/matrix has at most its intended cardinality.
The final incomplete component is charged by its prefix contract, not a future
successful return. Every old operand remains charged until the literal free.

PR2835 proves prefix effects for unchanged scalar arithmetic: unsigned division4,
unsigned addition2, subtraction1, modular add/subtract2, negate3, modular
multiply/literal4, inverse10. It also proves Callback construction(12R,15I),
retained(2R,6I), and Callback.weight(5m²+10R,10I), returning one residue.
Serialized continuations do not retain numerical matrices across evaluator
iterations. PR2845 proves the complete Consumer.apply rectangles(37672R,34I)
and(20494R,41I), restoring numerical entry state on normal return. We retain
these source-derived prefix results and their contracts; they are not newly
proved or inferred from measurements here. Every imported module is matched to
the actual Node cohort by bytes. All50 original files are authenticated.

## Original incoming coefficients

IncomingWeights.coefficient constructs a leaf Callback on the frozen original
prefix, checks final width/depth, and calls frame.weight. Its construction fits
(12,15). The retained callback(2,6) plus weight's prefix gives
(5m²+12,16). If negative_inverse is requested, the value stays resident during
ten inverse scratch and the returned inverse stays resident during negate;
including the callback this is at most13 residues, below5m²+12. Normal frame
close releases its two residues/six indices, leaving exactly one result.
This is a direct source composition, not substitution of Consumer's different
adapter entry or a claim that a synthetic coefficient is the actual callback.

## Constructors, preflight and fresh rows

Node.__init__ retains dimension and one while raw.divmod requests four indices:
(0,6), returning no new Word. SelectedNode constructs only numerical-neutral
source/compiler objects before this call. Consumer.__init__ only checks labels;
IncomingWeights.__init__ binds a fixed identity class without Arena allocation.

Node.run's five Count copies, positivity tests and stock_multiple division use
separate Tape cardinalities. read_prefix materializes no Word. Preflight retains
one zero index while the incoming callback runs: (5m²+12,17). Its returned value
and zero are freed before later work. fresh_rows.quotient calls radix_power
sequentially: divisor/power plus four division temporaries gives6 residues.
It retains no numerical result. Product/count operations are numerical-neutral;
times_small(parent_size,2) peaks at2 indices and leaves total while
multiply_atom_power uses a copied count Tape and at most6 residues. total is
freed before peel. No numerical Word survives these phases above Node entry.

## Whole original-offset remainder peel

peel.run retains columns1, Geometry's one/two/cutoff3 and Layout's
core/extra/total3: seven indices. Layout construction transiently has four roles
rather than its retained three, so its prefix is eight total. Layout's Count
leading contributes no Word. No residue is retained in this persistent baseline.

peel.events initially creates coordinate, total and last; total is freed before
the loop. During one remainder coordinate it retains coordinate/last/right,
then a/b and (for ADD) a copied request coordinate. With the persistent seven,
ADD suspension therefore owns13 indices. primitive transfers aliases, not
copies, and frees a/b/request.coordinate before the next stage. Stage7 frees a
before yielding sign. The eight stages and all remainder coordinates thus do
not accumulate numerical state. Construction, increment and subtraction
interiors fit within13; the first incomplete request is included.

Layout.extents adds at most four indices while radix work adds at most6 residues.
It releases its physical positions and after/distance counters before invoking
a coefficient. Layout.fibre has no numerical index and uses the same six-residue
radix prefix. Consequently an actual ADD callback starts at at most13 indices
above Node entry; the original incoming coefficient gives at most
(5m²+12R,29I). The optional negative inverse was already included. After it
returns, add_pass retains coefficient/x and multiplication scratch within6
residues, sequential rather than added to the large callback peak. Non-ADD
swap/sign cardinality/radix interiors have at most6 residues and no additional
persistent index. The complete peel rectangle is therefore(20492,29).
The use of embedded=False preserves original incoming offsets; the capacity
argument never replaces this peel by a residual on a smaller fibre.

## Complete route matrix and cursor lifetime

Write d=64. Matrices.constants has at most d² distinct rational palette entries.
While adding one palette entry it may retain numerator/denominator and inverse
scratch10, or numerator/denominator/inverse plus multiplication scratch4.
Thus its prefix is bounded by d²+12; while copying the output, the entire palette
and up to d² output Words coexist. The conservative2d²+16 covers both, including
the next requested slot. It returns d² chart entries. Denominator inverses are
actual modular routines, not free host constants.

route_cube next constructs its d² Odometer digits, while retaining the chart.
For high_key, raw_header retains qword, up to d² low palette entries and up to
d² output entries. A multiply needs4 scratch; add retains its term and needs2.
Together with chart and Odometer, this fits4d²+6. Once raw_header returns, its
palette/qword are freed. Matrix multiplication retains raw and chart/high while
constructing common plus4 scratch:4d²+4. It frees raw before dividing common into
keys. At that cut chart/high/common and up to d² keys coexist, with divisor,
low, difference and four division temporaries: at most4d²+7. The old remainder,
low and difference are freed before advancing to the next cell. Full or partial
key matrices are counted, including zero entries. Returned keys are freed before
the next high record. These are prefix bounds on allocation loops, not assumptions
that a full high cube can first be executed.

Stable partition retains chart and the finished-but-not-yet-closed Odometer:
2d² numerical residents. Buckets/keys/counts are Tape objects. Its cursor is one
residue; shift_add_bit constructs a replacement before freeing the old cursor,
still below2d²+4. During key removal the previous Odometer has already been closed
before its replacement; chart plus new high plus one decoded actual digit fits
2d²+1. Route_packet's outer prefix and payload work add no Word. The whole route
prefix is conservatively(4d²+16,0)=(16400,0), returns no numerical Word, and
therefore does not accumulate across old prefixes or the native inverse return.
Fixed compile_owner/inverse_chart operations use native fixed source data only;
their cost is not silently identified with zero physical work.

## Other Driver and Node phases; complete join

selection.gather/scatter calls high_power twice sequentially, each with residue
prefix6; its remaining count/bit loops are numerical-neutral. Fresh split/merge,
clone_packet, xor_packet, xor_family and bridge/exchange retain no numerical Word.
The finite-control LocalState and slot/owner maps hold no Word. Thus while family
and staged payloads coexist, every actual Consumer entry has exactly the Node
numerical resident baseline L: no route chart or Odometer survives the completed
route. MOVE/COPY/idle compose with PR2845 directly, including all inherited child
and callback allocation prefixes. No factor661 or number of rows/calls multiplies
numerical scratch; each completed local operation restores it. Normal final
cleanup only frees/clears/rewinds. The complete phase table is:

| Phase | Extra residue demand | Extra index demand |
| --- | ---: | ---: |
| Node construction |0|6|
| preflight incoming coefficient |20492|17|
| quotient/fibre preparation |6|2|
| original-offset peel |20492|29|
| gather/scatter |6|0|
| complete forward/backward route |16400|0|
| Consumer adapter rectangle |37672|34|
| Consumer child rectangle |20494|41|
| split/clone/XOR/bridge/exchange/merge/cleanup |0|0|

Every row is measured from the same Node-entry numerical baseline; all normal
phase exits restore it. The componentwise maximum is37672/41. This table covers
constructor and partial-body allocations, all packet tags and generated
coefficient branches through the cited Consumer contract. It does not claim a
new source-array bound for uncounted Tape categories.

## First inventory failure and warm backing

Assume a first inventory rejection. Earlier completed arena actions preserve
the canonical partition. If an available slot exists, zero reuses it and does
not reject for capacity. Otherwise all currently allocated K_t are live, and
the pending-prefix theorem gives K_t+1<=L+B<=C, contradicting rejection K_t>=C.
The entry feasibility condition K<=C matters independently. Existing erased
slots cannot be discarded by substituting L for K. Each arena's retained backing
is its own historical maximum, so maxima must be taken separately; a maximum of
simultaneous weighted live content would not imply the displayed backing bound.
Normal successful restoration follows the same phase induction. Rejection
cleanup is not needed by this argument and is not claimed: The separately published R11 task08
setup-only transaction does not extend through the entire Node.

## Evidence and limits

Finite controls observe actual Arena.zero before its guard. Actual n65 peel
runs all eight original-offset event constructors and real IncomingWeights,
including the negative inverse, with the enormous payload seam explicitly cut.
An actual selected call32 owner chart,64x64 matrices, modulus9 and high radix3
exercise chart/palette/high-key allocation; one high record is executed, not the
3^4096 high cube. Reduced-dimension complete local/route controls are labelled
separately. Real short-capacity rejection, borrowed-resident shifts and warm
backing discriminate the capacity statement. Finite tests corroborate the
written quantified source proof; no full GL64 node or historical suite is run.

## Open next questions

1. Supply noncapacity semantic/termination admission for the exact selected
   caller without replacing it by a reduced model.
2. Prove whole-Node rejecting-path ownership beyond the setup-only transaction.
3. Bind the complete source-array grant to fixed physical banks and paid movement,
   then handle the changed recursive Consumer and suspended parents separately.
