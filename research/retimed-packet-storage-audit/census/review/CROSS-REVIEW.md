# Independent review of the Gaussian owner census

## Decision and frozen boundary

**Accept the stated Gaussian slot-count theorem under its explicit valid-call
and mass-enclosure contracts. No blocking objection found.** The source argument
is uniform in legal column width, bundle width, epoch length, round count and
group count. Its justification is the allocation structure and calendar
invariants below; the finite checks corroborate those invariants.

Reviewed document: `work-storage/wave2-stock/OWNER-CENSUS.md`, SHA256
`c3a4466317732d44c7c3c7e57e1180106a71d2fb3083152cb54b8b7971b35bf0`.
The runtime is Ali Romman's PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd` in
`aliromman/integer-mult-bounds`. Canonical selected main is unchanged.

I independently opened the retained runtime through its hash-checked bootstrap,
authenticated all eleven modules in the author's binding manifest, compared
their actual resolved bytes with the author's copies, and separately checked
the installed exponent in `installations.py`. I reconstructed the graph and
layout from the retained journals. Their canonical hashes are respectively
`38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb` and
`0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee`.
`RESULT.json` records the twelve module digests. `READ-BOUNDARY.json` and
`FINAL-BOUNDARY.json` agree: the author's files were preserved.

This review accepts these two distinct implications:

1. For the actual integer calendar tables, a successful complete native-arena
   invocation with `B` public row fields satisfies
   `Arena.live ≤ B + 115058*C*`, where
   `C* = sum_e count[e]*(Q*delay[e]+1)`. This uses no analytic mass enclosure.
2. If the pinned transfer proof's **universal** bin-enclosure contract holds,
   the installed parameters imply `C* < 2*N^83` and consequently
   `Arena.high < 2*B`, with `B=N^92` and `N≥2^1024`.

The second implication retains the mass premise. This review does not certify
the rounding algorithm in `Measure.inverse_power`, a complete byte tariff,
private-control storage, or a global multiplication theorem.

## 1. The precise inclusive-lifetime argument

Write `m_e=count[e]`, `D_e=delay[e]`, `Q=len(paid)`, and `K=ticks`. Each context
is indexed by `(e,b,rep)`, with `0≤b<K` and `0≤rep<m_e`. The frame formula in
`Plan.events` is injective: the band index is below the band span and the replica
is below `max(count)`. Its open occurs at tick `b`; its paid ordinals occur at
`b+j*D_e` for `0≤j<Q`; its close occurs at `b+Q*D_e`.

The nonnegativity of the actual `m_e` does not require the analytic error
estimate. Internally, `Measure.inverse_power` keeps its integer lower value at
most its integer upper value: nonnegative multiplication, downward/upward
division and downward/upward integer square roots preserve that order. Its
lower value is nonincreasing in the positive argument, because the same
monotone integer recurrence is applied to the initial reciprocal floor.
Consequently `upper(e) ≥ lower(e) ≥ lower(e+2)`, so the mass upper endpoint and
its ceiling are nonnegative. This elementary order invariant is distinct from
the analytic claim that the enclosure is close to the intended integral.

For any logical tick `t`, the number of contexts whose **closed** lifetime
contains `t` is

\[
 I(t)=\sum_e m_e\,
 \max\{0,\min(K-1,t)-\max(0,t-QD_e)+1\}.
\]

Each integer interval has at most `Q*D_e+1` birth times, so `I(t)≤C*`. This
statement is valid at both epoch ends and requires no stationarity assumption.

The physical execution has more relevant cuts than dictionary membership:
`Plan.decode` can call `Machine.zero` while assembling the ports **before**
inserting the context into `live`. At close, it removes the context from `live`
**before** resuming the raw iterator, which can still materialize and transform
the final output bank, and before retiring private zero jobs. These operations
remain inside that context's closed lifetime. The proof therefore covers the
opening and closing transactions, not just the dictionary's stored entries.

