# Independent audit of retained numerical Word cells

This audit independently reads the byte-preserved `vendor/words.py` from
Jose Manuel (`jmbarrancoml`), PR2697 at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, exported by Ross Richardson's
PR2825 at `b553e912bcddef550d9fae6033041ff683399ebe`. Its SHA256 is
`5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9`.
The independent checker neither imports nor consults `verify.py`.
The precursor numerical allowances below remain conditional source findings;
this audit does not independently re-prove their arithmetic call graphs.
Prepared by Ross Richardson with substantial OpenAI Codex assistance.
New work is Apache-2.0; predecessor attribution remains in `vendor/NOTICE.md`.

## Measure, entry invariant, and domain

Fix integer `bits=b>=2` and integer `capacity=C>=1`. At a completed-operation
entry let `K=len(arena.words)` and `L=len(arena.live)`, with
`0<=L<=K<=C`. The entry need not be fresh: an arbitrary finite prior history
may have allocated and erased `K-L` slots.

The entry invariant is stronger than the two cardinalities. The `words` list
contains the unique Word for each slot `0..K-1`. Every Word identifies this
arena and its actual position. The available stack is a duplicate-free ordering
of exactly the complement of the live slots. Available Words have a LEFT in
cell 0 and BLANK in all other cells. Live Words have LEFT, exactly `b` binary
digits, then RIGHT. Available heads and the template head are restored to 1;
other live heads may be at any valid position. A Word passed to `free` has a
head position from which its erase routine succeeds (in this representation,
positions 1 through `b+1` suffice). The permanent template has LEFT, `b` zeros,
RIGHT. The source establishes this invariant from construction and preserves
it across legal successful `zero` and `free` calls. The counting argument does
not require every unrelated live arithmetic head to be simultaneously restored.

Calls are sequential and use the actual owned Word when freeing a live slot.
There is no external mutation of arena bookkeeping, Word identity, cell extent,
markers, or heads, and no concurrent or reentrant callback. Python allocation
failures and interrupted/exceptional partial calls are outside the theorem.
Other arithmetic may be interleaved if it preserves these boundary invariants
and every Word allocation/free is included in the history. Mere success of an
arbitrary Python call, with forged Words or mutated fields, is insufficient.

The measure is the sum of the **lengths of the retained Word.cells arrays**.
It includes erased BLANK cells, every LEFT and RIGHT position, and the
template. It does not count Python objects, list/set storage, bytearray allocator
slack, transient constructor lists/bytes, identifiers, counters, or physical
tapes. Each Word.cells array has exactly `b+2` entries. A constructor creates
one template immediately, but capacity is a lazy inventory guard: it does not
preallocate `C` ordinary Word arrays.

## Completed-operation recurrence: an all-parameter written proof

Index the completed `zero`/`free` calls by `t`, including entry `t=0`. Put
`ell_t=|live_t|`, `B_t=len(words_t)`, and
`H_t=max_{0<=s<=t} ell_s`. Then

```
B_t = max(K, H_t),
retained array cells at t = (B_t + 1)*(b + 2).
```

For a zero call, the partition invariant gives two exhaustive cases. If the
available stack is nonempty, `ell_t<B_t`; the call reuses one erased array,
so `B_{t+1}=B_t` and `ell_{t+1}=ell_t+1<=B_t`. If the stack is empty,
`ell_t=B_t`; a successful call constructs and appends exactly one Word, so
both counts increase by one. Thus in either case
`B_{t+1}=max(B_t,ell_{t+1})`. A free call erases the owned Word and moves its
slot from live to available; it never deletes the Word or shrinks its array,
so `B_{t+1}=B_t` and `ell_{t+1}=ell_t-1`. Induction, starting at `B_0=K`,
proves the equality for every finite legal successful history, independent of
free order or numerical digit values. The template contributes the extra one.

This is stronger than an upper bound but applies only to this exact array
inventory. Counting current nonblank cells, current live slots, or the total
number of allocation requests gives three different quantities.

## Intermediate construction, initialization, and erasure

The boundary formula must not be asserted literally at every Python statement.
`zero` constructs a new array, appends its Word, and only then calls `live.add`.
For example, from `K=L=0`, just after the first Word constructor there is one
ordinary array although the live count and its past maximum are still zero.

For an exact microstate formula let `N(u)` count distinct ordinary Word.cells
arrays retained by `words` **or the pending new Word in zero**, and let `H(u)`
be the largest observed live count since entry, including the current instant.
Let `q(u)=1` precisely when that new ordinary array has been constructed but
its slot has not yet been added to live; otherwise let `q(u)=0`. Then

```
N(u) = max(K, H(u), |live(u)| + q(u)),
retained array cells at u = (N(u) + 1)*(b + 2).
```

The only extra interval is new allocation while the old available stack is
empty, so `|live|` equals the old backing count. Construction adds exactly
one array; appending transfers its owner reference without adding an array;
`live.add` transfers the extra one into `H`. A reused array never creates the
extra interval. All later source actions leave the array inventory unchanged.
This proves the displayed microstate equality. The `len(words)` measure alone
does not include the fresh array before append.

At every `Word.write` in `zero`, the slot is already live. During `free`, the
slot remains live through the entire erasure, including deletion of RIGHT;
only then does `live.remove` execute. Thus the boundary high-water equality
also holds at these write events. Initialization/erasure fill/clear only the
existing `b+1` non-LEFT positions. Their nonblank non-LEFT content is at most
`(|live|+1)*(b+1)`, with equality at canonical completed boundaries. Every
allocated ordinary array nevertheless retains its LEFT and all BLANK positions.
A whole successfully completed interval's maximum array count equals
`max(K,maximum live during that interval)` even though the pointwise formula
needs the pending correction: every pending successful allocation subsequently
becomes live.

