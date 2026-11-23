# A source-bound Gaussian owner census

## Result and exact scope

This audits the Gaussian simultaneous-owner term in PR #8042 at
`aliromman/integer-mult-bounds@dfd25d553a843a946ca0b94130a5ff8943e98fdd`.
The actual `ComplexRaw` and calendar callers support a much smaller local
field bound than the published `2^67` allowance. For one active calendar
context, **115,058 complete owned fields suffice**, including all private
zero inputs, raw auxiliary fields, simultaneous return copies and one paid
leaf replacement. This is below `2^17`.

Let `m[e]=Plan.count[e]`, `D[e]=Plan.delay[e]`, and `Q=len(Plan.paid)`. Define

\[
 C_* = \sum_e m[e](QD[e]+1).
\]

During a successful complete positive invocation with `B` public row fields,
the native arena's live field count is at most

\[
 B+115058 C_* < B+2^{17}C_* . \tag{1}
\]

This is a universal source-specific allocation bound, not an inference from
a finite peak. Under the existing transfer proof's upper enclosure for the
bin masses, `sum m[e] < 2N^6`; the actual delay parameters give
`QD[e]+1 < N^77`. Thus `C_* < 2N^83`, and

\[
 \#\text{owned fields}<B+2^{18}N^{83}<2B,
 \qquad B=N^{92},\quad N\ge2^{1024}. \tag{2}
\]

Equation (1) does not need the analytic mass enclosure: it uses the actual
integer count and delay tables. Equation (2) reuses that existing enclosure
result rather than re-auditing its numerical rounding. The point under audit
here is the live-owner and caller binding. Private control bits, tag lengths,
ordinary tape-role byte extents and outer numerical working fields still
have their separate resource obligations. No new global storage constant
or kappa is claimed.

## What counts as an owner

The unit is an actual `spool.Field` allocated from the current positive
`Arena`. `Field.blank()` calls that same arena's `field()`; `Field.replace`
requires equal shape and equal arena, swaps the two streams and retires the
old stream through the temporary field. Each live `Field` therefore owns
one slot. Retirement clears the complete slot before freeing it. Allocated
zeroes count identically to arbitrary data.

Dictionary keys are not this unit. `ComplexRaw.scratch(field)` adds a new
owner key for an existing field. At an idle cut this is an alias of an input
field and allocates no slot. At a query cut the preceding `copy()` creates
one new slot. Conversely, most fields in `ComplexRaw.graph.held` are not in
the public `fields` dictionary. Counting that dictionary alone would miss
them. The proof counts field objects and actual allocation operations.

The following source functions are covered: `Plan.events/decode/run`,
`retimed_supplier.Raw.native/Positive._run`, `ComplexRaw.raw/graph/fresh/retire`,
the `spool.Field` allocation/return methods, and `compact_columns.Columns`.
The files in `sources/` are stable resolved copies of the hash-checked
bootstrap runtime. Their digests are preserved in the binding manifest.

## Per-context field bound

### 1. Transport zeroes: at most 105,216

`Plan.decode` handles each productive binding once at an open record.
An incoming loan uses `pending.pop`, and a valid external occurrence selects
an already allocated row. Every other binding calls `Machine.zero`, which
reaches `ComplexRaw.fresh`: one `blank()`, one `clear()`, one registered job.
Those zero jobs are retained in the context's `zeros` list and retired after
the raw iterator closes. The combined source has exactly 105,216 productive
bindings, so this many new zero fields per context is a valid worst case.
An incomplete last group and an incomplete periodic cycle are included;
neither receives free storage because its numerical value is zero.

### 2. Physical raw auxiliaries: at most 9,841

The two physical words in `Raw.native` execute sequentially at column scales
1 and 8. Both sets of productive inputs stay allocated, but the first raw
generator has fully returned before the second begins. The physical source
has 52,608 productive inputs per copy, of which 9,840 are root fields and
42,768 are helper fields. The root dictionary aliases productive fields;
it does not allocate another root bank.

The exact graph has 1,291 public inputs and 6,965 scheduled nodes. Every
graph invocation creates one copy of each public input, then at most one
persistent field per scheduled node. Hence its retained `held` fields plus
the current not-yet-inserted node total at most