The logical tick is an accounting label. A synchronous leaf call can perform
arbitrarily much work while a parent event is suspended; it cannot consume the
next parent event. Its new positive arena is separate, and the suspended
parent's owner count remains within the same `I(t)` cover. `decode` finishes a
close before requesting the next event. `Plan.run` finishes the whole decode
before starting the next round or group. Thus neither `K`, the number of rounds,
nor the number of groups adds a separate simultaneous multiplier.

The `+1` is correct for this inclusive cover. It is not asserted to be the
optimal bound obtainable after exploiting the within-tick order of all closes
and opens. For example, `Q=2,D=1,K=3,t=2` gives three closed lifetime intervals,
although a close-before-open implementation need not have all three live at
one microstep. Deleting the `+1` from this particular interval proof would fail.

## 2. Owner charges, stream replacement and private zeros

The quantity being bounded is the current arena's allocated slot reservations,
as counted by `Arena.live`. Neither dictionary entries nor retained Python
references are the unit. Every `Field.blank()` on these fields allocates from
the same arena. `ComplexRaw.scratch` by itself only registers an existing field.
The graph's private `held` bank must therefore be counted even though it is not
enumerated by the shared `fields` dictionary.

There is one important bookkeeping detail: a charge must follow the live owner
reservation, **not an immutable slot's allocation origin**. `Field.replace`
swaps streams and retires the old stream through the temporary object. A slot
created for an output copy can become the slot backing a public or borrowed
input after return. The surviving input owner retains its original charge and
the temporary reservation is discharged. No new slot is allocated during the
swap itself; its temporarily saved old stream is already covered by the
replacement reservation. Thus the charge is valid at the internal replacement
steps as well as at method boundaries. Parent aliases refer to the stable
`Field` object and remain suspended while a child changes its backing stream.

At each open, every productive binding either consumes one pending loan,
selects an existing public row, or creates a fresh zero field. There are exactly
105,216 bindings. Even if every binding requires a zero, at most 105,216 new
reservations are created. The not-yet-appended fresh zero is included in this
number, because at most one field is allocated per binding. Zero jobs remain
allocated through the final raw return and are then retired by `retire_zero`.
Their numerical values do not reduce their charge.

For external occurrences, a source block has length
`count*ticks*floor(rounds/period)`. Its base is disjoint from the other source
blocks. The offset within that block is
`(birth*count+replicaOffset)*cycles + cycle`, with `cycle<cycles`. This mixed-radix
encoding is injective among simultaneously eligible occurrences. Multiplying
by `group*source_width` keeps groups in separate index intervals; groups are
also run sequentially. The `index<width` test sends the padded last group to
fresh zero owners. The `cycle<rounds//period` test does the same for an incomplete
cycle, including a hypothetical zero-length complete-cycle block. Public row
reuse in later rounds does not overlap a live earlier decode.

## 3. The auxiliary maximum is 9,841

I reconstructed the finite source inventory and checked the key non-overwrite
conditions independently of the author's allocation mock:

| Source component | Verified inventory / bound |
|---|---:|
| Distinct root input owners per physical word | 9,840 |
| Distinct main roles in one graph | 400 |
| Helper roles in one graph | 891 |
| Complete graph input copies | 1,291 |
| Distinct scheduled graph nodes | 6,965 |
| Retained graph fields, including a node not yet inserted | 8,256 |
| Graph plus one transient replacement | 8,257 |
| Simultaneous final output copies plus one replacement | **9,841** |

The graph schedule has distinct node keys, all donors are already retained,
and all 1,291 output identifiers are distinct retained nodes. Output installation
consumes each returned field; the remaining 6,965 retained fields are retired.
Consequently no graph bank accumulates into the next graph invocation. The
first physical word fully returns before the second starts. Its productive
input owners remain allocated and are already covered by the all-input bound;
its auxiliary bank does not survive into the second word.

Outside graph execution, `LAMBDA` keeps one copied field and at most one
replacement. `QUERY` does the same. An idle cut adds an alias key. At final
return the `outs` list first materializes **all** 9,840 copies. Its first scalar
or chart transform can allocate one more replacement, giving the dominant
9,841 bound. It would be unsound to bound this caller by the graph maximum
alone or assume that output copies are produced and consumed one at a time.