## Capacity admission without a circular success assumption

Here is a separate, noncircular statement. Supply a finite, legal request
trace independently of the target capacity: either an abstract sequence of
allocate/free requests with valid owned-slot lifetimes, or a successful reference
execution with enough inventory. Include every pending allocation request,
not just calls that return in the smaller-capacity execution. Starting with
the same canonical entry, let `H*` be that trace's maximum demanded live count.
Provided `K<=C`, its inventory guards all pass **if and only if** `H*<=C`.

For sufficiency use induction on the given trace. A request with a free slot
does not inspect the inventory guard. A request without a free slot has
`B=ell`; its next demanded count is `ell+1<=C`, hence `B<C`, exactly the guard
in `zero`. For necessity, a first request demanding more than `C` cannot find
a free slot since `B<=C`; it fails the guard before constructing a Word or
mutating the state. Free operations do not test capacity. This proves only
absence of that inventory error; value, source, margin, callback, and host
memory contracts remain separate.

Equivalently, an a priori bound for **every capacity-independent request prefix,
including its pending allocation**, suffices. A statement of the form
“every successful target execution has live count at most C” does not suffice:
it is vacuously true of a demand trace that fails on its `(C+1)`st simultaneous
allocation. PR2825 explicitly assumes successful execution. Its stated
allowance alone therefore cannot establish unconditional actual-caller
capacity admission. A reference-trace premise or independent prefix proof
must be supplied before making that stronger claim.

## Two arenas and the conditional first-range consequence

Apply the recurrence separately to distinct residue and index arenas, with
entry backing `K_R,K_I`, entry live counts `L_R,L_I`, and bit widths `b_R,b_I`.
PR2825, under all of its original successful-call contracts and
`64<=n<128`, gives coordinatewise live excess bounds `(37672,41)`. Consequently
the total retained Word.cells inventory throughout such a successful call is
at most

```
(max(K_R, L_R+37672)+1)*(b_R+2)
  + (max(K_I, L_I+41)+1)*(b_I+2).
```

Each maximum can also be capped by its arena's capacity. The formula includes
every historical erased slot through `K_R,K_I`; omitting these terms is
unjustified without a separate history bound. The all-parameter allocator
proof is unconditional within its model; this numerical instantiation retains
the precursor's hypotheses and is not a new proof of its caller analysis.

A maximum of weighted simultaneous live-phase rectangles cannot replace the
sum of retained coordinate peaks. With `b_R=2,b_I=3`, a legal source schedule
first reaches live counts `(3,1)`, frees them, then reaches `(1,3)`. Both arena
high waters are 3, hence retained arrays occupy `4*4+4*5=36` cells. Even a
phase calculation charging a *complete array* per live Word and template
gives only `max(4*4+2*5,2*4+4*5)=28`. The non-LEFT occupied-content maximum
is a third quantity, `max(4*3+2*4,2*3+4*4)=22`.

In the precursor ledger, the rectangles `(37672,34)` and `(20494,41)` likewise
allow a purely abstract arena trace to retain coordinate maxima `(37672,41)`.
For positive full-array weights `w_R,w_I`, the difference between that sum and
the maximum of the two phase expressions is
`min(17178*w_R,7*w_I)>0`. This shows what the rectangular information alone
allows. It does **not** assert that the actual caller attains either rectangle,
or reaches both extrema in one execution. A better caller-specific backing
bound would require additional allocation-history information.

## Finite independent checks and limits

Run from the repository root:

```sh
python3 -B research/selected-numerical-arena-backing/independent.py
```

The checker hashes and imports the pinned runtime. It independently enumerates
all labeled successful histories of length at most 6, for capacities 1 through
3, bit widths 2 and 3, every entry backing count up to capacity, every live-slot
subset, and every ordering of the available stack. Its entry live values are
zero and all entry heads are restored; it does not exhaust binary digit values
or interior head positions. A separate fixture allocates while two unrelated
live heads are suspended (at a digit and at LEFT), then frees Words from legal
interior positions, including a nonzero Word. Its separate integer model
tracks identity lifetimes and predicts the exact boundary recurrence. Runtime
observers check every Word write, new-array construction before append, append
before live registration, and live-set change. Explicit controls reject
live-only storage, eager capacity allocation, total-call-count storage, omitted
templates, an underbudget demand trace, an uncorrected microstate formula,
and replacing separate retained high waters with a weighted phase maximum.

The recorded replay passed 10,164 histories, 52,862 operations, and 317,005
instrumented samples, including 5,930 pending-array samples. The script prints
its complete finite domain, source hash and explicit counterexample values.

These are finite exhaustive and defect-sensitive corroborations of the source
argument, not exhaustive tests over all widths, histories, or caller programs.
The induction above is an all-parameter written proof in its stated arena
model. No formal-kernel proof is supplied. The tests do not replay PR2825's
full caller or discharge its inherited coefficient contracts. Payload, count
tapes, continuations, records, directory keys, Python metadata, physical bank
layout, head movement, recursive reserve, selected supplier admission, and
multiplication/kappa conclusions remain outside this result.

## Open next question

To turn the conditional first-range allowance into an actual-caller inventory
admission theorem, prove the same live-demand bound for every legal prefix of
the capacity-independent caller, including each allocation before its guard.
The first step is to check the predecessor source-site induction against
prefixes ending at each `Arena.zero` request; merely rerunning small successful
fixtures cannot establish this missing implication.