\[
1291+6965=8256.
\]

Each scalar, phase, row, swap or repair operation uses at most one additional
replacement field, returning it before the next operation. Therefore graph
processing needs at most 8,257 auxiliary fields. The final graph output loop
consumes its returned fields with `dest.replace(value)`. Its remaining held
fields are explicitly retired; no graph's auxiliary bank survives into the
next native graph invocation.

Outside graph calls, `LAMBDA` retains one shifted copy and at most one
replacement; `QUERY` retains one copied borrowed field and at most one
replacement on return; idle yields add an alias key. Their bound is two
auxiliary fields. At the end of the complete raw caller, the `outs` list
materializes all 9,840 root return copies before any are installed. A return
transform can create one replacement while those copies remain live. Thus
the dominating bound is

\[
P=\max(8257,2,9840+1)=9841. \tag{3}
\]

This last simultaneous list is why a proof counting only the current graph
or one output at a time would be too small.

### 3. Source binding of the one-replacement contract

`Field.scale`, `scale_add`, `phase`, `swap` and `rotate` allocate one blank
output and consume it with `replace`. `copy` creates one new persistent
field. The `scale_add(self,self)` branch calls `scale`, preserving the bound.
`Columns.row` executes its swaps/rotations serially, then `repair`, then
`one`; `repair` has one blank output and replaces the input after its spool
work completes. `ComplexRaw.chart`, `align` and `unalign` invoke these
operations serially and retain only coordinate descriptors between them.
Their number of columns changes their work, not their simultaneous field
count. This proves the contract for every legal column/bundle width.

Snapshots are separate physical spools, not free data. In the immediate
Gaussian operations, `scale_add` can retain two input snapshots; `rotate`
retains a snapshot and a first-part spool; `repair` retains four spools.
`swap` retains its one input snapshot across the earlier ordinary service.
Those immediate roles are serial, and the preceding stage has its own
allocation. This identifies the immediate roles; it does not silently treat
repair tags as having zero byte length. The existing local adapter/tag bound
remains separate from the arena field count.

A paid singleton in `Positive._run` may run `one_axis`, retaining one new
replacement field in its parent arena. Reserve one more field for the
currently executing paid leaf. If it instead enters a recursive positive
cohort, the child's arena is charged separately. Combining this with (3),

\[
Z+P+1=105216+9841+1=115058<2^{17}. \tag{4}
\]

This allowance is per live calendar context. It deliberately overcounts the
single globally active leaf's extra field rather than excluding a suspended
raw parent. Before the first context or after the last context, input/output
staging does not create additional arena fields beyond the public rows;
its scratch files retain their separate adapter charge.

## Calendar count and custody

Each band `e`, birth `b` and replica `rep` identifies one raw context. The
source's frame-number formula is injective because `rep < max(count)`.
An open record occurs at tick `b`; its final close record occurs at
`b+QD[e]`. Its input zeroes can begin allocation before insertion into
`decode.live`. Its final output copies can exist after removal from that
dictionary. Consequently count the **closed lifetime interval** from birth
through completion of the close operation, not merely membership of `live`.
At any tick, at most `QD[e]+1` integer birth times can lie in this interval.
Multiplying by `m[e]` and summing proves the exact `C_*` cover.

Every close is completed before the next event is consumed. Group-rounds
are also sequential: `Plan.run` invokes a complete `decode` before starting
the next round or group. Successful raw return and zero retirement dispose
of the context's auxiliary fields. Therefore neither the epoch duration
`K`, the round count `R`, nor the number of copied groups multiplies the
simultaneous count. The `+1` also covers contexts currently opening or
closing, including the last padded group.

For a genuine transport edge, the installed positive grades satisfy
`r <= 4k/5`. At `e >= L=32768`, the receiving bin satisfies
`d <= 4(e+2)/5 < 5e/6`. Hence its delay is at most `D[e]/D0`, with
`D0=2^20 > Q=564144`. A child born at the parent's paid tick closes before
the parent's next paid tick. The decreasing-bin event order receives its
loan at that same tick; the decoder consumes it once with `pending.pop`.
Induction on the decreasing delay levels gives exclusive custody of each
physical field until return. External occurrence indices are disjoint
within an active decode, and a later round starts after all contexts close.
Missing inputs allocate distinct zero owners.