For arbitrary legal column counts, `scale`, `scale_add`, `phase`, `swap` and
`rotate` create one output field and consume it before returning. The self-add
branch delegates to `scale`. `Columns.row`, `chart`, `align` and `unalign` compose
these calls serially. `Columns.repair` has one output field. Their growing loops
do not nest additional persistent fields in the current arena. Their scratch
spools, repair labels and the preceding ordinary service have separate byte
obligations, which are not claimed to be free by this census.

A paid singleton can invoke `one_axis`, with one additional parent-arena
replacement. A larger paid call may run several such singleton operations
serially before entering its child arena; this still needs only one at a time.
Reserving one for every live context is conservative because execution is
serial. The resulting per-context allowance is

\[
 105216+9841+1=115058<2^{17}.
\]

All current-arena allocations belong to public-row staging, one of these
context families, or the one active paid replacement. Final outgoing staging
retires rows and creates a spool, not new arena fields. Assigning these charges
to the closed-lifetime cover proves the first accepted inequality.

## 4. Loan custody and both half-column cuts

For an installed positive edge, `r≤4k/5` and the actual receiving bin obeys
`d≤4(e+2)/5<5e/6` because `e≥32768`. The delay level therefore decreases by at
least one. For this source the exact adapted count is

\[
 Q=2(281568)+1008=564144,
 \qquad D_0=2^{20}=1048576>Q.
\]

A child born at a parent issue time `t` closes by
`t+Q*D_child < t+D_parent`, strictly before the next parent issue, or before its
final close if this was its last issue. The induction is on decreasing delay
levels, not on an assumed physical runtime bound. Other inputs of that child
may arrive from different parent ordinals; each source parent enjoys the same
return-before-next-issue inequality.

Within a tick, decreasing band order opens the recipient after its parents
have posted their prefixes. The send ranges and receiving ranges are disjoint,
`pending.pop` consumes each incoming serial exactly once, and the source checks
that every pending loan was collected. Starting with disjoint external or
fresh owners, this establishes exclusive custody inductively. A parent can
retain aliases, but cannot resume its raw generator while any current loan is
outstanding.

The first 1,008 rank-one loans in the small-scale copy each produce **two**
consecutive adapted ordinals. There are 183,312 original rank-one cuts, so this
split supply is present. For positive even column width `w`, their index ranges
are `[0,w/2)` and `[w/2,w)`: they are disjoint, concatenate to the original job,
and retain the same owner. The physical iterator advances only after both
yields. Each half may independently have an interior child; each child's return
precedes the next adapted ordinal by the inequality above. Omitting the second
half would shorten the claimed context lifetime by `1008*D_e` and would use the
wrong `Q` in the cover.

## 5. Historical capacity and the retained analytic input

The free-first invariant is particularly simple. At every allocation boundary,

```text
high = live + len(free),
free slots and live slots are disjoint and cover [0,high).
```

A retirement decreases `live` and appends its slot to `free`. An allocation
reuses a free slot if possible; only when `free` is empty does it increment
`high`. In that case the previous live count was already `high`, so the new live
count sets the new historical maximum. Induction gives
`Arena.high = maximum historical Arena.live`. Stream replacement swaps occupied
slots and retires one; it does not invalidate the invariant. The child arena is
placed at the parent's historical suffix and cannot allocate in its suspended
parent. Thus the live-field bound applies to historical capacity, including
holes, without multiplying by the number of successive allocations.

The analytic dependency is exactly the pinned `TRANSFER.md` assertion that,
for every installed `N` and every band, the actual integer ceiling `m_e` exceeds
the ideal bin mass by less than two. Retaining this statement gives

\[
 \sum_e m_e
 < \frac{N^6}{tL^t}+2U
 \le \frac{N^6}{6}+2N
 <2N^6.
\]

Here the installed `t=1-2092819/2^29>3/4` and `L≥16` justify the factor six;
`U≤N` bounds the number of bins conservatively. No rounding-error conclusion
is inferred from this review's finite calculations.

