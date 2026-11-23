# Binary raw-context owner census at the installed source

Prepared for Jerry with substantial OpenAI Codex assistance. Apache-2.0.
Source construction and interpreters: Ali Romman's PR #8042, exact head
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`; inherited binary graph and
36-call caller retain their source attribution. This is an owner-count proof,
not a new mass enclosure, byte bound, delay exponent proof or supplier admission.

## Claim and domain

Fix one successful invocation of the retained
`binary_receiver.Receiver.compiled`, with its `OwnerBanks` initially empty,
`B = self.owners` external fields, and a production `transport.Plan` obtained
from `raw_binary_stage.binary_recipe(height).open()`. Let

\[
q=104904,\qquad
C_* = \sum_{e\in\mathrm{bands}}\mathrm{count}[e]
                  (q\,\mathrm{delay}[e]+1).
\]

At every execution microstep, including initialization, opening and closing a
raw context, and return of the external fields,

\[
\boxed{\;|\mathrm{banks.live}|\le B+22339 C_*,\qquad
\mathrm{banks.capacity}\le B+22339 C_* .\;}
\tag{1}
\]

The same assertion holds for any successfully constructed Plan having this
fixed raw word and the source's descending-power delay and loan contracts.
`count[e]` need only be the actual finite nonnegative replica counts; no estimate
on the accuracy or asymptotic size of `Measure.mass` is used in (1).

Consequently `22339 C_* <= B` is a sufficient, separately checkable condition
for the binary `beta = 2` owner-capacity premise. This package does not certify
that inequality at every production height. It leaves the numerical count
enclosure and the global delay-size estimate as separate inputs.

## The literal template is independent of production rank

`binary_receiver.Receiver.__init__` selects `binary_recipe(height)` at height at
least 3000 and requires a dyadic dimension when a recipe is selected. Its
`compiled` method constructs `StrongBinarySource(banks)`, and its nested
`Machine.native` calls `binary_word().native(ports, columns, raw)`.

`raw_binary_stage.BinaryWord.__init__` constructs the labelled lists by the
literal call `binary_ports(graph(), caller())`. Both arguments are functions
from `strong_binary.py`: `graph()` authenticates the fixed compressed graph
with SHA256 `74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`,
and `caller()` authenticates the fixed caller with SHA256
`757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b`.
Neither function has a rank argument. `binary_recipe(height)` changes the
Recipe geometry, not these lists. `BinaryWord.native` zips exactly the fixed
target list, calls `physical.raw`, checks each fixed paid label and its
`port.rank * columns` extent, and checks that the raw generator then ends.

`StrongBinarySource.raw` constructs `ActiveCatalogue(dimension, columns)`.
Its initializer assigns those same `graph()` and `caller()` values. Dimension
and columns affect frame geometry and validity, not the graph instructions,
root event list, register count, or number of calls. In particular the
certified powered-word helper in the same module is not called along this
raw-stage dispatch path. There is no rank-dependent tensor multiplicity hidden
in the constants below: replica multiplicities belong to `count[e]`, the number
of simultaneous contexts to the delay schedule, and field byte size to the
separate field-volume accounting.

The exact decoded literals have the following census, also checked directly
against their authenticated compressed payloads:

| Fixed item | Count |
| --- | ---: |
| Root ports | 111 |
| Root diagonal entries | 38 |
| Root LOCAL calls | 36 |
| Root QUERY events | 4 |
| Root IDLE_ONE events | 32 |
| Inner public registers | 630 |
| Inner instructions | 39,600 |
| Inner MOVE instructions | 2,803 |
| Inner INIT instructions | 3,433 |
| Inner CLEAR instructions | 3,433 |
| Maximum simultaneously live inner private registers | 3,433 |

Each LOCAL has `630 - 2*111 = 408` helper targets. Hence the exact fixed
target count and paid-label count are

\[
P=38\cdot111+36\cdot408=18906,
\qquad q=36\cdot2803+(4+32)\cdot111=104904.
\tag{2}
\]

The inner census scans the **entire** fixed instruction list. It begins with
registers `0,...,629`; INIT adds a previously absent register, every opcode's
referenced registers must be live, and CLEAR removes a present private
register. The final register set is exactly the initial public set. The peak
private count is 3,433. This finite literal verification supports a universal
parameter claim because every raw context at every rank executes this same
fixed instruction list and caller; it is not an extrapolation from low rank.

## Owners charged to one context

Charge each allocated owner to the context whose decoder or interpreter first
allocated it. Existing external rows are charged to the initial `B` fields.
A selected borrowed job aliases its existing owner and retains that owner's
origin charge; selecting axes does not allocate a bank owner.

When `Plan.decode` opens a context, each of its P target bindings is supplied by
one external row, one pending loan, or one fresh `machine.zero`. Thus at most P
fresh input owners are charged to the context. They are retained until close.
This includes the opening interval before `live[ident]` is inserted.

The raw interpreter adds at most 3,433 owners to these input owners. During one
LOCAL event it calls `yield from self.inner(...)`. `BinarySource.inner` creates
an owner precisely on INIT and retires it precisely on CLEAR. Its MOVE jobs
alias existing register owners, while ADD, SWAP and routes only modify existing
owners. The literal register trace therefore proves the 3,433 bound throughout
all suspended paid cuts and every instruction between them. At return it has
no private register left.

The only outer raw event allocating an owner is QUERY. It clones one right
input, yields that borrowed owner, updates the left input and retires the clone
before the next port. There is at most one such clone. QUERY and LOCAL are
distinct serial branches of the root event loop: the inner call has fully
returned before a QUERY starts, and the clone has been retired before another
event starts. Their extra owners therefore have maximum `max(3433,1)`, rather
than a sum. Initial and final matcher routes allocate work tapes, not bank
owners. The same distinction applies to the clone's copying work tape.

Every context is consequently charged at most

\[
K=P+\max(3433,1)=22339
\tag{3}
\]

live owners. Closing first pops the generator from the decoder's live dictionary,
then resumes it to its actual return and retires its input zeros. Equation (3)
continues to include those owners until the close operation is physically
complete; dictionary removal is not treated as retirement.

## Loan custody and inclusive context lifetimes

A context with band e, birth b and replica index has q paid resumes at
`b+j*delay[e]`, for `0 <= j < q`, and a closing resume at `b+q*delay[e]`.
Give it the inclusive interval

\[
[b,b+q\,\mathrm{delay}[e]].
\tag{4}
\]

This interval covers all opening allocations, every suspended private owner and
the entire closing cleanup. At each integer tick, there are at most
`count[e]*(q*delay[e]+1)` such contexts in band e, since births are integer and
there are only `count[e]` replicas per birth. Restricting births to
`0 <= b < ticks` can only decrease that bound. Summing proves at most C_* live
or currently opening/closing origin contexts, with no dependence on epoch
length, number of rounds or groups.

An owner lent by a context cannot survive past the end of its origin's interval.
The Plan constructor accepts an allocated edge only when the child's delay is
strictly smaller than the parent's. Delays are integer powers of a common base
`D0 >= q`. Thus `q*D_child <= D_parent`. For the actual fixed binary q,
`Recipe.open` chooses `D0 = 2**19 = 524288 > 104904`.

A loan issued at a parent's paid tick s is collected by the child born at s:
`events()` visits bands in descending order, and strictly smaller delay implies
a smaller band. The child closes at `s+q*D_child`, at or before the parent's next
resume `s+D_parent`. The source emits closing rows before opening/paid rows at
a tick; if both are closes in the equality case, ascending-band close order
also puts the child first. Thus the owner is returned before the parent can
retire or reuse it, including a loan issued at the parent's last paid cut.
Any further descending loan is handled by the same argument inductively.
The pending dictionary stores `job.select(...)`, not a fresh owner.

Local leaf execution can recursively use other bank instances and work tapes;
it does not call zero/clone on this bank. This theorem counts the one compiler
bank. The separate ancestor-composition theorem is needed to charge other
simultaneously retained bank instances and their field volumes.

Equations (3) and (4), plus the B external owners retained during Plan.run,
prove the live-owner part of (1). Groups and rounds are serial; `decode` requires
all contexts and pending loans to have returned before another group/round.

## High-water capacity and entry history

`OwnerBanks` inherits `Banks.zero`, `retire` and `clone` unchanged. Its initializer
sets `capacity=0`, `vacant=[]`, and `live=set()`. A retirement erases and adds
exactly one index to `vacant`. Allocation uses a vacant index whenever one
exists and increases `capacity` only if no vacant index exists. The indices
below capacity partition into live and vacant indices at completed allocator
calls. At such boundaries, an increase of capacity equals the completed live
count, so capacity is the historical maximum completed live count since this
fresh initialization. Inside `zero`, the capacity increment precedes
`live.add`; inside `retire`, `live.remove` precedes the vacant-list append. At
these intermediate statements there is one owner allocation or retirement in
flight. Its prospective or departing owner is already included in the current
context's bound (or the initial B external fields). The same capacity bound
therefore holds throughout the call, without asserting a live/vacant partition
at each individual Python statement. This proves the second inequality in (1).
Returning external fields only reduces live count and does not increase
capacity.

This is a fresh owner allocator, not a claim that an old physical backing tape
shrinks when its contents are erased. If a fixed physical head starts with
reserved byte capacity K0 and this invocation has owner-field volume V, its
required reserve is `max(K0, V*(B+22339*C_*))`. Across reused calls use the
per-role maximum over the complete reservation history, as in the accompanying
`ENTRY-HISTORY.md` applicability note. No current-call volume may erase an
earlier, larger physical reservation from the accounting.

## Evidence, separation and open question

`check.py` authenticates the retained files, scans the complete literal register
trace and fixed labelled lists, executes source-extracted raw/native methods
with an ownership-only frame oracle, and checks bounded source-calendar loan
traces and failure controls. Geometry and data transformations in that oracle
are deliberately abstracted: it validates allocation/lifetime structure and
labels, not numerical field correctness. Production calendars are not executed.

The companion ordinary composition/local-byte proofs require beta=2; (1)
reduces that binary premise to the precise count/delay inequality
`22339*sum(count[e]*(104904*delay[e]+1)) <= B`. The separately published
mass-enclosure appendix at PR #8091 head
`de02b59fa9a74d4958d0d114d25e9083ab91b022` concerns numerical enclosure and replica
counts. It does not count these owners. No mass theorem from that appendix is
imported into (1) or silently promoted to a full capacity proof here.

**Open next question:** combine the accepted source-bound mass enclosure with
an independently reviewed all-size bound on the largest source delay, then
check the displayed sufficient inequality at the installed binary ranks.
The first step is to bind the exact mass proof and `Recipe.open` parameters in
one arithmetic corollary. Until that step is reviewed, beta=2 and all selected
record premises remain explicit; kappa is unchanged.