The parent generator may retain aliases, but cannot resume its next raw
operation before the child returns. The first 1,008 split loans are no
exception: `Raw.native` yields two disjoint halves of the same original job,
on consecutive adapted paid ordinals, and advances the physical iterator
only after both. Neither half creates another field. Both are covered by
the same delay/custody argument, including an interior child on either half.

Equation (1) follows by charging each context its zero inputs and its
instantaneous raw auxiliary bound (4), while reserving all `B` public rows.
The proof concerns physical slots, so duplicate aliases do not manufacture
new fields and hidden `held` fields do not disappear from the charge.

## Production exponent bound

The delay comparison is exact: `6^77 > 2^20 * 5^77`. If
`level(e)=floor(log_(6/5)(e/L))`, then
`D[e]=(2^20)^level(e) <= (e/L)^77`. Since
`e < U <= N/(1024 A)` and `A=1224`,

\[
QD[e]+1 < 2^{20}(N/2^{25})^{77}+1 < N^{77}
\]

throughout the installed range. This uses the actual adapted count `Q`,
which includes both halves, rather than the original raw count.

For birth counts, reuse the transfer proof's certified inequality that each
`count[e]` exceeds the ideal bin mass by less than two. With `t>3/4` and
`L>=16`, the sum of ideal masses is at most `N^6/(tL^t) <= N^6/6`.
There are fewer than `U` bins, and `U<=N`; thus the total is at most
`N^6/6+2N < 2N^6` for `N>=2`. This is a simple consequence of the stated
enclosure contract, not a fresh audit of `Measure.inverse_power`.

Finally `N^9 >= 2^9216 > 2^18`, giving (2). By free-first allocation,
`Arena.high` is the maximum live count reached in that arena, so the same
bound applies to historical slot capacity, including retired holes. Each
field in a child cohort has its actual `W/B` volume. Suspended positive
parents are charged in their own arena; a paid descendant's argument is one
such complete field. Combining this census with the previous suffix-base
lemma gives the geometric arena charge `2W/(1-1/B)` along same-carrier
positive descent, with entrance/output spools kept separate.

## Checks and controls

The source-derived constant reader reconstructs and hashes the exact graph
and layout. `census_raw.py` runs the actual `ComplexRaw.raw/graph` and
`Raw.native` control code through all 564,144 adapted cuts, including both
copies and all 1,008 half-column pairs. It replaces only payload transforms
by the proved one-replacement-field envelope. It observes 9,841 maximum
auxiliary fields, 7,706 at a yielded cut, and exactly 105,216 returned inputs.
It records 35,552,352 modeled field allocations, all with explicit retirement.
These counts are ownership evidence, not a new data-movement price.

`census_primitives.py` separately executes the real field methods on small
physical tapes. Eight methods obey their one-extra-field return contract;
zero data receive the same allocation as arbitrary data. `census_schedule.py`
uses the actual `Plan.events/decode` at small parameters with explicit
custody tokens. It includes interior loans, 535 simultaneously live contexts,
the first and last group, and a final incomplete periodic cycle. Its four
cases restore all external owners; the peak extra counts are 668, 709, 866
and 896, all below the exact lifetime cover.

The controls omit actual graph retirement, omit decoder zero retirement,
omit physical replacement retirement, and flatten the delay table after
construction. They respectively violate the per-context field cap, leave
zero owners after epoch return, retain a physical replacement slot, and
resume a parent while a child still holds its field. The last mutation is
deliberately inadmissible; it establishes that the custody check is sensitive
to the causal premise.

The all-depth statements are proved by the source structure above; these
finite checks do not execute a production-sized calendar. The proof closes
the specific Gaussian owner-census obligation under the existing mass
enclosure and valid-call contracts. It leaves the global ordinary/local
adapter byte census and private control bounds available for separate
review. Credits remain with Ali Romman and the retained source authors;
this is OpenAI-assisted work for @CubeJerry, not independent human or
formal-kernel acceptance.
