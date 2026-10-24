# A fixed workspace for the complete streamed leaf/XOR interval

Krzysztof Wójt, with substantial OpenAI Codex assistance. Apache-2.0.
JoyboyBrian's #5055 algorithm and fixtures, Jose Manuel's physical lease
lowering, David Arias's logical caller, Chris R's R437 bridge and their retained
source authors keep their credit. This is a scoped source-level refinement,
not independent acceptance of all inherited supplier hypotheses.

## 1. Boundary and the new statement

Retain the successful-input contract in
`research/r437-streaming-directory/PROOF.md`: a canonical old directory with
C positive physical occurrences of h fields, fixed compiled q and d, a valid
q^w context, complete equal-size source/dirty-target fibres, and a closed
prefix-local leaf. Equal byte prefixes at different positions remain different
occurrences. Put N=C*q^((w-1)*d^2) and let v be the complete fibre bit count,
including all intervening and exterior spectators.

The callback is the retained source coefficient evaluator (or a simpler
callback with the same lifetime and extent bounds), not arbitrary Python.
It returns owned numerical coefficients, restores its borrowed prefix/Program,
does not retain a scratch lease, and invokes no recursive child inside the leaf.
Supplied fixed numerical arenas must suffice. No callback, observer or event
producer may escape/reenter this synchronous interval. This is the predecessor's
leaf boundary, not a new permission to drop an internal recursive call.

**New composition.** The entire repeated local consumer, including its two
input-fibre copies, packet engine, all primitive passes, coefficient stacks,
prefix parsing, returned child, XOR and local disposal, can use one inventory
of A=q^2+136 physical record tapes. There is no physical Tape or Arena creation
inside that consumer. Every successful prefix ends every lease and leaves all
its physical bodies blank at the origin. The same inventory serves all N
prefixes. The returned full N*v-bit output remains an ordinary, separate tape.

The construction uses exactly the predecessor `run.__code__`, changing only
the `Tape` allocation binding and the synchronous `visit` callback boundary.
The full producer `visit.__code__` is unchanged. It reuses the existing
`ScratchPool` and its original source-module/default-factory specialization.
Frozen files are never edited. `actual_bridge.py` selects two actual64 prefixes
only for calibration; it is not used by the complete producer theorem.

## 2. Why this is not just passing a payload factory

The predecessor's direct `left,right=Tape(),Tape()` sites are in `streaming.py`,
outside the source tree recognized by `ScratchPool.install`. Passing a factory
to `packet_engine` alone misses those sites, nested Counters, prefix readers,
Natural/Count work and coefficient stacks. Installing the source pool around
the *entire producer* is also wrong: its saved prefix and reusable reader are
physical persistent roles, not leases that can be ended and then reused through
a stale object.

`Workspace.tape` has a finite phase flag. Outside the local interval it creates
the one full output. Inside it obtains a lease. The visitor suspends the producer,
installs the retained source factories, performs one complete consumer call,
uninstalls those factories, and checks the empty pool before resuming production.
The phase flag depends only on this call boundary, never on a decoded Word.
The adapter's Python specialization machinery stands for the same finite
source-specific role specialization used by the predecessor physical lowering;
it is not a general compiler or a claim that Python module scanning is free.

The installed source pool rejects an otherwise missed raw Tape or Arena
constructor. It also specializes default factory arguments captured at import
time. Source numerical allocation uses the supplied reusable Word arenas.
All within-prefix primitive and coefficient calls, their order, guards and
copies execute unchanged.

## 3. Lifetime proof and role count

The retained physical-caller proof, section 5, gives q^2+128 scratch roles for
each completed source block, including the packet/primitive/callback call graph.
Its ADD/coefficient allowance explicitly includes two Callback objects, eight
main/reverse Stack tapes and an extended Program. Arbitrary history is processed
on those sequential stacks, not by retaining a callback per ancestor. Its
digit-swap allowance includes q^2 bucket roles; sequential passes dispose of the
previous output before continuing. The active sign implementation is
`inputs/pr2753/linear_sign.py`, imported by the active `stream_runner.py`.
The older vendor sign is not substituted into this argument.

