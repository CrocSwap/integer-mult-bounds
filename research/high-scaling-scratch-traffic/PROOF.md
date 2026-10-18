# High-scaling scratch inventory and physical tape traffic

Nick Petalas. Apache-2.0.

## Statement and boundary

Use Jose Manuel/jmbarrancoml's complete PR2915 `kernels.doubled` and its actual
retained PR2809 `ScratchPool.install`. For every odd integer `Q>=3` and positive
integers `B,S`, use [PR2951's canonical borrowed encodings](../high-scaling-total-traffic/PROOF.md).
Put `V=BQS`, let `T` be that theorem's logical traffic, and set

```
A = 7 + 3B + 2BQ [S>1]
p = 7 + [S>1].
```

At entry, `k` active leases remain owned throughout the call, and at least `p`
additional roles are free. Every free role is blank with its head immediately
after LEFT. Borrowed source and Count tapes are distinct, each either external
or an active entry lease; the modulus is a separate numerical Word. Ownership
invariants hold and no concurrent caller, observer or arbitrary factory changes
the literal operations. The payload factory is `pool.acquire`.

Then in either direction exactly `A` acquisitions occur and the peak active
inventory is exactly `k+p`. The `p` free roles suffice and are necessary for
this literal schedule. The physical Tape/Word traffic from function entry
through successful return, including `finally`, is exactly `T+A<530V`.
Borrowed state is restored; the distinct returned output is the only additional
active lease. Other acquired roles are blank, rewound and reusable.

Traffic counts reads, writes and unit head moves on each physical object once.
`Lease.meter` aliases those operations and is not a second physical meter.
Installation, initial marker provisioning, finite-control slot selection and
bookkeeping, Python allocation, observers and later `pool.empty()` diagnostics
are outside this metric. Disposal of the returned output is a later caller
cost. This is not an exact total machine-step invoice, backing-cell bound,
remote-movement theorem or complete physical caller.

## Inventory proof before successful allocation is assumed

The complete source has these nested private lifetimes:

| Category | Roles |
| --- | --- |
| `half` and `even` Counts | 2 |
| `left`, `right`, returned `output` | 3 |
| Current `outer` Counter | 1 |
| Current `pairs` or `copy_rows` Counter | 1 |
| Current `copy_bits` Counter, only if `S>1` | `[S>1]` |

A Count's copy, division and increment operate on its own one Tape. The
`copy_rows` calls are sequential; each closes its Counter before the next.
`copy_bits` skips a suffix Counter exactly for canonical `S=1`. Every other
positive suffix uses one, closed before its enclosing row Counter ends.
No iteration retains an ended lease. Borrowed Word operations add no Tape.

Induct over acquisitions. Before each acquisition at most `p-1` new leases
are active. Since `k` entry owners persist and there are at least `k+p` roles,
a free role exists. Its blank origin comes from entry initialization or its
previous clear. Its marker probe therefore succeeds and ownership is restored.
This excludes a first inventory exhaustion without assuming successful return.

In both directions a row Counter and payload copy are reached while all five
persistent roles and the outer Counter remain live: `B>=1` and
`half=(Q-1)/2>=1`. All seven roles coexist, plus a suffix Counter if `S>1`.
Thus every permitted triple attains the bound. One fewer free role cannot
execute this lexical schedule. Rewritten schedules remain outside the claim.

The count of acquisitions is PR2951's construction count: two Counts, three
payload roles, two outer Counters, `3B` row Counters and, when `S>1`, `2BQ`
suffix Counters. The actual installation covers Count module globals and
default Tape factories; payload construction explicitly calls `pool.acquire`.
No physical Tape or Arena is constructed inside the installed call.

## Exact transfer of the invoice

Each acquisition adds exactly one physical blank-symbol read. The scan of
finite slot labels does not read or move tapes on occupied roles. Those `A`
reads are absent from PR2951's literal-constructor invoice.

`Lease.read`, `write` and `step` forward identical operations. `append`,
`rewind` and `clear` run the original physical Tape methods, including internal
reads and moves. `operation` only updates observer counters. Each private
lifetime here has one close, so inactive-close suppression removes no literal
cleanup loop. Previous clear already supplies the blank origin at reuse.
Retained blank backing beyond that origin changes none of these loops.

Hence the physical trace has the same `T` operations plus `A` probes. A pooled
borrowed source forwards the same operations, with its physical tape counted
once. All entry owners persist. Installer entry/exit restore the namespace
without tape work; its Callback.close specialization is not reached here.

PR2951 proves `T<=524V`. For `S=1`, `A=7+3B<=10B<=6BQ`. For `S>=2`,
`A=7+3B+2BQ<=6BQS`, since `Q>=3,B>=1`. Thus `T+A<=530V`. The strict
`<530V` follows because the retained payload estimate `23V+32<34V` is
strict for integer `V>=3`. The earlier `<1024V` tape allowance survives the
actual constructor probes. A machine-step lowering must separately charge
finite-control selection and installation; they have not been declared zero.

## Reproduction and evidence limits

The checker authenticates the complete PR2915 loader, both immutable archives,
all its declared live inputs, the complete kernel module and PR2951's invoice.
It runs the actual whole installer. Loaded pool bytes must match the pinned
main `selected-bit-physical-caller/scratch_pool.py`; the unchanged loader binds
archived runtime sources. Both temporary source exports are explicitly closed.

Finite corroboration covers 390 calls and 152,352 payload bits, eight occupied
pool cases including pooled sources, and four actual one-role-short rejections.
It checks complete Boolean endpoints, borrowed state, physical traffic,
acquisition counts, peaks and returned ownership. PR2951 retains credit for
its stronger independent-origin checks and logical theorem. This is not a new
independent-column audit. These finite checks corroborate the written proof;
they do not prove its universal quantifier alone.

An extra-marker-read mutant passes the endpoint before failing the invoice.
Inflating only alias meters leaves physical traffic unchanged. Other controls
check stale cleanup, namespace restoration, forbidden physical construction,
source corruption, typed receipt rejection and fixture bounds. Harness cleanup
after an inventory rejection does not prove general source exception safety.

## Engineering constraints

New fixtures enforce `Q<=129`, `B,S<=8`, volume at most 10,000, at most four
occupied and ten free roles. At most 64 pinned inputs of at most 32 MiB are
read. Registered commands time out after 60 seconds, test subprocesses after
30. No new recursion is introduced; contract checks survive `-O`.

Power-of-Ten rule 3 requires a managed-runtime deviation for bounded Python
fixtures. Rules 8 and 9 require a deviation for authenticated compile/exec,
the unchanged archive loader and its bounded installation of factories. The
compensating controls are exact source pins, enforced fixture/input limits,
forbidden constructors, namespace-restoration checks and normal/optimized
replays. Reassess these controls before enlarging the source set or limits.
Inherited loops and allocation are audit subjects, unchanged in frozen source.