The exact integer comparison `6^77>2^20*5^77` gives
`D_e≤(e/L)^77`. With `e<U≤N/(1024*A)`, `A=1224`, `L=2^15`, and `Q<2^20`,
the installed range has `Q*D_e+1<N^77`. Therefore `C*<2N^83` and

\[
 \mathrm{high}<B+2^{18}N^{83}<2B,
 \qquad B=N^{92},\quad N\ge2^{1024}.
\]

The final inequality has the explicit margin `N^9≥2^9216>2^18`.

The terminal geometric consequence `2W/(1-1/B)` is read as a bound for the
**native cohort arenas below an argument field of volume `W`**, along same-carrier
positive descent and using the previously established suffix-base lemma. Its
top argument/outer working field, entrance and output spools, ordinary-stage
roles and repair tags remain separately charged, as the author's stated scope
requires. This review does not absorb those objects into that expression.

## 6. Independent evidence and controls

I did **not** run `census_raw.py`, `census_primitives.py`, `census_schedule.py` or
the author's census driver as evidence for this review. `review_check.py` uses
the authenticated source syntax and a different event construction:

- It generates complete context lifetimes first and sorts their open/paid/close
  events, independently of `Plan.events`' tick scan. Across 32 bounded tables,
  all 6,270 source records agree. It checks 1,320 pre-insertion allocation phases
  and 1,320 post-removal close phases against the inclusive cover.
- An independent whole-owner custody interpreter checks 12 calendars and 107
  transfers, allowing both successive half cuts to use the same logical field.
  It covers strict return gaps and the equality boundary where close-first
  ordering is sufficient. Flattening the parent delay exposes premature resume
  at tick 1, paid ordinal 1. The mutation is deliberately outside the installed
  delay contract.
- The actual `Job.select` method preserves the same owner and partitions five
  noncanonical even-width axis lists into disjoint complete halves. The
  arbitrary-width conclusion is the interval identity, not extrapolation from
  those five lists.
- A separate external-index check has 148 valid visits and 122 zero occurrences,
  including incomplete cycles and the padded final group; all simultaneously
  valid external indices are distinct.
- A finite free-list state exploration checks 144 states through depth eight.
  An executed append-only mutation gives historical capacity two with peak live
  count one after `allocate, retire, allocate`, detecting the needed free-first
  hypothesis.
- Structural controls detect deleting the inclusive endpoint, overlooking the
  simultaneous output bank, and failing to retire a completed graph bank. For
  example, the last omission leaves 6,965 fields before the next graph's 8,256
  persistent fields, already exceeding the claimed 9,841 auxiliary allowance.

These are exact finite discrimination checks. The universal claims follow from
the preceding source arguments and declared premises. Small constructed
calendar tables test scheduling identities; they are not presented as
production-sized mass-certified plans.

## 7. Reproduction and next question

From `work-compiler/census-review`, run:

```bash
python3 -B review_check.py
```

The checker uses the existing exact local runtime and creates only temporary
restoration data beneath this review directory. Expected marker:
`PASS_INDEPENDENT_OWNER_CENSUS_REVIEW_CHECKS`. The complete result is in
`RESULT.json`; source boundaries are in `READ-BOUNDARY.json` and
`FINAL-BOUNDARY.json`. `COMMANDS.md` records the commands and scope. The source
bootstrap probe is retained in `BOOTSTRAP-READ.json`.

No correction to `OWNER-CENSUS.md` is required for the accepted scope. When
reusing the result, retain the explicit universal mass premise and the
distinction between current-arena slots and the separate byte/control roles.
The next independent task is the global ordinary-role and repair-tag byte
census, starting from the already identified immediate spool lifetimes. That
task needs the complete field geometry and lower-stage contracts; the present
slot bound alone does not settle it.

This is an independent model-assisted review of the author's argument and
checks, not independent human approval or formal kernel verification. Credit
Ali Romman and the retained source authors, the owner-census author, and
substantial OpenAI assistance for @CubeJerry. No new kappa or canonical
assumption removal is claimed.