We inherit that stated lexical source bound; finite measurements below are not
a new proof of that predecessor theorem. The new wrapper adds at most seven
simultaneously held roles even if we deliberately overcount: its two copied
input fibres, a completed leaf result kept through XOR, and the XOR output plus
three nested counters. Source block and XOR phases are sequential. Eight extra
roles therefore suffice, giving q^2+136. The producer's persistent prefix,
reader and count roles, borrowed metadata and full output are separate residents.

Within an event, the packet engine clears the changed fibre, local fibre and
copied fields after their last read; the completed previous event output is
cleared before advancing. Primitive loops clear their buckets/results and close
their counts before the next iteration. A callback closes its numerical state;
the retained pool adapter additionally retires its four now-empty Stack roles.
After the leaf, the XOR result is copied into the full output, then XOR output,
leaf result and the two input copies are cleared by the unchanged `finally`.
No lease crosses this boundary. A stale repeated clear is inert and cannot
erase a later owner; a stale read is rejected.

Induct on local allocation/retirement events. A fresh lease sees LEFT, an origin
head and an entirely blank body, so every source read/write/unit move produces
the same symbols and heads as a fresh source tape. Only simultaneous live leases
must have distinct roles. The above lifetime bound guarantees a free role in
the stated inventory. Induct next over complete prefixes: at return the pool is
blank and unleased; the producer advances exactly as before. Thus all N complete
dirty-payload outputs and all within-prefix coefficient calls agree with #5055.

## 4. Retained backing, including control tapes

The following are **source parameters**, not numbers decoded to drive execution:

- v: complete local fibre bits;
- D: largest complete copied prefix body, including code/high-word delimiters;
- P: largest Program body, including any transient extension;
- H: largest validated callback Program depth, including an extension;
- I and L: actual index/residue Word bit widths.

Take their maxima across the allowed prefixes and source callbacks. With a fixed
history length and fixed compiled vocabulary these do not grow with C or N.
For example, an h-step Program has body
`2I+L+5+h*(Q+2I+90)` in the retained 16-bit tag vocabulary. Include the extra
step if the callback constructs one; an input Program size alone is insufficient.

Set s=max(2I+4,L+3) and

```
M = max(v, D, P, (2H+3)*s, I+3, L+3, bit_length(v)+3).
```

Payload copies, event outputs and digit buckets contain at most v bits. Prefix
and Program copies are bounded by D and P. A VALUE stack record has two I-bit
words, a tag and three delimiters, hence 2I+4 symbols; scalar stack records have
L+3. The evaluator is a depth-first traversal: a pair frame leaves at most two
pending items per lower level, a good frame at most one, and each VALUE descent
strictly decreases the validated level. Thus 2H+3 records bound pending storage,
including the current replacement. The value stack holds at most H+1 completed
values. A reverse stack holds only one popped record. Multiple callbacks have
separate roles, not concatenated stack bodies.

All positive cardinal products in the local layout are bounded by v: before,
gap and suffix factors grow monotonically toward a factor of the complete fibre.
The local packet/XOR prefix count is one. Natural multiplication and binary
Count.product intermediates do not exceed their final product; marginal adds one
high zero. Count/Counter bodies therefore fit bit_length(v)+3. Counters copied
from encoded exponents or ring atoms fit I+3 or L+3. Matrix arithmetic stays in
the numerical arenas and does not create another record representation.

Consequently a fresh pool retains at most **A*(M+2) cells**: one LEFT marker,
the bounded body, and a conservative extra written blank per role. The latter
accounts for normalization/pop erasure at a prior right edge. Clearing does not
shrink backing. A pool reused from a larger earlier job must additionally charge
its entry backing; `entry_backing+A*(M+2)` is a safe conservative bound. The bound
is for physical backing, not just simultaneously live lease bodies.

