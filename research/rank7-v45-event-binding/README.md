# Bind the V45 helper and private-buffer events

Both final PR2979 providers emit the expected 73 direct events for
helper249/private953 in each orientation. The event-selected residual recipe
is `0:275`, with terminal basis `[256,128,64,35,16,11,5]` and rank seven.
Its inverse right and left wrappers give exactly F7, or inverse F7 in the
inverse-transpose orientation, on all 512 columns including global phase.

This closes the **direct event-binding subtask** of [PR3006][3006]'s handoff.
That predecessor checks the helper's native path and normalized endpoint
covectors. [PR2993][2993] checks the frame invoice, and [PR2987][2987] checks
a packing cut. This package adds a separately implemented comparison of actual
emitted events with original word operations, including their position among
other scalar operations. The complete dependency closure remains open.
No supplier or new kappa is claimed. The selected result is unchanged.

## Result and argument

The frozen construction is [PR2979][2979], head
`be191346391661f4d35fc0d1508d0a6029572576`. The scientific base is canonical main
`836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision 6. Source bytes,
Git blobs, overlap coverage and scope are recorded in [SOURCES.json](SOURCES.json)
and [TASK.json](TASK.json). Coordination is in [the existing family thread][claim].

The authenticated transport compacts 704 original names to 632 live registers.
The checker reconstructs that mapping from the original removed-role list.
Helper249 remains compact register249; original private953 is `['Z',249]`.
The generated canonical words, two 22,748-event programs and serialized adapter
records are read back from disk. Each provider's `LOCAL-CHECKS.json` and
`RESIDUAL-ADAPTERS.json` match its exact retained PR2979 native receipt. The
former contains the complete emitted programs' canonical JSON digests. Gzip
container hashes are not used for mathematical equality.

`events.py` independently reconstructs the following direct operations:

- The pre-wrapper, before the covered helper is used.
- 33 helper scalar operations and six climbs across A, B and restore.
- Private allocation, 30 FULL-frame cleanup operations and private free.
- The post-wrapper after cleanup, selecting the same entrance/terminal pair.

Each covered scalar must equal its original source operation after role
translation and orientation normalization. For each phase, a scalar clock counts
**all** emitted scalar operations, including those that do not touch the covered
pair. Covered operations must occur at the original source clock. This rejects
moving a helper operation across an intervening scalar while leaving the direct
helper-operation order unchanged. Climb clocks similarly bind the transition
to its consuming source gate. Unknown direct warps and ordinary adapters on the
cold helper are rejected. The source's omitted sections are checked for absence
of direct helper/private operations.

The six actual climbs have ranks `1,1,1,1,2,1`. The source compiler generates
only those climb recipes for this audit; the retained independently implemented
Gaussian-integer kernel decodes and checks them on all 512 columns in both
orientations. The actual emitted wrapper references select the regenerated
serialized residual recipe. Its pre operation is R inverse and its post operation
is L inverse. Their product with the actual terminal frame is checked exactly.
For these unitary native gates, inverse transpose is entrywise conjugation in
the original chronological order. It is not the adjoint.

[RESULT.json](RESULT.json) retains the direct inventory once, every covered
event index, artifact digests, selected wrapper literals and six climb recipes.
An internal read-only review checked the event boundary and dual semantics.
This is local finite evidence, not independent human or formal-kernel review.

## Reproduce

Python 3.12, with `numpy==1.26.4` for the unchanged source adapter producer:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-v45-event-binding
python3.12 -I -O -Werror -B research/rank7-v45-event-binding/verify.py
python3.12 -I -O -Werror -B research/rank7-v45-event-binding/test_verify.py
```

The hook runs the verifier and nine behavioral test groups. `--emit` prints a
fresh deterministic receipt without overwriting committed evidence. Direct
verification uses temporary directories, writes no repository files and needs
no network or Git access. The registered launcher also checks Git provenance.
Each source subprocess has a 120-second timeout.