This is not a bound on all caller residents. Preserve the two borrowed full
payloads (2Nv), full owned output (Nv), old directory, current/saved prefix,
producer setup/outer/emitted/expected counters, odometer, Program/codebook,
all numerical arenas, suspended parents, and every untouched source owner.
The #5055 producer ledger still applies in full. In particular, deleting
per-prefix scratch allocation does not make the full result or input disappear.

## 5. Movement and erasure are paid

For the literal source `Tape.clear`, let p>=1 be its entry head and l the length
of its contiguous nonblank body. Two rewinds and the sweep give exactly

```
reads  = p + 2l + 2
writes = l
moves  = p + 2l + 3.
```

The write count is erasure, not an omitted allocator operation. Stack.pop and
Count normalization also write blanks during ordinary source execution; those
remain in total primitive traffic and are not double-counted as clear writes.
All source payload copies, coefficient parsing, bucket scans and final output
copies remain paid.

Let K be the number of acquired/retired leases and J the number of temporary
Callback.close operations. Each acquisition adds one blank-check read. Each
successful prefix performs `pool.empty`: two reads and two moves per role.
Each callback close adds four empty-stack clears; at p=1,l=0 these cost 7 cell
actions each. Repeated stale clears can only remove empty-tape source work.
Relative to the same fresh-tape consumer's record-cell action count T, a safe
uniform incremental bound is therefore

```
T_pool <= T + K + 28J + 4AN.
```

The interval starts with prepared LEFT markers and heads just after them, as
does the retained Tape contract. If instead A blank tapes start at their origin
cells, prepare them with A LEFT writes and A unit moves to the right, once.
Those setup actions are separate from the interval meters. Numerical Word
actions are unchanged. This prices the pooling interface; it does **not** turn
T, source coefficient preparation or Context construction into a newly proved
closed all-parameter runtime formula, and implies no asymptotic speedup.

There is also an exact implementation-level conservation check. Let L_r,L_w,L_m
sum the meters of every lease at its unique retirement. At a complete boundary:

```
physical_reads  = L_r + K + 2AN
physical_writes = L_w
physical_moves  = L_m + 2AN.
```

`evidence.py` independently checks this equality and the clear formula at every
retirement/boundary using the physical tape meters. Its byte scans, counters and
history are verifier observations, not retained runtime state or selectors.

## 6. Evidence, failure boundary and remaining obligations

The complete q3/w2/d2 fixture keeps all 81 high matrices for each of three old
physical prefixes (including duplicate bytes), all 19,683 dirty payload bits,
1,458 coefficient calls, and the predecessor's independent permutation/XOR
oracle. The same 145 roles serve all 243 prefixes. All 261,468 leases retire;
the physical pool retains 1,248 cells after the first prefix and thereafter.

The separate actual SOURCE87 request1676 calibration executes two specified
dimension-64 high prefixes, the source-produced Program/callback, 13,122 payload
bits and the actual following XOR. It retains the predecessor's independent
payload oracle, wrong-return and wrong-coefficient controls. It never claims
execution of the 3^4096 prefix domain. Calibration-only `.cells` observations
unwrap a lease's physical tape; no runtime algorithm reads those observations.

Normal/optimized registered verification, exact receipts, under-capacity,
omitted-retirement, forbidden-constructor and dirty-reuse controls are documented
in README/TASK. Their status is reported only after running them. This is
author-checked source reasoning and finite corroboration, not proof-kernel or
independent human acceptance.

The success contract does not promise rollback of malformed source words,
arbitrary callback exceptions or pool exhaustion. Such a failure can leave a
lease active; subsequent use is refused rather than silently reclaiming it.
Inherited per-prefix cleanup does not establish transactional rollback.
Full original q127/GL64 payload execution, source tariff T, all caller residents,
Context/codebook construction, full node/recursive restoration, stock, precision,
native/compiler/outer admission and a new kappa remain outside this result.