`verify.py --run DIR` checks supplied artifacts in `DIR/base` and `DIR/extra`.
This diagnostic mode returns `PASS_V45_SUPPLIED_DIRECT_EVENT_CHECK` and
`native_receipt_bound: false`. It checks the declared direct semantics, not
membership of the whole supplied run in PR2979. Default reconstruction returns
`PASS_V45_DIRECT_EVENT_BINDING` with `native_receipt_bound: true`.

Controls delete or replace wrappers, change terminal frames and climb ranks,
insert a direct warp, change a scalar sign, move a covered scalar across another
scalar, omit cleanup and free the private buffer early. These call the semantic
checker directly, without relying on checksum rejection. A real optimized CLI
run rejects an omitted cleanup operation. Boolean frame IDs, duplicate JSON keys,
capacity exhaustion and corrupt source exports also reject.

The gauge control changes left phase by +1 and right phase by -1. The resulting
operator still equals the required residual and passes the local native identity,
but fails the exact source-recipe binding. Equivalent operators alone do not
establish which serialized recipe the source selected.

## Limits

Cleanup event agreement does not independently prove return to zero. PR3006's
formal endpoint argument and the retained source replay remain separate evidence.
The native identities here do not prove physical correctness of every peer
register, scalar implementation, center or warp. The direct clocks do not check
other registers' intervening warp dependencies. Full emitted Clifford-recipe
generation, dependency closure, ownership/storage, precision/tape, complete
supplier/outer release and inherited all-size/compiler obligations were not
independently replayed. This is a scoped audit, not a complete multiplication
theorem or admission of PR2979's claimed exponent.

## Open next questions

The next useful task is to bind the full native/warp dependency closure reaching
the private endpoint and join its actual storage/precision bill. Start with the
30 named cleanup operations and their peer roles in the retained inventory.
This matters because direct event agreement and an isolated wrapper identity
do not establish the complete caller contract. The blockers are those other
native transitions, common-chart incidence, physical ownership and precision.
No further lowering census is justified by this local result alone.

## Credit and engineering constraints

Nick Petalas. Apache-2.0. Credit Marius-Paul Dumitrean for PR2979's construction;
Jeremy Kothe for frame, native and cleanup work; Mason Hale and Jeremy Diviney
for paired extraction; Tekalign for the retained native driver sources;
icekylinx for the Clifford compiler; Sagar Thakrar for the independent exact
kernel; and Ross Richardson for the packing and accounting audits. Retain the
Yiyang Lu, Dugongue, DreamingOfClouds, Cinna Davis and geometry/owner lineage
credited by those source packages. No predecessor compiler or kernel is new here.

Build the Lever determined the rerunnable event checker. Prove It Works required
regenerating genuine artifacts and comparing exact retained receipts. Test
Behavior, Not Implementation required the semantic chronology and cleanup
controls. Unslop shaped the prose.

Power of Ten inspection covers the four new Python files. Functions stay below
60 physical lines. Reads stop at 16 MiB, inventories at 16 source records,
source sections at 10,000 gates, emitted streams at 100,000 events and frame
tables at 4,096 entries. The fixed native domain is nine binary axes and 512
columns. Runtime checks use exceptions and survive optimized Python. The
producer scripts are frozen inputs and are copied to fresh, cache-free temporary
directories before execution. Source hashes are checked before and after replay.

Rule 3 deviation: Python and NumPy allocate managed storage. The enforced file,
event and frame limits bound live state; a resident service would require a
fixed-capacity implementation. Rules 8/9 deviation: four fixed source modules
are compiled directly, and three authenticated producer scripts run as bounded
subprocesses. Tests also use fixed unittest callbacks. These research inputs
have fixed nine-axis domains and are checked through independent output decoding.
No new dynamic target is accepted from command input. A reusable untrusted-input
service would require static APIs and a separate capacity audit. Source-corruption,
capacity and optimized CLI controls exercise the boundaries. No frozen source or
shared production code changes.

[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
[2987]: https://github.com/CrocSwap/integer-mult-bounds/pull/2987
[2993]: https://github.com/CrocSwap/integer-mult-bounds/pull/2993
[3006]: https://github.com/CrocSwap/integer-mult-bounds/pull/3006
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18978584
